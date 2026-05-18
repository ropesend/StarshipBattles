from types import SimpleNamespace
from unittest.mock import Mock

from game.core.hex_math import HexCoord
from game.core.validation import ValidationResult
from game.strategy.facade.dto import PlanetInfo
from game.strategy.facade.slices.planet_slice import PlanetSlice


def test_get_planets_at_hex_returns_only_exact_global_matches(monkeypatch) -> None:
    matching = SimpleNamespace(id=1, location=HexCoord(2, -1))
    other = SimpleNamespace(id=2, location=HexCoord(3, -1))
    system = SimpleNamespace(
        global_location=HexCoord(10, 5),
        planets=[matching, other],
    )
    session = SimpleNamespace(
        galaxy=SimpleNamespace(get_system_at_location=Mock(return_value=system))
    )
    state = SimpleNamespace(session=session)
    monkeypatch.setattr(
        PlanetInfo,
        "from_planet",
        staticmethod(lambda planet: f"planet-{planet.id}"),
    )

    result = PlanetSlice(state).get_planets_at_hex(HexCoord(12, 4))

    assert result == ["planet-1"]


def test_get_planets_at_hex_uses_radius_lookup_when_strict_lookup_misses(
    monkeypatch,
) -> None:
    planet = SimpleNamespace(id=5, location=HexCoord(1, 0))
    system = SimpleNamespace(global_location=HexCoord(4, 4), planets=[planet])
    galaxy = SimpleNamespace(get_system_at_location=Mock(return_value=None))
    state = SimpleNamespace(session=SimpleNamespace(galaxy=galaxy))
    radius_lookup = Mock(return_value=system)
    # PROJ-414: shim deleted; patch the canonical GPS method directly.
    monkeypatch.setattr(
        "game.strategy.services.galaxy_pathfinding_service.GalaxyPathfindingService.get_system_at_hex",
        radius_lookup,
    )
    monkeypatch.setattr(
        PlanetInfo,
        "from_planet",
        staticmethod(lambda planet: planet.id),
    )

    result = PlanetSlice(state).get_planets_at_hex(HexCoord(5, 4))

    assert result == [5]
    # PROJ-414: patched on the GPS class -> the call args are (hex_coord, radius=50)
    # (the GPS `self` is not visible because the descriptor protocol unbinds
    # when the class attribute is replaced).
    radius_lookup.assert_called_once_with(HexCoord(5, 4), radius=50)


def test_can_colonize_with_no_planet_target_delegates_with_none() -> None:
    fleet = SimpleNamespace(id=11)
    validation = ValidationResult.success()
    turn_engine = SimpleNamespace(
        validate_colonize_order=Mock(return_value=validation)
    )
    session = SimpleNamespace(galaxy=object(), turn_engine=turn_engine)
    state = SimpleNamespace(
        session=session,
        get_fleet_by_id=Mock(return_value=fleet),
        get_planet_by_id=Mock(),
    )

    result = PlanetSlice(state).can_colonize(fleet_id=11, planet_id=None)

    assert result is validation
    state.get_planet_by_id.assert_not_called()
    turn_engine.validate_colonize_order.assert_called_once_with(
        session.galaxy,
        fleet,
        None,
    )


def test_can_colonize_returns_error_for_unknown_planet() -> None:
    state = SimpleNamespace(
        get_fleet_by_id=Mock(return_value=SimpleNamespace(id=1)),
        get_planet_by_id=Mock(return_value=None),
    )

    result = PlanetSlice(state).can_colonize(fleet_id=1, planet_id=404)

    assert not result.is_valid
    assert result.errors == ["Planet not found."]


def test_planet_stockpile_snapshot_uses_per_resource_mass() -> None:
    """F-A-014: max_stockpile caps are resource units, not mass.

    Multiply each cap by ``ResourceCatalog.get_mass_per_unit`` before
    summing; the bare sum treated every resource as mass_per_unit==1.0
    which was wildly wrong for vapors/fuel/exotics.
    """
    from game.core.resources import ResourceCatalog
    from game.strategy.facade.slices.planet_slice import (
        _planet_stockpile_snapshot,
    )

    planet = SimpleNamespace(
        id=42,
        name="Cap Test",
        stockpile={},
        max_stockpile={"vapors": 1000.0, "fuel": 500.0},
    )

    snap = _planet_stockpile_snapshot(planet)

    catalog = ResourceCatalog.from_json()
    expected = (
        1000.0 * catalog.get_mass_per_unit("vapors")
        + 500.0 * catalog.get_mass_per_unit("fuel")
    )
    assert snap.capacity_mass == expected
    # Sanity: must NOT be the old buggy sum of raw amounts.
    assert snap.capacity_mass != 1500.0


def test_planet_stockpile_snapshot_no_caps_set_reports_inf_capacity() -> None:
    """No caps set means capacity_mass = inf (unchanged behavior)."""
    from game.strategy.facade.slices.planet_slice import (
        _planet_stockpile_snapshot,
    )

    planet = SimpleNamespace(
        id=7,
        name="Uncapped",
        stockpile={"metals": 50.0},
        max_stockpile={},
    )

    snap = _planet_stockpile_snapshot(planet)

    assert snap.capacity_mass == float("inf")
