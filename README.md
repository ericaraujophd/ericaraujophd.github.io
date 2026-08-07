# ericaraujophd.github.io

Eric Araújo's unified academic portfolio — single private repo containing the CV data, document archive, website source, and build pipeline.

**Live site:** https://ericaraujo.com  
**GitHub Pages:** deployed via GitHub Actions (`astro build` → Pages)

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
│     refresh.sh           ← Entry point: CV + site + checks
│     build.py             ← CV only: JSON → rendercv YAML → PDF
│     to_rendercv.py       ← JSON + config → rendercv YAML
│
├── presentations/         ← Slide SOURCES (.qmd + images), not served
│     <year>/<venue>/      ← Rendered PDFs must be copied to public/ to ship
│
│   [Website source — Astro]
├── src/
│     layouts/BaseLayout.astro
│     pages/               ← index, publications, presentations, advising, teaching, updates
│     styles/global.css
├── public/                ← Static assets served as-is
│     cv/                  ← Eric_Araujo_CV.pdf (live) + archive/
│     files/               ← headshot, logos, PDFs
│     images/
│     cfr.html             ← CFR Generator tool
│     CNAME                ← ericaraujo.com
├── astro.config.mjs
├── package.json
│
├── _future/               ← Parked drafts (not part of the build)
└── .github/workflows/deploy.yml
```

---

## Running the site locally

```bash
npm install       # first time only
npm run dev       # starts dev server at http://localhost:4321
npm run build     # production build → dist/
npm run preview   # preview the production build
```

---

## How to add a new entry

**Use the cv-file-intake Cowork skill.** It prompts for the right fields, writes to the correct JSON file in `data/`, stores the document in `docs/`, and pushes to GitHub.

To add manually: edit the relevant `data/*.json` file. The Astro pages import JSON directly — no build step needed for website changes.

---

## Rebuilding everything

`scripts/refresh.sh` is the entry point. It rebuilds the CV, rebuilds the site,
and verifies both. It finds the repo root itself, so it runs from any directory,
and exits non-zero if anything fails — safe to run before a push.

```bash
scripts/refresh.sh           # CV + site + checks
scripts/refresh.sh --cv      # CV only
scripts/refresh.sh --site    # site only
scripts/refresh.sh --check   # checks only, rebuilds nothing
```

### Checks

| Check | Catches |
|---|---|
| Every `slides_url` resolves under `public/` | A talk linked to a PDF that Astro never ships |
| No truncated year badges on `/advising/` | Term strings (`"Fall 2025"`) sliced to 4 chars |
| Exactly one email address on the homepage | Hero and footer drifting apart |
| CV PDF newer than `data/*.json` + `config/personal.yaml` | A published CV silently falling behind its sources |

The staleness check compares mtimes, so touching a data file marks the CV stale
even if nothing changed. That's deliberate — it nags rather than letting real
drift through.

### Python environment

The CV pipeline is the repo's only Python dependency; the site is pure npm.

```bash
python3 -m venv .venv-cv
.venv-cv/bin/pip install -r rendercv/requirements.txt
.venv-cv/bin/rendercv --version        # expect: RenderCV v2.7
```

rendercv 2.7 needs Python 3.12 or newer — it will not install on 3.11 or below.
Homebrew's 3.14 works. Note that bare `python3` is Homebrew's system Python and
will refuse to install into itself (PEP 668 `externally-managed-environment`);
always go through `.venv-cv/bin/` or activate the venv first.

The older `.venv` (jupyter-book, ipython) is legacy Quarto/MyST tooling and has
no rendercv in it. Its interpreter was removed by a Homebrew upgrade, so it will
not start until `brew install python@3.13`. Nothing in the current build uses it.

### CV build details

`refresh.sh --cv` calls `scripts/build.py`, which archives the previous PDF to
`public/cv/archive/` before overwriting, then publishes to
`public/cv/Eric_Araujo_CV.pdf` — the path the website actually serves. To
regenerate the YAML without rendering: `python scripts/build.py --no-render`.

If the build exits with `BUILD FAILED`, the published PDF was left untouched on
purpose. The usual cause is a section in `to_rendercv.py` emitting keys that
aren't part of a real rendercv entry type: rendercv guesses the entry type from
the keys present, then rejects every entry for a missing required field. Fix the
`build_*` function to emit a valid entry type (`NormalEntry` is the flexible
one: `name` / `location` / `date` / `summary` / `highlights`).

### Adding a talk with slides

Astro serves **only** `public/`. A PDF in `presentations/<year>/<venue>/` is
invisible to the site. Copy it to `public/presentations/<year>/<venue>/` so it
matches the `slides_url` in `data/presentations.json`. `refresh.sh --check`
verifies this for every entry.

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
| `src/**` | ✏️ Hand-edited (Astro pages and styles) |
| `public/**` | ✏️ Hand-edited (static assets) |
| `rendercv/Eric_Araújo_CV.yaml` | ⚙️ Generated by `scripts/to_rendercv.py` |
| `public/cv/Eric_Araujo_CV.pdf` | ⚙️ Generated by `scripts/build.py` |

---

## Document naming conventions

- Folder slugs: `YYYY-VenueOrKeyword` (kebab-case)
- Keep original filenames inside subfolders
- `document_path` in JSON: always relative to repo root, e.g. `docs/publications/2026-QSS-brain-drain/paper.pdf`
