import argparse
import csv
import json
import shutil
from collections import deque
from pathlib import Path

from PIL import Image, ImageFilter

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None


COMPONENT_SIZES = [2048, 1024, 512, 256, 128, 64]
SOURCE_SIZE = 1024
SOURCE_PREFIX = f"{SOURCE_SIZE}Portrait_Comp_"
DEFAULT_THRESHOLD = 32
DEFAULT_REVIEW_THRESHOLD = 80


def find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "game").is_dir() and (current / "assets").is_dir():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")


PROJECT_ROOT = find_project_root()
COMPONENTS_ROOT = PROJECT_ROOT / "assets" / "Images" / "Components"
SOURCE_DIR = COMPONENTS_ROOT / f"Components {SOURCE_SIZE}"
STAGING_ROOT = COMPONENTS_ROOT / "_processed_preview"
STAGING_ROOT_V2 = COMPONENTS_ROOT / "_processed_preview_v2"
STAGING_ROOT_V3 = COMPONENTS_ROOT / "_processed_preview_v3"


def target_name(source_name: str, size: int) -> str:
    if source_name.startswith(SOURCE_PREFIX):
        return source_name.replace(str(SOURCE_SIZE), str(size), 1)
    return f"{size}_{source_name}"


def border_values(image: Image.Image) -> list[int]:
    px = image.load()
    width, height = image.size
    values = []
    for x in range(width):
        values.append(max(px[x, 0][:3]))
        values.append(max(px[x, height - 1][:3]))
    for y in range(height):
        values.append(max(px[0, y][:3]))
        values.append(max(px[width - 1, y][:3]))
    values.sort()
    return values


def percentile(values: list[int], pct: float) -> int:
    if not values:
        return 0
    index = min(len(values) - 1, max(0, int(len(values) * pct)))
    return values[index]


def remove_edge_connected_dark_background(
    image: Image.Image,
    threshold: int,
    feather_radius: float,
) -> tuple[Image.Image, int]:
    rgba = image.convert("RGBA")
    width, height = rgba.size
    pixels = rgba.load()
    dark = bytearray(width * height)

    for y in range(height):
        row = y * width
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a and max(r, g, b) <= threshold:
                dark[row + x] = 1

    background = bytearray(width * height)
    queue: deque[int] = deque()

    def seed(index: int) -> None:
        if dark[index] and not background[index]:
            background[index] = 1
            queue.append(index)

    last_row = (height - 1) * width
    for x in range(width):
        seed(x)
        seed(last_row + x)
    for y in range(height):
        row = y * width
        seed(row)
        seed(row + width - 1)

    while queue:
        index = queue.popleft()
        x = index % width

        left = index - 1
        if x and dark[left] and not background[left]:
            background[left] = 1
            queue.append(left)

        right = index + 1
        if x < width - 1 and dark[right] and not background[right]:
            background[right] = 1
            queue.append(right)

        up = index - width
        if up >= 0 and dark[up] and not background[up]:
            background[up] = 1
            queue.append(up)

        down = index + width
        if down < len(dark) and dark[down] and not background[down]:
            background[down] = 1
            queue.append(down)

    removed_count = sum(background)
    if not removed_count:
        return rgba, 0

    object_alpha = bytearray(len(background))
    for index, is_background in enumerate(background):
        object_alpha[index] = 0 if is_background else 255

    mask = Image.frombytes("L", (width, height), bytes(object_alpha))
    if feather_radius > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(feather_radius))

    original_alpha = rgba.getchannel("A")
    alpha_data = bytes(
        (base * keep) // 255
        for base, keep in zip(original_alpha.tobytes(), mask.tobytes())
    )
    rgba.putalpha(Image.frombytes("L", (width, height), alpha_data))
    return rgba, removed_count


def remove_grabcut_background(
    image: Image.Image,
    threshold: int,
    feather_radius: float,
    border: int = 10,
    iterations: int = 6,
) -> tuple[Image.Image, int]:
    rgba, foreground = create_grabcut_foreground_mask(
        image,
        threshold=threshold,
        border=border,
        iterations=iterations,
    )
    return apply_alpha_mask(rgba, foreground, feather_radius)


def create_grabcut_foreground_mask(
    image: Image.Image,
    threshold: int,
    border: int = 10,
    iterations: int = 6,
) -> tuple[Image.Image, "np.ndarray"]:
    if cv2 is None or np is None:
        raise RuntimeError("OpenCV and NumPy are required for --method grabcut")

    rgba = image.convert("RGBA")
    rgb = np.array(rgba.convert("RGB"))
    alpha = np.array(rgba.getchannel("A"))
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    height, width = alpha.shape

    max_channel = rgb.max(axis=2)
    min_channel = rgb.min(axis=2)
    saturation_proxy = max_channel - min_channel

    non_dark = (max_channel > threshold) & (alpha > 0)
    coords = np.argwhere(non_dark)
    if coords.size == 0:
        return rgba, np.zeros((height, width), dtype="uint8")

    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0)
    pad = 8
    x0 = max(1, int(x0) - pad)
    y0 = max(1, int(y0) - pad)
    x1 = min(width - 2, int(x1) + pad)
    y1 = min(height - 2, int(y1) + pad)

    mask = np.full((height, width), cv2.GC_PR_BGD, dtype=np.uint8)
    mask[y0 : y1 + 1, x0 : x1 + 1] = cv2.GC_PR_FGD

    # Strong background seeds: image edges and near-black pixels. The near-black
    # seed handles enclosed black pockets that an edge flood-fill cannot reach.
    edge = np.zeros((height, width), dtype=bool)
    edge[:border, :] = True
    edge[-border:, :] = True
    edge[:, :border] = True
    edge[:, -border:] = True
    mask[edge] = cv2.GC_BGD
    mask[(max_channel <= max(10, threshold // 2)) & (saturation_proxy <= 10)] = cv2.GC_BGD
    mask[(max_channel <= threshold) & (saturation_proxy <= 18)] = cv2.GC_PR_BGD

    # Strong foreground seeds: bright/colorful/details-rich component material.
    # This protects dark metal connected to lit object areas better than the v1
    # flood-fill, while still allowing black void pockets to be removed.
    strong_foreground = (
        ((max_channel >= 72) & (saturation_proxy >= 18))
        | (max_channel >= 118)
    ) & (alpha > 0)
    mask[strong_foreground] = cv2.GC_FGD
    mask[edge] = cv2.GC_BGD

    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)
    cv2.grabCut(
        bgr,
        mask,
        None,
        bgd_model,
        fgd_model,
        iterations,
        cv2.GC_INIT_WITH_MASK,
    )

    foreground = np.where(
        (mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD),
        255,
        0,
    ).astype("uint8")

    kernel = np.ones((3, 3), np.uint8)
    foreground = cv2.morphologyEx(foreground, cv2.MORPH_OPEN, kernel, iterations=1)
    foreground = cv2.morphologyEx(foreground, cv2.MORPH_CLOSE, kernel, iterations=2)
    return rgba, foreground


def apply_alpha_mask(
    rgba: Image.Image,
    foreground: "np.ndarray",
    feather_radius: float,
) -> tuple[Image.Image, int]:
    width, height = rgba.size
    foreground_image = Image.fromarray(foreground)
    if feather_radius > 0:
        foreground_image = foreground_image.filter(ImageFilter.GaussianBlur(feather_radius))

    original_alpha = rgba.getchannel("A")
    alpha_data = bytes(
        (base * keep) // 255
        for base, keep in zip(original_alpha.tobytes(), foreground_image.tobytes())
    )
    rgba.putalpha(Image.frombytes("L", (width, height), alpha_data))
    removed_count = alpha_data.count(0)
    return rgba, removed_count


def remove_hybrid_background(
    image: Image.Image,
    threshold: int,
    feather_radius: float,
) -> tuple[Image.Image, int]:
    if cv2 is None or np is None:
        raise RuntimeError("OpenCV and NumPy are required for --method hybrid")

    rgba, grabcut_mask = create_grabcut_foreground_mask(
        image,
        threshold=threshold,
        border=10,
        iterations=6,
    )
    rgb = np.array(rgba.convert("RGB"))
    original_alpha = np.array(rgba.getchannel("A"))
    height, width = original_alpha.shape

    max_channel = rgb.max(axis=2).astype("float32")
    min_channel = rgb.min(axis=2).astype("float32")
    saturation_proxy = max_channel - min_channel
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    gradient = cv2.Laplacian(gray, cv2.CV_32F)
    gradient = np.abs(gradient)

    foreground = grabcut_mask > 0
    coords = np.argwhere(foreground)
    if coords.size == 0:
        empty = rgba.copy()
        empty.putalpha(Image.new("L", rgba.size, 0))
        return empty, width * height

    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0)
    pad = 34
    region = np.zeros((height, width), dtype=bool)
    region[
        max(0, y0 - pad) : min(height, y1 + pad + 1),
        max(0, x0 - pad) : min(width, x1 + pad + 1),
    ] = True

    kernel_3 = np.ones((3, 3), np.uint8)
    kernel_9 = np.ones((9, 9), np.uint8)
    near_foreground = cv2.dilate(foreground.astype("uint8"), kernel_9, iterations=2) > 0

    dim_detail_candidates = (
        region
        & ~foreground
        & (original_alpha > 0)
        & (max_channel > 20)
        & (max_channel < 100)
        & (((saturation_proxy > 18) & (gradient > 5)) | (gradient > 16))
    )

    kept_dim = np.zeros_like(foreground)
    labels_count, labels, stats, _ = cv2.connectedComponentsWithStats(
        dim_detail_candidates.astype("uint8"),
        8,
    )
    for label in range(1, labels_count):
        area = stats[label, cv2.CC_STAT_AREA]
        if area < 12:
            continue
        component = labels == label
        if not np.any(component & near_foreground):
            continue
        mean_gradient = float(gradient[component].mean())
        mean_saturation = float(saturation_proxy[component].mean())
        if area > 12000 and mean_gradient < 16:
            continue
        if mean_gradient < 8 and mean_saturation < 22:
            continue
        if np.any(component & near_foreground):
            kept_dim |= component

    object_mask = foreground | kept_dim
    object_mask = cv2.morphologyEx(
        object_mask.astype("uint8") * 255,
        cv2.MORPH_CLOSE,
        kernel_3,
        iterations=1,
    ) > 0

    wider_near_foreground = cv2.dilate(object_mask.astype("uint8"), kernel_9, iterations=3) > 0
    aura = (
        wider_near_foreground
        & ~object_mask
        & (original_alpha > 0)
        & (max_channel > 20)
        & (max_channel < 170)
        & (saturation_proxy > 18)
    )

    alpha = np.zeros((height, width), dtype="uint8")
    alpha[object_mask] = 255

    # Conservative glow treatment: only add faint semi-transparent colored aura
    # outside the object mask. Do not alter solid object pixels here.
    glow_alpha = np.clip((max_channel - 15) * 1.4, 0, 90).astype("uint8")
    alpha[aura] = np.maximum(alpha[aura], glow_alpha[aura])

    alpha[(max_channel <= 12) & (saturation_proxy <= 12)] = 0

    out_rgb = rgb.copy().astype("float32")
    result = Image.fromarray(out_rgb.astype("uint8"), mode="RGB").convert("RGBA")
    if feather_radius > 0:
        alpha_image = Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(feather_radius))
        alpha = np.array(alpha_image)
    alpha = ((alpha.astype("uint16") * original_alpha.astype("uint16")) // 255).astype("uint8")
    result.putalpha(Image.fromarray(alpha))
    return result, int((alpha == 0).sum())


def write_resized_versions(
    master: Image.Image,
    source_name: str,
    output_root: Path,
    sizes: list[int] | None = None,
) -> None:
    resampling = Image.Resampling.LANCZOS
    for size in sizes or COMPONENT_SIZES:
        target_dir = output_root / f"Components {size}"
        target_dir.mkdir(parents=True, exist_ok=True)
        if master.size == (size, size):
            resized = master
        else:
            resized = master.resize((size, size), resampling)
        resized.save(target_dir / target_name(source_name, size))


def process_images(
    source_dir: Path,
    output_root: Path,
    threshold: int,
    review_threshold: int,
    feather_radius: float,
    limit: int,
    force: bool,
    method: str,
    sizes: list[int] | None = None,
) -> dict:
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source_dir}")

    output_root.mkdir(parents=True, exist_ok=True)
    reports_dir = output_root / "reports"
    manifest_path = output_root / "review_manifest.json"
    reports_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(source_dir.glob("*.png"))
    if limit:
        files = files[:limit]

    rows = []
    manifest = {
        "source_dir": str(source_dir),
        "staging_root": str(output_root),
        "threshold": threshold,
        "review_threshold": review_threshold,
        "feather_radius": feather_radius,
        "method": method,
        "images": {},
    }

    counts = {"processed": 0, "skipped": 0, "review": 0, "unchanged": 0}

    for index, path in enumerate(files, start=1):
        image = Image.open(path).convert("RGBA")
        if image.size != (SOURCE_SIZE, SOURCE_SIZE):
            status = "review"
            action = "unexpected_dimensions"
            result = image
            removed = 0
        else:
            values = border_values(image)
            p95 = percentile(values, 0.95)
            p99 = percentile(values, 0.99)
            if p95 <= threshold or (method in {"grabcut", "hybrid"} and p95 <= review_threshold):
                status = "processed"
                action = f"{method}_background_removed"
                if method == "edge":
                    result, removed = remove_edge_connected_dark_background(
                        image,
                        threshold=threshold,
                        feather_radius=feather_radius,
                    )
                elif method == "grabcut":
                    result, removed = remove_grabcut_background(
                        image,
                        threshold=threshold,
                        feather_radius=feather_radius,
                    )
                elif method == "hybrid":
                    result, removed = remove_hybrid_background(
                        image,
                        threshold=threshold,
                        feather_radius=min(feather_radius, 1.0),
                    )
                else:
                    raise ValueError(f"Unknown method: {method}")
            elif p95 <= review_threshold:
                status = "review"
                action = "copied_needs_review"
                result = image
                removed = 0
            else:
                status = "skipped"
                action = "copied_no_dark_edge_background"
                result = image
                removed = 0

        write_resized_versions(result, path.name, output_root, sizes=sizes)
        counts[status] = counts.get(status, 0) + 1
        if removed == 0 and status == "processed":
            counts["unchanged"] += 1

        row = {
            "filename": path.name,
            "status": status,
            "action": action,
            "removed_pixels": removed,
            "width": image.width,
            "height": image.height,
        }
        rows.append(row)
        manifest["images"][path.name] = {
            "processor_status": status,
            "review_status": "unreviewed",
            "action": action,
            "removed_pixels": removed,
            "notes": "",
        }

        print(f"[{index}/{len(files)}] {path.name}: {status} ({action})")

    report_csv = reports_dir / "processing_report.csv"
    with report_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["filename", "status", "action", "removed_pixels", "width", "height"],
        )
        writer.writeheader()
        writer.writerows(rows)

    report_json = reports_dir / "processing_report.json"
    report_json.write_text(json.dumps({"counts": counts, "images": rows}, indent=2), encoding="utf-8")

    if manifest_path.exists() and not force:
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        for filename, old_entry in existing.get("images", {}).items():
            if filename in manifest["images"]:
                manifest["images"][filename]["review_status"] = old_entry.get(
                    "review_status",
                    "unreviewed",
                )
                manifest["images"][filename]["notes"] = old_entry.get("notes", "")

    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"counts": counts, "report_csv": str(report_csv), "manifest": str(manifest_path)}


def promote_assets(staging_root: Path, components_root: Path, backup: bool) -> None:
    if not staging_root.exists():
        raise FileNotFoundError(f"Staging directory does not exist: {staging_root}")

    if backup:
        backup_root = components_root / "_backup_before_transparency"
        backup_root.mkdir(parents=True, exist_ok=True)
        for size in COMPONENT_SIZES:
            source = components_root / f"Components {size}"
            target = backup_root / f"Components {size}"
            if source.exists() and not target.exists():
                shutil.copytree(source, target)

    for size in COMPONENT_SIZES:
        source = staging_root / f"Components {size}"
        target = components_root / f"Components {size}"
        if not source.exists():
            raise FileNotFoundError(f"Missing staged size directory: {source}")
        target.mkdir(parents=True, exist_ok=True)
        for image_path in source.glob("*.png"):
            shutil.copy2(image_path, target / image_path.name)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove edge-connected black backgrounds from component images and build size variants."
    )
    parser.add_argument("--source", type=Path, default=SOURCE_DIR)
    parser.add_argument("--output", type=Path, default=STAGING_ROOT)
    parser.add_argument("--method", choices=["edge", "grabcut", "hybrid"], default="edge")
    parser.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD)
    parser.add_argument("--review-threshold", type=int, default=DEFAULT_REVIEW_THRESHOLD)
    parser.add_argument("--feather", type=float, default=1.5)
    parser.add_argument("--limit", type=int, default=0, help="Process only the first N images.")
    parser.add_argument("--masters-only", action="store_true", help="Write only the 1024 master output.")
    parser.add_argument("--force-manifest", action="store_true", help="Reset existing review decisions.")
    parser.add_argument("--promote", action="store_true", help="Copy staged files into live component folders.")
    parser.add_argument("--backup", action="store_true", help="Backup live component folders before promotion.")
    args = parser.parse_args()
    if args.method == "grabcut" and args.output == STAGING_ROOT:
        args.output = STAGING_ROOT_V2
    if args.method == "hybrid" and args.output == STAGING_ROOT:
        args.output = STAGING_ROOT_V3
        args.masters_only = True

    if args.promote:
        promote_assets(args.output, COMPONENTS_ROOT, backup=args.backup)
        print(f"Promoted staged assets from {args.output}")
        return

    result = process_images(
        source_dir=args.source,
        output_root=args.output,
        threshold=args.threshold,
        review_threshold=args.review_threshold,
        feather_radius=args.feather,
        limit=args.limit,
        force=args.force_manifest,
        method=args.method,
        sizes=[SOURCE_SIZE] if args.masters_only else None,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
