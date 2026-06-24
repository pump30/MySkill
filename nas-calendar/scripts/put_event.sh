#!/usr/bin/env bash
# Usage: put_event.sh <event-id> <ics-file>
# Reads ~/.config/nas-calendar/config.json and PUTs the .ics to the calendar.
set -euo pipefail

CONFIG="${NAS_CAL_CONFIG:-$HOME/.config/nas-calendar/config.json}"
if [[ ! -f "$CONFIG" ]]; then
  echo "config not found: $CONFIG" >&2
  echo "copy config.example.json there and fill it in" >&2
  exit 1
fi

EVID="${1:?event id required}"
ICS="${2:?ics file required}"

BASE_URL=$(jq -r .base_url "$CONFIG")
USER=$(jq -r .username "$CONFIG")
PASS=$(jq -r .password "$CONFIG")
CAL_PATH=$(jq -r .calendar_path "$CONFIG")
PROXY=$(jq -r '.proxy // ""' "$CONFIG")

# URL-encode @ in the username segment of calendar_path if present
ENCODED_PATH=$(echo "$CAL_PATH" | sed 's/@/%40/g')

CURL_ARGS=(-sS -o /dev/null -w "%{http_code}" -X PUT
  -u "$USER:$PASS"
  -H "Content-Type: text/calendar; charset=utf-8"
  --data-binary "@$ICS"
  "$BASE_URL$ENCODED_PATH$EVID.ics")

if [[ -n "$PROXY" ]]; then
  CURL_ARGS=(--proxy "$PROXY" "${CURL_ARGS[@]}")
fi

CODE=$(curl "${CURL_ARGS[@]}")
echo "$EVID -> HTTP $CODE"
case "$CODE" in
  201) echo "  created" ;;
  204) echo "  updated" ;;
  2*)  echo "  ok" ;;
  *)   echo "  FAILED"; exit 1 ;;
esac
