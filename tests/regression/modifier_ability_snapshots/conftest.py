"""
Shared fixtures and helpers for modifier-ability snapshot tests.

These tests capture the current behavior of the modifier system BEFORE any refactoring.
They serve as a baseline to ensure the refactored system produces identical results.
"""
import pytest
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from game.simulation.components.component import (
    Component, create_component, reset_component_caches
)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def snapshot_component_stats(component: Component) -> Dict[str, Any]:
    """
    Capture all stats from a component for regression comparison.

    Returns a dictionary with:
    - Component-level stats (mass, hp, cost, etc.)
    - All modifier values applied
    - The stats dictionary
    """
    return {
        'id': component.id,
        'name': component.name,
        'mass': component.mass,
        'base_mass': component.base_mass,
        'max_hp': component.max_hp,
        'base_max_hp': component.base_max_hp,
        'cost': getattr(component, 'cost', 0),
        'type_str': component.type_str,
        'stats': dict(component.stats) if component.stats else {},
        'modifiers': [
            {'id': m.definition.id, 'value': m.value}
            for m in component.modifiers
        ],
    }


def snapshot_ability_stats(ability) -> Dict[str, Any]:
    """
    Capture all stats from an ability for regression comparison.

    Handles different ability types by capturing their specific attributes.
    """
    snapshot = {
        'class_name': ability.__class__.__name__,
        'tags': list(ability.tags) if hasattr(ability, 'tags') else [],
    }

    # Weapon abilities
    if hasattr(ability, 'damage'):
        snapshot['damage'] = ability.damage
    if hasattr(ability, '_base_damage'):
        snapshot['base_damage'] = ability._base_damage
    if hasattr(ability, 'range'):
        snapshot['range'] = ability.range
    if hasattr(ability, '_base_range'):
        snapshot['base_range'] = ability._base_range
    if hasattr(ability, 'reload_time'):
        snapshot['reload_time'] = ability.reload_time
    if hasattr(ability, '_base_reload'):
        snapshot['base_reload'] = ability._base_reload
    if hasattr(ability, 'firing_arc'):
        snapshot['firing_arc'] = ability.firing_arc
    if hasattr(ability, '_base_firing_arc'):
        snapshot['base_firing_arc'] = ability._base_firing_arc
    if hasattr(ability, 'base_accuracy'):
        snapshot['base_accuracy'] = ability.base_accuracy
    if hasattr(ability, '_base_accuracy'):
        snapshot['_base_accuracy'] = ability._base_accuracy

    # Seeker/Projectile abilities
    if hasattr(ability, 'projectile_damage'):
        snapshot['projectile_damage'] = ability.projectile_damage
    if hasattr(ability, 'projectile_hp'):
        snapshot['projectile_hp'] = ability.projectile_hp
    if hasattr(ability, 'endurance'):
        snapshot['endurance'] = ability.endurance
    if hasattr(ability, '_base_endurance'):
        snapshot['base_endurance'] = ability._base_endurance

    # Propulsion abilities
    if hasattr(ability, 'thrust_force'):
        snapshot['thrust_force'] = ability.thrust_force
    if hasattr(ability, 'base_thrust'):
        snapshot['base_thrust'] = ability.base_thrust
    if hasattr(ability, 'turn_rate'):
        snapshot['turn_rate'] = ability.turn_rate
    if hasattr(ability, 'base_turn_rate'):
        snapshot['base_turn_rate'] = ability.base_turn_rate
    if hasattr(ability, 'movement_points'):
        snapshot['movement_points'] = ability.movement_points
    if hasattr(ability, 'base_movement_points'):
        snapshot['base_movement_points'] = ability.base_movement_points

    # Defense abilities
    if hasattr(ability, 'capacity'):
        snapshot['capacity'] = ability.capacity
    if hasattr(ability, 'base_capacity'):
        snapshot['base_capacity'] = ability.base_capacity
    if hasattr(ability, 'rate'):
        snapshot['rate'] = ability.rate
    if hasattr(ability, 'base_rate'):
        snapshot['base_rate'] = ability.base_rate

    # Crew abilities
    if hasattr(ability, 'amount'):
        snapshot['amount'] = ability.amount
    if hasattr(ability, '_base_amount'):
        snapshot['base_amount'] = ability._base_amount

    # Resource abilities
    if hasattr(ability, 'max_amount'):
        snapshot['max_amount'] = ability.max_amount

    return snapshot


def snapshot_full_component(component: Component) -> Dict[str, Any]:
    """
    Capture complete snapshot of a component including all abilities.
    """
    return {
        'component': snapshot_component_stats(component),
        'abilities': [
            snapshot_ability_stats(ab) for ab in component.ability_instances
        ]
    }


def compare_snapshots(actual: Dict, expected: Dict, tolerance: float = 1e-6) -> List[str]:
    """
    Compare two snapshots and return list of differences.

    Returns empty list if snapshots match, otherwise returns list of difference descriptions.
    """
    differences = []

    def compare_values(path: str, actual_val, expected_val):
        if isinstance(expected_val, dict):
            if not isinstance(actual_val, dict):
                differences.append(f"{path}: expected dict, got {type(actual_val).__name__}")
                return
            for key in expected_val:
                if key not in actual_val:
                    differences.append(f"{path}.{key}: missing in actual")
                else:
                    compare_values(f"{path}.{key}", actual_val[key], expected_val[key])
        elif isinstance(expected_val, list):
            if not isinstance(actual_val, list):
                differences.append(f"{path}: expected list, got {type(actual_val).__name__}")
                return
            if len(actual_val) != len(expected_val):
                differences.append(f"{path}: length mismatch (actual={len(actual_val)}, expected={len(expected_val)})")
            for i, (a, e) in enumerate(zip(actual_val, expected_val)):
                compare_values(f"{path}[{i}]", a, e)
        elif isinstance(expected_val, float):
            if not isinstance(actual_val, (int, float)):
                differences.append(f"{path}: expected number, got {type(actual_val).__name__}")
            elif abs(actual_val - expected_val) > tolerance:
                differences.append(f"{path}: {actual_val} != {expected_val} (diff={actual_val - expected_val})")
        elif actual_val != expected_val:
            differences.append(f"{path}: {actual_val} != {expected_val}")

    compare_values("root", actual, expected)
    return differences


def get_snapshots_dir() -> Path:
    """Get the snapshots directory path."""
    # Snapshots are in the parent directory (tests/regression/snapshots/)
    return Path(__file__).parent.parent / "snapshots"


def load_snapshot(name: str) -> Optional[Dict]:
    """Load a snapshot from the snapshots directory."""
    snapshot_path = get_snapshots_dir() / f"{name}.json"
    if snapshot_path.exists():
        with open(snapshot_path, 'r') as f:
            return json.load(f)
    return None


def save_snapshot(name: str, data: Dict):
    """Save a snapshot to the snapshots directory."""
    snapshot_dir = get_snapshots_dir()
    snapshot_dir.mkdir(exist_ok=True)
    snapshot_path = snapshot_dir / f"{name}.json"
    with open(snapshot_path, 'w') as f:
        json.dump(data, f, indent=2)


def fail_missing_baseline(name: str, snapshot: Dict):
    """Write the missing baseline to the snapshots dir and fail the test.

    PROJ-446 Phase 1 Task 1.4 (F-C-025): the previous `pytest.skip(...)` on
    missing baselines silently masked baseline-absence in CI on fresh
    checkouts. The regression-test intent is to detect drift, so a missing
    baseline must be a loud failure, not a silent skip. The maintainer
    regenerates by deleting and re-running, or by inspecting the just-saved
    file under `tests/regression/snapshots/`, then committing the new file.
    """
    save_snapshot(name, snapshot)
    snapshot_path = get_snapshots_dir() / f"{name}.json"
    pytest.fail(
        f"Baseline snapshot '{name}' was missing. "
        f"Wrote a fresh baseline to {snapshot_path}; inspect and commit it "
        f"if the values are correct, then re-run the test."
    )


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def setup_registries(stable_component_registries):
    """
    Provide registries for snapshot tests.

    Uses stable_component_registries (from root conftest.py) so snapshot
    expectations do not couple to mod-able balance values in
    data/components.json. Railgun/laser_cannon/thruster values are loaded
    from tests/fixtures/test_components.json; other components inherit
    from production registries.
    """
    reset_component_caches()
    yield stable_component_registries
    reset_component_caches()
