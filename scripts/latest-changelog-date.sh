#!/bin/bash
# Return the newest changelog date on elevenlabs-dx main.

set -euo pipefail

gh api repos/elevenlabs/elevenlabs-dx/contents/fern/docs/pages/changelog?ref=main \
  --jq 'map(select(.name | test("^[0-9]{4}-[0-9]{2}-[0-9]{2}\\.md$")) | .name | rtrimstr(".md")) | sort | last'
