from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from Tools.agent_coordination import claude_skill_usage_hook as hook


def _payload(**fields: object) -> dict[str, object]:
    return dict(fields)


def test_extract_skill_name_from_user_prompt_expansion() -> None:
    name = hook._extract_skill_name(_payload(
        hook_event_name="UserPromptExpansion",
        command_name="claude-proj-start",
        expansion_type="slash_command",
    ))
    assert name == "claude-proj-start"


def test_extract_skill_name_from_pretooluse_skill() -> None:
    name = hook._extract_skill_name(_payload(
        hook_event_name="PreToolUse",
        tool_name="Skill",
        tool_input={"skill": "claude-ticket-work"},
    ))
    assert name == "claude-ticket-work"


def test_extract_skill_name_from_pretooluse_alt_keys() -> None:
    # Some Claude Code versions may emit `skill_name` or `name` rather than `skill`.
    a = hook._extract_skill_name(_payload(
        tool_name="Skill", tool_input={"skill_name": "claude-foo"},
    ))
    b = hook._extract_skill_name(_payload(
        tool_name="Skill", tool_input={"name": "claude-bar"},
    ))
    assert a == "claude-foo"
    assert b == "claude-bar"


def test_extract_returns_none_for_non_skill_tool_use() -> None:
    name = hook._extract_skill_name(_payload(
        hook_event_name="PreToolUse",
        tool_name="Bash",
        tool_input={"command": "ls"},
    ))
    assert name is None


def test_extract_returns_none_for_empty_payload() -> None:
    assert hook._extract_skill_name({}) is None


def test_main_no_op_for_non_claude_prefix(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps({"command_name": "ocode-audit-shrink"})))
    rc = hook.main()
    assert rc == 0
    # No subprocess called means no by_install file.
    assert not (tmp_path / "AgentCoordination" / "generated" / "skill_usage" / "by_install").exists()


def test_main_no_op_for_invalid_skill_name(monkeypatch) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps({"command_name": "INVALID NAME"})))
    rc = hook.main()
    assert rc == 0


def test_main_no_op_for_empty_stdin(monkeypatch) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO(""))
    rc = hook.main()
    assert rc == 0


def test_main_no_op_for_malformed_json(monkeypatch) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("{not valid"))
    rc = hook.main()
    assert rc == 0


def test_main_invokes_log_skill_usage_for_claude_skill(
    monkeypatch, tmp_path: Path
) -> None:
    # Build a fake repo containing AGENTS.md and the log script (just the
    # presence of the path is checked; the subprocess call itself is captured).
    (tmp_path / "AGENTS.md").write_text("# AGENTS", encoding="utf-8")
    log_script_dir = tmp_path / "Tools" / "agent_coordination"
    log_script_dir.mkdir(parents=True)
    (log_script_dir / "log_skill_usage.py").write_text("# stub\n", encoding="utf-8")

    captured: list[list[str]] = []

    def fake_run(cmd, **kwargs):  # type: ignore[no-untyped-def]
        captured.append(list(cmd))

        class _Result:
            returncode = 0
            stdout = b""
            stderr = b""

        return _Result()

    monkeypatch.setattr(hook, "_resolve_repo_root", lambda: tmp_path)
    monkeypatch.setattr(hook.subprocess, "run", fake_run)
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps({"command_name": "claude-proj-start"})))

    rc = hook.main()
    assert rc == 0
    assert captured, "Expected log_skill_usage.py to be invoked"
    invocation = captured[0]
    assert "log_skill_usage.py" in invocation[1]
    assert invocation[invocation.index("--agent") + 1] == "claude"
    assert invocation[invocation.index("--skill") + 1] == "claude-proj-start"
