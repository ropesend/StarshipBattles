"""Tests for the discovered-issues logger and triage helpers.

These tests run the scripts as subprocesses to exercise the CLIs end-to-end,
matching the pattern in `test_create_review_request.py`.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
LOG_SCRIPT = HERE / "log_discovered_issue.py"
TRIAGE_SCRIPT = HERE / "triage_discovered_issues.py"


@pytest.fixture
def fake_repo(tmp_path: Path) -> Path:
    """A throwaway repo root with AGENTS.md and a sample source file."""
    (tmp_path / "AGENTS.md").write_text("fake\n", encoding="utf-8")
    src = tmp_path / "game" / "combat" / "resolver.py"
    src.parent.mkdir(parents=True)
    src.write_text(
        "def apply_damage(unit, dmg):\n"
        "    unit.hp -= dmg\n"
        "    is_dead = unit.hp <= 0\n"
        "    if is_dead:\n"
        "        unit.alive = False\n"
        "    if unit.hp <= 0 and not is_dead:\n"
        "        raise RuntimeError('unreachable')\n"
        "    return unit\n",
        encoding="utf-8",
    )
    return tmp_path


def _log(repo: Path, **kwargs: str) -> subprocess.CompletedProcess[str]:
    args = [sys.executable, str(LOG_SCRIPT), "--repo-root", str(repo)]
    for k, v in kwargs.items():
        args += [f"--{k.replace('_', '-')}", v]
    return subprocess.run(args, capture_output=True, text=True, timeout=15)


def _triage(repo: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TRIAGE_SCRIPT), "--repo-root", str(repo), *extra],
        capture_output=True, text=True, timeout=15,
    )


def _read_log(repo: Path) -> list[dict[str, object]]:
    log = repo / "AgentCoordination" / "discovered_issues" / "log.jsonl"
    if not log.exists():
        return []
    out = []
    for raw in log.read_text(encoding="utf-8").splitlines():
        if raw.strip():
            out.append(json.loads(raw))
    return out


def test_log_appends_entry_with_snippet(fake_repo: Path) -> None:
    r = _log(
        fake_repo,
        agent="claude",
        source_task="PROJ-test",
        file="game/combat/resolver.py",
        line="6",
        category="bug",
        severity="medium",
        description="not is_dead branch is unreachable.",
        suggested_action="Drop the redundant check.",
    )
    assert r.returncode == 0, r.stderr
    eid = r.stdout.strip()
    assert eid.startswith("DI-") and eid.endswith("-001")
    entries = _read_log(fake_repo)
    assert len(entries) == 1
    e = entries[0]
    assert e["id"] == eid
    assert e["agent"] == "claude"
    assert e["file"] == "game/combat/resolver.py"
    assert e["line"] == 6
    assert e["category"] == "bug"
    assert "not is_dead" in e["code_snippet"]
    assert e["code_snippet"].count("\n") == 2  # 3-line excerpt -> 2 newlines


def test_log_rejects_missing_file(fake_repo: Path) -> None:
    r = _log(
        fake_repo,
        agent="claude",
        source_task="x",
        file="game/does/not/exist.py",
        line="1",
        category="bug",
        description="...",
    )
    assert r.returncode != 0
    assert "does not exist" in r.stderr


def test_log_rejects_out_of_range_line(fake_repo: Path) -> None:
    r = _log(
        fake_repo,
        agent="claude",
        source_task="x",
        file="game/combat/resolver.py",
        line="9999",
        category="bug",
        description="...",
    )
    assert r.returncode != 0
    assert "out of range" in r.stderr


def test_log_rejects_unknown_agent(fake_repo: Path) -> None:
    r = _log(
        fake_repo,
        agent="hal9000",
        source_task="x",
        file="game/combat/resolver.py",
        line="1",
        category="bug",
        description="...",
    )
    assert r.returncode != 0


def test_log_rejects_unknown_category(fake_repo: Path) -> None:
    r = _log(
        fake_repo,
        agent="claude",
        source_task="x",
        file="game/combat/resolver.py",
        line="1",
        category="vibes",
        description="...",
    )
    assert r.returncode != 0


def test_log_assigns_monotonic_ids_within_day(fake_repo: Path) -> None:
    ids = []
    for i in range(3):
        r = _log(
            fake_repo,
            agent="claude",
            source_task=f"task-{i}",
            file="game/combat/resolver.py",
            line="2",
            category="bug",
            description=f"entry {i}",
        )
        assert r.returncode == 0, r.stderr
        ids.append(r.stdout.strip())
    suffixes = [int(eid.rsplit("-", 1)[-1]) for eid in ids]
    assert suffixes == [1, 2, 3]


def test_triage_match_exact(fake_repo: Path) -> None:
    _log(
        fake_repo,
        agent="claude", source_task="t",
        file="game/combat/resolver.py", line="6",
        category="bug", description="x",
    )
    r = _triage(fake_repo, "--format", "jsonl")
    assert r.returncode == 0, r.stderr
    out = [json.loads(l) for l in r.stdout.splitlines() if l.strip()]
    assert len(out) == 1
    assert out[0]["_verdict"] == "match-exact"


def test_triage_match_drifted_when_lines_added(fake_repo: Path) -> None:
    _log(
        fake_repo,
        agent="claude", source_task="t",
        file="game/combat/resolver.py", line="6",
        category="bug", description="x",
    )
    src = fake_repo / "game" / "combat" / "resolver.py"
    text = src.read_text(encoding="utf-8")
    src.write_text("# new top comment\n# another\n# and another\n" + text, encoding="utf-8")
    r = _triage(fake_repo, "--format", "jsonl")
    assert r.returncode == 0, r.stderr
    out = [json.loads(l) for l in r.stdout.splitlines() if l.strip()]
    assert out[0]["_verdict"] == "match-drifted"
    assert out[0]["_current_line"] == 9


def test_triage_snippet_gone_when_code_removed(fake_repo: Path) -> None:
    _log(
        fake_repo,
        agent="claude", source_task="t",
        file="game/combat/resolver.py", line="6",
        category="bug", description="x",
    )
    src = fake_repo / "game" / "combat" / "resolver.py"
    src.write_text("def apply_damage(unit, dmg):\n    return unit\n", encoding="utf-8")
    r = _triage(fake_repo, "--format", "jsonl")
    out = [json.loads(l) for l in r.stdout.splitlines() if l.strip()]
    assert out[0]["_verdict"] == "snippet-gone"


def test_triage_file_gone(fake_repo: Path) -> None:
    _log(
        fake_repo,
        agent="claude", source_task="t",
        file="game/combat/resolver.py", line="6",
        category="bug", description="x",
    )
    (fake_repo / "game" / "combat" / "resolver.py").unlink()
    r = _triage(fake_repo, "--format", "jsonl")
    out = [json.loads(l) for l in r.stdout.splitlines() if l.strip()]
    assert out[0]["_verdict"] == "file-gone"


def test_triage_filters(fake_repo: Path) -> None:
    _log(
        fake_repo, agent="claude", source_task="a",
        file="game/combat/resolver.py", line="2",
        category="bug", severity="low", description="one",
    )
    _log(
        fake_repo, agent="codex", source_task="b",
        file="game/combat/resolver.py", line="3",
        category="perf", severity="high", description="two",
    )
    r = _triage(fake_repo, "--agent", "codex", "--format", "jsonl")
    out = [json.loads(l) for l in r.stdout.splitlines() if l.strip()]
    assert len(out) == 1
    assert out[0]["agent"] == "codex"

    r = _triage(fake_repo, "--severity", "high", "--format", "jsonl")
    out = [json.loads(l) for l in r.stdout.splitlines() if l.strip()]
    assert len(out) == 1
    assert out[0]["severity"] == "high"


def test_prune_removes_listed_entries(fake_repo: Path) -> None:
    ids = []
    for i in range(3):
        r = _log(
            fake_repo, agent="claude", source_task=f"t{i}",
            file="game/combat/resolver.py", line="2",
            category="bug", description=f"e{i}",
        )
        ids.append(r.stdout.strip())
    r = _triage(fake_repo, "--prune", ids[0], ids[2])
    assert r.returncode == 0, r.stderr
    remaining = _read_log(fake_repo)
    assert [e["id"] for e in remaining] == [ids[1]]


def test_prune_reports_missing_ids(fake_repo: Path) -> None:
    _log(
        fake_repo, agent="claude", source_task="t",
        file="game/combat/resolver.py", line="2",
        category="bug", description="e",
    )
    r = _triage(fake_repo, "--prune", "DI-9999-12-31-001")
    assert r.returncode != 0
    assert "not found" in r.stderr


def test_log_file_outside_repo_rejected(fake_repo: Path, tmp_path_factory: pytest.TempPathFactory) -> None:
    other_dir = tmp_path_factory.mktemp("outside_repo")
    elsewhere = other_dir / "outside.py"
    elsewhere.write_text("x = 1\n", encoding="utf-8")
    r = _log(
        fake_repo, agent="claude", source_task="t",
        file=str(elsewhere), line="1",
        category="bug", description="...",
    )
    assert r.returncode != 0
    assert "outside repo root" in r.stderr


def test_log_supports_absolute_path_inside_repo(fake_repo: Path) -> None:
    abs_path = (fake_repo / "game" / "combat" / "resolver.py").resolve()
    r = _log(
        fake_repo, agent="claude", source_task="t",
        file=str(abs_path), line="2",
        category="bug", description="absolute",
    )
    assert r.returncode == 0, r.stderr
    entries = _read_log(fake_repo)
    assert entries[-1]["file"] == "game/combat/resolver.py"
