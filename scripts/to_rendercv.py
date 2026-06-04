#!/usr/bin/env python3
"""
to_rendercv.py — Compile data/*.json + config/personal.yaml → Eric_Araújo_CV.yaml

Usage (run from repo root):
    python scripts/to_rendercv.py

Output: rendercv/Eric_Araújo_CV.yaml
"""

import json
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

def build_publications(items):
    out = []
    for x in visible_cv(items):
        doi = x.get("doi")
        url = x.get("url")
        pub = {
            "title":   x["title"],
            "authors": x["authors"],
            "date":    f"{x['year']}-{x['month']:02d}" if x.get("month") else str(x["year"]),
            "journal": x["venue"],
        }
        if doi:
            pub["doi"] = doi
        if url:
            pub["url"] = url
        out.append(pub)
    return out

def build_events(items):
    out = []
    for x in visible_cv(items):
        e = {
            "role":       "speaker",
            "year":       x["date"][:4] if x.get("date") else "",
            "name":       x["event"],
            "url":        x.get("url") or None,
            "location":   x.get("location") or None,
            "start_date": x.get("date") or None,
            "end_date":   x.get("date") or None,
            "summary":    x.get("notes") or None,
        }
        out.append(e)
    return out

def build_grants(items):
    out = []
    for x in visible_cv(items):
        out.append({
            "name":        x["name"],
            "url":         x.get("url") or None,
            "institution": x["institution"],
            "start_date":  x["start_date"],
            "end_date":    x.get("end_date") or None,
            "summary":     x.get("summary") or None,
        })
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
            "start_date": x["start_date"],
            "end_date":   x.get("end_date") or None,
            "location":   x.get("location") or None,
            "summary":    x.get("summary") or None,
            "highlights": h if h else None,
        })
    return out

def build_students(items):
    out = []
    for x in visible_cv(items):
        outcomes = x.get("outcomes", [])
        out.append({
            "names":       "; ".join(x["names"]),
            "degree":      x["degree"],
            "institution": x["institution"],
            "project":     x["project"],
            "start":       x["start"],
            "end":         x["end"],
            "outcomes":    outcomes if outcomes else None,
            "doi":         x.get("doi") or None,
        })
    return out

def build_service(items):
    out = []
    for x in visible_cv(items):
        out.append({
            "type":        x["type"],
            "role":        x.get("role"),
            "title":       x["title"],
            "institution": x["institution"],
            "date":        x["date"],
            "summary":     x.get("summary") or None,
        })
    return out

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
            "photo":       personal.get("photo"),
            "social_networks": personal.get("social_networks"),
            "sections": {
                "Welcome":              personal.get("welcome", []),
                "education":            personal.get("education", []),
                "experience":           build_experience(load("experience.json")),
                "publications":         build_publications(load("publications.json")),
                "events":               build_events(load("presentations.json")),
                "grants_and_fellowships": build_grants(load("grants.json")),
                "teaching":             build_teaching(load("teaching.json")),
                "research_projects":    build_projects(load("projects.json")),
                "supervised_students":  build_students(load("students.json")),
                "service":              build_service(load("service.json")),
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
