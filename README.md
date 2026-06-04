# ericaraujophd.github.io

Eric Araújo's unified academic portfolio — single private repo containing the CV data, document archive, website source, and build pipeline.

**Live site:** https://ericaraujo.com  
**GitHub Pages:** deployed from the `gh-pages` branch (built content only)

---

## Structure

```
ericaraujophd.github.io/
│
├── data/                  ← JSON source of truth (the only files you edit)
│     publications.json
│     presentations.json
│     grants.json
│     experience.json
│     teaching.json
│     projects.json
│     students.json
│     service.json
│
├── config/                ← Static personal info (edit directly, never generated)
│     personal.yaml        ← name, contact, education, social links, research skills
│     headshot.jpg
│
├── docs/                  ← Document archive (PDFs, certificates, letters)
│     publications/        ← One subfolder per paper
│     presentations/       ← Slide decks and related docs
│     defense-committee/   ← Committee service records
│     grants-fellowships/  ← Award letters and grant docs
│     admin/               ← Institutional admin documents
│     PhD-supervision/     ← PhD student supervision records
│     recommendation-letters/
│     events/
│
├── rendercv/              ← rendercv config and output
│     Eric_Araújo_CV.yaml  ← GENERATED — do not edit by hand
│     requirements.txt
│     rendercv_output/     ← PDF rendered here by rendercv
│
├── scripts/               ← Build pipeline
│     build.py             ← Orchestrator (run this)
│     to_rendercv.py       ← JSON + config → rendercv YAML
│     to_website.py        ← JSON → website CSV/MD files
│
├── cv/                    ← Served CV PDF
│     Eric_Araujo_CV.pdf   ← Live version (accessible at /cv/Eric_Araujo_CV.pdf)
│     archive/             ← Previous versions, timestamped
│
│   [Website source files — MyST MD]
├── index.md
├── publications.md  /  publications/YYYY-YYYY.md   ← GENERATED
├── presentations.md                                 ← GENERATED
├── teaching.md
├── advising.md  /  advising/
├── updates.md
├── news.csv                                         ← GENERATED
├── presentations.csv                                ← GENERATED
├── students.csv                                     ← GENERATED
├── myst.yml
└── CNAME                  ← ericaraujo.com
```

---

## How to add a new entry

**Use the cv-file-intake Cowork skill.** It prompts for the right fields, writes to the correct JSON file in `data/`, stores the document in `docs/`, updates the website, and pushes to GitHub.

To add manually: edit the relevant `data/*.json` file, then run the build.

---

## Running the build

From the repo root (`ericaraujophd.github.io/`):

```bash
# Full build: YAML + PDF + website files
python scripts/build.py

# CV only (skip website)
python scripts/build.py --cv-only

# Website only (skip PDF render — fast)
python scripts/build.py --web-only

# Generate YAML but skip rendercv render
python scripts/build.py --no-render
```

The build automatically archives the previous PDF to `cv/archive/` before overwriting.

---

## Data schema

Every entry in `data/*.json` shares these fields:

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Unique slug, e.g. `2026-baylor-symposium` |
| `visible_cv` | bool | Include in the PDF CV |
| `visible_web` | bool | Include on the website |
| `news` | bool | Show in the website news feed (auto-generates description) |
| `news_blurb` | string? | Optional custom news description (overrides auto-generated) |
| `document_path` | string? | Relative path to associated file in `docs/` |

### publications.json
```json
{
  "id": "2026-qss-brain-drain",
  "type": "journal",
  "title": "From brain drain to brain circulation...",
  "authors": ["Leonardo Biazoli", "**Eric Araújo**"],
  "venue": "Quantitative Science Studies",
  "year": 2026, "month": 2,
  "doi": "10.1162/QSS.a.411",
  "url": "https://doi.org/10.1162/QSS.a.411",
  "visible_cv": true, "visible_web": true, "news": true,
  "document_path": "docs/publications/2026-QSS-brain-drain/qss.a.411.pdf"
}
```
Types: `journal` | `conference` | `book-chapter` | `proceedings` | `thesis`  
Use `**Name**` to bold your name in the author list.

### presentations.json
```json
{
  "id": "2026-baylor-symposium",
  "type": "talk",
  "title": "A Framework for Modeling Christian Communities...",
  "event": "Baylor Symposium on Faith & Culture 2026",
  "location": "Waco, TX",
  "date": "2026-02-27",
  "url": "https://...",
  "slides_url": "/presentations/2026/Baylor/2026-Baylor.pdf",
  "notes": null,
  "student_presentation": false,
  "visible_cv": true, "visible_web": true, "news": true,
  "document_path": null
}
```
Types: `talk` | `poster` | `panel` | `invited` | `keynote`

### grants.json
```json
{
  "id": "2026-nagel-fellowship",
  "type": "fellowship",
  "name": "Nagel Institute Fellowship",
  "institution": "Nagel Institute — Calvin University",
  "url": "https://nagelinstitute.org/fellowships/",
  "start_date": "2026", "end_date": null,
  "summary": "Supporting research on computational modeling of world Christian communities.",
  "visible_cv": true, "visible_web": true, "news": true,
  "document_path": "docs/grants-fellowships/2026-Nagel-Fellowship/"
}
```
Types: `fellowship` | `grant` | `award`

### experience.json
```json
{
  "id": "calvin-associate-professor-2024",
  "company": "Calvin University",
  "position": "Associate Professor",
  "start_date": "2024-07", "end_date": "present",
  "location": "Grand Rapids, MI",
  "highlights": ["Computer Science Department"],
  "visible_cv": true, "visible_web": false, "news": false,
  "document_path": null
}
```

### teaching.json
```json
{
  "id": "cs112",
  "code": "CS112",
  "name": "Introduction to Data Structures",
  "institution": "Calvin University",
  "url": "https://ericaraujo.com/26sp-cs112/",
  "location": "Calvin University USA",
  "start_date": "2024-09", "end_date": "present",
  "summary": "An introduction to data structures and algorithms.",
  "visible_cv": true, "visible_web": true, "news": false,
  "document_path": null
}
```

### projects.json
```json
{
  "id": "procores-2022",
  "name": "Procores",
  "url": "https://procores-cnpq.github.io/",
  "start_date": "2022-05", "end_date": "present",
  "location": "UFMG Brazil",
  "summary": "Research group funded by CNPq (Brazil).",
  "highlights": ["..."],
  "visible_cv": true, "visible_web": false, "news": false,
  "document_path": null
}
```

### students.json
```json
{
  "id": "modeling-introversion-fall-2024",
  "names": ["Jaden Brookens", "Daniel Kwon"],
  "degree": "B.S.",
  "institution": "Calvin University",
  "project": "Modeling Introversion in the Classroom: An Agent-Based Approach",
  "start": "Fall 2024", "end": "Spring 2025",
  "outcomes": ["Conference paper at AASG 2025 (Detroit)"],
  "doi": null,
  "visible_cv": true, "visible_web": true, "news": false,
  "document_path": null
}
```
`outcomes` is a list — add as many as apply.

### service.json
```json
{
  "id": "2025-masters-stephano-daniel-santos",
  "type": "defense-committee",
  "role": "External Member",
  "title": "Masters Exam — Stephano Daniel Santos",
  "institution": "UFLA Brazil",
  "date": "2025-08-22",
  "summary": "Machine learning for prediction of Portland cement compressive strength.",
  "visible_cv": true, "visible_web": false, "news": false,
  "document_path": "docs/defense-committee/2025-Stephano-Daniel-Santos/082025-Stephano-Daniel-Santos.pdf"
}
```
Types: `defense-committee` | `reviewer` | `admin` | `editorial`

---

## Generated vs. hand-edited files

| File | Status |
|---|---|
| `data/*.json` | ✏️ Hand-edited (source of truth) |
| `config/personal.yaml` | ✏️ Hand-edited |
| `config/headshot.jpg` | ✏️ Hand-edited |
| `docs/**` | ✏️ Hand-edited (PDFs added via skill) |
| `index.md`, `teaching.md`, `advising.md`, `updates.md` | ✏️ Hand-edited |
| `rendercv/Eric_Araújo_CV.yaml` | ⚙️ Generated by `to_rendercv.py` |
| `publications/YYYY-YYYY.md` | ⚙️ Generated by `to_website.py` |
| `presentations.md` | ⚙️ Generated by `to_website.py` |
| `news.csv`, `presentations.csv`, `students.csv` | ⚙️ Generated by `to_website.py` |
| `cv/Eric_Araujo_CV.pdf` | ⚙️ Generated by `build.py` |

---

## Obsolete files (safe to delete)

These were part of the old multi-repo system and are now replaced by `scripts/`:

- `generate_news.py`
- `generate_presentations.py`
- `generate_publications.py`
- `generate_students.py`

---

## Document naming conventions

- Folder slugs: `YYYY-VenueOrKeyword` (kebab-case)
- Keep original filenames inside subfolders
- `document_path` in JSON: always relative to repo root, e.g. `docs/publications/2026-QSS-brain-drain/paper.pdf`
