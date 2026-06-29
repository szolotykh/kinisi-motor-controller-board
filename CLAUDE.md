# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

KiCad 9 hardware design for the **Kinisi smart motor controller board** — an STM32F405-based board driving 4 brushed DC motors with quadrature encoder feedback (USB serial, I2C, CAN, GPIO). This repo is **design data only**: there is no firmware, build system, or test suite here.

Companion repos (all under https://github.com/szolotykh):
- Firmware: https://github.com/szolotykh/kinisi-motor-controller-firmware
- Client libraries: https://github.com/szolotykh/pykinisi, https://github.com/szolotykh/ArduinoKinisi, https://github.com/szolotykh/jskinisi
- ROS integration: https://github.com/szolotykh/kinisiros

## Editing design files

- `smart_motor_controller.kicad_pcb` (~46k lines) and `.kicad_sch` are large machine-managed S-expression files. **Edit them in KiCad, not by hand** — manual text edits risk silent corruption. Only hand-edit for trivial, well-understood metadata changes.
- The schematic is hierarchical: top sheet plus `power.kicad_sch` (TPS54331 5–12V→3.3V) and `brushed_motors_and_encoders.kicad_sch`.
- 4-layer board (F_Cu / In1_Cu / In2_Cu / B_Cu). SMD parts standardized on 0603.
- `*.lck` files mean KiCad has the project open; ignore them and don't commit them.
- Legacy `.sch`/`.lib`/`-rescue.kicad_sym` files are migration leftovers — prefer the `.kicad_*` files.

## Fabrication workflow (JLCPCB)

Production targets JLCPCB. When finalizing a revision, regenerate and commit production data together:
- Gerbers + drill files → `gerber/`
- BOM (CSV, with LCSC part numbers) + pick-and-place position CSV → `assembly/`

The BOM's LCSC part column feeds JLCPCB assembly — keep it populated. `kicad-cli` is not on PATH; on Windows it ships at `C:\Program Files\KiCad\9.0\bin\kicad-cli.exe`.

## Revisions & git

- Each board revision gets its own `vX.Y` branch (e.g. `v0.3`, `v0.4`), merged into `main` via PR.
- Reference designators: `M0`–`M3` motor outputs, `ENCODER_0..3_A/B` encoder signals, `U2` main MCU, `U201` power converter, `J*` connectors.
