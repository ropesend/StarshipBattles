from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TARGET_SIZE = 2048


def _find_project_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "game").is_dir() and (candidate / "assets").is_dir():
            return candidate
    raise RuntimeError(f"Could not find project root from {start}")


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = _find_project_root(SCRIPT_DIR)
for path in (str(PROJECT_ROOT), str(SCRIPT_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)

from game.core.ship_classes import SHIP_CLASSES_WITH_VISUAL_THEMES
from theme_common import CLASSES


def _build_assets(include_portraits: bool) -> dict[str, dict[str, object]]:
    expected_classes = set(SHIP_CLASSES_WITH_VISUAL_THEMES)
    class_names = {class_name for class_name, _, _ in CLASSES}
    if class_names != expected_classes:
        missing = sorted(expected_classes - class_names)
        extra = sorted(class_names - expected_classes)
        raise RuntimeError(
            "theme_common.CLASSES drifted from ship class registry: "
            f"missing={missing}, extra={extra}"
        )

    assets: dict[str, dict[str, object]] = {}
    for class_name, skin, portrait in CLASSES:
        entry: dict[str, object] = {
            "skin": f"Skins/{skin}",
            "scale": 1.0,
        }
        if include_portraits:
            entry["portrait"] = f"Portraits/{portrait}"
        assets[class_name] = entry
    return assets


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Starship Battles ship theme scaffold.")
    parser.add_argument("--theme-root", required=True, help="Output theme directory, e.g. assets/Images/ShipThemes/Voidforged")
    parser.add_argument("--name", required=True, help="Theme display name")
    parser.add_argument("--description", default="", help="Short theme description")
    parser.add_argument(
        "--omit-portraits",
        action="store_true",
        help="Do not declare portrait paths in theme.json.",
    )
    args = parser.parse_args()

    theme_root = Path(args.theme_root)
    for child in [
        "Skins",
        "Portraits",
        "Production",
        "Production/skin_sources",
        "Production/skin_alpha",
        "Production/portrait_sources",
    ]:
        (theme_root / child).mkdir(parents=True, exist_ok=True)

    manifest = {
        "schema_version": 1,
        "name": args.name,
        "description": args.description,
        "image_sizes": {
            "skin": [TARGET_SIZE, TARGET_SIZE],
            "portrait": [TARGET_SIZE, TARGET_SIZE],
        },
        "assets": _build_assets(include_portraits=not args.omit_portraits),
    }
    with (theme_root / "theme.json").open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=4)
        handle.write("\n")

    print(f"Created theme scaffold at {theme_root}")
    print(f"Manifest classes: {len(CLASSES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
