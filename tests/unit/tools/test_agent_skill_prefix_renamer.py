from __future__ import annotations

import json
from pathlib import Path

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
    _write_skill(tmp_path, ".claude/skills", "proj-extract-phase",
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


# ---------------------------------------------------------------------------
# Apply mode
# ---------------------------------------------------------------------------


def test_apply_renames_directory_and_updates_frontmatter(tmp_path: Path) -> None:
    _write_skill(tmp_path, ".claude/skills", "proj-start")
    rc = renamer.main(["--repo-root", str(tmp_path), "--apply"])
    assert rc == 0
    old_dir = tmp_path / ".claude" / "skills" / "proj-start"
    new_dir = tmp_path / ".claude" / "skills" / "claude-proj-start"
    assert not old_dir.exists()
    assert new_dir.is_dir()
    skill_md = new_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    assert "name: claude-proj-start" in text
    assert "name: proj-start" not in text


def test_apply_rewrites_slash_references_in_other_skills(tmp_path: Path) -> None:
    _write_skill(tmp_path, ".claude/skills", "proj-start")
    _write_skill(
        tmp_path,
        ".claude/skills",
        "proj-extract-phase",
        body="Run `/proj-start` to begin a new project.\n",
    )
    rc = renamer.main(["--repo-root", str(tmp_path), "--apply"])
    assert rc == 0
    other_renamed = tmp_path / ".claude" / "skills" / "claude-proj-extract-phase" / "SKILL.md"
    text = other_renamed.read_text(encoding="utf-8")
    assert "/claude-proj-start" in text
    assert "/proj-start" not in text


def test_apply_rewrites_path_literals_in_agents_md(tmp_path: Path) -> None:
    _write_skill(tmp_path, ".opencode/skills", "audit-shrink")
    agents = tmp_path / "AGENTS.md"
    agents.write_text(
        "See `.opencode/skills/audit-shrink/SKILL.md` for the workflow.\n",
        encoding="utf-8",
    )
    rc = renamer.main(["--repo-root", str(tmp_path), "--apply"])
    assert rc == 0
    text = agents.read_text(encoding="utf-8")
    assert ".opencode/skills/ocode-audit-shrink/SKILL.md" in text
    assert ".opencode/skills/audit-shrink/SKILL.md" not in text


def test_apply_rewrites_opencode_command_keys_and_template(tmp_path: Path) -> None:
    _write_skill(tmp_path, ".opencode/skills", "audit-shrink")
    config = tmp_path / "opencode.json"
    config.write_text(
        json.dumps({
            "command": {
                "audit-shrink": {
                    "template": "Load the audit-shrink skill and run audit.",
                    "description": "Run shrinkage audit",
                }
            },
            "permission": {
                "skill": {
                    "*": "allow",
                    "proj-*": "deny",
                }
            },
        }, indent=2),
        encoding="utf-8",
    )
    rc = renamer.main(["--repo-root", str(tmp_path), "--apply"])
    assert rc == 0
    data = json.loads(config.read_text(encoding="utf-8"))
    assert "ocode-audit-shrink" in data["command"]
    assert "audit-shrink" not in data["command"]
    template = data["command"]["ocode-audit-shrink"]["template"]
    assert "ocode-audit-shrink" in template
    assert "Load the audit-shrink" not in template
    perms = data["permission"]["skill"]
    assert perms["*"] == "allow"
    assert perms["claude-*"] == "deny"
    assert perms["codex-*"] == "deny"
    assert perms["anti-*"] == "deny"
    assert "proj-*" not in perms


def test_apply_rewrites_dollar_references_in_codex_yaml(tmp_path: Path) -> None:
    skill_dir = tmp_path / ".agents" / "skills" / "codex-foo" / "agents"
    skill_dir.mkdir(parents=True)
    skill_md = tmp_path / ".agents" / "skills" / "codex-foo" / "SKILL.md"
    skill_md.write_text(
        "---\nname: codex-foo\ndescription: t\n---\n\n# body\n",
        encoding="utf-8",
    )
    yaml_file = skill_dir / "openai.yaml"
    # Reference a non-codex skill that will be renamed
    _write_skill(tmp_path, ".claude/skills", "proj-start")
    yaml_file.write_text(
        'default_prompt: "Use $proj-start to begin."\n',
        encoding="utf-8",
    )
    rc = renamer.main(["--repo-root", str(tmp_path), "--apply"])
    assert rc == 0
    text = yaml_file.read_text(encoding="utf-8")
    assert "$claude-proj-start" in text
    assert "$proj-start" not in text


def test_apply_is_idempotent(tmp_path: Path) -> None:
    _write_skill(tmp_path, ".claude/skills", "proj-start")
    rc1 = renamer.main(["--repo-root", str(tmp_path), "--apply"])
    rc2 = renamer.main(["--repo-root", str(tmp_path), "--apply"])
    assert rc1 == 0
    assert rc2 == 0
    new_dir = tmp_path / ".claude" / "skills" / "claude-proj-start"
    assert new_dir.is_dir()


def test_apply_refuses_when_invalid_rename_present(tmp_path: Path) -> None:
    long_name = "x" * 60
    _write_skill(tmp_path, ".claude/skills", long_name)
    rc = renamer.main(["--repo-root", str(tmp_path), "--apply"])
    assert rc != 0
    # No rename happened
    assert (tmp_path / ".claude" / "skills" / long_name).is_dir()
