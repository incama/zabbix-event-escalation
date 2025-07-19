# Zabbix Event Severity Escalation

A Python script for automated Zabbix event severity management that escalates events to DISASTER level while preventing duplicate escalations.

## Overview

This tool solves the problem of managing event escalations in Zabbix when using multiple triggers. Instead of creating separate triggers for different severity levels, it uses a single trigger and programmatically escalates the severity through the Zabbix API.

## Prerequisites

- Python 3.x
- Zabbix API access credentials
- `requests` library

## Setup

1. Place the zabbix-api.conf file in /etc/zabbix/ and adjust the parameters:
```aiignore
# Zabbix API Information
ZABBIX_URL=https://<zabbixurl>/api_jsonrpc.php
ZABBIX_API_TOKEN=<your zabbix token>
```
2. Ensure proper file permissions for the config file.
```aiignore
chown zabbix:zabbix /etc/zabbix/zabbix-api.conf
chmod 600 /etc/zabbix/zabbix-api.conf
```
3. Copy the escalation_severity.py to /usr/lib/zabbix/alertscripts/

## Inline usage for testing
```aiignore
python3 escalation_severity.py <eventid>
```


## Features

- Single-trigger approach for better event correlation
- Automatic severity escalation to DISASTER
- Duplicate escalation prevention
- Event acknowledgment tracking

## Error Handling

The script includes comprehensive error handling and will exit with appropriate status codes and messages if issues occur.

## Security

Configuration is managed through a secure external config file with API token authentication.