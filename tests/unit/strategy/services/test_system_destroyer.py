"""Characterization tests for system_destroyer (PROJ-336).

Pins the public surface of `collect_system_contents` and `destroy_system`.
Uses real domain objects per Decision D-002 where they are cheap to build.
"""
from __future__ import annotations

import dataclasses
from unittest.mock import MagicMock

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.data.galaxy import Galaxy, StarSystem
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.stars import Spectrum, Star, StarType
from game.strategy.services.system_destroyer import (
    SYSTEM_RADIUS_HEXES,
    SystemDestructionPlan,
    collect_system_contents,
    destroy_system,
)


def _spectrum() -> Spectrum:
    return Spectrum(0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0)


def _make_star(name: str = "Sol") -> Star:
    return Star(
        name=name,
        mass=1.0,
        radius_hexes=1,
        temperature=5778.0,
        luminosity=1.0,
        spectrum=_spectrum(),
        star_type=StarType.MAIN_SEQUENCE,
        color=(255, 255, 200),
        age=4.6e9,
        location=HexCoord(0, 0),
    )


def _make_planet(name: str, local_loc: HexCoord, owner_id: int | None) -> Planet:
    p = Planet(
        name=name,
        location=local_loc,
        orbit_distance=3,
        mass=1e24, radius=6e6, surface_area=5e14, density=5500,
        surface_gravity=9.8, surface_pressure=101325,
        surface_temperature=288, surface_water=0.7,
        tectonic_activity=0.5, magnetic_field=1.0,
        planet_type=PlanetType.CONTINENTAL, image_id="t.png",
    )
    p.owner_id = owner_id
    return p


def _build_galaxy(system_center: HexCoord = HexCoord(0, 0)):
    galaxy = Galaxy(radius=100)
    system = StarSystem("Target", system_center, stars=[_make_star()])
    galaxy.add_system(system)
    return galaxy, system


class TestCollectSystemContents:
    def test_snapshots_planets_and_stars_from_system(self):
        galaxy, system = _build_galaxy()
        planet = _make_planet("Colony", HexCoord(3, 0), owner_id=1)
        system.planets.append(planet)
        galaxy.register_planet(system, planet)

        plan = collect_system_contents(system, galaxy, [])
        assert plan.planets == (planet,)
        assert len(plan.stars) == 1
        assert plan.stars[0].name == "Sol"

    def test_includes_fleet_strictly_inside_radius(self):
        galaxy, system = _build_galaxy()
        empire = Empire(1, "P", (255, 0, 0))
        # distance 49 from system center — strictly < 50.
        fleet = Fleet(1, empire.id, system.global_location + HexCoord(49, 0))
        empire.fleets.append(fleet)

        plan = collect_system_contents(system, galaxy, [empire])
        assert plan.fleet_count == 1
        assert plan.fleets[0] == (empire, fleet)

    def test_excludes_fleet_at_exact_radius_boundary(self):
        galaxy, system = _build_galaxy()
        empire = Empire(1, "P", (255, 0, 0))
        # distance 50 — `<` is strict, so this is excluded.
        fleet = Fleet(1, empire.id, system.global_location + HexCoord(50, 0))
        empire.fleets.append(fleet)

        plan = collect_system_contents(system, galaxy, [empire])
        assert plan.fleet_count == 0

    def test_excludes_fleet_outside_radius(self):
        galaxy, system = _build_galaxy()
        empire = Empire(1, "P", (255, 0, 0))
        fleet = Fleet(1, empire.id, system.global_location + HexCoord(60, 0))
        empire.fleets.append(fleet)

        plan = collect_system_contents(system, galaxy, [empire])
        assert plan.fleet_count == 0

    def test_with_empty_empires_returns_zero_fleets(self):
        galaxy, system = _build_galaxy()
        plan = collect_system_contents(system, galaxy, [])
        assert plan.fleet_count == 0

    def test_with_empire_having_no_fleets_returns_zero_fleets(self):
        galaxy, system = _build_galaxy()
        empire = Empire(1, "P", (255, 0, 0))
        plan = collect_system_contents(system, galaxy, [empire])
        assert plan.fleet_count == 0

    def test_with_custom_radius_kwarg_overrides_default(self):
        galaxy, system = _build_galaxy()
        empire = Empire(1, "P", (255, 0, 0))
        # At distance 9: inside radius=10, but inside default 50 too.
        near_fleet = Fleet(1, empire.id, system.global_location + HexCoord(9, 0))
        # At distance 20: outside radius=10, but inside default 50.
        far_fleet = Fleet(2, empire.id, system.global_location + HexCoord(20, 0))
        empire.fleets.extend([near_fleet, far_fleet])

        plan = collect_system_contents(system, galaxy, [empire], radius=10)
        assert plan.fleet_count == 1
        assert plan.fleets[0][1] is near_fleet

    def test_returns_frozen_plan(self):
        galaxy, system = _build_galaxy()
        plan = collect_system_contents(system, galaxy, [])
        with pytest.raises(dataclasses.FrozenInstanceError):
            plan.planets = ()  # type: ignore[misc]


class TestDestroySystem:
    def test_removes_planets_from_owner_empire_colonies_and_unregisters(self):
        galaxy, system = _build_galaxy()
        planet = _make_planet("Colony", HexCoord(3, 0), owner_id=1)
        system.planets.append(planet)
        galaxy.register_planet(system, planet)
        empire = Empire(1, "P", (255, 0, 0))
        empire.colonies.append(planet)

        plan = collect_system_contents(system, galaxy, [empire])
        result = destroy_system(plan, galaxy, [empire])

        assert planet not in empire.colonies
        assert result.planets_removed == 1

    def test_skips_colony_removal_when_planet_owner_id_is_none(self):
        galaxy, system = _build_galaxy()
        planet = _make_planet("Wild", HexCoord(3, 0), owner_id=None)
        system.planets.append(planet)
        galaxy.register_planet(system, planet)
        empire = Empire(1, "P", (255, 0, 0))
        # Defensive: make sure unowned planet is NOT in any empire's colonies.
        assert planet not in empire.colonies

        plan = collect_system_contents(system, galaxy, [empire])
        result = destroy_system(plan, galaxy, [empire])

        # Still unregistered + counted, but colony list never touched.
        assert result.planets_removed == 1
        assert planet not in empire.colonies

    def test_calls_remove_fleet_with_event_bus_passthrough(self):
        galaxy, system = _build_galaxy()
        empire = Empire(1, "P", (255, 0, 0))
        fleet = Fleet(1, empire.id, system.global_location + HexCoord(5, 0))
        empire.fleets.append(fleet)

        plan = collect_system_contents(system, galaxy, [empire])
        sentinel_bus = object()
        empire.remove_fleet = MagicMock()  # type: ignore[method-assign]

        destroy_system(plan, galaxy, [empire], event_bus=sentinel_bus)

        empire.remove_fleet.assert_called_once_with(fleet, event_bus=sentinel_bus)

    def test_clears_system_stars_when_remove_stars_true(self):
        galaxy, system = _build_galaxy()
        plan = collect_system_contents(system, galaxy, [])
        assert system.stars  # sanity

        result = destroy_system(plan, galaxy, [], remove_stars=True)

        assert system.stars == []
        assert result.stars_removed == 1

    def test_leaves_system_stars_intact_when_remove_stars_false(self):
        galaxy, system = _build_galaxy()
        plan = collect_system_contents(system, galaxy, [])
        original_stars = list(system.stars)

        result = destroy_system(plan, galaxy, [], remove_stars=False)

        assert system.stars == original_stars
        assert result.stars_removed == 0

    def test_collects_ship_names_into_result_and_skips_ships_missing_name(self):
        galaxy, system = _build_galaxy()
        empire = Empire(1, "P", (255, 0, 0))
        fleet = Fleet(1, empire.id, system.global_location + HexCoord(5, 0))

        named_ship = MagicMock()
        named_ship.name = "Endeavour"
        unnamed_ship = MagicMock()
        unnamed_ship.name = None
        # ships without `.name` attribute also skipped (getattr default None).
        spec_ship = MagicMock(spec=[])  # no .name attribute
        fleet.ships = [named_ship, unnamed_ship, spec_ship]
        empire.fleets.append(fleet)
        empire.remove_fleet = MagicMock()  # type: ignore[method-assign]

        plan = collect_system_contents(system, galaxy, [empire])
        result = destroy_system(plan, galaxy, [empire])

        assert result.ship_names == ["Endeavour"]
        assert result.fleets_removed == 1


class TestSystemRadiusBoundaryBehavior:
    """PROJ-353 Tier-7 (T2.8): rewritten from a vacuous module-constant
    assertion (`SYSTEM_RADIUS_HEXES == 50`) to a behavioral pin. The
    constant matters because it picks `dist < radius` — i.e. fleets at
    EXACTLY 50 hexes are NOT considered in-system. Pin the boundary
    via the public `collect_system_contents` API rather than reading
    the constant.
    """

    def test_default_radius_includes_fleet_at_distance_one_below_threshold(self):
        center = HexCoord(0, 0)
        system = MagicMock()
        system.global_location = center
        system.planets = []
        system.stars = []

        empire = Empire(empire_id=0, name="E", color=(0, 0, 0))
        # 49 hexes from origin along the q-axis is strictly inside.
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(49, 0), speed=1.0)
        empire.fleets.append(fleet)

        plan = collect_system_contents(system, MagicMock(), [empire])

        assert plan.fleets == ((empire, fleet),)

    def test_default_radius_excludes_fleet_at_exactly_threshold_distance(self):
        """`<` not `<=` — pathfinding contract per production comment at
        line 110 of system_destroyer.py."""
        center = HexCoord(0, 0)
        system = MagicMock()
        system.global_location = center
        system.planets = []
        system.stars = []

        empire = Empire(empire_id=0, name="E", color=(0, 0, 0))
        # Exactly SYSTEM_RADIUS_HEXES hexes from origin: NOT included.
        fleet = Fleet(
            fleet_id=1, owner_id=0,
            location=HexCoord(SYSTEM_RADIUS_HEXES, 0),
            speed=1.0,
        )
        empire.fleets.append(fleet)

        plan = collect_system_contents(system, MagicMock(), [empire])

        assert plan.fleets == ()

    def test_explicit_radius_overrides_default(self):
        """Caller-provided radius wins, proving the default isn't
        hard-baked downstream of the kwarg."""
        center = HexCoord(0, 0)
        system = MagicMock()
        system.global_location = center
        system.planets = []
        system.stars = []

        empire = Empire(empire_id=0, name="E", color=(0, 0, 0))
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(10, 0), speed=1.0)
        empire.fleets.append(fleet)

        # radius=5 → dist 10 is excluded.
        plan = collect_system_contents(system, MagicMock(), [empire], radius=5)
        assert plan.fleets == ()
        # radius=20 → dist 10 is included.
        plan = collect_system_contents(system, MagicMock(), [empire], radius=20)
        assert plan.fleets == ((empire, fleet),)
