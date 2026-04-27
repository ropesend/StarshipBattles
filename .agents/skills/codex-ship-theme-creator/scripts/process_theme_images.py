from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from theme_common import CLASSES, expected_portrait_names, expected_skin_names


def remove_green_key(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    width, height = rgba.size
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            greenish = g > 145 and g > r * 1.35 and g > b * 1.35
            bright_key = g > 190 and r < 110 and b < 110
            if greenish or bright_key:
                pixels[x, y] = (r, g, b, 0)
            elif a:
                # Light despill on antialiased edges.
                excess = max(0, g - max(r, b))
                if excess:
                    pixels[x, y] = (r, max(max(r, b), g - int(excess * 0.75)), b, a)
    return rgba


def fit_on_canvas(image: Image.Image, size: int, mode: str) -> Image.Image:
    if mode == "skins":
        image = remove_green_key(image)
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        bbox = image.getbbox()
        if bbox:
            image = image.crop(bbox)
        scale = min(size * 0.90 / image.width, size * 0.90 / image.height)
        resized = image.resize((max(1, int(image.width * scale)), max(1, int(image.height * scale))), Image.Resampling.LANCZOS)
        canvas.alpha_composite(resized, ((size - resized.width) // 2, (size - resized.height) // 2))
        return canvas

    rgb = image.convert("RGB")
    scale = max(size / rgb.width, size / rgb.height)
    resized = rgb.resize((max(1, int(rgb.width * scale)), max(1, int(rgb.height * scale))), Image.Resampling.LANCZOS)
    left = (resized.width - size) // 2
    top = (resized.height - size) // 2
    return resized.crop((left, top, left + size, top + size))


def make_contact_sheet(files: list[Path], out_path: Path, thumb: int = 180, label: int = 28, cols: int = 5) -> None:
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb, rows * (thumb + label)), (22, 22, 28))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, path in enumerate(files):
        img = Image.open(path).convert("RGBA")
        img.thumbnail((thumb, thumb), Image.Resampling.LANCZOS)
        x = (index % cols) * thumb
        y = (index // cols) * (thumb + label)
        preview = Image.new("RGBA", (thumb, thumb), (22, 22, 28, 255))
        preview.alpha_composite(img, ((thumb - img.width) // 2, (thumb - img.height) // 2))
        sheet.paste(preview.convert("RGB"), (x, y))
        draw.text((x + 4, y + thumb + 4), path.stem.replace("_Portrait", ""), fill=(255, 255, 255), font=font)
    sheet.save(out_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize generated ship theme images.")
    parser.add_argument("--theme-root", required=True)
    parser.add_argument("--mode", choices=["skins", "portraits"], required=True)
    args = parser.parse_args()

    theme_root = Path(args.theme_root)
    if args.mode == "skins":
        source_dir = theme_root / "Production" / "skin_sources"
        out_dir = theme_root / "Skins"
        names = expected_skin_names()
        size = 2048
        contact = theme_root / "Production" / "contact_sheet_skins.png"
        ext = ".png"
    else:
        source_dir = theme_root / "Production" / "portrait_sources"
        out_dir = theme_root / "Portraits"
        names = expected_portrait_names()
        size = 1024
        contact = theme_root / "Production" / "contact_sheet_portraits.png"
        ext = ".jpg"

    out_dir.mkdir(parents=True, exist_ok=True)
    processed: list[Path] = []
    missing: list[str] = []
    portrait_sources = {portrait: skin for _, skin, portrait in CLASSES}
    for name in names:
        source_name = name if args.mode == "skins" else portrait_sources[name]
        source = source_dir / source_name
        if not source.exists() and args.mode == "portraits":
            # Also accept portrait filenames in source dir.
            source = source_dir / name.replace(".jpg", ".png")
        if not source.exists():
            missing.append(source_name)
            continue
        image = Image.open(source)
        normalized = fit_on_canvas(image, size, args.mode)
        out_path = out_dir / (name if args.mode == "portraits" else Path(name).with_suffix(ext).name)
        normalized.save(out_path)
        processed.append(out_path)

    if missing:
        raise SystemExit(f"Missing {args.mode} source files: {', '.join(missing)}")

    make_contact_sheet(sorted(processed), contact)
    print(f"Processed {len(processed)} {args.mode}")
    print(f"Contact sheet: {contact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
