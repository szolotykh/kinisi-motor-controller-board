# Kinisi Smart Motor Controller — v0.4

STM32F405VGT6 (LQFP-100) driving four brushed DC motors via four TI DRV8873S H-bridges,
with quadrature encoder feedback, a BMI088 IMU, a TMP102 temperature sensor and FM24CL64B FRAM.

> **v0.4 is a new pin map, not an increment on v0.3.** Motor control moved from PWM pairs to
> EN/PH/DISABLE plus an SPI control bus. The firmware's `MP_V3` profile does **not** describe
> this board — see [Firmware compatibility](#firmware-compatibility).


---

## Motor driver control signals

Each DRV8873S uses six digital control/status lines, one analog current-sense input,
and a shared SPI bus. Directions below are relative to the MCU; numbers in parentheses
are U101 package-pad numbers.

| Signal | Dir | M0 | M1 | M2 | M3 |
|---|---|---|---|---|---|
| `EN` | out | PE14 (45) | PE12 (43) | PE10 (41) | PE8 (39) |
| `PH` | out | PD14 (61) | PD0 (81) | PD5 (86) | PE5 (4) |
| `DISABLE` | out | PD13 (60) | PA15 (77) | PD4 (85) | PE4 (3) |
| `nSLEEP` | out | PB15 (54) | PD2 (83) | PB4 (90) | PB8 (95) |
| `nFAULT` | in | PD8 (55) | PD3 (84) | PB5 (91) | PB9 (96) |
| `nSCS` | out | PD15 (62) | PD1 (82) | PD6 (87) | PE6 (5) |
| `IPROPI` | analog | PC4 (33) | PC5 (34) | PC0 (15) | PC1 (16) |

### Motor PWM — TIM1

| Motor | Enable pin | Timer output (AF1) |
|---|---|---|
| M0 | PE14 (45) | TIM1_CH4 |
| M1 | PE12 (43) | TIM1_CH3N |
| M2 | PE10 (41) | TIM1_CH2N |
| M3 | PE8 (39) | TIM1_CH1N |

All four enables use TIM1 with a shared PWM frequency and independent duty cycles.
Firmware must enable the complementary outputs for channels 1–3 and the regular
channel 4 output, with correct polarity, main-output enable and safe idle states.
Keep PH pins as direction GPIO and explicitly select PH/EN mode (`MODE = 00b`)
over SPI; the DRV8873S resets to PWM (IN1/IN2) mode instead.
Encoder timer assignments remain independent of TIM1.

References: [STM32 pin mapping](https://www.st.com/resource/en/datasheet/stm32f405rg.pdf),
[DRV8873 control modes](https://www.ti.com/lit/ds/symlink/drv8873.pdf).

### Shared SPI3 bus

| Board net | MCU pin (pad) | SPI3 function | Driver endpoint |
|---|---|---|---|
| `M_SCLK` | PC10 (78) | SCK | SCLK |
| `M_SDI` | PC12 (80) | MOSI, MCU output | SDI |
| `M_SDO` | PC11 (79) | MISO, MCU input | SDO |

Data-net names use the driver's perspective: MCU output connects to driver input.

**Current sense scaling.** `IPROPI1` and `IPROPI2` are tied together (TI's recommended way to
monitor both bridge halves in H-bridge operation)
into a 330 Ω resistor. The DRV8873's mirror ratio is 1 mA out per 1.1 A of load,
i.e. A<sub>IPROPI</sub> ≈ 909 µA/A:

> V<sub>IPROPI</sub> = I<sub>OUT</sub> × (1/1100) × 330 Ω = **0.300 V/A** → 3.3 V full scale = **11 A**

This is a nominal scale, not a qualified continuous-current rating. A 1 µF capacitor
(`C310`/`C311`/`C325`/`C324`) sits on the same node, giving a single-pole filter at
1/(2π·330 Ω·1 µF) = **482 Hz**. The 100 Ω series resistors
(`R303`/`R304`/`R309`/`R310`) isolate the ADC input; there is no separate capacitor at the MCU pin.

**`ITRIP` is *not* set by R<sub>IPROPI</sub> on this part.** Unlike the DRV8874 family, the
DRV8873's current-regulation threshold is an internal, factory-trimmed level selected by
`ITRIP_LVL` in the **IC4 control register**. It resets to 6.5 A nominal (`ITRIP_LVL = 10b`), with regulation enabled
(`DIS_ITRIP = 00b`). Program a suitable threshold; `DIS_ITRIP = 11b` disables regulation on both
outputs if the application intentionally manages current another way.

**`nSLEEP` must be driven high before a driver will do anything.** The DRV8873 has an internal
pulldown (≥62.5 kΩ) on this pin, so a floating or un-driven `nSLEEP` leaves the device asleep.

**`SDO` is tri-stated when `nSCS` is high** (not open-drain), so the four drivers sharing
`M_SDO` is a normal multi-slave SPI arrangement. Assert only one driver chip-select
at a time to prevent output contention.

`nFAULT` is open-drain, pulled up by R301 / R302 / R308 / R307 respectively.

---

## Interrupt (EXTI) allocation

On STM32, EXTI line *N* can be driven by only one port's pin *N*. Signals below are the ones
available for edge interrupts; firmware may poll them instead.

| Signal | Pin | EXTI line | NVIC vector |
|---|---|---|---|
| M0_nFAULT | PD8 (55) | 8 | `EXTI9_5_IRQn` |
| M1_nFAULT | PD3 (84) | 3 | `EXTI3_IRQn` |
| M2_nFAULT | PB5 (91) | 5 | `EXTI9_5_IRQn` |
| M3_nFAULT | PB9 (96) | 9 | `EXTI9_5_IRQn` |
| IMU_INT_ACCEL | PD11 (58) | 11 | `EXTI15_10_IRQn` |
| IMU_INT_GYRO | PD9 (56) | 9 | `EXTI9_5_IRQn` |

Three of the four motor faults (lines 8, 5, 9) share `EXTI9_5_IRQn`; the handler must read the
pending register to identify the source.

### Shared EXTI lines

These pairs occupy the same EXTI line number on different ports. **Only one of each pair can be
an interrupt source** — the other must be polled.

| Line | Claimant A | Claimant B | Consequence |
|---|---|---|---|
| **9** | `M3_nFAULT` (PB9) | `IMU_INT_GYRO` (PD9) | motor 3 fault interrupt **or** gyro data-ready, not both |
| **9** | `IMU_INT_GYRO` (PD9) | `GPIO3` (PE9) | select one port for GPIO EXTI9 |
| **9** | `USB_SENSE` (PA9), if used as GPIO | the three above | GPIO EXTI9 conflicts; native USB OTG VBUS sensing uses the USB peripheral |
| **5** | `M2_nFAULT` (PB5) | `GPIO7` (PA5) | select one port for GPIO EXTI5 |
| **11** | `IMU_INT_ACCEL` (PD11) | `GPIO2` (PE11) | select one port for GPIO EXTI11 |

Line 9 is claimed **four** ways. Encoders use timer encoder mode, so they consume no EXTI line.


---

## Encoders

| Encoder | A | B |
|---|---|---|
| 0 | PA6 (31) | PA7 (32) |
| 1 | PA0 (23) | PA1 (24) |
| 2 | PB6 (92) | PB7 (93) |
| 3 | PC6 (63) | PC7 (64) |

All eight A/B pins are `FT` (5 V tolerant in the appropriate powered digital-input configuration).
Open-collector encoders require pull-ups; none are fitted on the board. Respect the MCU's
power-sequencing and input-voltage limits.
The pins support timer encoder mode (TIM3, TIM2/TIM5, TIM4, TIM8), avoiding GPIO EXTI use.

`J401`–`J404` are 1 = GND, 2 = `V_ENCODER`, 3 = A, 4 = B. `V_ENCODER` is `+3V3` through `D401`
(rail voltage minus the load-dependent diode drop) unless an external supply is applied at `J405`.

There is no bulk capacitor on `V_ENCODER`, and there are no
series resistors, no pull-ups and no filtering on A/B. Cable-side protection and filtering depend on the connected encoder.

---

## Sensors and memory

| Signal | Pin | Notes |
|---|---|---|
| IMU_SCK | PB13 (52) | BMI088, SPI2 |
| IMU_SDI | PC3 (18) | |
| IMU_MISO | PC2 (17) | shared by both BMI088 SDO pins |
| IMU_CSB1_ACCEL | PD10 (57) | accelerometer chip select |
| IMU_CSB1_GYRO | PD12 (59) | gyroscope chip select |
| IMU_INT_ACCEL | PD11 (58) | BMI088 pad 1 = accel `INT2` |
| IMU_INT_GYRO | PD9 (56) | BMI088 pad 13 = gyro `INT4` |
| SENSOR_SCL | PA8 (67) | I²C to TMP102 (U602, 0x48) and FM24CL64B (U603, 0x50); 4k7 pull-ups R601/R602 |
| SENSOR_SDA | PC9 (66) | |

BMI088 accel `INT1` (pad 16) and gyro `INT3` (pad 12) are **shorted to each other** on a net that
has no other component endpoint; firmware must avoid configuring the tied pins as conflicting outputs.

**TMP102 `ALERT` (U602 pad 3) is not connected.** Over-temperature alarm must be polled over
I²C; it cannot raise an interrupt.

---

## Host interfaces

| Signal | Pin | Notes |
|---|---|---|
| USB_D+ / USB_D− | PA12 (71) / PA11 (70) | USB-C, 15 Ω series (R503/R504), USBLC6-2SC6 ESD |
| USB_SENSE | PA9 (68) | native OTG VBUS sense, or GPIO input with EXTI9 conflict |
| USART_E_TX / RX | PA2 (25) / PA3 (26) | USART2, external header |
| I2C_E_SCL / SDA | PB10 (47) / PB11 (48) | I²C2, external header |
| SWDIO / SWCLK / SWO | PA13 (72) / PA14 (76) / PB3 (89) | Tag-Connect TC2030 |
| LED | PB14 (53) | status |
| BOOT1 | PB2 (37) | |

Use SWD on PA13/PA14. Configure PA15 and PB4 as driver GPIO; retain PB3 as SWO if trace is used.

### USB data path

| Connector | Protection path | Series resistor | MCU |
|---|---|---|---|
| J501 A6/B6 (D+) | U501 3 → 4 | R504 | PA12 / pad 71 / OTG_FS_DP |
| J501 A7/B7 (D−) | U501 1 → 6 | R503 | PA11 / pad 70 / OTG_FS_DM |

## GPIO expansion header

| | GPIO0 | GPIO1 | GPIO2 | GPIO3 | GPIO4 | GPIO5 | GPIO6 | GPIO7 |
|---|---|---|---|---|---|---|---|---|
| Pin | PE15 (46) | PE13 (44) | PE11 (42) | PE9 (40) | PE7 (38) | PB1 (36) | PB0 (35) | PA5 (30) |
| EXTI | 15 ✅ | 13 ✅ | 11 ❌ | 9 ❌ | 7 ✅ | 1 ✅ | 0 ✅ | 5 ❌ |
| 5 V tolerant (digital mode) | ✅ FT | ✅ FT | ✅ FT | ✅ FT | ✅ FT | ✅ FT | ✅ FT | 🔴 **TTa** |

❌ = cannot share that GPIO EXTI line with the assigned motor/IMU interrupt.
GPIO0 (PE15) is general-purpose digital I/O with no hardware timer PWM output.
**GPIO7 (PA5) is not 5 V tolerant.** PB0/PB1 (GPIO6/GPIO5) are FT in digital mode;
ADC capability does not by itself make a pin non-FT. FT tolerance does not apply in analog mode.
Use appropriate level conversion for 5 V signals on PA5.

### J104 connector pinout (2×7, 2.54 mm)

Pin 1 is the square pad, at the right-hand end of the header (nearest the SWD/NRST corner).
Both silkscreen layers carry a legend below the header; `G0`–`G7` are `GPIO0`–`GPIO7`,
`TX`/`RX` are `USART_E_TX`/`USART_E_RX` (3.3 V logic).

| Odd row | 13 | 11 | 9 | 7 | 5 | 3 | 1 |
|---|---|---|---|---|---|---|---|
| Silk | GND | G0 | G2 | G4 | G6 | TX | GND |
| **Even row** | **14** | **12** | **10** | **8** | **6** | **4** | **2** |
| Silk | 3V3 | G1 | G3 | G5 | G7 | RX | 3V3 |

`3V3` is the board's own 3.3 V rail — it powers accessories, do not feed it externally.

---

## Power

12 V in via XT30 (J103) → TPS54331 buck (U201) → 3.3 V.
Feedback divider R201 10 k / R202 3.3 k sets **3.22 V** (0.8 V ref). R203 30 k + C205/C206 is the
COMP network.

- `VMOTORS` and `+12V` are the same net; KiCad uses `VMOTORS` in the netlist.
  The 12 V connector label is not evidence of qualification at 24–28 V.
- Power ORing: USB `VBUS` through `D101` and `VMOTORS` through `D102` (both B5819W) meet at
  `BACK_IN`, which feeds `VIN`. USB-only powering is supported by this topology; startup,
  stability and available USB current still need validation under the intended load.
- The converter's 3 A rating is not a board-level rating.
- J105 pin 2 is directly connected to USB VBUS (+5V). An external supply there can
  back-feed a connected USB host.
- `V_ENCODER` = `+3V3` minus `D401`'s forward drop, brought out on J401–J405.
  `J405` permits an external encoder supply; signal levels must still meet MCU input limits.
- **TPS54331 `EN` (U201 pad 3) is unconnected** — floats to enabled via the internal pull-up.
  The converter retains its internal UVLO; no external programmable UVLO divider is fitted.
- Unused MCU pins: PA4, PA10, PB12, PC8, PC13, PC14, PC15, PD7, PE0, PE1, PE2, PE3.
  PC14/PC15 are `OSC32_IN`/`OSC32_OUT` — no LSE crystal is fitted. RTC operation remains
  possible using an alternative clock source.

---

## Silkscreen conventions

- Board-level back-side silkscreen labels are horizontal (rotation 0).
- GPIO J104 and encoder E0/J401 have pin legends on both silk layers. I²C J101 has its
  pin legend on the back only. The E0 legend (`GND VE A B`) applies to E1–E3 as well;
  the four encoder connectors have the same pinout.
- `VE` = `V_ENCODER`, the external encoder supply. J405 (2-pin, "External encoders power") is
  labelled `VE` (pin 2, round pad, `+`) / `GND` (pin 1, square pad) on `B.SilkS`; the front
  carries the `VE` caption and a `+` polarity marker.
- 2.00 mm-pitch legends (I²C) are **staggered over two rows** — pins 1/3 above, pins 2/4 below,
  each centred on its own pad. Check text dimensions against the selected fabrication process.
- `3V3` is the board's own regulated 3.3 V rail (output, not an input).

Motor connector references are non-sequential: **J301 = M0, J302 = M1,
J304 = M2, J303 = M3**. Drivers U301–U304 correspond to M0–M3.
Use connector pad numbers and the schematic to identify terminals; do not rely solely
on back-side `1`/`2` motor-terminal markers.

---

## Verification status

### Manufacturing outputs

Use the [2026-09-07 release candidate](production/v0.4-2026-09-07/README.md):
[fabrication ZIP](production/v0.4-2026-09-07/fabrication.zip),
[assembly BOM](production/v0.4-2026-09-07/assembly/BOM-LCSC.csv), and
[matching placement file](production/v0.4-2026-09-07/assembly/CPL-LCSC.csv).
These were regenerated with KiCad 10.0.6 from the saved design, with source hashes
and validation reports included. The root `gerber/` and `assembly/` exports are obsolete.
Supplier-coded BOM and CPL contain the same 107 references; remaining inventory items
are listed separately for manual procurement/assembly review. Confirm rotations,
polarity and manufacturing settings in the assembler preview before ordering.
The board's existing title-block revision still exports as `0.1.1` in Gerber metadata;
the release-candidate folder name identifies the documented v0.4 hardware. Source hashes
and KiCad generation timestamps establish which saved design was exported.

### Regenerating a production package

Keep [docs/build_production_package.py](docs/build_production_package.py) for repeatable
future exports. Save the schematic and PCB, refill copper zones and save again, then
run the following from the board repository in PowerShell:

```powershell
& 'C:/Users/szolo/AppData/Local/Programs/KiCad/10.0/bin/python.exe' docs/build_production_package.py v0.4-2026-09-08
```

Adjust the Python path to your KiCad installation; use its bundled Python so `pcbnew`
and the adjacent `kicad-cli.exe` are available. Use a new revision/date folder name for
each run. The script refuses to overwrite an existing output directory.

Outputs are written to `production/<name>/`, with a complete `production/<name>.zip`
and a fabrication-only ZIP inside the output directory. They include Gerbers, separate
plated/non-plated drills, BOMs, placement files, DRC/ERC reports, source hashes and checksums.
The script does not modify CAD sources. It stops on reported DRC/parity issues, assembly
consistency failures or source changes during generation. A failed run can leave an
incomplete output directory; do not submit it. Do not run Python with `-O`, which disables
the script's assertion-based checks.

ERC findings are reported but do **not** block export. The script includes project-specific
part checks and fixed v0.4 package text; review these when changing hardware revisions.
Supplier part qualification, parts without supplier codes, placement rotations, polarity,
manufacturing settings and the assembler preview still require review before ordering.
ZIPs are ignored by this repository's `.gitignore`; retain release archives separately
if they need to be shared or preserved outside this workspace.

### Board checks

KiCad 10.0.6 DRC and schematic/PCB parity checks on the saved board on 2026-09-07
pass: zero violations, zero unconnected items and zero parity issues.
The saved schematic and PCB agree on M0_EN = PE14/pad 45 and GPIO0 = PE15/pad 46.

Report: [saved-board DRC](docs/production-review-2026-09-07/drc-m0-fixed.json).
Checks use the project's configured rules; disabled checks are listed in the reports.
This is not an ERC, powered functional-test or fabrication-qualification result.

---

## Firmware compatibility

`hw_config.h` `MP_V3` describes an **earlier board** and will not drive v0.4:

| | MP_V3 | v0.4 |
|---|---|---|
| Motor drive | PWM pairs (PB14/PB15, PC6/PC7, PC8/PC9, PA8/PA9) | EN/PH/DISABLE + SPI |
| Encoder 3 | PA15 / PB3 | PC6 / PC7 |
| GPIO | PB13, PB12, PC10, … | PE15, PE13, PE11, PE9, PE7, PB1, PB0, PA5 |

Note PC6/PC7 are encoder 3 on v0.4 but motor 1 PWM under `MP_V3` — a direct collision.
The companion firmware currently selects `MP_V3` in `include/hw_config.h`.
Use a v0.4-specific pin map and DRV8873S control implementation before enabling motors.

Additional firmware requirements introduced by v0.4:

- **`nSLEEP` must be driven high** per driver before any motion (internal pulldown).
- **`ITRIP` current regulation is enabled by default** and its level lives in the DRV8873's
  IC4 control register, not in any external resistor. Program `ITRIP_LVL`, or set `DIS_ITRIP = 11b`,
  according to the intended current-control strategy.
- Configure **PA15 and PB4** for driver GPIO; PB3 remains the optional SWO trace pin.
- Choose one port per shared GPIO EXTI line; poll other claimants ([Interrupt allocation](#interrupt-exti-allocation)).
- **GPIO7 / PA5 is not 5 V tolerant**; GPIO5/GPIO6 are FT only under the datasheet's digital-mode conditions.
- Configure SPI3 with PC12 / MOSI and PC11 / MISO; keep unselected driver chip-selects high.
