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

### [xiaoyuzhou-podcast](./xiaoyuzhou-podcast/)

自动下载小宇宙播客音频并生成完整转录文本，最终输出结构化笔记。

**Features:**
- 自动下载小宇宙播客音频和节目信息
- FunASR paraformer-zh 高质量中文语音识别（准确度 > 90%）
- Mac MPS (Metal) 加速，转录速度快 2-3 倍
- 自动合并 Show Notes + 转录文本
- **结构化笔记格式化**（核心观点、分章节摘要、金句、行动清单）
- 支持热词优化、Notion 同步

**Setup:**

1. Copy the `xiaoyuzhou-podcast` folder to `~/.claude/skills/xiaoyuzhou-podcast/`
2. Run `~/.claude/skills/xiaoyuzhou-podcast/scripts/install.sh` to install dependencies
3. Requires: macOS M1/M2/M3, Python 3.8+, ~2GB disk for ASR models

**Usage:**

```
# Give Claude a xiaoyuzhoufm.com link — the skill activates automatically
https://www.xiaoyuzhoufm.com/episode/<episode_id>
```

### [send-email](./send-email/)

通过 Gmail SMTP 发送邮件通知，支持 HTTP 代理（适配国内网络环境）。

**Features:**
- Gmail SMTP (SSL 465) 发送邮件
- HTTP CONNECT 代理支持（解决国内 Gmail 连接问题）
- 默认收件人可配置，也支持自定义收件人
- 纯 Python 实现，无额外依赖

**Setup:**

1. Copy the `send-email` folder to `~/.claude/skills/send-email/`
2. Edit `scripts/send.py` to configure your SMTP credentials and proxy

**Usage:**

```
/send-email                          # Claude will ask for subject and body
发邮件 主题xxx 内容xxx               # Natural language trigger
```

## Installation

```bash
# Clone this repo
git clone https://github.com/pump30/MySkill.git

# Symlink a skill into Claude Code
ln -s "$(pwd)/MySkill/approve-pr" ~/.claude/skills/approve-pr
ln -s "$(pwd)/MySkill/xiaoyuzhou-podcast" ~/.claude/skills/xiaoyuzhou-podcast
ln -s "$(pwd)/MySkill/send-email" ~/.claude/skills/send-email
```
