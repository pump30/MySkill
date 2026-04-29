---
name: send-email
description: Send an email notification. Use when the user says "send email", "email me", "发邮件", "通知我", or uses /send-email. Default recipient is 1069235479@qq.com. Supports custom recipient, subject, and body.
---

# Send Email

Send email notifications via Gmail SMTP (proxied). Default recipient: `1069235479@qq.com`.

## Usage

```bash
python ~/.claude/skills/send-email/scripts/send.py --subject "<subject>" --body "<body>" [--to "<recipient>"]
```

## Parameters

- `--subject` (required): Email subject line
- `--body` (required): Email body content (supports plain text)
- `--to` (optional): Recipient email. Defaults to `1069235479@qq.com`

## Examples

```bash
# Send to default recipient (QQ邮箱)
python ~/.claude/skills/send-email/scripts/send.py --subject "任务完成" --body "播客转录已完成"

# Send to a different recipient
python ~/.claude/skills/send-email/scripts/send.py --subject "Report" --body "Here is the report" --to "someone@example.com"
```

## When to Use

- User asks to send an email or notify someone
- User says "发个邮件", "邮件通知", "email me", "send email"
- After completing a long task and user wants notification
