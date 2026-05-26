#!/usr/bin/env python3
"""
Generate multi-resolution star images for performance optimization.

Creates 3 resolution tiers (512, 256, 128) from 1024px master images.
Uses PIL/Pillow with LANCZOS resampling for high quality.

Usage:
    python Projects/scripts/generate_star_resolutions.py
"""

import os
import sys
from pathlib import Path
from PIL import Image

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from game.core.paths import Paths
except ImportError:
    # Fallback if structure is different
    class Paths:
        ASSET_DIR = os.path.join(str(PROJECT_ROOT), "assets")
        STARS_DIR = os.path.join(ASSET_DIR, "Images", "stellar_objects", "Stars")
        STARS_1024_DIR = os.path.join(STARS_DIR, "1024")

def resize_image(source_path: Path, target_path: Path, target_size: int) -> bool:
    try:
        img = Image.open(source_path)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        resized = img.resize((target_size, target_size), Image.Resampling.LANCZOS)
        resized.save(target_path, 'PNG', optimize=True)
        return True
    except Exception as e:
        print(f"  ERROR processing {source_path.name}: {e}")
        return False

def main():
    source_dir = Path(Paths.STARS_1024_DIR)
    if not source_dir.exists():
        print(f"ERROR: Source directory not found: {source_dir}")
        return 1

    resolutions = [512, 256, 128]
    source_images = list(source_dir.glob('Star*.png'))

    if not source_images:
        print(f"ERROR: No Star*.png files found in {source_dir}")
        return 1

    print(f"Found {len(source_images)} images in {source_dir}")
    print(f"Target resolutions: {resolutions}")

    for res in resolutions:
        target_dir = Path(Paths.STARS_DIR) / str(res)
        target_dir.mkdir(exist_ok=True)
        print(f"Generating {res}px images...")
        
        for src in source_images:
            dest = target_dir / src.name
            if resize_image(src, dest, res):
                pass
            else:
                print(f"Failed to resize {src.name} to {res}")

    print("Generation complete!")
    return 0

if __name__ == '__main__':
    sys.exit(main())
