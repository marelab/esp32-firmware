/* esp32-firmware
 * Copyright (C) 2020-2021 Erik Fleckstein <erik@tinkerforge.com>
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the
 * Free Software Foundation, Inc., 59 Temple Place - Suite 330,
 * Boston, MA 02111-1307, USA.
 */

#pragma once

#include "mqtt_client.h"

#include "api.h"
#include "config.h"

#define MAX_CONNECT_ATTEMPT_INTERVAL_MS 5 * 60 * 1000

enum class MqttConnectionState {
    NOT_CONFIGURED,
    NOT_CONNECTED,
    CONNECTED,
    ERROR
};

struct MqttCommand {
    String topic;
    uint32_t max_len;
    std::function<void(char *, size_t)> callback;
    bool forbid_retained;
};

class Mqtt : public IAPIBackend {
public:
    Mqtt();
    void setup();
    void register_urls();
    void loop();
    void connect();

    void publish(String topic_suffix, String payload);
    void subscribe(String topic_suffix, uint32_t max_payload_length, std::function<void(char *, size_t)> callback, bool forbid_retained);

    // IAPIBackend implementation
    void addCommand(const CommandRegistration &reg);
    void addState(const StateRegistration &reg);
    void addRawCommand(const RawCommandRegistration &reg);
    void pushStateUpdate(String payload, String path);
    void wifiAvailable();

    bool initialized = false;

    void onMqttConnect();
    void onMqttMessage(char *topic, size_t topic_len, char *data, size_t data_len, bool retain);
    void onMqttDisconnect();

    ConfigRoot mqtt_config;
    ConfigRoot mqtt_state;

    ConfigRoot mqtt_config_in_use;

    std::vector<MqttCommand> commands;
    esp_mqtt_client_handle_t client;
};
