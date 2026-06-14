#!/usr/bin/env python3
"""Generate a self-contained HTML screenshot viewer/player from a folder of images."""

import argparse
import base64
import mimetypes
import re
import sys
from pathlib import Path

SUPPORTED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'}

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Screenshot Viewer - {title}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  background: #1a1a2e;
  color: #e0e0e0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}}
.header {{
  padding: 6px 16px;
  background: #16213e;
  border-bottom: 1px solid #0f3460;
  display: flex;
  align-items: center;
  justify-content: space-between;
}}
.header h1 {{
  font-size: 14px;
  font-weight: 500;
  color: #a0a0a0;
}}
.filename {{
  font-size: 14px;
  color: #4fc3f7;
  font-family: "Cascadia Code", "Fira Code", monospace;
}}
.viewer {{
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  position: relative;
  overflow: hidden;
}}
.viewer img {{
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: opacity 0.2s ease;
}}
.controls {{
  padding: 8px 16px;
  background: #16213e;
  border-top: 1px solid #0f3460;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}}
.controls button {{
  background: #0f3460;
  border: 1px solid #1a4a7a;
  color: #e0e0e0;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}}
.controls button:hover {{
  background: #1a4a7a;
  border-color: #4fc3f7;
}}
.controls button:active {{
  transform: scale(0.95);
}}
.controls button.active {{
  background: #4fc3f7;
  color: #1a1a2e;
  border-color: #4fc3f7;
}}
.progress {{
  font-size: 14px;
  color: #a0a0a0;
  min-width: 60px;
  text-align: center;
  font-family: "Cascadia Code", "Fira Code", monospace;
}}
.progress-bar {{
  flex: 1;
  max-width: 300px;
  height: 4px;
  background: #0f3460;
  border-radius: 2px;
  overflow: hidden;
  cursor: pointer;
}}
.progress-bar .fill {{
  height: 100%;
  background: #4fc3f7;
  transition: width 0.2s ease;
}}
.interval-control {{
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #a0a0a0;
}}
.interval-control input {{
  width: 50px;
  background: #0f3460;
  border: 1px solid #1a4a7a;
  color: #e0e0e0;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  text-align: center;
}}
.nav-hint {{
  position: fixed;
  bottom: 80px;
  right: 24px;
  font-size: 11px;
  color: #555;
}}
</style>
</head>
<body>
<div class="header">
  <h1>{title}</h1>
  <span class="filename" id="filename"></span>
</div>
<div class="viewer">
  <img id="screenshot" src="" alt="Screenshot">
</div>
<div class="controls">
  <button id="prevBtn" title="Previous (←)">&#9664; Prev</button>
  <button id="playBtn" title="Play/Pause (Space)">&#9654; Play</button>
  <button id="nextBtn" title="Next (→)">Next &#9654;</button>
  <div class="progress-bar" id="progressBar"><div class="fill" id="progressFill"></div></div>
  <span class="progress" id="progress"></span>
  <div class="interval-control">
    <label for="intervalInput">Interval:</label>
    <input type="number" id="intervalInput" value="{interval}" min="0.5" max="30" step="0.5">
    <span>s</span>
  </div>
</div>
<div class="nav-hint">← → keys to navigate &middot; Space to play/pause</div>

<script>
const images = {images_json};

let current = 0;
let playing = false;
let timer = null;
let interval = {interval};

const img = document.getElementById('screenshot');
const filename = document.getElementById('filename');
const progress = document.getElementById('progress');
const progressFill = document.getElementById('progressFill');
const playBtn = document.getElementById('playBtn');
const intervalInput = document.getElementById('intervalInput');

function show(index) {{
  if (index < 0) index = images.length - 1;
  if (index >= images.length) index = 0;
  current = index;
  img.src = images[current].data;
  filename.textContent = images[current].name;
  progress.textContent = (current + 1) + ' / ' + images.length;
  progressFill.style.width = ((current + 1) / images.length * 100) + '%';
}}

function next() {{ show(current + 1); }}
function prev() {{ show(current - 1); }}

function togglePlay() {{
  playing = !playing;
  playBtn.innerHTML = playing ? '&#9646;&#9646; Pause' : '&#9654; Play';
  playBtn.classList.toggle('active', playing);
  if (playing) {{
    timer = setInterval(next, interval * 1000);
  }} else {{
    clearInterval(timer);
    timer = null;
  }}
}}

document.getElementById('prevBtn').addEventListener('click', prev);
document.getElementById('nextBtn').addEventListener('click', next);
document.getElementById('playBtn').addEventListener('click', togglePlay);

document.getElementById('progressBar').addEventListener('click', function(e) {{
  const rect = this.getBoundingClientRect();
  const ratio = (e.clientX - rect.left) / rect.width;
  show(Math.floor(ratio * images.length));
}});

intervalInput.addEventListener('change', function() {{
  interval = parseFloat(this.value) || 2;
  if (playing) {{
    clearInterval(timer);
    timer = setInterval(next, interval * 1000);
  }}
}});

document.addEventListener('keydown', function(e) {{
  if (e.target.tagName === 'INPUT') return;
  if (e.key === 'ArrowLeft') prev();
  else if (e.key === 'ArrowRight') next();
  else if (e.key === ' ') {{ e.preventDefault(); togglePlay(); }}
}});

show(0);
</script>
</body>
</html>'''


def extract_sort_key(filename: str):
    match = re.match(r'^(\d+)', filename)
    if match:
        return (0, int(match.group(1)), filename)
    return (1, 0, filename)


def get_mime_type(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    return mime or 'image/png'


def encode_image(path: Path) -> str:
    mime = get_mime_type(path)
    with open(path, 'rb') as f:
        data = base64.b64encode(f.read()).decode('ascii')
    return f'data:{mime};base64,{data}'


def main():
    parser = argparse.ArgumentParser(description='Generate HTML screenshot viewer')
    parser.add_argument('folder', help='Path to screenshot folder')
    parser.add_argument('--output', '-o', help='Output HTML file path')
    parser.add_argument('--interval', '-i', type=float, default=2,
                        help='Auto-play interval in seconds (default: 2)')
    args = parser.parse_args()

    folder = Path(args.folder).resolve()
    if not folder.is_dir():
        print(f'Error: {folder} is not a directory', file=sys.stderr)
        sys.exit(1)

    images = []
    for f in folder.iterdir():
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
            images.append(f)

    if not images:
        print(f'Error: No image files found in {folder}', file=sys.stderr)
        sys.exit(1)

    images.sort(key=lambda p: extract_sort_key(p.name))

    print(f'Found {len(images)} images, encoding...')

    images_json_list = []
    for i, img_path in enumerate(images):
        data_uri = encode_image(img_path)
        images_json_list.append(f'{{"name":"{img_path.name}","data":"{data_uri}"}}')
        print(f'  [{i+1}/{len(images)}] {img_path.name}')

    images_json = '[' + ','.join(images_json_list) + ']'

    output_path = Path(args.output) if args.output else folder / 'viewer.html'

    html = HTML_TEMPLATE.format(
        title=folder.name,
        interval=args.interval,
        images_json=images_json,
    )

    output_path.write_text(html, encoding='utf-8')
    print(f'\nGenerated: {output_path}')
    print(f'Open in browser to view.')


if __name__ == '__main__':
    main()
