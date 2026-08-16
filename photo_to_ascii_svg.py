#!/usr/bin/env python3
"""
Converts a photo into a self-typing, monochrome ASCII-art SVG.

Usage:
    python3 scripts/photo_to_ascii_svg.py path/to/photo.jpg ascii-portrait.svg

The animation is pure SVG/CSS (each row "types in" via a clip-path wipe,
staggered by row index) - no JavaScript, no external stylesheet, so it
survives GitHub's README sanitizer.
"""
import sys

from PIL import Image

RAMP = "@%#*+=-:. "  # dark -> light
COLS = 100
ROW_ASPECT = 2.0  # terminal chars are taller than wide; compensate
CHAR_W = 6.2
CHAR_H = 12
FONT_SIZE = 12
FG = "#39d353"
BG = "#0d1117"


def image_to_ascii(path, cols=COLS):
    img = Image.open(path).convert("L")
    w, h = img.size
    rows = max(1, int((h / w) * cols / ROW_ASPECT))
    img = img.resize((cols, rows))
    pixels = list(img.getdata())

    lines = []
    for r in range(rows):
        row_pixels = pixels[r * cols:(r + 1) * cols]
        line = "".join(RAMP[min(len(RAMP) - 1, p * len(RAMP) // 256)] for p in row_pixels)
        lines.append(line)
    return lines


def escape(ch):
    return {"&": "&amp;", "<": "&lt;", ">": "&gt;"}.get(ch, ch)


def render_svg(lines):
    width = int(len(lines[0]) * CHAR_W) + 20
    height = int(len(lines) * CHAR_H) + 20

    text_rows = []
    clip_rects = []
    row_delay = 0.05
    for i, line in enumerate(lines):
        y = 20 + i * CHAR_H
        safe = "".join(escape(c) for c in line)
        text_rows.append(
            f'<text x="10" y="{y}" clip-path="url(#wipe{i})">{safe}</text>'
        )
        row_width = len(line) * CHAR_W + 10
        delay = i * row_delay
        clip_rects.append(
            f'<clipPath id="wipe{i}"><rect x="0" y="{y - FONT_SIZE}" width="0" height="{CHAR_H + 4}">'
            f'<animate attributeName="width" from="0" to="{row_width}" dur="0.35s" '
            f'begin="{delay:.3f}s" fill="freeze"/></rect></clipPath>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    {''.join(clip_rects)}
  </defs>
  <style>
    text {{
      font-family: 'Courier New', monospace;
      font-size: {FONT_SIZE}px;
      fill: {FG};
      white-space: pre;
    }}
  </style>
  <rect x="0" y="0" width="{width}" height="{height}" fill="{BG}"/>
  {''.join(text_rows)}
</svg>"""
    return svg


def main():
    if len(sys.argv) != 3:
        print("usage: photo_to_ascii_svg.py <input-photo> <output.svg>")
        sys.exit(1)
    lines = image_to_ascii(sys.argv[1])
    svg = render_svg(lines)
    with open(sys.argv[2], "w") as f:
        f.write(svg)
    print(f"Wrote {sys.argv[2]} ({len(lines)} rows x {len(lines[0])} cols)")


if __name__ == "__main__":
    main()
