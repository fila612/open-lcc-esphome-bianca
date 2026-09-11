# Open LCC ESPHome – Lelit Bianca (my fork)

ESPHome-based firmware for the ESP32-S3 half of the [Open LCC](https://github.com/open-lcc) hardware mod for the Lelit Bianca. Companion to the [fila612/open-lcc-rp2040-bianca](https://github.com/fila612/open-lcc-rp2040-bianca) firmware (a fork of [variegated-coffee/open-lcc-rp2040-bianca](https://github.com/variegated-coffee/open-lcc-rp2040-bianca)), which runs on the RP2040 and talks to the machine's Gicar control board; the ESP32-S3 handles Wi-Fi, Home Assistant and the display.

This repository is a fork of [variegated-coffee/open-lcc-esphome-bianca](https://github.com/variegated-coffee/open-lcc-esphome-bianca), the original ESPHome configuration for this hardware. That upstream README, project background and licensing terms still apply and are worth reading there.

## Why this fork exists

The upstream `main` branch was the starting point. From there, this fork's goal is **feature parity with the machine's original Gicar/Lelit firmware**, plus keeping the build alive on current ESPHome. Since branching off, the main additions are:

- **ESPHome upgraded from 2023.x to 2026.x**, including the compatibility fixes that migration required: `ota: platform: esphome`, `type:` on `image:` entries, an `esp_random.h` include for ESP-IDF ≥ 5.x, a patch removing an internal ESPHome API call from the stream server component that no longer exists, disabling `esp32_ble_tracker` (ESPHome ≥ 2025.7 rejects it together with `power_save_mode: NONE`), and splitting the water-tank sensor into its own platform entry to avoid a circular-dependency deadlock at compile time.
- **A full button-driven menu on the OLED**, built from scratch: seven top-level entries with submenus for pre-infusion and sleep, short press to page or adjust a value, long press to open or confirm, an eight-second timeout, and six switches to hide individual entries per board. Language switch between English and German.
- **Reworked pre-infusion**, rebuilt from the original LCC's behavior (build pressure, then pause, then continue): a **Preset** mode using the RP2040's fixed timing, and a **Custom** mode with two menu-adjustable values (pressure time, pause) — Custom is the default for new devices.
- **Sleep mode matching the original control panel**: the OLED turns off (not just the boiler) to avoid burn-in, and the +/- buttons now end sleep mode directly, the same as on the stock LCC panel — confirmed working on the machine.
- **More reliable shot counting and water-tank handling**: persistent shot counters across reboots, a minimum-shot-duration filter to keep flushes out of the count, and a flag that discards a "brew" if the tank ran dry mid-shot — or the RP2040 blocked it entirely for not being operationally ready yet — so it isn't counted, timed, or shown running on the display.
- **A genuine one-time "OK" confirmation** when heat-up finishes (matching the original LCC), backed by a real latch on the RP2040 side (`operational_ready`) instead of a text-sensor edge trick — the latter used to re-flash "OK" every time the temperature briefly wobbled back into range during normal PID settling. **Requires RP2040 firmware v.0.2.1 or newer** from the companion repo above; with older/stock RP2040 firmware this indicator just stays off and everything else keeps working normally (the ESP32 side is deliberately kept backward compatible — see `esp-protocol.h`).
- **Wi-Fi setup made resilient**: a fallback access point (`Smart-LCC Setup`) so a board that can't join the configured network is still reachable to set up Wi-Fi from a browser — the point for boards being sold, no rebuild needed — plus fixing `power_save_mode: NONE`, which ESPHome was silently ignoring and which raises latency on a weak signal.
- **A new OLED display layout** designed for this hardware (large digits, icon set, sleep power-off, calibration view), plus a calibration frame to line up the visible area behind the case bezel and a runtime-toggleable verbose-log switch for diagnostics.
- **Web server updated to v3** with a grouped, sortable card layout.

Progress toward that parity goal is tracked via the project version in `openlcc.yaml` (currently 0.9.3; 1.0 marks full parity with the original LCC firmware, confirmed on the machine). The RP2040 side's own running firmware version is reported live (not a manually-maintained value) as a "RP2040 Firmware Version" text sensor — visible on this device's local web server.

`openlcc.yaml` is the active configuration to build and flash. `esphome.yaml` is kept as a frozen reference of the pre-fork upstream state and is not built anymore.

## Compatibility

Per the upstream project, Open LCC board revisions R1A through R2B are supported. This fork is running on a newer Main Board R2C on a Lelit Bianca V1 - confirmed working. V2 and V3 machines are expected to work too, but haven't been personally verified.

## Disclaimer

This connects to an expensive machine that runs on line voltage, hot pressurized water and steam. Use at your own risk — damage to the machine, personal injury and property damage are all possible, and the liability is yours. Components have already been damaged during development.

## Licensing

The firmware itself is MIT licensed. Including GPL-licensed components (e.g. the serial bridge/stream server) makes the resulting firmware GPL. This only matters if you distribute it, not if you build and flash it for yourself.
