#!/usr/bin/env bash
#
# purge-adams-fulltext.sh
# =======================
#
# WHAT THIS DOES
#   Commit a43b60e ("Adams' News", 21 Aug 2026) is the one and only commit in
#   your repository whose data/adams-news.json contains the FULL verbatim text
#   of nine copyrighted articles. A later commit removed that text from the
#   working tree, but git keeps every old version forever, so anyone who clones
#   the repo can still run
#
#       git show a43b60e:data/adams-news.json
#
#   and read all nine articles in full. This script rewrites that one commit so
#   the full text was never there, then leaves you with a single push command.
#
# WHAT THIS DOES NOT DO
#   It does not change your website. The rewrite swaps one old blob for another;
#   the tree at HEAD is byte-for-byte identical afterwards. I verified this on a
#   fresh clone of your public repo: the HEAD tree hash was
#   1af9754c52a8d828b17f75d07e98f105692c7998 both before and after, and the
#   commit count stayed at 514. GitHub Actions rebuilds from HEAD, so the
#   deployed site is unaffected.
#
#   It also does not push. It stops before that on purpose, prints its
#   verification, and tells you the one command to run once you are satisfied.
#
# WHAT CHANGES
#   Every commit SHA from a43b60e forward is rewritten, because a commit's hash
#   depends on its content and on its parent's hash. That is unavoidable with any
#   history rewrite. It means the push must be a force push, and any other clone
#   of this repo (another machine, a collaborator) must re-clone afterwards
#   rather than pull.
#
# BEFORE YOU RUN IT
#   Your working tree currently has about ten modified files, including the CV
#   PDF and refresh.sh. Commit or stash them first. The script refuses to run on
#   a dirty tree, because a history rewrite plus uncommitted work is how people
#   lose an afternoon.
#
# REQUIREMENT
#   git-filter-repo, which is not currently installed on your machine:
#       brew install git-filter-repo
#   or, if you would rather not use Homebrew:
#       pip3 install git-filter-repo
#
set -euo pipefail

REPO="$HOME/Documents/Claude/Projects/ericaraujo.com/ericaraujophd.github.io"
TARGET_FILE="data/adams-news.json"

# A sentence that appears only inside the full article text, never in an
# excerpt, a summary, or Joel's own notes. Its presence in a blob is what marks
# that blob as needing replacement.
MARKER="Autonomous agents could dramatically increase"

# The commit whose version of the file is the clean, excerpt-only replacement.
# This is "Removing full texts", the commit that fixed the working tree.
CLEAN_SOURCE="25ae06b"

cd "$REPO"

# ---------------------------------------------------------------- 0. sanity ---
command -v git-filter-repo >/dev/null 2>&1 || {
  echo "ERROR: git-filter-repo is not installed."
  echo "       brew install git-filter-repo    (or: pip3 install git-filter-repo)"
  exit 1
}

if [ -n "$(git status --porcelain)" ]; then
  echo "ERROR: your working tree has uncommitted changes. Commit or stash first:"
  echo
  git status --short
  exit 1
fi

# ------------------------------------------------------------- 1. back up -----
# A full mirror of the repository as it stands right now. If anything below goes
# wrong, this is a complete, restorable copy including every branch and tag.
BACKUP="$HOME/Desktop/ericaraujophd-backup-$(date +%Y%m%d-%H%M%S).git"
echo "==> Backing up to $BACKUP"
git clone --mirror . "$BACKUP" >/dev/null 2>&1
echo "    done"

# --------------------------------------------- 2. capture the replacement -----
# Extract the clean version of the file BEFORE rewriting, because the rewrite
# changes every commit SHA and $CLEAN_SOURCE will no longer resolve afterwards.
REPLACEMENT="$(mktemp -t adams-news-clean)"
git show "$CLEAN_SOURCE:$TARGET_FILE" > "$REPLACEMENT"

# Confirm the replacement really is clean, and really is the right file.
if grep -q "$MARKER" "$REPLACEMENT"; then
  echo "ERROR: the replacement blob still contains the full text. Aborting."
  exit 1
fi
python3 -c "import json,sys; d=json.load(open('$REPLACEMENT')); print(f'    replacement: {len(d)} entries, no full text')"

# Record the HEAD tree hash so we can prove the site content did not move.
TREE_BEFORE="$(git rev-parse 'HEAD^{tree}')"
COMMITS_BEFORE="$(git rev-list --count HEAD)"
REMOTE_URL="$(git remote get-url origin)"

# ---------------------------------------------------------- 3. rewrite --------
# git-filter-repo walks every blob in history. Any blob containing the marker
# is replaced wholesale with the clean file. Only one blob matches.
echo "==> Rewriting history (this takes a minute or two on a 519 MB repo)"
git filter-repo --force --quiet --blob-callback "
if b'$MARKER' in blob.data:
    blob.data = open('$REPLACEMENT','rb').read()
"

# filter-repo deliberately drops the remote so you cannot push by accident.
git remote add origin "$REMOTE_URL"

# ------------------------------------------------------------ 4. verify -------
echo
echo "==> Verification"

TREE_AFTER="$(git rev-parse 'HEAD^{tree}')"
COMMITS_AFTER="$(git rev-list --count HEAD)"

if [ "$TREE_BEFORE" = "$TREE_AFTER" ]; then
  echo "    site content   UNCHANGED  ($TREE_AFTER)"
else
  echo "    site content   CHANGED  $TREE_BEFORE -> $TREE_AFTER"
  echo "    STOP. Do not push. Restore from $BACKUP."
  exit 1
fi

if [ "$COMMITS_BEFORE" = "$COMMITS_AFTER" ]; then
  echo "    commit count   $COMMITS_AFTER (unchanged)"
else
  echo "    commit count   $COMMITS_BEFORE -> $COMMITS_AFTER"
fi

# Walk every historical version of the file and count marker hits. Expect zeroes.
echo -n "    full text in history: "
HITS=0
for c in $(git rev-list HEAD -- "$TARGET_FILE"); do
  n=$(git show "$c:$TARGET_FILE" 2>/dev/null | grep -c "$MARKER" || true)
  HITS=$((HITS + n))
done
if [ "$HITS" -eq 0 ]; then
  echo "none found (clean)"
else
  echo "$HITS occurrences STILL PRESENT"
  echo "    STOP. Do not push. Restore from $BACKUP."
  exit 1
fi

rm -f "$REPLACEMENT"

# ------------------------------------------------------------- 5. push --------
cat <<'EOF'

==> Ready to push.

    Nothing has left your machine yet. When you are satisfied, run:

        git push --force origin master

    Then confirm the site still builds and looks right:

        https://ericaraujo.com/adams-news

ONE HONEST CAVEAT
    A force push makes the old commits unreachable, but GitHub does not delete
    them immediately. For a while, anyone who already knows the old SHA
    (a43b60e) can still fetch that object through the GitHub API or a direct
    commit URL. Normal cloning, browsing and searching will not surface it.
    To have the old objects purged properly you have to ask GitHub Support to
    run garbage collection on the repository, citing the force push. Worth doing
    if you want this genuinely gone rather than merely hard to reach.
EOF
