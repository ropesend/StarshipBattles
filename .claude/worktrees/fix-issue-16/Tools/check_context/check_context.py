"""Check current Claude Code session context usage.

Reads the most recently modified JSONL transcript under
`~/.claude/projects/<cwd-slug>/`, finds the last `assistant` record,
and uses Anthropic's `usage` object as ground truth for how many input
tokens that turn processed — i.e., the true context window occupancy.

No estimation. The `usage` block on every assistant record is what
Anthropic's API reports, which includes the system prompt, tool schemas
(loaded + deferred), memory files, skills, and all message history
together — all of it.

Exit codes:
    0 - CONTINUE (below threshold)
    1 - STOP (at or above threshold)
    2 - UNKNOWN (transcript not found, or no assistant turns yet)

Run from the repo root:
    python Tools/check_context/check_context.py

Also wired as a `Stop` hook in `.claude/settings.json` — runs
automatically when the assistant finishes a response and surfaces the
output before the next user prompt.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

CONFIG_PATH = (
    Path(__file__).resolve().parents[2] / "Projects" / "protocols" / "context_config.md"
)


def _cwd_slug() -> str:
    """Claude Code's transcript dir slug: cwd with drive colon and separators
    replaced by '-'. E.g. 'c:\\Dev\\Starship Battles' -> 'c--Dev-Starship-Battles'."""
    cwd = os.getcwd()
    slug = cwd.replace(":", "-").replace("\\", "-").replace("/", "-").replace(" ", "-")
    return slug


def _transcript_dir() -> Path:
    home = Path(os.path.expanduser("~"))
    return home / ".claude" / "projects" / _cwd_slug()


def _latest_transcript(transcript_dir: Path) -> Optional[Path]:
    if not transcript_dir.is_dir():
        return None
    jsonls = list(transcript_dir.glob("*.jsonl"))
    if not jsonls:
        return None
    return max(jsonls, key=lambda p: p.stat().st_mtime)


def _load_config() -> tuple[int, float]:
    text = CONFIG_PATH.read_text(encoding="utf-8")
    window_match = re.search(r"CONTEXT_WINDOW_TOKENS[^\d]*(\d+)", text)
    pct_match = re.search(r"STOP_THRESHOLD_PERCENT[^\d]*(\d+(?:\.\d+)?)", text)
    if not window_match or not pct_match:
        raise RuntimeError(f"Could not parse settings from {CONFIG_PATH}")
    return int(window_match.group(1)), float(pct_match.group(1))


def _last_assistant_usage(path: Path) -> Optional[dict]:
    """Walk the JSONL in reverse and return the `usage` dict from the most
    recent assistant record. Returns None if no assistant turn has
    happened yet in this session."""
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("type") != "assistant":
            continue
        message = record.get("message")
        if not isinstance(message, dict):
            continue
        usage = message.get("usage")
        if isinstance(usage, dict):
            return usage
    return None


def _total_input_tokens(usage: dict) -> int:
    """Sum the three input-side token counters that together equal the
    context window occupancy Claude processed for a given turn."""
    return (
        int(usage.get("input_tokens", 0))
        + int(usage.get("cache_creation_input_tokens", 0))
        + int(usage.get("cache_read_input_tokens", 0))
    )


def main() -> int:
    try:
        window, threshold_pct = _load_config()
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 2

    transcript_dir = _transcript_dir()
    transcript = _latest_transcript(transcript_dir)
    if transcript is None:
        print(f"Session: UNKNOWN (no transcript found under {transcript_dir})")
        print("Verdict: UNKNOWN")
        return 2

    usage = _last_assistant_usage(transcript)
    if usage is None:
        print(f"Session: {transcript.stem}")
        print("Tokens used: UNKNOWN (no assistant turns yet this session)")
        print("Note: fresh sessions carry ~40-70k of baseline overhead")
        print("      (system prompt + tool schemas + memory) before any")
        print("      message content. Treat as safe to continue.")
        print(f"Threshold: {threshold_pct:.1f}%")
        print("Verdict: UNKNOWN")
        return 2

    tokens = _total_input_tokens(usage)
    pct = (tokens / window) * 100 if window else 0.0
    verdict = "STOP" if pct >= threshold_pct else "CONTINUE"

    fresh = int(usage.get("input_tokens", 0))
    cache_created = int(usage.get("cache_creation_input_tokens", 0))
    cache_read = int(usage.get("cache_read_input_tokens", 0))

    print(f"Session: {transcript.stem}")
    print(f"Tokens used: {tokens:,} / {window:,} ({pct:.1f}%)")
    print(f"  cache_read:    {cache_read:>10,}")
    print(f"  cache_created: {cache_created:>10,}")
    print(f"  fresh_input:   {fresh:>10,}")
    print(f"Threshold: {threshold_pct:.1f}%")
    print(f"Verdict: {verdict}")
    return 1 if verdict == "STOP" else 0


if __name__ == "__main__":
    sys.exit(main())
