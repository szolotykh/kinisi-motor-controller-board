# Kinisi Smart Motor Controller — v0.4

STM32F405VGT6 (LQFP-100) driving four brushed DC motors via four TI DRV8873S H-bridges,
with quadrature encoder feedback, a BMI088 IMU, a TMP102 temperature sensor and FM24CL64B FRAM.

> **v0.4 is a new pin map, not an increment on v0.3.** Motor control moved from PWM pairs to
> EN/PH/DISABLE plus an SPI control bus. The firmware's `MP_V3` profile does **not** describe
> this board — see [Firmware compatibility](#firmware-compatibility).

---

## Motor driver control signals

Each DRV8873S takes six MCU lines plus a shared SPI bus.

| Signal | Dir | M0 | M1 | M2 | M3 |
|---|---|---|---|---|---|
| `EN` | out | PE15 (46) | PE12 (43) | PE10 (41) | PE8 (39) |
| `PH` | out | PD14 (61) | PD0 (81) | PD5 (86) | PE5 (4) |
| `DISABLE` | out | PD13 (60) | PA15 (77) | PD4 (85) | PE4 (3) |
| `nSLEEP` | out | PB15 (54) | PD2 (83) | PB4 (90) | PB8 (95) |
| `nFAULT` | in | PD8 (55) | PD3 (84) | PB5 (91) | PB9 (96) |
| `nSCS` | out | PD15 (62) | PD1 (82) | PD6 (87) | PE6 (5) |
| `IPROPI` | analog | PC4 (33) | PC5 (34) | PC0 (15) | PC1 (16) |

Shared SPI bus to all four drivers: `M_SCLK` PC10 (78), `M_SDI` PC11 (79), `M_SDO` PC12 (80).

**`nSLEEP` must be driven high before a driver will do anything.** The DRV8873 has an internal
pulldown (≥62.5 kΩ) on this pin, so a floating or un-driven `nSLEEP` leaves the device asleep.

`nFAULT` is open-drain, pulled up by R301 / R302 / R308 / R307 respectively.

---

## Interrupt (EXTI) allocation

On STM32, EXTI line *N* can be driven by only one port's pin *N*. Signals below are the ones
that need edge interrupts.

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

### ⚠ Unresolved line conflicts

These pairs occupy the same EXTI line number on different ports. **Only one of each pair can be
an interrupt source** — the other must be polled.

| Line | Claimant A | Claimant B | Consequence |
|---|---|---|---|
| **9** | `M3_nFAULT` (PB9) | `IMU_INT_GYRO` (PD9) | motor 3 fault interrupt **or** gyro data-ready, not both |
| **5** | `M2_nFAULT` (PB5) | `GPIO7` (PA5) | GPIO7 cannot be interrupt-capable |
| **11** | `IMU_INT_ACCEL` (PD11) | `GPIO2` (PE11) | GPIO2 cannot be interrupt-capable |
| **9** | `IMU_INT_GYRO` (PD9) | `GPIO3` (PE9) | GPIO3 cannot be interrupt-capable |

Conflict-free alternatives, should any of these be remapped: **EXTI10** (PA10, pin 69),
**EXTI12** (PB12, pin 51), **EXTI15** (PC15, pin 9 — VBAT domain, limited drive).
Moving `M3_nFAULT` to **PE2 (pin 1, EXTI2)** would clear the line-9 conflict and is a
shorter route than PB9.

---

## Encoders

| Encoder | A | B |
|---|---|---|
| 0 | PA6 (31) | PA7 (32) |
| 1 | PA0 (23) | PA1 (24) |
| 2 | PB6 (92) | PB7 (93) |
| 3 | PC6 (63) | PC7 (64) |

---

## Sensors and memory

| Signal | Pin | Notes |
|---|---|---|
| IMU_SCK | PB13 (52) | BMI088, SPI2 |
| IMU_SDI | PC3 (18) | |
| IMU_MISO | PC2 (17) | shared by both BMI088 SDO pins |
| IMU_CSB1_ACCEL | PD10 (57) | accelerometer chip select |
| IMU_CSB1_GYRO | PD12 (59) | gyroscope chip select |
| IMU_INT_ACCEL | PD11 (58) | |
| IMU_INT_GYRO | PD9 (56) | |
| SENSOR_SCL | PA8 (67) | I²C to TMP102 (U602) and FM24CL64B (U603) |
| SENSOR_SDA | PC9 (66) | |

**TMP102 `ALERT` (U602 pad 3) is not connected.** Over-temperature alarm must be polled over
I²C; it cannot raise an interrupt.

---

## Host interfaces

| Signal | Pin | Notes |
|---|---|---|
| USB_D+ / USB_D− | PA12 (71) / PA11 (70) | USB-C, 15 Ω series (R503/R504), USBLC6-2SC6 ESD |
| USB_SENSE | PA9 (68) | VBUS detect — line 9, already contended |
| USART_E_TX / RX | PA2 (25) / PA3 (26) | USART2, external header |
| I2C_E_SCL / SDA | PB10 (47) / PB11 (48) | I²C2, external header |
| SWDIO / SWCLK / SWO | PA13 (72) / PA14 (76) / PB3 (89) | Tag-Connect TC2030 |
| LED | PB14 (53) | status |
| BOOT1 | PB2 (37) | |

SWD only — PA15, PB3 and PB4 are repurposed JTAG pins and must be reconfigured as GPIO in firmware.

## GPIO expansion header

| | GPIO0 | GPIO1 | GPIO2 | GPIO3 | GPIO4 | GPIO5 | GPIO6 | GPIO7 |
|---|---|---|---|---|---|---|---|---|
| Pin | PE14 (45) | PE13 (44) | PE11 (42) | PE9 (40) | PE7 (38) | PB1 (36) | PB0 (35) | PA5 (30) |
| EXTI | 14 ✅ | 13 ✅ | 11 ❌ | 9 ❌ | 7 ✅ | 1 ✅ | 0 ✅ | 5 ❌ |

❌ = interrupt unavailable, line claimed elsewhere (see conflicts above).

---

## Power

12 V in via XT30 (J103) → TPS54331 buck (U201) → 3.3 V.
Feedback divider R201 10 k / R202 3.3 k sets **3.22 V** (0.8 V ref). R203 30 k + C205 is the COMP network.

- `VMOTORS` and `+12V` are the same net; KiCad uses `VMOTORS` in the netlist.
- **TPS54331 `EN` (U201 pad 3) is unconnected** — floats to enabled via the internal pull-up.
  Works, but there is no UVLO threshold and no way to shut the rail down.

---

## Known issues

| # | Issue | Severity |
|---|---|---|
| 1 | `M_SDO` track passes **0.0693 mm** from a GND via at (153.63, 92.94). Below JLCPCB's 0.127 mm minimum — likely short, would kill driver SPI readback. | **critical** |
| 2 | `M3_nFAULT` (PB9) and `IMU_INT_GYRO` (PD9) both need EXTI line 9. | **high** |
| 3 | TMP102 `ALERT` not connected — no thermal interrupt. | medium |
| 4 | TPS54331 `EN` not connected — no UVLO. | medium |
| 5 | Dangling copper: `M_SDO` stub (3.17 mm), `IMU_CSB1_GYRO` via, `Net-(U201-BOOT)`, `M1_IPROPI`, `M3_nSCS`, `Net-(U303-IPROPI1)`. | low |
| 6 | `U101` pad 22 (+3.3VA) to `ENCODER_1_A` via: 0.175 mm vs 0.200 mm rule. | low |
| 7 | J501 USB-C GND pads to its NPTH holes: 0.1944 mm vs 0.200 mm rule (×4). | low |
| 8 | U602 SOT-563 pad-to-pad 0.15 mm trips the 0.2 mm global rule — inherent to the package, needs a rule exception. | none (noise) |
| 9 | `#PWR0316` GND power symbol connected to nothing (motor sheet). | investigate |
| 10 | `L_Sunlord_MWSA0518_5.4x5.2mm` not resolvable in `Inductor_SMD`; fitted part C351099 is a YJYCOIN YSPI0530-100M. | low |

Zone fills are stale — refill all zones before trusting DRC clearance counts.

DRC/ERC noise that needs exclusions rather than fixes: DRV8873 `OUT1` (18/19) and `OUT2` (14/15)
are meant to be paralleled; the four `SDO` pins share the SPI MISO bus; `IPROPI1`+`IPROPI2` are
tied to sum current sense; BMI088 `SDO1`/`SDO2` share a line; TPS54331 `GND` + `PowerPAD` are one net.

---

## Firmware compatibility

`hw_config.h` `MP_V3` describes an **earlier board** and will not drive v0.4:

| | MP_V3 | v0.4 |
|---|---|---|
| Motor drive | PWM pairs (PB14/PB15, PC6/PC7, PC8/PC9, PA8/PA9) | EN/PH/DISABLE + SPI |
| Encoder 3 | PA15 / PB3 | PC6 / PC7 |
| GPIO 0–9 | PB13, PB12, PC10, … | PE14, PE13, PE11, PE9, PE7, PB1, PB0, PA5 |

Note PC6/PC7 are encoder 3 on v0.4 but motor 1 PWM under `MP_V3` — a direct collision.
A new `MP_V4` profile is required.
