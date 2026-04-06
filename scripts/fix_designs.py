#!/usr/bin/env python
"""Fix quickstart designs: add crew housing/life support as needed, recalculate expected_stats.

Usage:
    python scripts/fix_designs.py [directory]

Default directory: tests/fixtures/quickstart/designs/
"""
import json
import math
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from game.core.registry import GameRegistries
from game.simulation.components.component import load_components_data, load_modifiers_data
from game.simulation.entities.ship import Ship
from game.simulation.entities.ship_loader import load_vehicle_classes_data
from game.strategy.services.design_validator import DesignValidator


def load_registries() -> GameRegistries:
    minimal = GameRegistries(components={}, modifiers={}, vehicle_classes={}, resources={})
    return GameRegistries(
        components=load_components_data(registries=minimal),
        modifiers=load_modifiers_data(),
        vehicle_classes=load_vehicle_classes_data(),
        resources={}
    )


CREW_QUARTERS_TEMPLATE = {
    "id": "crew_quarters",
    "modifiers": [
        {"id": "simple_size_mount", "value": 1.0},
        {"id": "hardened_mount", "value": 1.0}
    ]
}

LIFE_SUPPORT_TEMPLATE = {
    "id": "life_support",
    "modifiers": [
        {"id": "simple_size_mount", "value": 1.0},
        {"id": "hardened_mount", "value": 1.0}
    ]
}

CREW_PER_QUARTERS = 10
LIFE_SUPPORT_PER_MODULE = 25


def get_crew_deficit(design_data, registries):
    """Return (crew_deficit, life_support_deficit) using DesignValidator."""
    validator = DesignValidator(registries)
    result = validator.validate(design_data)
    crew_deficit = 0
    ls_deficit = 0
    for err in result.errors:
        if "crew housing" in err:
            # Parse "Need X more crew housing" format
            crew_deficit = int(err.split("Need ")[1].split(" more")[0])
        elif "life support" in err:
            ls_deficit = int(err.split("Need ")[1].split(" more")[0])
    return crew_deficit, ls_deficit


def fix_design(filepath, registries):
    """Fix a single design file. Returns (name, changes_made)."""
    with open(filepath) as f:
        design_data = json.load(f)

    name = design_data.get('name', filepath.stem)
    changes = []

    # Check crew/life support deficits
    crew_deficit, ls_deficit = get_crew_deficit(design_data, registries)

    if crew_deficit > 0:
        needed = math.ceil(crew_deficit / CREW_PER_QUARTERS)
        core_layer = design_data.get('layers', {}).get('CORE', [])
        for _ in range(needed):
            core_layer.append(json.loads(json.dumps(CREW_QUARTERS_TEMPLATE)))
        changes.append(f"+{needed} crew_quarters (was short {crew_deficit})")

    if ls_deficit > 0:
        needed = math.ceil(ls_deficit / LIFE_SUPPORT_PER_MODULE)
        core_layer = design_data.get('layers', {}).get('CORE', [])
        for _ in range(needed):
            core_layer.append(json.loads(json.dumps(LIFE_SUPPORT_TEMPLATE)))
        changes.append(f"+{needed} life_support (was short {ls_deficit})")

    # Recalculate expected_stats using Ship (single source of truth)
    ship = Ship.from_dict(design_data, registries=registries)
    ship.recalculate_stats()
    existing = design_data.get('expected_stats', {})
    existing['max_hp'] = ship.max_hp
    existing['mass'] = ship.mass
    existing['max_speed'] = ship.max_speed
    existing['acceleration_rate'] = ship.acceleration_rate
    existing['turn_speed'] = ship.turn_speed
    existing['total_thrust'] = ship.total_thrust
    design_data['expected_stats'] = existing
    changes.append("updated expected_stats")

    # Write back
    with open(filepath, 'w') as f:
        json.dump(design_data, f, indent=2)
        f.write('\n')

    return name, changes


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

    for filepath in design_files:
        name, changes = fix_design(filepath, registries)
        if changes:
            print(f"  [FIXED] {name}: {', '.join(changes)}")
        else:
            print(f"  [OK]    {name}: no changes needed")

    print(f"\n{len(design_files)} designs processed.")


if __name__ == "__main__":
    main()
