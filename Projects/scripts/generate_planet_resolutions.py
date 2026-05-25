#!/usr/bin/env python3
"""
Generate multi-resolution planet images for performance optimization.

Creates 4 resolution tiers (1024, 512, 256, 128) from 2048px master images.
Uses PIL/Pillow with LANCZOS resampling for high quality.

Usage:
    python Projects/scripts/generate_planet_resolutions.py
    python Projects/scripts/generate_planet_resolutions.py --source 2048 --resolutions 1024,512,256,128
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List

try:
    from PIL import Image
except ImportError:
    print("ERROR: PIL/Pillow is required but not installed.")
    print("Install it with: pip install Pillow")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    print("WARNING: tqdm not installed. Progress bar will not be available.")
    print("Install it with: pip install tqdm")
    tqdm = None


# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from game.core.paths import Paths


def get_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate multi-resolution planet images'
    )
    parser.add_argument(
        '--source',
        default='2048',
        help='Source folder name containing 2048px images (default: 2048)'
    )
    parser.add_argument(
        '--resolutions',
        default='1024,512,256,128',
        help='Comma-separated list of target resolutions (default: 1024,512,256,128)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without actually creating files'
    )
    return parser.parse_args()


def resize_image(source_path: Path, target_path: Path, target_size: int) -> bool:
    """
    Resize a single PNG image using high-quality LANCZOS resampling.

    Args:
        source_path: Path to source image
        target_path: Path to save resized image
        target_size: Target width and height (assumes square images)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Open image
        img = Image.open(source_path)

        # Verify it's RGBA (PNG with alpha channel)
        if img.mode != 'RGBA':
            print(f"  WARNING: {source_path.name} is {img.mode}, not RGBA. Converting...")
            img = img.convert('RGBA')

        # Resize using LANCZOS (highest quality)
        resized = img.resize((target_size, target_size), Image.Resampling.LANCZOS)

        # Save as PNG with optimization
        resized.save(target_path, 'PNG', optimize=True)

        return True

    except Exception as e:
        print(f"  ERROR processing {source_path.name}: {e}")
        return False


def main():
    """Main execution."""
    args = get_args()

    # Parse resolutions
    try:
        resolutions = [int(r.strip()) for r in args.resolutions.split(',')]
    except ValueError:
        print(f"ERROR: Invalid resolutions format: {args.resolutions}")
        print("Expected comma-separated integers like: 1024,512,256,128")
        sys.exit(1)

    # Determine source folder
    source_folder = Path(Paths.PLANETS_DIR) / args.source

    if not source_folder.exists():
        print(f"ERROR: Source folder not found: {source_folder}")
        print(f"\nExpected location: {source_folder}")
        print(f"\nDid you move the 2048px images to {args.source}/ subdirectory?")
        print("If not, run:")
        print(f"  mkdir \"{source_folder}\"")
        print(f"  mv \"{Paths.PLANETS_DIR}/planet_*.png\" \"{source_folder}/\"")
        sys.exit(1)

    # Find all planet images
    source_images = list(source_folder.glob('planet_*.png'))

    if not source_images:
        print(f"ERROR: No planet_*.png files found in {source_folder}")
        sys.exit(1)

    print(f"Found {len(source_images)} images in {source_folder}")
    print(f"Target resolutions: {resolutions}")
    print()

    # Statistics
    total_images = len(source_images) * len(resolutions)
    processed = 0
    errors = 0
    skipped = 0

    # Process each resolution
    for resolution in resolutions:
        # Create target folder
        target_folder = Path(Paths.PLANETS_DIR) / str(resolution)

        if args.dry_run:
            print(f"[DRY RUN] Would create: {target_folder}")
        else:
            target_folder.mkdir(exist_ok=True)
            print(f"Processing {resolution}x{resolution} images...")

        # Progress bar setup
        iterator = source_images
        if tqdm and not args.dry_run:
            iterator = tqdm(source_images, desc=f"  {resolution}px", unit="img")

        # Process each image
        for source_path in iterator:
            target_path = target_folder / source_path.name

            if args.dry_run:
                processed += 1
                continue

            # Skip if already exists and is newer
            if target_path.exists():
                source_mtime = source_path.stat().st_mtime
                target_mtime = target_path.stat().st_mtime
                if target_mtime >= source_mtime:
                    skipped += 1
                    continue

            # Resize
            if resize_image(source_path, target_path, resolution):
                processed += 1
            else:
                errors += 1

        if not args.dry_run:
            print()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total images processed: {processed}/{total_images}")
    if skipped > 0:
        print(f"Skipped (already up-to-date): {skipped}")
    if errors > 0:
        print(f"Errors: {errors}")

    if args.dry_run:
        print("\n[DRY RUN] No files were actually created.")
        print("Run without --dry-run to generate images.")
    else:
        print()
        print("Image generation complete!")

        # Show folder sizes
        print("\nGenerated folders:")
        for resolution in resolutions:
            target_folder = Path(Paths.PLANETS_DIR) / str(resolution)
            if target_folder.exists():
                file_count = len(list(target_folder.glob('planet_*.png')))
                print(f"  {target_folder.name}: {file_count} files")

    return 0 if errors == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
