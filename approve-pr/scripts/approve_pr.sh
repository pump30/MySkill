#!/usr/bin/env bash
set -euo pipefail

GH_HOST="${GH_HOST:-github.wdf.sap.corp}"
PR_URL="${1:-}"

if [[ -z "${APPROVE_PR_TOKEN:-}" ]]; then
  echo "❌ APPROVE_PR_TOKEN environment variable is not set."
  echo "Set it in Claude Code settings.json env or: export APPROVE_PR_TOKEN=ghp_..."
  exit 1
fi
export GH_TOKEN="$APPROVE_PR_TOKEN"
export GH_ENTERPRISE_TOKEN="$APPROVE_PR_TOKEN"

# If no PR URL provided, list PRs requesting review from current user
if [[ -z "$PR_URL" ]]; then
  echo "🔍 Searching for PRs requesting your review on $GH_HOST..."
  echo ""

  PRS=$(GH_HOST="$GH_HOST" gh search prs --review-requested=@me --state=open --json url,title,author,repository --limit 20 2>/dev/null || true)

  if [[ -z "$PRS" || "$PRS" == "[]" ]]; then
    echo "No open PRs requesting your review."
    exit 0
  fi

  echo "$PRS" | python3 -c "
import json, sys
prs = json.load(sys.stdin)
for i, pr in enumerate(prs, 1):
    author = pr.get('author', {})
    author_login = author.get('login', 'unknown') if isinstance(author, dict) else str(author)
    print(f\"  [{i}] {pr['repository']['nameWithOwner']}  —  {pr['title']}\")
    print(f\"      Author: {author_login}  |  {pr['url']}\")
    print()
"
  echo "---"
  echo "Pass a PR URL as argument to approve: /approve-pr <url>"
  exit 0
fi

# Validate the URL looks like a PR
if [[ ! "$PR_URL" =~ /pull/[0-9]+ ]]; then
  echo "❌ Invalid PR URL: $PR_URL"
  echo "Expected format: https://$GH_HOST/<owner>/<repo>/pull/<number>"
  exit 1
fi

# Extract repo and PR number
REPO=$(echo "$PR_URL" | sed -E 's|https?://[^/]+/([^/]+/[^/]+)/pull/[0-9]+.*|\1|')
PR_NUM=$(echo "$PR_URL" | sed -E 's|.*/pull/([0-9]+).*|\1|')

echo "📋 PR #$PR_NUM in $REPO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Fetch PR details
PR_JSON=$(gh pr view "$PR_URL" --json title,author,additions,deletions,changedFiles,baseRefName,headRefName 2>&1)

TITLE=$(echo "$PR_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['title'])")
AUTHOR=$(echo "$PR_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['author']['login'])")
ADDS=$(echo "$PR_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['additions'])")
DELS=$(echo "$PR_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['deletions'])")
CHANGED=$(echo "$PR_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['changedFiles'])")
BASE=$(echo "$PR_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['baseRefName'])")
HEAD=$(echo "$PR_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['headRefName'])")

echo "  Title:    $TITLE"
echo "  Author:   $AUTHOR"
echo "  Branch:   $HEAD → $BASE"
echo "  Changes:  $CHANGED files (+$ADDS / -$DELS)"
echo ""

# Show changed files
echo "📁 Changed files:"
gh pr diff "$PR_URL" --name-only 2>/dev/null | sed 's/^/  /'
echo ""

# Output PR metadata for the caller
echo "PR_TITLE=$TITLE"
echo "PR_AUTHOR=$AUTHOR"
echo "PR_URL=$PR_URL"
echo "PR_NUM=$PR_NUM"
echo "PR_REPO=$REPO"
echo "PR_BRANCH=$HEAD → $BASE"
echo "PR_CHANGES=$CHANGED files (+$ADDS / -$DELS)"
