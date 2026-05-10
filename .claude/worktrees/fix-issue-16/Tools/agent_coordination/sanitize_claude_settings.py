#!/usr/bin/env python3
"""Classify Claude Code settings entries into OK / STALE_WARN / EXTERNAL_REVIEW / DANGEROUS / SECRET.

Dry-run by default. Apply mode is opt-in and refuses rewrites that broaden
permissions.

Operates by default on tracked shared settings:
- .claude/settings.json
- .claude/settings.example.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

SCHEMA_VERSION = 1
TARGET_FILES = (
    Path(".claude/settings.json"),
    Path(".claude/settings.example.json"),
)

# Anything that *isn't* a settings entry under permissions.allow / additionalDirectories
# is preserved as-is. Hooks and effortLevel never produce findings.

# Path classification patterns ----------------------------------------------

_OLD_DEV_RE = re.compile(r"[/\\]+Dev[/\\]+Starship[ _]Battles", re.IGNORECASE)
_CURRENT_SB_RE = re.compile(r"[/\\]+(?:Developer|Dev2|Dev3|Source|src)[/\\]+StarshipBattles\b", re.IGNORECASE)
_GENERIC_SB_RE = re.compile(r"StarshipBattles", re.IGNORECASE)
_ABS_PATH_RE = re.compile(
    r"(?:[A-Za-z]:[\\/]|//[A-Za-z][/]|/[A-Za-z][/])"
    r"[^\"'\s,;)]+"
)

# Known-safe system library paths (Python site-packages, etc.).
_SAFE_SYSTEM_PATTERNS = (
    re.compile(r"AppData[/\\]+Roaming[/\\]+Python", re.IGNORECASE),
    re.compile(r"site-packages", re.IGNORECASE),
)

# Dangerous command patterns (Bash() rules)
_DANGEROUS_PATTERNS = (
    re.compile(r"\brm\b\s+(-rf|-fr|-r\s+-f|-f\s+-r)", re.IGNORECASE),
    re.compile(r"\bdel\b\s*/s", re.IGNORECASE),
    re.compile(r"\brmdir\b\s*/s", re.IGNORECASE),
    re.compile(r"\bgit\s+push\s+--force\b", re.IGNORECASE),
    re.compile(r"\bgit\s+reset\s+--hard\b", re.IGNORECASE),
    re.compile(r"\bgit\s+clean\s+-[^-\s]*[fdx]", re.IGNORECASE),
)

# Overly broad globs (post-prefix stripping)
_DANGEROUS_BROAD_GLOBS = (
    re.compile(r"^//\*\*?\)?$"),       # Read(//**)
    re.compile(r"^/\*\*?\)?$"),
    re.compile(r"^\*\*?\)?$"),         # Read(**) or Read(*)
    re.compile(r"^\*:\*\)?$"),
)

# Secret detection
_SECRET_PATTERNS = (
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),                 # AWS access key
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),              # OpenAI API key
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),     # GitHub PAT
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),     # Slack token
)


@dataclass(frozen=True)
class Classification:
    level: str  # OK | STALE_WARN | EXTERNAL_REVIEW | DANGEROUS | SECRET
    rule_text: str
    reason: str
    proposed_rewrite: str | None = None
    source_field: str = "permissions.allow"


@dataclass
class FileReport:
    path: Path
    classifications: list[Classification] = field(default_factory=list)
    parse_error: str | None = None
    missing: bool = False


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


def _is_secret(value: str) -> bool:
    return any(pattern.search(value) for pattern in _SECRET_PATTERNS)


def _is_dangerous_command(value: str) -> bool:
    return any(pattern.search(value) for pattern in _DANGEROUS_PATTERNS)


def _is_dangerous_broad(inner: str) -> bool:
    return any(pattern.search(inner) for pattern in _DANGEROUS_BROAD_GLOBS)


def _strip_outer(rule: str) -> tuple[str, str]:
    """Strip outer Bash(...) / Read(...) wrapper. Returns (kind, inner)."""
    match = re.match(r"^([A-Za-z]+)\((.*)\)$", rule.strip(), re.DOTALL)
    if not match:
        return "", rule
    return match.group(1), match.group(2)


def _is_safe_system_path(value: str) -> bool:
    return any(pattern.search(value) for pattern in _SAFE_SYSTEM_PATTERNS)


_OLD_DEV_REWRITE_RE = re.compile(
    r"(?P<sep>[\\/]+)Dev(?P<sep2>[\\/]+)Starship[ _]Battles",
    re.IGNORECASE,
)


def _propose_rewrite(rule: str) -> str | None:
    """Replace stale `Dev/Starship Battles` segments with the canonical
    `Developer/StarshipBattles` form, preserving the original separator style
    (single vs doubled backslashes, forward vs back slashes). Returns None
    when nothing to rewrite or when rewriting would broaden permissions.
    """
    if not _OLD_DEV_RE.search(rule):
        return None

    def _swap(match: re.Match[str]) -> str:
        sep = match.group("sep")
        sep2 = match.group("sep2")
        return f"{sep}Developer{sep2}StarshipBattles"

    rewritten = _OLD_DEV_REWRITE_RE.sub(_swap, rule)
    if rewritten == rule:
        return None
    if _broadens_permission(rule, rewritten):
        return None
    return rewritten


def classify_entry(rule: str, *, source_field: str = "permissions.allow") -> Classification:
    """Classify a single permission rule string."""
    if _is_secret(rule):
        return Classification(
            level="SECRET",
            rule_text=rule,
            reason="Looks like a hard-coded secret/credential.",
            source_field=source_field,
        )

    kind, inner = _strip_outer(rule)
    inner_stripped = inner.strip()

    if kind == "Bash" and _is_dangerous_command(inner):
        return Classification(
            level="DANGEROUS",
            rule_text=rule,
            reason="Destructive shell pattern (rm -rf / del /s / force push / reset --hard / git clean -f).",
            source_field=source_field,
        )

    if _is_dangerous_broad(inner_stripped):
        return Classification(
            level="DANGEROUS",
            rule_text=rule,
            reason="Overly broad permission (matches the entire filesystem).",
            source_field=source_field,
        )

    abs_paths = _ABS_PATH_RE.findall(rule)

    # Stale-path detection scans the full rule text because the absolute-path
    # matcher stops at whitespace, and the legacy folder name `Starship Battles`
    # contains a space.
    has_old_dev = bool(_OLD_DEV_RE.search(rule))

    # No absolute paths → repo-relative or pure command rule.
    if not abs_paths and not has_old_dev:
        return Classification(
            level="OK",
            rule_text=rule,
            reason="No absolute paths; assumed repo-relative or command-only.",
            source_field=source_field,
        )

    has_safe_lib = any(_is_safe_system_path(p) for p in abs_paths)
    has_sb_anywhere = bool(_GENERIC_SB_RE.search(rule))
    has_current_sb = bool(_CURRENT_SB_RE.search(rule))

    if has_old_dev:
        return Classification(
            level="STALE_WARN",
            rule_text=rule,
            reason="References the old `Dev\\Starship Battles` checkout layout.",
            proposed_rewrite=_propose_rewrite(rule),
            source_field=source_field,
        )

    if has_current_sb or (has_sb_anywhere and not has_old_dev):
        return Classification(
            level="OK",
            rule_text=rule,
            reason="Path inside a Starship Battles checkout.",
            source_field=source_field,
        )

    if has_safe_lib:
        return Classification(
            level="OK",
            rule_text=rule,
            reason="Known-safe system library path.",
            source_field=source_field,
        )

    return Classification(
        level="EXTERNAL_REVIEW",
        rule_text=rule,
        reason="Absolute path outside known Starship Battles roots.",
        source_field=source_field,
    )


# ---------------------------------------------------------------------------
# No-broadening invariant
# ---------------------------------------------------------------------------


def _broadens_permission(original: str, proposed: str) -> bool:
    """Return True if `proposed` is broader than `original`.

    Heuristic: count the number of `**` glob expansions and the path-segment
    depth. A proposal that drops path segments or introduces a `**` where
    none existed is broadening.
    """
    if proposed == original:
        return False
    orig_kind, orig_inner = _strip_outer(original)
    prop_kind, prop_inner = _strip_outer(proposed)
    if orig_kind != prop_kind:
        return True
    orig_segments = re.split(r"[\\/]+", orig_inner)
    prop_segments = re.split(r"[\\/]+", prop_inner)
    # If the proposed has fewer non-empty segments, it covers more.
    orig_nonempty = [s for s in orig_segments if s]
    prop_nonempty = [s for s in prop_segments if s]
    if len(prop_nonempty) < len(orig_nonempty):
        return True
    orig_double_stars = orig_inner.count("**")
    prop_double_stars = prop_inner.count("**")
    if prop_double_stars > orig_double_stars:
        return True
    return False


# ---------------------------------------------------------------------------
# File scanning
# ---------------------------------------------------------------------------


def _classify_iterable(
    rules: list[object],
    source_field: str,
) -> list[Classification]:
    findings: list[Classification] = []
    for raw in rules:
        if not isinstance(raw, str):
            continue
        findings.append(classify_entry(raw, source_field=source_field))
    return findings


def scan_file(path: Path) -> FileReport:
    if not path.exists():
        return FileReport(path=path, missing=True)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return FileReport(path=path, parse_error=str(exc))

    findings: list[Classification] = []
    permissions = data.get("permissions") if isinstance(data, dict) else None
    if isinstance(permissions, dict):
        allow = permissions.get("allow")
        if isinstance(allow, list):
            findings.extend(_classify_iterable(allow, "permissions.allow"))
        deny = permissions.get("deny")
        if isinstance(deny, list):
            findings.extend(_classify_iterable(deny, "permissions.deny"))
        ask = permissions.get("ask")
        if isinstance(ask, list):
            findings.extend(_classify_iterable(ask, "permissions.ask"))
        extras = permissions.get("additionalDirectories")
        if isinstance(extras, list):
            findings.extend(_classify_iterable(extras, "permissions.additionalDirectories"))

    return FileReport(path=path, classifications=findings)


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _summary(report: FileReport) -> dict[str, int]:
    counts: dict[str, int] = {
        "OK": 0,
        "STALE_WARN": 0,
        "EXTERNAL_REVIEW": 0,
        "DANGEROUS": 0,
        "SECRET": 0,
    }
    for c in report.classifications:
        counts[c.level] = counts.get(c.level, 0) + 1
    return counts


def _format_text_report(reports: list[FileReport]) -> str:
    lines: list[str] = ["# Claude Settings Sanitizer Report", ""]
    for report in reports:
        rel = report.path
        lines.append(f"## {rel}")
        if report.missing:
            lines.append("  (file not present)")
            lines.append("")
            continue
        if report.parse_error:
            lines.append(f"  PARSE ERROR: {report.parse_error}")
            lines.append("")
            continue
        counts = _summary(report)
        lines.append(
            "  Counts: OK={OK} STALE_WARN={STALE_WARN} EXTERNAL_REVIEW={EXTERNAL_REVIEW} "
            "DANGEROUS={DANGEROUS} SECRET={SECRET}".format(**counts)
        )
        for c in report.classifications:
            if c.level == "OK":
                continue
            lines.append(f"  [{c.level}] {c.rule_text}")
            lines.append(f"    reason: {c.reason}")
            if c.proposed_rewrite:
                lines.append(f"    proposed: {c.proposed_rewrite}")
        lines.append("")
    return "\n".join(lines)


def _format_json_report(reports: list[FileReport]) -> str:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "tool": "Tools/agent_coordination/sanitize_claude_settings.py",
        "files": [
            {
                "path": str(report.path).replace("\\", "/"),
                "missing": report.missing,
                "parse_error": report.parse_error,
                "summary": _summary(report),
                "classifications": [
                    {
                        "level": c.level,
                        "rule": c.rule_text,
                        "reason": c.reason,
                        "proposed_rewrite": c.proposed_rewrite,
                        "source_field": c.source_field,
                    }
                    for c in report.classifications
                ],
            }
            for report in reports
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def _exit_code(reports: list[FileReport]) -> int:
    for report in reports:
        if report.parse_error:
            return 2
        for c in report.classifications:
            if c.level in {"DANGEROUS", "SECRET", "EXTERNAL_REVIEW"}:
                return 1
    return 0


# ---------------------------------------------------------------------------
# Apply mode
# ---------------------------------------------------------------------------


def _apply_to_file(path: Path, report: FileReport) -> tuple[int, list[str]]:
    """Rewrite STALE_WARN entries in `path` using their proposed_rewrite.

    Returns (number_of_rewrites, error_messages). Refuses to apply if any
    classification is SECRET or DANGEROUS — those need human handling.
    """
    errors: list[str] = []
    blockers = [c for c in report.classifications if c.level in {"SECRET", "DANGEROUS", "EXTERNAL_REVIEW"}]
    if blockers:
        for c in blockers:
            errors.append(f"{path}: refusing to apply because of {c.level}: {c.rule_text}")
        return 0, errors

    rewrites = {
        c.rule_text: c.proposed_rewrite
        for c in report.classifications
        if c.level == "STALE_WARN" and c.proposed_rewrite is not None
    }
    if not rewrites:
        return 0, []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        errors.append(f"{path}: parse error: {exc}")
        return 0, errors

    backup = path.with_suffix(path.suffix + f".backup.{_safe_now()}")
    try:
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    except OSError as exc:
        errors.append(f"{path}: backup failed: {exc}")
        return 0, errors

    rewrite_count = 0

    permissions = data.get("permissions") if isinstance(data, dict) else None
    if isinstance(permissions, dict):
        for key in ("allow", "deny", "ask", "additionalDirectories"):
            entries = permissions.get(key)
            if not isinstance(entries, list):
                continue
            for i, entry in enumerate(entries):
                if isinstance(entry, str) and entry in rewrites:
                    entries[i] = rewrites[entry]
                    rewrite_count += 1

    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return rewrite_count, errors


def _safe_now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for _ in range(10):
        if (current / "AGENTS.md").exists():
            return current
        if current.parent == current:
            break
        current = current.parent
    return start


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sanitize Claude settings files (dry-run by default)")
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--apply", action="store_true",
                        help="Rewrite STALE_WARN entries in place (refuses if SECRET/DANGEROUS/EXTERNAL_REVIEW present).")
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve() if args.repo_root else _find_repo_root(Path.cwd())
    reports = [scan_file(repo_root / target) for target in TARGET_FILES]

    if args.apply:
        total_rewrites = 0
        all_errors: list[str] = []
        for report in reports:
            if report.missing or report.parse_error:
                continue
            rewrites, errors = _apply_to_file(report.path, report)
            total_rewrites += rewrites
            all_errors.extend(errors)
        if all_errors:
            for err in all_errors:
                print(err, file=sys.stderr)
            return 1
        print(f"Applied {total_rewrites} rewrite(s).")
        # Re-scan after apply so the printed report reflects post-apply state.
        reports = [scan_file(repo_root / target) for target in TARGET_FILES]

    if args.format == "json":
        print(_format_json_report(reports))
    else:
        print(_format_text_report(reports))
    return _exit_code(reports)


if __name__ == "__main__":
    sys.exit(main())
