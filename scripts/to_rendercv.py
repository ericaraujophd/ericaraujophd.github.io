#!/usr/bin/env python3
"""
to_rendercv.py — Compile data/*.json + config/personal.yaml → Eric_Araújo_CV.yaml

Usage (run from repo root):
    python scripts/to_rendercv.py

Output: rendercv/Eric_Araújo_CV.yaml
"""

import json
import os
import re
import yaml
from pathlib import Path

ROOT   = Path(__file__).parent.parent
DATA   = ROOT / "data"
CONFIG = ROOT / "config" / "personal.yaml"
OUT    = ROOT / "rendercv" / "Eric_Araújo_CV.yaml"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))

def visible_cv(items):
    return [x for x in items if x.get("visible_cv", True)]

# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

# rendercv's own month abbreviations, matched so hand-built date strings sit
# flush with the ones rendercv formats itself.
_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "June",
           "July", "Aug", "Sept", "Oct", "Nov", "Dec"]


def _sort_key(v):
    """Newest-first sort key for mixed 'YYYY' / 'YYYY-MM' / 'YYYY-MM-DD' values."""
    if not v:
        return "0000-00-00"
    v = str(v).strip()
    if v == "present":
        return "9999-99-99"
    parts = v.split("-")
    parts += ["00"] * (3 - len(parts))
    return "-".join(p.zfill(2) if i else p.zfill(4) for i, p in enumerate(parts[:3]))


def _fmt_date(v):
    if not v:
        return None
    v = str(v).strip()
    if v == "present" or (len(v) == 4 and v.isdigit()):
        return v
    m = re.match(r"^(\d{4})-(\d{1,2})", v)
    if m:
        return f"{_MONTHS[int(m.group(2)) - 1]} {m.group(1)}"
    return v


def _date_fields(start, end):
    """Build the date string ourselves and hand rendercv free text.

    Letting rendercv parse start_date/end_date renders a bare year as
    "Jan <year>", which misstates an academic-year award or an ongoing role.
    Formatting here keeps years as years and months as month names.
    """
    s, e = _fmt_date(start), _fmt_date(end)
    if not s:
        return {}
    if not e or s == e:
        return {"date": s}
    return {"date": f"{s} \u2013 {e}"}


def build_experience(items):
    out = []
    for x in visible_cv(items):
        h = x.get("highlights", [])
        out.append({
            "company":    x["company"],
            "position":   x["position"],
            "start_date": x["start_date"],
            "end_date":   x["end_date"],
            "location":   x.get("location") or None,
            "highlights": h if h else None,
        })
    return out

def _publication_entry(x):
    """One rendercv PublicationEntry.

    'status' and 'note' are appended to the venue because PublicationEntry has
    no summary field — anything else would be silently dropped.
    """
    venue = x["venue"]
    if x.get("status"):
        venue = f'{venue}. {x["status"]}'
    if x.get("note"):
        venue = f'{venue}. {x["note"]}'
    pub = {
        "title":   x["title"],
        "authors": x["authors"],
        "date":    x.get("date_display") or (f"{x['year']}-{x['month']:02d}" if x.get("month") else str(x["year"])),
        "journal": venue,
    }
    if x.get("doi"):
        pub["doi"] = x["doi"]
    if x.get("url"):
        pub["url"] = x["url"]
    return pub


def build_books(items):
    """Books and monographs — rendered above the article list."""
    return [_publication_entry(x) for x in visible_cv(items) if x.get("type") == "book"]


def build_publications(items):
    return [_publication_entry(x) for x in visible_cv(items) if x.get("type") != "book"]

def build_events(items):
    out = []
    for x in visible_cv(items):
        e = {
            "role":       "speaker",
            "year":       x["date"][:4] if x.get("date") else "",
            "name":       x["event"],
            "url":        x.get("url") or None,
            "location":   x.get("location") or None,
            "summary":    x.get("notes") or None,
            # a one-day event has start == end; _date_fields collapses that to a
            # single date instead of rendering "Aug 2026 - Aug 2026"
            **_date_fields(x.get("date"), x.get("date")),
        }
        out.append(e)
    return out

def build_grants(items):
    out = []
    for x in visible_cv(items):
        entry = {
            "name":        x["name"],
            "url":         x.get("url") or None,
            "institution": x["institution"],
            "summary":     x.get("summary") or None,
        }
        entry.update(_date_fields(x["start_date"], x.get("end_date")))
        out.append(entry)
    return out

def build_teaching(items):
    out = []
    for x in visible_cv(items):
        out.append({
            "code":       x["code"],
            "name":       x["name"],
            "url":        x.get("url") or None,
            "location":   x.get("location") or None,
            "start_date": x["start_date"],
            "end_date":   x["end_date"],
            "summary":    x.get("summary") or None,
        })
    return out

def build_projects(items):
    out = []
    for x in visible_cv(items):
        h = x.get("highlights", [])
        out.append({
            "name":       x["name"],
            "url":        x.get("url") or None,
            "location":   x.get("location") or None,
            "summary":    x.get("summary") or None,
            "highlights": h if h else None,
            **_date_fields(x["start_date"], x.get("end_date")),
        })
    return out

def build_students(items):
    """Supervised students -> rendercv NormalEntry.

    rendercv has no 'supervision' entry type. NormalEntry is the flexible one:
    name / location / date / summary / highlights. Anything else (names,
    project, start, end) is silently dropped by rendercv AND fails validation,
    because rendercv then guesses EducationEntry and demands an 'area' field.
    """
    out = []
    for x in visible_cv(items):
        highlights = list(x.get("outcomes") or [])
        doi = x.get("doi")
        if doi:
            highlights.append(f"DOI: [{doi}](https://doi.org/{doi})")

        start, end = x.get("start"), x.get("end")
        date = f"{start} - {end}" if start and end else (start or end or None)

        out.append({
            "name":       ", ".join(x["names"]),
            "location":   x.get("institution") or None,
            "date":       date,
            "summary":    f'{x["degree"]} - {x["project"]}',
            "highlights": highlights or None,
        })
    return out

def build_service(items, scope):
    """Service -> rendercv NormalEntry, one line each, filtered by scope.

    rendercv has no sub-heading mechanism inside a section, so the Calvin /
    professional / church split is expressed as three separate sections.
    Entries with no explicit scope default to 'professional'.
    """
    out = []
    for x in visible_cv(items):
        if (x.get("scope") or "professional") != scope:
            continue
        title = x.get("cv_title") or x["title"]
        parts = [p for p in (x.get("role"), title) if p]
        label = " - ".join(parts)
        if x.get("institution") and x["institution"] not in label:
            label = f'{label}, {x["institution"]}'
        entry = {"name": label}
        entry.update(_date_fields(x.get("date"), x.get("end_date")))
        if scope != "professional" and x.get("summary"):
            entry["summary"] = x["summary"]
        out.append((_sort_key(x.get("date")), entry))
    return [e for _, e in sorted(out, key=lambda p: p[0], reverse=True)]


def build_professional_development(items):
    out = []
    for x in visible_cv(items):
        entry = {
            "name":       x["title"],
            "location":   x.get("institution") or None,
            "summary":    x.get("summary") or None,
        }
        entry.update(_date_fields(x.get("start_date"), x.get("end_date")))
        out.append((_sort_key(x.get("start_date")), entry))
    return [e for _, e in sorted(out, key=lambda p: p[0], reverse=True)]


def photo_path(rel):
    """Make the headshot path relative to the YAML file, not the repo root.

    rendercv resolves `cv.photo` relative to the input YAML's directory, but
    config/personal.yaml stores it relative to the repo root.
    """
    if not rel:
        return None
    p = (ROOT / rel).resolve()
    if not p.exists():
        return None
    return os.path.relpath(p, OUT.parent).replace(os.sep, "/")


# ---------------------------------------------------------------------------
# Main assembler
# ---------------------------------------------------------------------------

def main():
    personal = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))

    cv = {
        "cv": {
            "name":        personal["name"],
            "headline":    personal["headline"],
            "location":    personal["location"],
            "email":       personal["email"],
            "phone":       personal.get("phone"),
            "website":     personal.get("website"),
            "photo":       photo_path(personal.get("photo")),
            "social_networks": personal.get("social_networks"),
            "sections": {
                "Welcome":              personal.get("welcome", []),
                "education":            personal.get("education", []),
                "experience":           build_experience(load("experience.json")),
                "books":                build_books(load("publications.json")),
                "publications":         build_publications(load("publications.json")),
                "events":               build_events(load("presentations.json")),
                "grants_and_fellowships": build_grants(load("grants.json")),
                "teaching":             build_teaching(load("teaching.json")),
                "research_projects":    build_projects(load("projects.json")),
                "supervised_students":  build_students(load("students.json")),
                "university_service":   build_service(load("service.json"), "university"),
                "professional_service": build_service(load("service.json"), "professional"),
                "church_and_community_service": build_service(load("service.json"), "church"),
                "professional_development": build_professional_development(load("professional_development.json")),
                "research_skills":      personal.get("research_skills", []),
            },
        }
    }

    # Remove None values recursively (rendercv prefers absence to null)
    def drop_none(obj):
        if isinstance(obj, dict):
            return {k: drop_none(v) for k, v in obj.items() if v is not None}
        if isinstance(obj, list):
            return [drop_none(i) for i in obj]
        return obj

    clean = drop_none(cv)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        yaml.dump(clean, allow_unicode=True, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )
    print(f"Wrote {OUT.resolve()}")

if __name__ == "__main__":
    main()
