#!/usr/bin/env python3
"""
build.py — Full CV build orchestrator.

Steps:
  1. Compile JSON → rendercv YAML  (to_rendercv.py)
  2. Compile JSON → website files  (to_website.py)
  3. Run rendercv to render the PDF
  4. Archive the previous PDF to cv/archive/ with a timestamp
  5. Copy the new PDF to cv/ so it's accessible at /cv/Eric_Araujo_CV.pdf

Usage (run from repo root):
    python scripts/build.py [--cv-only] [--web-only] [--no-render]

Flags:
  --cv-only    Skip website generation
  --web-only   Skip rendercv YAML + PDF rendering
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
WEB_PDF   = ROOT / "cv" / "Eric_Araujo_CV.pdf"
BACKUPS   = ROOT / "cv" / "archive"


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
        print(f"  Archived → cv/archive/Eric_Araujo_CV_{stamp}.pdf")
    else:
        print("  No existing CV PDF to archive.")


def render_cv():
    print("\n── Rendering PDF with rendercv ──")
    result = subprocess.run(
        ["rendercv", "render", CV_YAML.name],
        cwd=RENDERCV,
    )
    if result.returncode != 0:
        sys.exit("  rendercv render FAILED")
    # Copy rendered PDF to website root as cv.pdf
    if CV_PDF.exists():
        shutil.copy2(CV_PDF, WEB_PDF)
        print(f"  Copied → {WEB_PDF.relative_to(ROOT.parent)}")
    else:
        print(f"  Warning: expected PDF at {CV_PDF} not found.")


def main():
    parser = argparse.ArgumentParser(description="Build CV and website from JSON sources.")
    parser.add_argument("--cv-only",   action="store_true", help="Skip website generation")
    parser.add_argument("--web-only",  action="store_true", help="Skip rendercv YAML + PDF")
    parser.add_argument("--no-render", action="store_true", help="Generate YAML but skip PDF render")
    args = parser.parse_args()

    if not args.web_only:
        run("to_rendercv.py", "Compiling JSON → rendercv YAML")
        if not args.no_render:
            archive_pdf()
            render_cv()

    if not args.cv_only:
        run("to_website.py", "Compiling JSON → website files")

    print("\n✓ Build complete.")


if __name__ == "__main__":
    main()
