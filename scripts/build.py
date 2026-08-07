#!/usr/bin/env python3
"""
build.py — CV build orchestrator.

Steps:
  1. Compile JSON → rendercv YAML  (to_rendercv.py)
  2. Run rendercv to render the PDF
  3. Archive the previous PDF to public/cv/archive/ with a timestamp
  4. Copy the new PDF to public/cv/ so it's accessible at /cv/Eric_Araujo_CV.pdf

Note: website generation (to_website.py) has been retired. The Astro site
imports data/*.json directly — no intermediate CSV or Markdown files needed.

Usage (run from repo root):
    python scripts/build.py [--no-render]

Flags:
  --no-render  Generate YAML but skip the rendercv render step
"""

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT      = Path(__file__).parent.parent
SCRIPTS   = ROOT / "scripts"
RENDERCV  = ROOT / "rendercv"
CV_YAML   = RENDERCV / "Eric_Araújo_CV.yaml"
CV_PDF    = RENDERCV / "rendercv_output" / "Eric_Araújo_CV.pdf"
WEB_PDF   = ROOT / "public" / "cv" / "Eric_Araujo_CV.pdf"
BACKUPS   = ROOT / "public" / "cv" / "archive"


def run(script: str, label: str):
    print(f"\n── {label} ──")
    result = subprocess.run([sys.executable, SCRIPTS / script], cwd=ROOT)
    if result.returncode != 0:
        sys.exit(f"  FAILED: {script}")


def archive_pdf():
    """Copy the current CV PDF to cv/archive/ with today's date stamp."""
    BACKUPS.mkdir(parents=True, exist_ok=True)
    if WEB_PDF.exists():
        stamp = datetime.now().strftime("%Y-%m-%d")
        dest  = BACKUPS / f"Eric_Araujo_CV_{stamp}.pdf"
        shutil.copy2(WEB_PDF, dest)
        print(f"  Archived → public/cv/archive/Eric_Araujo_CV_{stamp}.pdf")
    else:
        print("  No existing CV PDF to archive.")


def render_cv():
    print("\n── Rendering PDF with rendercv ──")

    before = CV_PDF.stat().st_mtime if CV_PDF.exists() else 0

    result = subprocess.run(
        ["rendercv", "render", CV_YAML.name],
        cwd=RENDERCV,
    )
    if result.returncode != 0:
        sys.exit(
            "\n  BUILD FAILED: rendercv exited non-zero.\n"
            "  The published PDF was NOT updated. Scroll up for the validation\n"
            "  table — every section must use a real rendercv entry type\n"
            "  (NormalEntry, EducationEntry, PublicationEntry, ...). Custom keys\n"
            "  are silently dropped and trip 'This field is required!' errors.\n"
            "  Needs rendercv 2.7 on Python >= 3.12 (see rendercv/requirements.txt)."
        )

    # A zero exit code is not enough: confirm a PDF was actually (re)written.
    if not CV_PDF.exists():
        sys.exit(f"\n  BUILD FAILED: rendercv reported success but {CV_PDF} does not exist.")
    if CV_PDF.stat().st_mtime <= before:
        sys.exit(f"\n  BUILD FAILED: {CV_PDF} was not rewritten — stale output, refusing to publish.")

    WEB_PDF.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(CV_PDF, WEB_PDF)
    print(f"  Published → {WEB_PDF.relative_to(ROOT)}")


def main():
    parser = argparse.ArgumentParser(description="Build CV PDF from JSON sources.")
    parser.add_argument("--no-render", action="store_true", help="Generate YAML but skip PDF render")
    args = parser.parse_args()

    run("to_rendercv.py", "Compiling JSON → rendercv YAML")
    if not args.no_render:
        archive_pdf()
        render_cv()

    print("\n✓ Build complete.")


if __name__ == "__main__":
    main()
