from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from theme_common import CLASSES, load_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Starship Battles ship theme.")
    parser.add_argument("--theme-root", required=True)
    args = parser.parse_args()
    theme_root = Path(args.theme_root)
    manifest = load_manifest(theme_root)

    errors: list[str] = []
    images = manifest.get("images", {})
    for class_name, skin_name, portrait_name in CLASSES:
        ref = images.get(class_name)
        if ref != f"Skins/{skin_name}":
            errors.append(f"Manifest ref mismatch for {class_name}: {ref!r}")
            continue
        skin_path = theme_root / ref
        if not skin_path.exists():
            errors.append(f"Missing skin: {skin_path}")
            continue
        skin = Image.open(skin_path).convert("RGBA")
        if skin.size != (2048, 2048):
            errors.append(f"Skin {skin_name} is {skin.size}, expected 2048x2048")
        corners = [skin.getpixel(p)[3] for p in [(0, 0), (2047, 0), (0, 2047), (2047, 2047)]]
        if any(corners):
            errors.append(f"Skin {skin_name} has non-transparent corners: {corners}")

        portrait_path = theme_root / "Portraits" / portrait_name
        if not portrait_path.exists():
            errors.append(f"Missing portrait: {portrait_path}")
            continue
        portrait = Image.open(portrait_path)
        if portrait.size != (1024, 1024):
            errors.append(f"Portrait {portrait_name} is {portrait.size}, expected 1024x1024")

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Validation passed for {manifest.get('name', theme_root.name)}")
    print(f"Classes: {len(CLASSES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
