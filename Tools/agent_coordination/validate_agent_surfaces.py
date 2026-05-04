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
import fnmatch
import json
import re
import subprocess
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
TEST_BASELINE_SCHEMA_VERSION = 2
TEST_BASELINE_VERIFICATION_SCHEMA_VERSION = 1

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

POLICY_RELATIVE_PATH = Path("AgentCoordination") / "agent_surface_policy.json"
POLICY_REQUIRED_SECTIONS = (
    "skill_prefixes",
    "antigravity",
    "cross_agent_references",
    "claude_settings",
    "rollback",
)

SURFACE_BY_ROOT = {
    ".claude/skills": "claude",
    ".agents/skills": "codex",
    ".opencode/skills": "ocode",
    ".agent/skills": "anti",
}
SURFACE_BY_ADAPTER = {
    "CLAUDE.md": "claude",
    ".agents/CODEX.md": "codex",
}
PREFIX_TO_AGENT = {
    "claude-": "claude",
    "codex-": "codex",
    "ocode-": "ocode",
    "anti-": "anti",
}

SKILL_INVOCATION_RE = re.compile(
    r"(?<![A-Za-z0-9_-])(?P<marker>[/$])(?P<skill>(?:claude|codex|ocode|anti)-[a-z0-9]+(?:-[a-z0-9]+)*)\b"
)
SKILL_PATH_RE = re.compile(
    r"(?P<path>\.(?:claude|agent|agents|opencode)[/\\]skills[/\\]"
    r"(?P<skill>[a-z0-9]+(?:-[a-z0-9]+)*)[/\\]SKILL\.md)"
)
ROLLBACK_HARD_RESET_RE = re.compile(r"\bgit\s+reset\s+--hard\s+HEAD~1\b")


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str  # "fail" | "warn"
    message: str
    path: str | None = None
    line: int | None = None


# ---------------------------------------------------------------------------
# Policy manifest
# ---------------------------------------------------------------------------


def load_agent_surface_policy(repo_root: Path) -> dict[str, object]:
    """Load the mutable agent surface policy manifest.

    Missing or malformed policy files return an empty dict; callers that need
    diagnostic detail should use `check_agent_surface_policy`.
    """
    path = repo_root / POLICY_RELATIVE_PATH
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return payload if isinstance(payload, dict) else {}


def check_agent_surface_policy(repo_root: Path) -> list[Finding]:
    path = repo_root / POLICY_RELATIVE_PATH
    rel = POLICY_RELATIVE_PATH.as_posix()
    if not path.exists():
        return [Finding(
            rule="policy.missing",
            severity="fail",
            message="AgentCoordination/agent_surface_policy.json is missing.",
            path=rel,
        )]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [Finding(
            rule="policy.unparsable",
            severity="fail",
            message=f"Could not parse agent_surface_policy.json: {exc}",
            path=rel,
        )]
    if not isinstance(data, dict):
        return [Finding(
            rule="policy.not_object",
            severity="fail",
            message="agent_surface_policy.json must contain a JSON object.",
            path=rel,
        )]

    findings: list[Finding] = []
    if "schema_version" not in data:
        findings.append(Finding(
            rule="policy.schema_version_missing",
            severity="fail",
            message="`schema_version` field missing from agent_surface_policy.json.",
            path=rel,
        ))
    elif data.get("schema_version") != 1:
        findings.append(Finding(
            rule="policy.schema_version_unknown",
            severity="fail",
            message=f"Unknown policy schema_version: {data.get('schema_version')!r}.",
            path=rel,
        ))

    for section in POLICY_REQUIRED_SECTIONS:
        if section not in data:
            findings.append(Finding(
                rule="policy.required_section_missing",
                severity="fail",
                message=f"Required section {section!r} missing from agent_surface_policy.json.",
                path=rel,
            ))
        elif not isinstance(data.get(section), dict):
            findings.append(Finding(
                rule="policy.required_section_malformed",
                severity="fail",
                message=f"Required section {section!r} must be an object.",
                path=rel,
            ))

    skill_prefixes = data.get("skill_prefixes")
    if isinstance(skill_prefixes, dict):
        for agent, expected in {
            "claude": "claude-",
            "codex": "codex-",
            "ocode": "ocode-",
            "anti": "anti-",
        }.items():
            if skill_prefixes.get(agent) != expected:
                findings.append(Finding(
                    rule="policy.skill_prefix_mismatch",
                    severity="fail",
                    message=f"Policy prefix for {agent!r} must be {expected!r}.",
                    path=rel,
                ))

    antigravity = data.get("antigravity")
    if isinstance(antigravity, dict):
        if not isinstance(antigravity.get("allowed_skills"), list):
            findings.append(Finding(
                rule="policy.antigravity_allowed_skills_missing",
                severity="fail",
                message="Policy antigravity.allowed_skills must be a list.",
                path=rel,
            ))
        if not isinstance(antigravity.get("retired_patterns"), list):
            findings.append(Finding(
                rule="policy.antigravity_retired_patterns_missing",
                severity="fail",
                message="Policy antigravity.retired_patterns must be a list.",
                path=rel,
            ))

    rollback = data.get("rollback")
    if isinstance(rollback, dict):
        if rollback.get("failed_merge_strategy") != "revert":
            findings.append(Finding(
                rule="policy.rollback_strategy_mismatch",
                severity="fail",
                message="Policy rollback.failed_merge_strategy must be 'revert'.",
                path=rel,
            ))
        expected_command = "git revert -m 1 <merge_commit_sha> --no-edit"
        if rollback.get("merge_commit_revert_command") != expected_command:
            findings.append(Finding(
                rule="policy.rollback_command_mismatch",
                severity="fail",
                message=f"Policy rollback.merge_commit_revert_command must be {expected_command!r}.",
                path=rel,
            ))

    return findings


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
    elif data.get("schema_version") != TEST_BASELINE_SCHEMA_VERSION:
        findings.append(Finding(
            rule="baseline.schema_version_unknown", severity="fail",
            message=f"Unknown baseline schema_version: {data.get('schema_version')!r}.",
            path="AgentCoordination/generated/test_baseline.json",
        ))

    required_fields = ("command", "total", "passed", "failed", "errors", "skipped",
                       "baseline_changed_at")
    for field_name in required_fields:
        if field_name not in data:
            findings.append(Finding(
                rule="baseline.required_field_missing", severity="fail",
                message=f"Required field {field_name!r} missing from test_baseline.json.",
                path="AgentCoordination/generated/test_baseline.json",
            ))

    for field_name in ("verified_at", "git_sha"):
        if field_name in data:
            findings.append(Finding(
                rule="baseline.volatile_field_in_canonical",
                severity="fail",
                message=(
                    f"{field_name!r} belongs in "
                    "AgentCoordination/generated/test_baseline/by_install/<install_id>.json, "
                    "not in the canonical baseline."
                ),
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


def check_test_baseline_verification_shape(repo_root: Path) -> list[Finding]:
    by_install_dir = repo_root / "AgentCoordination" / "generated" / "test_baseline" / "by_install"
    if not by_install_dir.is_dir():
        return []

    findings: list[Finding] = []
    required_fields = (
        "schema_version", "install_id", "command", "total", "passed",
        "failed", "errors", "skipped", "verified_at", "git_sha",
    )
    for path in sorted(by_install_dir.glob("*.json")):
        rel = path.relative_to(repo_root).as_posix()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            findings.append(Finding(
                rule="baseline_verification.unparsable",
                severity="fail",
                message=f"Could not parse test baseline verification file: {exc}",
                path=rel,
            ))
            continue
        if not isinstance(data, dict):
            findings.append(Finding(
                rule="baseline_verification.invalid_shape",
                severity="fail",
                message="Test baseline verification file must contain a JSON object.",
                path=rel,
            ))
            continue
        for field_name in required_fields:
            if field_name not in data:
                findings.append(Finding(
                    rule="baseline_verification.required_field_missing",
                    severity="fail",
                    message=f"Required field {field_name!r} missing from test baseline verification.",
                    path=rel,
                ))
        if data.get("schema_version") != TEST_BASELINE_VERIFICATION_SCHEMA_VERSION:
            findings.append(Finding(
                rule="baseline_verification.schema_version_unknown",
                severity="fail",
                message=f"Unknown verification schema_version: {data.get('schema_version')!r}.",
                path=rel,
            ))
        install_id = data.get("install_id")
        if not isinstance(install_id, str) or not install_id:
            findings.append(Finding(
                rule="baseline_verification.missing_install_id_field",
                severity="fail",
                message="`install_id` field is missing or empty.",
                path=rel,
            ))

        total = data.get("total", 0)
        passed = data.get("passed", 0)
        failed = data.get("failed", 0)
        errors = data.get("errors", 0)
        skipped = data.get("skipped", 0)
        try:
            if int(passed) + int(failed) + int(errors) + int(skipped) != int(total):
                findings.append(Finding(
                    rule="baseline_verification.counts_do_not_sum",
                    severity="fail",
                    message=(
                        f"passed+failed+errors+skipped ({passed}+{failed}+{errors}+{skipped}) "
                        f"!= total ({total})."
                    ),
                    path=rel,
                ))
        except (TypeError, ValueError):
            findings.append(Finding(
                rule="baseline_verification.invalid_count_types",
                severity="fail",
                message="One or more count fields in test baseline verification is not an integer.",
                path=rel,
            ))
    return findings


TEST_BASELINE_BY_INSTALL_PREFIX = "AgentCoordination/generated/test_baseline/by_install/"


def check_test_baseline_verification_ownership(repo_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    by_install_dir = repo_root / "AgentCoordination" / "generated" / "test_baseline" / "by_install"

    if by_install_dir.is_dir():
        for path in sorted(by_install_dir.glob("*.json")):
            rel = path.relative_to(repo_root).as_posix()
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            if not isinstance(data, dict):
                continue
            content_id = data.get("install_id")
            filename_id = path.stem
            if isinstance(content_id, str) and content_id and content_id != filename_id:
                findings.append(Finding(
                    rule="baseline_verification.filename_install_id_mismatch",
                    severity="fail",
                    message=(
                        f"Verification file {rel} has filename install_id "
                        f"{filename_id!r} but content install_id {content_id!r}."
                    ),
                    path=rel,
                ))

    local_id = _local_install_id(repo_root)
    if local_id is None:
        return findings
    staged = _staged_files_from_git(repo_root)
    if staged is None:
        return findings
    for rel in sorted(staged):
        if not rel.startswith(TEST_BASELINE_BY_INSTALL_PREFIX):
            continue
        filename_id = Path(rel).stem
        if filename_id == local_id:
            continue
        findings.append(Finding(
            rule="baseline_verification.foreign_install_modified",
            severity="fail",
            message=(
                f"Refusing staged change to {rel}: this verification file belongs "
                f"to install {filename_id!r}, but this machine's install_id "
                f"is {local_id!r}."
            ),
            path=rel,
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
# Agent surface policy enforcement
# ---------------------------------------------------------------------------


def _current_surface_for_path(rel: str) -> str | None:
    normalized = rel.replace("\\", "/")
    if normalized in SURFACE_BY_ADAPTER:
        return SURFACE_BY_ADAPTER[normalized]
    for root, surface in SURFACE_BY_ROOT.items():
        if normalized.startswith(root + "/"):
            return surface
    return None


def _surface_from_skill_name(skill_name: str) -> str | None:
    for prefix, surface in PREFIX_TO_AGENT.items():
        if skill_name.startswith(prefix):
            return surface
    return None


def _surface_from_skill_path(path_text: str) -> str | None:
    normalized = path_text.replace("\\", "/")
    for root, surface in SURFACE_BY_ROOT.items():
        if normalized.startswith(root + "/"):
            return surface
    return None


def _policy_text_targets(repo_root: Path) -> list[Path]:
    candidates: set[Path] = set()
    for rel in (
        "AGENTS.md",
        "CLAUDE.md",
        ".agents/CODEX.md",
        "Projects/README.md",
        "Tracking/README.md",
        "AgentCoordination/README.md",
        "Tools/agent_coordination/README.md",
    ):
        path = repo_root / rel
        if path.is_file():
            candidates.add(path)
    for pattern in ("Projects/protocols/*.md", "Tracking/protocols/*.md"):
        for path in repo_root.glob(pattern):
            if path.is_file():
                candidates.add(path)
    for surface in SURFACES:
        skills_dir = repo_root / str(surface["surface_path"])
        if skills_dir.is_dir():
            for skill_md in skills_dir.rglob("SKILL.md"):
                candidates.add(skill_md)
    return sorted(candidates, key=lambda p: p.relative_to(repo_root).as_posix())


def _policy_allows_reference(policy: dict[str, object], rel: str, reference: str) -> bool:
    cross_agent = policy.get("cross_agent_references")
    if not isinstance(cross_agent, dict):
        return False
    allowed = cross_agent.get("allowed")
    if not isinstance(allowed, list):
        return False
    for entry in allowed:
        if not isinstance(entry, dict):
            continue
        path_pattern = entry.get("path")
        reference_pattern = entry.get("reference")
        if not isinstance(path_pattern, str) or not isinstance(reference_pattern, str):
            continue
        if fnmatch.fnmatch(rel, path_pattern) and fnmatch.fnmatch(reference, reference_pattern):
            return True
    return False


def check_cross_agent_references(repo_root: Path) -> list[Finding]:
    policy = load_agent_surface_policy(repo_root)
    findings: list[Finding] = []
    for path in _policy_text_targets(repo_root):
        rel = path.relative_to(repo_root).as_posix()
        current_surface = _current_surface_for_path(rel)
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for line_no, line in enumerate(lines, start=1):
            for match in SKILL_INVOCATION_RE.finditer(line):
                skill_name = match.group("skill")
                ref_surface = _surface_from_skill_name(skill_name)
                reference = match.group(0)
                is_cross_surface = current_surface is not None and ref_surface != current_surface
                is_anti_outside_antigravity = ref_surface == "anti" and current_surface != "anti"
                if not (is_cross_surface or is_anti_outside_antigravity):
                    continue
                if _policy_allows_reference(policy, rel, reference):
                    continue
                findings.append(Finding(
                    rule="policy.cross_agent_reference",
                    severity="fail",
                    message=(
                        f"{reference!r} references the {ref_surface!r} surface from "
                        f"{current_surface or 'shared'} context."
                    ),
                    path=rel,
                    line=line_no,
                ))
            for match in SKILL_PATH_RE.finditer(line):
                path_text = match.group("path").replace("\\", "/")
                ref_surface = _surface_from_skill_path(path_text)
                skill_surface = _surface_from_skill_name(match.group("skill"))
                surfaces = {s for s in (ref_surface, skill_surface) if s is not None}
                is_cross_surface = current_surface is not None and any(s != current_surface for s in surfaces)
                is_anti_outside_antigravity = "anti" in surfaces and current_surface != "anti"
                if not (is_cross_surface or is_anti_outside_antigravity):
                    continue
                if _policy_allows_reference(policy, rel, path_text):
                    continue
                findings.append(Finding(
                    rule="policy.cross_agent_reference",
                    severity="fail",
                    message=(
                        f"{path_text!r} references {sorted(surfaces)!r} from "
                        f"{current_surface or 'shared'} context."
                    ),
                    path=rel,
                    line=line_no,
                ))
    return findings


def check_nonexistent_skill_path_references(repo_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in _policy_text_targets(repo_root):
        rel = path.relative_to(repo_root).as_posix()
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for line_no, line in enumerate(lines, start=1):
            for match in SKILL_PATH_RE.finditer(line):
                target = match.group("path").replace("\\", "/")
                if (repo_root / target).is_file():
                    continue
                findings.append(Finding(
                    rule="policy.nonexistent_skill_path",
                    severity="fail",
                    message=f"Referenced skill path does not exist: {target}.",
                    path=rel,
                    line=line_no,
                ))
    return findings


def check_antigravity_policy(repo_root: Path) -> list[Finding]:
    policy = load_agent_surface_policy(repo_root)
    antigravity = policy.get("antigravity")
    allowed = set()
    retired_patterns: list[str] = []
    if isinstance(antigravity, dict):
        raw_allowed = antigravity.get("allowed_skills")
        if isinstance(raw_allowed, list):
            allowed = {str(name) for name in raw_allowed if isinstance(name, str)}
        raw_patterns = antigravity.get("retired_patterns")
        if isinstance(raw_patterns, list):
            retired_patterns = [str(pattern) for pattern in raw_patterns if isinstance(pattern, str)]

    findings: list[Finding] = []
    skills_dir = repo_root / ".agent" / "skills"
    if not skills_dir.is_dir():
        return findings
    for skill_dir in sorted(skills_dir.iterdir(), key=lambda p: p.name):
        if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").exists():
            continue
        name = skill_dir.name
        if not name.startswith("anti-") or name in allowed:
            continue
        matched_retired = any(fnmatch.fnmatch(name, pattern) for pattern in retired_patterns)
        detail = "matches retired Antigravity policy" if matched_retired else "is not in the Antigravity allowlist"
        findings.append(Finding(
            rule="policy.antigravity_unapproved_skill",
            severity="fail",
            message=f"Antigravity skill {name!r} {detail}.",
            path=f".agent/skills/{name}/SKILL.md",
        ))
    return findings


def _tracked_files_from_git(repo_root: Path) -> set[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=False,
        )
    except FileNotFoundError:
        return set()
    if result.returncode != 0:
        return set()
    raw = result.stdout.decode("utf-8", errors="replace")
    return {item.replace("\\", "/") for item in raw.split("\0") if item}


def check_tracked_local_settings(repo_root: Path) -> list[Finding]:
    policy = load_agent_surface_policy(repo_root)
    claude_settings = policy.get("claude_settings")
    ignored_files: list[str] = [".claude/settings.local.json"]
    if isinstance(claude_settings, dict):
        raw_ignored = claude_settings.get("ignored_files")
        if isinstance(raw_ignored, list):
            ignored_files = [str(item).replace("\\", "/") for item in raw_ignored if isinstance(item, str)]
    tracked = _tracked_files_from_git(repo_root)
    findings: list[Finding] = []
    for rel in ignored_files:
        if rel in tracked:
            findings.append(Finding(
                rule="policy.tracked_local_settings",
                severity="fail",
                message=f"{rel} is policy-ignored local state but is tracked by git.",
                path=rel,
            ))
    return findings


def check_rollback_policy(repo_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    targets: set[Path] = set()
    for pattern in ("Projects/protocols/*.md", "Tracking/protocols/*.md"):
        for path in repo_root.glob(pattern):
            if path.is_file():
                targets.add(path)
    for surface in SURFACES:
        skills_dir = repo_root / str(surface["surface_path"])
        if skills_dir.is_dir():
            for skill_md in skills_dir.rglob("SKILL.md"):
                targets.add(skill_md)
    for path in sorted(targets, key=lambda p: p.relative_to(repo_root).as_posix()):
        rel = path.relative_to(repo_root).as_posix()
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for line_no, line in enumerate(lines, start=1):
            if ROLLBACK_HARD_RESET_RE.search(line):
                findings.append(Finding(
                    rule="policy.rollback_hard_reset",
                    severity="fail",
                    message=(
                        "Parallel rollback guidance must use merge revert, not "
                        "`git reset --hard HEAD~1`."
                    ),
                    path=rel,
                    line=line_no,
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


DUPLICATION_MIN_LINES = 5
MARKER_LOOKBACK_LIMIT = 10


def _normalize_line(line: str) -> str | None:
    """Return None for blank/trivial/decorative lines that shouldn't count
    toward a duplication match. Otherwise return the stripped form.
    """
    stripped = line.strip()
    if not stripped:
        return None
    if len(stripped) < 8:
        return None
    if re.fullmatch(r"#{1,6}\s+.{0,40}", stripped):
        return None  # short heading
    if re.fullmatch(r"[-*=#`_ ]+", stripped):
        return None  # decorative
    return stripped


def _has_preceding_marker(raw_lines: list[str], target_index: int) -> bool:
    """Walk back from target_index looking for a valid reinforcement marker
    within MARKER_LOOKBACK_LIMIT non-blank lines.
    """
    seen_nonblank = 0
    for j in range(target_index - 1, -1, -1):
        line = raw_lines[j]
        match = REINFORCEMENT_RE.match(line)
        if match and match.group("tag") in ALLOWED_REINFORCEMENT_TAGS:
            return True
        if line.strip():
            seen_nonblank += 1
            if seen_nonblank >= MARKER_LOOKBACK_LIMIT:
                return False
    return False


def _find_unmarked_duplications(
    agents_lines: list[str],
    target_lines: list[str],
) -> list[tuple[int, int]]:
    """Return (start_index, length) tuples for runs of >= DUPLICATION_MIN_LINES
    consecutive normalized target lines that exist verbatim in agents_lines.

    Indices are 0-based into target_lines. Blank/decorative lines are skipped
    during the matching window but the returned `start_index` references the
    original target file's line position.
    """
    agents_norm: list[str] = []
    for line in agents_lines:
        normalized = _normalize_line(line)
        if normalized is not None:
            agents_norm.append(normalized)

    if len(agents_norm) < DUPLICATION_MIN_LINES:
        return []

    agents_ngrams: dict[tuple[str, ...], int] = {}
    for i in range(len(agents_norm) - DUPLICATION_MIN_LINES + 1):
        window = tuple(agents_norm[i:i + DUPLICATION_MIN_LINES])
        agents_ngrams[window] = i

    target_norm: list[tuple[int, str]] = []  # (original_line_index, normalized_text)
    for idx, line in enumerate(target_lines):
        normalized = _normalize_line(line)
        if normalized is not None:
            target_norm.append((idx, normalized))

    if len(target_norm) < DUPLICATION_MIN_LINES:
        return []

    findings: list[tuple[int, int]] = []
    cursor = 0
    while cursor <= len(target_norm) - DUPLICATION_MIN_LINES:
        window = tuple(t[1] for t in target_norm[cursor:cursor + DUPLICATION_MIN_LINES])
        if window in agents_ngrams:
            agents_start = agents_ngrams[window]
            length = DUPLICATION_MIN_LINES
            while (
                cursor + length < len(target_norm)
                and agents_start + length < len(agents_norm)
                and target_norm[cursor + length][1] == agents_norm[agents_start + length]
            ):
                length += 1
            start_line_index = target_norm[cursor][0]
            findings.append((start_line_index, length))
            cursor += length
        else:
            cursor += 1
    return findings


def check_reinforcement_markers(repo_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    agents_path = repo_root / "AGENTS.md"
    agents_lines: list[str] = []
    if agents_path.exists():
        try:
            agents_lines = agents_path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            agents_lines = []

    for path in _reinforcement_target_files(repo_root):
        rel = path.relative_to(repo_root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        raw_lines = text.splitlines()

        for line_no, line in enumerate(raw_lines, start=1):
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

        if path.resolve() == agents_path.resolve():
            continue  # AGENTS.md is the source; don't compare it to itself

        if not agents_lines:
            continue

        for start_index, length in _find_unmarked_duplications(agents_lines, raw_lines):
            if _has_preceding_marker(raw_lines, start_index):
                continue
            findings.append(Finding(
                rule="rein.unmarked_duplication", severity="fail",
                message=(
                    f"{length} consecutive lines duplicate AGENTS.md without a preceding "
                    f"`<!-- agent-coordination:reinforcement <tag> -->` marker. Either add a "
                    f"marker (closed tags: {sorted(ALLOWED_REINFORCEMENT_TAGS)}) or remove "
                    f"the duplicated content."
                ),
                path=rel, line=start_index + 1,
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


LEGACY_BARE_NAMES = (
    # Antigravity-only originals
    "proj-close",
    "proj-sequential",
    "debug-sequential",
    "deep-dive-sequential",
    # OpenCode original
    "audit-shrink",
    # Claude-only originals
    "proj-parallel",
    "debug-parallel",
    "deep-dive-parallel",
    # Shared originals (existed in both Claude and Antigravity)
    "analysis-complexity",
    "analysis-dead-code",
    "analysis-sweep",
    "fix-crash",
    "loc",
    "proj-add-to-plan",
    "proj-archive",
    "proj-audit",
    "proj-continue",
    "proj-extract-phase",
    "proj-manage-plan",
    "proj-reset-baseline",
    "proj-review",
    "proj-revise",
    "proj-start",
    "qa-feedback",
    "qa-triage",
    "ticket-add",
    "ticket-answer",
    "ticket-batch-close",
    "ticket-close",
    "ticket-continue",
    "ticket-deep-dive",
    "ticket-next",
    "ticket-reject",
    "ticket-update",
    "ticket-work",
    "triage-to-proj",
    "validate-designs",
)
# Sort longest-first so e.g. `proj-extract-phase` matches before `proj-`.
_LEGACY_NAME_ALT = "|".join(re.escape(name) for name in sorted(LEGACY_BARE_NAMES, key=len, reverse=True))
LEGACY_SLASH_RE = re.compile(rf"(?<![A-Za-z0-9_-])/(?P<name>{_LEGACY_NAME_ALT})\b")
LEGACY_DOLLAR_RE = re.compile(rf"(?<![A-Za-z0-9_-])\$(?P<name>{_LEGACY_NAME_ALT})\b")

LEGACY_SCAN_TARGETS = (
    "AGENTS.md",
    "CLAUDE.md",
    ".agents/CODEX.md",
    "Projects/README.md",
    "Tracking/README.md",
    "docs/README.md",
)
LEGACY_SCAN_GLOBS = (
    "Tools/*/README.md",
    "Projects/protocols/*.md",
    "Tracking/protocols/*.md",
    "Projects/active_projects/*/manifest.md",
    "Projects/active_projects/*/plan.md",
    "Projects/active_projects/*/design.md",
    "Tracking/bugs/active/*.md",
    "Tracking/features/active/*.md",
)
LEGACY_SCAN_EXCLUDE_DIRS = (
    "AgentCoordination",
    "docs/_ignore",
    "Projects/archived_projects",
    "Projects/deep_archive",
    "Tracking/bugs/archived",
    "Tracking/features/archived",
    "_marked_for_deletion_2026-05-29",
)


def _legacy_scan_files(repo_root: Path) -> list[Path]:
    candidates: set[Path] = set()
    for rel in LEGACY_SCAN_TARGETS:
        path = repo_root / rel
        if path.is_file():
            candidates.add(path)
    for pattern in LEGACY_SCAN_GLOBS:
        for path in repo_root.glob(pattern):
            if path.is_file():
                candidates.add(path)
    # Also scan SKILL.md files (current state, not archived).
    for surface in (".claude/skills", ".agent/skills", ".agents/skills", ".opencode/skills"):
        d = repo_root / surface
        if d.is_dir():
            for skill_md in d.rglob("SKILL.md"):
                candidates.add(skill_md)
    # Apply exclusions.
    excluded: list[Path] = []
    for path in candidates:
        rel = path.relative_to(repo_root).as_posix()
        if any(rel.startswith(prefix + "/") or rel == prefix for prefix in LEGACY_SCAN_EXCLUDE_DIRS):
            continue
        excluded.append(path)
    return sorted(excluded, key=lambda p: p.as_posix())


def _today():
    """Return today's date. Patched in tests for deterministic results."""
    from datetime import date
    return date.today()


REVIEWS_SLA_DAYS = 60
REVIEWS_SLA_TERMINAL_STATUSES = ("Completed", "Archived", "Led to Project")
_REVIEWS_INDEX_ROW_RE = re.compile(
    r"^\|\s*(?P<date>\d{4}-\d{2}-\d{2})\s*\|\s*[^|]+\|\s*[^|]+\|\s*(?P<status>[^|]+?)\s*\|"
)


def check_reviews_sla(repo_root: Path) -> list[Finding]:
    """Warn on `In Progress` reviews older than REVIEWS_SLA_DAYS days.

    Initially warn-only. After one cleanup cycle, promote to fail.
    """
    from datetime import date
    index = repo_root / "Reviews" / "reviews_index.md"
    if not index.is_file():
        return []
    findings: list[Finding] = []
    today = _today()
    try:
        text = index.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    rel = index.relative_to(repo_root).as_posix()
    for line_no, line in enumerate(text.splitlines(), start=1):
        match = _REVIEWS_INDEX_ROW_RE.match(line)
        if not match:
            continue
        status = match.group("status").strip()
        if "In Progress" not in status or any(t in status for t in REVIEWS_SLA_TERMINAL_STATUSES):
            continue
        try:
            entry_date = date.fromisoformat(match.group("date"))
        except ValueError:
            continue
        age_days = (today - entry_date).days
        if age_days > REVIEWS_SLA_DAYS:
            findings.append(Finding(
                rule="reviews.sla_violation", severity="warn",
                message=(
                    f"Review entry dated {entry_date.isoformat()} has been `In Progress` for "
                    f"{age_days} days (SLA: {REVIEWS_SLA_DAYS}). Update or close to "
                    f"`Completed`/`Archived`/`Abandoned (>60d)`/`Led to Project`."
                ),
                path=rel, line=line_no,
            ))
    return findings


def check_tools_inventory(repo_root: Path) -> list[Finding]:
    """Diff Tools/ subdirectories against Tools/README.md's inventory."""
    tools_dir = repo_root / "Tools"
    readme = tools_dir / "README.md"
    if not tools_dir.is_dir() or not readme.is_file():
        return []
    try:
        readme_text = readme.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    listed: set[str] = set()
    for match in re.finditer(r"\[([a-z0-9_]+)\]\(\1/\)", readme_text):
        listed.add(match.group(1))
    findings: list[Finding] = []
    for child in sorted(tools_dir.iterdir(), key=lambda p: p.name):
        if not child.is_dir():
            continue
        name = child.name
        # Skip Python build artifacts and intentionally-private dirs.
        if name.startswith("_") or name.startswith("."):
            continue
        if name == "__pycache__":
            continue
        if name not in listed:
            findings.append(Finding(
                rule="tools.missing_from_inventory", severity="fail",
                message=(
                    f"Tools/{name}/ exists on disk but is not listed in Tools/README.md. "
                    f"Add a row to the inventory table."
                ),
                path="Tools/README.md",
            ))
    return findings


def check_legacy_slash_commands(repo_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in _legacy_scan_files(repo_root):
        rel = path.relative_to(repo_root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            for match in LEGACY_SLASH_RE.finditer(line):
                findings.append(Finding(
                    rule="legacy.unprefixed_slash", severity="fail",
                    message=(
                        f"Legacy unprefixed slash invocation `/{match.group('name')}` "
                        f"in current docs. Use the prefixed form (claude-, anti-, ocode-, codex-)."
                    ),
                    path=rel, line=line_no,
                ))
            for match in LEGACY_DOLLAR_RE.finditer(line):
                findings.append(Finding(
                    rule="legacy.unprefixed_dollar", severity="fail",
                    message=(
                        f"Legacy unprefixed `$` invocation `${match.group('name')}` "
                        f"in current docs. Use the prefixed form."
                    ),
                    path=rel, line=line_no,
                ))
    return findings


def check_usage_counter_shape(repo_root: Path) -> list[Finding]:
    """Validate the per-install usage counter files and the summary."""
    by_install_dir = repo_root / "AgentCoordination" / "generated" / "skill_usage" / "by_install"
    summary_path = repo_root / "AgentCoordination" / "generated" / "skill_usage" / "summary.json"

    if not by_install_dir.is_dir() and not summary_path.exists():
        return []

    findings: list[Finding] = []
    install_totals: dict[str, dict[str, int]] = {}

    if by_install_dir.is_dir():
        for install_path in sorted(by_install_dir.glob("*.json")):
            rel = install_path.relative_to(repo_root).as_posix()
            try:
                data = json.loads(install_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as exc:
                findings.append(Finding(
                    rule="usage.unparsable", severity="fail",
                    message=f"Could not parse usage counter file: {exc}",
                    path=rel,
                ))
                continue
            install_id = data.get("install_id") if isinstance(data, dict) else None
            if not isinstance(install_id, str) or not install_id:
                findings.append(Finding(
                    rule="usage.missing_install_id_field", severity="fail",
                    message="`install_id` field is missing or empty.",
                    path=rel,
                ))
                continue
            skills = data.get("skills") if isinstance(data, dict) else None
            if not isinstance(skills, dict):
                continue
            counts: dict[str, int] = {}
            for skill_name, entry in skills.items():
                count = entry.get("count") if isinstance(entry, dict) else None
                if not isinstance(count, int) or count < 0:
                    findings.append(Finding(
                        rule="usage.invalid_counter_value", severity="fail",
                        message=(
                            f"Skill {skill_name!r} has invalid count {count!r}; "
                            "must be a non-negative integer."
                        ),
                        path=rel,
                    ))
                    continue
                counts[skill_name] = count
            install_totals[install_id] = counts

    if summary_path.exists():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            findings.append(Finding(
                rule="usage.summary_unparsable", severity="fail",
                message=f"Could not parse summary.json: {exc}",
                path=summary_path.relative_to(repo_root).as_posix(),
            ))
        else:
            summary_skills = summary.get("skills") if isinstance(summary, dict) else None
            if isinstance(summary_skills, dict):
                computed: dict[str, int] = {}
                for counts in install_totals.values():
                    for name, count in counts.items():
                        computed[name] = computed.get(name, 0) + count
                for name, summary_entry in summary_skills.items():
                    expected = computed.get(name, 0)
                    if not isinstance(summary_entry, dict):
                        continue
                    actual = summary_entry.get("total_count")
                    if isinstance(actual, int) and actual != expected:
                        findings.append(Finding(
                            rule="usage.summary_mismatch", severity="warn",
                            message=(
                                f"Skill {name!r} summary total {actual} does not match "
                                f"sum across by_install ({expected}). Re-run summarize_skill_usage.py."
                            ),
                            path=summary_path.relative_to(repo_root).as_posix(),
                        ))
    return findings


USAGE_BY_INSTALL_PREFIX = "AgentCoordination/generated/skill_usage/by_install/"


def _local_install_id(repo_root: Path) -> str | None:
    path = repo_root / "AgentCoordination" / "local" / "install_id.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    install_id = data.get("install_id")
    return install_id if isinstance(install_id, str) and install_id else None


def _staged_files_from_git(repo_root: Path) -> set[str] | None:
    """Return staged file paths (forward-slash relative). None if git unavailable."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "-z"],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=False,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    raw = result.stdout.decode("utf-8", errors="replace")
    return {item.replace("\\", "/") for item in raw.split("\0") if item}


def check_usage_counter_ownership(repo_root: Path) -> list[Finding]:
    """Enforce per-machine ownership invariants on by_install/<uuid>.json files.

    Two rules:
      * `usage.filename_install_id_mismatch` (always run when files exist):
        each `by_install/<X>.json` must carry `install_id == "<X>"` in its
        body. A divergence indicates the file was hand-edited or renamed.
      * `usage.foreign_install_modified` (run when both git and a local
        install_id are available): a staged change to `by_install/<X>.json`
        is only allowed when `<X>` matches the local machine's install_id.
        Other machines' counter files may be pulled but never modified locally.
    """
    findings: list[Finding] = []
    by_install_dir = repo_root / "AgentCoordination" / "generated" / "skill_usage" / "by_install"

    if by_install_dir.is_dir():
        for path in sorted(by_install_dir.glob("*.json")):
            rel = path.relative_to(repo_root).as_posix()
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            if not isinstance(data, dict):
                continue
            content_id = data.get("install_id")
            filename_id = path.stem
            if isinstance(content_id, str) and content_id and content_id != filename_id:
                findings.append(Finding(
                    rule="usage.filename_install_id_mismatch",
                    severity="fail",
                    message=(
                        f"Counter file {rel} has filename install_id "
                        f"{filename_id!r} but content install_id {content_id!r}. "
                        "Filenames and content must match; the file may have "
                        "been hand-edited or renamed."
                    ),
                    path=rel,
                ))

    local_id = _local_install_id(repo_root)
    if local_id is None:
        return findings
    staged = _staged_files_from_git(repo_root)
    if staged is None:
        return findings
    for rel in sorted(staged):
        if not rel.startswith(USAGE_BY_INSTALL_PREFIX):
            continue
        filename_id = Path(rel).stem
        if filename_id == local_id:
            continue
        findings.append(Finding(
            rule="usage.foreign_install_modified",
            severity="fail",
            message=(
                f"Refusing staged change to {rel}: this counter file belongs "
                f"to install {filename_id!r}, but this machine's install_id "
                f"is {local_id!r}. Either the file was edited by hand, or "
                f"AgentCoordination/local/install_id.json was copied from "
                f"another machine."
            ),
            path=rel,
        ))
    return findings


def check_claude_settings_policy(repo_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    policy = load_agent_surface_policy(repo_root)
    claude_settings = policy.get("claude_settings")
    targets = list(sanitizer.TARGET_FILES)
    if isinstance(claude_settings, dict):
        raw_tracked = claude_settings.get("tracked_files")
        if isinstance(raw_tracked, list):
            targets = [Path(str(item)) for item in raw_tracked if isinstance(item, str)]
        if claude_settings.get("validate_ignored_file_contents") is False:
            ignored = {
                str(item).replace("\\", "/")
                for item in claude_settings.get("ignored_files", [])
                if isinstance(item, str)
            }
            targets = [target for target in targets if target.as_posix() not in ignored]
    for target in targets:
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
    ("agent_surface_policy", check_agent_surface_policy),
    ("inventory_freshness", check_inventory_freshness),
    ("test_baseline_validity", check_test_baseline_validity),
    ("test_baseline_verification_shape", check_test_baseline_verification_shape),
    ("test_baseline_verification_ownership", check_test_baseline_verification_ownership),
    ("prefix_compliance", check_prefix_compliance),
    ("agent_skills_spec", check_agent_skills_spec),
    ("cross_agent_references", check_cross_agent_references),
    ("nonexistent_skill_path_references", check_nonexistent_skill_path_references),
    ("antigravity_policy", check_antigravity_policy),
    ("tracked_local_settings", check_tracked_local_settings),
    ("rollback_policy", check_rollback_policy),
    ("opencode_permissions", check_opencode_permissions),
    ("reinforcement_markers", check_reinforcement_markers),
    ("volatile_facts", check_volatile_facts),
    ("stale_surfaces", check_stale_surfaces),
    ("claude_settings_policy", check_claude_settings_policy),
    ("usage_counter_shape", check_usage_counter_shape),
    ("usage_counter_ownership", check_usage_counter_ownership),
    ("legacy_slash_commands", check_legacy_slash_commands),
    ("reviews_sla", check_reviews_sla),
    ("tools_inventory", check_tools_inventory),
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
