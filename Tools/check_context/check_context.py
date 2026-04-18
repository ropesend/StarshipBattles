"""Estimate current Claude Code session context usage.

Reads the most recently modified JSONL transcript under
`~/.claude/projects/<cwd-slug>/`, sums the character length of message content,
estimates tokens as chars/4, and compares against the threshold in
`Projects/protocols/context_config.md`.

Exit codes:
    0 - CONTINUE (below threshold)
    1 - STOP (at or above threshold)
    2 - UNKNOWN (transcript not found)

Run from the repo root:
    python Projects/scripts/check_context.py
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

CHARS_PER_TOKEN = 4  # standard rough ratio for English text + code
CONFIG_PATH = Path(__file__).resolve().parents[1] / "protocols" / "context_config.md"


def _cwd_slug() -> str:
    """Claude Code's transcript dir slug: cwd with drive colon and separators
    replaced by '-'. E.g. 'c:\\Dev\\Starship Battles' -> 'c--Dev-Starship-Battles'."""
    cwd = os.getcwd()
    slug = cwd.replace(":", "-").replace("\\", "-").replace("/", "-").replace(" ", "-")
    return slug


def _transcript_dir() -> Path:
    home = Path(os.path.expanduser("~"))
    return home / ".claude" / "projects" / _cwd_slug()


def _latest_transcript(transcript_dir: Path) -> Path | None:
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


def _content_chars(content) -> int:
    """Recursively count characters in a message's content field.

    The JSONL uses a mix of string content and list-of-blocks (text, tool_use,
    tool_result). Count everything — it all lands in the context window."""
    if content is None:
        return 0
    if isinstance(content, str):
        return len(content)
    if isinstance(content, list):
        return sum(_content_chars(item) for item in content)
    if isinstance(content, dict):
        total = 0
        for key, value in content.items():
            if key in ("type", "id", "name"):
                total += len(str(value)) if value is not None else 0
            else:
                total += _content_chars(value)
        return total
    return len(str(content))


def _count_transcript_chars(path: Path) -> int:
    total = 0
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            message = record.get("message")
            if isinstance(message, dict):
                total += _content_chars(message.get("content"))
            elif "content" in record:
                total += _content_chars(record.get("content"))
    return total


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
        print(f"Verdict: UNKNOWN")
        return 2

    chars = _count_transcript_chars(transcript)
    tokens = chars // CHARS_PER_TOKEN
    pct = (tokens / window) * 100 if window else 0.0
    verdict = "STOP" if pct >= threshold_pct else "CONTINUE"

    print(f"Session: {transcript.stem}")
    print(f"Tokens used (est): {tokens:,} / {window:,} ({pct:.1f}%)")
    print(f"Threshold: {threshold_pct:.1f}%")
    print(f"Verdict: {verdict}")
    return 1 if verdict == "STOP" else 0


if __name__ == "__main__":
    sys.exit(main())
