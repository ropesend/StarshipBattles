from __future__ import annotations

import json
from pathlib import Path

import pytest

from Tools.agent_coordination import rename_skills_with_prefixes as renamer


def _write_skill(root: Path, surface: str, name: str, *, body: str = "") -> Path:
    skill_dir = root / surface / name
    skill_dir.mkdir(parents=True)
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        f"---\nname: {name}\ndescription: t\n---\n\n# {name}\n\n{body}",
        encoding="utf-8",
    )
    return skill_md


# ---------------------------------------------------------------------------
# Rename map construction
# ---------------------------------------------------------------------------


def test_build_rename_map_assigns_expected_prefixes(tmp_path: Path) -> None:
    _write_skill(tmp_path, ".claude/skills", "proj-start")
    _write_skill(tmp_path, ".agent/skills", "ticket-work")
    _write_skill(tmp_path, ".opencode/skills", "audit-shrink")
    _write_skill(tmp_path, ".agents/skills", "codex-already")

    plan = renamer.build_rename_plan(tmp_path)
    by_old = {entry["old_name"]: entry for entry in plan["renames"]}
    assert by_old["proj-start"]["new_name"] == "claude-proj-start"
    assert by_old["proj-start"]["surface_path"] == ".claude/skills"
    assert by_old["ticket-work"]["new_name"] == "anti-ticket-work"
    assert by_old["audit-shrink"]["new_name"] == "ocode-audit-shrink"
    # Already prefixed skills are listed as no-op
    assert by_old["codex-already"]["new_name"] == "codex-already"
    assert by_old["codex-already"]["already_compliant"] is True


def test_build_rename_map_skips_shared_prefix(tmp_path: Path) -> None:
    _write_skill(tmp_path, ".claude/skills", "shared-helper")
    plan = renamer.build_rename_plan(tmp_path)
    entry = next(r for r in plan["renames"] if r["old_name"] == "shared-helper")
    assert entry["new_name"] == "shared-helper"
    assert entry["already_compliant"] is True


def test_build_rename_map_rejects_invalid_resulting_name(tmp_path: Path) -> None:
    long_name = "x" * 60
    _write_skill(tmp_path, ".claude/skills", long_name)
    plan = renamer.build_rename_plan(tmp_path)
    entry = next(r for r in plan["renames"] if r["old_name"] == long_name)
    assert entry["valid"] is False  # claude- + 60 chars > 64
    assert "exceeds" in entry["error"].lower() or "too long" in entry["error"].lower()


# ---------------------------------------------------------------------------
# Reference discovery
# ---------------------------------------------------------------------------


def test_find_slash_references_in_markdown(tmp_path: Path) -> None:
    _write_skill(tmp_path, ".claude/skills", "proj-start")
    other = _write_skill(tmp_path, ".claude/skills", "proj-extract-phase",
                          body="See `/proj-start` for initialization.\n")

    refs = renamer.find_references(tmp_path, names={"proj-start"})
    matched = [r for r in refs if "proj-extract-phase" in str(r["path"])]
    assert matched
    assert any(r["form"] == "slash" for r in matched)


def test_find_dollar_references_in_yaml(tmp_path: Path) -> None:
    skills = tmp_path / ".agents" / "skills" / "codex-x" / "agents"
    skills.mkdir(parents=True)
    yaml = skills / "openai.yaml"
    yaml.write_text(
        'default_prompt: "Use $codex-starship-project-system to start work."\n',
        encoding="utf-8",
    )
    refs = renamer.find_references(tmp_path, names={"codex-starship-project-system"})
    assert any(r["form"] == "dollar" and r["path"].endswith("openai.yaml") for r in refs)


def test_find_path_literal_references(tmp_path: Path) -> None:
    _write_skill(tmp_path, ".opencode/skills", "audit-shrink")
    agents = tmp_path / "AGENTS.md"
    agents.write_text(
        "See `.opencode/skills/audit-shrink/SKILL.md` for the workflow.\n",
        encoding="utf-8",
    )
    refs = renamer.find_references(tmp_path, names={"audit-shrink"})
    assert any(r["form"] == "path_literal" and r["path"].endswith("AGENTS.md") for r in refs)


def test_find_opencode_command_key(tmp_path: Path) -> None:
    (tmp_path / "opencode.json").write_text(
        json.dumps({
            "command": {
                "audit-shrink": {
                    "template": "Load the audit-shrink skill and run audit.",
                }
            }
        }),
        encoding="utf-8",
    )
    refs = renamer.find_references(tmp_path, names={"audit-shrink"})
    forms = {r["form"] for r in refs if r["path"].endswith("opencode.json")}
    assert "opencode_command_key" in forms or "opencode_template_body" in forms


# ---------------------------------------------------------------------------
# Dry-run output
# ---------------------------------------------------------------------------


def test_dry_run_writes_skill_renames_md_and_toml(tmp_path: Path) -> None:
    _write_skill(tmp_path, ".claude/skills", "proj-start")
    _write_skill(tmp_path, ".opencode/skills", "audit-shrink")

    rc = renamer.main(["--repo-root", str(tmp_path), "--dry-run"])
    assert rc == 0

    map_path = tmp_path / "AgentCoordination" / "skill_rename_map.toml"
    md_path = tmp_path / "AgentCoordination" / "SKILL_RENAMES.md"
    assert map_path.exists()
    assert md_path.exists()
    md_text = md_path.read_text(encoding="utf-8")
    assert "claude-proj-start" in md_text
    assert "ocode-audit-shrink" in md_text


def test_dry_run_does_not_rename_directories(tmp_path: Path) -> None:
    _write_skill(tmp_path, ".claude/skills", "proj-start")
    rc = renamer.main(["--repo-root", str(tmp_path), "--dry-run"])
    assert rc == 0
    # Original directory still present, no renamed directory created
    assert (tmp_path / ".claude" / "skills" / "proj-start").is_dir()
    assert not (tmp_path / ".claude" / "skills" / "claude-proj-start").exists()


def test_dry_run_refuses_when_invalid_rename_exists(tmp_path: Path) -> None:
    long_name = "x" * 60
    _write_skill(tmp_path, ".claude/skills", long_name)
    rc = renamer.main(["--repo-root", str(tmp_path), "--dry-run"])
    assert rc != 0


# ---------------------------------------------------------------------------
# OpenCode permission planning
# ---------------------------------------------------------------------------


def test_plan_opencode_permissions_includes_anti_deny() -> None:
    new_perms = renamer.plan_opencode_permissions({
        "*": "allow",
        "proj-*": "deny",
        "ticket-*": "deny",
        "codex-*": "deny",
    })
    assert new_perms["*"] == "allow"
    assert new_perms.get("claude-*") == "deny"
    assert new_perms.get("codex-*") == "deny"
    assert new_perms.get("anti-*") == "deny"
    # Old unprefixed wildcards should be removed
    assert "proj-*" not in new_perms
    assert "ticket-*" not in new_perms


def test_plan_opencode_permissions_preserves_explicit_ocode_allow() -> None:
    new_perms = renamer.plan_opencode_permissions({
        "*": "allow",
        "ocode-*": "allow",
    })
    assert new_perms["ocode-*"] == "allow"
