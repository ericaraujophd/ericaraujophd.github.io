# SQL Homework Assignment Guide

## GitHub Classroom + Docker + PostgreSQL + Hashed Autograding

---

## Overview

This guide describes the complete workflow for creating SQL homework assignments that:

- Give students a **local PostgreSQL environment** via Docker
- Allow students to **write and test queries** directly in VSCode
- **Autograde submissions** automatically on every push via GitHub Actions
- Keep **answer keys private** using hashed result sets — no private repos or tokens needed

---

## One-Time Setup

Do this once for the entire course.

### 1. Install Tools on Your Machine

| Tool | URL |
|------|------|
| Docker Desktop | docker.com/products/docker-desktop |
| VSCode | code.visualstudio.com |
| Claude extension for VSCode | Install from VSCode marketplace |

### 2. Create a GitHub Organization for Your Course

```
github.com
→ Your profile photo (top right)
→ Your organizations
→ New organization
→ Free plan
→ Name: e.g. calvin-cs354
```

### 3. Set Up GitHub Classroom

```
classroom.github.com
→ New classroom
→ Select your organization
→ Name your classroom (e.g. CS354 Spring 2026)
```

That's it. No tokens, no secrets, no private repos needed.

---

## Per-Assignment Workflow

### Phase 1 — Generate Files with Claude Agent

Open VSCode, switch to Agent mode, and use the following prompt.
Fill in the five fields marked with brackets before sending.

---

```
I am a CS professor teaching a Database Management Systems course.
I need to create a complete SQL homework assignment for GitHub Classroom
with local development support for students and automated grading via
GitHub Actions using hashed result sets.

## Tech Stack
- PostgreSQL 16 (via Docker)
- Python + psycopg2-binary for the autograder
- GitHub Classroom
- VSCode as the student's local development environment

## Credentials (hardcoded throughout all files)
- POSTGRES_USER: admin
- POSTGRES_PASSWORD: admin
- POSTGRES_DB: [DATABASE NAME]

## Assignment Details
- Assignment name: [HOMEWORK NAME]
- Topic: [TOPIC]
- Number of questions: [N]
- Points per question: [N]
- Database theme: [THEME]

## Questions
[LIST YOUR QUESTIONS HERE]

## Please generate ALL of the following files:

### Database
1. `sql/01_schema.sql` — CREATE TABLE statements appropriate
   for the questions
2. `sql/02_seed.sql` — realistic sample data (at least 20 rows
   per main table, with intentional edge cases like students with
   no enrollments, departments with one student, etc.)

### Student query files
3. One `q[N].sql` file per question containing:
   - A clear comment block explaining the question
   - The expected output columns listed in comments
   - A blank line where the student writes their query

### Hash generation (instructor only)
4. `generate_hashes.py` that:
   - Contains the correct answer query for each question
     as a dictionary
   - Connects to PostgreSQL
   - Runs each answer query
   - Normalizes results (sort rows, round floats to 4 decimals)
   - Hashes each result set with SHA256
   - Prints all hashes clearly
   - Saves hashes to hashes.json
   - Flags which questions are order-sensitive (require ORDER BY)

### Autograder
5. `grade.py` that:
   - Has a placeholder EXPECTED_HASHES dictionary at the top
     with empty strings that I will fill in manually
   - Has an ORDERED_QUESTIONS list for questions requiring ORDER BY
   - Connects to PostgreSQL
   - Runs each student .sql file
   - Normalizes results the same way as generate_hashes.py
     (sort rows, round floats to 4 decimals)
   - Hashes each result set
   - Compares against EXPECTED_HASHES
   - Handles empty files, syntax errors gracefully
   - Prints ✅ or ❌ per question
   - Writes results.json with score per question and total

6. `.github/workflows/autograder.yml` that:
   - Triggers on every push
   - Spins up PostgreSQL 16 as a service with hardcoded credentials
   - Loads schema and seed data via explicit psql -f commands
   - Installs Python and psycopg2-binary
   - Runs grade.py
   - Posts results as a GitHub Actions summary so students
     can see their score in the Actions tab
   - Never exposes answer queries or hashes in the log,
     only ✅ or ❌ per question

### Local development
7. `docker-compose.yml` that:
   - Runs PostgreSQL 16
   - Auto-loads schema and seed data via
     /docker-entrypoint-initdb.d/ volume mounts
   - Exposes port 5432

8. `.vscode/settings.json` that configures the SQLTools
   PostgreSQL extension to connect automatically
   with the correct credentials so students can run
   queries directly in VSCode with one click

### Dependencies
9. `requirements.txt` containing only:
   psycopg2-binary

### Documentation
10. `README.md` with:
    - Assignment overview and learning objectives
    - Prerequisites:
        - Docker Desktop
        - VSCode
        - SQLTools extension
        - SQLTools PostgreSQL Driver extension
    - Step by step setup:
        1. Clone the repo
        2. Create and activate a virtual environment
        3. pip install -r requirements.txt
        4. Run docker compose up
        5. Connect VSCode SQLTools to the database
        6. Write queries in the q[N].sql files
        7. Run grade.py locally to check score before submitting
        8. Reset the database with docker compose down -v
    - How to submit (git add, commit, push)
    - Grading breakdown per question

### Gitignore
11. `.gitignore` that excludes:
    - generate_hashes.py
    - hashes.json
    - venv/
    - __pycache__/
    - *.pyc
    - .env

## Constraints
- Do NOT generate test.sh — students use VSCode SQLTools
  to run queries directly in the editor
- Use psycopg2-binary (not psycopg2) everywhere
- generate_hashes.py must never be committed — it is gitignored
- hashes.json must never be committed — it is gitignored
- Grader compares hashed result sets, not query strings
- Normalization must be identical in both generate_hashes.py
  and grade.py
- Seed data must make at least one question return an empty
  result set for wrong answers (to catch SELECT *)
- All files must be consistent with each other
  (same table names, column names, credentials everywhere)
- The .vscode/settings.json must work out of the box with
  the SQLTools and SQLTools PostgreSQL Driver extensions

## After generating all files, print a checklist:
1. Run: docker compose up -d
2. Activate venv and run: python generate_hashes.py
3. Copy hashes into grade.py EXPECTED_HASHES dictionary
4. Run grade.py with correct answers pasted in — confirm all ✅
5. Clear student query files back to blank
6. Run grade.py again — confirm all ❌
7. Confirm .gitignore excludes generate_hashes.py and hashes.json
8. Push to GitHub
9. Create assignment in GitHub Classroom

Please create all files directly in the workspace.
```

---

### Fields to Fill In Per Assignment

| Field | Example |
|---|---|
| `[DATABASE NAME]` | `university` |
| `[HOMEWORK NAME]` | `hw02-joins` |
| `[TOPIC]` | `JOINs and aggregate functions` |
| `[N] questions` | `5` |
| `[N] points` | `20` |
| `[THEME]` | `university with students, departments, courses, enrollments` |
| `[QUESTIONS]` | your list |

---

### Phase 2 — Generate the Hashes

After Claude creates all the files:

**1. Start the database**

```bash
docker compose up -d
```

**2. Set up Python environment**

```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
# or
venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

**3. Run the hash generator**
```bash
python generate_hashes.py
```

Output will look like:
```
q1: 7f3d9a2b1c8e4f6a5d2c8b9e3f1a4d7c
q2: 2a8f1c5e9b3d7a4f6c2e8b1d5a9f3c7e
q3: 9c3e7a1f5b8d2c6e4a9f1b7d3c5e8a2f

Saved to hashes.json
```

**4. Paste hashes into `grade.py`**

Open `grade.py` and fill in the `EXPECTED_HASHES` dictionary:
```python
EXPECTED_HASHES = {
    "q1": "7f3d9a2b1c8e4f6a5d2c8b9e3f1a4d7c",
    "q2": "2a8f1c5e9b3d7a4f6c2e8b1d5a9f3c7e",
    "q3": "9c3e7a1f5b8d2c6e4a9f1b7d3c5e8a2f",
}
```

**5. Verify with correct answers**
```bash
# Temporarily paste correct answers into q1.sql, q2.sql etc.
python grade.py
# Expected output: all ✅
```

**6. Verify with blank files**
```bash
# Clear q1.sql, q2.sql etc. back to blank
python grade.py
# Expected output: all ❌  — confirms grader is working correctly
```

---

### Phase 3 — Push to GitHub

**1. Confirm gitignore is working**
```bash
git status
# generate_hashes.py and hashes.json must NOT appear in the list
```

**2. Initialize and push**
```bash
git init
git add .
git commit -m "hw01 initial setup"
git remote add origin https://github.com/[YOUR-ORG]/[HOMEWORK-NAME]
git push -u origin main
```

---

### Phase 4 — Create the GitHub Classroom Assignment

```
classroom.github.com
→ Your classroom
→ New assignment
→ Title: [HOMEWORK NAME]
→ Repository prefix: [HOMEWORK NAME]
→ Private repositories: ✅
→ Template repository: [YOUR-ORG]/[HOMEWORK-NAME]
→ Next: Grading and feedback
→ Custom YAML tab → paste contents of autograder.yml
→ Protected file paths → type: .github/**/*  → Add Path
→ Enable feedback pull requests: ✅ (optional but recommended)
→ Create assignment
→ Copy invitation link → share with students
```

> **Note on Protected file paths:** Adding `.github/**/*` means that
> if a student modifies the autograder to give themselves full marks,
> GitHub Classroom will flag their submission with a warning label
> on your dashboard.

---

### Phase 5 — Student Flow

This is what students do after receiving the invitation link:

**1. Accept the assignment**
```
Click invitation link
→ GitHub creates their own private repo automatically
→ Clone it locally
```

**2. Set up locally**
```bash
# Start the database
docker compose up

# Set up Python
python -m venv venv
source venv/bin/activate    # Mac/Linux
venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

**3. Connect VSCode to the database**
```
Open VSCode
→ SQLTools extension (left sidebar)
→ The connection appears automatically from .vscode/settings.json
→ Click Connect
→ Write and run queries directly in VSCode with one click
```

**4. Write and test queries**
```
Open q1.sql
→ Write query below the comment instructions
→ Click Run in SQLTools to see results immediately
→ Adjust until results look correct
```

**5. Check score locally before submitting**
```bash
python grade.py
```

**6. Reset database if needed**
```bash
docker compose down -v    # destroys data
docker compose up         # fresh start with seed data
```

**7. Submit**
```bash
git add .
git commit -m "completed homework"
git push
```

**8. See results**
```
Go to their repo on GitHub
→ Actions tab
→ Latest workflow run
→ See ✅ or ❌ per question and total score
```

---

## How the Hashing Works

The autograder never compares query text — only result sets. This means:

- A student can write a completely different query than yours
- As long as it produces the **same rows**, they get full marks
- Students can read `grade.py` and see the hashes — but a hash reveals nothing about the answer

```
Your answer query runs
        ↓
Produces result set
        ↓
Result set is hashed → stored in grade.py
                              ↓
Student query runs    → produces result set → hashed → compared
```

---

## What Lives Where

| File | In student repo | Purpose |
|---|---|---|
| `q1.sql`, `q2.sql`... | ✅ | Student writes queries here |
| `grade.py` (with hashes) | ✅ | Hashes visible but meaningless |
| `docker-compose.yml` | ✅ | Local PostgreSQL |
| `.vscode/settings.json` | ✅ | Auto-connect SQLTools |
| `requirements.txt` | ✅ | Python dependencies |
| `.github/workflows/autograder.yml` | ✅ | GitHub Actions grading |
| `generate_hashes.py` | ❌ | Gitignored — your machine only |
| `hashes.json` | ❌ | Gitignored — your machine only |
| Answer queries | ❌ | Only ever inside generate_hashes.py |

---

## Troubleshooting

### psycopg2 installation errors
Always use `psycopg2-binary`, never `psycopg2`:
```bash
pip install psycopg2-binary
```

### Docker database not resetting
```bash
docker compose down -v    # -v flag removes the data volume
docker compose up
```

### Hash mismatch on correct answer
The most common cause is column ordering or float precision.
Re-run `generate_hashes.py` after any change to `seed.sql`.

### GitHub Actions failing
Check the Actions tab in the student repo for the full log.
The most common cause is a syntax error in a `.sql` file that
crashes the grader before writing `results.json`.

---

*Guide created for CS354 — Database Management Systems*