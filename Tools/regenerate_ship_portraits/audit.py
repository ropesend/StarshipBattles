"""Audit script for ship-theme assets (PROJ-314).

Walks ``assets/images/ship_themes/`` and reports per-theme schema version,
coverage gaps, filename casing violations, and image-size mismatches in
a single table. Read-only — produces no side effects.

Run::

    python -m Tools.regenerate_ship_portraits.audit
    python -m Tools.regenerate_ship_portraits.audit --theme Federation
    python -m Tools.regenerate_ship_portraits.audit --json

Exit codes:
    0 = no findings
    2 = size mismatches or other non-portrait findings
    3 = missing portraits, regardless of other findings
    1 = unexpected script crash
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional


def _find_project_root() -> Path:
    """Find project root by looking for game/ and data/ directories."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "game").is_dir() and (current / "data").is_dir():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")


_PROJECT_ROOT = _find_project_root()
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from game.core.paths import Paths
from game.core.ship_classes import SHIP_CLASSES_WITH_VISUAL_THEMES


_LOWERCASE_UNDERSCORES = re.compile(r"^[a-z0-9_]+\.png$")


@dataclass
class FileFinding:
    """Per-file audit result."""
    relpath: str
    exists: bool
    actual_size: Optional[tuple[int, int]] = None
    declared_size: Optional[tuple[int, int]] = None
    casing_ok: bool = True


@dataclass
class ShipFinding:
    """Per-ship-class audit result within a theme."""
    ship_class: str
    skin: Optional[FileFinding] = None
    portrait: Optional[FileFinding] = None


@dataclass
class ThemeFinding:
    """Per-theme audit result."""
    theme: str
    theme_dir: str
    schema_ok: bool
    schema_version: Optional[int]
    declared_keys: list[str] = field(default_factory=list)
    extras: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    ships: list[ShipFinding] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def _read_actual_size(path: str) -> Optional[tuple[int, int]]:
    """Return the (W, H) of a PNG, or None on decode failure."""
    try:
        from PIL import Image
        with Image.open(path) as img:
            return (int(img.width), int(img.height))
    except Exception:  # Intentional broad catch: audit must not blow up on corrupt files.
        return None


def audit_theme(theme_dir: str) -> ThemeFinding:
    """Audit a single theme directory."""
    theme_name = os.path.basename(theme_dir)
    json_path = os.path.join(theme_dir, "theme.json")
    finding = ThemeFinding(
        theme=theme_name,
        theme_dir=theme_dir,
        schema_ok=False,
        schema_version=None,
    )
    if not os.path.exists(json_path):
        finding.errors.append("theme.json missing")
        return finding

    try:
        with open(json_path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (json.JSONDecodeError, OSError) as e:
        finding.errors.append(f"theme.json unreadable: {e}")
        return finding

    finding.theme = data.get("name", theme_name)
    finding.schema_version = data.get("schema_version")
    image_sizes = data.get("image_sizes") or {}

    if "assets" not in data:
        finding.errors.append("legacy 'images:' schema (PROJ-314)")
        return finding

    finding.schema_ok = True
    assets = data["assets"]
    finding.declared_keys = sorted(assets.keys())
    finding.extras = sorted(set(finding.declared_keys) - SHIP_CLASSES_WITH_VISUAL_THEMES)
    finding.missing = sorted(SHIP_CLASSES_WITH_VISUAL_THEMES - set(finding.declared_keys))

    declared_skin = image_sizes.get("skin")
    declared_portrait = image_sizes.get("portrait")
    declared_skin_tup = (
        (int(declared_skin[0]), int(declared_skin[1]))
        if isinstance(declared_skin, list) and len(declared_skin) == 2
        else None
    )
    declared_portrait_tup = (
        (int(declared_portrait[0]), int(declared_portrait[1]))
        if isinstance(declared_portrait, list) and len(declared_portrait) == 2
        else None
    )

    for ship_class in finding.declared_keys:
        entry = assets[ship_class]
        if not isinstance(entry, dict):
            finding.errors.append(f"{ship_class}: entry not an object")
            continue
        ship_finding = ShipFinding(ship_class=ship_class)
        skin_rel = entry.get("skin")
        if skin_rel:
            ship_finding.skin = _audit_file(theme_dir, skin_rel, declared_skin_tup)
        portrait_rel = entry.get("portrait")
        if portrait_rel:
            ship_finding.portrait = _audit_file(theme_dir, portrait_rel, declared_portrait_tup)
        else:
            ship_finding.portrait = FileFinding(
                relpath="",
                exists=False,
                declared_size=declared_portrait_tup,
                casing_ok=True,
            )
        finding.ships.append(ship_finding)

    return finding


def _audit_file(
    theme_dir: str, relpath: str, declared_size: Optional[tuple[int, int]],
) -> FileFinding:
    """Build a FileFinding for one declared asset."""
    abs_path = os.path.join(theme_dir, relpath)
    exists = os.path.exists(abs_path)
    basename = os.path.basename(relpath)
    casing_ok = bool(_LOWERCASE_UNDERSCORES.fullmatch(basename))
    actual_size = _read_actual_size(abs_path) if exists else None
    return FileFinding(
        relpath=relpath,
        exists=exists,
        actual_size=actual_size,
        declared_size=declared_size,
        casing_ok=casing_ok,
    )


def audit_all(themes_dir: Optional[str] = None) -> list[ThemeFinding]:
    """Audit every theme directory under ``themes_dir`` (default ``Paths.SHIP_THEMES_DIR``)."""
    root = themes_dir or Paths.SHIP_THEMES_DIR
    findings: list[ThemeFinding] = []
    for entry in sorted(os.scandir(root), key=lambda e: e.name):
        if entry.is_dir():
            findings.append(audit_theme(entry.path))
    return findings


def _format_human(findings: list[ThemeFinding]) -> str:
    """Pretty-print the findings as a single human-readable table."""
    out: list[str] = []
    out.append(f"PROJ-314 Ship Theme Audit — {len(findings)} themes\n")
    out.append("=" * 78 + "\n")
    for f in findings:
        out.append(f"\n[{f.theme}]   {f.theme_dir}")
        if not f.schema_ok:
            out.append(f"  SCHEMA: NOT OK  ({'; '.join(f.errors)})")
            continue
        out.append(f"  schema_version={f.schema_version}  declared={len(f.declared_keys)} ships")
        if f.extras:
            out.append(f"  EXTRAS:    {f.extras}")
        if f.missing:
            out.append(f"  MISSING:   {f.missing}")
        skin_missing = [s.ship_class for s in f.ships if s.skin and not s.skin.exists]
        portrait_missing = [s.ship_class for s in f.ships if s.portrait and not s.portrait.exists]
        casing_violations = [
            (s.ship_class, kind, getattr(s, kind).relpath)
            for s in f.ships
            for kind in ("skin", "portrait")
            if getattr(s, kind) and not getattr(s, kind).casing_ok
        ]
        size_mismatches = [
            (s.ship_class, kind,
             f"declared={getattr(s, kind).declared_size} actual={getattr(s, kind).actual_size}")
            for s in f.ships
            for kind in ("skin", "portrait")
            if (getattr(s, kind) and getattr(s, kind).exists
                and getattr(s, kind).declared_size
                and getattr(s, kind).actual_size
                and getattr(s, kind).actual_size != getattr(s, kind).declared_size)
        ]
        if skin_missing:
            out.append(f"  SKIN GAPS: {skin_missing}")
        if portrait_missing:
            out.append(f"  PORTRAIT GAPS: {portrait_missing}")
        if casing_violations:
            out.append(f"  CASING VIOLATIONS: {casing_violations}")
        if size_mismatches:
            out.append(f"  SIZE MISMATCHES: {size_mismatches}")
        if not (skin_missing or portrait_missing or casing_violations
                or size_mismatches or f.extras or f.missing):
            out.append("  CLEAN")
    exit_code = _exit_code_for(findings)
    size_count = _count_size_mismatches(findings)
    missing_portrait_count = _count_missing_portraits(findings)
    out.append(
        f"EXIT {exit_code} - {size_count} size mismatches, "
        f"{missing_portrait_count} missing portraits"
    )
    return "\n".join(out)


def _count_missing_portraits(findings: list[ThemeFinding]) -> int:
    """Return the number of declared ship slots without a real portrait file."""
    return sum(
        1
        for finding in findings
        for ship in finding.ships
        if ship.portrait is not None and not ship.portrait.exists
    )


def _count_size_mismatches(findings: list[ThemeFinding]) -> int:
    """Return the number of files whose actual size differs from declaration."""
    count = 0
    for finding in findings:
        for ship in finding.ships:
            for file_finding in (ship.skin, ship.portrait):
                if (
                    file_finding is not None
                    and file_finding.exists
                    and file_finding.declared_size
                    and file_finding.actual_size
                    and file_finding.actual_size != file_finding.declared_size
                ):
                    count += 1
    return count


def _has_other_findings(findings: list[ThemeFinding]) -> bool:
    """Return True for schema, coverage, casing, or skin findings."""
    for finding in findings:
        if finding.errors or finding.extras or finding.missing:
            return True
        for ship in finding.ships:
            if ship.skin is not None and not ship.skin.exists:
                return True
            for file_finding in (ship.skin, ship.portrait):
                if file_finding is not None and not file_finding.casing_ok:
                    return True
    return False


def _exit_code_for(findings: list[ThemeFinding]) -> int:
    """Return the audit process exit code for a set of findings."""
    if _count_missing_portraits(findings):
        return 3
    if _count_size_mismatches(findings) or _has_other_findings(findings):
        return 2
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entry point for the audit tool."""
    parser = argparse.ArgumentParser(
        prog="audit",
        description="Audit ship-theme assets against the PROJ-314 schema.",
    )
    parser.add_argument(
        "--theme",
        help="Audit a single theme by name (default: all under assets/images/ship_themes/)",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Emit JSON instead of a human-readable table.",
    )
    args = parser.parse_args(argv)

    if args.theme:
        theme_dir = os.path.join(Paths.SHIP_THEMES_DIR, args.theme)
        if not os.path.isdir(theme_dir):
            print(f"Theme directory not found: {theme_dir}", file=sys.stderr)
            return 2
        findings = [audit_theme(theme_dir)]
    else:
        findings = audit_all()

    if args.json:
        print(json.dumps([asdict(f) for f in findings], indent=2))
    else:
        print(_format_human(findings))
    return _exit_code_for(findings)


if __name__ == "__main__":
    raise SystemExit(main())
