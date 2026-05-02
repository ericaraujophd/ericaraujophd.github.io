#!/usr/bin/env python3
"""
generate_presentations.py — Regenerate presentations.md from two sources:

  1. presentations.csv  — invited talks, panels, posters, keynotes (no published paper)
  2. pubs.bib           — @inproceedings entries (published conference papers)

Usage (run from the website root):
    python generate_presentations.py

CSV columns:
  date        ISO date, e.g. 2026-02-27
  type        talk | poster | panel | invited | keynote
  title       Title of the presentation
  event       Conference or event name
  location    City / country (or "Online")
  url         Conference URL (optional)
  slides_url  Link to slides/PDF (optional)
  notes       Short note, e.g. "In Portuguese", "With X et al." (optional)
"""

import csv
import re
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

try:
    import bibtexparser
    from bibtexparser.bparser import BibTexParser
    from bibtexparser.customization import convert_to_unicode
except ImportError:
    sys.exit(
        "bibtexparser not found.\n"
        "Install it with: pip install bibtexparser --break-system-packages"
    )

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
HERE     = Path(__file__).parent
BIB_PATH = HERE / "../rendercv/sources/pubs.bib"
CSV_PATH = HERE / "presentations.csv"
OUT_PATH = HERE / "presentations.md"

# ---------------------------------------------------------------------------
# Helpers shared with generate_publications.py
# ---------------------------------------------------------------------------

ERIC_NAME_FRAGMENTS = [
    "eric araújo", "eric araujo",
    "araújo, eric", "araujo, eric",
]


def _is_eric(name: str) -> bool:
    lower = name.lower()
    return any(frag in lower for frag in ERIC_NAME_FRAGMENTS)


def _normalize_author(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return raw
    if raw.startswith("**"):
        return raw
    if "," in raw:
        last, first = raw.split(",", 1)
        return f"{first.strip()} {last.strip()}"
    return raw


def format_authors(raw_field: str) -> str:
    tokens = raw_field.replace("\n", " ").split(" and ")
    result = []
    for token in tokens:
        name = _normalize_author(token)
        if not name.startswith("**") and _is_eric(name):
            name = f"**{name}**"
        result.append(name)
    return ", ".join(result)


def _clean(text: str) -> str:
    return re.sub(r"[{}]", "", text).strip()


def _try_int(val) -> int:
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0


# ---------------------------------------------------------------------------
# Load sources
# ---------------------------------------------------------------------------

def load_csv_presentations() -> list:
    """Read presentations.csv and return a list of dicts with a _year key."""
    items = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row = {k: v.strip() for k, v in row.items()}
            try:
                dt = datetime.strptime(row["date"], "%Y-%m-%d")
                row["_year"]  = dt.year
                row["_month"] = dt.month
                row["_day"]   = dt.day
            except ValueError:
                row["_year"] = row["_month"] = row["_day"] = 0
            row["_source"] = "csv"
            items.append(row)
    return items


def load_bib_inproceedings() -> list:
    """Load @inproceedings entries from pubs.bib as presentation dicts."""
    parser = BibTexParser(common_strings=True)
    parser.customization = convert_to_unicode
    with open(BIB_PATH, encoding="utf-8") as f:
        db = bibtexparser.load(f, parser=parser)

    items = []
    for entry in db.entries:
        if entry.get("ENTRYTYPE", "").lower() != "inproceedings":
            continue

        year  = _try_int(entry.get("year", "0"))
        month = _try_int(entry.get("month", "0"))

        doi = entry.get("doi", "").strip()
        url = entry.get("url", "").strip()
        link = f"https://doi.org/{doi}" if doi else url

        items.append({
            "_source": "bib",
            "_year":   year,
            "_month":  month,
            "_day":    0,
            "title":   _clean(entry.get("title", "Untitled")),
            "event":   _clean(entry.get("booktitle", "")),
            "location": _clean(entry.get("address", entry.get("location", ""))),
            "authors": format_authors(entry.get("author", "")),
            "url":     link,
            "slides_url": "",
            "notes":   "",
            "type":    "paper",   # marks it as a published paper
        })
    return items


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def _sort_key(item: dict):
    return (item["_year"], item["_month"], item["_day"])


def format_csv_item(item: dict) -> str:
    """Format one CSV (non-paper) presentation as a Markdown list item."""
    title     = item.get("title", "").strip()
    event     = item.get("event", "").strip()
    location  = item.get("location", "").strip()
    url       = item.get("url", "").strip()
    slides    = item.get("slides_url", "").strip()
    notes     = item.get("notes", "").strip()
    ptype     = item.get("type", "talk").strip()

    # Format: **Title** (or linked). Event. Location. [Slides.] [Notes.]
    title_md  = f"[{title}]({url})" if url else f"*{title}*"
    type_tag  = f"*({ptype})* " if ptype and ptype != "talk" else ""

    parts = [f"{type_tag}{title_md}. {event}."]
    if location:
        parts.append(f" {location}.")
    if slides:
        parts.append(f" [Slides]({slides}).")
    if notes:
        parts.append(f" *{notes}.*")

    return "- " + "".join(parts)


def format_bib_item(item: dict) -> str:
    """Format one bib-sourced conference paper as a Markdown list item."""
    title    = item.get("title", "").strip()
    event    = item.get("event", "").strip()
    location = item.get("location", "").strip()
    authors  = item.get("authors", "").strip()
    url      = item.get("url", "").strip()

    title_md = f"[{title}]({url})" if url else title

    parts = [f"{authors}. {title_md}."]
    if event:
        parts.append(f" *{event}*.")
    if location:
        parts.append(f" {location}.")

    return "- " + "".join(parts)


# ---------------------------------------------------------------------------
# Page builder
# ---------------------------------------------------------------------------

def build_page(all_items: list) -> str:
    # Group by year
    by_year: dict = defaultdict(list)
    for item in all_items:
        by_year[item["_year"]].append(item)

    lines = [
        "---",
        'title: "Presentations"',
        "---",
        "",
        "Talks, panels, and posters from 2021 onward. "
        "Published conference papers are listed under each year where applicable.",
        "",
        "---",
        "",
    ]

    for year in sorted(by_year.keys(), reverse=True):
        lines.append(f"## {year}")
        lines.append("")

        items = sorted(by_year[year], key=_sort_key, reverse=True)

        # Separate talks/posters from published papers
        talks  = [i for i in items if i["_source"] == "csv"]
        papers = [i for i in items if i["_source"] == "bib"]

        if talks:
            lines.append("### Talks & Presentations")
            lines.append("")
            for item in talks:
                lines.append(format_csv_item(item))
            lines.append("")

        if papers:
            lines.append("### Conference Papers")
            lines.append("")
            for item in papers:
                lines.append(format_bib_item(item))
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    csv_items = load_csv_presentations()
    print(f"Loaded {len(csv_items)} entries from {CSV_PATH.name}")

    bib_items = load_bib_inproceedings()
    print(f"Loaded {len(bib_items)} @inproceedings from {BIB_PATH.name}")

    all_items = csv_items + bib_items
    content   = build_page(all_items)
    OUT_PATH.write_text(content, encoding="utf-8")
    print(f"Wrote {OUT_PATH.name} ({len(all_items)} total entries)")


if __name__ == "__main__":
    main()
