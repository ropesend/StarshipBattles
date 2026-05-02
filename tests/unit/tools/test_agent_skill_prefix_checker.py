from __future__ import annotations

from pathlib import Path

import pytest

from Tools.agent_coordination import check_skill_prefixes as checker


def _write_skill(root: Path, surface: str, name: str) -> None:
    skill_dir = root / surface / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: t\n---\n\n# {name}\n",
        encoding="utf-8",
    )


def test_checker_passes_when_every_skill_has_expected_prefix(tmp_path: Path) -> None:
    _write_skill(tmp_path, ".claude/skills", "claude-foo")
    _write_skill(tmp_path, ".agent/skills", "anti-bar")
    _write_skill(tmp_path, ".agents/skills", "codex-baz")
    _write_skill(tmp_path, ".opencode/skills", "ocode-quux")

    rc, findings = checker.run(tmp_path)
    assert rc == 0
    assert findings == []


def test_checker_fails_on_unprefixed_claude_skill(tmp_path: Path) -> None:
    _write_skill(tmp_path, ".claude/skills", "proj-start")
    rc, findings = checker.run(tmp_path)
    assert rc == 1
    assert any("claude-" in f["expected_prefix"] for f in findings)
    assert any(f["surface_path"] == ".claude/skills" for f in findings)


def test_checker_fails_on_unprefixed_anti_skill(tmp_path: Path) -> None:
    _write_skill(tmp_path, ".agent/skills", "ticket-work")
    rc, findings = checker.run(tmp_path)
    assert rc == 1
    assert any(f["expected_prefix"] == "anti-" for f in findings)


def test_checker_fails_on_unprefixed_ocode_skill(tmp_path: Path) -> None:
    _write_skill(tmp_path, ".opencode/skills", "audit-shrink")
    rc, findings = checker.run(tmp_path)
    assert rc == 1
    assert any(f["expected_prefix"] == "ocode-" for f in findings)


def test_checker_main_exits_with_code(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _write_skill(tmp_path, ".claude/skills", "no-prefix")
    rc = checker.main(["--repo-root", str(tmp_path)])
    assert rc == 1
    captured = capsys.readouterr()
    assert "no-prefix" in captured.out


def test_checker_passes_with_empty_repo(tmp_path: Path) -> None:
    rc, findings = checker.run(tmp_path)
    assert rc == 0
    assert findings == []


def test_checker_allows_shared_prefix(tmp_path: Path) -> None:
    # `shared-*` is the reserved cross-agent prefix; it should not fail prefix
    # compliance for the surface it lives in.
    _write_skill(tmp_path, ".claude/skills", "shared-helper")
    rc, findings = checker.run(tmp_path)
    assert rc == 0
    assert findings == []
