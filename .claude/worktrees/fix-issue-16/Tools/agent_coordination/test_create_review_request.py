"""Tests for create_review_request.py — payload-file interface."""
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent / "create_review_request.py"


def run_create(payload_file: Path, cwd: Path, pending_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--payload-file", str(payload_file), "--pending-dir", str(pending_dir)],
        cwd=str(cwd), capture_output=True, text=True, timeout=10,
    )


@pytest.fixture
def tmp_pending(tmp_path: Path) -> Path:
    pending = tmp_path / "pending"
    pending.mkdir(parents=True)
    return pending


def _write_payload(payload_dir: Path, **kwargs: object) -> Path:
    payload_path = payload_dir / "payload.json"
    payload_path.write_text(json.dumps(kwargs, indent=2))
    return payload_path


def _request_content(pending_dir: Path, stdout: str) -> str:
    request_id = stdout.strip()
    return (pending_dir / f"{request_id}.md").read_text(encoding="utf-8")


def test_multiline_fields_preserved(tmp_path: Path) -> None:
    pending = tmp_path / "pending"
    pending.mkdir()
    scope = "game/simulation/combat/ — all files\nC:\\Windows\\Paths\\test.py — Windows path\n- bullet\n- list"
    instructions = "Check `backtick` code and \"quotes\"\n1. Step one\n2. Step two"
    payload_file = _write_payload(
        tmp_path, type="code", title="Multiline Test", scope=scope, instructions=instructions,
        context="This is context\nwith newlines",
    )
    r = run_create(payload_file, cwd=tmp_path, pending_dir=pending)
    assert r.returncode == 0, r.stderr
    content = _request_content(pending, r.stdout)
    assert "game/simulation/combat/" in content
    assert "C:\\Windows\\Paths" in content
    assert "`backtick`" in content
    assert '"quotes"' in content
    assert "with newlines" in content


def test_id_format_and_uniqueness(tmp_path: Path) -> None:
    pending = tmp_path / "pending"
    pending.mkdir()
    ids = set()
    for _ in range(10):
        payload_file = _write_payload(tmp_path, type="general", title="T", scope="x", instructions="y")
        r = run_create(payload_file, cwd=tmp_path, pending_dir=pending)
        assert r.returncode == 0
        rid = r.stdout.strip()
        assert re.match(r"^req_\d{8}_\d{6}_[0-9a-f]{6}$", rid), f"bad id: {rid}"
        ids.add(rid)
    assert len(ids) == 10


def test_no_leftover_temp_files(tmp_path: Path) -> None:
    pending = tmp_path / "pending"
    pending.mkdir()
    payload_file = _write_payload(tmp_path, type="general", title="T", scope="x", instructions="y")
    r = run_create(payload_file, cwd=tmp_path, pending_dir=pending)
    assert r.returncode == 0
    assert not list(pending.glob(".tmp_*.md"))


def test_invalid_type_rejected(tmp_path: Path) -> None:
    # Mirror real layout: AgentCoordination/opencodereview/<system_root>
    pending_parent = tmp_path / "AgentCoordination" / "opencodereview"
    pending = pending_parent / "pending_review_requests"
    pending.mkdir(parents=True)
    payload_file = _write_payload(tmp_path, type="bogus", title="T", scope="x", instructions="y")
    r = run_create(payload_file, cwd=tmp_path, pending_dir=pending)
    assert r.returncode != 0
    assert not list(pending.glob("req_*.md"))
    # Failed payload MUST be saved under the test temp tree (not the real repo).
    expected_failed_dir = pending_parent / "local" / "failed_payloads"
    failed = list(expected_failed_dir.glob("*.json"))
    assert failed, f"failed payload not saved at {expected_failed_dir}"
    assert "invalid_type" in failed[0].name


def test_malformed_json_rejected(tmp_path: Path) -> None:
    pending = tmp_path / "pending"
    pending.mkdir()
    payload_file = tmp_path / "bad.json"
    payload_file.write_text("{not json")
    r = run_create(payload_file, cwd=tmp_path, pending_dir=pending)
    assert r.returncode != 0
    assert not list(pending.glob("req_*.md"))


def test_parent_field_emitted(tmp_path: Path) -> None:
    pending = tmp_path / "pending"
    pending.mkdir()
    payload_file = _write_payload(
        tmp_path, type="code", title="Follow-up", scope="x", instructions="y",
        parent="req_abc_123",
    )
    r = run_create(payload_file, cwd=tmp_path, pending_dir=pending)
    assert r.returncode == 0
    content = _request_content(pending, r.stdout)
    assert "**Parent:** req_abc_123" in content


def test_no_parent_when_absent(tmp_path: Path) -> None:
    pending = tmp_path / "pending"
    pending.mkdir()
    payload_file = _write_payload(tmp_path, type="general", title="T", scope="x", instructions="y")
    r = run_create(payload_file, cwd=tmp_path, pending_dir=pending)
    assert r.returncode == 0
    content = _request_content(pending, r.stdout)
    assert "**Parent:**" not in content


def test_no_per_field_flags(tmp_path: Path) -> None:
    """Regression guard: per-field flags must not exist after v2.4 rewrite."""
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--scope", "x", "--instructions", "y"],
        capture_output=True, text=True, timeout=5,
    )
    assert r.returncode != 0  # argparse should reject unknown flags
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--scope-stdin", "--instructions-stdin"],
        capture_output=True, text=True, timeout=5,
    )
    assert r.returncode != 0
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--payload-stdin"],
        capture_output=True, text=True, timeout=5,
    )
    assert r.returncode != 0


def test_required_fields_rejected(tmp_path: Path) -> None:
    """Missing required fields produce non-zero exit."""
    pending = tmp_path / "pending"
    pending.mkdir()
    payload_file = _write_payload(tmp_path, type="code")  # missing title, scope, instructions
    r = run_create(payload_file, cwd=tmp_path, pending_dir=pending)
    assert r.returncode != 0
    assert not list(pending.glob("req_*.md"))
