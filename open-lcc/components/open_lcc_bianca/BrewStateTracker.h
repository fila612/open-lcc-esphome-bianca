#pragma once
#include "esp-protocol.h"

// Both binary sensor and timer consume the same packet-based decision, independent
// of entity callback order. Legacy senders retain the valid-shot rising-edge rule.
class BrewStateTracker {
 public:
    bool update(const ESPSystemStatusMessage &message) {
        // Reuse the existing version bytes; no new fields or handshake required.
        if (message.firmwareVersionMajor > 0 || message.firmwareVersionMinor >= 5) {
            active_ = message.currentlyBrewing;
        } else if (!message.currentlyBrewing) {
            active_ = false;
        } else if (!lever_was_on_) {
            active_ = message.operationalReady && !message.waterTankLow;
        }
        lever_was_on_ = message.currentlyBrewing;
        return active_;
    }
 private:
    bool active_ = false;
    bool lever_was_on_ = false;
};
