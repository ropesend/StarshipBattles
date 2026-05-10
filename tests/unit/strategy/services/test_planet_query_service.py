"""PROJ-372 Phase 2: PlanetQueryService static-query tests."""
from __future__ import annotations

from game.core.hex_math import HexCoord
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.planetary_facility import PlanetaryFacility
from game.strategy.services.planet_query_service import PlanetQueryService


def _make_planet(**overrides) -> Planet:
    base = dict(
        name="Test",
        location=HexCoord(0, 0),
        orbit_distance=1,
        mass=5.97e24,
        radius=6.371e6,
        surface_area=5.1e14,
        density=5515.0,
        surface_gravity=9.81,
        surface_pressure=101325.0,
        surface_temperature=288.0,
        surface_water=0.7,
        tectonic_activity=0.5,
        magnetic_field=1.0,
        planet_type=PlanetType.CONTINENTAL,
    )
    base.update(overrides)
    return Planet(**base)


def _facility_with_active_ability(ability_name: str) -> PlanetaryFacility:
    f = PlanetaryFacility(
        instance_id="test-id",
        design_id="test_design",
        name="Test Facility",
        design_data={},
    )
    f.component_states["k1"] = {"phase": "active", "ability_name": ability_name}
    return f


def test_active_abilities_empty_for_no_facilities() -> None:
    p = _make_planet()
    assert PlanetQueryService.active_abilities(p) == {}


def test_active_abilities_only_includes_active_phase() -> None:
    p = _make_planet()
    p.facilities.append(_facility_with_active_ability("Shield"))
    inactive = PlanetaryFacility(
        instance_id="off-id", design_id="d", name="N", design_data={},
    )
    inactive.component_states["k"] = {"phase": "powered_down", "ability_name": "Cloak"}
    p.facilities.append(inactive)
    abilities = PlanetQueryService.active_abilities(p)
    assert abilities == {"Shield": True}


def test_is_ability_active_true_when_present() -> None:
    p = _make_planet()
    p.facilities.append(_facility_with_active_ability("Shield"))
    assert PlanetQueryService.is_ability_active(p, "Shield") is True


def test_is_ability_active_false_when_absent() -> None:
    p = _make_planet()
    assert PlanetQueryService.is_ability_active(p, "Shield") is False


def test_occupied_hexes_single_hex_for_normal_planet() -> None:
    p = _make_planet(radius_hexes=0)
    assert PlanetQueryService.occupied_hexes(p) == frozenset({p.location})


def test_occupied_hexes_multi_hex_for_dyson_sphere() -> None:
    p = _make_planet(radius_hexes=3, location=HexCoord(0, 0))
    hexes = PlanetQueryService.occupied_hexes(p)
    # radius_hexes=3 -> hex_circle_filled(loc, 2) = 19 hexes.
    assert len(hexes) == 19
    assert HexCoord(0, 0) in hexes


def test_can_build_complex_always_true() -> None:
    p = _make_planet()
    assert PlanetQueryService.can_build_type(p, "complex") is True
    assert PlanetQueryService.can_build_type(p, "Complex") is True  # case-insensitive


def test_can_build_ship_requires_shipyard() -> None:
    p = _make_planet()
    assert PlanetQueryService.can_build_type(p, "ship") is False


def test_can_build_unknown_type_false() -> None:
    p = _make_planet()
    assert PlanetQueryService.can_build_type(p, "wormhole") is False


def test_planet_facade_methods_delegate_to_service() -> None:
    """The 1-line facade methods on Planet should produce the same
    output as direct service calls (PROJ-372 Phase 2 invariant)."""
    p = _make_planet(radius_hexes=2)
    p.facilities.append(_facility_with_active_ability("Shield"))

    assert p.active_abilities == PlanetQueryService.active_abilities(p)
    assert p.is_ability_active("Shield") is PlanetQueryService.is_ability_active(p, "Shield")
    assert p.occupied_hexes == PlanetQueryService.occupied_hexes(p)
    assert p.can_build_type("ship") is PlanetQueryService.can_build_type(p, "ship")
