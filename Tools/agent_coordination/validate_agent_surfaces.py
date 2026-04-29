#!/usr/bin/env python3
"""Validate Starship Battles agent coordination surfaces.

Implements the checks listed in `AgentCoordination/codex_agent_coordination_plan_final.md`
§"Validator". Each check is a pure function that takes the repo root and
returns a list of `Finding` objects. The CLI runs every registered check,
prints a human or JSON report, and exits non-zero on any hard fail.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    _here = Path(__file__).resolve()
    for _ in range(6):
        if (_here.parent / "AGENTS.md").exists():
            sys.path.insert(0, str(_here.parent))
            break
        _here = _here.parent

from Tools.agent_coordination.inventory_agent_surfaces import (  # noqa: E402
    SCHEMA_VERSION as INVENTORY_SCHEMA_VERSION,
    SURFACES,
    _find_project_root,
    build_inventory,
)
from Tools.agent_coordination import sanitize_claude_settings as sanitizer  # noqa: E402

VALIDATOR_SCHEMA_VERSION = 1

ALLOWED_REINFORCEMENT_TAGS = frozenset({
    "tdd",
    "docs-first",
    "code-doc-consistency",
    "root-cause",
    "no-ignore-folder",
    "no-revert-unrelated",
})

REINFORCEMENT_HINT = "agent-coordination:reinforcement"
REINFORCEMENT_RE = re.compile(
    r"^[ \t]*<!--\s*agent-coordination:reinforcement\s+(?P<tag>[a-z0-9-]+)\s*-->[ \t]*$"
)

# Volatile fact regexes
EXACT_TEST_COUNT_RE = re.compile(
    r"\b(\d{5})\+?\b(?=[^\n]{0,80}\b(?:tests?|baseline|passed|passing)\b)"
    r"|"
    r"\b(?:tests?|baseline|passed|passing)\b[^\n]{0,80}\b(\d{5})\+?\b",
    re.IGNORECASE,
)
STALE_HARDCODED_BASELINE_RE = re.compile(r"\b(?:15\d{3})\+?\b")
UNITTEST_DISCOVER_LITERAL = "python -m unittest discover"
REMOVED_PATH_LITERALS = (
    ("docs/bug_tracker.md", "vol.removed_doc_path"),
    ("docs/lessons_learned.md", "vol.removed_doc_path"),
    ("assets/tools/ship_background_remover.py", "vol.removed_tool_path"),
)

# Files exempt from volatile-fact scanning. Currently the scanner only walks
# adapter docs (AGENTS.md, CLAUDE.md, .agents/CODEX.md) and SKILL.md files,
# so this list intentionally has zero entries — none of those would ever need
# excluding from a volatile-fact rule.
VOLATILE_EXCLUDE_SUFFIXES: tuple[str, ...] = ()


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str  # "fail" | "warn"
    message: str
    path: str | None = None
    line: int | None = None


# ---------------------------------------------------------------------------
# Test baseline validity
# ---------------------------------------------------------------------------


def check_test_baseline_validity(repo_root: Path) -> list[Finding]:
    path = repo_root / "AgentCoordination" / "generated" / "test_baseline.json"
    if not path.exists():
        return [Finding(
            rule="baseline.missing",
            severity="fail",
            message="AgentCoordination/generated/test_baseline.json is missing.",
            path="AgentCoordination/generated/test_baseline.json",
        )]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [Finding(rule="baseline.unparsable", severity="fail",
                        message=f"Could not parse test_baseline.json: {exc}",
                        path="AgentCoordination/generated/test_baseline.json")]

    findings: list[Finding] = []
    if "schema_version" not in data:
        findings.append(Finding(
            rule="baseline.schema_version_missing", severity="fail",
            message="`schema_version` field missing from test_baseline.json.",
            path="AgentCoordination/generated/test_baseline.json",
        ))
    elif data.get("schema_version") != 1:
        findings.append(Finding(
            rule="baseline.schema_version_unknown", severity="fail",
            message=f"Unknown baseline schema_version: {data.get('schema_version')!r}.",
            path="AgentCoordination/generated/test_baseline.json",
        ))

    required_fields = ("command", "total", "passed", "failed", "errors", "skipped",
                       "baseline_changed_at", "verified_at", "git_sha")
    for field_name in required_fields:
        if field_name not in data:
            findings.append(Finding(
                rule="baseline.required_field_missing", severity="fail",
                message=f"Required field {field_name!r} missing from test_baseline.json.",
                path="AgentCoordination/generated/test_baseline.json",
            ))

    total = data.get("total", 0)
    passed = data.get("passed", 0)
    failed = data.get("failed", 0)
    errors = data.get("errors", 0)
    skipped = data.get("skipped", 0)

    if isinstance(total, int) and total < 100:
        findings.append(Finding(
            rule="baseline.implausible_count", severity="fail",
            message=f"`total` ({total}) is implausibly low for the Starship Battles suite.",
            path="AgentCoordination/generated/test_baseline.json",
        ))

    try:
        if int(passed) + int(failed) + int(errors) + int(skipped) != int(total):
            findings.append(Finding(
                rule="baseline.counts_do_not_sum", severity="fail",
                message=(
                    f"passed+failed+errors+skipped ({passed}+{failed}+{errors}+{skipped}) "
                    f"!= total ({total})."
                ),
                path="AgentCoordination/generated/test_baseline.json",
            ))
    except (TypeError, ValueError):
        findings.append(Finding(
            rule="baseline.invalid_count_types", severity="fail",
            message="One or more count fields in test_baseline.json is not an integer.",
            path="AgentCoordination/generated/test_baseline.json",
        ))

    return findings


# ---------------------------------------------------------------------------
# Inventory freshness
# ---------------------------------------------------------------------------


def _canonical_inventory_text(data: dict) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def check_inventory_freshness(repo_root: Path) -> list[Finding]:
    path = repo_root / "AgentCoordination" / "generated" / "agent_surface_inventory.json"
    if not path.exists():
        return [Finding(
            rule="inventory.missing", severity="fail",
            message="agent_surface_inventory.json is missing. Run inventory_agent_surfaces.py.",
            path="AgentCoordination/generated/agent_surface_inventory.json",
        )]
    try:
        committed_text = path.read_text(encoding="utf-8")
        committed = json.loads(committed_text)
    except (json.JSONDecodeError, OSError) as exc:
        return [Finding(rule="inventory.unparsable", severity="fail",
                        message=f"Could not read inventory: {exc}",
                        path="AgentCoordination/generated/agent_surface_inventory.json")]

    if committed.get("schema_version") != INVENTORY_SCHEMA_VERSION:
        return [Finding(
            rule="inventory.schema_mismatch", severity="fail",
            message=(
                f"Committed inventory schema_version {committed.get('schema_version')} "
                f"differs from current {INVENTORY_SCHEMA_VERSION}. Regenerate."
            ),
            path="AgentCoordination/generated/agent_surface_inventory.json",
        )]

    fresh = build_inventory(repo_root)
    fresh_text = _canonical_inventory_text(fresh)
    if committed_text != fresh_text:
        diff = "".join(difflib.unified_diff(
            committed_text.splitlines(keepends=True),
            fresh_text.splitlines(keepends=True),
            fromfile="committed", tofile="fresh", n=2,
        ))
        truncated = "".join(diff.splitlines(keepends=True)[:50])
        return [Finding(
            rule="inventory.stale", severity="fail",
            message=(
                "Committed inventory does not match fresh generation. "
                "Re-run inventory_agent_surfaces.py and commit the result.\n"
                f"---\n{truncated}"
            ),
            path="AgentCoordination/generated/agent_surface_inventory.json",
        )]
    return []


# ---------------------------------------------------------------------------
# Prefix compliance
# ---------------------------------------------------------------------------


def check_prefix_compliance(repo_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for config in SURFACES:
        surface_path = str(config["surface_path"])
        expected_prefix = str(config["expected_prefix"])
        directory = repo_root / surface_path
        if not directory.is_dir():
            continue
        for skill_dir in sorted(directory.iterdir(), key=lambda p: p.name):
            if not skill_dir.is_dir():
                continue
            if not (skill_dir / "SKILL.md").exists():
                continue
            name = skill_dir.name
            if name.startswith(expected_prefix) or name.startswith("shared-"):
                continue
            findings.append(Finding(
                rule="prefix.unprefixed_skill", severity="fail",
                message=(
                    f"Skill {name!r} on surface {surface_path!r} is missing required "
                    f"prefix {expected_prefix!r}."
                ),
                path=f"{surface_path}/{name}",
            ))
    return findings


# ---------------------------------------------------------------------------
# Agent Skills spec compliance
# ---------------------------------------------------------------------------


def check_agent_skills_spec(repo_root: Path) -> list[Finding]:
    inventory = build_inventory(repo_root)
    findings: list[Finding] = []
    for surface in inventory.get("surfaces", []):
        for skill in surface.get("skills", []):
            for violation in skill.get("spec_violations", []):
                findings.append(Finding(
                    rule="spec.violation", severity="fail",
                    message=(
                        f"Skill {skill.get('directory')!r} on "
                        f"{surface.get('surface_path')!r}: {violation}"
                    ),
                    path=skill.get("skill_md"),
                ))
    return findings


# ---------------------------------------------------------------------------
# OpenCode permissions
# ---------------------------------------------------------------------------


def check_opencode_permissions(repo_root: Path) -> list[Finding]:
    config_path = repo_root / "opencode.json"
    if not config_path.exists():
        return [Finding(
            rule="opencode.missing_config", severity="warn",
            message="opencode.json not present; skipping OpenCode permission checks.",
        )]
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [Finding(rule="opencode.unparsable", severity="fail",
                        message=f"opencode.json parse error: {exc}",
                        path="opencode.json")]

    skill_perms = data.get("permission", {}).get("skill", {}) if isinstance(data.get("permission"), dict) else {}
    findings: list[Finding] = []
    if not isinstance(skill_perms, dict):
        return [Finding(rule="opencode.malformed_skill_block", severity="fail",
                        message="opencode.json `permission.skill` is not an object.",
                        path="opencode.json")]
    if skill_perms.get("anti-*") != "deny":
        findings.append(Finding(
            rule="opencode.missing_anti_deny", severity="fail",
            message=(
                "Defensive `anti-*: deny` rule missing from opencode.json. "
                "Even though OpenCode does not currently document `.agent/skills/` "
                "discovery, the rule costs nothing and protects against future changes."
            ),
            path="opencode.json",
        ))
    keys = list(skill_perms.keys())
    if "*" in keys and keys[0] != "*":
        findings.append(Finding(
            rule="opencode.wildcard_not_first", severity="warn",
            message=(
                "`*` permission key is not first; last-match-wins resolution may "
                "invert specific rules."
            ),
            path="opencode.json",
        ))
    return findings


# ---------------------------------------------------------------------------
# Volatile facts
# ---------------------------------------------------------------------------


def _volatile_target_files(repo_root: Path) -> list[Path]:
    candidates = [
        repo_root / "AGENTS.md",
        repo_root / "CLAUDE.md",
        repo_root / ".agents" / "CODEX.md",
    ]
    for surface in SURFACES:
        skills_dir = repo_root / str(surface["surface_path"])
        if skills_dir.is_dir():
            for skill_md in skills_dir.rglob("SKILL.md"):
                candidates.append(skill_md)
    return [p for p in candidates if p.is_file()]


def _is_excluded(path: Path, repo_root: Path) -> bool:
    rel = path.relative_to(repo_root).as_posix()
    return any(rel.endswith(suffix) for suffix in VOLATILE_EXCLUDE_SUFFIXES)


def check_volatile_facts(repo_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in _volatile_target_files(repo_root):
        if _is_excluded(path, repo_root):
            continue
        rel = path.relative_to(repo_root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            if UNITTEST_DISCOVER_LITERAL in line:
                findings.append(Finding(
                    rule="vol.unittest_discover", severity="fail",
                    message="Stale `python -m unittest discover` reference; use the sharded runner.",
                    path=rel, line=line_no,
                ))
            for literal, rule in REMOVED_PATH_LITERALS:
                if literal in line:
                    findings.append(Finding(
                        rule=rule, severity="fail",
                        message=f"Reference to removed path {literal!r}.",
                        path=rel, line=line_no,
                    ))
            if STALE_HARDCODED_BASELINE_RE.search(line):
                findings.append(Finding(
                    rule="vol.stale_hardcoded_baseline", severity="fail",
                    message=(
                        "Looks like a stale 15xxx test count. "
                        "Reference AgentCoordination/generated/test_baseline.json instead."
                    ),
                    path=rel, line=line_no,
                ))
            if EXACT_TEST_COUNT_RE.search(line):
                # Only fail when not already flagged by stale 15xxx.
                if not STALE_HARDCODED_BASELINE_RE.search(line):
                    findings.append(Finding(
                        rule="vol.exact_test_count_in_prose", severity="fail",
                        message=(
                            "Exact 5-digit test count in prose. "
                            "Reference AgentCoordination/generated/test_baseline.json instead."
                        ),
                        path=rel, line=line_no,
                    ))
    return findings


# ---------------------------------------------------------------------------
# Reinforcement markers
# ---------------------------------------------------------------------------


def _reinforcement_target_files(repo_root: Path) -> list[Path]:
    candidates = [
        repo_root / "AGENTS.md",
        repo_root / "CLAUDE.md",
        repo_root / ".agents" / "CODEX.md",
    ]
    for surface in SURFACES:
        d = repo_root / str(surface["surface_path"])
        if d.is_dir():
            for skill_md in d.rglob("SKILL.md"):
                candidates.append(skill_md)
    return [p for p in candidates if p.is_file()]


def _is_skill_md(path: Path) -> bool:
    return path.name == "SKILL.md"


def check_reinforcement_markers(repo_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in _reinforcement_target_files(repo_root):
        rel = path.relative_to(repo_root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            if REINFORCEMENT_HINT not in line:
                continue
            match = REINFORCEMENT_RE.match(line)
            if not match:
                findings.append(Finding(
                    rule="rein.bad_syntax", severity="fail",
                    message=(
                        "`agent-coordination:reinforcement` marker syntax is invalid. "
                        "Required form: <!-- agent-coordination:reinforcement <tag> -->"
                    ),
                    path=rel, line=line_no,
                ))
                continue
            tag = match.group("tag")
            if tag not in ALLOWED_REINFORCEMENT_TAGS:
                findings.append(Finding(
                    rule="rein.unknown_tag", severity="fail",
                    message=(
                        f"Reinforcement tag {tag!r} is not in the allowed set: "
                        f"{sorted(ALLOWED_REINFORCEMENT_TAGS)}."
                    ),
                    path=rel, line=line_no,
                ))
                continue
            if _is_skill_md(path):
                findings.append(Finding(
                    rule="rein.no_marker_in_skill_md", severity="fail",
                    message=(
                        "Reinforcement markers are not allowed inside SKILL.md "
                        "(adapter-only). Move to AGENTS.md/CLAUDE.md/.agents/CODEX.md."
                    ),
                    path=rel, line=line_no,
                ))
    return findings


# ---------------------------------------------------------------------------
# Stale surfaces
# ---------------------------------------------------------------------------


def check_stale_surfaces(repo_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    if (repo_root / ".agent" / "workflows").exists():
        findings.append(Finding(
            rule="stale.agent_workflows_present", severity="warn",
            message=".agent/workflows/ should be removed once replacement artifacts exist.",
            path=".agent/workflows",
        ))
    if (repo_root / ".agent" / "MIGRATION_PROGRESS.md").exists():
        findings.append(Finding(
            rule="stale.migration_progress_present", severity="warn",
            message=".agent/MIGRATION_PROGRESS.md is superseded by the generated inventory.",
            path=".agent/MIGRATION_PROGRESS.md",
        ))
    return findings


# ---------------------------------------------------------------------------
# Claude settings policy
# ---------------------------------------------------------------------------


def check_claude_settings_policy(repo_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for target in sanitizer.TARGET_FILES:
        report = sanitizer.scan_file(repo_root / target)
        if report.parse_error:
            findings.append(Finding(
                rule="claude.unparsable", severity="fail",
                message=f"Could not parse {target}: {report.parse_error}",
                path=str(target).replace("\\", "/"),
            ))
            continue
        for c in report.classifications:
            level_to_rule_severity = {
                "DANGEROUS": ("claude.dangerous_permission", "fail"),
                "SECRET": ("claude.secret_present", "fail"),
                "EXTERNAL_REVIEW": ("claude.external_path_unapproved", "fail"),
                "STALE_WARN": ("claude.stale_starship_path", "warn"),
            }
            mapping = level_to_rule_severity.get(c.level)
            if not mapping:
                continue
            rule, severity = mapping
            findings.append(Finding(
                rule=rule, severity=severity,
                message=c.reason,
                path=str(target).replace("\\", "/"),
            ))
    return findings


# ---------------------------------------------------------------------------
# Registry + CLI
# ---------------------------------------------------------------------------


CHECKS = (
    ("inventory_freshness", check_inventory_freshness),
    ("test_baseline_validity", check_test_baseline_validity),
    ("prefix_compliance", check_prefix_compliance),
    ("agent_skills_spec", check_agent_skills_spec),
    ("opencode_permissions", check_opencode_permissions),
    ("reinforcement_markers", check_reinforcement_markers),
    ("volatile_facts", check_volatile_facts),
    ("stale_surfaces", check_stale_surfaces),
    ("claude_settings_policy", check_claude_settings_policy),
)


def run_checks(repo_root: Path, *, names: set[str] | None = None) -> dict[str, list[Finding]]:
    results: dict[str, list[Finding]] = {}
    for name, fn in CHECKS:
        if names is not None and name not in names:
            continue
        results[name] = list(fn(repo_root))
    return results


def _format_text(results: dict[str, list[Finding]]) -> tuple[str, int]:
    lines: list[str] = []
    fail_count = warn_count = 0
    for name, findings in results.items():
        fails = [f for f in findings if f.severity == "fail"]
        warns = [f for f in findings if f.severity == "warn"]
        fail_count += len(fails)
        warn_count += len(warns)
        if not findings:
            lines.append(f"[PASS] {name}")
            continue
        lines.append(f"[{'FAIL' if fails else 'WARN'}] {name} ({len(fails)} fail / {len(warns)} warn)")
        for f in findings:
            location = f.path or ""
            if f.line:
                location = f"{location}:{f.line}"
            lines.append(f"  - {f.severity.upper()} {f.rule}  {location}  {f.message}")
    lines.append(f"\nSummary: {fail_count} failures, {warn_count} warnings.")
    return "\n".join(lines) + "\n", fail_count


def _format_json(results: dict[str, list[Finding]]) -> tuple[str, int]:
    fail_count = sum(1 for findings in results.values() for f in findings if f.severity == "fail")
    warn_count = sum(1 for findings in results.values() for f in findings if f.severity == "warn")
    payload = {
        "schema_version": VALIDATOR_SCHEMA_VERSION,
        "tool": "Tools/agent_coordination/validate_agent_surfaces.py",
        "summary": {
            "checks_run": len(results),
            "fail_count": fail_count,
            "warn_count": warn_count,
        },
        "findings": [
            {
                "check": check_name,
                "rule": f.rule,
                "severity": f.severity,
                "message": f.message,
                "path": f.path,
                "line": f.line,
            }
            for check_name, findings in results.items()
            for f in findings
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True), fail_count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate agent coordination surfaces")
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--checks", default=None,
                        help="Comma-separated check IDs to run (default: all)")
    parser.add_argument("--treat-warnings-as-errors", action="store_true")
    args = parser.parse_args(argv)

    repo_root = (args.repo_root or _find_project_root()).resolve()
    names = set(args.checks.split(",")) if args.checks else None
    results = run_checks(repo_root, names=names)

    if args.format == "json":
        text, fail_count = _format_json(results)
    else:
        text, fail_count = _format_text(results)
    print(text)

    if fail_count > 0:
        return 1
    if args.treat_warnings_as_errors:
        warn_count = sum(1 for findings in results.values() for f in findings if f.severity == "warn")
        if warn_count > 0:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
