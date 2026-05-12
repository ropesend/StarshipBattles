"""Subprocess helper for cross-agent CLI invocation.

Provides binary resolution and per-partner argv construction for codex,
claude, and opencode CLIs. Used by the consult-on-Claude-side skills
(`claude-consult`, `claude-consult-respond`) to invoke a partner agent
non-interactively.

The harmonized contract this module implements lives at
`AgentCoordination/Scratchpad/Discussion/20260509T170814Z_consult-discuss-harmonize/plans/consult_harmonization_r002.md`.
The canonical CLI recipe registry lives at
`AgentCoordination/protocols/partner_cli.md`.

Sandbox enforcement is treated as policy carried by prompts and tool
restrictions, NOT a CLI guarantee, until live probing confirms otherwise.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

PartnerName = Literal["codex", "claude", "opencode", "gemini"]
DEFAULT_GEMINI_MODEL = "gemini-3.1-pro-preview"
Sandbox = Literal["read-only", "workspace-write"]
ExitStatus = Literal["ok", "error"]
ErrorKind = Literal["timeout", "nonzero-exit", "missing-response", "invocation-failed"]
ConsultMode = Literal["planning", "mid-project-review", "pre-final-check", "deep-dive"]

CONSULT_PROTOCOL = "consult/v1"
_VALID_EXIT_STATUSES = {"ok", "error", "partial"}
_VALID_ERROR_KINDS = {
    "timeout",
    "nonzero-exit",
    "missing-response",
    "invocation-failed",
}


def resolve_repo_root() -> Path:
    """Walk up from this file to find the repo root."""
    here = Path(__file__).resolve()
    for parent in (here.parent, *here.parents):
        if (parent / "AGENTS.md").exists() and (parent / "game").is_dir():
            return parent
    raise RuntimeError("Unable to discover repository root from partner_invoke.py")


def _known_install_locations(name: PartnerName) -> list[Path]:
    """Best-effort fallback paths to probe when PATH lookup fails.

    Returns paths to check via `Path.is_file()`. Empty list means no
    platform-specific fallback is available. The caller MUST verify the
    file still exists before returning it from `resolve_binary`.
    """
    if sys.platform != "win32":
        return []
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        return []
    locations: dict[str, list[Path]] = {
        "codex": [Path(local_app_data) / "OpenAI" / "Codex" / "bin" / "codex.exe"],
    }
    return locations.get(name, [])


def resolve_binary(name: PartnerName) -> str | None:
    """Find a partner CLI.

    Resolution order:
    1. Env-var override (e.g., `CODEX_BIN`, `CLAUDE_BIN`, `OPENCODE_BIN`,
       `GEMINI_BIN`) pointing at an existing file.
    2. PATH lookup via `shutil.which` (Windows-aware: probes .exe/.cmd/.ps1).
    3. Known per-platform install locations (e.g.,
       `%LOCALAPPDATA%\\OpenAI\\Codex\\bin\\codex.exe` on Windows).
    """
    env_override = os.environ.get(f"{name.upper()}_BIN")
    if env_override and Path(env_override).is_file():
        return env_override
    candidates: list[str] = [name]
    if sys.platform == "win32":
        candidates += [f"{name}.exe", f"{name}.cmd", f"{name}.ps1"]
    for candidate in candidates:
        exe = shutil.which(candidate)
        if exe:
            return exe
    for path in _known_install_locations(name):
        if path.is_file():
            return str(path)
    return None


def atomic_write_text(path: Path, content: str) -> None:
    """Write text through a same-directory temp file and final rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.parent / f".tmp_{uuid.uuid4().hex}.md"
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def parse_frontmatter(text: str) -> dict[str, str]:
    """Parse simple YAML-style frontmatter into string fields."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("frontmatter must start on line 1")
    end_index: int | None = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break
    if end_index is None:
        raise ValueError("frontmatter closing marker missing")

    fields: dict[str, str] = {}
    for line in lines[1:end_index]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip("\"'")
    return fields


def validate_response_file(
    path: Path,
    *,
    expected_from: str | None = None,
    expected_to: str | None = None,
) -> dict[str, str]:
    """Validate a `consult/v1` response artifact and return frontmatter.

    When `expected_from` / `expected_to` are supplied (r003 Change E), the
    parsed `from` / `to` fields must match — catches schema-shaped artifacts
    that have reversed direction (codex live smoke 2026-05-10 produced a
    valid-looking artifact with `from: codex, to: gemini` when it should
    have been `from: gemini, to: codex`).
    """
    fields = parse_frontmatter(path.read_text(encoding="utf-8"))
    required = {
        "protocol",
        "from",
        "to",
        "mode",
        "created_at_utc",
        "complete",
        "exit_status",
    }
    missing = sorted(required.difference(fields))
    if missing:
        raise ValueError(f"response missing required fields: {', '.join(missing)}")
    if fields["protocol"] != CONSULT_PROTOCOL:
        raise ValueError(f"unexpected protocol: {fields['protocol']!r}")
    if fields["complete"] != "true":
        raise ValueError("response complete marker must be true")
    if fields["exit_status"] not in _VALID_EXIT_STATUSES:
        raise ValueError(f"invalid exit_status: {fields['exit_status']!r}")
    if fields["exit_status"] == "error":
        if fields.get("error_kind") not in _VALID_ERROR_KINDS:
            raise ValueError("error response must include a valid error_kind")
        if fields.get("partner_completed") != "false":
            raise ValueError("error response must include partner_completed: false")
    if expected_from is not None and fields["from"] != expected_from:
        raise ValueError(
            f"response direction mismatch: expected from={expected_from!r}, "
            f"got from={fields['from']!r}"
        )
    if expected_to is not None and fields["to"] != expected_to:
        raise ValueError(
            f"response direction mismatch: expected to={expected_to!r}, "
            f"got to={fields['to']!r}"
        )
    return fields


def write_error_response(
    path: Path,
    *,
    from_agent: PartnerName | str,
    to_agent: PartnerName | str,
    mode: ConsultMode | str,
    error_kind: ErrorKind,
    detail: str = "",
    created_at_utc: str | None = None,
) -> None:
    """Publish a complete `consult/v1` error response artifact."""
    if error_kind not in _VALID_ERROR_KINDS:
        raise ValueError(f"invalid error_kind: {error_kind!r}")
    timestamp = created_at_utc or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    body_detail = detail.strip() or "Partner invocation did not produce a usable response."
    content = (
        "---\n"
        f"protocol: {CONSULT_PROTOCOL}\n"
        f"from: {from_agent}\n"
        f"to: {to_agent}\n"
        f"mode: {mode}\n"
        f"created_at_utc: {timestamp}\n"
        "complete: true\n"
        "exit_status: error\n"
        f"error_kind: {error_kind}\n"
        "partner_completed: false\n"
        "---\n\n"
        "## Findings\n\n"
        "The partner consult failed before producing advisory findings.\n\n"
        "## Risks\n\n"
        "- Treat this consult as incomplete; do not infer partner agreement.\n\n"
        "## Open questions\n\n"
        f"- {body_detail}\n"
    )
    atomic_write_text(path, content)
    validate_response_file(path)


def build_command(
    partner: PartnerName,
    binary: str,
    prompt: str,
    *,
    repo_root: Path,
    response_file: Path | None = None,
    sandbox: Sandbox = "read-only",
    model: str | None = None,
) -> list[str]:
    """Build the partner-specific argv per `AgentCoordination/protocols/partner_cli.md`.

    The trailing element is always the prompt string. Callers MUST pass the
    full final prompt (Claude/OpenCode read it as a single argument; Codex
    accepts a positional prompt or stdin).
    """
    if partner == "opencode":
        return [
            binary,
            "run",
            "--dir", str(repo_root),
            "--format", "json",
            "--dangerously-skip-permissions",
            prompt,
        ]
    if partner == "codex":
        # `codex exec` is already non-interactive — no `--ask-for-approval`
        # flag exists in 0.130.x. `--sandbox <mode>` is the policy boundary.
        # `--skip-git-repo-check` keeps the smoke working when invoked from a
        # subdirectory or non-default workspace state.
        # `--add-dir <consult-leaf>` is passed for documentation-of-intent
        # purposes, but in 0.130.x it does NOT grant write access under
        # `--sandbox read-only` (verified 2026-05-12: per `codex exec --help`,
        # --add-dir adds dirs "writable alongside the primary workspace", and
        # the primary workspace is non-writable under read-only sandbox). The
        # caller (`claude-consult`) therefore always passes
        # `sandbox='workspace-write'` for consults so codex can write
        # `response.md`. Advisory-only is enforced by the responder skill's
        # Permissions section, not by sandbox policy.
        cmd = [
            binary,
            "exec",
            "-C", str(repo_root),
            "--sandbox", sandbox,
            "--skip-git-repo-check",
        ]
        if response_file is not None:
            # `--output-last-message` writes codex's final assistant text to the
            # given path AT END OF RUN. Pointing it at `response_file` directly
            # OVERWRITES whatever codex produced via `apply_patch`, replacing
            # the valid consult/v1 artifact with chat text like "Done. Wrote
            # response.md." (verified 2026-05-12 — caused spurious
            # missing-response failures after a successful apply_patch). Point
            # it at a sidecar `last_message.txt` so the artifact codex writes
            # via `apply_patch` survives untouched, and the sidecar is
            # available as fallback evidence if needed.
            last_message_file = response_file.with_name("last_message.txt")
            cmd += [
                "--add-dir", str(response_file.parent),
                "--output-last-message", str(last_message_file),
            ]
        cmd.append(prompt)
        return cmd
    if partner == "claude":
        return [
            binary,
            "-p",
            "--no-session-persistence",
            "--output-format", "json",
            "--permission-mode", "dontAsk",
            prompt,
        ]
    if partner == "gemini":
        # Pattern A: read-only mode + skip-trust + JSON stdout. No
        # `--output-last-message` exists, so the wrapper materializes
        # `response.md` from gemini's stdout JSON via
        # `_materialize_gemini_response`. `--include-directories` is omitted
        # because plan mode forbids writes anyway; granting workspace would
        # be cosmetic.
        # NOTE: gemini's `-p/--prompt` is a string-valued flag; the prompt
        # must be the next arg (live smoke 2026-05-10 surfaced "not enough
        # arguments following: p" when prompt was at the end).
        # `--session-id <fresh-uuid>` is mandatory per r003 Change D: gemini
        # `-p` mode persists session/tool state across separate invocations
        # by default (codex live smoke 2026-05-10 caught carryover from a
        # prior leaf's request file into a subsequent inline-prompt run).
        gemini_model = model or DEFAULT_GEMINI_MODEL
        session_id = str(uuid.uuid4())
        return [
            binary,
            "-p", prompt,
            "-m", gemini_model,
            "--approval-mode", "plan",
            "--skip-trust",
            "--output-format", "json",
            "--session-id", session_id,
        ]
    raise ValueError(f"Unknown partner: {partner!r}")


@dataclass
class InvokeResult:
    """Outcome of a partner invocation.

    `partner_completed` distinguishes "wrapper finished publishing" (always
    true on return) from "partner produced its response artifact" — the
    consult contract uses the latter for `complete: true / partner_completed`
    semantics in error stubs.
    """
    partner: PartnerName
    exit_status: ExitStatus
    error_kind: ErrorKind | None = None
    return_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    log_path: Path | None = None
    response_path: Path | None = None
    partner_completed: bool = False


def kill_process_tree(proc: subprocess.Popen) -> None:
    """Kill subprocess and descendants. Windows uses taskkill /T to clean the tree."""
    try:
        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                capture_output=True,
                timeout=10,
            )
        else:
            proc.kill()
    except Exception:  # Intentional broad catch: best-effort cleanup of partner subprocess
        pass
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass


def _extract_consult_v1_artifact(text: str) -> str | None:
    """Locate and extract a `consult/v1` artifact embedded in raw text.

    Used as a fallback when gemini's `--output-format json` is not honored
    (live smoke 2026-05-10 found that tool-error cascades cause gemini to
    emit raw markdown to stdout instead of structured JSON). Searches for a
    block beginning with `---\nprotocol: consult/v1` and ending at the next
    line-starting `---` (closing frontmatter), then returns from the
    artifact's opening `---` through end-of-text.
    """
    import re as _re
    match = _re.search(
        r"^(---\s*\nprotocol:\s*consult/v1\b)",
        text,
        flags=_re.MULTILINE,
    )
    if not match:
        return None
    start = match.start(1)
    return text[start:].rstrip() + "\n"


def _materialize_gemini_response(stdout: str, response_file: Path) -> bool:
    """Extract gemini's final assistant text and write it to `response_file`.

    Two paths:
    1. JSON path: `--output-format json` produces an object whose `response`
       field carries the assistant's final message.
    2. Text fallback: when JSON output is not honored (tool-error cascade,
       per the 2026-05-10 live smoke), parse the captured stdout as raw
       text and extract the `consult/v1` artifact embedded somewhere
       inside.

    Returns True on successful write; False if neither path yields a
    usable artifact. Schema validation of the written file happens
    separately in `invoke_sync`'s validate-on-harvest block.
    """
    import json as _json

    text: str | None = None

    # JSON path
    try:
        payload = _json.loads(stdout)
    except (_json.JSONDecodeError, TypeError):
        payload = None
    if isinstance(payload, dict):
        candidate = payload.get("response") or payload.get("text") or ""
        if isinstance(candidate, str) and candidate.strip():
            text = candidate

    # Text fallback: extract embedded consult/v1 artifact
    if text is None:
        text = _extract_consult_v1_artifact(stdout)

    if text is None or not text.strip():
        return False
    atomic_write_text(response_file, text)
    return True


def invoke_sync(
    partner: PartnerName,
    prompt: str,
    *,
    log_path: Path,
    repo_root: Path | None = None,
    response_file: Path | None = None,
    sandbox: Sandbox = "read-only",
    timeout_sec: int = 600,
    model: str | None = None,
    expected_from: str | None = None,
    expected_to: str | None = None,
) -> InvokeResult:
    """Invoke a partner CLI synchronously, blocking until exit, kill, or timeout.

    Always writes a log file at `log_path` with command, cwd, exit status,
    captured stdout, and stderr — even on missing-binary or invocation
    failures. Callers can attach the log path to error artifacts.
    """
    if repo_root is None:
        repo_root = resolve_repo_root()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    binary = resolve_binary(partner)
    if binary is None:
        msg = f"{partner} not found on PATH"
        log_path.write_text(f"[invocation-failed] {msg}\n", encoding="utf-8")
        return InvokeResult(
            partner=partner,
            exit_status="error",
            error_kind="invocation-failed",
            stderr=msg,
            log_path=log_path,
        )

    cmd = build_command(
        partner,
        binary,
        prompt,
        repo_root=repo_root,
        response_file=response_file,
        sandbox=sandbox,
        model=model,
    )

    started = datetime.now(timezone.utc).isoformat()
    log_lines: list[str] = [
        f"[{started}] partner={partner} cwd={repo_root}\n",
        f"command: {cmd}\n",
    ]

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(repo_root),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            # Force UTF-8 with replacement on decode error: partner CLIs
            # emit Unicode (curly apostrophes, em-dashes) and on Windows
            # `text=True` defaults to cp1252, which crashes the reader
            # thread. Live smoke 2026-05-09 proved this.
            encoding="utf-8",
            errors="replace",
            creationflags=(
                subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            ),
        )
    except OSError as exc:
        log_lines.append(f"[invocation-failed] {exc}\n")
        log_path.write_text("".join(log_lines), encoding="utf-8")
        return InvokeResult(
            partner=partner,
            exit_status="error",
            error_kind="invocation-failed",
            stderr=str(exc),
            log_path=log_path,
        )

    try:
        stdout, stderr = proc.communicate(timeout=timeout_sec)
    except subprocess.TimeoutExpired:
        kill_process_tree(proc)
        try:
            stdout, stderr = proc.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            stdout, stderr = "", ""
        log_lines.append(f"[timeout after {timeout_sec}s] killed process tree\n")
        log_lines.append(f"--- stdout (post-kill) ---\n{stdout}\n")
        log_lines.append(f"--- stderr (post-kill) ---\n{stderr}\n")
        log_path.write_text("".join(log_lines), encoding="utf-8")
        return InvokeResult(
            partner=partner,
            exit_status="error",
            error_kind="timeout",
            return_code=None,
            stdout=stdout,
            stderr=stderr,
            log_path=log_path,
        )

    log_lines.append(f"[exit] returncode={proc.returncode}\n")
    log_lines.append(f"--- stdout ---\n{stdout}\n--- stderr ---\n{stderr}\n")
    log_path.write_text("".join(log_lines), encoding="utf-8")

    if proc.returncode != 0:
        return InvokeResult(
            partner=partner,
            exit_status="error",
            error_kind="nonzero-exit",
            return_code=proc.returncode,
            stdout=stdout,
            stderr=stderr,
            log_path=log_path,
        )

    # Gemini materialization: gemini-cli has no `--output-last-message`, so
    # the wrapper extracts the final assistant text from stdout JSON and
    # writes `response.md` itself before validate-on-harvest runs. If the
    # JSON has no extractable assistant text, partner_completed stays False
    # and validate-on-harvest is skipped — the result is downgraded to
    # missing-response below.
    if partner == "gemini" and response_file is not None:
        if not _materialize_gemini_response(stdout, response_file):
            log_path.write_text(
                log_path.read_text(encoding="utf-8")
                + "[gemini-materialize] could not extract assistant text from stdout JSON\n",
                encoding="utf-8",
            )
            return InvokeResult(
                partner=partner,
                exit_status="error",
                error_kind="missing-response",
                return_code=0,
                stdout=stdout,
                stderr=stderr,
                log_path=log_path,
                response_path=None,
                partner_completed=False,
            )

    partner_completed = response_file is not None and response_file.exists()

    # Validate-on-harvest: when response_file is provided and exists, the
    # captured text MUST validate as a consult/v1 artifact. `--output-last-message`
    # captures whatever the partner's last assistant text happened to be; that
    # is not necessarily a deliberately-written artifact (live smoke 2026-05-09
    # caught a sandbox-blocked write whose chat-output explanation got captured
    # in place of a real response). On validation failure, move the invalid
    # capture aside so the canonical name stays vacant for a proper error
    # artifact, and downgrade to error_kind="missing-response".
    if partner_completed:
        try:
            validate_response_file(  # type: ignore[arg-type]
                response_file,
                expected_from=expected_from,
                expected_to=expected_to,
            )
        except (ValueError, OSError) as exc:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            sidecar = response_file.with_name(  # type: ignore[union-attr]
                f"{response_file.name}.invalid-output-{timestamp}.txt"  # type: ignore[union-attr]
            )
            response_file.replace(sidecar)  # type: ignore[union-attr]
            log_path.write_text(
                log_path.read_text(encoding="utf-8")
                + f"[validate-on-harvest] response did not validate as consult/v1: {exc}\n"
                + f"[validate-on-harvest] moved capture to {sidecar}\n",
                encoding="utf-8",
            )
            return InvokeResult(
                partner=partner,
                exit_status="error",
                error_kind="missing-response",
                return_code=0,
                stdout=stdout,
                stderr=stderr,
                log_path=log_path,
                response_path=None,
                partner_completed=False,
            )

    return InvokeResult(
        partner=partner,
        exit_status="ok",
        error_kind=None,
        return_code=0,
        stdout=stdout,
        stderr=stderr,
        log_path=log_path,
        response_path=response_file if partner_completed else None,
        partner_completed=partner_completed,
    )
