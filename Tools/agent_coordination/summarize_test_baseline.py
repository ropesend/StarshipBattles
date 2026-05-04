#!/usr/bin/env python3
"""Aggregate test baseline counts and per-install verification receipts."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    _here = Path(__file__).resolve()
    for _ in range(6):
        if (_here.parent / "AGENTS.md").exists():
            sys.path.insert(0, str(_here.parent))
            break
        _here = _here.parent

SUMMARY_SCHEMA_VERSION = 1
BASELINE_FILE = Path("AgentCoordination") / "generated" / "test_baseline.json"
BY_INSTALL_DIR = Path("AgentCoordination") / "generated" / "test_baseline" / "by_install"
SUMMARY_FILE = Path("AgentCoordination") / "generated" / "test_baseline" / "summary.json"


def _read_json(path: Path) -> dict[str, object] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"warning: skipping malformed {path}: {exc}", file=sys.stderr)
        return None
    return payload if isinstance(payload, dict) else None


def _load_baseline(repo_root: Path) -> dict[str, object]:
    payload = _read_json(repo_root / BASELINE_FILE)
    return payload if payload is not None else {}


def _load_verifications(repo_root: Path) -> dict[str, dict[str, object]]:
    by_install: dict[str, dict[str, object]] = {}
    directory = repo_root / BY_INSTALL_DIR
    if not directory.is_dir():
        return by_install

    for path in sorted(directory.glob("*.json")):
        payload = _read_json(path)
        if payload is None:
            continue
        install_id = payload.get("install_id")
        if not isinstance(install_id, str) or not install_id:
            print(f"warning: skipping malformed {path.name}: missing install_id", file=sys.stderr)
            continue
        by_install[install_id] = payload
    return by_install


def _latest_verification(by_install: dict[str, dict[str, object]]) -> tuple[str, dict[str, object] | None]:
    latest_install_id = ""
    latest_payload: dict[str, object] | None = None
    latest_verified_at = ""
    for install_id, payload in by_install.items():
        verified_at = payload.get("verified_at")
        if isinstance(verified_at, str) and verified_at > latest_verified_at:
            latest_install_id = install_id
            latest_payload = payload
            latest_verified_at = verified_at
    return latest_install_id, latest_payload


def build_summary(repo_root: Path) -> dict[str, object]:
    baseline = _load_baseline(repo_root)
    by_install = _load_verifications(repo_root)
    latest_install_id, latest_payload = _latest_verification(by_install)
    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "baseline": baseline,
        "verification": {
            "by_install": by_install,
            "last_verified_at": latest_payload.get("verified_at", "") if latest_payload else "",
            "last_verified_install_id": latest_install_id,
            "last_verified_git_sha": latest_payload.get("git_sha", "") if latest_payload else "",
        },
    }


def write_summary(repo_root: Path) -> None:
    summary_path = repo_root / SUMMARY_FILE
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        json.dumps(build_summary(repo_root), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Aggregate test baseline verification receipts")
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--stdout", action="store_true", help="Print summary JSON instead of writing summary.json")
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve() if args.repo_root else Path.cwd()
    if args.stdout:
        print(json.dumps(build_summary(repo_root), indent=2, sort_keys=True))
    else:
        write_summary(repo_root)
        print(f"Wrote {repo_root / SUMMARY_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
