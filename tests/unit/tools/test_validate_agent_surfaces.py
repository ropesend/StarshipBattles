from __future__ import annotations

import json
from pathlib import Path

import pytest

from Tools.agent_coordination import validate_agent_surfaces as validator


# Helper -------------------------------------------------------------------


def _make_repo(
    tmp_path: Path,
    *,
    agents_md: str = "# AGENTS\n",
    claude_md: str = "# CLAUDE\n",
    codex_md: str = "# CODEX\n",
    skills: dict[str, dict[str, dict[str, str]]] | None = None,
    opencode: dict | None = None,
    settings_json: dict | None = None,
    settings_local: dict | None = None,
    baseline: dict | None = None,
    inventory: dict | None = None,
    stale_workflows: bool = False,
    stale_migration: bool = False,
) -> Path:
    """Build a minimal fake repo. `skills` maps surface_path -> {dir_name -> frontmatter}."""
    (tmp_path / "AGENTS.md").write_text(agents_md, encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text(claude_md, encoding="utf-8")
    (tmp_path / ".agents").mkdir(exist_ok=True)
    (tmp_path / ".agents" / "CODEX.md").write_text(codex_md, encoding="utf-8")

    skills = skills or {}
    for surface_path, surface_skills in skills.items():
        for name, frontmatter in surface_skills.items():
            skill_dir = tmp_path / surface_path / name
            skill_dir.mkdir(parents=True)
            lines = ["---"]
            for key, value in frontmatter.items():
                lines.append(f"{key}: {value}")
            lines.extend(["---", "", "# body"])
            (skill_dir / "SKILL.md").write_text("\n".join(lines), encoding="utf-8")

    if opencode is not None:
        (tmp_path / "opencode.json").write_text(json.dumps(opencode), encoding="utf-8")
    if settings_json is not None:
        (tmp_path / ".claude").mkdir(exist_ok=True)
        (tmp_path / ".claude" / "settings.json").write_text(json.dumps(settings_json), encoding="utf-8")
    if settings_local is not None:
        (tmp_path / ".claude").mkdir(exist_ok=True)
        (tmp_path / ".claude" / "settings.local.json").write_text(json.dumps(settings_local), encoding="utf-8")
    if baseline is not None:
        baseline_path = tmp_path / "AgentCoordination" / "generated" / "test_baseline.json"
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        baseline_path.write_text(json.dumps(baseline), encoding="utf-8")
    if inventory is not None:
        inv_path = tmp_path / "AgentCoordination" / "generated" / "agent_surface_inventory.json"
        inv_path.parent.mkdir(parents=True, exist_ok=True)
        inv_path.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if stale_workflows:
        wf = tmp_path / ".agent" / "workflows"
        wf.mkdir(parents=True, exist_ok=True)
        (wf / "run-tests.md").write_text("python -m unittest discover\n", encoding="utf-8")
    if stale_migration:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir(parents=True, exist_ok=True)
        (agent_dir / "MIGRATION_PROGRESS.md").write_text("legacy", encoding="utf-8")

    return tmp_path


# ---------------------------------------------------------------------------
# Test baseline validity
# ---------------------------------------------------------------------------


def _good_baseline() -> dict:
    return {
        "schema_version": 1,
        "command": "python Tools/test_sharded/test_sharded.py",
        "total": 16063,
        "passed": 16060,
        "failed": 0,
        "errors": 0,
        "skipped": 3,
        "baseline_changed_at": "2026-04-29T00:00:00Z",
        "verified_at": "2026-04-29T00:00:00Z",
        "git_sha": "abc1234",
    }


def test_baseline_validity_passes_on_well_formed_file(tmp_path: Path) -> None:
    _make_repo(tmp_path, baseline=_good_baseline())
    findings = validator.check_test_baseline_validity(tmp_path)
    assert findings == []


def test_baseline_validity_fails_when_counts_do_not_add_up(tmp_path: Path) -> None:
    bad = _good_baseline()
    bad["passed"] = 999  # 999 + 0 + 0 + 3 != 16063
    _make_repo(tmp_path, baseline=bad)
    findings = validator.check_test_baseline_validity(tmp_path)
    assert any(f.rule == "baseline.counts_do_not_sum" for f in findings)


def test_baseline_validity_fails_on_missing_schema_version(tmp_path: Path) -> None:
    bad = _good_baseline()
    del bad["schema_version"]
    _make_repo(tmp_path, baseline=bad)
    findings = validator.check_test_baseline_validity(tmp_path)
    assert any(f.rule == "baseline.schema_version_missing" for f in findings)


def test_baseline_validity_fails_when_file_missing(tmp_path: Path) -> None:
    _make_repo(tmp_path)
    findings = validator.check_test_baseline_validity(tmp_path)
    assert any(f.rule == "baseline.missing" for f in findings)


def test_baseline_validity_fails_on_implausibly_low_total(tmp_path: Path) -> None:
    bad = _good_baseline()
    bad["total"] = 5
    bad["passed"] = 2
    bad["skipped"] = 3
    _make_repo(tmp_path, baseline=bad)
    findings = validator.check_test_baseline_validity(tmp_path)
    assert any(f.rule == "baseline.implausible_count" for f in findings)


# ---------------------------------------------------------------------------
# Inventory freshness
# ---------------------------------------------------------------------------


def test_inventory_freshness_passes_when_committed_matches_fresh(tmp_path: Path) -> None:
    skills = {".agents/skills": {"codex-foo": {"name": "codex-foo", "description": "x"}}}
    _make_repo(tmp_path, skills=skills)
    # First produce a fresh inventory and commit it.
    from Tools.agent_coordination.inventory_agent_surfaces import build_inventory
    fresh = build_inventory(tmp_path)
    inv_path = tmp_path / "AgentCoordination" / "generated" / "agent_surface_inventory.json"
    inv_path.parent.mkdir(parents=True, exist_ok=True)
    inv_path.write_text(json.dumps(fresh, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    findings = validator.check_inventory_freshness(tmp_path)
    assert findings == []


def test_inventory_freshness_fails_when_committed_is_stale(tmp_path: Path) -> None:
    skills = {".agents/skills": {"codex-foo": {"name": "codex-foo", "description": "x"}}}
    _make_repo(tmp_path, skills=skills, inventory={"schema_version": 1, "surfaces": [], "stale_references": [], "warnings": []})
    findings = validator.check_inventory_freshness(tmp_path)
    assert any(f.rule == "inventory.stale" for f in findings)


def test_inventory_freshness_fails_when_committed_missing(tmp_path: Path) -> None:
    _make_repo(tmp_path)
    findings = validator.check_inventory_freshness(tmp_path)
    assert any(f.rule == "inventory.missing" for f in findings)


# ---------------------------------------------------------------------------
# Prefix compliance + agent skills spec
# ---------------------------------------------------------------------------


def test_prefix_compliance_passes_on_prefixed_skills(tmp_path: Path) -> None:
    skills = {
        ".claude/skills": {"claude-foo": {"name": "claude-foo", "description": "x"}},
        ".agents/skills": {"codex-bar": {"name": "codex-bar", "description": "x"}},
    }
    _make_repo(tmp_path, skills=skills)
    findings = validator.check_prefix_compliance(tmp_path)
    assert findings == []


def test_prefix_compliance_fails_on_unprefixed_skill(tmp_path: Path) -> None:
    skills = {".claude/skills": {"proj-start": {"name": "proj-start", "description": "x"}}}
    _make_repo(tmp_path, skills=skills)
    findings = validator.check_prefix_compliance(tmp_path)
    assert any(f.rule == "prefix.unprefixed_skill" for f in findings)


def test_agent_skills_spec_fails_on_name_mismatch(tmp_path: Path) -> None:
    skills = {".agents/skills": {"codex-x": {"name": "different-name", "description": "x"}}}
    _make_repo(tmp_path, skills=skills)
    findings = validator.check_agent_skills_spec(tmp_path)
    assert any(f.rule == "spec.violation" for f in findings)


# ---------------------------------------------------------------------------
# OpenCode permissions
# ---------------------------------------------------------------------------


def test_opencode_defensive_anti_deny_passes_when_present(tmp_path: Path) -> None:
    _make_repo(tmp_path, opencode={"permission": {"skill": {
        "*": "allow",
        "claude-*": "deny",
        "codex-*": "deny",
        "anti-*": "deny",
    }}})
    findings = validator.check_opencode_permissions(tmp_path)
    assert not any(f.rule == "opencode.missing_anti_deny" for f in findings)


def test_opencode_defensive_anti_deny_fails_when_absent(tmp_path: Path) -> None:
    _make_repo(tmp_path, opencode={"permission": {"skill": {"*": "allow", "claude-*": "deny"}}})
    findings = validator.check_opencode_permissions(tmp_path)
    assert any(f.rule == "opencode.missing_anti_deny" for f in findings)


# ---------------------------------------------------------------------------
# Volatile facts
# ---------------------------------------------------------------------------


def test_volatile_facts_fails_on_unittest_discover(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path, agents_md="# AGENTS\n\nRun: python -m unittest discover\n")
    findings = validator.check_volatile_facts(repo)
    assert any(f.rule == "vol.unittest_discover" for f in findings)


def test_volatile_facts_fails_on_test_count_in_prose(tmp_path: Path) -> None:
    repo = _make_repo(
        tmp_path,
        agents_md="# AGENTS\n\nBaseline: 16060 passed\n",
    )
    findings = validator.check_volatile_facts(repo)
    assert any(f.rule == "vol.exact_test_count_in_prose" for f in findings)


def test_volatile_facts_passes_when_clean(tmp_path: Path) -> None:
    _make_repo(tmp_path)
    findings = validator.check_volatile_facts(tmp_path)
    # Clean fixture has no AGENTS.md prose containing volatile facts
    assert not any(f.severity == "fail" for f in findings)


def test_volatile_facts_fails_on_removed_doc_path(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path, agents_md="# AGENTS\n\nSee docs/bug_tracker.md\n")
    findings = validator.check_volatile_facts(repo)
    assert any(f.rule == "vol.removed_doc_path" for f in findings)


# ---------------------------------------------------------------------------
# Reinforcement markers
# ---------------------------------------------------------------------------


def test_reinforcement_markers_pass_on_known_tag(tmp_path: Path) -> None:
    _make_repo(
        tmp_path,
        agents_md=(
            "# AGENTS\n\n"
            "<!-- agent-coordination:reinforcement tdd -->\n"
            "TDD always.\n"
        ),
    )
    findings = validator.check_reinforcement_markers(tmp_path)
    assert not any(f.severity == "fail" for f in findings)


def test_reinforcement_markers_fail_on_unknown_tag(tmp_path: Path) -> None:
    _make_repo(
        tmp_path,
        agents_md=(
            "# AGENTS\n\n"
            "<!-- agent-coordination:reinforcement bogus -->\n"
        ),
    )
    findings = validator.check_reinforcement_markers(tmp_path)
    assert any(f.rule == "rein.unknown_tag" for f in findings)


def test_reinforcement_markers_fail_on_bad_syntax(tmp_path: Path) -> None:
    _make_repo(
        tmp_path,
        agents_md=(
            "# AGENTS\n\n"
            "<!--agent-coordination:reinforcement-->\n"  # missing tag
        ),
    )
    findings = validator.check_reinforcement_markers(tmp_path)
    assert any(f.rule == "rein.bad_syntax" for f in findings)


def test_reinforcement_markers_fail_when_inside_skill_md(tmp_path: Path) -> None:
    skills = {
        ".agents/skills": {
            "codex-foo": {
                "name": "codex-foo",
                "description": "x",
            }
        }
    }
    _make_repo(tmp_path, skills=skills)
    skill_md = tmp_path / ".agents" / "skills" / "codex-foo" / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    skill_md.write_text(
        text + "\n<!-- agent-coordination:reinforcement tdd -->\n",
        encoding="utf-8",
    )
    findings = validator.check_reinforcement_markers(tmp_path)
    assert any(f.rule == "rein.no_marker_in_skill_md" for f in findings)


# ---------------------------------------------------------------------------
# Stale surfaces
# ---------------------------------------------------------------------------


def test_stale_surfaces_warns_when_workflow_dir_present(tmp_path: Path) -> None:
    _make_repo(tmp_path, stale_workflows=True)
    findings = validator.check_stale_surfaces(tmp_path)
    assert any(f.rule == "stale.agent_workflows_present" for f in findings)


def test_stale_surfaces_warns_when_migration_doc_present(tmp_path: Path) -> None:
    _make_repo(tmp_path, stale_migration=True)
    findings = validator.check_stale_surfaces(tmp_path)
    assert any(f.rule == "stale.migration_progress_present" for f in findings)


def test_stale_surfaces_clean(tmp_path: Path) -> None:
    _make_repo(tmp_path)
    findings = validator.check_stale_surfaces(tmp_path)
    assert findings == []


# ---------------------------------------------------------------------------
# Claude settings policy
# ---------------------------------------------------------------------------


def test_claude_settings_policy_fails_on_dangerous(tmp_path: Path) -> None:
    _make_repo(tmp_path, settings_local={"permissions": {"allow": ["Bash(rm -rf:*)"]}})
    findings = validator.check_claude_settings_policy(tmp_path)
    assert any(f.rule == "claude.dangerous_permission" for f in findings)


def test_claude_settings_policy_warns_on_stale(tmp_path: Path) -> None:
    _make_repo(tmp_path, settings_local={"permissions": {"allow": ["Read(//c/Dev/Starship Battles/**)"]}})
    findings = validator.check_claude_settings_policy(tmp_path)
    assert any(f.rule == "claude.stale_starship_path" and f.severity == "warn" for f in findings)


# ---------------------------------------------------------------------------
# CLI / main
# ---------------------------------------------------------------------------


def test_main_returns_zero_on_clean_repo(tmp_path: Path) -> None:
    skills = {".agents/skills": {"codex-foo": {"name": "codex-foo", "description": "x"}}}
    _make_repo(
        tmp_path,
        skills=skills,
        baseline=_good_baseline(),
        opencode={"permission": {"skill": {
            "*": "allow",
            "claude-*": "deny",
            "codex-*": "deny",
            "anti-*": "deny",
        }}},
    )
    # Build matching inventory
    from Tools.agent_coordination.inventory_agent_surfaces import build_inventory
    fresh = build_inventory(tmp_path)
    inv_path = tmp_path / "AgentCoordination" / "generated" / "agent_surface_inventory.json"
    inv_path.parent.mkdir(parents=True, exist_ok=True)
    inv_path.write_text(json.dumps(fresh, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rc = validator.main(["--repo-root", str(tmp_path)])
    assert rc == 0


def test_main_emits_json_format(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _make_repo(tmp_path)
    rc = validator.main(["--repo-root", str(tmp_path), "--format", "json"])
    assert rc != 0  # missing inventory + baseline
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["schema_version"] == 1
    assert "findings" in data


# ---------------------------------------------------------------------------
# Reinforcement: unmarked duplication detection
# ---------------------------------------------------------------------------


def test_unmarked_duplication_detects_5_consecutive_identical_lines(tmp_path: Path) -> None:
    agents = (
        "Always run the full test suite before declaring a task complete.\n"
        "Document architectural changes in the same commit as the code.\n"
        "Prefer integration tests over unit tests for behavior verification.\n"
        "Avoid silent fallback paths that mask configuration drift.\n"
        "Never commit secrets or per-machine paths into shared settings.\n"
    )
    duplicate = (
        "# Adapter\n\n"
        "Always run the full test suite before declaring a task complete.\n"
        "Document architectural changes in the same commit as the code.\n"
        "Prefer integration tests over unit tests for behavior verification.\n"
        "Avoid silent fallback paths that mask configuration drift.\n"
        "Never commit secrets or per-machine paths into shared settings.\n"
    )
    _make_repo(tmp_path, agents_md=agents, claude_md=duplicate)
    findings = validator.check_reinforcement_markers(tmp_path)
    assert any(f.rule == "rein.unmarked_duplication" for f in findings)


def test_unmarked_duplication_passes_below_threshold(tmp_path: Path) -> None:
    agents = (
        "Always run the full test suite before declaring a task complete.\n"
        "Document architectural changes in the same commit as the code.\n"
        "Prefer integration tests over unit tests for behavior verification.\n"
        "Avoid silent fallback paths that mask configuration drift.\n"
        "Never commit secrets or per-machine paths into shared settings.\n"
    )
    only_three = (
        "# Adapter\n\n"
        "Always run the full test suite before declaring a task complete.\n"
        "Document architectural changes in the same commit as the code.\n"
        "Prefer integration tests over unit tests for behavior verification.\n"
        "(unrelated text)\n"
    )
    _make_repo(tmp_path, agents_md=agents, claude_md=only_three)
    findings = validator.check_reinforcement_markers(tmp_path)
    assert not any(f.rule == "rein.unmarked_duplication" for f in findings)


def test_unmarked_duplication_allowed_with_preceding_marker(tmp_path: Path) -> None:
    agents = (
        "Always run the full test suite before declaring a task complete.\n"
        "Document architectural changes in the same commit as the code.\n"
        "Prefer integration tests over unit tests for behavior verification.\n"
        "Avoid silent fallback paths that mask configuration drift.\n"
        "Never commit secrets or per-machine paths into shared settings.\n"
    )
    duplicate_with_marker = (
        "# Adapter\n\n"
        "<!-- agent-coordination:reinforcement tdd -->\n"
        "Always run the full test suite before declaring a task complete.\n"
        "Document architectural changes in the same commit as the code.\n"
        "Prefer integration tests over unit tests for behavior verification.\n"
        "Avoid silent fallback paths that mask configuration drift.\n"
        "Never commit secrets or per-machine paths into shared settings.\n"
    )
    _make_repo(tmp_path, agents_md=agents, claude_md=duplicate_with_marker)
    findings = validator.check_reinforcement_markers(tmp_path)
    assert not any(f.rule == "rein.unmarked_duplication" for f in findings)


def test_unmarked_duplication_ignores_short_decorative_lines(tmp_path: Path) -> None:
    # Headings and decorative lines should not contribute to a 5-line match.
    agents = (
        "## Section\n"
        "---\n"
        "## Other\n"
        "---\n"
        "## Yet another\n"
    )
    duplicate = (
        "## Section\n"
        "---\n"
        "## Other\n"
        "---\n"
        "## Yet another\n"
    )
    _make_repo(tmp_path, agents_md=agents, claude_md=duplicate)
    findings = validator.check_reinforcement_markers(tmp_path)
    # All five lines are decorative/short headings. Should NOT trigger.
    assert not any(f.rule == "rein.unmarked_duplication" for f in findings)


# ---------------------------------------------------------------------------
# Legacy slash-command detection
# ---------------------------------------------------------------------------


def test_legacy_slash_pass_when_only_prefixed_commands(tmp_path: Path) -> None:
    (tmp_path / "Projects").mkdir()
    (tmp_path / "Projects" / "README.md").write_text(
        "Use `/claude-proj-start` to begin a project.\n",
        encoding="utf-8",
    )
    findings = validator.check_legacy_slash_commands(tmp_path)
    assert not any(f.severity == "fail" for f in findings)


def test_legacy_slash_fails_on_unprefixed_command_in_readme(tmp_path: Path) -> None:
    (tmp_path / "Projects").mkdir()
    (tmp_path / "Projects" / "README.md").write_text(
        "Use `/proj-start` to begin.\n",
        encoding="utf-8",
    )
    findings = validator.check_legacy_slash_commands(tmp_path)
    assert any(f.rule == "legacy.unprefixed_slash" for f in findings)


def test_legacy_slash_fails_on_dollar_form(tmp_path: Path) -> None:
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "CODEX.md").write_text(
        "Run $proj-start to begin.\n",
        encoding="utf-8",
    )
    findings = validator.check_legacy_slash_commands(tmp_path)
    assert any(f.rule == "legacy.unprefixed_dollar" for f in findings)


def test_legacy_slash_fails_in_tools_readme(tmp_path: Path) -> None:
    (tmp_path / "Tools" / "audit_shrink").mkdir(parents=True)
    (tmp_path / "Tools" / "audit_shrink" / "README.md").write_text(
        "Then run `/audit-shrink` to start phase 2.\n",
        encoding="utf-8",
    )
    findings = validator.check_legacy_slash_commands(tmp_path)
    assert any(f.rule == "legacy.unprefixed_slash" for f in findings)


def test_legacy_slash_skips_archived_paths(tmp_path: Path) -> None:
    archived = tmp_path / "Tracking" / "bugs" / "archived"
    archived.mkdir(parents=True)
    (archived / "BUG-9.md").write_text("Closed via `/ticket-close bug 9`.\n", encoding="utf-8")
    findings = validator.check_legacy_slash_commands(tmp_path)
    assert findings == []


def test_legacy_slash_skips_agent_coordination_history(tmp_path: Path) -> None:
    coord = tmp_path / "AgentCoordination"
    coord.mkdir()
    (coord / "claude_code_v2_comments.md").write_text("Old: `/proj-start`.\n", encoding="utf-8")
    findings = validator.check_legacy_slash_commands(tmp_path)
    assert findings == []


def test_legacy_slash_skips_docs_ignore(tmp_path: Path) -> None:
    ignore = tmp_path / "docs" / "_ignore"
    ignore.mkdir(parents=True)
    (ignore / "scratch.md").write_text("`/proj-start` here\n", encoding="utf-8")
    findings = validator.check_legacy_slash_commands(tmp_path)
    assert findings == []


def test_legacy_slash_fails_in_active_project_manifest(tmp_path: Path) -> None:
    proj = tmp_path / "Projects" / "active_projects" / "PROJ-300"
    proj.mkdir(parents=True)
    (proj / "manifest.md").write_text("Run `/ticket-work bug 5`.\n", encoding="utf-8")
    findings = validator.check_legacy_slash_commands(tmp_path)
    assert any(f.rule == "legacy.unprefixed_slash" for f in findings)


def test_legacy_slash_does_not_match_localhost_or_unrelated_words(tmp_path: Path) -> None:
    # `loc` is a legacy skill name, but `/localhost`, `/locator`, etc. should
    # not be flagged because they are not exact matches.
    (tmp_path / "Tools" / "x").mkdir(parents=True)
    (tmp_path / "Tools" / "x" / "README.md").write_text(
        "Visit `/localhost:8080`. Then `/locator/api`. Both are unrelated.\n",
        encoding="utf-8",
    )
    findings = validator.check_legacy_slash_commands(tmp_path)
    assert findings == []


def test_usage_counter_shape_passes_when_no_usage_files(tmp_path: Path) -> None:
    _make_repo(tmp_path)
    findings = validator.check_usage_counter_shape(tmp_path)
    assert findings == []


def test_usage_counter_shape_passes_on_valid_files(tmp_path: Path) -> None:
    _make_repo(tmp_path)
    by_install = tmp_path / "AgentCoordination" / "generated" / "skill_usage" / "by_install"
    by_install.mkdir(parents=True)
    (by_install / "abc123.json").write_text(json.dumps({
        "schema_version": 1,
        "install_id": "abc123",
        "skills": {"claude-proj-start": {"count": 3, "last_used": "2026-04-29T00:00:00Z"}},
    }), encoding="utf-8")
    summary_path = by_install.parent / "summary.json"
    summary_path.write_text(json.dumps({
        "schema_version": 1,
        "skills": {
            "claude-proj-start": {
                "total_count": 3,
                "by_install": {"abc123": 3},
                "last_used": "2026-04-29T00:00:00Z",
            }
        },
    }), encoding="utf-8")
    findings = validator.check_usage_counter_shape(tmp_path)
    assert findings == []


def test_usage_counter_shape_fails_on_missing_install_id(tmp_path: Path) -> None:
    by_install = tmp_path / "AgentCoordination" / "generated" / "skill_usage" / "by_install"
    by_install.mkdir(parents=True)
    (by_install / "x.json").write_text(json.dumps({
        "schema_version": 1,
        "skills": {},
    }), encoding="utf-8")
    findings = validator.check_usage_counter_shape(tmp_path)
    assert any(f.rule == "usage.missing_install_id_field" for f in findings)


def test_usage_counter_shape_fails_on_negative_count(tmp_path: Path) -> None:
    by_install = tmp_path / "AgentCoordination" / "generated" / "skill_usage" / "by_install"
    by_install.mkdir(parents=True)
    (by_install / "x.json").write_text(json.dumps({
        "schema_version": 1,
        "install_id": "x",
        "skills": {"claude-foo": {"count": -1}},
    }), encoding="utf-8")
    findings = validator.check_usage_counter_shape(tmp_path)
    assert any(f.rule == "usage.invalid_counter_value" for f in findings)


def test_usage_counter_shape_warns_on_summary_mismatch(tmp_path: Path) -> None:
    by_install = tmp_path / "AgentCoordination" / "generated" / "skill_usage" / "by_install"
    by_install.mkdir(parents=True)
    (by_install / "x.json").write_text(json.dumps({
        "schema_version": 1,
        "install_id": "x",
        "skills": {"claude-foo": {"count": 5}},
    }), encoding="utf-8")
    summary_path = by_install.parent / "summary.json"
    summary_path.write_text(json.dumps({
        "schema_version": 1,
        "skills": {
            "claude-foo": {"total_count": 99, "by_install": {"x": 5}},  # 99 != 5
        },
    }), encoding="utf-8")
    findings = validator.check_usage_counter_shape(tmp_path)
    assert any(f.rule == "usage.summary_mismatch" and f.severity == "warn" for f in findings)


def test_unmarked_duplication_blank_lines_do_not_break_run(tmp_path: Path) -> None:
    # Blank lines between matching content are skipped during normalization.
    agents = (
        "Always run the full test suite before declaring a task complete.\n"
        "Document architectural changes in the same commit as the code.\n"
        "Prefer integration tests over unit tests for behavior verification.\n"
        "Avoid silent fallback paths that mask configuration drift.\n"
        "Never commit secrets or per-machine paths into shared settings.\n"
    )
    duplicate_with_blanks = (
        "# Adapter\n\n"
        "Always run the full test suite before declaring a task complete.\n"
        "\n"
        "Document architectural changes in the same commit as the code.\n"
        "\n"
        "Prefer integration tests over unit tests for behavior verification.\n"
        "Avoid silent fallback paths that mask configuration drift.\n"
        "Never commit secrets or per-machine paths into shared settings.\n"
    )
    _make_repo(tmp_path, agents_md=agents, claude_md=duplicate_with_blanks)
    findings = validator.check_reinforcement_markers(tmp_path)
    assert any(f.rule == "rein.unmarked_duplication" for f in findings)
