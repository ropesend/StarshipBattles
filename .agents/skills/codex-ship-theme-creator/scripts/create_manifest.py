from __future__ import annotations

import argparse
import json
from pathlib import Path

from theme_common import CLASSES


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Starship Battles ship theme scaffold.")
    parser.add_argument("--theme-root", required=True, help="Output theme directory, e.g. assets/ShipThemes/Voidforged")
    parser.add_argument("--name", required=True, help="Theme display name")
    parser.add_argument("--description", default="", help="Short theme description")
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
        "name": args.name,
        "description": args.description,
        "images": {class_name: f"Skins/{skin}" for class_name, skin, _ in CLASSES},
    }
    with (theme_root / "theme.json").open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=4)
        handle.write("\n")

    print(f"Created theme scaffold at {theme_root}")
    print(f"Manifest classes: {len(CLASSES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
