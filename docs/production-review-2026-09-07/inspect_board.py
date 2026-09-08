"""Read-only inspection; run with KiCad 10's bundled Python from the board directory."""
import csv
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import pcbnew

root = Path.cwd()
board = pcbnew.LoadBoard(str(root / 'smart_motor_controller.kicad_pcb'))
fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
netlist = ET.parse(root / 'docs/production-review-2026-09-07/schematic.xml')
components = {c.attrib['ref']: c for c in netlist.findall('.//components/comp')}
bom_rows = list(csv.DictReader((root/'assembly/smart_motor_controller-BOM.csv').open(encoding='utf-8-sig')))
bom = {ref.strip(): row for row in bom_rows for ref in row['Designator'].split(',')}
positions = list(csv.DictReader((root/'assembly/smart_motor_controller-all-pos.csv').open(encoding='utf-8-sig')))
mismatches = []
for ref, row in bom.items():
    if ref not in fps:
        mismatches.append({'ref': ref, 'issue': 'BOM reference absent from PCB'})
        continue
    actual = str(fps[ref].GetFPID().GetLibItemName())
    expected = row['Footprint'].split(':')[-1]
    if actual != expected:
        mismatches.append({'ref': ref, 'bom_footprint': row['Footprint'], 'pcb_footprint': actual})
    comp = components.get(ref)
    if comp is not None:
        lcsc = next((f.text for f in comp.findall('fields/field') if f.attrib.get('name') == 'LCSC Part #'), None)
        if lcsc and lcsc != row['LCSC']:
            mismatches.append({'ref': ref, 'bom_lcsc': row['LCSC'], 'schematic_lcsc': lcsc})
missing_bom = [ref for ref, c in components.items() if ref not in bom and any(f.attrib.get('name') == 'LCSC Part #' and f.text for f in c.findall('fields/field'))]
critical = {}
for ref in ['U101','U201','U301','U302','U303','U304','U601','U501','J501','C309','C314','C323','C328']:
    fp = fps[ref]
    critical[ref] = {'value': fp.GetValue(), 'footprint': str(fp.GetFPID().GetLibItemName()), 'pads': [
        {'number': p.GetNumber(), 'net': p.GetNetname(), 'size_mm': [pcbnew.ToMM(p.GetSize().x), pcbnew.ToMM(p.GetSize().y)], 'drill_mm': [pcbnew.ToMM(p.GetDrillSize().x), pcbnew.ToMM(p.GetDrillSize().y)], 'paste': p.IsOnLayer(pcbnew.F_Paste)} for p in fp.Pads()]}
report = {
    'source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in root.glob('*.kicad_*') if p.suffix in ['.kicad_pcb','.kicad_sch','.kicad_pro']},
    'pcb_footprints': len(fps), 'bom_footprint_or_part_mismatches': mismatches,
    'lcsc_populated_parts_missing_from_bom': missing_bom,
    'placement_refs_absent_from_pcb': [r['Designator'] for r in positions if r['Designator'] not in fps],
    'pcb_refs_absent_from_placement': sorted(set(fps) - {r['Designator'] for r in positions}),
    'critical_footprints': critical,
}
print(json.dumps(report, indent=2))
