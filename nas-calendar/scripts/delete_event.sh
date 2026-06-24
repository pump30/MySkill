#!/usr/bin/env bash
# Usage: delete_event.sh <event-id>
set -euo pipefail

CONFIG="${NAS_CAL_CONFIG:-$HOME/.config/nas-calendar/config.json}"
EVID="${1:?event id required}"

BASE_URL=$(jq -r .base_url "$CONFIG")
USER=$(jq -r .username "$CONFIG")
PASS=$(jq -r .password "$CONFIG")
CAL_PATH=$(jq -r .calendar_path "$CONFIG")
PROXY=$(jq -r '.proxy // ""' "$CONFIG")
ENCODED_PATH=$(echo "$CAL_PATH" | sed 's/@/%40/g')

CURL_ARGS=(-sS -o /dev/null -w "%{http_code}" -X DELETE
  -u "$USER:$PASS"
  "$BASE_URL$ENCODED_PATH$EVID.ics")

[[ -n "$PROXY" ]] && CURL_ARGS=(--proxy "$PROXY" "${CURL_ARGS[@]}")

CODE=$(curl "${CURL_ARGS[@]}")
echo "$EVID -> HTTP $CODE"
