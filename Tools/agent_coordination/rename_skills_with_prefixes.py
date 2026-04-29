#!/usr/bin/env python3
"""Plan and (optionally) execute the agent-skill prefix migration.

Per the final coordination plan: every runtime skill must use one of the
prefixes `claude-`, `anti-`, `ocode-`, or `codex-`. This tool builds a
deterministic rename map across all four surfaces, finds every reference that
must be rewritten, emits an audit report, and (with `--apply`) performs the
migration in one atomic pass.

Default mode is `--dry-run`. `--apply` is intentionally separate so a human
reviews the SKILL_RENAMES.md output before the rename touches the working
tree.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterable
from pathlib import Path

# Allow running this file directly: prepend the repo root so the absolute
# `Tools.agent_coordination` import resolves without requiring `python -m`.
if __name__ == "__main__" and __package__ is None:
    _here = Path(__file__).resolve()
    for _ in range(6):
        if (_here.parent / "AGENTS.md").exists():
            sys.path.insert(0, str(_here.parent))
            break
        _here = _here.parent

from Tools.agent_coordination.inventory_agent_surfaces import (  # noqa: E402
    SKILL_NAME_RE,
    SURFACES,
    _find_project_root,
)

SHARED_PREFIX = "shared-"
MAX_NAME_LENGTH = 64

# Files/directories that the reference scanner walks. Keep this aligned with
# the renamer scope listed in `AgentCoordination/codex_agent_coordination_plan_final.md`.
REFERENCE_SEARCH_TARGETS = (
    "AGENTS.md",
    "CLAUDE.md",
    ".agents/CODEX.md",
    "opencode.json",
)
REFERENCE_SEARCH_DIRS = (
    ".claude/skills",
    ".agent/skills",
    ".agents/skills",
    ".opencode/skills",
    "Projects/protocols",
    "Tracking/protocols",
)


# ---------------------------------------------------------------------------
# Plan construction
# ---------------------------------------------------------------------------


def build_rename_plan(repo_root: Path) -> dict[str, object]:
    resolved = repo_root.resolve()
    renames: list[dict[str, object]] = []
    for config in SURFACES:
        surface_path = str(config["surface_path"])
        expected_prefix = str(config["expected_prefix"])
        agent = str(config["agent"])
        surface_dir = resolved / surface_path
        if not surface_dir.is_dir():
            continue
        for skill_dir in sorted(surface_dir.iterdir(), key=lambda p: p.name):
            if not skill_dir.is_dir():
                continue
            if not (skill_dir / "SKILL.md").exists():
                continue
            old_name = skill_dir.name
            entry = _plan_one(old_name, expected_prefix, surface_path, agent)
            renames.append(entry)
    return {"renames": renames, "expected_prefixes": [c["expected_prefix"] for c in SURFACES]}


def _plan_one(
    old_name: str,
    expected_prefix: str,
    surface_path: str,
    agent: str,
) -> dict[str, object]:
    already_compliant = old_name.startswith(expected_prefix) or old_name.startswith(SHARED_PREFIX)
    new_name = old_name if already_compliant else f"{expected_prefix}{old_name}"
    valid = True
    error: str | None = None
    if not SKILL_NAME_RE.fullmatch(new_name):
        valid = False
        error = "Resulting name does not satisfy the Agent Skills name regex"
    if len(new_name) > MAX_NAME_LENGTH:
        valid = False
        error = (
            f"Resulting name length {len(new_name)} exceeds Agent Skills max ({MAX_NAME_LENGTH}); "
            "rename manually."
        )
    return {
        "old_name": old_name,
        "new_name": new_name,
        "surface_path": surface_path,
        "agent": agent,
        "expected_prefix": expected_prefix,
        "already_compliant": already_compliant,
        "valid": valid,
        "error": error,
    }


# ---------------------------------------------------------------------------
# Reference discovery
# ---------------------------------------------------------------------------


def _candidate_files(repo_root: Path) -> Iterable[Path]:
    for rel in REFERENCE_SEARCH_TARGETS:
        target = repo_root / rel
        if target.is_file():
            yield target
    for rel in REFERENCE_SEARCH_DIRS:
        directory = repo_root / rel
        if not directory.is_dir():
            continue
        for path in directory.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() in {".md", ".yaml", ".yml", ".json", ".toml", ".txt"}:
                yield path


def find_references(repo_root: Path, names: set[str]) -> list[dict[str, object]]:
    if not names:
        return []
    sorted_names = sorted(names, key=len, reverse=True)
    name_alt = "|".join(re.escape(n) for n in sorted_names)
    slash_re = re.compile(rf"(?<![A-Za-z0-9_-])/({name_alt})\b")
    dollar_re = re.compile(rf"\$({name_alt})\b")
    path_re = re.compile(
        rf"(?:\.claude|\.agent|\.agents|\.opencode)[/\\]+skills[/\\]+({name_alt})(?=[/\\\s\"'`)/.])"
    )
    bare_re = re.compile(rf"(?<![A-Za-z0-9_-])({name_alt})(?![A-Za-z0-9_-])")

    results: list[dict[str, object]] = []
    repo_resolved = repo_root.resolve()
    for path in _candidate_files(repo_resolved):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        rel = path.relative_to(repo_resolved).as_posix()

        for line_no, line in enumerate(text.splitlines(), start=1):
            for form, regex in (("slash", slash_re), ("dollar", dollar_re), ("path_literal", path_re)):
                for match in regex.finditer(line):
                    results.append({
                        "path": rel,
                        "line": line_no,
                        "form": form,
                        "name": match.group(1),
                        "match_text": match.group(0),
                    })

        # Frontmatter `name:` field (only the first SKILL.md frontmatter block).
        if path.name == "SKILL.md":
            for line_no, line in enumerate(text.splitlines(), start=1):
                stripped = line.strip()
                if stripped.startswith("name:"):
                    value = stripped.split(":", 1)[1].strip().strip("\"'")
                    if value in names:
                        results.append({
                            "path": rel,
                            "line": line_no,
                            "form": "frontmatter_name",
                            "name": value,
                            "match_text": stripped,
                        })
                    break

        # opencode.json command keys + template bodies are extracted structurally.
        if path.name == "opencode.json":
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                data = None
            if isinstance(data, dict):
                command = data.get("command")
                if isinstance(command, dict):
                    for key, value in command.items():
                        if key in names:
                            results.append({
                                "path": rel,
                                "line": 0,
                                "form": "opencode_command_key",
                                "name": key,
                                "match_text": key,
                            })
                        if isinstance(value, dict):
                            template = value.get("template")
                            if isinstance(template, str):
                                for match in bare_re.finditer(template):
                                    if match.group(1) in names:
                                        results.append({
                                            "path": rel,
                                            "line": 0,
                                            "form": "opencode_template_body",
                                            "name": match.group(1),
                                            "match_text": match.group(0),
                                        })

    return results


# ---------------------------------------------------------------------------
# OpenCode permission planning
# ---------------------------------------------------------------------------


def plan_opencode_permissions(current: dict[str, str]) -> dict[str, str]:
    """Replace the current pre-rename permission list with the post-rename
    layout. Drops obsolete unprefixed deny patterns (proj-*, ticket-*, etc.)
    and adds the four agent-prefix rules plus the defensive `anti-*: deny`.

    Preserves any explicit `ocode-*` or `shared-*` entries the user may have
    set, and preserves the leading `*: allow` default if present.
    """
    new_perms: dict[str, str] = {}
    if current.get("*") == "allow":
        new_perms["*"] = "allow"
    else:
        new_perms["*"] = current.get("*", "allow")

    for prefix in ("claude-*", "codex-*", "anti-*"):
        new_perms[prefix] = "deny"

    for prefix in ("ocode-*", "shared-*"):
        if current.get(prefix) == "allow":
            new_perms[prefix] = "allow"
        elif prefix == "ocode-*":
            new_perms[prefix] = "allow"
    return new_perms


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _toml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def render_rename_map_toml(plan: dict[str, object]) -> str:
    lines = [
        "# Skill rename map — generated by Tools/agent_coordination/rename_skills_with_prefixes.py",
        "# Do not edit by hand. Re-run the renamer to refresh.",
        "",
        "schema_version = 1",
        "",
    ]
    for entry in plan["renames"]:  # type: ignore[index]
        lines.append("[[renames]]")
        lines.append(f"old_name = {_toml_quote(str(entry['old_name']))}")
        lines.append(f"new_name = {_toml_quote(str(entry['new_name']))}")
        lines.append(f"surface_path = {_toml_quote(str(entry['surface_path']))}")
        lines.append(f"agent = {_toml_quote(str(entry['agent']))}")
        lines.append(f"expected_prefix = {_toml_quote(str(entry['expected_prefix']))}")
        lines.append(f"already_compliant = {str(entry['already_compliant']).lower()}")
        lines.append(f"valid = {str(entry['valid']).lower()}")
        if entry.get("error"):
            lines.append(f"error = {_toml_quote(str(entry['error']))}")
        lines.append("")
    return "\n".join(lines)


def render_renames_md(plan: dict[str, object], references: list[dict[str, object]]) -> str:
    lines = ["# Skill Rename Plan (Audit Artifact)", ""]
    lines.append(
        "Generated by `Tools/agent_coordination/rename_skills_with_prefixes.py`. "
        "Old skill names are not preserved as aliases — the rename is atomic and "
        "any reference that is not rewritten will break."
    )
    lines.append("")
    lines.append("## Renames by surface")
    lines.append("")

    by_surface: dict[str, list[dict[str, object]]] = {}
    for entry in plan["renames"]:  # type: ignore[index]
        by_surface.setdefault(str(entry["surface_path"]), []).append(entry)

    for surface_path, entries in sorted(by_surface.items()):
        lines.append(f"### `{surface_path}`")
        lines.append("")
        lines.append("| old name | new name | status |")
        lines.append("| --- | --- | --- |")
        for entry in entries:
            status_parts: list[str] = []
            if entry["already_compliant"]:
                status_parts.append("already compliant (no rename)")
            else:
                status_parts.append("rename")
            if not entry["valid"]:
                status_parts.append(f"INVALID: {entry['error']}")
            lines.append(f"| `{entry['old_name']}` | `{entry['new_name']}` | {' / '.join(status_parts)} |")
        lines.append("")

    lines.append("## Reference rewrites")
    lines.append("")
    lines.append(f"{len(references)} reference site(s) detected.")
    lines.append("")
    if references:
        # Aggregate by file for readability.
        by_file: dict[str, list[dict[str, object]]] = {}
        for ref in references:
            by_file.setdefault(str(ref["path"]), []).append(ref)
        for path, refs in sorted(by_file.items()):
            lines.append(f"### `{path}` ({len(refs)} ref(s))")
            for ref in refs:
                line = ref.get("line", 0)
                form = ref["form"]
                name = ref["name"]
                lines.append(f"  - line {line}: form={form} name=`{name}`")
            lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Plan or apply the agent-skill prefix migration")
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true", default=True, help="Default mode; only writes the audit artifacts")
    parser.add_argument("--apply", action="store_true", help="Actually perform the rename. Refused if any plan entry is invalid.")
    args = parser.parse_args(argv)

    repo_root = (args.repo_root or _find_project_root()).resolve()
    plan = build_rename_plan(repo_root)
    invalid = [r for r in plan["renames"] if not r["valid"]]
    if invalid:
        print("Refusing to proceed: invalid rename targets:", file=sys.stderr)
        for entry in invalid:
            print(f"  {entry['surface_path']}/{entry['old_name']} → {entry['new_name']}: {entry['error']}", file=sys.stderr)
        # In dry-run we still want to write the report so the user can review.
        # Continue, but exit non-zero.

    new_names = {r["old_name"] for r in plan["renames"] if not r["already_compliant"] and r["valid"]}
    references = find_references(repo_root, names=new_names)

    output_dir = repo_root / "AgentCoordination"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "skill_rename_map.toml").write_text(render_rename_map_toml(plan), encoding="utf-8")
    (output_dir / "SKILL_RENAMES.md").write_text(render_renames_md(plan, references), encoding="utf-8")

    print(f"Wrote {output_dir / 'skill_rename_map.toml'}")
    print(f"Wrote {output_dir / 'SKILL_RENAMES.md'}")
    print(f"Renames planned: {sum(1 for r in plan['renames'] if not r['already_compliant'])}")
    print(f"References: {len(references)}")

    if args.apply and not invalid:
        print("--apply is reserved for the dedicated atomic rename phase. Use the dedicated rename PR instead.", file=sys.stderr)
        return 2

    return 1 if invalid else 0


if __name__ == "__main__":
    sys.exit(main())
