"""Authoritative state for 03c phase-aware project execution.

Defines `phase_state.json` schema, atomic save/load, file locking for
concurrent writers, and CRUD helpers for phases, reviews, and findings.

Design rules:
    - State is a plain dict; serialized as JSON. No dataclasses, no ORM.
    - All mutations go through helpers that validate transitions and
      maintain invariants (e.g., supersession on clean cumulative reviews).
    - Concurrent writes are serialized via `locked(path)` (stdlib only:
      msvcrt on Windows, fcntl on Unix).
    - Saves are atomic (temp file + os.replace).

Schema version 1.
"""
from __future__ import annotations

import contextlib
import json
import os
import platform
import time
from pathlib import Path
from typing import Any, Iterator

SCHEMA_VERSION = 1
EXECUTION_PROTOCOL = "03c-phase-aware-execution"

VALID_PHASE_STATUSES = {
    "not_started",
    "in_progress",
    "committed",
    "under_review",
    "verified",
    "scrapped",
}
VALID_REVIEW_MODES = {"standard", "lightweight"}
VALID_REVIEW_RESULT_STATUSES = {
    "pending",
    "completed_clean",
    "completed_findings",
    "failed",
    "sha_mismatch",
}
VALID_FINDING_STATUSES = {
    "open",
    "addressed_pending_review",
    "verified",
    "deferred_until_phase",
    "wontfix_with_rationale",
    "superseded",
}
VALID_AUDIT_STATUSES = {"not_run", "in_progress", "passed", "failed"}


def initial_state(project_id: str) -> dict[str, Any]:
    """Build a fresh state dict for a new 03c project."""
    return {
        "schema_version": SCHEMA_VERSION,
        "project_id": project_id,
        "execution_protocol": EXECUTION_PROTOCOL,
        # Project trunk and phase branches share the proj/{id}/ namespace.
        # Using proj/{id}/main avoids git's ref directory/file conflict.
        "project_branch": f"proj/{project_id}/main",
        "buffer_depth": 0,
        "buffer_depth_override_reason": None,
        "phases": {},
        "reviews": {},
        "findings": {},
        "audit": {
            "final_audit_request_id": None,
            "final_audit_status": "not_run",
            "merge_to_main_sha": None,
            "merge_to_main_at_utc": None,
        },
    }


def validate(state: dict[str, Any]) -> None:
    """Raise ValueError if state is structurally invalid."""
    if state.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(
            f"unsupported schema_version: {state.get('schema_version')!r} (expected {SCHEMA_VERSION})"
        )
    for required in ("project_id", "execution_protocol", "project_branch", "phases", "reviews", "findings", "audit"):
        if required not in state:
            raise ValueError(f"state missing required key: {required!r}")
    if state["buffer_depth"] not in (0, 1):
        raise ValueError(f"buffer_depth must be 0 or 1, got {state['buffer_depth']!r}")
    if state["buffer_depth"] == 1 and not state.get("buffer_depth_override_reason"):
        raise ValueError("buffer_depth=1 requires buffer_depth_override_reason")
    if state["audit"]["final_audit_status"] not in VALID_AUDIT_STATUSES:
        raise ValueError(f"invalid audit final_audit_status: {state['audit']['final_audit_status']!r}")


def load_state(path: Path) -> dict[str, Any]:
    """Load state from disk. Raises FileNotFoundError if missing."""
    text = Path(path).read_text(encoding="utf-8")
    state = json.loads(text)
    validate(state)
    return state


def load_or_init(path: Path, project_id: str) -> dict[str, Any]:
    """Load existing state, or return initial_state if file does not exist."""
    p = Path(path)
    if p.exists():
        return load_state(p)
    return initial_state(project_id)


def save_state(path: Path, state: dict[str, Any]) -> None:
    """Atomically write state to disk after validating."""
    validate(state)
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(f".tmp_{os.getpid()}_{time.time_ns()}_{p.name}")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, p)


@contextlib.contextmanager
def locked(path: Path, timeout: float = 30.0, poll: float = 0.05) -> Iterator[None]:
    """Acquire a process-level exclusive lock for the given state file.

    Uses a sidecar `<path>.lock` file. Both Windows (msvcrt.locking) and
    Unix (fcntl.lockf) are supported via stdlib only.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    lock_path = p.with_name(p.name + ".lock")
    deadline = time.monotonic() + timeout
    if platform.system() == "Windows":
        import msvcrt
        # Open and try to lock 1 byte from offset 0; retry until acquired.
        fp = open(lock_path, "a+b")
        try:
            fp.seek(0)
            if fp.tell() == 0:
                fp.write(b"\x00")
                fp.flush()
            while True:
                try:
                    fp.seek(0)
                    msvcrt.locking(fp.fileno(), msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise TimeoutError(f"could not lock {lock_path} within {timeout}s")
                    time.sleep(poll)
            try:
                yield
            finally:
                fp.seek(0)
                try:
                    msvcrt.locking(fp.fileno(), msvcrt.LK_UNLCK, 1)
                except OSError:
                    pass
        finally:
            fp.close()
    else:
        import fcntl
        fp = open(lock_path, "a+b")
        try:
            while True:
                try:
                    fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise TimeoutError(f"could not lock {lock_path} within {timeout}s")
                    time.sleep(poll)
            try:
                yield
            finally:
                try:
                    fcntl.lockf(fp, fcntl.LOCK_UN)
                except OSError:
                    pass
        finally:
            fp.close()


# ---------------------------------------------------------------------------
# Phase CRUD
# ---------------------------------------------------------------------------


def add_phase(
    state: dict[str, Any],
    phase_id: str,
    *,
    depends_on: list[str],
    planned_files: list[str] | None = None,
    review_mode: str = "standard",
) -> None:
    """Add a phase record. Idempotent: re-adding overwrites the metadata only."""
    if review_mode not in VALID_REVIEW_MODES:
        raise ValueError(
            f"review_mode must be one of {sorted(VALID_REVIEW_MODES)}, got {review_mode!r}"
        )
    state["phases"][phase_id] = {
        "depends_on": list(depends_on),
        "review_mode": review_mode,
        "planned_files": list(planned_files or []),
        "status": "not_started",
        "phase_branch": None,
        "phase_base_sha": None,
        "phase_head_sha": None,
        "merged_into_project_at_sha": None,
        "review_request_id": None,
        "verifying_review_id": None,
        "review_dispatch_failed": False,
        "scrap_history": [],
    }


def set_phase_status(state: dict[str, Any], phase_id: str, new_status: str) -> None:
    if new_status not in VALID_PHASE_STATUSES:
        raise ValueError(
            f"phase status must be one of {sorted(VALID_PHASE_STATUSES)}, got {new_status!r}"
        )
    state["phases"][phase_id]["status"] = new_status


def set_phase_branch(
    state: dict[str, Any],
    phase_id: str,
    *,
    phase_branch: str,
    phase_base_sha: str,
) -> None:
    p = state["phases"][phase_id]
    p["phase_branch"] = phase_branch
    p["phase_base_sha"] = phase_base_sha


def set_phase_head_sha(state: dict[str, Any], phase_id: str, sha: str) -> None:
    state["phases"][phase_id]["phase_head_sha"] = sha


def set_phase_merged(state: dict[str, Any], phase_id: str, project_sha: str) -> None:
    state["phases"][phase_id]["merged_into_project_at_sha"] = project_sha


def set_phase_review_request(
    state: dict[str, Any], phase_id: str, request_id: str | None, *, dispatch_failed: bool = False
) -> None:
    p = state["phases"][phase_id]
    p["review_request_id"] = request_id
    p["review_dispatch_failed"] = dispatch_failed


def record_scrap(state: dict[str, Any], phase_id: str, *, reason: str) -> None:
    """Reset a phase to not_started and append a scrap_history entry."""
    p = state["phases"][phase_id]
    from datetime import datetime, timezone
    entry = {
        "at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "reason": reason,
        "prior_phase_branch": p["phase_branch"],
        "prior_phase_head_sha": p["phase_head_sha"],
        "prior_review_request_id": p["review_request_id"],
    }
    p["scrap_history"].append(entry)
    p["status"] = "not_started"
    p["phase_branch"] = None
    p["phase_base_sha"] = None
    p["phase_head_sha"] = None
    p["merged_into_project_at_sha"] = None
    p["review_request_id"] = None
    p["verifying_review_id"] = None
    p["review_dispatch_failed"] = False


# ---------------------------------------------------------------------------
# Review CRUD
# ---------------------------------------------------------------------------


def record_review(
    state: dict[str, Any],
    review_id: str,
    project_tip_sha: str,
    coverage_set: list[str],
    focus_phase: str,
    review_mode: str,
    dispatched_at_utc: str,
) -> None:
    if review_mode not in VALID_REVIEW_MODES:
        raise ValueError(f"review_mode must be one of {sorted(VALID_REVIEW_MODES)}")
    sequence = len(state["reviews"]) + 1
    state["reviews"][review_id] = {
        "review_sequence": sequence,
        "project_tip_sha": project_tip_sha,
        "coverage_set": list(coverage_set),
        "focus_phase": focus_phase,
        "review_mode": review_mode,
        "dispatched_at_utc": dispatched_at_utc,
        "result_status": "pending",
        "result_path": None,
        "supersedes": [],
        "superseded_by": None,
    }


def mark_review_result(
    state: dict[str, Any],
    review_id: str,
    result_status: str,
    *,
    result_path: str | None = None,
) -> None:
    if result_status not in VALID_REVIEW_RESULT_STATUSES:
        raise ValueError(
            f"result_status must be one of {sorted(VALID_REVIEW_RESULT_STATUSES)}, got {result_status!r}"
        )
    review = state["reviews"][review_id]
    review["result_status"] = result_status
    if result_path is not None:
        review["result_path"] = result_path

    if result_status == "completed_clean":
        # Verify every phase in coverage_set.
        for phase_id in review["coverage_set"]:
            phase = state["phases"][phase_id]
            phase["status"] = "verified"
            phase["verifying_review_id"] = review_id
        # Supersede earlier clean reviews whose coverage_set is a strict subset.
        my_cov = set(review["coverage_set"])
        for other_id, other in state["reviews"].items():
            if other_id == review_id:
                continue
            if other["result_status"] != "completed_clean":
                continue
            if other.get("superseded_by"):
                continue
            other_cov = set(other["coverage_set"])
            if other_cov < my_cov:  # strict subset
                other["superseded_by"] = review_id
                review["supersedes"].append(other_id)


# ---------------------------------------------------------------------------
# Finding CRUD
# ---------------------------------------------------------------------------


def add_finding(
    state: dict[str, Any],
    finding_id: str,
    fingerprint: str,
    source_review_id: str,
    source_phase: str,
    severity: str,
    summary: str,
    *,
    file: str | None = None,
    line: int | None = None,
) -> None:
    state["findings"][finding_id] = {
        "fingerprint": fingerprint,
        "source_review_id": source_review_id,
        "source_phase": source_phase,
        "severity": severity,
        "summary": summary,
        "file": file,
        "line": line,
        "status": "open",
        "rationale": None,
        "addressed_commit": None,
        "verifying_review_id": None,
        "deferred_until_phase": None,
        "human_notes": None,
    }


def set_finding_status(
    state: dict[str, Any],
    finding_id: str,
    new_status: str,
    *,
    verifying_review_id: str | None = None,
    deferred_until_phase: str | None = None,
    rationale: str | None = None,
    addressed_commit: str | None = None,
) -> None:
    if new_status not in VALID_FINDING_STATUSES:
        raise ValueError(
            f"finding status must be one of {sorted(VALID_FINDING_STATUSES)}, got {new_status!r}"
        )
    if new_status == "verified" and not verifying_review_id:
        raise ValueError("status=verified requires verifying_review_id")
    if new_status == "deferred_until_phase" and not deferred_until_phase:
        raise ValueError("status=deferred_until_phase requires deferred_until_phase")
    if new_status == "wontfix_with_rationale" and not rationale:
        raise ValueError("status=wontfix_with_rationale requires rationale")
    f = state["findings"][finding_id]
    f["status"] = new_status
    if verifying_review_id is not None:
        f["verifying_review_id"] = verifying_review_id
    if deferred_until_phase is not None:
        f["deferred_until_phase"] = deferred_until_phase
    if rationale is not None:
        f["rationale"] = rationale
    if addressed_commit is not None:
        f["addressed_commit"] = addressed_commit


# ---------------------------------------------------------------------------
# Project-level settings
# ---------------------------------------------------------------------------


def set_buffer_depth(state: dict[str, Any], depth: int, *, reason: str | None = None) -> None:
    if depth not in (0, 1):
        raise ValueError("buffer_depth must be 0 or 1")
    if depth == 1 and not reason:
        raise ValueError("buffer_depth=1 requires buffer_depth_override_reason")
    state["buffer_depth"] = depth
    state["buffer_depth_override_reason"] = reason if depth == 1 else None
