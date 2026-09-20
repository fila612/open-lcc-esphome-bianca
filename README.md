# Open LCC ESPHome – Lelit Bianca (my fork)

ESPHome-based firmware for the ESP32-S3 half of the [Open LCC](https://github.com/open-lcc) hardware mod for the Lelit Bianca. Companion to the [fila612/open-lcc-rp2040-bianca](https://github.com/fila612/open-lcc-rp2040-bianca) firmware (a fork of [variegated-coffee/open-lcc-rp2040-bianca](https://github.com/variegated-coffee/open-lcc-rp2040-bianca)), which runs on the RP2040 and talks to the machine's Gicar control board; the ESP32-S3 handles Wi-Fi, Home Assistant and the display.

This repository is a fork of [variegated-coffee/open-lcc-esphome-bianca](https://github.com/variegated-coffee/open-lcc-esphome-bianca), the original ESPHome configuration for this hardware. That upstream README, project background and licensing terms still apply and are worth reading there.

## Why this fork exists

The upstream `main` branch was the starting point. From there, this fork's goal is **feature parity with the machine's original Gicar/Lelit firmware**, plus keeping the build alive on current ESPHome. Since branching off, the main additions are:

- **ESPHome upgraded from 2023.x to 2026.x**, including the compatibility fixes that migration required: `ota: platform: esphome`, `type:` on `image:` entries, an `esp_random.h` include for ESP-IDF ≥ 5.x, a patch removing an internal ESPHome API call from the stream server component that no longer exists, disabling `esp32_ble_tracker` (ESPHome ≥ 2025.7 rejects it together with `power_save_mode: NONE`), and splitting the water-tank sensor into its own platform entry to avoid a circular-dependency deadlock at compile time.
- **A full button-driven menu on the OLED**, built from scratch: seven top-level entries with submenus for pre-infusion and sleep, short press to page or adjust a value, long press to open or confirm, an eight-second timeout, and six switches to hide individual entries per board. Language switch between English and German.
- **Reworked pre-infusion**, rebuilt from the original LCC's behavior (build pressure, then pause, then continue): a **Preset** mode using the RP2040's fixed timing, and a **Custom** mode with two menu-adjustable values (pressure time, pause) — Custom is the default for new devices.
- **Sleep mode matching the original control panel**: the OLED turns off (not just the boiler) to avoid burn-in, and the +/- buttons now end sleep mode directly, the same as on the stock LCC panel — confirmed working on the machine.
- **Shot counting and water-tank handling**: persistent shot counters across reboots and a minimum-shot-duration filter keep short flushes out of the count. A lever activation with tank-low already reported or without operational readiness is not treated as a valid shot. Once a shot is valid, a later tank-low report preserves its timer, counting eligibility and pre-infusion sequence, matching the RP2040's upstream shot-saving behavior. The tank warning remains visible; the RP2040 continues to block new shots while its tank-empty latch is active.
- **A genuine one-time "OK" confirmation** when heat-up finishes (matching the original LCC), backed by a real latch on the RP2040 side (`operational_ready`) instead of a text-sensor edge trick — the latter used to re-flash "OK" every time the temperature briefly wobbled back into range during normal PID settling. **Requires RP2040 firmware v.0.2.1 or newer** from the companion repo above. The protocol still accepts older/stock RP2040 messages, but since ESPHome 0.9.2 the valid-shot logic also requires this readiness field: without it, the shot display/counting and automatically started pre-infusion remain inactive. RP2040 v.0.3.0 adds the 30-second stability requirement; v.0.4.0 adds live firmware-version reporting.
- **Wi-Fi setup made resilient**: a fallback access point (`Smart-LCC Setup`) so a board that can't join the configured network is still reachable to set up Wi-Fi from a browser — the point for boards being sold, no rebuild needed — plus fixing `power_save_mode: NONE`, which ESPHome was silently ignoring and which raises latency on a weak signal.
- **A new OLED display layout** designed for this hardware (large digits, icon set, sleep power-off, calibration view), plus a calibration frame to line up the visible area behind the case bezel and a runtime-toggleable verbose-log switch for diagnostics.
- **Web server updated to v3** with a grouped, sortable card layout.

Progress toward that parity goal is tracked via the project version in `openlcc.yaml` (currently 0.10.0, tag `v.0.10.0`; 1.0 marks full parity with the original LCC firmware, confirmed on the machine). The RP2040 side's own running firmware version is reported live (not a manually-maintained value) as a "RP2040 Firmware Version" text sensor — visible on this device's local web server.

`openlcc.yaml` is the active personal configuration and is deliberately ignored by Git.
`openlcc-template.yaml` is its tracked, generic counterpart at the same functional version:
it enables the MAC suffix and omits the personal `wifi.use_address`. WiFi credentials and
the API key remain `!secret` references. `esphome.yaml` is a frozen reference of the
pre-fork upstream state and is not built anymore.

After editing the personal configuration, regenerate and check the template:

```sh
python3 scripts/sync_template.py
python3 scripts/sync_template.py --check
```

The script preserves comments and lambdas and only applies the documented differences.
Review the resulting diff for any additional personal settings before publishing. It runs
in the maintainer's checkout, where the ignored `openlcc.yaml` exists. A new checkout can
start by copying `openlcc-template.yaml` to a personal configuration and supplying secrets.

## Compatibility

Per the upstream project, Open LCC board revisions R1A through R2B are supported. This fork is running on a newer Main Board R2C on a Lelit Bianca V1 - confirmed working. V2 and V3 machines are expected to work too, but haven't been personally verified.

## Disclaimer

This connects to an expensive machine that runs on line voltage, hot pressurized water and steam. Use at your own risk — damage to the machine, personal injury and property damage are all possible, and the liability is yours. Components have already been damaged during development.

## Licensing

The firmware itself is MIT licensed. Including GPL-licensed components (e.g. the serial bridge/stream server) makes the resulting firmware GPL. This only matters if you distribute it, not if you build and flash it for yourself.

### Accepted brew status (0.10.0)

`Currently Brewing` is the single accepted-shot entity. With RP2040 0.5.0 and newer,
its existing wire field reports a shot actually accepted by the controller, including
pump-off pre-infusion and tank-low during a running shot. No new wire fields or separate
Brew Active entity are added. Timer, pre-infusion start and counting use this same state.
A firmware bail ends the reported shot; a valid shot that reached the configured minimum
duration still counts. Existing automations using this entity as a raw lever contact
will instead see accepted shots.

The existing firmware version bytes distinguish the new semantics. With an older
RP2040, the component latches validity at the rising edge of the legacy brewing flag,
using readiness and tank state from the same packet. This avoids entity-publication
ordering dependencies but cannot enforce the physical lever interlock on older RP2040
firmware. Neither this update nor its fallback changes recovery after a transient error.

No update order is required by this change: RP2040 0.5.0 retains the 0.4.0 packet layout.
Older ESPHome versions accepting that layout remain able to read it, though their own
legacy display/counting logic still applies. This is not a blanket compatibility guarantee
for every historical community/fork protocol layout. New ESPHome continues to accept
shorter legacy messages; features requiring missing readiness data remain unavailable.

Host check for the shared binary-sensor/timer decision and legacy payload handling:

```sh
clang++ -std=c++17 -fsanitize=address,undefined -Iopen-lcc/components/open_lcc_bianca tests/brew_state.cpp -o /tmp/bianca-brew-state-test
/tmp/bianca-brew-state-test
```

Hardware checks still required: hold the lever up through heat-up and settling
(no automatic start), lower/raise to start, verify timer continuity during pump-off
pre-infusion and tank-low, and verify the unchanged minimum-duration counting rule.

Release notes are maintained in [CHANGELOG.md](CHANGELOG.md).
