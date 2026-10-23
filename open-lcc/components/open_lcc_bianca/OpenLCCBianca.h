//
// Created by Magnus Nordlander on 2023-01-01.
//

#ifndef SMART_LCC_OPENLCCBIANCA_H
#define SMART_LCC_OPENLCCBIANCA_H

#include "esphome/core/component.h"
#include "esphome/core/automation.h"
#include "esphome/core/helpers.h"
#include "esphome/components/uart/uart.h"

#include <cstdint>
#include <cmath>
#include "esp-protocol.h"

// Fix: statt handgeschriebener C++-Deklaration den offiziellen Header nutzen
// (extern "C"-Linkage; noetig ab ESP-IDF 5.x)
#include "esp_random.h"

namespace esphome {
    namespace open_lcc_bianca {
        class OpenLCCBianca : public esphome::PollingComponent, public esphome::uart::UARTDevice {
        public:
            void update();

            void setup();

            void loop();

            void enable() {
                enabled = true;
            }

            void disable() {
                enabled = false;
            }

            void handleNack(ESPMessageHeader *header);

            void handlePingMessage(ESPMessageHeader *header);

            void handleSystemStatusMessage(ESPMessageHeader *header);

            void ackMessage(ESPMessageHeader *header);

            void nackMessage(ESPMessageHeader *header);

            void sendCommand(ESPSystemCommandType type, bool boolArg);

            void sendCommand(ESPSystemCommandType type, float floatArg);

            void sendCommand(ESPSystemCommandType type, uint32_t intArg);

            void sendCommand(ESPSystemCommandPayload payload);

            uint32_t crc32_for_byte(uint32_t r);

            uint32_t crc32(const void *data, size_t n_bytes);

            void add_on_status_update_callback(std::function<void(ESPSystemStatusMessage)> callback) {
                this->on_status_update_callback_.add(std::move(callback));
            }

            // [MOD] Whether the RP2040 firmware sends the standby fields (RP2040 >= 0.6.0). Fields
            // are only ever appended to ESPSystemStatusMessage, so the length of the last status
            // message tells which of them the running firmware knows about.
            bool supports_standby() const {
                return last_status_length_ >= offsetof(ESPSystemStatusMessage, plannedAutoStandbyInSeconds) + sizeof(uint16_t);
            }

        private:
            bool enabled = true;
            uint32_t last_status_length_{0};

            uint8_t *messageBuffer{nullptr};

            CallbackManager<void(ESPSystemStatusMessage)> on_status_update_callback_;
        };

        class OpenLCCBiancaOnStatusUpdateTrigger : public Trigger<ESPSystemStatusMessage> {
        public:
            explicit OpenLCCBiancaOnStatusUpdateTrigger(OpenLCCBianca *parent) {
                parent->add_on_status_update_callback([this](ESPSystemStatusMessage msg) { this->trigger(msg); });
            }
        };
    }
}
#endif //SMART_LCC_OPENLCCBIANCA_H