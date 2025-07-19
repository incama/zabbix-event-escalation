#!/usr/bin/env python3
import os
import sys
import json
import requests
import time

# Loading the api config information file, making it more secure.
CONFIG_PATH = "/etc/zabbix/zabbix-api.conf"

def load_config(path):
    config = {}
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    config[key.strip()] = val.strip()
    except Exception as e:
        raise RuntimeError(f"Failed to read config file: {e}")
    return config

# Load config
config = load_config(CONFIG_PATH)
ZABBIX_URL = config.get("ZABBIX_URL")
API_TOKEN = config.get("ZABBIX_API_TOKEN")

if not ZABBIX_URL or not API_TOKEN:
    raise RuntimeError("Missing ZABBIX_URL or ZABBIX_API_TOKEN in config")

# Input: Event ID from Zabbix action using the {EVENT.ID} macro.
if len(sys.argv) != 2:
    print("Usage: escalation_severity.py <eventid>")
    sys.exit(1)

EVENT_ID = sys.argv[1]
# Check if event already has been escalated.
def has_been_escalated(event_id):
    result = zabbix_api("event.get", {
        "eventids": [event_id],
        "selectAcknowledges": "extend",
        "output": "extend"
    })

    if not result:
        return False
# Searching for keywords in older messages, if they are found, the script skips the escalation. See line 93.
    for ack in result[0].get("acknowledges", []):
        msg = ack.get("message", "").lower()
        if "raised to" in msg or "escalation" in msg:
            return True
    return False

def zabbix_api(method, params):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_TOKEN}"
    }
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    response = requests.post(ZABBIX_URL, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    data = response.json()
    if "error" in data:
        raise Exception(f"Zabbix API error: {data['error']}")
    return data["result"]

def escalate_event_severity(event_id):
    print(f"Checking event {event_id}...")
    if has_been_escalated(event_id):
        print(f"Event {event_id} was already escalated, SKIPPING.")
        return
    print(f"Escalating severity for event {event_id}...")

    # 1. Change severity to DISASTER (5).
    zabbix_api("event.acknowledge", {
        "eventids": [event_id],
        "action": 8,
        "severity": 5
    })

    # 2. Add visible comment of the escalation.
    zabbix_api("event.acknowledge", {
        "eventids": [event_id],
        "action": 4,
        "message": "Severity raised to DISASTER on event"
    })

if __name__ == "__main__":
    try:
        escalate_event_severity(EVENT_ID)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)