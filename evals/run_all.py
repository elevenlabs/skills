#!/usr/bin/env python3
from __future__ import annotations
"""Run trigger and functional evaluations across all ElevenLabs skills.

Functional evals run cursor-agent with workspace = each eval's scratch folder only; skill
SKILL.md files and the rest of the repo are not writable by the nested agent.

Trigger evals run cursor-agent in an isolated temporary workspace directory (outside the repo),
with a ``.claude/commands/`` tree created inside that temp workspace so nothing is written under
the repo's own ``.claude/`` and the nested agent cannot create folders in the repo root.

Usage:
    # Run everything
    python evals/run_all.py

    # Trigger evals only
    python evals/run_all.py --trigger-only

    # Functional evals only
    python evals/run_all.py --functional-only

    # Specific skills
    python evals/run_all.py --skills text-to-speech agents

    # Custom model and parallelism
    python evals/run_all.py --model gpt-5.4-high --workers 5
"""

import argparse
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
EVALS_DIR = Path(__file__).parent

# Cursor Agent CLI (https://cursor.com/docs/cli/using); override with CURSOR_AGENT if needed.
CURSOR_AGENT_BIN = os.environ.get("CURSOR_AGENT", "cursor-agent")
# Default GPT-5.4 tier (see `cursor-agent --list-models`).
DEFAULT_CURSOR_MODEL = "gpt-5.4-medium"


def _ensure_cursor_agent_available() -> None:
    """Fail fast if the configured cursor-agent binary is not available on PATH."""
    if shutil.which(CURSOR_AGENT_BIN) is None:
        print(
            f"Error: cursor-agent binary '{CURSOR_AGENT_BIN}' not found on PATH.\n"
            "Install the cursor-agent CLI and/or set the CURSOR_AGENT environment "
            "variable to the correct binary name or path.",
            file=sys.stderr,
        )
        sys.exit(1)


ALL_SKILLS = [
    "text-to-speech",
    "speech-to-text",
    "agents",
    "sound-effects",
    "music",
    "setup-api-key",
]


def parse_skill_md(skill_path: Path) -> tuple:
    """Parse a SKILL.md file, returning (name, description, full_content)."""
    content = (skill_path / "SKILL.md").read_text()
    lines = content.split("\n")
    if lines[0].strip() != "---":
        raise ValueError("SKILL.md missing frontmatter")
    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        raise ValueError("SKILL.md missing closing ---")
    name = ""
    description = ""
    fm_lines = lines[1:end_idx]
    i = 0
    while i < len(fm_lines):
        line = fm_lines[i]
        if line.startswith("name:"):
            name = line[len("name:"):].strip().strip('"').strip("'")
        elif line.startswith("description:"):
            value = line[len("description:"):].strip()
            if value in (">", "|", ">-", "|-"):
                parts = []
                i += 1
                while i < len(fm_lines) and (fm_lines[i].startswith("  ") or fm_lines[i].startswith("\t")):
                    parts.append(fm_lines[i].strip())
                    i += 1
                description = " ".join(parts)
                continue
            else:
                description = value.strip('"').strip("'")
        i += 1
    if not name:
        raise ValueError("SKILL.md missing 'name' in frontmatter")
    if not description:
        raise ValueError("SKILL.md missing 'description' in frontmatter")
    return name, description, content


def run_single_trigger_query(
    query: str,
    skill_name: str,
    skill_description: str,
    timeout: int,
    model: str = None,
) -> bool:
    """Run a single query and return whether the skill was triggered.

    Uses a throwaway temp workspace (only ``.claude/commands/``) so the nested
    agent cannot create files in the real repo root. Works with installed skills
    (e.g. under ``~/.cursor`` / global config) and the temporary slash command.
    """
    unique_id = uuid.uuid4().hex[:8]
    clean_name = "%s-skill-%s" % (skill_name, unique_id)

    # Names to match: both the real skill name and the temp command name
    match_names = {skill_name, clean_name}

    workspace_dir = tempfile.mkdtemp(prefix="skills-eval-trigger-")
    try:
        project_commands_dir = Path(workspace_dir) / ".claude" / "commands"
        project_commands_dir.mkdir(parents=True, exist_ok=True)
        command_file = project_commands_dir / ("%s.md" % clean_name)

        indented_desc = "\n  ".join(skill_description.split("\n"))
        command_content = (
            "---\n"
            "description: |\n"
            "  %s\n"
            "---\n\n"
            "# %s\n\n"
            "This skill handles: %s\n"
        ) % (indented_desc, skill_name, skill_description)
        command_file.write_text(command_content)

        m = model or DEFAULT_CURSOR_MODEL
        cmd = [
            CURSOR_AGENT_BIN,
            "-p",
            "--output-format", "stream-json",
            "--trust",
            "--workspace",
            workspace_dir,
            "--model",
            m,
            query,
        ]

        env = dict(os.environ)

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd=workspace_dir,
            env=env,
        )
        assert process.stdout is not None

        triggered = False
        start_time = time.time()
        line_queue: queue.Queue[str | None] = queue.Queue()

        def _process_stream_line(raw_line: str) -> bool:
            """Parse one stream-json line. Returns True if processing should stop."""
            nonlocal triggered
            line = raw_line.strip()
            if not line:
                return False
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                return False

            if event.get("type") == "assistant":
                message = event.get("message", {})
                for block in message.get("content", []):
                    if block.get("type") != "tool_use":
                        continue
                    tool_name = block.get("name", "")
                    tool_input = block.get("input", {})

                    if tool_name == "Skill":
                        skill_arg = tool_input.get("skill", "")
                        if any(n in skill_arg for n in match_names):
                            triggered = True

                    elif tool_name == "Read":
                        file_path = tool_input.get("file_path", "")
                        if any(n in file_path for n in match_names):
                            triggered = True

                    elif tool_name == "ToolSearch":
                        continue

            elif event.get("type") == "result":
                return True

            return triggered

        def _read_stdout_lines() -> None:
            """Stream newline-delimited JSON from the child process on all platforms."""
            try:
                for raw_line in process.stdout:
                    line_queue.put(raw_line.decode("utf-8", errors="replace"))
            finally:
                line_queue.put(None)

        stdout_reader = threading.Thread(target=_read_stdout_lines, daemon=True)
        stdout_reader.start()

        try:
            while time.time() - start_time < timeout:
                try:
                    raw_line = line_queue.get(timeout=1.0)
                except queue.Empty:
                    if process.poll() is not None:
                        break
                    continue

                if raw_line is None:
                    break

                if _process_stream_line(raw_line):
                    break

        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
            process.stdout.close()
            stdout_reader.join(timeout=1.0)

        return triggered
    finally:
        shutil.rmtree(workspace_dir, ignore_errors=True)


def run_trigger_eval_for_skill(
    skill_name: str,
    model: str,
    workers: int,
    runs_per_query: int,
    timeout: int,
    verbose: bool,
) -> dict:
    """Run trigger evaluation for a single skill."""
    trigger_file = EVALS_DIR / skill_name / "trigger_eval.json"
    skill_path = REPO_ROOT / skill_name

    if not trigger_file.exists():
        return {"skill": skill_name, "error": "No trigger_eval.json found"}
    if not (skill_path / "SKILL.md").exists():
        return {"skill": skill_name, "error": "No SKILL.md at %s" % skill_path}

    eval_set = json.loads(trigger_file.read_text())
    name, description, _ = parse_skill_md(skill_path)

    if verbose:
        print("\n" + "=" * 60, file=sys.stderr)
        print("TRIGGER EVAL: %s" % skill_name, file=sys.stderr)
        print("Description: %s..." % description[:80], file=sys.stderr)
        print("Queries: %d" % len(eval_set), file=sys.stderr)
        print("=" * 60, file=sys.stderr)

    t0 = time.time()

    # Run all queries in parallel
    with ProcessPoolExecutor(max_workers=workers) as executor:
        future_to_info = {}
        for item in eval_set:
            for run_idx in range(runs_per_query):
                future = executor.submit(
                    run_single_trigger_query,
                    item["query"],
                    name,
                    description,
                    timeout,
                    model,
                )
                future_to_info[future] = (item, run_idx)

        query_triggers = {}
        query_items = {}
        for future in as_completed(future_to_info):
            item, _ = future_to_info[future]
            query = item["query"]
            query_items[query] = item
            if query not in query_triggers:
                query_triggers[query] = []
            try:
                query_triggers[query].append(future.result())
            except Exception as e:
                print("Warning: query failed: %s" % e, file=sys.stderr)
                query_triggers[query].append(False)

    results = []
    for query, triggers in query_triggers.items():
        item = query_items[query]
        trigger_rate = sum(triggers) / len(triggers)
        should_trigger = item["should_trigger"]
        did_pass = trigger_rate >= 0.5 if should_trigger else trigger_rate < 0.5
        results.append({
            "query": query,
            "should_trigger": should_trigger,
            "trigger_rate": trigger_rate,
            "triggers": sum(triggers),
            "runs": len(triggers),
            "pass": did_pass,
        })

    elapsed = time.time() - t0
    passed = sum(1 for r in results if r["pass"])
    total = len(results)

    if verbose:
        print("  Result: %d/%d passed (%.1fs)" % (passed, total, elapsed), file=sys.stderr)
        for r in results:
            status = "PASS" if r["pass"] else "FAIL"
            rate = "%d/%d" % (r["triggers"], r["runs"])
            print("  [%s] rate=%s expected=%s: %s" % (status, rate, r["should_trigger"], r["query"][:60]), file=sys.stderr)

    return {
        "skill": skill_name,
        "type": "trigger",
        "summary": {"total": total, "passed": passed, "failed": total - passed},
        "results": results,
        "elapsed_seconds": round(elapsed, 1),
    }


def run_functional_eval_for_skill(
    skill_name: str,
    model: str,
    output_dir: Path,
    timeout: int,
    verbose: bool,
) -> dict:
    """Run functional evals for a single skill using cursor-agent -p."""
    evals_file = EVALS_DIR / skill_name / "evals.json"
    skill_path = REPO_ROOT / skill_name

    if not evals_file.exists():
        return {"skill": skill_name, "error": "No evals.json found"}
    if not (skill_path / "SKILL.md").exists():
        return {"skill": skill_name, "error": f"No SKILL.md at {skill_path}"}

    eval_data = json.loads(evals_file.read_text())
    skill_md = (skill_path / "SKILL.md").read_text()

    skill_output_dir = output_dir / skill_name
    skill_output_dir.mkdir(parents=True, exist_ok=True)

    if verbose:
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"FUNCTIONAL EVAL: {skill_name}", file=sys.stderr)
        print(f"Test cases: {len(eval_data['evals'])}", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)

    eval_results = []
    for ev in eval_data["evals"]:
        eval_id = ev["id"]
        prompt = ev["prompt"]
        expectations = ev.get("expectations", [])

        if verbose:
            print(f"  Running eval {eval_id}: {prompt[:60]}...", file=sys.stderr)

        eval_dir = skill_output_dir / f"eval-{eval_id}"
        eval_dir.mkdir(parents=True, exist_ok=True)

        # Build prompt that includes skill content. Workspace is only eval_dir so the nested
        # agent cannot edit skill packages or other repo files (eval runs must not "fix" skills).
        full_prompt = (
            f"You have access to the following skill for reference. "
            f"Use its guidance to complete the task.\n\n"
            f"<skill>\n{skill_md}\n</skill>\n\n"
            f"Task: {prompt}\n\n"
            f"This workspace is an isolated eval scratch directory. "
            f"Put all new files under ./outputs/ (create it if needed). "
            f"Do not edit, create, or delete anything outside this directory.\n"
        )

        # Run cursor-agent -p with text output for readable response (--force: non-interactive edits).
        # --workspace is eval_dir (not REPO_ROOT) so only outputs/ here are writable, not */SKILL.md.
        m = model or DEFAULT_CURSOR_MODEL
        cmd = [
            CURSOR_AGENT_BIN,
            "-p",
            "--output-format",
            "text",
            "--force",
            "--trust",
            "--workspace",
            str(eval_dir),
            "--model",
            m,
            full_prompt,
        ]

        env = dict(os.environ)

        t0 = time.time()
        response_text = ""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(eval_dir),
                env=env,
            )
            elapsed = time.time() - t0
            success = result.returncode == 0

            response_text = result.stdout

            # Save full response
            (eval_dir / "response.md").write_text(response_text)
            if result.stderr:
                (eval_dir / "stderr.txt").write_text(result.stderr)

            # Include output files in grading context
            grading_text = response_text
            outputs_dir = eval_dir / "outputs"
            if outputs_dir.is_dir():
                for out_file in sorted(outputs_dir.iterdir()):
                    if out_file.is_file() and out_file.suffix in (
                        ".py", ".js", ".ts", ".jsx", ".tsx", ".sh", ".json", ".yaml", ".yml", ".md", ".txt",
                    ):
                        try:
                            content = out_file.read_text(errors="replace")
                            grading_text += f"\n\n--- {out_file.name} ---\n{content}"
                        except Exception:
                            pass

            # Grade against expectations
            grades = grade_expectations(grading_text, expectations)

            passed = sum(1 for g in grades if g["passed"])
            total = len(grades)

        except subprocess.TimeoutExpired:
            elapsed = time.time() - t0
            success = False
            response_text = "[TIMED OUT after %ds]" % timeout
            grades = [{"text": exp, "passed": False, "evidence": "Timed out"} for exp in expectations]
            passed = 0
            total = len(expectations)
        except Exception as exc:
            elapsed = time.time() - t0
            success = False
            err_msg = str(exc)
            response_text = "[ERROR: %s]" % err_msg
            grades = [{"text": exp, "passed": False, "evidence": err_msg} for exp in expectations]
            passed = 0
            total = len(expectations)

        eval_result = {
            "eval_id": eval_id,
            "prompt": prompt,
            "success": success,
            "passed": passed,
            "total": total,
            "pass_rate": round(passed / total, 2) if total > 0 else 0,
            "elapsed_seconds": round(elapsed, 1),
            "grades": grades,
            "response": response_text,
        }
        eval_results.append(eval_result)

        # Save grading
        (eval_dir / "grading.json").write_text(json.dumps(eval_result, indent=2))

        if verbose:
            print(f"    Result: {passed}/{total} expectations passed ({elapsed:.1f}s)", file=sys.stderr)
            for g in grades:
                status = "PASS" if g["passed"] else "FAIL"
                print(f"    [{status}] {g['text'][:70]}", file=sys.stderr)

    total_passed = sum(e["passed"] for e in eval_results)
    total_expectations = sum(e["total"] for e in eval_results)
    total_elapsed = sum(e["elapsed_seconds"] for e in eval_results)

    return {
        "skill": skill_name,
        "type": "functional",
        "summary": {
            "evals_run": len(eval_results),
            "total_passed": total_passed,
            "total_expectations": total_expectations,
            "pass_rate": round(total_passed / total_expectations, 2) if total_expectations > 0 else 0,
        },
        "results": eval_results,
        "elapsed_seconds": round(total_elapsed, 1),
    }


def grade_expectations(response_text, expectations):
    """Simple keyword/pattern grading of expectations against response text.

    For more rigorous grading, use the skill-creator's grader agent.
    """
    response_lower = response_text.lower()
    grades = []

    for expectation in expectations:
        passed, evidence = check_expectation(response_lower, response_text, expectation)
        grades.append({
            "text": expectation,
            "passed": passed,
            "evidence": evidence,
        })

    return grades


def extract_negative_terms(expectation: str) -> list[str]:
    """Extract quoted terms from generic NOT clauses like ``(NOT 'elevenlabs')``."""
    return [match[1] for match in re.findall(r"\bnot\b[^\"']*([\"'])(.+?)\1", expectation, flags=re.IGNORECASE)]


def find_forbidden_reference(response_text: str, term: str) -> str | None:
    """Detect an exact forbidden package reference in JS/package-manager contexts."""
    escaped = re.escape(term)
    patterns = [
        rf"(?im)^\s*import\s+(?:[\w*\s{{}},$]+\s+from\s+)?[\"']{escaped}[\"']\s*;?\s*$",
        rf"(?i)\brequire\(\s*[\"']{escaped}[\"']\s*\)",
        rf"(?i)\bimport\(\s*[\"']{escaped}[\"']\s*\)",
        rf"(?i)\b(?:npm\s+install|pnpm\s+add|yarn\s+add|bun\s+add)\s+{escaped}(?:\s|$)",
    ]

    for pattern in patterns:
        match = re.search(pattern, response_text)
        if match:
            return match.group(0)
    return None


def _contains_regex(response_text: str, pattern: str) -> bool:
    """Case-insensitive regex search helper."""
    return re.search(pattern, response_text, flags=re.IGNORECASE) is not None


def has_python_elevenlabs_import(response_text: str) -> bool:
    """Accept direct SDK imports from either supported Python module path."""
    return any(
        _contains_regex(response_text, pattern)
        for pattern in (
            r"\bfrom\s+elevenlabs\s+import\s+ElevenLabs\b",
            r"\bfrom\s+elevenlabs\.client\s+import\s+ElevenLabs\b",
        )
    )


def has_python_elevenlabs_constructor(response_text: str) -> bool:
    """Accept ElevenLabs() with or without constructor arguments."""
    return _contains_regex(response_text, r"\bElevenLabs\s*\(")


def has_js_elevenlabs_client_constructor(response_text: str) -> bool:
    """Accept JS SDK client construction with normal syntax."""
    return _contains_regex(response_text, r"\bnew\s+ElevenLabsClient\s*\(")


def has_dotted_call(response_text: str, dotted_name: str) -> bool:
    """Accept dotted method calls with optional whitespace before the call."""
    return _contains_regex(response_text, rf"\b{re.escape(dotted_name)}\s*\(")


def has_high_prompt_influence(response_text: str) -> tuple[bool, str]:
    """Detect a high prompt_influence value even when prose omits 'high adherence'."""
    values = [
        float(match)
        for match in re.findall(
            r"prompt_influence\s*[:=]\s*['\"]?([01](?:\.\d+)?)",
            response_text,
            flags=re.IGNORECASE,
        )
    ]
    if not values:
        return False, ""
    highest = max(values)
    if highest >= 0.7:
        return True, f"Found prompt_influence={highest:g}"
    return False, f"Found prompt_influence={highest:g}, below high-adherence threshold"


def mentions_sixty_second_duration(response_text: str) -> tuple[bool, str]:
    """Detect equivalent 60-second duration references."""
    patterns = {
        r"\b60000\b": "60000 ms",
        r"\b60(?:\.0+)?\s*seconds?\b": "60 seconds",
        r"\b60-?second\b": "60-second",
        r"\bone\s+minute\b": "one minute",
    }
    for pattern, label in patterns.items():
        if _contains_regex(response_text, pattern):
            return True, f"Found duration reference: {label}"
    return False, ""


def has_successful_agent_cli_setup(response_text: str) -> bool:
    """Accept successful CLI project creation/push wording without literal commands."""
    checks = [
        _contains_regex(response_text, r"\b(created|initialized)\b.*\b(cli project|agent project)\b"),
        _contains_regex(response_text, r"\b(create|created|used it to create)\b.*\bvoice agent\b"),
        _contains_regex(response_text, r"\b(push|pushed|deploy|deployed)\b.*\b(agent|tool|tools)\b"),
    ]
    return sum(checks) >= 2


def has_verified_api_key_wording(response_text: str) -> bool:
    """Accept prose that clearly says the API key was validated against ElevenLabs."""
    return (
        _contains_regex(response_text, r"\b(verif(?:y|ied)|validat(?:e|ed)|checked)\b")
        and _contains_regex(response_text, r"\b(api key|elevenlabs_api_key|key)\b")
        and (
            _contains_regex(response_text, r"\b(api\.elevenlabs|/v1/user)\b")
            or _contains_regex(response_text, r"\bagainst\s+elevenlabs\b")
            or _contains_regex(response_text, r"\breturned\s+200\b")
        )
    )


def has_cli_agent_project_artifacts(response_text: str) -> bool:
    """Detect nested CLI project artifacts captured from outputs/."""
    has_agent_config = _contains_regex(
        response_text,
        r"(?:(?:^|\n)---\s+(?:.*/)?(?:agent_configs?/.*\.json|agents?\.json)\s+---|outputs?/.*(?:agent_configs?/.*\.json|agents?\.json))",
    )
    has_tool_config = _contains_regex(
        response_text,
        r"(?:(?:^|\n)---\s+(?:.*/)?(?:tool_configs?/.*\.json|tools?\.json)\s+---|outputs?/.*(?:tool_configs?/.*\.json|tools?\.json))",
    )
    has_readme = _contains_regex(
        response_text,
        r"(?:(?:^|\n)---\s+(?:.*/)?readme\.md\s+---|outputs?/.*readme\.md)",
    )
    return has_agent_config and has_tool_config and has_readme


def build_grading_text(response_text: str, outputs_dir: Path) -> str:
    """Append generated output files recursively for grading context."""
    grading_text = response_text
    if not outputs_dir.is_dir():
        return grading_text

    allowed_suffixes = {
        ".py", ".js", ".mjs", ".cjs", ".ts", ".jsx", ".tsx", ".sh",
        ".json", ".yaml", ".yml", ".md", ".txt",
    }
    for out_file in sorted(p for p in outputs_dir.rglob("*") if p.is_file()):
        if out_file.suffix not in allowed_suffixes:
            continue
        try:
            content = out_file.read_text(errors="replace")
            rel_path = out_file.relative_to(outputs_dir)
            grading_text += f"\n\n--- {rel_path} ---\n{content}"
        except Exception:
            pass
    return grading_text


def _pattern_present(matcher, response_text: str, response_lower: str) -> bool:
    """Evaluate a string or callable matcher against the grading text."""
    if callable(matcher):
        return matcher(response_text)
    return matcher in response_lower


def check_expectation(response_lower, response_text, expectation):
    """Check a single expectation against the response. Returns (passed, evidence)."""
    exp_lower = expectation.lower()

    # Negative deprecation checks must run before generic "from elevenlabs import" pattern
    # matching; otherwise expectations that quote the forbidden import pass incorrectly.
    if "not" in exp_lower and ("deprecated" in exp_lower or "do not use" in exp_lower):
        deprecated_patterns = [
            "from elevenlabs import generate",
            "from elevenlabs import voices",
            'require("elevenlabs")',
            "npm install elevenlabs",
        ]
        found_deprecated = [p for p in deprecated_patterns if p in response_lower]
        if found_deprecated:
            return False, "Found deprecated pattern: %s" % found_deprecated[0]
        return True, "No deprecated patterns found"

    negative_terms = extract_negative_terms(expectation)
    for term in negative_terms:
        forbidden_match = find_forbidden_reference(response_text, term)
        if forbidden_match:
            return False, "Found forbidden reference: %s" % forbidden_match

    # Direct pattern checks — look for specific API patterns in the response
    pattern_checks = [
        # SDK imports (specifically `from elevenlabs import ElevenLabs`)
        ("from elevenlabs import elevenlabs", has_python_elevenlabs_import, "elevenlabs import"),
        ("elevenlabs()", has_python_elevenlabs_constructor, "client constructor"),
        ("elevenlabsclient", has_js_elevenlabs_client_constructor, "JS client constructor"),
        # API methods
        ("text_to_speech.convert", lambda text: has_dotted_call(text, "text_to_speech.convert"), "TTS convert"),
        ("texttospeech.convert", lambda text: has_dotted_call(text, "textToSpeech.convert"), "JS TTS convert"),
        ("speech_to_text.convert", lambda text: has_dotted_call(text, "speech_to_text.convert"), "STT convert"),
        ("speechtotext.convert", lambda text: has_dotted_call(text, "speechToText.convert"), "JS STT convert"),
        ("text_to_sound_effects.convert", lambda text: has_dotted_call(text, "text_to_sound_effects.convert"), "SFX convert"),
        ("music.compose", lambda text: has_dotted_call(text, "music.compose"), "music compose"),
        # Parameters
        ("model_id", "model_id", "model_id param"),
        ("modelid", "modelid", "JS modelId param"),
        ("voice_id", "voice_id", "voice_id param"),
        ("scribe_v2", "scribe_v2", "scribe_v2 model"),
        ("multilingual", "multilingual", "multilingual model"),
        ("music_length_ms", "music_length_ms", "music duration"),
        ("diariz", "diariz", "diarization"),
        # JS SDK
        ("@elevenlabs/elevenlabs-js", "@elevenlabs/elevenlabs-js", "JS SDK package"),
        ("@elevenlabs/", "@elevenlabs/", "JS SDK package"),
        # Agents
        ("elevenlabs agents", lambda text: "elevenlabs agents" in text.lower() or has_successful_agent_cli_setup(text), "CLI agents command"),
        ("convai", "convai", "ConvAI widget"),
        ("agent-id", "agent-id", "agent-id attribute"),
        ("agent_id", "agent_id", "agent_id attribute"),
        ("webhook", "webhook", "webhook tool"),
        # API key
        ("elevenlabs_api_key", "elevenlabs_api_key", "API key env var"),
    ]

    matched_pattern_checks = []
    seen_pattern_labels = set()
    for trigger, search, label in pattern_checks:
        if trigger in exp_lower and label not in seen_pattern_labels:
            matched_pattern_checks.append((search, label))
            seen_pattern_labels.add(label)

    pattern_check_passed = None
    pattern_check_evidence = ""
    if matched_pattern_checks:
        missing_patterns = [
            label for matcher, label in matched_pattern_checks
            if not _pattern_present(matcher, response_text, response_lower)
        ]
        if missing_patterns:
            pattern_check_passed = False
            pattern_check_evidence = "Missing pattern(s): %s" % ", ".join(missing_patterns)
        else:
            pattern_check_passed = True
            pattern_check_evidence = "Found pattern(s): %s" % ", ".join(label for _, label in matched_pattern_checks)

    if "prompt_influence" in exp_lower and "high adherence" in exp_lower:
        prompt_match, prompt_evidence = has_high_prompt_influence(response_text)
        return prompt_match, prompt_evidence or "Missing prompt_influence evidence"

    if "60000ms" in exp_lower or "60 seconds" in exp_lower:
        duration_match, duration_evidence = mentions_sixty_second_duration(response_text)
        if duration_match:
            return True, duration_evidence

    if (
        "agent configuration" in exp_lower
        and "tool configuration" in exp_lower
        and "outputs" in exp_lower
    ):
        artifact_match = has_cli_agent_project_artifacts(response_text)
        if artifact_match:
            return True, "Found nested CLI agent project artifacts in outputs/"
        return False, "Missing CLI agent project artifacts in outputs/"

    if "agent project under outputs" in exp_lower:
        artifact_match = has_cli_agent_project_artifacts(response_text)
        if artifact_match:
            return True, "Found CLI-ready agent project artifacts in outputs/"
        return False, "Missing CLI-ready agent project artifacts in outputs/"

    if "init/add/push" in exp_lower and "readme" in exp_lower:
        has_commands = (
            _contains_regex(response_text, r"\belevenlabs\s+agents\s+init\b")
            and _contains_regex(response_text, r"\belevenlabs\s+agents\s+add\b")
            and _contains_regex(response_text, r"\belevenlabs\s+agents\s+push\b")
        )
        if has_commands:
            return True, "Found README-style init/add/push command sequence"
        return False, "Missing README-style init/add/push command sequence"

    if "readme" in exp_lower and "elevenlabs agents push" in exp_lower:
        command_match = _contains_regex(response_text, r"\belevenlabs\s+agents\s+push\b")
        if command_match:
            return True, "Found CLI push command in generated instructions"
        return False, "Missing CLI push command in generated instructions"

    if "/v1/user" in exp_lower or ("validate" in exp_lower and "user endpoint" in exp_lower):
        validation_match = has_verified_api_key_wording(response_text)
        if validation_match:
            return True, "Found explicit API-key validation wording"

    # Semantic checks for natural language expectations
    semantic_checks = [
        # Streaming
        (["streaming", "stream"], ["stream", "chunk", "generator", "yield", "async", "iter"], {"generator", "yield", "async", "iter"}),
        # File operations
        (["saves", "output", "file", "writes"], ["open(", "write", "save", ".mp3", ".wav", ".mp4"], {"open(", "save", ".mp3", ".wav", ".mp4"}),
        # Audio processing
        (["audio", "chunk"], ["chunk", "audio", "byte", "stream", "iter"], {"chunk", "byte", "iter"}),
        # Real-time / playback
        (["play", "real-time", "realtime"], ["play", "stream", "chunk", "audio", "realtime", "real-time"], {"realtime", "real-time"}),
        # Dashboard / instructions
        (["dashboard", "instructions"], ["dashboard", "elevenlabs.io", "settings", "profile", "api key", "navigate"], {"elevenlabs.io", "api key"}),
        # Validation / test API
        (["validate", "test", "api call"], ["validate", "verify", "test", "curl", "request", "/v1/user", "api.elevenlabs"], {"curl", "/v1/user", "api.elevenlabs"}),
        # Causes / suggestions / debugging
        (["suggests", "causes", "expired", "debug"], ["expired", "invalid", "wrong", "rotate", "regenerate", "check", "verify", "troubleshoot", "common"], {"expired", "invalid", "regenerate", "troubleshoot"}),
        # Steps / getting new key
        (["steps", "new key", "get a new"], ["step", "new key", "generate", "create", "regenerate", "dashboard", "replace"], {"new key", "regenerate", "replace"}),
        # System prompt
        (["system prompt"], ["system", "prompt", "instruction", "persona", "role"], {"persona", "role"}),
        # Tool / booking / availability
        (["tool", "checking", "booking", "availability"], ["tool", "function", "action", "book", "reserv", "avail", "check"], {"reserv", "avail"}),
        # Speaker labels / diarization
        (["speaker", "speaker label", "who said what", "diariz"], ["speaker", "speaker_id", "speaker:", "speaker label", "speaker_label", "diariz", "segment", "utterance"], {"speaker", "speaker_id", "speaker:", "speaker label", "speaker_label", "diariz"}),
        # Instruments / musical
        (["instrument", "musical"], ["instrument", "piano", "guitar", "drum", "bass", "string", "synth", "musical"], {"piano", "guitar", "drum", "bass", "string", "synth"}),
        # Timestamps / processing
        (["timestamp", "timestamped", "word-level"], ["timestamp", "word", "time", "start", "end", "display", "print", "output", "format"], {"timestamp", "start", "end", "format"}),
        # Lyrics / composition
        (["lyrics", "coding", "programming"], ["lyrics", "lyric", "coding", "code", "program", "develop", "debug"], {"lyrics", "lyric", "coding", "program", "develop", "debug"}),
    ]

    semantic_check_applied = False
    semantic_check_evidence = ""
    semantic_check_passed = False
    for triggers, indicators, strong_indicators in semantic_checks:
        if any(t in exp_lower for t in triggers):
            semantic_check_applied = True
            found = [ind for ind in indicators if ind in response_lower]
            if len(found) >= 2:
                semantic_check_passed = True
                semantic_check_evidence = "Semantic match: %s" % ", ".join(found[:4])
                break
            if len(found) == 1 and found[0] in strong_indicators:
                semantic_check_passed = True
                semantic_check_evidence = "Strong semantic match: %s" % found[0]
                break
            if not semantic_check_evidence:
                semantic_check_evidence = "Missing semantic indicators: %s" % ", ".join(indicators[:4])

    if matched_pattern_checks and semantic_check_applied:
        if not pattern_check_passed:
            return False, pattern_check_evidence
        if not semantic_check_passed:
            return False, semantic_check_evidence
        return True, "%s; %s" % (pattern_check_evidence, semantic_check_evidence)

    if matched_pattern_checks:
        return pattern_check_passed, pattern_check_evidence

    if semantic_check_applied:
        return semantic_check_passed, semantic_check_evidence

    # Fallback: extract key terms and check presence (relaxed threshold)
    stop_words = {
        "uses", "with", "that", "this", "from", "have", "should", "must",
        "includes", "contains", "provides", "shows", "calls", "creates",
        "writes", "saves", "outputs", "handles", "defines", "sets",
        "parameter", "appropriate", "correct", "proper", "working", "valid",
        "using", "when", "does", "like", "also", "into", "some", "such",
        "each", "make", "need", "them", "their", "will", "been", "more",
        "very", "just", "only", "than", "other", "about", "over", "most",
        "equivalent", "similar", "least",
    }
    key_terms = [w for w in exp_lower.split() if len(w) > 3 and w not in stop_words]

    if key_terms:
        matches = sum(1 for t in key_terms if t in response_lower)
        ratio = matches / len(key_terms) if key_terms else 0
        # Relaxed: 35% match threshold instead of 50%
        if ratio >= 0.35:
            matched = [t for t in key_terms if t in response_lower]
            return True, "Found %d/%d key terms: %s" % (matches, len(key_terms), ", ".join(matched[:5]))
        else:
            missing = [t for t in key_terms if t not in response_lower]
            return False, "Missing key terms: %s" % ", ".join(missing[:5])

    if negative_terms:
        return True, "Forbidden references absent: %s" % ", ".join(negative_terms)

    return False, "Could not verify expectation"


def generate_report(trigger_results, functional_results, output_dir, skills):
    """Generate a markdown summary report."""
    lines = ["# Skills Evaluation Report", ""]
    lines.append(f"**Date:** {time.strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Output:** `{output_dir}`")
    lines.append("")

    # Overall summary
    lines.append("## Summary")
    lines.append("")
    lines.append("| Skill | Trigger | Functional |")
    lines.append("|-------|---------|------------|")

    trigger_by_skill = {r["skill"]: r for r in trigger_results}
    func_by_skill = {r["skill"]: r for r in functional_results}

    for skill in skills:
        tr = trigger_by_skill.get(skill, {})
        fr = func_by_skill.get(skill, {})

        if "error" in tr:
            trigger_str = f"error"
        elif "summary" in tr:
            s = tr["summary"]
            trigger_str = f"{s['passed']}/{s['total']}"
        else:
            trigger_str = "-"

        if "error" in fr:
            func_str = "error"
        elif "summary" in fr:
            s = fr["summary"]
            func_str = f"{s['total_passed']}/{s['total_expectations']}"
        else:
            func_str = "-"

        lines.append(f"| {skill} | {trigger_str} | {func_str} |")

    lines.append("")

    # Trigger details
    if trigger_results:
        lines.append("## Trigger Evaluation Details")
        lines.append("")
        for r in trigger_results:
            if "error" in r:
                lines.append(f"### {r['skill']}: ERROR - {r['error']}")
                continue
            s = r["summary"]
            lines.append(f"### {r['skill']} ({s['passed']}/{s['total']} passed, {r['elapsed_seconds']}s)")
            lines.append("")
            failures = [res for res in r["results"] if not res["pass"]]
            if failures:
                lines.append("**Failures:**")
                for f in failures:
                    rate = f"{f['triggers']}/{f['runs']}"
                    expected = "trigger" if f["should_trigger"] else "not trigger"
                    lines.append(f"- rate={rate} (expected {expected}): {f['query'][:80]}")
                lines.append("")
            else:
                lines.append("All queries passed.")
                lines.append("")

    # Functional details
    if functional_results:
        lines.append("## Functional Evaluation Details")
        lines.append("")
        for r in functional_results:
            if "error" in r:
                lines.append(f"### {r['skill']}: ERROR - {r['error']}")
                continue
            s = r["summary"]
            lines.append(f"### {r['skill']} ({s['total_passed']}/{s['total_expectations']} passed, {r['elapsed_seconds']}s)")
            lines.append("")
            for ev in r["results"]:
                lines.append(f"#### Eval {ev['eval_id']} ({ev['passed']}/{ev['total']})")
                lines.append("")
                lines.append(f"**Prompt:** {ev['prompt']}")
                lines.append("")

                # Expectations
                lines.append("**Expectations:**")
                for g in ev["grades"]:
                    status = "PASS" if g["passed"] else "FAIL"
                    lines.append(f"- [{status}] {g['text']} — {g['evidence']}")
                lines.append("")

                # Generated response
                response = ev.get("response", "")
                if response:
                    lines.append("<details>")
                    lines.append(f"<summary>Generated Response ({len(response)} chars)</summary>")
                    lines.append("")
                    lines.append(response)
                    lines.append("")
                    lines.append("</details>")
                    lines.append("")

    return "\n".join(lines)


def main():
    _ensure_cursor_agent_available()
    parser = argparse.ArgumentParser(description="Run evaluations across all ElevenLabs skills")
    parser.add_argument("--skills", nargs="*", default=ALL_SKILLS, help="Skills to evaluate (default: all)")
    parser.add_argument("--trigger-only", action="store_true", help="Run trigger evals only")
    parser.add_argument("--functional-only", action="store_true", help="Run functional evals only")
    parser.add_argument(
        "--model",
        default=DEFAULT_CURSOR_MODEL,
        help="Model for cursor-agent (default: %(default)s; see `cursor-agent --list-models`)",
    )
    parser.add_argument("--workers", type=int, default=8, help="Parallel workers for trigger evals")
    parser.add_argument("--runs-per-query", type=int, default=3, help="Runs per trigger query")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout per functional eval (seconds)")
    parser.add_argument("--trigger-timeout", type=int, default=45, help="Timeout per trigger query (seconds)")
    parser.add_argument("--output-dir", default=None, help="Output directory (default: evals/results/<timestamp>)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if args.trigger_only and args.functional_only:
        parser.error("cannot combine --trigger-only and --functional-only")

    run_trigger = not args.functional_only
    run_functional = not args.trigger_only

    # Set up output directory
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    if args.output_dir:
        # Honor user-specified directory and allow reuse
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        # Create a unique default directory to avoid mixing results from concurrent runs
        base_results_dir = EVALS_DIR / "results"
        for _ in range(5):
            unique_suffix = uuid.uuid4().hex[:8]
            output_dir = base_results_dir / f"{timestamp}_{unique_suffix}"
            try:
                output_dir.mkdir(parents=True, exist_ok=False)
                break
            except FileExistsError:
                # Extremely unlikely; retry with a new suffix
                continue
        else:
            # If we somehow failed repeatedly, let the exception surface
            output_dir.mkdir(parents=True, exist_ok=False)

    print(f"Skills Evaluation", file=sys.stderr)
    print(f"  Skills: {', '.join(args.skills)}", file=sys.stderr)
    print(f"  Trigger evals: {'yes' if run_trigger else 'no'}", file=sys.stderr)
    print(f"  Functional evals: {'yes' if run_functional else 'no'}", file=sys.stderr)
    print(f"  Output: {output_dir}", file=sys.stderr)
    print(f"  Model: {args.model}", file=sys.stderr)
    print("", file=sys.stderr)

    trigger_results = []
    functional_results = []

    # Run trigger evals
    if run_trigger:
        print("Running trigger evaluations...", file=sys.stderr)
        for skill in args.skills:
            result = run_trigger_eval_for_skill(
                skill_name=skill,
                model=args.model,
                workers=args.workers,
                runs_per_query=args.runs_per_query,
                timeout=args.trigger_timeout,
                verbose=args.verbose,
            )
            trigger_results.append(result)

    # Run functional evals
    if run_functional:
        print("\nRunning functional evaluations...", file=sys.stderr)
        for skill in args.skills:
            result = run_functional_eval_for_skill(
                skill_name=skill,
                model=args.model,
                output_dir=output_dir,
                timeout=args.timeout,
                verbose=args.verbose,
            )
            functional_results.append(result)

    # Generate report
    report = generate_report(trigger_results, functional_results, output_dir, args.skills)
    report_path = output_dir / "report.md"
    report_path.write_text(report)

    # Save raw results
    all_results = {
        "timestamp": timestamp,
        "skills": args.skills,
        "trigger_results": trigger_results,
        "functional_results": functional_results,
    }
    (output_dir / "results.json").write_text(json.dumps(all_results, indent=2))

    # Print report
    print("\n" + report)
    print(f"\nResults saved to: {output_dir}", file=sys.stderr)


if __name__ == "__main__":
    main()
