---
name: approve-pr
description: Approve a GitHub Enterprise PR that is requesting your review. Use when the user says "approve pr", "approve pull request", wants to review and approve PRs, or uses /approve-pr. Lists pending review requests or approves a specific PR by URL. Targets SAP GitHub Enterprise (github.wdf.sap.corp).
---

# Approve PR

Approve open PRs on SAP GitHub Enterprise (`github.wdf.sap.corp`) that are requesting your review.

## Usage

Accept an optional PR URL as the skill argument.

### List pending review requests

If no argument is provided, list all open PRs requesting the user's review:

```bash
bash ~/.claude/skills/approve-pr/scripts/approve_pr.sh
```

### Approve a specific PR

If a PR URL is provided as argument:

```bash
bash ~/.claude/skills/approve-pr/scripts/approve_pr.sh "<PR_URL>"
```

The script shows PR details (title, author, branch, changed files) before approving.

### Post-approve notification

After a successful approve, send an email to andy.du@sap.com via Outlook MCP:

- **To:** andy.du@sap.com
- **Subject:** PR Approved: `<PR title>`
- **Body:** Include the PR link and a brief note that the PR has been approved.

Use `mcp__outlook__send_email` to send the notification.

## Configuration

- `APPROVE_PR_TOKEN` (required): Your personal access token for GitHub Enterprise. Only used by this skill — mapped to `GH_TOKEN` at runtime without affecting other `gh` commands.
- `GH_HOST` (optional): Override the default host (`github.wdf.sap.corp`).
