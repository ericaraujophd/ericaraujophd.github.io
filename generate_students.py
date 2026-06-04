#!/usr/bin/env python3
"""
generate_students.py — Regenerate advising/current.md and advising/past.md
from students.csv.

Usage (run from the website root):
    python generate_students.py

To add a student: append a row to students.csv, then run this script.
To graduate a student: fill in the 'end' column and re-run.

CSV columns:
  names       Student name(s), separated by semicolons for group projects
  degree      B.S. | M.S. | Ph.D.
  institution Their institution
  project     Project title
  start       Term/year started, e.g. "Fall 2024" or "2022"
  end         Term/year finished; leave blank if still active
  outcome     One-line description of the result (paper, presentation, etc.)
  doi         DOI of any resulting publication (without https://doi.org/)
"""

import csv
from pathlib import Path
from collections import defaultdict

HERE        = Path(__file__).parent
CSV_PATH    = HERE / "students.csv"
CURRENT_MD  = HERE / "advising" / "current.md"
PAST_MD     = HERE / "advising" / "past.md"

DEGREE_ORDER = ["Ph.D.", "M.S.", "B.S."]
DEGREE_LABEL = {
    "Ph.D.": "Ph.D. Students",
    "M.S.":  "M.S. Students",
    "B.S.":  "B.S. Students",
}


def load_students():
    current, past = [], []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row = {k: v.strip() for k, v in row.items()}
            row["_names"] = [n.strip() for n in row["names"].split(";") if n.strip()]
            if row["end"]:
                past.append(row)
            else:
                current.append(row)
    return current, past


def format_names(names: list) -> str:
    return " and ".join(f"**{n}**" for n in names)


def outcome_line(row: dict) -> str:
    outcome = row.get("outcome", "").strip()
    doi     = row.get("doi", "").strip()
    if doi:
        url = f"https://doi.org/{doi}"
        if outcome:
            return f"*Outcome:* [{outcome}]({url})"
        return f"*Outcome:* [Publication](https://doi.org/{doi})"
    if outcome:
        return f"*Outcome:* {outcome}"
    return ""


# ---------------------------------------------------------------------------
# current.md
# ---------------------------------------------------------------------------

def build_current(students: list) -> str:
    lines = [
        "---",
        'title: "Current Students"',
        "---",
        "",
    ]

    if not students:
        lines.append("No active students at this time.")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("[Back to Advising Overview](../advising.md) · [Past Students](past.md)")
        lines.append("")
        return "\n".join(lines)

    by_degree = defaultdict(list)
    for s in students:
        by_degree[s["degree"]].append(s)

    for degree in DEGREE_ORDER:
        if degree not in by_degree:
            continue
        lines.append(f"## {DEGREE_LABEL[degree]}")
        lines.append("")
        for s in by_degree[degree]:
            lines.append(f"### {s['project']}")
            lines.append("")
            lines.append(
                f"**{'Students' if len(s['_names']) > 1 else 'Student'}:** "
                f"{format_names(s['_names'])} "
                f"({s['institution']}, started {s['start']})"
            )
            lines.append("")
            o = outcome_line(s)
            if o:
                lines.append(o)
                lines.append("")
            lines.append("---")
            lines.append("")

    lines.append("[Back to Advising Overview](../advising.md) · [Past Students](past.md)")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# past.md
# ---------------------------------------------------------------------------

def _end_sort_key(s: dict) -> tuple:
    """Sort by end term: extract year and rough semester order."""
    end = s.get("end", "").strip()
    year = 0
    sem  = 0
    for token in end.split():
        if token.isdigit():
            year = int(token)
        elif token.lower() == "spring":
            sem = 1
        elif token.lower() in ("summer",):
            sem = 2
        elif token.lower() == "fall":
            sem = 3
    return (year, sem)


def build_past(students: list) -> str:
    lines = [
        "---",
        'title: "Past Students"',
        "---",
        "",
    ]

    if not students:
        lines.append("No past students yet.")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("[Back to Advising Overview](../advising.md) · [Current Students](current.md)")
        lines.append("")
        return "\n".join(lines)

    by_degree = defaultdict(list)
    for s in students:
        by_degree[s["degree"]].append(s)

    for degree in DEGREE_ORDER:
        if degree not in by_degree:
            continue
        lines.append(f"## {DEGREE_LABEL[degree]}")
        lines.append("")

        group = sorted(by_degree[degree], key=_end_sort_key, reverse=True)
        for s in group:
            names_str = ", ".join(f"**{n}**" for n in s["_names"])
            period    = f"{s['start']}–{s['end']}"
            lines.append(
                f"- {names_str} — *{s['project']}* "
                f"({s['institution']}, {period})"
            )
            o = outcome_line(s)
            if o:
                lines.append(f"  {o}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("[Back to Advising Overview](../advising.md) · [Current Students](current.md)")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    current, past = load_students()
    print(f"Loaded {len(current)} current, {len(past)} past students from {CSV_PATH.name}")

    CURRENT_MD.parent.mkdir(exist_ok=True)
    CURRENT_MD.write_text(build_current(current), encoding="utf-8")
    print(f"Wrote {CURRENT_MD.name}")

    PAST_MD.write_text(build_past(past), encoding="utf-8")
    print(f"Wrote {PAST_MD.name}")


if __name__ == "__main__":
    main()
