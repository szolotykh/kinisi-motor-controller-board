# v0.4 manufacturing release candidate

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
