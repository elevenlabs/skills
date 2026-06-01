#!/bin/bash
# Fetch a merged weekly changelog markdown file from elevenlabs-dx main.
#
# Usage:
#   ./scripts/fetch-changelog.sh 2026-06-01
#   CHANGELOG_DATE=2026-06-01 ./scripts/fetch-changelog.sh

set -euo pipefail

CHANGELOG_DATE="${1:-${CHANGELOG_DATE:-}}"

if [ -z "$CHANGELOG_DATE" ]; then
  echo "Usage: $0 YYYY-MM-DD" >&2
  exit 1
fi

PATH_IN_REPO="fern/docs/pages/changelog/${CHANGELOG_DATE}.md"

gh api "repos/elevenlabs/elevenlabs-dx/contents/${PATH_IN_REPO}?ref=main" \
  --jq -r '.content' \
  | base64 -d
