#!/usr/bin/env bash
# Drive the ElevenLabs skills catalog with the skills CLI.
# Session and proof files stay outside the disposable project.
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SKILL_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
CATALOG=$(cd "$SKILL_DIR/../../.." && pwd)

usage() {
  echo "Usage: verify-skills-catalog.sh launch|doctor|drive|cleanup" >&2
  echo "       verify-skills-catalog.sh drive install-text-to-speech" >&2
  exit 2
}

evidence_root() {
  if [[ -n "${VERIFY_SKILLS_EVIDENCE_DIR:-}" ]]; then
    printf '%s\n' "$VERIFY_SKILLS_EVIDENCE_DIR"
  else
    printf '%s\n' "$SKILL_DIR/evidence/latest"
  fi
}

session_file() {
  printf '%s/session.env\n' "$(evidence_root)"
}

require_session() {
  local file
  file=$(session_file)
  if [[ ! -f "$file" ]]; then
    echo "No session at $file. Run launch first." >&2
    exit 1
  fi
  # shellcheck disable=SC1090
  source "$file"
}

assert_safe_project() {
  local project=$1
  local home catalog evidence
  home=$(cd "$HOME" && pwd)
  catalog=$(cd "$CATALOG" && pwd)
  evidence=$(cd "$(evidence_root)" && pwd)
  case "$project" in
    /tmp/verify-skills-catalog.*) ;;
    *)
      echo "Refusing project path $project (must match /tmp/verify-skills-catalog.*)." >&2
      exit 1
      ;;
  esac
  if [[ "$project" == "$home" || "$project" == "$catalog" || "$project" == "$evidence" ]]; then
    echo "Refusing to drive $project." >&2
    exit 1
  fi
  case "$evidence" in
    "$project"|"$project"/*)
      echo "Evidence directory is inside the disposable project." >&2
      exit 1
      ;;
  esac
  case "$catalog" in
    "$project"|"$project"/*)
      echo "Catalog checkout is inside the disposable project." >&2
      exit 1
      ;;
  esac
}

log_cmd() {
  local evidence=$1
  shift
  mkdir -p "$evidence/transcript"
  {
    printf 'command:'
    printf ' %q' "$@"
    printf '\n'
  } >>"$evidence/transcript/commands.log"
}

run_logged() {
  local evidence=$1
  local name=$2
  shift 2
  mkdir -p "$evidence/transcript"
  log_cmd "$evidence" "$@"
  set +e
  "$@" >"$evidence/transcript/${name}.stdout" 2>"$evidence/transcript/${name}.stderr"
  local code=$?
  set -e
  printf '%s\n' "$code" >"$evidence/transcript/${name}.exit"
  return "$code"
}

assert_version_file() {
  local path=$1
  python3 - "$path" <<'PY'
import pathlib, sys
text = pathlib.Path(sys.argv[1]).read_text()
if text != "1.5.18\n":
    sys.stderr.write(f"expected skills CLI 1.5.18, got {text!r}\n")
    sys.exit(1)
PY
}

assert_catalog_list() {
  local path=$1
  python3 - "$path" <<'PY'
import pathlib, re, sys
text = pathlib.Path(sys.argv[1]).read_text()
names = []
for line in text.splitlines():
    match = re.match(r"^[\s│◇●├└╮╯─]*([a-z0-9]+(?:-[a-z0-9]+)*)\s*$", line)
    if match:
        names.append(match.group(1))
expected = {
    "agents",
    "dubbing",
    "music",
    "setup-api-key",
    "sound-effects",
    "speech-engine",
    "speech-to-text",
    "text-to-speech",
    "update-skills-from-changelog",
    "voice-changer",
    "voice-isolator",
}
if set(names) != expected or len(names) != len(expected):
    sys.stderr.write(f"catalog names {names!r} != {sorted(expected)!r}\n")
    sys.exit(1)
PY
}

assert_empty_list() {
  local path=$1
  python3 - "$path" <<'PY'
import pathlib, sys
text = pathlib.Path(sys.argv[1]).read_text().strip()
if text != "[]":
    sys.stderr.write(f"expected empty project list, got {text!r}\n")
    sys.exit(1)
PY
}

assert_installed_list() {
  local path=$1
  local project=$2
  python3 - "$path" "$project" <<'PY'
import json, pathlib, sys
payload = json.loads(pathlib.Path(sys.argv[1]).read_text())
project = sys.argv[2]
if len(payload) != 1:
    sys.stderr.write(f"expected one installed skill, got {payload!r}\n")
    sys.exit(1)
item = payload[0]
expected_path = f"{project}/.agents/skills/text-to-speech"
if item.get("name") != "text-to-speech" or item.get("scope") != "project":
    sys.stderr.write(f"unexpected list entry {item!r}\n")
    sys.exit(1)
if item.get("path") != expected_path or item.get("agents") != ["Cursor"]:
    sys.stderr.write(f"unexpected list entry {item!r}\n")
    sys.exit(1)
PY
}

assert_lock() {
  local path=$1
  local catalog=$2
  python3 - "$path" "$catalog" <<'PY'
import json, pathlib, re, sys
lock = json.loads(pathlib.Path(sys.argv[1]).read_text())
catalog = sys.argv[2]
entry = lock.get("skills", {}).get("text-to-speech")
if lock.get("version") != 1 or not isinstance(entry, dict):
    sys.stderr.write(f"unexpected lock {lock!r}\n")
    sys.exit(1)
if entry.get("source") != catalog or entry.get("sourceType") != "local":
    sys.stderr.write(f"unexpected lock entry {entry!r}\n")
    sys.exit(1)
if not re.fullmatch(r"[0-9a-f]{64}", entry.get("computedHash", "")):
    sys.stderr.write(f"unexpected computedHash {entry.get('computedHash')!r}\n")
    sys.exit(1)
PY
}

launch() {
  local evidence file project
  evidence=$(evidence_root)
  file=$(session_file)
  if [[ -e "$file" ]]; then
    echo "Session already exists at $file. Run cleanup before launching again." >&2
    exit 1
  fi
  mkdir -p "$evidence/transcript"
  project=$(mktemp -d /tmp/verify-skills-catalog.XXXXXX)
  assert_safe_project "$project"
  cat >"$file" <<EOF
VERIFY_PROJECT=$project
SKILLS_CATALOG=$CATALOG
EOF
  if ! run_logged "$evidence" launch-version npx --yes skills --version; then
    echo "skills CLI failed to launch. See $evidence/transcript/launch-version.stderr" >&2
    exit 1
  fi
  assert_version_file "$evidence/transcript/launch-version.stdout"
  printf '%s\n' "$project" >"$evidence/project-path.txt"
  echo "Launched skills CLI 1.5.18. Disposable project: $project"
  echo "Evidence: $evidence"
}

doctor() {
  local evidence
  require_session
  assert_safe_project "$VERIFY_PROJECT"
  evidence=$(evidence_root)
  if [[ ! -d "$VERIFY_PROJECT" ]]; then
    echo "Disposable project is missing: $VERIFY_PROJECT" >&2
    exit 1
  fi
  (
    cd "$VERIFY_PROJECT"
    run_logged "$evidence" doctor-version npx --yes skills --version
    run_logged "$evidence" doctor-list-catalog npx --yes skills add "$SKILLS_CATALOG" --list
    run_logged "$evidence" doctor-list-installed npx --yes skills list --agent cursor --json
  )
  assert_version_file "$evidence/transcript/doctor-version.stdout"
  assert_catalog_list "$evidence/transcript/doctor-list-catalog.stdout"
  assert_empty_list "$evidence/transcript/doctor-list-installed.stdout"
  if [[ -e "$VERIFY_PROJECT/.agents/skills/text-to-speech" || -e "$VERIFY_PROJECT/skills-lock.json" ]]; then
    echo "Doctor expected a project with no text-to-speech install." >&2
    exit 1
  fi
  echo "Doctor ok. CLI 1.5.18, catalog lists text-to-speech, project list is []."
}

drive_install() {
  local evidence skill_md
  require_session
  assert_safe_project "$VERIFY_PROJECT"
  evidence=$(evidence_root)
  printf '%s\n' "install-text-to-speech" >"$evidence/feature-id.txt"
  (
    cd "$VERIFY_PROJECT"
    run_logged "$evidence" drive-install npx --yes skills add "$SKILLS_CATALOG" --skill text-to-speech --agent cursor -y --copy
  )
  if [[ "$(cat "$evidence/transcript/drive-install.exit")" != "0" ]]; then
    echo "Install command failed. See $evidence/transcript/drive-install.stderr" >&2
    exit 1
  fi
  skill_md="$VERIFY_PROJECT/.agents/skills/text-to-speech/SKILL.md"
  if [[ -L "$skill_md" || ! -f "$skill_md" ]]; then
    echo "Expected a regular copied SKILL.md at $skill_md" >&2
    exit 1
  fi
  cmp "$SKILLS_CATALOG/text-to-speech/SKILL.md" "$skill_md"
  mkdir -p "$evidence/installed"
  cp -a "$VERIFY_PROJECT/skills-lock.json" "$evidence/installed/skills-lock.json"
  mkdir -p "$evidence/installed/.agents/skills"
  cp -a "$VERIFY_PROJECT/.agents/skills/text-to-speech" "$evidence/installed/.agents/skills/text-to-speech"
  assert_lock "$evidence/installed/skills-lock.json" "$SKILLS_CATALOG"
  (
    cd "$VERIFY_PROJECT"
    run_logged "$evidence" list-after npx --yes skills list --agent cursor --json
  )
  assert_installed_list "$evidence/transcript/list-after.stdout" "$VERIFY_PROJECT"
  find "$VERIFY_PROJECT" -print | sort >"$evidence/installed-tree.txt"
  echo "Drove install-text-to-speech. Copied skill files and skills-lock.json into $evidence/installed"
}

cleanup() {
  local evidence remove_exit
  require_session
  assert_safe_project "$VERIFY_PROJECT"
  evidence=$(evidence_root)
  remove_exit=0
  if [[ -d "$VERIFY_PROJECT" ]]; then
    (
      cd "$VERIFY_PROJECT"
      run_logged "$evidence" cleanup-remove npx --yes skills remove --skill text-to-speech --agent cursor -y
    ) || remove_exit=$?
    mkdir -p "$evidence/after-remove"
    if [[ -f "$VERIFY_PROJECT/skills-lock.json" ]]; then
      cp -a "$VERIFY_PROJECT/skills-lock.json" "$evidence/after-remove/skills-lock.json"
    fi
    find "$VERIFY_PROJECT" -print | sort >"$evidence/after-remove/tree.txt"
    rm -rf "$VERIFY_PROJECT"
  fi
  if [[ -d "$VERIFY_PROJECT" ]]; then
    echo "Failed to remove disposable project $VERIFY_PROJECT" >&2
    exit 1
  fi
  local required=(
    "$evidence/transcript/drive-install.stdout"
    "$evidence/transcript/drive-install.exit"
    "$evidence/transcript/list-after.stdout"
    "$evidence/installed/skills-lock.json"
    "$evidence/installed/.agents/skills/text-to-speech/SKILL.md"
    "$evidence/feature-id.txt"
  )
  local path
  for path in "${required[@]}"; do
    if [[ ! -f "$path" ]]; then
      echo "Cleanup removed or never captured evidence: $path" >&2
      exit 1
    fi
  done
  printf '%s\n' "$VERIFY_PROJECT" >"$evidence/project-removed.txt"
  echo "Cleaned $VERIFY_PROJECT. Evidence remains at $evidence"
  if [[ "$remove_exit" != "0" ]]; then
    echo "skills remove exited $remove_exit" >&2
    exit "$remove_exit"
  fi
}

main() {
  local command=${1:-}
  case "$command" in
    launch) launch ;;
    doctor) doctor ;;
    drive)
      local feature=${2:-}
      if [[ "$feature" != "install-text-to-speech" ]]; then
        echo "This helper drives install-text-to-speech. Other features are in features/." >&2
        usage
      fi
      drive_install
      ;;
    cleanup) cleanup ;;
    *) usage ;;
  esac
}

main "$@"
