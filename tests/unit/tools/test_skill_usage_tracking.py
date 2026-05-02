from __future__ import annotations

import json
from pathlib import Path

from Tools.agent_coordination import log_skill_usage
from Tools.agent_coordination import summarize_skill_usage


def test_log_creates_install_id_file_on_first_use(tmp_path: Path) -> None:
    rc = log_skill_usage.main([
        "--repo-root", str(tmp_path),
        "--agent", "claude",
        "--skill", "claude-proj-start",
    ])
    assert rc == 0
    install_id_path = tmp_path / "AgentCoordination" / "local" / "install_id.json"
    assert install_id_path.exists()
    data = json.loads(install_id_path.read_text(encoding="utf-8"))
    assert "install_id" in data
    assert isinstance(data["install_id"], str)
    assert len(data["install_id"]) >= 8


def test_log_appends_to_per_install_file(tmp_path: Path) -> None:
    rc = log_skill_usage.main([
        "--repo-root", str(tmp_path),
        "--agent", "claude",
        "--skill", "claude-proj-start",
    ])
    assert rc == 0

    install_id = json.loads(
        (tmp_path / "AgentCoordination" / "local" / "install_id.json").read_text(encoding="utf-8")
    )["install_id"]
    by_install = tmp_path / "AgentCoordination" / "generated" / "skill_usage" / "by_install" / f"{install_id}.json"
    assert by_install.exists()
    payload = json.loads(by_install.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["install_id"] == install_id
    assert payload["skills"]["claude-proj-start"]["count"] == 1
    assert payload["skills"]["claude-proj-start"]["last_used"]


def test_log_increments_existing_skill_count(tmp_path: Path) -> None:
    for _ in range(3):
        rc = log_skill_usage.main([
            "--repo-root", str(tmp_path),
            "--agent", "claude",
            "--skill", "claude-proj-start",
        ])
        assert rc == 0
    install_id = json.loads(
        (tmp_path / "AgentCoordination" / "local" / "install_id.json").read_text(encoding="utf-8")
    )["install_id"]
    by_install = tmp_path / "AgentCoordination" / "generated" / "skill_usage" / "by_install" / f"{install_id}.json"
    payload = json.loads(by_install.read_text(encoding="utf-8"))
    assert payload["skills"]["claude-proj-start"]["count"] == 3


def test_log_records_separate_skills(tmp_path: Path) -> None:
    log_skill_usage.main([
        "--repo-root", str(tmp_path),
        "--agent", "claude",
        "--skill", "claude-proj-start",
    ])
    log_skill_usage.main([
        "--repo-root", str(tmp_path),
        "--agent", "claude",
        "--skill", "claude-ticket-work",
    ])
    install_id = json.loads(
        (tmp_path / "AgentCoordination" / "local" / "install_id.json").read_text(encoding="utf-8")
    )["install_id"]
    by_install = tmp_path / "AgentCoordination" / "generated" / "skill_usage" / "by_install" / f"{install_id}.json"
    payload = json.loads(by_install.read_text(encoding="utf-8"))
    assert set(payload["skills"].keys()) == {"claude-proj-start", "claude-ticket-work"}


def test_log_rejects_invalid_agent(tmp_path: Path) -> None:
    rc = log_skill_usage.main([
        "--repo-root", str(tmp_path),
        "--agent", "unknown-agent",
        "--skill", "claude-proj-start",
    ])
    assert rc != 0


def test_log_rejects_invalid_skill_name(tmp_path: Path) -> None:
    rc = log_skill_usage.main([
        "--repo-root", str(tmp_path),
        "--agent", "claude",
        "--skill", "INVALID NAME",
    ])
    assert rc != 0


# ---------------------------------------------------------------------------
# Summarize
# ---------------------------------------------------------------------------


def _write_install_payload(repo_root: Path, install_id: str, skills: dict[str, int]) -> None:
    by_install = repo_root / "AgentCoordination" / "generated" / "skill_usage" / "by_install"
    by_install.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "install_id": install_id,
        "skills": {
            name: {"count": count, "last_used": "2026-04-29T00:00:00Z"}
            for name, count in skills.items()
        },
    }
    (by_install / f"{install_id}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_summarize_aggregates_across_installs(tmp_path: Path) -> None:
    _write_install_payload(tmp_path, "install-a", {"claude-proj-start": 3, "claude-ticket-work": 1})
    _write_install_payload(tmp_path, "install-b", {"claude-proj-start": 2})

    rc = summarize_skill_usage.main(["--repo-root", str(tmp_path)])
    assert rc == 0

    summary_path = tmp_path / "AgentCoordination" / "generated" / "skill_usage" / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["schema_version"] == 1
    assert summary["skills"]["claude-proj-start"]["total_count"] == 5
    assert summary["skills"]["claude-proj-start"]["by_install"]["install-a"] == 3
    assert summary["skills"]["claude-proj-start"]["by_install"]["install-b"] == 2
    assert summary["skills"]["claude-ticket-work"]["total_count"] == 1


def test_summarize_handles_no_install_files(tmp_path: Path) -> None:
    rc = summarize_skill_usage.main(["--repo-root", str(tmp_path)])
    assert rc == 0
    summary = json.loads(
        (tmp_path / "AgentCoordination" / "generated" / "skill_usage" / "summary.json")
        .read_text(encoding="utf-8")
    )
    assert summary["schema_version"] == 1
    assert summary["skills"] == {}


def test_summarize_warns_on_malformed_install_file(tmp_path: Path) -> None:
    by_install = tmp_path / "AgentCoordination" / "generated" / "skill_usage" / "by_install"
    by_install.mkdir(parents=True)
    (by_install / "bad.json").write_text("{not valid", encoding="utf-8")
    rc = summarize_skill_usage.main(["--repo-root", str(tmp_path)])
    # Malformed file is skipped with a warning; summary still produced.
    assert rc == 0
