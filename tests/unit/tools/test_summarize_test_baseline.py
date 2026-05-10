from __future__ import annotations

import json
from pathlib import Path

from Tools.agent_coordination import summarize_test_baseline as summarizer


def _write_canonical_baseline(repo_root: Path) -> None:
    path = repo_root / "AgentCoordination" / "generated" / "test_baseline.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({
            "schema_version": 2,
            "command": "python Tools/test_sharded/test_sharded.py",
            "total": 16063,
            "passed": 16060,
            "failed": 0,
            "errors": 0,
            "skipped": 3,
            "baseline_changed_at": "2026-04-29T00:00:00Z",
        }),
        encoding="utf-8",
    )


def _write_verification(
    repo_root: Path,
    install_id: str,
    *,
    verified_at: str,
    git_sha: str,
) -> None:
    by_install = repo_root / "AgentCoordination" / "generated" / "test_baseline" / "by_install"
    by_install.mkdir(parents=True, exist_ok=True)
    (by_install / f"{install_id}.json").write_text(
        json.dumps({
            "schema_version": 1,
            "install_id": install_id,
            "command": "python Tools/test_sharded/test_sharded.py",
            "total": 16063,
            "passed": 16060,
            "failed": 0,
            "errors": 0,
            "skipped": 3,
            "verified_at": verified_at,
            "git_sha": git_sha,
        }),
        encoding="utf-8",
    )


def test_build_summary_combines_canonical_counts_and_latest_verification(tmp_path: Path) -> None:
    _write_canonical_baseline(tmp_path)
    _write_verification(
        tmp_path,
        "older-install",
        verified_at="2026-04-29T00:00:00Z",
        git_sha="old-sha",
    )
    _write_verification(
        tmp_path,
        "newer-install",
        verified_at="2026-05-01T00:00:00Z",
        git_sha="new-sha",
    )

    summary = summarizer.build_summary(tmp_path)

    assert summary["baseline"]["total"] == 16063
    assert summary["verification"]["last_verified_at"] == "2026-05-01T00:00:00Z"
    assert summary["verification"]["last_verified_install_id"] == "newer-install"
    assert summary["verification"]["last_verified_git_sha"] == "new-sha"
    assert sorted(summary["verification"]["by_install"]) == ["newer-install", "older-install"]


def test_write_summary_persists_derived_summary_file(tmp_path: Path) -> None:
    _write_canonical_baseline(tmp_path)
    _write_verification(
        tmp_path,
        "local-install",
        verified_at="2026-05-01T00:00:00Z",
        git_sha="new-sha",
    )

    summarizer.write_summary(tmp_path)

    summary_path = tmp_path / "AgentCoordination" / "generated" / "test_baseline" / "summary.json"
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    assert data["baseline"]["passed"] == 16060
    assert data["verification"]["by_install"]["local-install"]["git_sha"] == "new-sha"
