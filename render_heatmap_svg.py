#!/usr/bin/env python3
"""
Renders data/contributions.json into contrib-heatmap.svg.
Animation is pure SVG/CSS (staggered fade+grow per cell) - no JS,
so it plays fine on GitHub's sanitized README renderer.
"""
import json
import os
from datetime import datetime

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "contrib-heatmap.svg")

# level 0..4 -> color (terminal green ramp, level 0 = empty cell)
COLORS = ["#0d1117", "#0e4429", "#006d32", "#26a641", "#39d353"]

CELL = 11
GAP = 3
LEFT_PAD = 28
TOP_PAD = 20


def load_days():
    with open(DATA_PATH) as f:
        payload = json.load(f)
    return payload["username"], payload["days"]


def build_weeks(days):
    """Bucket days into week-columns aligned Sun-Sat, like GitHub's own graph."""
    weeks = []
    current_week = [None] * 7
    for d in days:
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        dow = (dt.weekday() + 1) % 7  # convert Mon=0 -> Sun=0
        if dow == 0 and any(current_week):
            weeks.append(current_week)
            current_week = [None] * 7
        current_week[dow] = d
    if any(current_week):
        weeks.append(current_week)
    return weeks


def render(username, weeks):
    width = LEFT_PAD + len(weeks) * (CELL + GAP) + 10
    height = TOP_PAD + 7 * (CELL + GAP) + 10

    rects = []
    delay_step = 0.0035
    idx = 0
    for w, week in enumerate(weeks):
        for d, day in enumerate(week):
            if day is None:
                continue
            x = LEFT_PAD + w * (CELL + GAP)
            y = TOP_PAD + d * (CELL + GAP)
            color = COLORS[min(day["level"], 4)]
            delay = idx * delay_step
            idx += 1
            title = f"{day['count']} contributions on {day['date']}"
            rects.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="2" ry="2" fill="{color}" style="animation-delay:{delay:.4f}s">'
                f"<title>{title}</title></rect>"
            )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" font-family="'Courier New', monospace">
  <style>
    .cell {{
      opacity: 0;
      transform-box: fill-box;
      transform-origin: center;
      transform: scale(0.4);
      animation: pop 0.5s ease-out forwards;
    }}
    @keyframes pop {{
      0%   {{ opacity: 0; transform: scale(0.4); }}
      60%  {{ opacity: 1; transform: scale(1.15); }}
      100% {{ opacity: 1; transform: scale(1); }}
    }}
    .label {{ fill: #8b949e; font-size: 9px; }}
  </style>
  <rect x="0" y="0" width="{width}" height="{height}" fill="#0d1117"/>
  <text x="4" y="{TOP_PAD + 3 * (CELL+GAP)}" class="label">{username}</text>
  {''.join(rects)}
</svg>"""
    return svg


def main():
    username, days = load_days()
    weeks = build_weeks(days)
    svg = render(username, weeks)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
