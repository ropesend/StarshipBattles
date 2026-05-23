#!/usr/bin/env python3
"""
Diagnostic script to verify star system blueprints produce expected results.

Generates systems from each blueprint and evaluates whether they match expectations.
"""
import sys
import random
from pathlib import Path


def _find_project_root():
    """Find project root by looking for game/ and data/ directories."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "game").is_dir() and (current / "data").is_dir():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")


sys.path.insert(0, str(_find_project_root()))

from game.strategy.data.stars import StarGenerator, StarType
from game.strategy.data.planet_gen import PlanetGenerator
from game.strategy.data.planet import PlanetType
from game.core.constants import EARTH_MASS
from game.strategy.data.planet_physics import MASS_JUPITER
from game.strategy.generation.loaders.system_blueprints_loader import SystemBlueprintsLoader
from game.strategy.generation.planet_image_registry import PlanetImageRegistry


# Expected characteristics for each blueprint
EXPECTATIONS = {
    "binary_no_planets": {
        "star_count": (2, 2),
        "planet_count": (0, 1),
        "description": "Binary star system with 0-1 planets"
    },
    "solar_like": {
        "star_count": (1, 1),
        "planet_count": (4, 8),
        "star_mass_range": (0.5, 1.5),
        "star_type": [StarType.MAIN_SEQUENCE, StarType.RED_DWARF],  # G/K type
        "description": "Sol-like system with 4-8 planets, G/K star (0.5-1.5 Msol)"
    },
    "red_dwarf_pack": {
        "star_count": (1, 1),
        "planet_count": (5, 10),
        "star_mass_range": (0.08, 0.5),
        "star_type": [StarType.RED_DWARF, StarType.BROWN_DWARF],
        "expect_small_planets": True,
        "description": "Red dwarf with 5-10 small, closely packed planets"
    },
    "empty_warp_hub": {
        "star_count": (1, 1),
        "planet_count": (0, 1),
        "description": "Single star with 0-1 planets"
    },
    "gas_giant_system": {
        "star_count": (1, 1),
        "planet_count": (2, 5),
        "star_mass_range": (0.8, 3.0),
        "expect_gas_giants": True,
        "description": "System dominated by gas giants (2-5 planets, >1e25 kg)"
    },
    "trinary_system": {
        "star_count": (3, 3),
        "planet_count": (0, 3),
        "description": "Triple star system with 0-3 planets"
    },
    "quad_system": {
        "star_count": (4, 4),
        "planet_count": (0, 1),
        "description": "Quadruple star system with 0-1 planets"
    },
    "hot_jupiter": {
        "star_count": (1, 1),
        "planet_count": (1, 3),
        "star_mass_range": (0.8, 1.5),
        "expect_hot_jupiter": True,
        "description": "F/G star with hot Jupiter (gas giant in close orbit)"
    }
}


def generate_system(blueprint_name: str, blueprint: dict, seed: int = None):
    """Generate a system from a blueprint and return stats."""
    if seed:
        random.seed(seed)

    system_name = f"Test_{blueprint_name}"

    # Generate stars
    star_gen = StarGenerator()
    stars = star_gen.generate_from_blueprint(system_name, blueprint)

    # Generate planets with blueprint constraints
    image_registry = PlanetImageRegistry()
    planet_gen = PlanetGenerator(image_registry)
    planets = planet_gen.generate_system_bodies(system_name, stars, blueprint)

    return {
        "stars": stars,
        "planets": planets,
        "star_count": len(stars),
        "planet_count": len(planets)
    }


def analyze_system(result: dict, blueprint_name: str, expectations: dict) -> dict:
    """Analyze a generated system against expectations."""
    issues = []
    passes = []

    stars = result["stars"]
    planets = result["planets"]

    # Check star count
    min_stars, max_stars = expectations.get("star_count", (1, 4))
    if not (min_stars <= len(stars) <= max_stars):
        issues.append(f"Star count {len(stars)} outside expected range [{min_stars}, {max_stars}]")
    else:
        passes.append(f"Star count OK: {len(stars)}")

    # Check planet count
    min_planets, max_planets = expectations.get("planet_count", (0, 20))
    if not (min_planets <= len(planets) <= max_planets):
        issues.append(f"Planet count {len(planets)} outside expected range [{min_planets}, {max_planets}]")
    else:
        passes.append(f"Planet count OK: {len(planets)}")

    # Check star mass range
    if "star_mass_range" in expectations:
        min_mass, max_mass = expectations["star_mass_range"]
        for star in stars:
            if not (min_mass <= star.mass <= max_mass):
                issues.append(f"Star {star.name} mass {star.mass:.3f} Msol outside [{min_mass}, {max_mass}]")
            else:
                passes.append(f"Star {star.name} mass OK: {star.mass:.3f} Msol")

    # Check star type
    if "star_type" in expectations:
        expected_types = expectations["star_type"]
        for star in stars:
            if star.star_type not in expected_types:
                issues.append(f"Star {star.name} type {star.star_type.name} not in expected {[t.name for t in expected_types]}")

    # Check for expected gas giants
    if expectations.get("expect_gas_giants"):
        gas_giants = [p for p in planets if p.planet_type in (PlanetType.JOVIAN, PlanetType.ICE_GIANT)]
        if len(gas_giants) == 0:
            issues.append("No gas giants found, but gas_giant_system should have mostly giants")
        else:
            passes.append(f"Found {len(gas_giants)} gas giants")

        # Check if majority are giants
        if len(planets) > 0 and len(gas_giants) / len(planets) < 0.5:
            issues.append(f"Only {len(gas_giants)}/{len(planets)} are gas giants (expected majority)")

    # Check for small planets in red_dwarf_pack
    if expectations.get("expect_small_planets"):
        small_threshold = 5 * EARTH_MASS  # 5 Earth masses
        small_planets = [p for p in planets if p.mass < small_threshold]
        if len(planets) > 0:
            small_ratio = len(small_planets) / len(planets)
            if small_ratio < 0.5:
                issues.append(f"Only {len(small_planets)}/{len(planets)} are small (<5 Mearth), expected majority")
            else:
                passes.append(f"{len(small_planets)}/{len(planets)} are small planets")

    # Check for hot Jupiter
    if expectations.get("expect_hot_jupiter"):
        # Hot Jupiter = gas giant in close orbit (orbit_distance <= 3)
        hot_jupiters = [p for p in planets
                       if p.planet_type in (PlanetType.JOVIAN, PlanetType.ICE_GIANT)
                       and p.orbit_distance <= 3]
        if len(hot_jupiters) == 0:
            # Check if we even have gas giants
            gas_giants = [p for p in planets if p.planet_type in (PlanetType.JOVIAN, PlanetType.ICE_GIANT)]
            if len(gas_giants) == 0:
                issues.append("No gas giants found for hot_jupiter blueprint")
            else:
                closest_giant = min(gas_giants, key=lambda p: p.orbit_distance)
                issues.append(f"No hot Jupiter found. Closest giant at orbit {closest_giant.orbit_distance}")
        else:
            passes.append(f"Hot Jupiter found at orbit {hot_jupiters[0].orbit_distance}")

    return {"issues": issues, "passes": passes}


def print_system_details(result: dict, blueprint_name: str):
    """Print detailed information about a generated system."""
    print(f"\n{'='*60}")
    print(f"Blueprint: {blueprint_name}")
    print(f"{'='*60}")

    print(f"\n--- Stars ({len(result['stars'])}) ---")
    for star in result["stars"]:
        print(f"  {star.name}:")
        print(f"    Type: {star.star_type.name}")
        print(f"    Mass: {star.mass:.3f} Msol")
        print(f"    Temp: {star.temperature:.0f} K")
        print(f"    Luminosity: {star.luminosity:.4f} Lsol")
        print(f"    Location: {star.location}")

    print(f"\n--- Planets ({len(result['planets'])}) ---")
    for planet in result["planets"]:
        mass_earth = planet.mass / EARTH_MASS
        mass_jupiter = planet.mass / MASS_JUPITER
        print(f"  {planet.name}:")
        print(f"    Type: {planet.planet_type.name}")
        print(f"    Mass: {mass_earth:.2f} Mearth ({mass_jupiter:.4f} Mjup)")
        print(f"    Orbit: {planet.orbit_distance} hexes")
        print(f"    Temp: {planet.surface_temperature:.0f} K")
        print(f"    Location: {planet.location}")


def run_diagnostics(samples_per_blueprint: int = 5, verbose: bool = True):
    """Run diagnostic tests on all blueprints."""
    loader = SystemBlueprintsLoader()
    data = loader.load()
    blueprints = data.get("blueprints", {})

    print("\n" + "="*70)
    print("STAR SYSTEM BLUEPRINT DIAGNOSTICS")
    print("="*70)

    all_results = {}

    for blueprint_name, blueprint in blueprints.items():
        expectations = EXPECTATIONS.get(blueprint_name, {})

        print(f"\n\n{'#'*70}")
        print(f"# Testing: {blueprint_name}")
        print(f"# Expected: {expectations.get('description', 'No description')}")
        print(f"{'#'*70}")

        blueprint_issues = []
        blueprint_passes = []

        for i in range(samples_per_blueprint):
            seed = 1000 + i
            result = generate_system(blueprint_name, blueprint, seed)

            if verbose:
                print_system_details(result, f"{blueprint_name} (seed={seed})")

            analysis = analyze_system(result, blueprint_name, expectations)
            blueprint_issues.extend(analysis["issues"])
            blueprint_passes.extend(analysis["passes"])

        # Summary for this blueprint
        print(f"\n--- Summary for {blueprint_name} ({samples_per_blueprint} samples) ---")

        unique_issues = list(set(blueprint_issues))
        unique_passes = list(set(blueprint_passes))

        if unique_passes:
            print("PASSES:")
            for p in unique_passes[:5]:  # Limit output
                print(f"  [OK] {p}")

        if unique_issues:
            print("ISSUES:")
            for issue in unique_issues:
                count = blueprint_issues.count(issue)
                print(f"  [FAIL] {issue} (occurred {count}/{samples_per_blueprint} times)")
        else:
            print("  No issues found!")

        all_results[blueprint_name] = {
            "issues": unique_issues,
            "passes": unique_passes,
            "issue_count": len(blueprint_issues),
            "pass_count": len(blueprint_passes)
        }

    # Final summary
    print("\n\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)

    total_issues = 0
    for name, result in all_results.items():
        issue_count = result["issue_count"]
        total_issues += issue_count
        status = "PASS" if issue_count == 0 else f"FAIL ({issue_count} issues)"
        print(f"  {name}: {status}")

    print(f"\nTotal issues across all blueprints: {total_issues}")

    return all_results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Diagnose star system blueprint generation")
    parser.add_argument("-n", "--samples", type=int, default=3, help="Samples per blueprint")
    parser.add_argument("-q", "--quiet", action="store_true", help="Less verbose output")
    args = parser.parse_args()

    run_diagnostics(samples_per_blueprint=args.samples, verbose=not args.quiet)
