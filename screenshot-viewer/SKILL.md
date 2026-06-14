---
name: screenshot-viewer
description: Use when user wants to view a folder of screenshots as a slideshow/player, or says "生成截图查看器", "screenshot viewer", "查看截图", "review screenshots". Generates a self-contained HTML player from numbered screenshot files.
---

# Screenshot Viewer

Generate a self-contained HTML player from a folder of screenshots. Images are base64-embedded for full portability.

## Usage

```bash
python ~/.claude/skills/screenshot-viewer/scripts/generate.py <screenshot_folder> [--output <output.html>] [--interval <seconds>]
```

## Parameters

- `<screenshot_folder>` (required): Path to folder containing screenshot images
- `--output` (optional): Output HTML path. Defaults to `<screenshot_folder>/viewer.html`
- `--interval` (optional): Auto-play interval in seconds. Defaults to 2

## Supported Formats

png, jpg, jpeg, gif, webp, bmp

## Sorting

Files are sorted by the leading number in their filename (e.g., `1-login.png`, `02-click.png`, `100_result.png`). Files without a leading number are sorted alphabetically after numbered files.

## When to Use

- User provides a screenshot folder and wants to review steps visually
- After GluCode tests leave screenshots to review
- User says "生成截图查看器", "播放截图", "screenshot player"
- User wants to turn a folder of images into a browsable slideshow

## Example

```bash
python ~/.claude/skills/screenshot-viewer/scripts/generate.py ~/Desktop/test-screenshots --interval 3
# Opens: ~/Desktop/test-screenshots/viewer.html
```

After generating, open the HTML file in a browser:
```bash
start <output.html>   # Windows
open <output.html>    # macOS
```
