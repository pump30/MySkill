---
name: nas-calendar
description: Use when user wants to add, update, or delete calendar events on their self-hosted CalDAV server (Radicale on NAS). Triggers on keywords like "加日程", "加日历", "calendar event", "排班", "添加事件", "delete event", "改日程", or when user shares a schedule/screenshot and asks to put it on their calendar.
---

# NAS CalDAV Calendar Management

Create, update, and delete events on a self-hosted Radicale CalDAV server via raw HTTP. Works with both all-day and timed events. Uses idempotent UIDs so re-running the same operation overwrites rather than duplicates.

## Config

Credentials and URLs are read from a local config file (NOT in this repo):

```
~/.config/nas-calendar/config.json
```

Schema — see `config.example.json`:

```json
{
  "base_url": "https://<your-dav-host>",
  "username": "<dav-user>",
  "password": "<dav-pass>",
  "calendar_path": "/<user>/<calendar-uuid>/",
  "proxy": "http://127.0.0.1:7897"
}
```

Read this file at the start of every session and use the values verbatim. Never echo the password to the user; never commit any of these values to git.

## When invoked

1. Read `~/.config/nas-calendar/config.json`. If missing, tell the user to copy `config.example.json` and fill it in.
2. Confirm the target calendar with `PROPFIND` if you're not sure it exists (depth 1 on `calendar_path`).
3. For each event the user wants:
   - Choose a stable UID (e.g. `shift-20260624-claude@<dav-host>` or `meeting-<slug>-<date>`). Same UID + PUT = update; new UID = new event.
   - Build the `.ics` body with **CRLF line endings**. `printf` in bash handles this with `\r\n`.
   - `PUT` to `<base_url><calendar_path><filename>.ics`.
4. Report what was created/updated/deleted in one short line per event. Do not paste back the full .ics.

## .ics templates

### All-day event

```
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Claude//nas-calendar//EN
BEGIN:VEVENT
UID:<stable-uid>
DTSTAMP:<YYYYMMDDTHHMMSSZ>
DTSTART;VALUE=DATE:<YYYYMMDD>
DTEND;VALUE=DATE:<YYYYMMDD-of-next-day>
SUMMARY:<title>
END:VEVENT
END:VCALENDAR
```

`DTEND` for an all-day event is **exclusive** — for a single-day event on the 24th, set `DTEND` to the 25th.

### Timed event

```
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Claude//nas-calendar//EN
BEGIN:VEVENT
UID:<stable-uid>
DTSTAMP:<YYYYMMDDTHHMMSSZ>
DTSTART;TZID=Asia/Shanghai:<YYYYMMDDTHHMMSS>
DTEND;TZID=Asia/Shanghai:<YYYYMMDDTHHMMSS>
SUMMARY:<title>
LOCATION:<optional>
DESCRIPTION:<optional>
END:VEVENT
END:VCALENDAR
```

## Operations

### Create or update

```bash
# Reads config, writes /tmp/ev.ics, PUTs it
bash scripts/put_event.sh <event-id> <ics-file>
```

Or inline with curl (read values from config first):

```bash
curl -sS -X PUT \
  --proxy "$PROXY" \
  -u "$USER:$PASS" \
  -H "Content-Type: text/calendar; charset=utf-8" \
  --data-binary @/tmp/ev.ics \
  "$BASE_URL$CAL_PATH<event-id>.ics"
```

A `201` means new, `204` means update, `2xx` means success. Anything else — report it.

### Delete

```bash
curl -sS -X DELETE --proxy "$PROXY" -u "$USER:$PASS" \
  "$BASE_URL$CAL_PATH<event-id>.ics"
```

### List events in a date range (REPORT)

Use this to find existing UIDs before bulk-updating.

```bash
curl -sS -X REPORT --proxy "$PROXY" -u "$USER:$PASS" \
  -H "Depth: 1" -H "Content-Type: application/xml" \
  --data '<?xml version="1.0"?><c:calendar-query xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav"><d:prop><d:getetag/><c:calendar-data/></d:prop><c:filter><c:comp-filter name="VCALENDAR"><c:comp-filter name="VEVENT"><c:time-range start="20260601T000000Z" end="20260701T000000Z"/></c:comp-filter></c:comp-filter></c:filter></c:calendar-query>' \
  "$BASE_URL$CAL_PATH"
```

## Batch patterns

When the user shares a screenshot of a schedule:

1. Extract `(date, summary, start?, end?)` rows.
2. Generate stable UIDs (e.g. `shift-<YYYYMMDD>`).
3. Write a small bash loop that calls the PUT for each. Don't loop in Python — Python's urllib auth handling has been flaky over the tunnel; curl is reliable.
4. After the loop, report `N created / M updated / K failed`.

When the user asks to **modify** an existing batch (e.g. "remove the H2/H1 prefix"):

1. Reuse the same UIDs (filename = `<uid>.ics`).
2. Build new .ics bodies with the corrected `SUMMARY`.
3. PUT again — Radicale will return 204 (update) for each.

## Gotchas

- **CRLF required.** LF-only .ics bodies cause subtle parse failures. Always `printf` with `\r\n` or use a script that writes binary mode.
- **`UID` is a bash builtin** — name your shell variable `EVID` or `EV_UID`, not `UID`.
- **Proxy.** The server is fronted by Cloudflare Tunnel; from CN networks curl needs `--proxy "$PROXY"`. If the user is abroad, `proxy` in config can be `""`.
- **Authentication.** Radicale uses HTTP Basic with bcrypt htpasswd. `-u user:pass` works directly.
- **Calendar path.** Radicale's path is `/<user>/<calendar-uuid>/`. The UUID is assigned by the client when the calendar was first created and is stable. Find it with a depth-1 PROPFIND on `/<user>/`.
- **All-day DTEND is exclusive.** A single-day event on the 24th has DTEND on the 25th.
- **No DAV-on-public-internet auth wall.** This server is reachable from the public internet (the tunnel doesn't gate it with Access). Only the password protects it — never log or paste it.
