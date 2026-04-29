#!/usr/bin/env python3
"""Generate a schema-versioned inventory of agent-facing repo surfaces."""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path


SCHEMA_VERSION = 1
DEFAULT_OUTPUT = Path("AgentCoordination/generated/agent_surface_inventory.json")
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# 4-5 digit candidate counts. Keyword co-occurrence on the same line is required
# to avoid false positives on PROJ ids, ports, version numbers, etc.
TEST_COUNT_CANDIDATE_RE = re.compile(r"(?<![\w-])(\d{4,5})\+?(?![\w-])")
TEST_COUNT_KEYWORD_RE = re.compile(r"\b(?:tests?|baseline|passed|skipped|failed|errored?|errors)\b", re.IGNORECASE)

# Generic absolute-path detection. Matches Windows drive letters (`c:\`, `C:/`)
# and POSIX-style absolute mounts (`//c/`, `/c/`). Settings files that legitimately
# carry absolute paths are still flagged here; downstream policy decides severity.
ABSOLUTE_PATH_RE = re.compile(
    r"(?:[A-Za-z]:[\\/]|(?<![\w/])//[A-Za-z]/|(?<![\w/])/[A-Za-z]/)"
    r"[^\"'\s,;)]+"
)

CLAUDE_FRONTMATTER_KEYS = {
    "allowed-tools",
    "argument-hint",
    "arguments",
    "context",
    "disable-model-invocation",
    "effort",
    "agent",
    "hooks",
    "model",
    "paths",
    "shell",
    "user-invocable",
    "when_to_use",
}

SURFACES = [
    {
        "surface_path": ".agents/skills",
        "agent": "codex",
        "expected_prefix": "codex-",
        "opencode_visible": True,
    },
    {
        "surface_path": ".claude/skills",
        "agent": "claude",
        "expected_prefix": "claude-",
        "opencode_visible": True,
    },
    {
        "surface_path": ".opencode/skills",
        "agent": "opencode",
        "expected_prefix": "ocode-",
        "opencode_visible": True,
    },
    {
        "surface_path": ".agent/skills",
        "agent": "antigravity",
        "expected_prefix": "anti-",
        "opencode_visible": False,
    },
]

STALE_LITERAL_PATTERNS = [
    ("python -m unittest discover", "removed_test_command"),
    ("docs/bug_tracker.md", "removed_doc_path"),
    ("docs/lessons_learned.md", "removed_doc_path"),
    ("assets/tools/ship_background_remover.py", "removed_tool_path"),
]


def _find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "game").is_dir() and (current / "data").is_dir():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")


def _relative_path(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def _parse_frontmatter(path: Path) -> dict[str, str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {}

    if not lines or lines[0].strip() != "---":
        return {}

    data: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip("\"'")
    return data


def _load_opencode_permissions(repo_root: Path) -> dict[str, str]:
    config_path = repo_root / "opencode.json"
    if not config_path.exists():
        return {}
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    permission = data.get("permission", {})
    if not isinstance(permission, dict):
        return {}
    skill_permissions = permission.get("skill", {})
    if not isinstance(skill_permissions, dict):
        return {}
    return {
        str(pattern): str(value)
        for pattern, value in skill_permissions.items()
    }


def _opencode_permission_warnings(permissions: dict[str, str]) -> list[dict[str, object]]:
    warnings: list[dict[str, object]] = []
    if not permissions:
        return warnings
    keys = list(permissions.keys())
    if "*" in keys and keys[0] != "*":
        warnings.append({
            "kind": "opencode_wildcard_not_first",
            "severity": "warn",
            "detail": (
                "opencode.json skill permissions list `*` after specific patterns. "
                "Inventory pattern resolution uses last-match-wins, so a trailing "
                "`*` overrides earlier specific rules. Move `*` to the first key."
            ),
        })
    return warnings


def _opencode_permission(
    skill_name: str,
    permissions: dict[str, str],
    visible: bool,
) -> str:
    if not visible:
        return "not_visible"
    matched = "unconfigured"
    for pattern, value in permissions.items():
        if fnmatch.fnmatchcase(skill_name, pattern):
            matched = value
    return matched


def _spec_violations(
    directory_name: str,
    frontmatter: dict[str, str],
    skill_md_exists: bool,
) -> list[str]:
    violations: list[str] = []
    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")

    if not skill_md_exists:
        violations.append("missing SKILL.md")
    if not name:
        violations.append("missing frontmatter name")
    elif not SKILL_NAME_RE.fullmatch(name):
        violations.append("frontmatter name is not a valid skill name")
    if name and name != directory_name:
        violations.append("frontmatter name does not match directory")
    if not description:
        violations.append("missing frontmatter description")
    return violations


def _build_skill_entry(
    skill_dir: Path,
    repo_root: Path,
    expected_prefix: str,
    opencode_visible: bool,
    opencode_permissions: dict[str, str],
) -> dict[str, object]:
    skill_md = skill_dir / "SKILL.md"
    frontmatter = _parse_frontmatter(skill_md)
    frontmatter_name = frontmatter.get("name", "")
    skill_name = frontmatter_name or skill_dir.name
    claude_keys = sorted(
        key for key in frontmatter
        if key in CLAUDE_FRONTMATTER_KEYS
    )
    violations = _spec_violations(skill_dir.name, frontmatter, skill_md.exists())

    return {
        "directory": skill_dir.name,
        "skill_md": _relative_path(skill_md, repo_root),
        "frontmatter": {
            "name": frontmatter_name,
            "description": frontmatter.get("description", ""),
        },
        "frontmatter_name": frontmatter_name,
        "frontmatter_description": frontmatter.get("description", ""),
        "frontmatter_fields": sorted(frontmatter),
        "name_matches_directory": frontmatter_name == skill_dir.name,
        "expected_prefix": expected_prefix,
        "prefix_compliant": skill_name.startswith(expected_prefix),
        "agent_skills_spec_compliant": not violations,
        "spec_violations": violations,
        "claude_frontmatter_present": bool(claude_keys),
        "claude_specific_frontmatter": claude_keys,
        "opencode_visible": opencode_visible,
        "opencode_permission": _opencode_permission(
            skill_name,
            opencode_permissions,
            opencode_visible,
        ),
    }


def _build_surface(
    repo_root: Path,
    config: dict[str, object],
    opencode_permissions: dict[str, str],
) -> dict[str, object]:
    surface_path = str(config["surface_path"])
    surface_dir = repo_root / surface_path
    child_dirs = (
        sorted((path for path in surface_dir.iterdir() if path.is_dir()), key=lambda p: p.name)
        if surface_dir.is_dir()
        else []
    )
    expected_prefix = str(config["expected_prefix"])
    opencode_visible = bool(config["opencode_visible"])
    skills = [
        _build_skill_entry(
            skill_dir,
            repo_root,
            expected_prefix,
            opencode_visible,
            opencode_permissions,
        )
        for skill_dir in child_dirs
        if (skill_dir / "SKILL.md").exists()
    ]

    return {
        "surface_path": surface_path,
        "agent": str(config["agent"]),
        "kind": "skill_surface",
        "exists": surface_dir.exists(),
        "expected_prefix": expected_prefix,
        "opencode_visible": opencode_visible,
        "directory_count": len(child_dirs),
        "skill_names": [str(skill["frontmatter_name"] or skill["directory"]) for skill in skills],
        "skills": skills,
    }


def _scan_file_for_stale_patterns(path: Path, repo_root: Path) -> list[dict[str, object]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []

    findings: list[dict[str, object]] = []
    for line_number, line in enumerate(lines, start=1):
        for literal, kind in STALE_LITERAL_PATTERNS:
            if literal in line:
                findings.append({
                    "path": _relative_path(path, repo_root),
                    "line": line_number,
                    "pattern": literal,
                    "kind": kind,
                    "severity": "stale",
                })
        if TEST_COUNT_CANDIDATE_RE.search(line) and TEST_COUNT_KEYWORD_RE.search(line):
            findings.append({
                "path": _relative_path(path, repo_root),
                "line": line_number,
                "pattern": "hardcoded test baseline",
                "kind": "hardcoded_test_baseline",
                "severity": "stale",
            })
        for match in ABSOLUTE_PATH_RE.finditer(line):
            findings.append({
                "path": _relative_path(path, repo_root),
                "line": line_number,
                "pattern": match.group(0),
                "kind": "absolute_path",
                "severity": "warn",
            })
    return findings


def _stale_scan_files(repo_root: Path) -> list[Path]:
    candidates = [
        repo_root / "AGENTS.md",
        repo_root / "CLAUDE.md",
        repo_root / ".claude" / "settings.json",
        repo_root / ".claude" / "settings.local.json",
        repo_root / ".agent" / "MIGRATION_PROGRESS.md",
    ]
    workflows_dir = repo_root / ".agent" / "workflows"
    if workflows_dir.is_dir():
        candidates.extend(sorted(workflows_dir.rglob("*.md")))
    return [path for path in candidates if path.is_file()]


def _find_stale_references(repo_root: Path) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    stale_workflows = repo_root / ".agent" / "workflows"
    if stale_workflows.exists():
        findings.append({
            "path": ".agent/workflows",
            "kind": "stale_surface",
            "severity": "stale",
        })
    stale_migration = repo_root / ".agent" / "MIGRATION_PROGRESS.md"
    if stale_migration.exists():
        findings.append({
            "path": ".agent/MIGRATION_PROGRESS.md",
            "kind": "stale_surface",
            "severity": "stale",
        })

    for path in _stale_scan_files(repo_root):
        findings.extend(_scan_file_for_stale_patterns(path, repo_root))
    return sorted(
        findings,
        key=lambda item: (str(item["path"]), int(item.get("line", 0)), str(item["kind"])),
    )


def build_inventory(repo_root: Path) -> dict[str, object]:
    """Build a read-only inventory of known agent coordination surfaces."""
    resolved_root = repo_root.resolve()
    opencode_permissions = _load_opencode_permissions(resolved_root)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_by": "Tools/agent_coordination/inventory_agent_surfaces.py",
        "surfaces": [
            _build_surface(resolved_root, config, opencode_permissions)
            for config in SURFACES
        ],
        "stale_references": _find_stale_references(resolved_root),
        "warnings": _opencode_permission_warnings(opencode_permissions),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inventory agent coordination surfaces")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=_find_project_root(),
        help="Repository root to scan",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=f"Output JSON path (default: {DEFAULT_OUTPUT.as_posix()})",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print JSON instead of writing a file",
    )
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    data = build_inventory(repo_root)
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"

    if args.stdout:
        print(text, end="")
        return 0

    output = args.output or repo_root / DEFAULT_OUTPUT
    if not output.is_absolute():
        output = repo_root / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
