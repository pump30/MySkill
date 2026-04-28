# MySkill

A collection of Claude Code skills for SAP GitHub Enterprise workflows.

## Skills

### [approve-pr](./approve-pr/)

Approve open PRs on SAP GitHub Enterprise (`github.wdf.sap.corp`) that are requesting your review.

**Features:**
- List all PRs pending your review
- Approve a specific PR by URL
- Auto-authenticate Outlook and send email notification before approving
- Email-first workflow: PR is only approved after notification email succeeds

**Setup:**

1. Copy the `approve-pr` folder to `~/.claude/skills/approve-pr/`
2. Set `APPROVE_PR_TOKEN` in Claude Code settings (`env` section) with your GitHub Enterprise personal access token

**Usage:**

```
/approve-pr                          # List PRs requesting your review
/approve-pr <PR_URL>                 # Approve a specific PR
```

## Installation

```bash
# Clone this repo
git clone https://github.wdf.sap.corp/I572881/MySkill.git

# Symlink a skill into Claude Code
ln -s "$(pwd)/MySkill/approve-pr" ~/.claude/skills/approve-pr
```
