"""Tests for Tools/agent_coordination/partner_invoke.py.

The module wraps cross-agent CLI invocation (codex/claude/opencode) per the
harmonized contract in plans/consult_harmonization_r002.md. Tests cover:
- per-partner argv construction (build_command)
- binary discovery (resolve_binary)
- sync invocation: ok, nonzero-exit, timeout, missing-binary, partner-completed
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
TOOLS_DIR = REPO_ROOT / "Tools" / "agent_coordination"

if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import partner_invoke  # noqa: E402


# ---------- build_command ----------


def test_build_command_opencode_includes_dir_and_skip_permissions(tmp_path: Path) -> None:
    cmd = partner_invoke.build_command(
        "opencode",
        binary="opencode",
        prompt="hello",
        repo_root=tmp_path,
    )
    assert cmd[0] == "opencode"
    assert cmd[1] == "run"
    assert "--dangerously-skip-permissions" in cmd
    assert "--dir" in cmd
    assert str(tmp_path) in cmd
    assert "--format" in cmd and "json" in cmd
    assert cmd[-1] == "hello"


def test_build_command_codex_includes_sandbox_and_output_last_message(tmp_path: Path) -> None:
    response_file = tmp_path / "response.md"
    cmd = partner_invoke.build_command(
        "codex",
        binary="codex",
        prompt="please advise",
        repo_root=tmp_path,
        response_file=response_file,
        sandbox="read-only",
    )
    assert cmd[0] == "codex"
    assert cmd[1] == "exec"
    assert "-C" in cmd and str(tmp_path) in cmd
    # codex exec 0.130.x has no --ask-for-approval; non-interactive by default.
    assert "--ask-for-approval" not in cmd
    assert "--sandbox" in cmd and "read-only" in cmd
    assert "--skip-git-repo-check" in cmd
    # --output-last-message must NOT point at response_file itself — codex
    # writes that file via apply_patch and --output-last-message would
    # overwrite it with the final chat message (regression 2026-05-12).
    assert "--output-last-message" in cmd
    assert str(response_file) not in cmd
    expected_last_message = response_file.with_name("last_message.txt")
    assert str(expected_last_message) in cmd
    # --add-dir must point at the response file's parent (consult leaf)
    assert "--add-dir" in cmd
    assert str(response_file.parent) in cmd
    assert cmd[-1] == "please advise"


def test_build_command_codex_workspace_write_when_requested(tmp_path: Path) -> None:
    cmd = partner_invoke.build_command(
        "codex",
        binary="codex",
        prompt="x",
        repo_root=tmp_path,
        sandbox="workspace-write",
    )
    assert "workspace-write" in cmd


def test_build_command_claude_uses_print_flag_and_no_session(tmp_path: Path) -> None:
    cmd = partner_invoke.build_command(
        "claude",
        binary="claude",
        prompt="please review",
        repo_root=tmp_path,
    )
    assert cmd[0] == "claude"
    assert "-p" in cmd or "--print" in cmd
    assert "--no-session-persistence" in cmd
    assert "--permission-mode" in cmd
    assert cmd[-1] == "please review"


def test_build_command_gemini_uses_plan_mode_and_default_model(tmp_path: Path) -> None:
    cmd = partner_invoke.build_command(
        "gemini",
        binary="gemini",
        prompt="please advise",
        repo_root=tmp_path,
    )
    assert cmd[0] == "gemini"
    assert "-p" in cmd
    # gemini's -p is string-valued: the prompt MUST be the next arg.
    p_idx = cmd.index("-p")
    assert cmd[p_idx + 1] == "please advise"
    assert "--approval-mode" in cmd and "plan" in cmd
    assert "--skip-trust" in cmd
    assert "--output-format" in cmd and "json" in cmd
    # Default model when none provided.
    assert "-m" in cmd or "--model" in cmd
    assert "gemini-3.1-pro-preview" in cmd


def test_build_command_gemini_includes_unique_session_id(tmp_path: Path) -> None:
    """Each gemini build_command call must produce a fresh --session-id <uuid>
    to prevent cross-invocation session contamination (r003 Change D)."""
    cmd1 = partner_invoke.build_command(
        "gemini", binary="gemini", prompt="x", repo_root=tmp_path,
    )
    cmd2 = partner_invoke.build_command(
        "gemini", binary="gemini", prompt="x", repo_root=tmp_path,
    )
    assert "--session-id" in cmd1
    assert "--session-id" in cmd2
    sid1 = cmd1[cmd1.index("--session-id") + 1]
    sid2 = cmd2[cmd2.index("--session-id") + 1]
    # uuid4 string form is 36 chars with hyphens at fixed positions.
    assert len(sid1) == 36 and sid1.count("-") == 4
    assert len(sid2) == 36 and sid2.count("-") == 4
    assert sid1 != sid2  # distinct ids per invocation


def test_build_command_gemini_uses_provided_model_override(tmp_path: Path) -> None:
    cmd = partner_invoke.build_command(
        "gemini",
        binary="gemini",
        prompt="x",
        repo_root=tmp_path,
        model="gemini-foo-test",
    )
    assert "gemini-foo-test" in cmd
    assert "gemini-3.1-pro-preview" not in cmd


def test_build_command_unknown_partner_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        partner_invoke.build_command(
            "unknown_agent",  # type: ignore[arg-type]
            binary="unknown_agent",
            prompt="x",
            repo_root=tmp_path,
        )


# ---------- resolve_binary ----------


def test_resolve_binary_returns_none_when_not_on_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CODEX_BIN", raising=False)
    monkeypatch.setattr(partner_invoke.shutil, "which", lambda _name: None)
    monkeypatch.setattr(partner_invoke, "_known_install_locations", lambda _p: [])
    assert partner_invoke.resolve_binary("codex") is None


def test_resolve_binary_finds_plain_name(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENCODE_BIN", raising=False)

    def fake_which(name: str) -> str | None:
        return "/usr/local/bin/opencode" if name == "opencode" else None
    monkeypatch.setattr(partner_invoke.shutil, "which", fake_which)
    assert partner_invoke.resolve_binary("opencode") == "/usr/local/bin/opencode"


def test_resolve_binary_finds_windows_extensions(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CLAUDE_BIN", raising=False)
    monkeypatch.setattr(partner_invoke.sys, "platform", "win32", raising=False)
    seen = []

    def fake_which(name: str) -> str | None:
        seen.append(name)
        return r"C:\bin\claude.ps1" if name == "claude.ps1" else None

    monkeypatch.setattr(partner_invoke.shutil, "which", fake_which)
    result = partner_invoke.resolve_binary("claude")
    assert result == r"C:\bin\claude.ps1"
    assert "claude" in seen
    assert "claude.ps1" in seen


def test_resolve_binary_uses_env_override_when_set(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """CODEX_BIN env var pointing at a real file wins over PATH lookup."""
    stub = tmp_path / "my-codex.exe"
    stub.write_text("")
    monkeypatch.setenv("CODEX_BIN", str(stub))

    def fake_which(_name: str) -> str | None:
        raise AssertionError("PATH lookup must not happen when env override resolves")

    monkeypatch.setattr(partner_invoke.shutil, "which", fake_which)
    assert partner_invoke.resolve_binary("codex") == str(stub)


def test_resolve_binary_ignores_env_override_when_file_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """CODEX_BIN pointing at a non-existent file falls back to PATH."""
    monkeypatch.setenv("CODEX_BIN", str(tmp_path / "nope.exe"))
    monkeypatch.setattr(
        partner_invoke.shutil, "which",
        lambda n: "/path/codex" if n == "codex" else None,
    )
    monkeypatch.setattr(partner_invoke, "_known_install_locations", lambda _p: [])
    assert partner_invoke.resolve_binary("codex") == "/path/codex"


def test_resolve_binary_falls_back_to_known_install_location(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """When env override is unset and PATH lookup fails, known install locations are checked."""
    monkeypatch.delenv("CODEX_BIN", raising=False)
    monkeypatch.setattr(partner_invoke.shutil, "which", lambda _n: None)

    fake_install = tmp_path / "OpenAI" / "Codex" / "bin" / "codex.exe"
    fake_install.parent.mkdir(parents=True)
    fake_install.write_text("")
    monkeypatch.setattr(
        partner_invoke, "_known_install_locations",
        lambda partner: [fake_install] if partner == "codex" else [],
    )
    assert partner_invoke.resolve_binary("codex") == str(fake_install)


def test_known_install_locations_codex_uses_localappdata_on_windows(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The Windows fallback maps codex to %LOCALAPPDATA%\\OpenAI\\Codex\\bin\\codex.exe."""
    monkeypatch.setattr(partner_invoke.sys, "platform", "win32", raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    paths = partner_invoke._known_install_locations("codex")
    assert paths == [tmp_path / "OpenAI" / "Codex" / "bin" / "codex.exe"]


def test_known_install_locations_empty_on_non_windows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """On non-Windows platforms, no fallback locations are probed."""
    monkeypatch.setattr(partner_invoke.sys, "platform", "linux", raising=False)
    assert partner_invoke._known_install_locations("codex") == []


# ---------- invoke_sync ----------


@pytest.fixture
def stub_dir(tmp_path: Path) -> Path:
    return tmp_path


_VALID_RESPONSE_BODY = (
    "---\n"
    "protocol: consult/v1\n"
    "from: codex\n"
    "to: claude\n"
    "mode: planning\n"
    "created_at_utc: 2026-05-09T00:00:00Z\n"
    "complete: true\n"
    "exit_status: ok\n"
    "---\n\n"
    "## Findings\n\nstub.\n\n"
    "## Risks\n\nnone.\n\n"
    "## Open questions\n\nnone.\n"
)


def _make_stub(stub_path: Path, *, exit_code: int, write_response: Path | None = None,
               response_body: str = _VALID_RESPONSE_BODY,
               sleep_sec: float = 0.0, stdout: str = "ok", stderr: str = "") -> Path:
    """Write a Python stub script that simulates a partner CLI."""
    body = f"""\
import sys, time
time.sleep({sleep_sec!r})
sys.stdout.write({stdout!r})
sys.stderr.write({stderr!r})
"""
    if write_response is not None:
        body += (
            f"open(r'{write_response}', 'w', encoding='utf-8')"
            f".write({response_body!r})\n"
        )
    body += f"sys.exit({exit_code})\n"
    stub_path.write_text(body, encoding="utf-8")
    return stub_path


def test_invoke_sync_missing_binary_returns_invocation_failed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(partner_invoke, "resolve_binary", lambda _p: None)
    log = tmp_path / "log.txt"
    result = partner_invoke.invoke_sync(
        "codex", "hi", log_path=log, repo_root=tmp_path,
    )
    assert result.exit_status == "error"
    assert result.error_kind == "invocation-failed"
    assert log.exists()
    assert "not found on PATH" in log.read_text(encoding="utf-8")


def test_invoke_sync_nonzero_exit_returns_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    stub = _make_stub(tmp_path / "stub.py", exit_code=2, stderr="boom")
    monkeypatch.setattr(partner_invoke, "resolve_binary", lambda _p: sys.executable)
    monkeypatch.setattr(
        partner_invoke, "build_command",
        lambda *a, **kw: [sys.executable, str(stub)],
    )
    log = tmp_path / "log.txt"
    result = partner_invoke.invoke_sync(
        "opencode", "hi", log_path=log, repo_root=tmp_path,
    )
    assert result.exit_status == "error"
    assert result.error_kind == "nonzero-exit"
    assert result.return_code == 2


def test_invoke_sync_timeout_kills_and_returns_timeout_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    stub = _make_stub(tmp_path / "stub.py", exit_code=0, sleep_sec=10.0)
    monkeypatch.setattr(partner_invoke, "resolve_binary", lambda _p: sys.executable)
    monkeypatch.setattr(
        partner_invoke, "build_command",
        lambda *a, **kw: [sys.executable, str(stub)],
    )
    log = tmp_path / "log.txt"
    result = partner_invoke.invoke_sync(
        "opencode", "hi", log_path=log, repo_root=tmp_path, timeout_sec=1,
    )
    assert result.exit_status == "error"
    assert result.error_kind == "timeout"
    assert "timeout" in log.read_text(encoding="utf-8").lower()


def test_invoke_sync_ok_with_partner_completed_when_response_written(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    response_path = tmp_path / "response.md"
    stub = _make_stub(tmp_path / "stub.py", exit_code=0, write_response=response_path)
    monkeypatch.setattr(partner_invoke, "resolve_binary", lambda _p: sys.executable)
    monkeypatch.setattr(
        partner_invoke, "build_command",
        lambda *a, **kw: [sys.executable, str(stub)],
    )
    log = tmp_path / "log.txt"
    result = partner_invoke.invoke_sync(
        "codex", "hi", log_path=log, repo_root=tmp_path,
        response_file=response_path,
    )
    assert result.exit_status == "ok"
    assert result.partner_completed is True
    assert result.response_path == response_path


def test_invoke_sync_ok_without_partner_completed_when_response_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    stub = _make_stub(tmp_path / "stub.py", exit_code=0)
    monkeypatch.setattr(partner_invoke, "resolve_binary", lambda _p: sys.executable)
    monkeypatch.setattr(
        partner_invoke, "build_command",
        lambda *a, **kw: [sys.executable, str(stub)],
    )
    log = tmp_path / "log.txt"
    expected_response = tmp_path / "response.md"
    result = partner_invoke.invoke_sync(
        "codex", "hi", log_path=log, repo_root=tmp_path,
        response_file=expected_response,
    )
    assert result.exit_status == "ok"
    assert result.partner_completed is False


# ---------- validate-on-harvest ----------


def test_invoke_sync_validates_response_and_passes_through_valid_artifact(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Stub writes a valid consult/v1 artifact; invoke_sync returns ok."""
    response_path = tmp_path / "response.md"
    stub = _make_stub(tmp_path / "stub.py", exit_code=0, write_response=response_path)
    monkeypatch.setattr(partner_invoke, "resolve_binary", lambda _p: sys.executable)
    monkeypatch.setattr(
        partner_invoke, "build_command",
        lambda *a, **kw: [sys.executable, str(stub)],
    )
    log = tmp_path / "log.txt"
    result = partner_invoke.invoke_sync(
        "codex", "hi", log_path=log, repo_root=tmp_path,
        response_file=response_path,
    )
    assert result.exit_status == "ok"
    assert result.partner_completed is True
    assert result.response_path == response_path
    # No invalid-output sidecar should have been created.
    assert not list(tmp_path.glob("response.md.invalid-output*"))


def test_invoke_sync_downgrades_invalid_capture_and_moves_to_sidecar(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Stub writes a non-consult/v1 file; invoke_sync moves it aside and downgrades."""
    response_path = tmp_path / "response.md"
    invalid_body = (
        "I couldn't write the file, here's the artifact in a code block:\n\n"
        "```\n---\nprotocol: consult/v1\n...\n```\n"
    )
    stub = _make_stub(
        tmp_path / "stub.py", exit_code=0,
        write_response=response_path, response_body=invalid_body,
    )
    monkeypatch.setattr(partner_invoke, "resolve_binary", lambda _p: sys.executable)
    monkeypatch.setattr(
        partner_invoke, "build_command",
        lambda *a, **kw: [sys.executable, str(stub)],
    )
    log = tmp_path / "log.txt"
    result = partner_invoke.invoke_sync(
        "codex", "hi", log_path=log, repo_root=tmp_path,
        response_file=response_path,
    )
    assert result.exit_status == "error"
    assert result.error_kind == "missing-response"
    assert result.partner_completed is False
    assert result.response_path is None
    # Canonical response.md must be vacated.
    assert not response_path.exists()
    # Invalid capture must survive at the sidecar path.
    sidecars = list(tmp_path.glob("response.md.invalid-output*"))
    assert len(sidecars) == 1
    assert "I couldn't write the file" in sidecars[0].read_text(encoding="utf-8")


# ---------- gemini stdout-JSON materialization ----------


def _gemini_stub(stub_path: Path, *, exit_code: int, assistant_text: str) -> Path:
    """Write a Python stub that emits gemini-cli-shaped JSON on stdout."""
    import json as _json
    payload = {
        "response": assistant_text,
        "stats": {"models": {"gemini-3.1-pro-preview": {"tokens": 100}}},
    }
    body = (
        "import sys\n"
        f"sys.stdout.write({_json.dumps(_json.dumps(payload))})\n"
        f"sys.exit({exit_code})\n"
    )
    stub_path.write_text(body, encoding="utf-8")
    return stub_path


def test_invoke_sync_gemini_materializes_response_from_stdout_json(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    response_path = tmp_path / "response.md"
    stub = _gemini_stub(
        tmp_path / "gemini_stub.py", exit_code=0,
        assistant_text=_VALID_RESPONSE_BODY,
    )
    monkeypatch.setattr(partner_invoke, "resolve_binary", lambda _p: sys.executable)
    monkeypatch.setattr(
        partner_invoke, "build_command",
        lambda *a, **kw: [sys.executable, str(stub)],
    )
    log = tmp_path / "log.txt"
    result = partner_invoke.invoke_sync(
        "gemini", "hi", log_path=log, repo_root=tmp_path,
        response_file=response_path,
    )
    assert result.exit_status == "ok"
    assert result.partner_completed is True
    assert response_path.exists()
    assert response_path.read_text(encoding="utf-8") == _VALID_RESPONSE_BODY


def test_invoke_sync_gemini_invalid_assistant_text_downgrades(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    response_path = tmp_path / "response.md"
    stub = _gemini_stub(
        tmp_path / "gemini_stub.py", exit_code=0,
        assistant_text="hi I can't really do that, here's some prose instead",
    )
    monkeypatch.setattr(partner_invoke, "resolve_binary", lambda _p: sys.executable)
    monkeypatch.setattr(
        partner_invoke, "build_command",
        lambda *a, **kw: [sys.executable, str(stub)],
    )
    log = tmp_path / "log.txt"
    result = partner_invoke.invoke_sync(
        "gemini", "hi", log_path=log, repo_root=tmp_path,
        response_file=response_path,
    )
    assert result.exit_status == "error"
    assert result.error_kind == "missing-response"
    assert not response_path.exists()
    sidecars = list(tmp_path.glob("response.md.invalid-output*"))
    assert len(sidecars) == 1


def test_invoke_sync_gemini_text_fallback_extracts_artifact_from_raw_stdout(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """When --output-format json fails (tool errors), gemini emits raw text.
    The materialization helper must still extract the consult/v1 artifact.
    """
    response_path = tmp_path / "response.md"
    # Gemini commonly emits preamble before the artifact when JSON output
    # falls through to text. The extractor must find the artifact regardless.
    # Trailing chatter is uncommon when the prompt says "output the artifact
    # last" — we don't enforce its exclusion in the helper.
    raw_text_with_artifact = (
        "I will now respond.\n\n"
        "Some preamble gemini felt compelled to add.\n\n"
        + _VALID_RESPONSE_BODY
    )
    body = (
        "import sys\n"
        f"sys.stdout.write({raw_text_with_artifact!r})\n"
        "sys.exit(0)\n"
    )
    stub = tmp_path / "gemini_stub.py"
    stub.write_text(body, encoding="utf-8")
    monkeypatch.setattr(partner_invoke, "resolve_binary", lambda _p: sys.executable)
    monkeypatch.setattr(
        partner_invoke, "build_command",
        lambda *a, **kw: [sys.executable, str(stub)],
    )
    log = tmp_path / "log.txt"
    result = partner_invoke.invoke_sync(
        "gemini", "hi", log_path=log, repo_root=tmp_path,
        response_file=response_path,
    )
    assert result.exit_status == "ok"
    assert result.partner_completed is True
    # The materialized file must START at the artifact, dropping all preamble.
    written = response_path.read_text(encoding="utf-8")
    assert written.startswith("---\nprotocol: consult/v1\n")
    assert "preamble" not in written


def test_invoke_sync_gemini_missing_response_field_returns_missing_response(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """If gemini's stdout JSON has no extractable assistant text, result is missing-response."""
    response_path = tmp_path / "response.md"
    # Stub emits valid JSON but no `response` field — wrapper should not write the file.
    body = (
        "import sys\n"
        "sys.stdout.write('{\"stats\": {}}')\n"
        "sys.exit(0)\n"
    )
    stub = tmp_path / "gemini_stub.py"
    stub.write_text(body, encoding="utf-8")
    monkeypatch.setattr(partner_invoke, "resolve_binary", lambda _p: sys.executable)
    monkeypatch.setattr(
        partner_invoke, "build_command",
        lambda *a, **kw: [sys.executable, str(stub)],
    )
    log = tmp_path / "log.txt"
    result = partner_invoke.invoke_sync(
        "gemini", "hi", log_path=log, repo_root=tmp_path,
        response_file=response_path,
    )
    assert result.exit_status == "error"
    assert result.error_kind == "missing-response"
    assert not response_path.exists()


# ---------- repo root discovery ----------


def test_resolve_repo_root_returns_dir_with_agents_and_game() -> None:
    root = partner_invoke.resolve_repo_root()
    assert (root / "AGENTS.md").exists()
    assert (root / "game").is_dir()


# ---------- consult/v1 artifact helpers ----------


def test_write_error_response_publishes_complete_error_artifact(tmp_path: Path) -> None:
    response = tmp_path / "response.md"

    partner_invoke.write_error_response(
        response,
        from_agent="claude",
        to_agent="codex",
        mode="planning",
        error_kind="timeout",
        detail="timed out after 600s",
        created_at_utc="2026-05-09T00:00:00Z",
    )

    fields = partner_invoke.validate_response_file(response)
    assert fields["protocol"] == "consult/v1"
    assert fields["complete"] == "true"
    assert fields["exit_status"] == "error"
    assert fields["error_kind"] == "timeout"
    assert fields["partner_completed"] == "false"
    assert not list(tmp_path.glob(".tmp_*"))


def test_validate_response_file_rejects_reversed_direction_fields(tmp_path: Path) -> None:
    """A schema-shaped artifact with the wrong from/to direction must fail
    when expected_from/expected_to are supplied (r003 Change E)."""
    response = tmp_path / "response.md"
    # Reversed direction: artifact says from=codex/to=gemini but the caller
    # expected from=gemini (the partner) and to=codex (the initiator).
    response.write_text(
        "---\n"
        "protocol: consult/v1\n"
        "from: codex\n"
        "to: gemini\n"
        "mode: planning\n"
        "created_at_utc: 2026-05-10T00:00:00Z\n"
        "complete: true\n"
        "exit_status: ok\n"
        "---\n\n"
        "## Findings\n\nstub.\n",
        encoding="utf-8",
    )
    # Without direction kwargs: existing behavior, validation passes.
    fields = partner_invoke.validate_response_file(response)
    assert fields["from"] == "codex"
    # With direction kwargs: reversed fields must raise.
    with pytest.raises(ValueError, match="from|direction"):
        partner_invoke.validate_response_file(
            response, expected_from="gemini", expected_to="codex",
        )


def test_validate_response_file_accepts_correct_direction_when_kwargs_provided(
    tmp_path: Path,
) -> None:
    response = tmp_path / "response.md"
    response.write_text(
        "---\n"
        "protocol: consult/v1\n"
        "from: gemini\n"
        "to: claude\n"
        "mode: planning\n"
        "created_at_utc: 2026-05-10T00:00:00Z\n"
        "complete: true\n"
        "exit_status: ok\n"
        "---\n\n"
        "## Findings\n\nstub.\n",
        encoding="utf-8",
    )
    fields = partner_invoke.validate_response_file(
        response, expected_from="gemini", expected_to="claude",
    )
    assert fields["from"] == "gemini"
    assert fields["to"] == "claude"


def test_validate_response_file_rejects_incomplete_response(tmp_path: Path) -> None:
    response = tmp_path / "response.md"
    response.write_text(
        "---\n"
        "protocol: consult/v1\n"
        "from: claude\n"
        "to: codex\n"
        "mode: planning\n"
        "created_at_utc: 2026-05-09T00:00:00Z\n"
        "complete: false\n"
        "exit_status: ok\n"
        "---\n\n"
        "## Findings\n\nNo issues.\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="complete"):
        partner_invoke.validate_response_file(response)

