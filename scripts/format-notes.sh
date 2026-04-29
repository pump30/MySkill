#!/bin/bash

# 将 README.md（Show Notes + 转录文本）格式化为结构化笔记
# 需要 Claude API 或在 Claude Code 中以 skill 方式调用
#
# 本脚本输出格式化指令，实际格式化由 Claude 完成

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
echo_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
echo_error() { echo -e "${RED}[ERROR]${NC} $1"; }

if [ $# -lt 1 ]; then
    echo "用法: $0 <播客目录路径>"
    echo ""
    echo "将 README.md 格式化为结构化笔记。"
    echo "需要在 Claude Code 中运行，由 AI 执行格式化。"
    echo ""
    echo "输出格式："
    echo "  - YAML 元数据（标题、嘉宾、标签等）"
    echo "  - 嘉宾介绍"
    echo "  - 核心观点（3条金句）"
    echo "  - 分章节内容摘要"
    echo "  - 金句摘录"
    echo "  - 行动清单"
    exit 1
fi

INPUT="$1"

if [ -d "$INPUT" ]; then
    EPISODE_DIR="$INPUT"
else
    EPISODE_DIR=$(find "$HOME/Research/Podcast" -maxdepth 1 -type d -name "*$INPUT*" 2>/dev/null | head -1)
fi

README="$EPISODE_DIR/README.md"

if [ ! -f "$README" ]; then
    echo_error "README.md 不存在: $README"
    exit 1
fi

WORD_COUNT=$(wc -m < "$README" | xargs)
echo_info "播客目录: $EPISODE_DIR"
echo_info "文档大小: $WORD_COUNT 字符"
echo ""
echo "===FORMAT_REQUEST==="
echo "FILE: $README"
echo "INSTRUCTION: 将此播客转录文档格式化为结构化笔记，格式如下："
echo ""
cat << 'TEMPLATE'
## 输出格式要求

1. **YAML Front Matter** — title, podcast, host, guest, episode_id, url, published, duration, tags
2. **嘉宾介绍** — 简短背景（3-5条）
3. **核心观点** — 3条最有价值的引用（blockquote）
4. **分章节内容** — 按主题分3-6个大章节，每章含：
   - 小节标题
   - 要点列表或表格
   - 关键引用
5. **金句摘录** — 5-8条精华语录
6. **行动清单** — 5条可执行的 todo

## 格式规范

- 使用 Markdown 标题层级（##, ###）
- 善用表格对比信息
- 用 blockquote 标记金句
- 用代码块标记公式/模型
- 保持简洁，去除口语化表达和重复内容
- 保留原始观点，不添加个人评论
TEMPLATE
echo ""
echo "===END_FORMAT_REQUEST==="
