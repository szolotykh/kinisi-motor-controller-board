# Project-pinned footprint libraries

These libraries preserve the footprint geometry already used by the routed board. They resolve library-mismatch warnings against newer KiCad libraries and supply the missing L_Sunlord_MWSA0518_5.4x5.2mm footprint without replacing pads or moving copper.

The project fp-lib-table selects these libraries before global libraries with the same nickname. Each contains only the footprints used by this project, not the entire stock library. To use another footprint under one of these nicknames, add it to the corresponding project .pretty directory first, or use a separately named global library.

D_SOD-123_Encoder preserves the distinct D401 footprint. Its identifier is set in both the PCB and encoders.kicad_sch; the other diodes retain D_SOD-123.

Exported using KiCad 10.0.6. Footprint library checks remain enabled. Final PCB DRC: no footprint-library warnings, no unconnected items, and 22 other warnings (6 clearance, 6 silk over copper, 8 dangling tracks, 1 dangling via, 1 nonmirrored back-layer text). This does not certify the existing geometry for manufacturing.

When loading these changes in an already-open KiCad session, reopen the project and PCB/schematic files from disk before saving, so the session does not overwrite the updated footprint identifiers.
