"""Shared fixtures for save/load tests."""
import json
import pytest
import os
import tempfile
import shutil
from typing import Any, Optional, Set, TYPE_CHECKING

from game.strategy.engine.game_session import GameSession
from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.strategy.data.fleet import Fleet
from game.core.hex_math import HexCoord
from tests.conftest import make_mock_ship_instance
from tests.infrastructure.deep_compare import deep_compare

if TYPE_CHECKING:
    from game.core.registry import GameRegistries


@pytest.fixture
def temp_save_folder():
    """Create a temporary folder for saves and clean up after test."""
    temp_dir = tempfile.mkdtemp(prefix="test_saves_")
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def minimal_game_session():
    """Create a minimal game session for testing."""
    config = GameConfig()
    config.galaxy_radius = 300
    config.system_count = 2
    config.players = [
        PlayerConfig(name="TestPlayer", is_human=True, color=(0, 100, 200)),
        PlayerConfig(name="TestEnemy", is_human=False, color=(200, 100, 0)),
    ]
    return GameSession(config=config)


@pytest.fixture
def game_session_with_state(minimal_game_session, fresh_registries):
    """Create a game session with some game state to preserve."""
    session = minimal_game_session

    # Add some fleets (PROJ-211: pass registries for DI compliance)
    fleet1 = Fleet(100, 0, HexCoord(10, 10), speed=15.0)
    fleet1.ships = [make_mock_ship_instance("Scout", 0, registries=fresh_registries)]
    session.empires[0].add_fleet(fleet1)

    fleet2 = Fleet(200, 1, HexCoord(20, 20), speed=10.0)
    fleet2.ships = [make_mock_ship_instance("Destroyer", 1, registries=fresh_registries)]
    session.empires[1].add_fleet(fleet2)

    # Advance a few turns
    session.process_turn()
    session.process_turn()

    return session


# =============================================================================
# Round-trip assertion helpers (PROJ-223)
# =============================================================================

def assert_round_trip_fidelity(
    original_obj,
    type_class,
    ignore_fields: Optional[Set[str]] = None,
    unordered_lists: Optional[Set[str]] = None,
    float_tolerance: float = 1e-10,
    **from_dict_kwargs: Any,
):
    """Assert that an object survives to_dict → JSON → from_dict with full fidelity.

    Args:
        original_obj: Object with to_dict() method.
        type_class: Class with from_dict() classmethod.
        ignore_fields: Dot-separated paths to skip in comparison.
        unordered_lists: Dot-separated paths where list order doesn't matter.
        float_tolerance: Tolerance for float comparison.
        **from_dict_kwargs: Extra kwargs for from_dict (e.g. registries, galaxy).

    Returns:
        The restored object (for further assertions if needed).

    Raises:
        AssertionError: If round-trip produces differences.
    """
    original_dict = original_obj.to_dict()

    # Validate JSON serializability
    json_str = json.dumps(original_dict)
    parsed = json.loads(json_str)

    # Reconstruct
    restored = type_class.from_dict(parsed, **from_dict_kwargs)
    restored_dict = restored.to_dict()

    # Compare
    diffs = deep_compare(
        original_dict,
        restored_dict,
        ignore_fields=ignore_fields,
        unordered_lists=unordered_lists,
        float_tolerance=float_tolerance,
    )

    if diffs:
        diff_report = "\n".join(
            f"  {d.path}: expected {d.expected!r}, got {d.actual!r} ({d.message})"
            for d in diffs[:20]  # Cap at 20 to avoid huge output
        )
        total = len(diffs)
        suffix = f"\n  ... and {total - 20} more" if total > 20 else ""
        raise AssertionError(
            f"{type_class.__name__} round-trip produced {total} difference(s):\n"
            f"{diff_report}{suffix}"
        )

    return restored


def assert_field_preserved(
    original: Any,
    restored: Any,
    field_name: str,
    tolerance: Optional[float] = None,
):
    """Assert a single field matches between original and restored objects.

    Args:
        original: Original object.
        restored: Restored object (after round-trip).
        field_name: Attribute name to compare.
        tolerance: Float tolerance (None for exact match).
    """
    orig_val = getattr(original, field_name)
    rest_val = getattr(restored, field_name)

    if tolerance is not None and isinstance(orig_val, float):
        assert abs(orig_val - rest_val) <= tolerance, (
            f"{field_name}: {orig_val} != {rest_val} (tolerance={tolerance})"
        )
    else:
        assert orig_val == rest_val, (
            f"{field_name}: {orig_val!r} != {rest_val!r}"
        )


# =============================================================================
# Pre-populated entity fixtures (PROJ-223)
# =============================================================================

@pytest.fixture
def populated_planet(fresh_registries):
    """Create a fully-populated planet for round-trip tests."""
    from tests.fixtures.strategy_entities import create_test_planet
    return create_test_planet(has_facilities=True, has_population=True)


@pytest.fixture
def populated_fleet(fresh_registries):
    """Create a fully-populated fleet for round-trip tests."""
    from tests.fixtures.strategy_entities import create_test_fleet
    return create_test_fleet(num_ships=2, registries=fresh_registries)


@pytest.fixture
def populated_empire(fresh_registries):
    """Create a fully-populated empire for round-trip tests."""
    from tests.fixtures.strategy_entities import create_test_empire
    return create_test_empire(num_fleets=1, registries=fresh_registries)
