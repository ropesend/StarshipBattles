#!/usr/bin/env python3
"""Validate caption sidecar JSON files for the visual assets (PROJ-299).

Walks `assets/images/flags/`, `assets/images/race_portraits/`,
and `assets/images/ship_themes/`, looks up the canonical sidecar location for
each asset, and validates the sidecar against the appropriate schema in
`Tools/captioning/schemas/`.

Usage:
    python Tools/captioning/validate_captions.py [--quiet]

Exit code 0 when all sidecars are present and valid; non-zero otherwise.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Tuple

THIS_DIR = Path(__file__).resolve().parent
SCHEMAS_DIR = THIS_DIR / "schemas"
PROJECT_ROOT = THIS_DIR.parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"


class Status(str, Enum):
    OK = "OK"
    MISSING = "MISSING"
    MALFORMED = "MALFORMED"
    INVALID = "INVALID"


@dataclass
class SidecarReport:
    asset_id: str
    asset_type: str
    path: Path
    status: Status
    details: List[str] = field(default_factory=list)


# ----------------------------------------------------------------------------
# Schema loading + validation
# ----------------------------------------------------------------------------


def load_schema(asset_type: str) -> dict:
    """Load the JSON schema for the given asset type ('flag', 'portrait', 'theme')."""
    path = SCHEMAS_DIR / f"{asset_type}.schema.json"
    if not path.exists():
        raise ValueError(f"Unknown asset type {asset_type!r}; no schema at {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_caption_dict(caption: dict, asset_type: str) -> Tuple[bool, List[str]]:
    """Validate an in-memory caption dict against the schema.

    Returns (ok, errors). `errors` is empty when ok is True.
    """
    errors: List[str] = []
    schema = load_schema(asset_type)

    # schema_version
    expected_version = schema.get("schema_version", 1)
    if caption.get("schema_version") != expected_version:
        errors.append(
            f"schema_version is {caption.get('schema_version')!r}, "
            f"expected {expected_version}"
        )

    # required_fields presence + non-empty
    required = schema.get("required_fields", [])
    for field_name in required:
        if field_name not in caption:
            errors.append(f"missing required field {field_name!r}")
            continue
        value = caption[field_name]
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append(f"required field {field_name!r} is empty")

    # enum values
    enums = schema.get("enums", {})
    for field_name, allowed in enums.items():
        if field_name in caption:
            value = caption[field_name]
            if value not in allowed:
                errors.append(
                    f"field {field_name!r} value {value!r} is not in allowed enum {allowed}"
                )

    return (not errors, errors)


def validate_sidecar_path(path: Path, asset_type: str) -> SidecarReport:
    """Validate a sidecar at the given path against the schema for `asset_type`."""
    asset_id = path.stem.replace(".caption", "")
    if not path.exists():
        return SidecarReport(
            asset_id=asset_id,
            asset_type=asset_type,
            path=path,
            status=Status.MISSING,
        )

    try:
        caption = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return SidecarReport(
            asset_id=asset_id,
            asset_type=asset_type,
            path=path,
            status=Status.MALFORMED,
            details=[str(e)],
        )

    ok, errors = validate_caption_dict(caption, asset_type)
    return SidecarReport(
        asset_id=asset_id,
        asset_type=asset_type,
        path=path,
        status=Status.OK if ok else Status.INVALID,
        details=errors,
    )


# ----------------------------------------------------------------------------
# Asset discovery
# ----------------------------------------------------------------------------


def discover_flags() -> List[Tuple[str, Path]]:
    """Returns [(flag_id, sidecar_path), ...] for every flag in assets/."""
    base = ASSETS_DIR / "Images" / "flags"
    if not base.exists():
        return []
    out: List[Tuple[str, Path]] = []
    for flag_dir in sorted(base.iterdir()):
        if not flag_dir.is_dir() or not flag_dir.name.startswith("flag_"):
            continue
        sidecar = flag_dir / f"{flag_dir.name}.caption.json"
        out.append((flag_dir.name, sidecar))
    return out


def discover_portraits() -> List[Tuple[str, Path]]:
    """Returns [(portrait_filename, sidecar_path), ...] for every portrait."""
    base = ASSETS_DIR / "Images" / "race_portraits"
    if not base.exists():
        return []
    out: List[Tuple[str, Path]] = []
    for path in sorted(base.iterdir()):
        if path.suffix.lower() not in (".jpg", ".jpeg", ".png"):
            continue
        # Skip caption files themselves.
        if path.name.endswith(".caption.json"):
            continue
        sidecar = path.with_name(path.name + ".caption.json")
        out.append((path.name, sidecar))
    return out


def discover_themes() -> List[Tuple[str, Path]]:
    """Returns [(theme_name, sidecar_path), ...] for every ship theme."""
    base = ASSETS_DIR / "ship_themes"
    if not base.exists():
        return []
    out: List[Tuple[str, Path]] = []
    for theme_dir in sorted(base.iterdir()):
        if not theme_dir.is_dir():
            continue
        # A theme dir is identified by the presence of theme.json.
        if not (theme_dir / "theme.json").exists():
            continue
        sidecar = theme_dir / "theme.caption.json"
        out.append((theme_dir.name, sidecar))
    return out


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


def run_validation() -> List[SidecarReport]:
    reports: List[SidecarReport] = []
    for flag_id, sidecar in discover_flags():
        reports.append(validate_sidecar_path(sidecar, "flag"))
    for portrait_id, sidecar in discover_portraits():
        reports.append(validate_sidecar_path(sidecar, "portrait"))
    for theme_id, sidecar in discover_themes():
        reports.append(validate_sidecar_path(sidecar, "theme"))
    return reports


def print_summary(reports: List[SidecarReport], quiet: bool = False) -> None:
    by_status: dict = {s: 0 for s in Status}
    for r in reports:
        by_status[r.status] += 1

    total = len(reports)
    print(f"Caption sidecar audit — {total} assets")
    print(
        f"  OK: {by_status[Status.OK]:>3} | "
        f"MISSING: {by_status[Status.MISSING]:>3} | "
        f"MALFORMED: {by_status[Status.MALFORMED]:>3} | "
        f"INVALID: {by_status[Status.INVALID]:>3}"
    )

    if quiet:
        return

    bad = [r for r in reports if r.status != Status.OK]
    if not bad:
        return
    print()
    print("Issues:")
    for r in bad:
        rel = r.path.relative_to(PROJECT_ROOT) if r.path.is_absolute() else r.path
        print(f"  [{r.status.value:9}] {r.asset_type:8} {r.asset_id}")
        print(f"      sidecar: {rel}")
        for detail in r.details:
            print(f"        - {detail}")


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quiet", action="store_true", help="Print summary only.")
    args = parser.parse_args(argv)

    reports = run_validation()
    print_summary(reports, quiet=args.quiet)

    has_issues = any(r.status != Status.OK for r in reports)
    return 1 if has_issues else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
