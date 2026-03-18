## Cursor Cloud specific instructions

This is a **documentation/skills repository** — not a traditional application. It contains Markdown skill definitions for ElevenLabs AI products following the [Agent Skills specification](https://agentskills.io/specification), plus one runnable Python transcription tool.

### Repository structure

- Top-level directories (`text-to-speech/`, `speech-to-text/`, `agents/`, `sound-effects/`, `music/`, `setup-api-key/`) contain `SKILL.md` files and `references/` Markdown docs. No build/lint/test applies to these.
- `openclaw/elevenlabs-transcribe/` contains the only executable code: a Python transcription script with a self-bootstrapping bash wrapper.

### Running the transcription tool

The script is at `openclaw/elevenlabs-transcribe/scripts/transcribe.sh`. It auto-creates a `.venv/` and installs Python dependencies on first run.

Prerequisites: `python3`, `ffmpeg`, and `ELEVENLABS_API_KEY` env var.

```bash
# Basic transcription
bash openclaw/elevenlabs-transcribe/scripts/transcribe.sh <audio_file>

# With diarization and JSON output
bash openclaw/elevenlabs-transcribe/scripts/transcribe.sh <audio_file> --diarize --json
```

### Cursor CLI

The Cursor CLI (`agent`) is installed at `~/.local/bin/agent`. It authenticates via the `CURSOR_API_KEY` env var (injected from secrets).

```bash
# Non-interactive (print mode)
agent --trust -p "your prompt"

# Interactive
agent --trust
```

The `--trust` flag is required to skip the workspace trust prompt in non-interactive/scripted usage.

### Caveats

- There is no project-wide linter, test framework, or build system. The repo is documentation-first.
- `python3.12-venv` system package is required for `python3 -m venv` to work (not pre-installed on some Ubuntu images).
- The `.venv/` directory under `openclaw/elevenlabs-transcribe/scripts/` is gitignored; it will be recreated automatically by `transcribe.sh` on first run.
- All ElevenLabs API calls require a valid `ELEVENLABS_API_KEY` — there is no offline/mock mode.
- `~/.local/bin` must be on `PATH` for the `agent` command — this is configured in `~/.bashrc`.
