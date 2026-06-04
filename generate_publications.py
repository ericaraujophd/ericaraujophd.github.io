#!/usr/bin/env python3
"""
generate_publications.py — Regenerate publications/*.md from pubs.bib.

Usage (run from the website root):
    python generate_publications.py

Source:  ../rendercv/sources/pubs.bib
Outputs: publications/2025-2029.md
         publications/2020-2024.md
         publications/2015-2019.md

To add a publication: edit pubs.bib, then run this script.
"""

import re
import sys
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
PUB_DIR  = HERE / "publications"

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Time-period pages: (filename-stem, year range)
PERIODS = [
    ("2025-2029", range(2025, 2030)),
    ("2020-2024", range(2020, 2025)),
    ("2015-2019", range(2015, 2020)),
    ("2000-2014", range(2000, 2015)),
]

# Human-readable section labels per BibTeX entry type
TYPE_LABELS = {
    "article":       "Journal Papers",
    "inproceedings": "Conference Papers",
    "incollection":  "Book Chapters",
    "phdthesis":     "Theses",
    "mastersthesis": "Theses",
    "misc":          "Other",
}

# Canonical order of entry types within a year
TYPE_ORDER = ["article", "inproceedings", "incollection",
              "phdthesis", "mastersthesis", "misc"]

# Name fragments that identify Eric in the author list
ERIC_NAME_FRAGMENTS = [
    "eric araújo",
    "eric araujo",
    "araújo, eric",
    "araujo, eric",
]

# ---------------------------------------------------------------------------
# Author formatting helpers
# ---------------------------------------------------------------------------

def _is_eric(name: str) -> bool:
    """Return True if the name string refers to Eric Araújo."""
    lower = name.lower()
    return any(frag in lower for frag in ERIC_NAME_FRAGMENTS)


def _normalize_single_author(raw: str) -> str:
    """
    Convert one author token to 'First Last' form.
    Handles:
      - 'Last, First'         → 'First Last'
      - 'First Last'          → unchanged
      - '**Eric Araújo**'     → unchanged (already marked up)
    """
    raw = raw.strip()
    if not raw:
        return raw

    # Already bolded in the .bib — keep it
    if raw.startswith("**"):
        return raw

    # "Last, First [Middle]" → "First [Middle] Last"
    if "," in raw:
        last, first = raw.split(",", 1)
        return f"{first.strip()} {last.strip()}"

    return raw


def format_authors(raw_field: str) -> str:
    """
    Parse a BibTeX author field and return a formatted, comma-separated
    string with Eric Araújo bolded.
    """
    tokens = raw_field.replace("\n", " ").split(" and ")
    result = []
    for token in tokens:
        name = _normalize_single_author(token)
        # Bold if it's Eric and not already bolded
        if not name.startswith("**") and _is_eric(name):
            name = f"**{name}**"
        result.append(name)
    return ", ".join(result)


# ---------------------------------------------------------------------------
# Entry formatting
# ---------------------------------------------------------------------------

def _clean(text: str) -> str:
    """Strip LaTeX braces and tidy whitespace."""
    return re.sub(r"[{}]", "", text).strip()


def _link(entry: dict) -> str:
    """Return the best available URL for an entry."""
    doi = entry.get("doi", "").strip()
    url = entry.get("url", "").strip()
    if doi:
        return f"https://doi.org/{doi}"
    return url


def _venue(entry: dict) -> str:
    """Return the publication venue (journal, booktitle, or school)."""
    for field in ("journal", "booktitle", "school"):
        v = entry.get(field, "").strip()
        if v:
            return _clean(v)
    return ""


def format_entry(entry: dict) -> str:
    """Return a Markdown list item for one BibTeX entry."""
    authors  = format_authors(entry.get("author", ""))
    title    = _clean(entry.get("title", "Untitled"))
    venue    = _venue(entry)
    year     = entry.get("year", "").strip()
    href     = _link(entry)

    title_md = f"[{title}]({href})" if href else title

    parts = [f"{authors}. {title_md}."]
    if venue:
        parts.append(f" *{venue}*.")
    if year:
        parts.append(f" {year}.")

    return "- " + "".join(parts)


# ---------------------------------------------------------------------------
# Page builder
# ---------------------------------------------------------------------------

def build_period_page(period_name: str, entries: list) -> str:
    """Return the full Markdown content for one time-period page."""
    lines = ["---", f'title: "{period_name}"', "---", ""]

    if not entries:
        lines.append("*No publications in this period yet.*")
        lines.append("")
        return "\n".join(lines)

    # Group: year → entry_type → [entries]
    by_year: dict = defaultdict(lambda: defaultdict(list))
    for entry in entries:
        try:
            year = int(entry.get("year", 0))
        except ValueError:
            year = 0
        etype = entry.get("ENTRYTYPE", "misc").lower()
        by_year[year][etype].append(entry)

    for year in sorted(by_year.keys(), reverse=True):
        lines.append(f"## {year}")
        lines.append("")
        types_present = by_year[year]
        for etype in TYPE_ORDER:
            if etype not in types_present:
                continue
            label = TYPE_LABELS.get(etype, "Other")
            lines.append(f"### {year} {label}")
            lines.append("")
            for entry in types_present[etype]:
                lines.append(format_entry(entry))
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if not BIB_PATH.exists():
        sys.exit(f"Cannot find pubs.bib at: {BIB_PATH.resolve()}")

    parser = BibTexParser(common_strings=True)
    parser.customization = convert_to_unicode
    with open(BIB_PATH, encoding="utf-8") as f:
        db = bibtexparser.load(f, parser=parser)

    print(f"Loaded {len(db.entries)} entries from {BIB_PATH.name}")

    PUB_DIR.mkdir(exist_ok=True)

    for period_name, year_range in PERIODS:
        entries = [e for e in db.entries
                   if _try_int(e.get("year", "0")) in year_range]
        content = build_period_page(period_name, entries)
        out_path = PUB_DIR / f"{period_name}.md"
        out_path.write_text(content, encoding="utf-8")
        print(f"  {out_path.name}: {len(entries)} entries")

    # Warn about any entries outside all defined periods
    all_years = set()
    for _, yr in PERIODS:
        all_years.update(yr)
    orphans = [e for e in db.entries
               if _try_int(e.get("year", "0")) not in all_years]
    if orphans:
        print(f"\nWarning: {len(orphans)} entries outside defined periods:")
        for e in orphans:
            print(f"  [{e.get('year', '?')}] {_clean(e.get('title', '?'))[:70]}")


def _try_int(val: str) -> int:
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0


if __name__ == "__main__":
    main()
