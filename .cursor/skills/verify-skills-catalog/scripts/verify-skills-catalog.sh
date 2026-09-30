#!/usr/bin/env bash
# Drive the ElevenLabs skills catalog with the skills CLI.
# Session and proof files stay outside the disposable project.
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SKILL_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
CATALOG=$(cd "$SKILL_DIR/../../.." && pwd)

usage() {
  echo "Usage: verify-skills-catalog.sh launch|doctor|drive|cleanup" >&2
  echo "       verify-skills-catalog.sh drive install-catalog" >&2
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

assert_readme_stdout() {
  local path=$1
  python3 - "$path" <<'PY'
import pathlib, re, sys
text = pathlib.Path(sys.argv[1]).read_text()
plain = re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "", text)
required = [
    "https://github.com/elevenlabs/skills.git",
    "Found 11 skills",
    "Installing all 11 skills",
    "text-to-speech (copied)",
    "Installed 11 skills",
    "Agent detected — installing non-interactively",
]
missing = [line for line in required if line not in plain]
if missing:
    sys.stderr.write(f"README install stdout missing {missing!r}\n")
    sys.exit(1)
PY
}

assert_github_lock() {
  local path=$1
  python3 - "$path" <<'PY'
import json, pathlib, re, sys
lock = json.loads(pathlib.Path(sys.argv[1]).read_text())
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
skills = lock.get("skills", {})
if lock.get("version") != 1 or set(skills) != expected:
    sys.stderr.write(f"unexpected lock skills {sorted(skills)!r}\n")
    sys.exit(1)
for name, entry in skills.items():
    if entry.get("source") != "elevenlabs/skills" or entry.get("sourceType") != "github":
        sys.stderr.write(f"unexpected lock entry for {name}: {entry!r}\n")
        sys.exit(1)
    skill_path = entry.get("skillPath", "")
    if not skill_path.endswith("SKILL.md"):
        sys.stderr.write(f"unexpected skillPath for {name}: {skill_path!r}\n")
        sys.exit(1)
    if not re.fullmatch(r"[0-9a-f]{64}", entry.get("computedHash", "")):
        sys.stderr.write(f"unexpected computedHash for {name}: {entry.get('computedHash')!r}\n")
        sys.exit(1)
if skills["text-to-speech"].get("skillPath") != "text-to-speech/SKILL.md":
    sys.stderr.write(f"unexpected text-to-speech skillPath {skills['text-to-speech']!r}\n")
    sys.exit(1)
PY
}

assert_installed_catalog() {
  local path=$1
  local project=$2
  python3 - "$path" "$project" <<'PY'
import json, pathlib, sys
payload = json.loads(pathlib.Path(sys.argv[1]).read_text())
project = sys.argv[2]
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
if {item.get("name") for item in payload} != expected or len(payload) != len(expected):
    sys.stderr.write(f"expected the catalog install, got {payload!r}\n")
    sys.exit(1)
for item in payload:
    name = item.get("name")
    expected_path = f"{project}/.agents/skills/{name}"
    if item.get("scope") != "project" or item.get("agents") != ["Cursor"] or item.get("path") != expected_path:
        sys.stderr.write(f"unexpected list entry {item!r}\n")
        sys.exit(1)
PY
}

copy_proof() {
  local src=$1
  local dest=$2
  python3 - "$src" "$dest" <<'PY'
import pathlib, shutil, sys
src = pathlib.Path(sys.argv[1])
dest = pathlib.Path(sys.argv[2])

def copy_file(source: pathlib.Path, target: pathlib.Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)

def copy_dir(source: pathlib.Path, target: pathlib.Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for child in source.iterdir():
        destination = target / child.name
        if child.is_dir() and not child.is_symlink():
            copy_dir(child, destination)
        else:
            copy_file(child, destination)

if dest.exists():
    if dest.is_dir() and not dest.is_symlink():
        shutil.rmtree(dest)
    else:
        dest.unlink()
if src.is_dir() and not src.is_symlink():
    copy_dir(src, dest)
else:
    copy_file(src, dest)
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
  if [[ -z "${CURSOR_AGENT:-}" ]]; then
    echo "CURSOR_AGENT is unset. The README command would prompt for skills and hang." >&2
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
  if [[ -e "$project/.agents/skills" || -e "$project/skills-lock.json" ]]; then
    echo "Refusing to install into a project that already has skills." >&2
    exit 1
  fi
  run_logged "$evidence" launch-global-before npx --yes skills list -g --agent cursor --json
  (
    cd "$project"
    run_logged "$evidence" launch-add npx --yes skills add elevenlabs/skills
  ) || true
  if [[ "$(cat "$evidence/transcript/launch-add.exit")" != "0" ]]; then
    echo "README install failed. See $evidence/transcript/launch-add.stderr" >&2
    exit 1
  fi
  if [[ -s "$evidence/transcript/launch-add.stderr" ]]; then
    echo "README install wrote stderr. See $evidence/transcript/launch-add.stderr" >&2
    exit 1
  fi
  assert_readme_stdout "$evidence/transcript/launch-add.stdout"
  assert_github_lock "$project/skills-lock.json"
  run_logged "$evidence" launch-global-after npx --yes skills list -g --agent cursor --json
  cmp "$evidence/transcript/launch-global-before.stdout" "$evidence/transcript/launch-global-after.stdout"
  printf '%s\n' "$project" >"$evidence/project-path.txt"
  echo "Launched skills CLI 1.5.18 with: npx skills add elevenlabs/skills"
  echo "Disposable project: $project"
  echo "Evidence: $evidence"
}

doctor() {
  local evidence skill_md
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
  assert_installed_catalog "$evidence/transcript/doctor-list-installed.stdout" "$VERIFY_PROJECT"
  assert_github_lock "$VERIFY_PROJECT/skills-lock.json"
  skill_md="$VERIFY_PROJECT/.agents/skills/text-to-speech/SKILL.md"
  if [[ -L "$skill_md" || ! -f "$skill_md" ]]; then
    echo "Expected a regular copied SKILL.md at $skill_md" >&2
    exit 1
  fi
  cmp "$SKILLS_CATALOG/text-to-speech/SKILL.md" "$skill_md"
  run_logged "$evidence" doctor-global npx --yes skills list -g --agent cursor --json
  cmp "$evidence/transcript/launch-global-before.stdout" "$evidence/transcript/doctor-global.stdout"
  echo "Doctor ok. CLI 1.5.18, README install lists 11 Cursor project skills, global list unchanged."
}

drive_install() {
  local evidence skill_md
  require_session
  assert_safe_project "$VERIFY_PROJECT"
  evidence=$(evidence_root)
  printf '%s\n' "install-catalog" >"$evidence/feature-id.txt"
  skill_md="$VERIFY_PROJECT/.agents/skills/text-to-speech/SKILL.md"
  if [[ -L "$skill_md" || ! -f "$skill_md" ]]; then
    echo "Expected a regular copied SKILL.md at $skill_md" >&2
    exit 1
  fi
  cmp "$SKILLS_CATALOG/text-to-speech/SKILL.md" "$skill_md"
  mkdir -p "$evidence/installed/.agents/skills"
  copy_proof "$VERIFY_PROJECT/skills-lock.json" "$evidence/installed/skills-lock.json"
  copy_proof "$VERIFY_PROJECT/.agents/skills" "$evidence/installed/.agents/skills"
  assert_github_lock "$evidence/installed/skills-lock.json"
  (
    cd "$VERIFY_PROJECT"
    run_logged "$evidence" list-after npx --yes skills list --agent cursor --json
  )
  assert_installed_catalog "$evidence/transcript/list-after.stdout" "$VERIFY_PROJECT"
  find "$VERIFY_PROJECT" -print | sort >"$evidence/installed-tree.txt"
  echo "Drove install-catalog. Copied the README install into $evidence/installed"
}

cleanup() {
  local evidence
  require_session
  assert_safe_project "$VERIFY_PROJECT"
  evidence=$(evidence_root)
  if [[ -d "$VERIFY_PROJECT" ]]; then
    rm -rf "$VERIFY_PROJECT"
  fi
  if [[ -d "$VERIFY_PROJECT" ]]; then
    echo "Failed to remove disposable project $VERIFY_PROJECT" >&2
    exit 1
  fi
  local required=(
    "$evidence/transcript/launch-add.stdout"
    "$evidence/transcript/launch-add.exit"
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
}

main() {
  local command=${1:-}
  case "$command" in
    launch) launch ;;
    doctor) doctor ;;
    drive)
      local feature=${2:-}
      if [[ "$feature" != "install-catalog" ]]; then
        echo "This helper drives install-catalog. Other features are in features/." >&2
        usage
      fi
      drive_install
      ;;
    cleanup) cleanup ;;
    *) usage ;;
  esac
}

main "$@"
