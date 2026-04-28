from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

TARGET_SIZE = (2048, 2048)


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
from theme_common import CLASSES, load_manifest


def _resolve_theme_root(theme_ref: str | None, explicit_root: str | None) -> Path:
    if explicit_root:
        return Path(explicit_root).resolve()
    if not theme_ref:
        raise ValueError("Provide either a theme name/path or --theme-root.")

    ref_path = Path(theme_ref)
    if ref_path.exists():
        return ref_path.resolve()
    return PROJECT_ROOT / "assets" / "ShipThemes" / theme_ref


def _validate_registry_alignment(errors: list[str]) -> None:
    expected_classes = set(SHIP_CLASSES_WITH_VISUAL_THEMES)
    class_names = {class_name for class_name, _, _ in CLASSES}
    if class_names == expected_classes:
        return
    missing = sorted(expected_classes - class_names)
    extra = sorted(class_names - expected_classes)
    errors.append(f"theme_common.CLASSES drift: missing={missing}, extra={extra}")


def _validate_manifest_shape(manifest: dict, errors: list[str]) -> dict:
    if "images" in manifest:
        errors.append("legacy 'images' schema is not supported; use top-level 'assets'")
    if manifest.get("schema_version") != 1:
        errors.append(f"schema_version is {manifest.get('schema_version')!r}, expected 1")

    image_sizes = manifest.get("image_sizes", {})
    if image_sizes.get("skin") != [2048, 2048]:
        errors.append(f"image_sizes.skin is {image_sizes.get('skin')!r}, expected [2048, 2048]")
    if image_sizes.get("portrait") != [2048, 2048]:
        errors.append(f"image_sizes.portrait is {image_sizes.get('portrait')!r}, expected [2048, 2048]")

    assets = manifest.get("assets", {})
    if not isinstance(assets, dict):
        errors.append("assets must be an object keyed by display-form ship class")
        return {}
    return assets


def _validate_asset_keys(assets: dict, errors: list[str]) -> None:
    expected_classes = set(SHIP_CLASSES_WITH_VISUAL_THEMES)
    actual_classes = set(assets)
    missing = sorted(expected_classes - actual_classes)
    extra = sorted(actual_classes - expected_classes)
    if missing:
        errors.append(f"Missing manifest asset keys: {missing}")
    if extra:
        errors.append(f"Unexpected manifest asset keys: {extra}")


def _relative_png_path(value: object, label: str, errors: list[str]) -> str | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{label} path is missing")
        return None
    path = Path(value)
    if path.is_absolute():
        errors.append(f"{label} path must be relative: {value}")
    if path.suffix.lower() != ".png":
        errors.append(f"{label} path must be PNG: {value}")
    return value


def _image_size(path: Path, label: str, errors: list[str]) -> tuple[int, int] | None:
    if not path.exists():
        errors.append(f"Missing {label}: {path}")
        return None
    with Image.open(path) as image:
        size = image.size
    if size != TARGET_SIZE:
        errors.append(f"{label} {path.name} is {size}, expected 2048x2048")
    return size


def _validate_skin(path: Path, skin_name: str, errors: list[str]) -> bool:
    if _image_size(path, f"Skin {skin_name}", errors) != TARGET_SIZE:
        return False
    with Image.open(path) as image:
        rgba = image.convert("RGBA")
        corners = [
            rgba.getpixel(p)[3]
            for p in [(0, 0), (2047, 0), (0, 2047), (2047, 2047)]
        ]
    if any(corners):
        errors.append(f"Skin {skin_name} has non-transparent corners: {corners}")
        return False
    return True


def _validate_portrait(path: Path, portrait_name: str, errors: list[str]) -> bool:
    return _image_size(path, f"Portrait {portrait_name}", errors) == TARGET_SIZE


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Starship Battles ship theme.")
    parser.add_argument("theme", nargs="?", help="Theme name or theme-root path.")
    parser.add_argument("--theme-root", help="Explicit theme directory path.")
    args = parser.parse_args()

    try:
        theme_root = _resolve_theme_root(args.theme, args.theme_root)
    except ValueError as exc:
        parser.error(str(exc))

    manifest = load_manifest(theme_root)

    errors: list[str] = []
    _validate_registry_alignment(errors)
    assets = _validate_manifest_shape(manifest, errors)
    _validate_asset_keys(assets, errors)

    skin_count = 0
    skin_target_count = 0
    portrait_count = 0
    portrait_target_count = 0
    for class_name, skin_name, portrait_name in CLASSES:
        entry = assets.get(class_name)
        if not isinstance(entry, dict):
            continue

        skin_rel = _relative_png_path(entry.get("skin"), f"{class_name} skin", errors)
        if skin_rel is not None:
            expected_skin_ref = f"Skins/{skin_name}"
            if skin_rel != expected_skin_ref:
                errors.append(f"Manifest skin ref mismatch for {class_name}: {skin_rel!r}")
            skin_count += 1
            if _validate_skin(theme_root / skin_rel, skin_name, errors):
                skin_target_count += 1

        portrait_rel = entry.get("portrait")
        if portrait_rel is not None:
            portrait_ref = _relative_png_path(portrait_rel, f"{class_name} portrait", errors)
            if portrait_ref is not None:
                expected_portrait_ref = f"Portraits/{portrait_name}"
                if portrait_ref != expected_portrait_ref:
                    errors.append(
                        f"Manifest portrait ref mismatch for {class_name}: {portrait_ref!r}"
                    )
                portrait_count += 1
                if _validate_portrait(theme_root / portrait_ref, portrait_name, errors):
                    portrait_target_count += 1

    theme_name = manifest.get("name", theme_root.name)
    print(f"Theme: {theme_name}")
    print(f"schema_version: {manifest.get('schema_version')!r}")
    print(f"manifest keys: {len(assets)}/{len(SHIP_CLASSES_WITH_VISUAL_THEMES)}")
    print(f"skin coverage: {skin_count}/{len(SHIP_CLASSES_WITH_VISUAL_THEMES)}")
    print(f"skin target-size: {skin_target_count}/{skin_count}")
    print(f"portrait coverage: {portrait_count}/{len(SHIP_CLASSES_WITH_VISUAL_THEMES)}")
    print(f"portrait target-size: {portrait_target_count}/{portrait_count}")

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Validation passed for {theme_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
