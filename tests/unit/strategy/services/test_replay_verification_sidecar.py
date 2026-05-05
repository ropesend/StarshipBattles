"""PROJ-354B Phase 2.1 — Sidecar schema + atomic writer tests."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from game.strategy.services.replay_verification_sidecar import (
    REPLAY_VERIFICATION_SCHEMA_VERSION,
    VerificationSidecar,
    VerificationSource,
    VerificationStatus,
    read_verification_sidecar,
    sidecar_path_for_replay,
    write_verification_sidecar,
)


def _make_sidecar(
    replay_id: str = "abc123",
    status: VerificationStatus = VerificationStatus.PASSED,
) -> VerificationSidecar:
    return VerificationSidecar(
        replay_id=replay_id,
        schema_version=REPLAY_VERIFICATION_SCHEMA_VERSION,
        status=status.name,
        source=VerificationSource.BACKGROUND.name,
        verified_at="2026-05-04T12:00:00+00:00",
        duration_ms=42,
        diff=None,
        error=None,
    )


class TestSidecarPath:
    def test_path_format(self, tmp_path: Path):
        path = sidecar_path_for_replay(tmp_path, "abc123")
        assert path.name == "replay_abc123.verification.json"
        assert path.parent == tmp_path

    def test_path_does_not_create_dir(self, tmp_path: Path):
        # Pure helper — must not have side effects.
        sub = tmp_path / "does-not-exist"
        path = sidecar_path_for_replay(sub, "abc")
        assert not sub.exists()
        assert path.parent == sub


class TestWriteSidecar:
    def test_round_trip_write_read(self, tmp_path: Path):
        sidecar = _make_sidecar()
        path = write_verification_sidecar(tmp_path, sidecar)
        assert path is not None
        assert path.exists()

        loaded = read_verification_sidecar(tmp_path, sidecar.replay_id)
        assert loaded is not None
        assert loaded.replay_id == sidecar.replay_id
        assert loaded.status == sidecar.status
        assert loaded.source == sidecar.source
        assert loaded.duration_ms == 42

    def test_atomic_write_leaves_no_temp_file(self, tmp_path: Path):
        sidecar = _make_sidecar()
        write_verification_sidecar(tmp_path, sidecar)
        leftover = list(tmp_path.glob("*.tmp"))
        assert leftover == []

    def test_writes_json_payload(self, tmp_path: Path):
        sidecar = _make_sidecar()
        path = write_verification_sidecar(tmp_path, sidecar)
        assert path is not None
        data = json.loads(path.read_text())
        assert data["replay_id"] == "abc123"
        assert data["schema_version"] == REPLAY_VERIFICATION_SCHEMA_VERSION
        assert data["status"] == "PASSED"
        assert data["source"] == "BACKGROUND"

    def test_diff_serialized(self, tmp_path: Path):
        sidecar = VerificationSidecar(
            replay_id="r1",
            schema_version=REPLAY_VERIFICATION_SCHEMA_VERSION,
            status=VerificationStatus.FAILED.name,
            source=VerificationSource.BACKGROUND.name,
            verified_at="2026-05-04T12:00:00+00:00",
            duration_ms=10,
            diff=[
                {"path": ["teams", 0, "name"], "expected": "A", "actual": "B"},
            ],
            error=None,
        )
        path = write_verification_sidecar(tmp_path, sidecar)
        assert path is not None
        loaded = read_verification_sidecar(tmp_path, "r1")
        assert loaded is not None
        assert loaded.diff == [
            {"path": ["teams", 0, "name"], "expected": "A", "actual": "B"},
        ]

    def test_error_serialized(self, tmp_path: Path):
        sidecar = VerificationSidecar(
            replay_id="r2",
            schema_version=REPLAY_VERIFICATION_SCHEMA_VERSION,
            status=VerificationStatus.ERROR.name,
            source=VerificationSource.BACKGROUND.name,
            verified_at="2026-05-04T12:00:00+00:00",
            duration_ms=5,
            diff=None,
            error={"type": "ValueError", "message": "boom"},
        )
        write_verification_sidecar(tmp_path, sidecar)
        loaded = read_verification_sidecar(tmp_path, "r2")
        assert loaded is not None
        assert loaded.error == {"type": "ValueError", "message": "boom"}


class TestReadSidecar:
    def test_missing_returns_none(self, tmp_path: Path):
        assert read_verification_sidecar(tmp_path, "nope") is None

    def test_corrupt_returns_none(self, tmp_path: Path):
        path = sidecar_path_for_replay(tmp_path, "bad")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{not valid json")
        assert read_verification_sidecar(tmp_path, "bad") is None

    def test_missing_required_fields_returns_none(self, tmp_path: Path):
        path = sidecar_path_for_replay(tmp_path, "incomplete")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"replay_id": "incomplete"}))
        # Missing required fields → still parseable as VerificationSidecar?
        # Implementation must be tolerant: return None on schema mismatch.
        result = read_verification_sidecar(tmp_path, "incomplete")
        assert result is None
