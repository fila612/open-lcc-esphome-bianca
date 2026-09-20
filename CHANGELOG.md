# Changelog

## 0.10.0 — 2026-09-20

Changes since v.0.9.3. Incorporates work developed locally as 0.9.4;
no separate 0.9.4 release was published.

### Behavior and fixes

- Keep one Currently Brewing entity. For RP2040 0.5.0+, use its accepted-shot
  status directly for the entity, timer and resulting shot/pre-infusion automations.
- With older RP2040 firmware, infer validity on the legacy brewing rising edge
  from readiness and tank state in the same packet, independent of entity callback order.
- Preserve a valid running shot when tank-low is reported: timer, counting eligibility
  and pre-infusion continue. Tank warnings remain available; the OLED timer retains
  priority until its normal post-shot display period ends.
- Keep the existing minimum-duration counting rule, including technical error ends.

### Configuration and maintenance

- Synchronize the public template with the private working configuration. The old
  template still carried version 0.9.1 and a static RP2040 version string; live version
  reporting already existed in the personal 0.9.3 configuration.
- Add `scripts/sync_template.py` and `--check`. The private `openlcc.yaml` remains
  ignored; the public template enables the MAC suffix and omits the personal address.
- Add host regression checks and document version-dependent functionality.

### Compatibility

- No new status fields or additional Brew Active entity. RP2040 0.5.0 retains the
  0.4.0 wire layout; this change does not require an update order.
- The physical lever re-arm interlock requires RP2040 0.5.0. Older senders retain
  their firmware behavior, even though ESPHome filters invalid displayed shots.
- Shorter legacy status messages remain supported. Without operational readiness,
  legacy shot display/counting and automatically started pre-infusion remain inactive.
- These guarantees do not cover every historical community/fork protocol layout.

### Validation

- Host checks passed with AddressSanitizer/UndefinedBehaviorSanitizer for accepted
  and legacy shot states, tank-low continuation and unchanged status layout.
- Full template build passed with ESPHome 2026.8.2; template synchronization verified.
- Hardware validation remains outstanding; no device was flashed during preparation.
