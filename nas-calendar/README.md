# nas-calendar

Add, update, and delete calendar events on a self-hosted Radicale (CalDAV) server via raw HTTP.

## Setup

1. Copy `config.example.json` to `~/.config/nas-calendar/config.json` and fill in your server details.
2. Symlink the skill into Claude Code:
   ```bash
   ln -s "$(pwd)/nas-calendar" ~/.claude/skills/nas-calendar
   ```
3. Requires `curl`, `jq`, and bash.

## Usage

Trigger phrases (Chinese or English):

- "加一个日程：明天下午2点开会"
- "把这张排班表加到日历"
- "删掉昨天那个日程"
- "改一下日程的标题"

The skill picks stable UIDs so re-running the same operation updates instead of duplicates.
