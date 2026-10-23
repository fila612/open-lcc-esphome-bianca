#include <cassert>
#include <cstddef>
#include <cstring>
#include <iostream>
#include "BrewStateTracker.h"
int main() {
    // RP2040 0.6.0 appended the standby fields after the 0.4.0/0.5.0 layout - never inserted.
    static_assert(offsetof(ESPSystemStatusMessage, standbyMode) ==
                  offsetof(ESPSystemStatusMessage, firmwareVersionPatch) + 1);
    static_assert(sizeof(ESPSystemStatusMessage) ==
                  offsetof(ESPSystemStatusMessage, plannedAutoStandbyInSeconds) + sizeof(uint16_t));
    ESPSystemStatusMessage msg{};
    msg.firmwareVersionMinor = 4; // Latest published legacy semantics: 0.4.0.
    BrewStateTracker legacy;
    msg.currentlyBrewing = true;
    assert(!legacy.update(msg));
    msg.operationalReady = true;
    assert(!legacy.update(msg)); // No inferred start halfway through a held lever.
    msg.currentlyBrewing = false;
    assert(!legacy.update(msg));
    msg.currentlyBrewing = true;
    assert(legacy.update(msg));
    msg.waterTankLow = true;
    assert(legacy.update(msg)); // Keep shot saving.
    msg.currentlyBrewing = false;
    assert(!legacy.update(msg));
    msg.currentlyBrewing = true;
    assert(!legacy.update(msg)); // Empty tank at start.

    BrewStateTracker current;
    msg.firmwareVersionMinor = 5;
    msg.currentlyBrewing = false;
    msg.waterTankLow = false;
    assert(!current.update(msg)); // Lever on + readiness is insufficient.
    msg.currentlyBrewing = true;
    assert(current.update(msg));
    msg.waterTankLow = true;
    msg.operationalReady = false;
    assert(current.update(msg)); // Firmware is authoritative.
    msg.currentlyBrewing = false;
    assert(!current.update(msg)); // End/bail while lever can still be up.

    BrewStateTracker standby_firmware; // RP2040 0.6.0 keeps the accepted-shot semantics.
    msg.firmwareVersionMinor = 6;
    msg.currentlyBrewing = true;
    assert(standby_firmware.update(msg));

    ESPSystemStatusMessage old_message{};
    // Match receiver zero-initialization and truncated legacy payload handling.
    std::memcpy(&old_message, &msg, offsetof(ESPSystemStatusMessage, firmwareVersionMajor));
    assert(old_message.firmwareVersionMajor == 0 && old_message.firmwareVersionMinor == 0);

    // A 0.5.0 payload ends before the standby fields: they stay at their defaults.
    ESPSystemStatusMessage pre_standby{};
    msg.standbyMode = true;
    std::memcpy(&pre_standby, &msg, offsetof(ESPSystemStatusMessage, standbyMode));
    assert(!pre_standby.standbyMode && pre_standby.plannedAutoStandbyInSeconds == 0);
    std::cout << "PASS: authoritative and legacy brew states, shot saving, appended-only protocol layout\n";
}
