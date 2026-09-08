# Production-readiness review — 2026-09-07

## Decision: hold submission

Following the user's M0 pin correction, the saved board passes its configured DRC and the M0 timer assignment is resolved. A fresh [manufacturing release candidate](../../production/v0.4-2026-09-07/README.md) now replaces the stale exports and resolves the listed BOM field discrepancies. Hold final release approval pending the remaining electrical/firmware qualifications and manufacturer preview. This is a static review, not a certification or a substitute for prototype testing.

Scope: saved KiCad 10 schematic hierarchy, PCB, project rules, existing Gerbers/drill/BOM/placement data, and the companion firmware's selected hardware profile. No design, rule, firmware or production-export files were changed. An autosave PCB also exists; this review deliberately uses `smart_motor_controller.kicad_pcb`, not unsaved editor/autosave contents. Source hashes are in [board-inventory.json](board-inventory.json).

## Release blockers and required decisions

### 1. Outdated manufacturing files — replaced by current release candidate

Gerbers, separate PTH/NPTH drill files, full BOM, supplier-coded BOM and matching CPL were regenerated using KiCad 10.0.6. Validation confirms 128 current PCB references in the full placement file and matching 107-reference supplier BOM/CPL sets. Source hashes were unchanged throughout generation. See the package's verification/validation.json. The legacy files below remain historical only, with warning README files; they are not included in the new package. Manufacturer visual/DFM approval remains required.

`gerber/smart_motor_controller-F_Cu.gbr` and the drill file identify KiCad 7 and a creation date of 2023-05-21. The placement CSV contains 26 references absent from the current PCB, including U2, U3 and C3. The current PCB contains U101 and 128 footprints. Do not submit the existing Gerbers, drill or placement file as v0.4. Regenerate a consistent package from the final saved/refilled board, and verify its layer set, outline, drill plating, placement origin, rotations and assembly sides in the manufacturer's preview. The existing ZIP was not independently qualified.

### 2. Assembly BOM discrepancies — resolved in regenerated BOM

The new BOM takes supplier codes from the fresh schematic netlist and footprints/values from the saved PCB. R503/R504 now use C22810; C309/C314/C328 use Capacitor_SMD:CP_Elec_5x5.4; D401 uses its actual custom PCB footprint name. Items without supplier codes are explicitly listed separately, not silently treated as DNP. This resolves the field discrepancies below, not independent physical qualification of every supplier part. The table describes the superseded legacy BOM.

| References | Existing BOM | Saved design | Disposition |
|---|---|---|---|
| R503, R504 | LCSC C25118 | LCSC C22810, 15 ohm, 0603 | Correct the orderable part mapping |
| C309, C314, C328 | Through-hole radial footprint | SMD CP_Elec_5x5.4 | Regenerate/correct the footprint column and confirm the selected part fits |
| D401 | D_SOD-123 | D_SOD-123_Encoder | Reconcile the custom-footprint naming; difference alone does not prove physical incompatibility |

The USB-resistor discrepancy is substantive: [LCSC C25118](https://www.lcsc.com/product-detail/C25118.html) identifies 0402WGF470JTCE, while [C22810](https://www.lcsc.com/product-detail/C22810.html) identifies 0603WAF150JT5E. A component-selection evaluation CSV does not supersede a conflicting assembly BOM. This review compares all BOM reference/footprint/LCSC fields against the design but does not independently qualify every supplier part's electrical ratings or availability.

### M0 hardware PWM — resolved in saved design

Follow-up verification on 2026-09-07 confirms M0_EN connects U101 PE14/pad 45 to U301 EN/IN1/pad 7 in both the saved schematic and PCB. GPIO0 connects PE15/pad 46 to J104/pad 11. M1_EN/M2_EN/M3_EN remain on PE12/PE10/PE8. The resulting TIM1 outputs are CH4/CH3N/CH2N/CH1N, providing independent duty cycles at a shared PWM frequency.

M0_PH remains PD14 as direction GPIO, leaving TIM4 available for encoder 2. GPIO0 now uses EXTI15 and has no timer PWM output. See [ST DS8626, alternate-function table](https://www.st.com/resource/en/datasheet/stm32f405rg.pdf).

Firmware must configure TIM1's complementary channels 1–3 and regular channel 4 with appropriate polarity and safe idle states. Explicitly configure the driver's MODE register for PH/EN: the SPI variant defaults to PWM mode. This follow-up verifies wiring, not firmware operation. [TI DRV8873, section 7.3.1](https://www.ti.com/lit/ds/symlink/drv8873.pdf)

Evidence: [fresh schematic netlist](schematic-m0-fixed.xml) and [saved-board DRC/parity](drc-m0-fixed.json). The new saved-board check reports zero violations, zero unconnected items and zero parity issues without an in-memory refill. The source hashes and automated results below describe the earlier review snapshot, not this corrected board.

The companion firmware still selects MP_V3 in `include/hw_config.h`. It is not a working v0.4 motor-control implementation. That blocks claiming a tested functional product, even if prototype PCB fabrication is pursued knowingly.

## Automated checks

| Check | Result |
|---|---|
| Saved-fill DRC, including exclusions | 4 zone-clearance warnings; 0 unconnected items; 0 parity issues |
| In-memory zone-refilled DRC, including exclusions | 0 violations; 0 unconnected items; 0 parity issues |
| Schematic ERC, including exclusions | 23 errors and 57 warnings |

Reports: [saved DRC](drc-saved.json), [refilled DRC](drc-refilled.json), [ERC](erc.json), [fresh netlist](schematic.xml).

The earlier saved-fill warnings are resolved in the follow-up saved-board check. DRC uses the project's rules: copper-edge minimum is 0.025 mm, global minimum clearance is 0 mm, and the Default netclass separately specifies 0.2 mm. Several checks, including missing courtyards and silkscreen overlap, are disabled. Passing this rule set is not confirmation of the selected fabricator's capabilities.

ERC breakdown: 17 output/output reports, five undriven-power reports, one disconnected GND-symbol report, 56 library-symbol mismatches and one multiple-net-name warning. Many output/output findings reflect intentionally shared SPI SDO lines, paired H-bridge output pins, summed current mirrors or incorrectly typed ground/PowerPAD pins. These are not 23 proven electrical defects. Reconcile symbol types, verify external power sources, inspect the disconnected #PWR0316 symbol, and document intentional connections rather than indiscriminately suppressing ERC. Library mismatches need review; do not bulk-update custom symbols without pin verification.

## Electrical and assembly qualification still required

- Buck compensation is C205=1 nF in series with R203=30 kohm, shunted by C206=10 nF. Its ideal passive impedance zero/pole are about 5.31/5.84 kHz, a narrow phase-lead interval. This is a reason to verify loop response, not proof of instability. Validate against actual capacitor bias/ESR, load and input range using the [TPS54331 compensation procedure](https://www.ti.com/lit/ds/symlink/tps54331.pdf), followed by startup and load-step tests.
- Establish supported input voltage, continuous/stall motor current, total logic/accessory load, regeneration handling and temperature rise. A driver peak-current rating or a converter IC rating is not a board rating. These operating requirements were not supplied for this release review.
- BMI088 pins 12/INT3 and 16/INT1 are tied together without another endpoint. Bosch instructs unused interrupt pins to be left unconnected. Prefer separating them before production, or document the intentional use and firmware configuration; no contention at reset is asserted. [Bosch BMI088 pin table](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmi088-ds001.pdf)
- Driver exposed pads are 3.2 x 5.26 mm with F.Paste enabled. A single aperture is not automatically wrong: TI shows that aperture size for a 0.125 mm stencil. Have the assembler approve stencil thickness, paste volume and the thermal-via process. [TI package/stencil example](https://www.ti.com/lit/ds/symlink/drv8873.pdf)
- Confirm custom footprints, courtyards, solder polarity, connector numbering, mechanical clearances and through-hole assembly responsibility in the actual fabrication/assembly preview. This run did not render and visually qualify the new production outputs because no current production package exists.

## Confirmed correct in the reviewed files

- SPI3: PC12/pad 80 -> driver SDI; driver SDO -> PC11/pad 79; PC10/pad 78 -> SCLK.
- USB assigned endpoints: J501 A6/B6 -> U501 3/4 -> R504 -> PA12; A7/B7 -> U501 1/6 -> R503 -> PA11.
- USB CC1/CC2 each have a separate 5.1 kohm pull-down.
- MCU VCAP1/VCAP2 each connect to a separate 2.2 uF capacitor.
- No schematic/PCB parity or unconnected-item failures were reported.

Recommended release sequence: settle the unused IMU connection; reconcile ERC; regenerate and reconcile Gerbers/drill/BOM/placement from the final saved board; obtain assembler DFM approval; build a small bring-up batch and qualify power, USB, four motors/encoders and thermal behavior before committing to a production quantity.
