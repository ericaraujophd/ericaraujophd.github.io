#!/usr/bin/env python3
"""
to_website.py — Regenerate MyST website source files from data/*.json.

Writes to:
  news.csv
  presentations.csv
  students.csv
  publications/YYYY-YYYY.md   (one per period)
  presentations.md

Usage (run from repo root):
    python scripts/to_website.py
"""

import csv, json, re, textwrap
from collections import defaultdict
from pathlib import Path

ROOT    = Path(__file__).parent.parent
DATA    = ROOT / "data"
WEBSITE = ROOT

def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))

def visible_web(items):
    return [x for x in items if x.get("visible_web", True)]

def clean_md(s):
    """Strip ** markers from author names for plain CSV/text contexts."""
    return re.sub(r"\*\*([^*]+)\*\*", r"\1", s or "")

# ---------------------------------------------------------------------------
# news.csv
# ---------------------------------------------------------------------------

def write_news():
    all_items = (
        load("publications.json") +
        load("presentations.json") +
        load("grants.json") +
        load("service.json")
    )
    news = [x for x in all_items if x.get("news") and x.get("visible_web", True)]

    # Build description per item type
    def describe(x):
        blurb = x.get("news_blurb")
        if blurb:
            return blurb
        t = x.get("type","")
        if t in ("journal","conference","book-chapter","proceedings","thesis"):
            authors_clean = ", ".join(clean_md(a) for a in x.get("authors", []))
            return f"Published: *{x['title']}*. {x['venue']}. {authors_clean}."
        if t in ("talk","poster","panel","invited","keynote"):
            return f"Presented *{x['title']}* at {x.get('event','')}. {x.get('location','')}."
        if t == "fellowship":
            return f"Awarded {x['name']} ({x.get('institution','')})."
        if t == "defense-committee":
            return x.get("summary","")
        return x.get("summary") or x.get("title","")

    def news_date(x):
        d = x.get("date") or f"{x.get('start_date','')}-01" or f"{x.get('year','')}-01-01"
        return str(d)[:10]

    def news_type(x):
        t = x.get("type","")
        if t in ("journal","conference","book-chapter","proceedings"): return "publication"
        if t in ("talk","poster","panel","invited","keynote"):         return "presentation"
        if t == "fellowship":                                          return "award"
        if t == "defense-committee":                                   return "service"
        return t

    out = sorted(news, key=news_date, reverse=True)
    path = WEBSITE / "news.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date","type","title","description","url"])
        for x in out:
            w.writerow([
                news_date(x),
                news_type(x),
                x.get("name") or x.get("title",""),
                describe(x),
                x.get("url",""),
            ])
    print(f"  news.csv: {len(out)} entries")

# ---------------------------------------------------------------------------
# presentations.csv
# ---------------------------------------------------------------------------

def write_presentations():
    items = visible_web(load("presentations.json"))
    path  = WEBSITE / "presentations.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date","type","title","event","location","url","slides_url","notes"])
        for x in sorted(items, key=lambda x: x.get("date",""), reverse=True):
            w.writerow([
                x.get("date",""),
                x.get("type","talk"),
                x.get("title",""),
                x.get("event",""),
                x.get("location",""),
                x.get("url","") or "",
                x.get("slides_url","") or "",
                x.get("notes","") or "",
            ])
    print(f"  presentations.csv: {len(items)} entries")

# ---------------------------------------------------------------------------
# students.csv
# ---------------------------------------------------------------------------

def write_students():
    items = visible_web(load("students.json"))
    path  = WEBSITE / "students.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["names","degree","institution","project","start","end","outcome","doi"])
        for x in items:
            w.writerow([
                "; ".join(x.get("names", [])),
                x.get("degree",""),
                x.get("institution",""),
                x.get("project",""),
                x.get("start",""),
                x.get("end",""),
                "; ".join(x.get("outcomes", [])),
                x.get("doi","") or "",
            ])
    print(f"  students.csv: {len(items)} entries")

# ---------------------------------------------------------------------------
# publications/*.md
# ---------------------------------------------------------------------------

PERIODS = [
    ("2025-2029", range(2025, 2030)),
    ("2020-2024", range(2020, 2025)),
    ("2015-2019", range(2015, 2020)),
    ("2000-2014", range(2000, 2015)),
]

TYPE_LABELS = {
    "journal":      "Journal Papers",
    "conference":   "Conference Papers",
    "book-chapter": "Book Chapters",
    "proceedings":  "Conference Papers",
    "thesis":       "Theses",
    "other":        "Other",
}

TYPE_ORDER = ["journal","conference","book-chapter","proceedings","thesis","other"]


def fmt_author_list(authors):
    """Format author list; **Name** becomes bold in Markdown."""
    return ", ".join(authors)


def fmt_pub_entry(x):
    authors = fmt_author_list(x.get("authors", []))
    title   = x["title"]
    venue   = x.get("venue","")
    year    = x.get("year","")
    url     = x.get("url","")

    title_md = f"[{title}]({url})" if url else title
    parts = [f"{authors}. {title_md}."]
    if venue:
        parts.append(f" *{venue}*.")
    if year:
        parts.append(f" {year}.")
    return "- " + "".join(parts)


def write_publications():
    items  = visible_web(load("publications.json"))
    pubdir = WEBSITE / "publications"
    pubdir.mkdir(exist_ok=True)

    for period_name, yr_range in PERIODS:
        period_items = [x for x in items if x.get("year") in yr_range]
        by_year = defaultdict(lambda: defaultdict(list))
        for x in period_items:
            by_year[x["year"]][x.get("type","other")].append(x)

        lines = ["---", f'title: "{period_name}"', "---", ""]
        if not period_items:
            lines.append("*No publications in this period yet.*")
            lines.append("")
        else:
            for year in sorted(by_year, reverse=True):
                lines.append(f"## {year}")
                lines.append("")
                for ptype in TYPE_ORDER:
                    if ptype not in by_year[year]:
                        continue
                    label = TYPE_LABELS.get(ptype, "Other")
                    lines.append(f"### {year} {label}")
                    lines.append("")
                    for pub in by_year[year][ptype]:
                        lines.append(fmt_pub_entry(pub))
                    lines.append("")

        out = pubdir / f"{period_name}.md"
        out.write_text("\n".join(lines), encoding="utf-8")
        print(f"  publications/{period_name}.md: {len(period_items)} entries")

# ---------------------------------------------------------------------------
# presentations.md
# ---------------------------------------------------------------------------

def write_presentations_md():
    items = visible_web(load("presentations.json"))
    by_year = defaultdict(list)
    for x in items:
        year = int(x.get("date","0")[:4] or 0)
        by_year[year].append(x)

    lines = [
        "---",
        'title: "Presentations"',
        "---",
        "",
        "Invited talks, panels, and posters.",
        "",
        "---",
        "",
    ]

    for year in sorted(by_year, reverse=True):
        lines.append(f"## {year}")
        lines.append("")
        for x in sorted(by_year[year], key=lambda x: x.get("date",""), reverse=True):
            title    = x.get("title","")
            event    = x.get("event","")
            location = x.get("location","")
            url      = x.get("url","")
            slides   = x.get("slides_url","")
            notes    = x.get("notes","")
            ptype    = x.get("type","talk")

            title_md = f"[{title}]({url})" if url else f"*{title}*"
            type_tag = f"*({ptype})* " if ptype and ptype != "talk" else ""

            parts = [f"{type_tag}{title_md}. {event}."]
            if location:
                parts.append(f" {location}.")
            if slides:
                parts.append(f" [Slides]({slides}).")
            if notes:
                parts.append(f" *{notes}.*")
            lines.append("- " + "".join(parts))
        lines.append("")

    out = WEBSITE / "presentations.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"  presentations.md: {len(items)} entries")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Generating website files...")
    write_news()
    write_presentations()
    write_students()
    write_publications()
    write_presentations_md()
    print("Done.")

if __name__ == "__main__":
    main()
