import json
import os
import subprocess
import sys
import time
import argparse
from pathlib import Path

from PIL import Image


def find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "game").is_dir() and (current / "assets").is_dir():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")


PROJECT_ROOT = find_project_root()
COMPONENTS_ROOT = PROJECT_ROOT / "assets" / "Images" / "Components"
SOURCE_DIR = COMPONENTS_ROOT / "1024"
OUTPUT_ROOT = COMPONENTS_ROOT / "_ai_recreate_preview"

CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
IMAGE_GEN = CODEX_HOME / "skills" / ".system" / "imagegen" / "scripts" / "image_gen.py"
REMOVE_CHROMA = CODEX_HOME / "skills" / ".system" / "imagegen" / "scripts" / "remove_chroma_key.py"

SKIP_FILENAMES = {
    "1024Portrait_Comp_001.png",
    "1024Portrait_Comp_002.png",
    "1024Portrait_Comp_003.png",
}


def ensure_api_key() -> None:
    if os.environ.get("OPENAI_API_KEY"):
        return
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "[Environment]::GetEnvironmentVariable('OPENAI_API_KEY','User')",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        result = None

    key = result.stdout.strip() if result else ""
    if key:
        os.environ["OPENAI_API_KEY"] = key
        return
    raise RuntimeError("OPENAI_API_KEY is not set in this process or the Windows user environment.")


def border_p95(path: Path) -> int:
    image = Image.open(path).convert("RGBA")
    width, height = image.size
    px = image.load()
    values = []
    for x in range(width):
        values.append(max(px[x, 0][:3]))
        values.append(max(px[x, height - 1][:3]))
    for y in range(height):
        values.append(max(px[0, y][:3]))
        values.append(max(px[width - 1, y][:3]))
    values.sort()
    return values[int(len(values) * 0.95)]


def eligible_files(limit: int) -> list[Path]:
    files = []
    for path in sorted(SOURCE_DIR.glob("*.png")):
        if path.name in SKIP_FILENAMES:
            continue
        if border_p95(path) <= 80:
            files.append(path)
        if len(files) >= limit:
            break
    return files


def files_from_names(names: list[str]) -> list[Path]:
    files = []
    for name in names:
        filename = name if name.endswith(".png") else f"1024Portrait_Comp_{int(name):03d}.png"
        path = SOURCE_DIR / filename
        if not path.exists():
            raise FileNotFoundError(path)
        files.append(path)
    return files


def prompt_for(path: Path, mode: str, key_color: str = "#00ff00") -> str:
    component_id = path.stem.replace("1024Portrait_", "")
    if mode == "enhanced_opaque":
        return f"""
Use case: style-transfer
Asset type: 1024x1024 sci-fi strategy game component image
Input image: reference image for {component_id}
Primary request: Recreate and enhance the referenced starship component image as a premium game asset while preserving the complete image concept, including its background or scene.
Subject: Keep the same functional object, silhouette, viewing angle, proportions, major layout, recognizable details, and any existing background or scene context from the reference. Enhance with tasteful high-end material detail, sharper geometry, clean bevels, worn edges, glass, panels, cables, machinery, and emissive accents where appropriate.
Style/medium: high-end 3D game icon or scene render with photorealistic sci-fi materials; polished and readable at game UI sizes.
Composition/framing: centered in a square 1024x1024 image, same approximate camera angle and framing as the reference, full important subject visible.
Scene/backdrop: preserve and enhance the reference backdrop or scene. Do not isolate the object. Do not make the background transparent. Do not replace the scene with a chroma-key color.
Lighting/mood: cinematic studio or environment lighting appropriate to the reference; internal glows should remain vivid and attached to the object.
Constraints: fully opaque final image with no alpha holes. One coherent component image only. No text, no watermark, no border, no extra unrelated objects.
Avoid: transparent background, chroma-key background, checkerboard, cutout-only presentation, cropped edges, changing the component category, excessive redesign.
""".strip()

    if mode == "enhanced":
        return f"""
Use case: background-extraction
Asset type: 1024x1024 sci-fi strategy game component icon
Input image: reference image for {component_id}
Primary request: Recreate and enhance the referenced starship component as a premium isolated game asset.
Subject: Keep the same functional object, silhouette, viewing angle, proportions, major layout, and recognizable details from the reference. Enhance the object with tasteful high-end material detail, sharper geometry, small mechanical features, clean bevels, vents, cables, panels, worn edges, glass, and emissive accents where appropriate.
Style/medium: high-end 3D game icon with photorealistic sci-fi materials; readable at game UI sizes, polished but not redesigned into a different object.
Composition/framing: centered in a square 1024x1024 image, same approximate isometric/three-quarter view as the reference, full object visible with generous padding.
Scene/backdrop: perfectly flat solid {key_color} chroma-key background for local background removal.
Lighting/mood: clean studio asset lighting with soft rim highlights; keep internal glows attached to the object; no cast shadow.
Constraints: one component only. Background must be one uniform {key_color} color with no shadows, gradients, texture, floor plane, reflections, haze, or vignette. Do not use {key_color} anywhere in the component. Internal glowing cores, lenses, glass, screens, reactor centers, and energy cells must remain opaque visible parts of the component, not transparent holes. No text, no watermark, no border, no extra objects.
Avoid: black background, starfield, smoke, dark halo, contact shadow, cropped edges, changing the component category, excessive redesign.
""".strip()

    return f"""
Use case: background-extraction
Asset type: 1024x1024 sci-fi game component sprite
Input image: reference image for {component_id}
Primary request: Recreate the referenced starship component as a clean isolated game asset.
Subject: Preserve the component's overall shape, viewing angle, silhouette, proportions, material types, major colors, and recognizable mechanical details from the reference.
Style/medium: polished 3D-rendered sci-fi game asset, realistic metallic and industrial materials.
Composition/framing: centered in a square 1024x1024 image, same approximate isometric/three-quarter view as the reference, generous padding around the object.
Scene/backdrop: perfectly flat solid {key_color} chroma-key background for local background removal.
Lighting/mood: clean studio-like asset lighting; keep useful internal glows as part of the object, but no cast shadow.
Constraints: background must be one uniform {key_color} color with no shadows, gradients, texture, floor plane, reflections, haze, or vignette. Do not use {key_color} anywhere in the component. Internal glowing cores, lenses, glass, screens, reactor centers, and energy cells must remain opaque visible parts of the component, not transparent holes. No text, no watermark, no border, no extra objects.
Avoid: black background, starfield, smoke, dark halo, contact shadow, cropped edges.
""".strip()


def run_command(command: list[str], retries: int = 0, retry_delay: int = 0) -> None:
    print(" ".join(str(part) for part in command))
    for attempt in range(retries + 1):
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        if result.returncode == 0:
            return
        combined_output = f"{result.stdout}\n{result.stderr}"
        should_retry = (
            "must be verified to use the model" in combined_output
            and attempt < retries
        )
        if not should_retry:
            raise subprocess.CalledProcessError(
                result.returncode,
                command,
                output=result.stdout,
                stderr=result.stderr,
            )
        print(
            f"Model access may still be propagating; retrying in {retry_delay}s "
            f"({attempt + 1}/{retries})..."
        )
        time.sleep(retry_delay)


def add_manifest_entry(
    manifest: dict,
    source: Path,
    chroma_out: Path | None,
    final_out: Path,
    mode: str,
) -> dict:
    with Image.open(final_out).convert("RGBA") as image:
        alpha = image.getchannel("A")
        alpha_bbox = alpha.getbbox()
        alpha_extrema = alpha.getextrema()

    entry = {
        "processor_status": "processed",
        "review_status": "unreviewed",
        "action": f"gpt-image-2_chroma_recreation_{mode}",
        "removed_pixels": 0,
        "notes": "",
        "source": str(source),
        "chroma_source": str(chroma_out) if chroma_out else "",
        "alpha_bbox": alpha_bbox,
        "alpha_extrema": alpha_extrema,
    }
    manifest["images"][source.name] = entry
    return {
        "filename": source.name,
        "source": str(source),
        "chroma": str(chroma_out) if chroma_out else "",
        "output": str(final_out),
        "alpha_bbox": alpha_bbox,
        "alpha_extrema": alpha_extrema,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Recreate component images with GPT Image and chroma-key removal.")
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    parser.add_argument("--mode", choices=["faithful", "enhanced", "enhanced_opaque"], default="faithful")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--names", nargs="*", default=[])
    parser.add_argument("--quality", choices=["low", "medium", "high", "auto"], default="medium")
    parser.add_argument("--key-color", default="#00ff00", help="Chroma key color for transparent-background modes.")
    parser.add_argument("--retries", type=int, default=0)
    parser.add_argument("--retry-delay", type=int, default=60)
    parser.add_argument("--force", action="store_true", help="Regenerate even if final output already exists.")
    args = parser.parse_args()

    ensure_api_key()
    if not IMAGE_GEN.exists():
        raise FileNotFoundError(IMAGE_GEN)
    if not REMOVE_CHROMA.exists():
        raise FileNotFoundError(REMOVE_CHROMA)

    output_root = args.output_root
    output_dir = output_root / "1024"
    chroma_dir = output_root / "_chroma"
    reports_dir = output_root / "reports"
    manifest_path = output_root / "review_manifest.json"

    output_dir.mkdir(parents=True, exist_ok=True)
    chroma_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    files = files_from_names(args.names) if args.names else eligible_files(args.limit)
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            manifest = {}
    else:
        manifest = {}
    manifest.update(
        {
            "source_dir": str(SOURCE_DIR),
            "staging_root": str(output_root),
            "method": f"gpt-image-2 chroma-key recreation {args.mode}",
        }
    )
    manifest.setdefault("images", {})

    report_path = reports_dir / "ai_recreate_report.json"
    if report_path.exists():
        try:
            rows = json.loads(report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            rows = []
    else:
        rows = []

    for index, source in enumerate(files, start=1):
        chroma_out = chroma_dir / source.name
        final_out = output_dir / source.name
        print(f"[{index}/{len(files)}] Recreating {source.name}")

        if final_out.exists() and not args.force:
            print(f"  Existing final output found, keeping {final_out}")
            rows.append(add_manifest_entry(manifest, source, chroma_out, final_out, args.mode))
            continue

        run_command(
            [
                sys.executable,
                str(IMAGE_GEN),
                "edit",
                "--model",
                "gpt-image-2",
                "--image",
                str(source),
                "--prompt",
                prompt_for(source, args.mode, args.key_color),
                "--size",
                "1024x1024",
                "--quality",
                args.quality,
                "--output-format",
                "png",
                "--out",
                str(chroma_out),
                "--force",
                "--no-augment",
            ],
            retries=args.retries,
            retry_delay=args.retry_delay,
        )
        if args.mode == "enhanced_opaque":
            with Image.open(chroma_out).convert("RGBA") as image:
                image.putalpha(255)
                image.save(final_out)
        else:
            run_command(
                [
                    sys.executable,
                    str(REMOVE_CHROMA),
                    "--input",
                    str(chroma_out),
                    "--out",
                    str(final_out),
                    "--auto-key",
                    "border",
                    "--key-color",
                    args.key_color,
                    "--soft-matte",
                    "--transparent-threshold",
                    "12",
                    "--opaque-threshold",
                    "220",
                    "--despill",
                    "--force",
                ]
            )
        rows.append(add_manifest_entry(manifest, source, chroma_out, final_out, args.mode))
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        report_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    report_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"Wrote {len(files)} recreated samples to {output_dir}")


if __name__ == "__main__":
    main()
