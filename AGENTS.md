# AGENTS.md

## Cursor Cloud specific instructions

This is a **documentation/skills repository** (not a traditional application). It contains ElevenLabs Agent Skills (structured `SKILL.md` files + reference docs) and an evaluation framework.

### Key components

| Component | Path | Purpose |
|-----------|------|---------|
| Skills | `{skill}/SKILL.md` + `{skill}/references/*.md` | Agent skill definitions for 8 ElevenLabs capabilities |
| Eval framework | `evals/run_all.py` | Tests skill triggering and functional correctness via `cursor-agent` CLI |
| Eval data | `evals/{skill}/trigger_eval.json`, `evals/{skill}/evals.json` | Test cases for each skill |
| Community scripts | `openclaw/` | Community-maintained transcription script (do not modify in automated updates) |

### Running evaluations

The eval harness (`evals/run_all.py`) requires:
- Python 3.x (stdlib only — no pip install needed)
- `cursor-agent` CLI on PATH (or set `CURSOR_AGENT` env var to override)
- Cursor authentication (`cursor-agent login` or `CURSOR_API_KEY` env var)

See README.md for full eval commands (trigger-only, functional-only, specific skills, etc.).

### Linting / testing without cursor-agent

You can validate all skill and eval files structurally without `cursor-agent`:
```bash
python3 -c "
import json
from pathlib import Path
skills = ['text-to-speech','speech-to-text','agents','sound-effects','music','voice-changer','voice-isolator','setup-api-key']
for s in skills:
    content = (Path(s)/'SKILL.md').read_text()
    assert content.split('\n')[0].strip() == '---', f'{s}: bad frontmatter'
    for f in ['trigger_eval.json','evals.json']:
        p = Path('evals')/s/f
        if p.exists(): json.loads(p.read_text())
print('All files valid')
"
```

### Gotchas

- `evals/run_all.py` calls `_ensure_cursor_agent_available()` at module import time and exits immediately if `cursor-agent` is not found. This is intentional — the full eval suite cannot run without it.
- The eval script uses only Python stdlib (no third-party packages). Do not add a `requirements.txt` for the core project.
- The `openclaw/` directory is community-maintained and has its own `requirements.txt` and venv-bootstrapping script.
