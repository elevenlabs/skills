# AGENTS.md

## Cursor Cloud specific instructions

### Repository overview

This is a **content/documentation repository** — a collection of AI coding assistant skill definitions (SKILL.md files + reference markdown) for ElevenLabs developer products. It is **not a runnable application**. There is no build step, no web server, no database, and no package manager workspace at the root level.

### Key components

| Component | Path | Purpose |
|---|---|---|
| Skill definitions | `<skill>/SKILL.md` + `<skill>/references/` | Markdown content consumed by AI coding assistants |
| Eval harness | `evals/run_all.py` | Python script that tests skills via `cursor-agent` CLI |
| Eval data | `evals/<skill>/trigger_eval.json`, `evals/<skill>/evals.json` | Trigger and functional eval test cases |
| Transcribe tool | `openclaw/elevenlabs-transcribe/` | Community OpenClaw tool with its own venv (`scripts/transcribe.sh` auto-manages) |

### Running evals

The eval harness (`evals/run_all.py`) requires the external [Cursor Agent CLI](https://cursor.com/docs/cli/using) (`cursor-agent` on `PATH`) and Cursor authentication (`cursor-agent login` or `CURSOR_API_KEY` env var). See `README.md` for full usage. The harness uses only Python stdlib — no pip install needed for it.

**Gotcha**: `evals/run_all.py` calls `_ensure_cursor_agent_available()` at module import time, so importing the module without `cursor-agent` on PATH will cause `sys.exit(1)`. To test grading functions in isolation, patch out that call before exec'ing the source.

### Transcribe tool

The `openclaw/elevenlabs-transcribe/scripts/transcribe.sh` wrapper auto-creates a `.venv/` and installs deps from its local `requirements.txt` on first run. It requires `ffmpeg` (pre-installed) and `ELEVENLABS_API_KEY`.

### Linting / testing / building

There are **no configured linters, test frameworks, or build systems** at the repo level. The SKILL.md files are static markdown content. The eval harness is the closest thing to a test suite.

To verify the codebase integrity without `cursor-agent`:
- Parse all SKILL.md frontmatter (check `name:` and `description:` fields)
- Validate all eval JSON files (`trigger_eval.json`, `evals.json`)
- Syntax-check `evals/run_all.py` (`python3 -c "import ast; ast.parse(open('evals/run_all.py').read())"`)
- Test grading functions by patching out the cursor-agent availability check

### Environment notes

- Python 3.12+ is available system-wide
- `python3.12-venv` must be installed for the transcribe tool's venv to work (`sudo apt-get install -y python3.12-venv`)
- `ffmpeg` is pre-installed
- No `node`, `npm`, or JS runtime is needed for development (only for end-user skill installation via `npx skills add`)
