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

If a PR URL is provided as argument, follow these steps **in strict order**:

#### Step 1: Fetch PR details

```bash
bash ~/.claude/skills/approve-pr/scripts/approve_pr.sh "<PR_URL>"
```

The script outputs PR metadata (title, author, branch, changes, changed files) but does NOT approve. Parse the output to extract PR_TITLE, PR_URL, PR_NUM, and PR_REPO.

#### Step 2: Send notification email (MUST succeed before approve)

First, ensure Outlook authentication is ready by calling `mcp__outlook__ensure_auth`. If it fails, call `mcp__outlook__authorize` to re-authenticate.

Then send an email to andy.du@sap.com via `mcp__outlook__send_email`:

- **To:** andy.du@sap.com
- **Subject:** PR Approved: `<PR title>`
- **Body:** Include the PR link, repo, author, branch, changes, and a brief note that the PR has been approved.

If the email fails due to auth issues, call `mcp__outlook__authorize` and retry once. **If it still fails after retry, STOP immediately. Do NOT proceed to Step 3. Report the failure to the user.**

#### Step 3: Approve the PR (only after email succeeds)

Run gh to approve:

```bash
GH_TOKEN="$APPROVE_PR_TOKEN" GH_ENTERPRISE_TOKEN="$APPROVE_PR_TOKEN" gh pr review "<PR_URL>" --approve --body "LGTM 👍"
```

Report the final result to the user.

## Configuration

- `APPROVE_PR_TOKEN` (required): Your personal access token for GitHub Enterprise. Only used by this skill — mapped to `GH_TOKEN` at runtime without affecting other `gh` commands.
- `GH_HOST` (optional): Override the default host (`github.wdf.sap.corp`).
