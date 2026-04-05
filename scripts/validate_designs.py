#!/usr/bin/env python
"""Validate ship/complex designs against the component registry.

Checks each design for:
- Component existence in registry
- Crew housing sufficiency
- Life support sufficiency
- Layer mass budgets
- Mass consistency with expected_stats (if present)

Usage:
    python scripts/validate_designs.py [directory]

Default directory: tests/fixtures/quickstart/designs/
Exit code: 0 if all valid, 1 if any errors.
"""
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from game.core.registry import GameRegistries
from game.simulation.components.component import load_components_data, load_modifiers_data
from game.simulation.entities.ship_loader import load_vehicle_classes_data
from game.strategy.services.design_validator import DesignValidator
from game.strategy.services.ship_stats_calculator import ShipStatsCalculator


def load_registries() -> GameRegistries:
    """Load full game registries."""
    minimal = GameRegistries(components={}, modifiers={}, vehicle_classes={}, resources={})
    return GameRegistries(
        components=load_components_data(registries=minimal),
        modifiers=load_modifiers_data(),
        vehicle_classes=load_vehicle_classes_data(),
        resources={}
    )


def validate_design_file(filepath: Path, registries: GameRegistries) -> tuple:
    """Validate a single design file.

    Returns:
        (design_name, errors, warnings, mass_mismatch)
    """
    with open(filepath) as f:
        design_data = json.load(f)

    name = design_data.get('name', filepath.stem)

    # Run validator
    validator = DesignValidator(registries)
    result = validator.validate(design_data)

    # Check mass consistency
    mass_mismatch = None
    expected_stats = design_data.get('expected_stats', {})
    expected_mass = expected_stats.get('mass')
    if expected_mass is not None:
        calc = ShipStatsCalculator(registries=registries)
        stats = calc.calculate_stats(design_data)
        actual_mass = stats.get('mass', 0)
        if abs(actual_mass - expected_mass) > 0.5:
            mass_mismatch = (actual_mass, expected_mass)

    return name, result.errors, result.warnings, mass_mismatch


def main():
    designs_dir = sys.argv[1] if len(sys.argv) > 1 else "tests/fixtures/quickstart/designs"
    designs_path = Path(designs_dir)

    if not designs_path.exists():
        print(f"Directory not found: {designs_path}")
        sys.exit(1)

    design_files = sorted(designs_path.glob("*.json"))
    if not design_files:
        print(f"No .json files found in {designs_path}")
        sys.exit(1)

    registries = load_registries()
    total_errors = 0
    total_warnings = 0

    for filepath in design_files:
        name, errors, warnings, mass_mismatch = validate_design_file(filepath, registries)

        status = "OK" if not errors else "FAIL"
        if mass_mismatch:
            status = "FAIL"

        icon = "PASS" if status == "OK" else "FAIL"
        print(f"  [{icon}] {name} ({filepath.name})")

        for err in errors:
            print(f"        ERROR: {err}")
            total_errors += 1
        for warn in warnings:
            print(f"        WARN:  {warn}")
            total_warnings += 1
        if mass_mismatch:
            actual, expected = mass_mismatch
            print(f"        ERROR: Mass mismatch: calculated={actual:.1f}, expected={expected:.1f}")
            total_errors += 1

    print(f"\n{len(design_files)} designs checked: {total_errors} errors, {total_warnings} warnings")

    sys.exit(1 if total_errors > 0 else 0)


if __name__ == "__main__":
    main()
