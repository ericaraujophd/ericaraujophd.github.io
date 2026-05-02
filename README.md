# ericaraujophd.github.io — Maintenance Guide

Personal academic website for Eric Araújo, built with [MyST](https://mystmd.org/). Most content is generated from source files — you should rarely need to edit the output `.md` files by hand.

Live site: [ericaraujo.com](https://ericaraujo.com)

---

## Quick reference

| What to update | Edit this file | Then run |
|---|---|---|
| News / recent activity | `news.csv` | `python generate_news.py` |
| Publications | `../rendercv/sources/pubs.bib` | `python generate_publications.py` |
| Conference papers (also on Presentations) | `../rendercv/sources/pubs.bib` | `python generate_presentations.py` |
| Talks, panels, posters | `presentations.csv` | `python generate_presentations.py` |
| Teaching | `teaching.md` | *(edit directly)* |
| Advising overview | `advising.md` | *(edit directly)* |
| Current & past students | `students.csv` | `python generate_students.py` |
| Navigation / site config | `myst.yml` | *(edit directly)* |
| CSS / visual style | `custom.css` | *(edit directly)* |
| Footer | `footer.md` | *(edit directly)* |

---

## 1. Adding news

Open `news.csv` and prepend a new row (newest items at the top).

```csv
date,type,title,description,url
2026-09-01,publication,Journal Name — Short Title,"Full sentence description.",https://doi.org/...
```

**Columns:**

- `date` — `YYYY-MM-DD`. Use `YYYY-01-01` when only the year is known.
- `type` — `publication`, `presentation`, `talk`, `service`, `award`, or `other`
- `title` — short label, shown in bold or as a link anchor
- `description` — one or two sentences. Markdown allowed (`*italics*`, links).
- `url` — optional. Makes the title a hyperlink.

Then run:

```bash
python generate_news.py
```

This rewrites `updates.md` (full archive) and refreshes the `<!-- NEWS_START/END -->` block in `index.md`. The homepage shows the 6 most recent items.

---

## 2. Adding a publication

Add a BibTeX entry to `../rendercv/sources/pubs.bib`. Use the right entry type:

- `@article` — journal paper
- `@inproceedings` — conference paper *(also appears on Presentations page automatically)*
- `@incollection` — book chapter
- `@phdthesis` / `@mastersthesis` — thesis

Bold your name: `author = {**Eric Araújo** and Someone Else}`.

Then run:

```bash
python generate_publications.py   # rebuilds publications/*.md
python generate_presentations.py  # picks up @inproceedings automatically
```

To add a new time period (e.g. 2030–2034): add a row to `PERIODS` in `generate_publications.py`, add the new file to `toc` in `myst.yml`, then run the script.

---

## 3. Adding a talk, panel, or poster

Open `presentations.csv` and add a row:

```csv
date,type,title,event,location,url,slides_url,notes
2026-09-15,talk,Title of Talk,Conference Name,"City, Country",https://conf.example.com,/presentations/2026/slides.pdf,Optional note
```

**Type options:** `talk`, `poster`, `panel`, `invited`, `keynote`. Anything other than `talk` appears as a parenthetical label.

Then run:

```bash
python generate_presentations.py
```

---

## 4. Updating students

Open `students.csv` and add or update a row:

```csv
names,degree,institution,project,start,end,outcome,doi
Jane Doe,B.S.,Calvin University,Project Title,Fall 2026,,,
```

**Column guide:**

- `names` — semicolon-separated for group projects: `Jane Doe; John Smith`
- `degree` — `B.S.`, `M.S.`, or `Ph.D.`
- `start` / `end` — term and year, e.g. `Fall 2025` or just `2022`. **Leave `end` blank for current students.**
- `outcome` — one line describing the result (paper title, conference, etc.)
- `doi` — if there's a publication, just the DOI (e.g. `10.1093/comnet/cnaf016`). The script links it automatically.

To graduate a student: fill in their `end` column and re-run. They move from `current.md` to `past.md` automatically.

```bash
python generate_students.py
```

---

## 5. Updating teaching (direct edit)

Edit `teaching.md` directly:

- Move the current semester block to the "Previous Semesters" section (change `:open: true` to remove it).
- Add a new current semester block at the top.

---

## 5. Updating advising

Edit `advising/current.md` and `advising/past.md` directly. When a student finishes, move their entry from `current.md` to `past.md`.

---

## 6. Updating the CV PDF

The PDF CV is managed in `../rendercv/`. After rebuilding it there, copy the output to:

```
cv/Eric_Araujo_CV.pdf
```

---

## 7. Preview locally

```bash
npm install -g mystmd   # first time only
myst start              # serves at http://localhost:3000
```

Build static HTML:

```bash
myst build --html       # output → _build/html/
```

---

## 8. Deploy

The site deploys via GitHub Actions on push to `main`. Just commit and push:

```bash
git add .
git commit -m "update: <what changed>"
git push
```

---

## File map

```
ericaraujophd.github.io/
│
├── myst.yml                    Site config and navigation
├── custom.css                  Calvin colors, fonts, styling
├── footer.md                   Footer (edit manually)
│
├── index.md                    Homepage — bio, research, news block
├── teaching.md                 Teaching history (edit manually)
├── publications.md             Publications landing page (edit manually)
├── advising.md                 Advising overview (edit manually)
│
├── updates.md                  ← GENERATED by generate_news.py
├── presentations.md            ← GENERATED by generate_presentations.py
│
├── publications/
│   ├── 2025-2029.md            ← GENERATED by generate_publications.py
│   ├── 2020-2024.md            ← GENERATED
│   ├── 2015-2019.md            ← GENERATED
│   └── 2000-2014.md            ← GENERATED
│
├── advising/
│   ├── current.md              ← GENERATED by generate_students.py
│   └── past.md                 ← GENERATED by generate_students.py
│
├── news.csv                    Source data: news items
├── presentations.csv           Source data: talks / posters / panels
├── students.csv                Source data: current and past students
│
├── generate_news.py            Rebuilds updates.md + index.md news block
├── generate_publications.py    Rebuilds publications/*.md from pubs.bib
├── generate_presentations.py   Rebuilds presentations.md from pubs.bib + presentations.csv
└── generate_students.py        Rebuilds advising/current.md + advising/past.md
```

---

## Semester-start checklist

- [ ] Add new courses to `teaching.md` under "Currently Teaching"; archive last semester
- [ ] Update `students.csv` — add new students, fill `end` for graduated ones — run `generate_students.py`
- [ ] Add new publications to `pubs.bib`, run `generate_publications.py` + `generate_presentations.py`
- [ ] Add new talks/events to `news.csv` and `presentations.csv`, run generators
- [ ] Update the CV PDF in `cv/`
- [ ] Commit and push
