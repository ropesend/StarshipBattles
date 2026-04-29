from __future__ import annotations

import json
from pathlib import Path

from Tools.agent_coordination import inventory_agent_surfaces as inventory


def _write_skill(
    root: Path,
    surface_path: str,
    directory_name: str,
    *,
    frontmatter_name: str | None = None,
    description: str = "Test skill",
    extra_frontmatter: str = "",
) -> None:
    skill_dir = root / surface_path / directory_name
    skill_dir.mkdir(parents=True)
    name = frontmatter_name if frontmatter_name is not None else directory_name
    lines = [
        "---",
        f"name: {name}",
        f"description: {description}",
    ]
    if extra_frontmatter:
        lines.extend(extra_frontmatter.splitlines())
    lines.extend(["---", "", "# Test Skill", ""])
    (skill_dir / "SKILL.md").write_text("\n".join(lines), encoding="utf-8")


def test_build_inventory_records_skill_surface_metadata(tmp_path: Path) -> None:
    _write_skill(tmp_path, ".agents/skills", "codex-alpha")
    _write_skill(
        tmp_path,
        ".claude/skills",
        "ticket-work",
        extra_frontmatter="argument-hint: bug|feature <number>",
    )
    (tmp_path / ".agent" / "workflows").mkdir(parents=True)
    (tmp_path / ".agent" / "MIGRATION_PROGRESS.md").write_text(
        "stale",
        encoding="utf-8",
    )

    data = inventory.build_inventory(tmp_path)

    assert data["schema_version"] == 1
    surfaces = {surface["surface_path"]: surface for surface in data["surfaces"]}
    assert surfaces[".agents/skills"]["directory_count"] == 1
    assert surfaces[".agents/skills"]["skill_names"] == ["codex-alpha"]
    assert surfaces[".agents/skills"]["opencode_visible"] is True

    codex_skill = surfaces[".agents/skills"]["skills"][0]
    assert codex_skill["frontmatter_name"] == "codex-alpha"
    assert codex_skill["frontmatter_description"] == "Test skill"
    assert codex_skill["expected_prefix"] == "codex-"
    assert codex_skill["prefix_compliant"] is True
    assert codex_skill["agent_skills_spec_compliant"] is True
    assert codex_skill["claude_specific_frontmatter"] == []

    claude_skill = surfaces[".claude/skills"]["skills"][0]
    assert claude_skill["expected_prefix"] == "claude-"
    assert claude_skill["prefix_compliant"] is False
    assert claude_skill["claude_frontmatter_present"] is True
    assert claude_skill["claude_specific_frontmatter"] == ["argument-hint"]

    stale_paths = {entry["path"] for entry in data["stale_references"]}
    assert ".agent/workflows" in stale_paths
    assert ".agent/MIGRATION_PROGRESS.md" in stale_paths


def test_build_inventory_flags_invalid_agent_skill_names(tmp_path: Path) -> None:
    _write_skill(
        tmp_path,
        ".opencode/skills",
        "audit-shrink",
        frontmatter_name="Audit Shrink",
    )

    data = inventory.build_inventory(tmp_path)

    skill = next(
        surface["skills"][0]
        for surface in data["surfaces"]
        if surface["surface_path"] == ".opencode/skills"
    )
    assert skill["agent_skills_spec_compliant"] is False
    assert "frontmatter name is not a valid skill name" in skill["spec_violations"]


def test_main_writes_inventory_json(tmp_path: Path) -> None:
    _write_skill(tmp_path, ".agents/skills", "codex-alpha")
    output = tmp_path / "AgentCoordination" / "generated" / "agent_surface_inventory.json"

    rc = inventory.main([
        "--repo-root",
        str(tmp_path),
        "--output",
        str(output),
    ])

    assert rc == 0
    written = json.loads(output.read_text(encoding="utf-8"))
    assert written["schema_version"] == 1
    assert written["surfaces"][0]["surface_path"] == ".agents/skills"


def test_hardcoded_test_count_detected_with_keyword_context(tmp_path: Path) -> None:
    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text(
        "Baseline: 16060 passed. See generated baseline.\n"
        "Older snapshot referenced 15405 tests.\n"
        "PROJ-2950 is unrelated and should not match.\n",
        encoding="utf-8",
    )

    findings = inventory._scan_file_for_stale_patterns(agents_md, tmp_path)
    matched_lines = {finding["line"] for finding in findings if finding["kind"] == "hardcoded_test_baseline"}
    assert matched_lines == {1, 2}


def test_hardcoded_test_count_does_not_match_unrelated_numbers(tmp_path: Path) -> None:
    doc = tmp_path / "AGENTS.md"
    doc.write_text(
        "Project PROJ-2950 lives at port 16080.\n"
        "Version 17000 of the codec.\n",
        encoding="utf-8",
    )

    findings = inventory._scan_file_for_stale_patterns(doc, tmp_path)
    assert not any(finding["kind"] == "hardcoded_test_baseline" for finding in findings)


def test_absolute_path_detected_generically(tmp_path: Path) -> None:
    settings = tmp_path / ".claude" / "settings.local.json"
    settings.parent.mkdir(parents=True)
    settings.write_text(
        '{"permissions":{"allow":['
        '"Read(//c/Dev/Starship Battles/foo)",'
        '"Bash(if not exist \\"c:\\\\Dev2\\\\StarshipBattles\\\\tests\\")",'
        '"Bash(echo hi)"'
        "]}}",
        encoding="utf-8",
    )

    findings = inventory._scan_file_for_stale_patterns(settings, tmp_path)
    kinds = {finding["kind"] for finding in findings}
    assert "absolute_path" in kinds
    paths = {finding.get("pattern", "") for finding in findings if finding["kind"] == "absolute_path"}
    # The matcher stops at whitespace, so the `//c/Dev/Starship Battles` literal
    # is captured up to the space. The Windows-style path under the `Bash(...)`
    # rule has no internal space and is captured fully.
    assert any(pattern.startswith("//c/Dev/Starship") for pattern in paths)
    assert any("Dev2" in pattern and "StarshipBattles" in pattern for pattern in paths)


def test_claude_frontmatter_detection_includes_paths_hooks_shell(tmp_path: Path) -> None:
    _write_skill(
        tmp_path,
        ".agent/skills",
        "anti-foo",
        extra_frontmatter="paths: src/**\nhooks: PostToolUse\nshell: powershell",
    )

    data = inventory.build_inventory(tmp_path)
    skill = next(
        surface["skills"][0]
        for surface in data["surfaces"]
        if surface["surface_path"] == ".agent/skills"
    )
    assert set(skill["claude_specific_frontmatter"]) >= {"paths", "hooks", "shell"}


def test_opencode_permission_warns_when_wildcard_not_first(tmp_path: Path) -> None:
    _write_skill(tmp_path, ".claude/skills", "claude-foo")
    (tmp_path / "opencode.json").write_text(
        json.dumps({
            "permission": {
                "skill": {
                    "claude-*": "deny",
                    "*": "allow",
                }
            }
        }),
        encoding="utf-8",
    )

    data = inventory.build_inventory(tmp_path)
    warnings = [item for item in data.get("warnings", []) if item["kind"] == "opencode_wildcard_not_first"]
    assert warnings, "Expected a warning when wildcard `*` is not the first key in opencode.json skill permissions"
