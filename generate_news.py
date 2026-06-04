#!/usr/bin/env python3
"""
generate_news.py — Rebuild updates.md and the news snippet in index.md from news.csv.

Usage:
    python generate_news.py

Add a new item by appending a row to news.csv, then run this script.
The script rewrites:
  - updates.md  (full archive, newest first)
  - index.md    (replaces the block between NEWS_START / NEWS_END markers)

CSV columns:
  date        ISO date, e.g. 2025-07-19
  type        One of: publication | presentation | talk | service | award | other
  title       Short title (used as bold label)
  description Full sentence(s). Markdown is allowed (links, *italics*, **bold**).
  url         Optional link attached to the title. Leave blank if none.
"""

import csv
import re
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent
CSV_PATH   = HERE / "news.csv"
UPDATES_MD = HERE / "updates.md"
INDEX_MD   = HERE / "index.md"

# Markers that delimit the auto-generated block inside index.md
NEWS_START = "<!-- NEWS_START -->"
NEWS_END   = "<!-- NEWS_END -->"

# How many items to show on the homepage
HOMEPAGE_ITEMS = 6


def load_items():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        items = []
        for row in reader:
            row["date"] = row["date"].strip()
            row["_dt"] = datetime.strptime(row["date"], "%Y-%m-%d")
            items.append(row)
    items.sort(key=lambda r: r["_dt"], reverse=True)
    return items


def format_item(item, *, show_date=True):
    """Return a single Markdown paragraph for one news item."""
    date_str = item["_dt"].strftime("%B %-d, %Y") if show_date else ""
    title    = item["title"].strip()
    desc     = item["description"].strip()
    url      = item["url"].strip()

    # If there's a URL, hyperlink the title
    title_md = f"[{title}]({url})" if url else f"**{title}**"

    if show_date:
        return f"**{date_str}** — {title_md}  \n{desc}"
    else:
        return f"{title_md}  \n{desc}"


def build_updates_md(items):
    lines = [
        "---",
        'title: "News & Updates"',
        "---",
        "",
        "Recent activity is also visible on the [main page](index.md).",
        "",
        "---",
        "",
    ]

    by_year = defaultdict(list)
    for item in items:
        by_year[item["_dt"].year].append(item)

    for year in sorted(by_year.keys(), reverse=True):
        lines.append(f"## {year}")
        lines.append("")
        for item in by_year[year]:
            lines.append(format_item(item))
            lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def build_homepage_snippet(items):
    """Return the Markdown block to inject between the NEWS markers in index.md."""
    lines = [NEWS_START, ""]
    for item in items[:HOMEPAGE_ITEMS]:
        lines.append(format_item(item))
        lines.append("")
    lines.append(f"[See all past updates →](updates.md)")
    lines.append("")
    lines.append(NEWS_END)
    return "\n".join(lines)


def update_index_md(snippet):
    text = INDEX_MD.read_text(encoding="utf-8")
    if NEWS_START not in text:
        print(
            f"WARNING: {NEWS_START} marker not found in index.md.\n"
            "Add the following two comment lines to index.md to mark where the news block goes:\n"
            f"  {NEWS_START}\n"
            f"  {NEWS_END}\n"
            "The script will fill in everything between them."
        )
        return False

    pattern = re.compile(
        re.escape(NEWS_START) + r".*?" + re.escape(NEWS_END),
        re.DOTALL,
    )
    new_text = pattern.sub(snippet, text)
    INDEX_MD.write_text(new_text, encoding="utf-8")
    return True


def main():
    items = load_items()
    print(f"Loaded {len(items)} items from {CSV_PATH.name}")

    # Rebuild updates.md
    UPDATES_MD.write_text(build_updates_md(items), encoding="utf-8")
    print(f"Wrote {UPDATES_MD.name}")

    # Inject news block into index.md
    snippet = build_homepage_snippet(items)
    if update_index_md(snippet):
        print(f"Updated news block in {INDEX_MD.name}")
    else:
        print(f"Skipped {INDEX_MD.name} (see warning above)")


if __name__ == "__main__":
    main()
