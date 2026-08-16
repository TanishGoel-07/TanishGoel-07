#!/usr/bin/env python3
"""
Scrapes the public, unauthenticated GitHub contributions calendar HTML
fragment (the same endpoint your profile page uses) and dumps it to
data/contributions.json.

Endpoint: https://github.com/users/<username>/contributions
No token needed - this is the plain HTML GitHub renders for the little
green-square calendar on every profile page.
"""
import json
import os
import re
import sys

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_USERNAME", "TanishGoel-07")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")


def fetch():
    resp = requests.get(URL, headers={"User-Agent": "profile-readme-bot"}, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse(html: str):
    soup = BeautifulSoup(html, "html.parser")
    cells = soup.select("td.ContributionCalendar-day")

    days = []
    for cell in cells:
        date = cell.get("data-date")
        level = cell.get("data-level")
        if date is None or level is None:
            continue
        tool_tip_id = cell.get("id")
        count = 0
        if tool_tip_id:
            tip = soup.select_one(f"tool-tip[for='{tool_tip_id}']")
            if tip:
                match = re.search(r"(\d+|No)\s+contribution", tip.text)
                if match:
                    count = 0 if match.group(1) == "No" else int(match.group(1))
        days.append({"date": date, "level": int(level), "count": count})

    days.sort(key=lambda d: d["date"])
    return days


def main():
    html = fetch()
    days = parse(html)
    if not days:
        print("No contribution cells found - GitHub may have changed markup.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump({"username": USERNAME, "days": days}, f, indent=2)

    print(f"Wrote {len(days)} days to {OUT_PATH}")


if __name__ == "__main__":
    main()
