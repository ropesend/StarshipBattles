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
