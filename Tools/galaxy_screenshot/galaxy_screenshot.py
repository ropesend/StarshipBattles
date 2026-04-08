#!/usr/bin/env python3
"""
Galaxy screenshot generator for visual feedback during development.

Generates galaxy layouts and saves screenshots for review.
Uses PIL/Pillow for headless rendering (no pygame display needed).

Usage:
    python scripts/galaxy_screenshot.py --type spiral --count 250 --seed 12345
    python scripts/galaxy_screenshot.py --type spiral --count 250 --no-warp
    python scripts/galaxy_screenshot.py --type cluster --count 500 --batch
"""
import sys
import random
import time
import argparse
import math
from pathlib import Path


def _find_project_root():
    """Find project root by looking for game/ and data/ directories."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "game").is_dir() and (current / "data").is_dir():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")


project_root = _find_project_root()
sys.path.insert(0, str(project_root))

from PIL import Image, ImageDraw

from game.strategy.data.galaxy import Galaxy
from game.strategy.data.hex_math import hex_to_pixel
from game.strategy.generation.placement_strategies import (
    RandomPlacementStrategy,
    DensityBasedPlacementStrategy
)
from game.strategy.generation.loaders.galaxy_layouts_loader import GalaxyLayoutsLoader
from game.strategy.generation.density.density_map import DensityMap
from game.strategy.generation.region_classifier import RegionClassifier


# Screenshot dimensions
WIDTH = 1920
HEIGHT = 1080

# Min distance between systems (matches GameSession)
MIN_DIST = 400


def calculate_radius(count: int, min_dist: int = MIN_DIST) -> int:
    """Calculate appropriate galaxy radius for system count.

    Formula: We need enough area to fit count systems with min_dist spacing.
    Area per system ≈ (min_dist)² (rough packing)
    Total area = count × min_dist²
    Radius = sqrt(total_area / π) × safety_factor

    Note: Density-based placement only uses ~20-30% of galaxy area,
    so we need a larger radius to ensure enough valid spots.
    """
    area_needed = count * min_dist * min_dist
    base_radius = int(math.sqrt(area_needed / math.pi))
    # Need larger margin for density-based sampling (only ~25% of area is valid)
    return max(3000, int(base_radius * 2.5))


def generate_galaxy(
    galaxy_type: str,
    system_count: int,
    galaxy_radius: int,
    seed: int,
    inter_region_mode: str = 'normal'
):
    """Generate a galaxy with specified parameters.

    Args:
        galaxy_type: Type of galaxy layout (spiral, cluster, random, etc.)
        system_count: Number of star systems to generate
        galaxy_radius: Galaxy radius in hex units
        seed: Random seed for reproducibility
        inter_region_mode: How to handle inter-region warp connections:
            - 'normal': No region restrictions
            - 'limited': Allow 1-2 inter-region links per region pair
            - 'minimal': Only allow MST-required inter-region links
    """
    random.seed(seed)
    rng = random.Random(seed)

    galaxy = Galaxy(radius=galaxy_radius)
    region_classifier = None
    scaled_config = None

    if galaxy_type == "random":
        strategy = RandomPlacementStrategy()
    else:
        # Load and scale layout for this galaxy radius
        scaled_config = GalaxyLayoutsLoader.load_and_scale(galaxy_type, galaxy_radius)
        density_map = DensityMap.from_config(scaled_config, galaxy_radius)
        strategy = DensityBasedPlacementStrategy(density_map)

        # Create region classifier for region-aware generation
        region_classifier = RegionClassifier(scaled_config, galaxy_radius)

    # Generate systems
    galaxy.generate_systems(
        count=system_count,
        min_dist=400,
        placement_strategy=strategy,
        rng=rng
    )

    # Assign region IDs to all systems
    if region_classifier:
        for sys in galaxy.systems.values():
            sys.region_id = region_classifier.classify(sys.global_location)

    # Generate warp lanes with region awareness
    galaxy.generate_warp_lanes(
        region_classifier=region_classifier,
        inter_region_mode=inter_region_mode
    )

    return galaxy


def render_galaxy(galaxy: Galaxy, show_warp_lines: bool = True, color_by_region: bool = True) -> Image.Image:
    """Render galaxy to a PIL Image.

    Args:
        galaxy: Galaxy to render
        show_warp_lines: Whether to draw warp lanes
        color_by_region: Whether to color-code systems by region_id
    """
    # Create image with dark background
    img = Image.new('RGB', (WIDTH, HEIGHT), (15, 20, 30))
    draw = ImageDraw.Draw(img)

    # Color palette for regions (distinct, saturated colors)
    REGION_COLORS = [
        (255, 100, 100),  # Red - Arm/Cluster 0
        (100, 255, 100),  # Green - Arm/Cluster 1
        (100, 150, 255),  # Blue - Arm/Cluster 2
        (255, 200, 50),   # Gold - Arm/Cluster 3
        (200, 100, 255),  # Purple - Arm/Cluster 4
        (100, 255, 255),  # Cyan - Arm/Cluster 5
        (255, 150, 100),  # Orange - Arm/Cluster 6
        (200, 200, 200),  # Gray - Core/Other
    ]

    # Find bounds
    if not galaxy.systems:
        return img

    min_x, max_x = float('inf'), float('-inf')
    min_y, max_y = float('inf'), float('-inf')

    hex_size = 10.0
    for sys in galaxy.systems.values():
        px, py = hex_to_pixel(sys.global_location, hex_size)
        min_x = min(min_x, px)
        max_x = max(max_x, px)
        min_y = min(min_y, py)
        max_y = max(max_y, py)

    # Calculate zoom to fit with margin
    margin = 100
    world_width = max_x - min_x + margin * 2
    world_height = max_y - min_y + margin * 2

    zoom_x = WIDTH / world_width if world_width > 0 else 1.0
    zoom_y = HEIGHT / world_height if world_height > 0 else 1.0
    zoom = min(zoom_x, zoom_y)

    # Camera offset
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2

    def world_to_screen(wx, wy):
        sx = (wx - center_x) * zoom + WIDTH / 2
        sy = (wy - center_y) * zoom + HEIGHT / 2
        return int(sx), int(sy)

    # Draw warp lanes first
    if show_warp_lines:
        drawn_pairs = set()
        inter_region_count = 0
        intra_region_count = 0

        for sys in galaxy.systems.values():
            sx, sy = hex_to_pixel(sys.global_location, hex_size)

            for wp in sys.warp_points:
                target_sys = galaxy.get_system_by_name(wp.destination_id)
                if not target_sys:
                    continue

                pair_key = tuple(sorted([sys.name, target_sys.name]))
                if pair_key in drawn_pairs:
                    continue
                drawn_pairs.add(pair_key)

                tx, ty = hex_to_pixel(target_sys.global_location, hex_size)

                scr_a = world_to_screen(sx, sy)
                scr_b = world_to_screen(tx, ty)

                # Color warp lanes differently for inter-region vs intra-region
                if color_by_region and sys.region_id is not None and target_sys.region_id is not None:
                    if sys.region_id == target_sys.region_id:
                        # Same region - subtle color
                        line_color = (40, 60, 80)
                        intra_region_count += 1
                    else:
                        # Different region - highlight in bright color
                        line_color = (255, 80, 80)  # Bright red for inter-region
                        inter_region_count += 1
                else:
                    line_color = (50, 50, 100)

                draw.line([scr_a, scr_b], fill=line_color, width=1)

        if color_by_region:
            print(f"  Warp lanes: {intra_region_count} intra-region, {inter_region_count} inter-region")

    # Draw systems as dots
    for sys in galaxy.systems.values():
        px, py = hex_to_pixel(sys.global_location, hex_size)
        screen_pos = world_to_screen(px, py)

        radius = max(2, int(4 * zoom))
        x, y = screen_pos

        # Color by region if enabled
        if color_by_region and sys.region_id is not None:
            color = REGION_COLORS[sys.region_id % len(REGION_COLORS)]
        else:
            color = (200, 200, 100)

        draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=color)

    # Print stats
    warp_count = sum(len(sys.warp_points) for sys in galaxy.systems.values()) // 2
    print(f"  Stats: {len(galaxy.systems)} systems, {warp_count} warp lanes")

    # Draw legend indicator in corner
    legend_color = (100, 200, 100) if show_warp_lines else (200, 100, 100)
    draw.rectangle([10, 10, 30, 30], fill=legend_color)

    return img


def save_screenshot(img: Image.Image, filename: str, output_dir: Path):
    """Save image as PNG."""
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / filename
    img.save(str(filepath), 'PNG')
    print(f"Saved: {filepath}")
    return filepath


def run_batch(
    galaxy_types: list,
    counts: list,
    seed: int,
    output_dir: Path,
    show_warp: bool = True,
    inter_region_mode: str = 'normal'
):
    """Generate batch of screenshots for multiple types and counts."""
    for gtype in galaxy_types:
        # Choose inter_region_mode based on galaxy type if not specified
        mode = inter_region_mode
        if mode == 'auto':
            if gtype in ('spiral', 'spiral_no_core'):
                mode = 'minimal'  # No inter-arm warps for spirals
            elif gtype == 'cluster':
                mode = 'limited'  # 1-2 links between clusters
            else:
                mode = 'normal'

        for count in counts:
            # Calculate appropriate radius
            radius = calculate_radius(count)

            print(f"\nGenerating {gtype} with {count} systems (radius={radius}, mode={mode})...")
            start = time.perf_counter()

            galaxy = generate_galaxy(gtype, count, radius, seed, inter_region_mode=mode)
            gen_time = time.perf_counter() - start
            print(f"  Generation: {gen_time:.2f}s")

            # Render with warp
            if show_warp:
                img = render_galaxy(galaxy, show_warp_lines=True, color_by_region=True)
                filename = f"{gtype}_{count}_warp_{mode}_seed{seed}.png"
                save_screenshot(img, filename, output_dir)

            # Render without warp
            img = render_galaxy(galaxy, show_warp_lines=False, color_by_region=True)
            filename = f"{gtype}_{count}_nowarp_{mode}_seed{seed}.png"
            save_screenshot(img, filename, output_dir)


def main():
    parser = argparse.ArgumentParser(description="Generate galaxy screenshots for visual feedback")
    parser.add_argument("--type", "-t", default="spiral", help="Galaxy type (spiral, cluster, random, etc.)")
    parser.add_argument("--count", "-c", type=int, default=250, help="Number of star systems")
    parser.add_argument("--radius", "-r", type=int, default=None, help="Galaxy radius (auto-calculated if not set)")
    parser.add_argument("--seed", "-s", type=int, default=None, help="Random seed (random if not set)")
    parser.add_argument("--no-warp", action="store_true", help="Hide warp lines")
    parser.add_argument("--batch", action="store_true", help="Run batch test across multiple sizes")
    parser.add_argument("--output", "-o", default="docs/screenshots/galaxy", help="Output directory")
    parser.add_argument(
        "--region-mode", "-m",
        default="auto",
        choices=["normal", "limited", "minimal", "auto"],
        help="Inter-region warp mode: normal (no restrictions), limited (1-2 per pair), "
             "minimal (MST only), auto (choose based on galaxy type)"
    )

    args = parser.parse_args()

    # Set seed
    seed = args.seed if args.seed else random.randint(0, 2**31 - 1)

    # Output directory
    output_dir = project_root / args.output

    if args.batch:
        # Batch mode - test multiple sizes
        galaxy_types = ["spiral", "cluster", "random"]
        counts = [50, 250, 1000]  # Skip 2500 by default
        run_batch(
            galaxy_types, counts, seed, output_dir,
            show_warp=not args.no_warp,
            inter_region_mode=args.region_mode
        )
    else:
        # Single galaxy
        radius = args.radius if args.radius else calculate_radius(args.count)

        # Determine inter_region_mode
        mode = args.region_mode
        if mode == 'auto':
            if args.type in ('spiral', 'spiral_no_core'):
                mode = 'minimal'
            elif args.type == 'cluster':
                mode = 'limited'
            else:
                mode = 'normal'

        print(f"Generating {args.type} galaxy with {args.count} systems (radius={radius}, seed={seed}, mode={mode})...")
        start = time.perf_counter()

        galaxy = generate_galaxy(args.type, args.count, radius, seed, inter_region_mode=mode)
        gen_time = time.perf_counter() - start
        print(f"Generation time: {gen_time:.2f}s")

        # Render
        img = render_galaxy(galaxy, show_warp_lines=not args.no_warp, color_by_region=True)

        # Save
        warp_suffix = "nowarp" if args.no_warp else "warp"
        filename = f"{args.type}_{args.count}_{warp_suffix}_{mode}_seed{seed}.png"
        save_screenshot(img, filename, output_dir)

    print("\nDone!")


if __name__ == "__main__":
    main()
