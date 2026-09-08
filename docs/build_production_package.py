"""Generate a traceable release candidate using KiCad's bundled Python. Never edits CAD sources."""
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
import pcbnew

ROOT = Path(__file__).resolve().parents[1]
CLI = Path(sys.executable).with_name('kicad-cli.exe')
OUT = ROOT / 'production' / sys.argv[1]
OUT.mkdir(parents=True, exist_ok=False)
for folder in ['fabrication', 'assembly', 'verification']:
    (OUT / folder).mkdir()
board_path = ROOT / 'smart_motor_controller.kicad_pcb'
sources = sorted(p for p in ROOT.iterdir() if p.suffix in ['.kicad_pcb', '.kicad_sch', '.kicad_pro'] and not p.name.startswith('_autosave'))
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = {p.name: digest(p) for p in sources}

def run(*args):
    subprocess.run([str(CLI), *map(str, args)], cwd=ROOT, check=True)

def write_csv(path, fields, rows):
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

run('pcb', 'drc', '--schematic-parity', '--severity-all', '--format', 'json', '-o', OUT/'verification/drc.json', board_path)
drc = json.loads((OUT/'verification/drc.json').read_text())
for key in ['violations', 'unconnected_items', 'schematic_parity']:
    assert not drc.get(key), f'DRC failed: {key}'
run('sch', 'export', 'netlist', '--format', 'kicadxml', '-o', OUT/'verification/schematic.xml', ROOT/'smart_motor_controller.kicad_sch')
run('sch', 'erc', '--severity-all', '--format', 'json', '-o', OUT/'verification/erc.json', ROOT/'smart_motor_controller.kicad_sch')
layers = 'F.Cu,In1.Cu,In2.Cu,B.Cu,F.Mask,B.Mask,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,Edge.Cuts'
run('pcb', 'export', 'gerbers', '--layers', layers, '--no-protel-ext', '--subtract-soldermask', '-o', str(OUT/'fabrication')+'/', board_path)
run('pcb', 'export', 'drill', '--format', 'excellon', '--drill-origin', 'absolute', '--excellon-units', 'mm', '--excellon-separate-th', '-o', str(OUT/'fabrication')+'/', board_path)
run('pcb', 'export', 'pos', '--format', 'csv', '--units', 'mm', '--side', 'both', '--exclude-dnp', '-o', OUT/'assembly/positions-kicad.csv', board_path)

board = pcbnew.LoadBoard(str(board_path))
fps = {f.GetReference(): f for f in board.GetFootprints()}
netlist = ET.parse(OUT/'verification/schematic.xml')
comps = {c.attrib['ref']: c for c in netlist.findall('.//components/comp')}
sortref = lambda ref: (re.sub(r'\d+', '', ref), int(re.search(r'\d+', ref).group()) if re.search(r'\d+', ref) else 0)
full, selected, manual = [], [], []
for ref in sorted(fps, key=sortref):
    fp = fps[ref]
    if fp.GetAttributes() & (pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_DNP):
        continue
    comp = comps.get(ref)
    fields = {} if comp is None else {f.attrib['name']: f.text or '' for f in comp.findall('fields/field')}
    row = {'Comment': fp.GetValue(), 'Designator': ref, 'Footprint': str(fp.GetFPID().GetLibNickname())+':'+str(fp.GetFPID().GetLibItemName()), 'LCSC': fields.get('LCSC Part #', '')}
    full.append(row)
    if row['LCSC']:
        selected.append(row)
    else:
        manual.append(row)
for name, rows in [('BOM-all.csv', full), ('BOM-LCSC.csv', selected), ('BOM-manual-selection.csv', manual)]:
    write_csv(OUT/'assembly'/name, ['Comment', 'Designator', 'Footprint', 'LCSC'], rows)
positions = list(csv.DictReader((OUT/'assembly/positions-kicad.csv').open(encoding='utf-8')))
assert all(p['Ref'] in fps for p in positions), 'Obsolete placement references'
pos_by_ref = {p['Ref']: p for p in positions}
assert all(r['Designator'] in pos_by_ref for r in selected), 'Selected assembly part missing placement'
cpl = [{'Designator': r['Designator'], 'Mid X': pos_by_ref[r['Designator']]['PosX']+'mm', 'Mid Y': pos_by_ref[r['Designator']]['PosY']+'mm', 'Layer': 'Top' if pos_by_ref[r['Designator']]['Side']=='top' else 'Bottom', 'Rotation': pos_by_ref[r['Designator']]['Rot']} for r in selected]
write_csv(OUT/'assembly/CPL-LCSC.csv', ['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'], cpl)
assert {r['Designator'] for r in selected} == {r['Designator'] for r in cpl}
for ref in ['R503', 'R504']:
    assert next(r for r in full if r['Designator']==ref)['LCSC']=='C22810'
for ref in ['C309', 'C314', 'C328']:
    assert next(r for r in full if r['Designator']==ref)['Footprint']=='Capacitor_SMD:CP_Elec_5x5.4'
after = {p.name: digest(p) for p in sources}
assert before == after, 'CAD sources changed during generation; discard package'
verification = {'source_sha256': before, 'kicad_version': subprocess.check_output([str(CLI), 'version'], text=True).strip(), 'copper_layers': board.GetCopperLayerCount(), 'pcb_footprints': len(fps), 'bom_parts': len(full), 'lcsc_bom_and_cpl_parts': len(selected), 'manual_selection_parts': [r['Designator'] for r in manual], 'placement_parts': len(positions), 'placement_excluded': sorted(set(fps)-set(pos_by_ref)), 'drc_violations': len(drc.get('violations', [])), 'unconnected_items': len(drc.get('unconnected_items', [])), 'schematic_parity': len(drc.get('schematic_parity', [])), 'sources_unchanged': before==after}
(OUT/'verification/validation.json').write_text(json.dumps(verification, indent=2)+'\n', encoding='utf-8')
with zipfile.ZipFile(OUT/'fabrication.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for p in sorted((OUT/'fabrication').iterdir()):
        archive.write(p, p.name)
instructions = '''# v0.4 manufacturing release candidate

Generated from the final saved CAD files using KiCad 10. See verification/validation.json for exact source hashes and check results. No CAD sources were modified. This package supersedes the legacy root gerber/ and assembly/ exports.

## Files to use

- fabrication.zip: four copper layers (F.Cu, In1.Cu, In2.Cu, B.Cu), top/bottom mask, paste and silkscreen, board outline, Gerber job metadata, and separate plated/non-plated Excellon drill files.
- assembly/BOM-LCSC.csv and assembly/CPL-LCSC.csv: matching reference sets for parts with supplier codes in the saved schematic. Footprints and values come from the current PCB. One component per row.
- assembly/BOM-all.csv: full population inventory.
- assembly/BOM-manual-selection.csv: parts without supplier codes; arrange procurement/hand assembly or select parts before ordering assembly. These are NOT declared DNP.
- assembly/positions-kicad.csv: unfiltered assembly-position reference, including through-hole parts.
- verification/: DRC, ERC, schematic netlist, source hashes and consistency checks.

## Manufacturing conventions and release limitations

Gerbers and drill use the absolute board origin; placement uses KiCad absolute coordinates in millimetres, with its normal Y-axis convention and no bottom-X negation. CPL rotations are native KiCad rotations, NOT vendor-footprint-corrected rotations. Confirm position, side, rotation, polarity and connector orientation in the assembler preview before approving assembly. Do not apply arbitrary universal rotation corrections.

Copper stack order is F.Cu / In1.Cu / In2.Cu / B.Cu. Confirm thickness, copper weight, finish, soldermask, drill limits and stackup with the manufacturer; this export does not qualify an ordering specification or controlled impedance. Approve the exposed-pad stencil and thermal-via process with the assembler.

Saved-board DRC/parity passes under configured rules. ERC and the other electrical, firmware, thermal and assembly qualifications from docs/production-review-2026-09-07/REVIEW.md remain applicable. Fresh exports do not certify production readiness. Supplier codes are copied from the schematic, not an independent qualification of every selected part.
'''
(OUT/'README.md').write_text(instructions, encoding='utf-8')
manifest = {str(p.relative_to(OUT)).replace('\\', '/'): digest(p) for p in sorted(OUT.rglob('*')) if p.is_file()}
(OUT/'SHA256.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
with zipfile.ZipFile(OUT.parent / (OUT.name + '.zip'), 'w', zipfile.ZIP_DEFLATED) as archive:
    for p in sorted(OUT.rglob('*')):
        if p.is_file():
            archive.write(p, str(p.relative_to(OUT)))
print(json.dumps(verification, indent=2))
print('Package:', OUT.parent / (OUT.name + '.zip'))
