"""End-to-end regression tests for system destruction.

User report (PROJ-277): firing STELLERATE_STAR destroyed the star but
ships elsewhere in the system survived.

Root cause: `SuperweaponOrderProcessor.process_stellerate_star` unregisters
planets BEFORE calling `get_all_fleets_in_system`, which builds its set of
valid "system hexes" by iterating `system.planets`. By the time the fleet
collection runs, there are no planets left to derive hexes from. Worse,
`get_all_fleets_in_system` only checks hexes that contain a placed entity
(planet / star / warp point / dyson sphere) — ships in empty "open space"
hexes inside the system never died.

Fix: `SystemDestroyer` service uses a collect-then-mutate pattern and
collects every fleet whose hex is within the system's 50-hex radius (per
`get_system_at_hex(radius=50)` in `pathfinding.py` and user confirmation
that a system is a 50-hex-radius region).
"""
from __future__ import annotations

from game.core.hex_math import HexCoord
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.data.galaxy import Galaxy, StarSystem
from game.strategy.data.order_types import Order, OrderType
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.stars import Spectrum, Star, StarType
from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor


def _spectrum() -> Spectrum:
    return Spectrum(0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0)


def _make_star(name="Sol") -> Star:
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


def _make_planet(name: str, local_loc: HexCoord, owner_id: int) -> Planet:
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


def _build_scenario(system_center: HexCoord = HexCoord(0, 0)):
    """Galaxy with one system and one colonized planet."""
    galaxy = Galaxy(radius=100)
    system = StarSystem("Target", system_center, stars=[_make_star()])
    galaxy.add_system(system)

    planet = _make_planet("Colony", HexCoord(3, 0), owner_id=1)
    system.planets.append(planet)
    galaxy.register_planet(system, planet)

    empire = Empire(1, "Player", (255, 0, 0))
    empire.colonies.append(planet)
    return galaxy, system, planet, empire


def _add_actor_ship(fleet: Fleet):
    """Attach a stellerator ship so SuperweaponValidator finds the ability."""
    class _ShipStub:
        design_data = {"layers": {"HULL": [{"id": "stellerator"}]}}
        is_derelict = False
        name = "Actor"
        id = 999

        def is_combat_capable(self):
            return True

    fleet.ships.append(_ShipStub())


def _stellerator_registry():
    return {
        "stellerator": {"id": "stellerator", "abilities": {"DestroyStar": {}}},
    }


# ---------------------------------------------------------------------------
# System destruction contract: every ship within 50-hex radius dies.
# ---------------------------------------------------------------------------


class TestStellerateStarDestroysAllFleetsInSystem:
    """Per user: a system is the 50-hex radius around its center; firing
    STELLERATE_STAR must destroy EVERY fleet in that radius, regardless of
    whether the fleet is at a planet hex, star hex, warp point, or open
    space within the system."""

    def test_fleet_at_planet_hex_is_destroyed(self):
        """Regression: planet-orbiting fleet survived because planets were
        unregistered before `get_all_fleets_in_system` scanned planet hexes."""
        galaxy, system, planet, empire = _build_scenario()
        actor = Fleet(1, empire.id, system.global_location)
        _add_actor_ship(actor)
        actor.orders.append(Order(OrderType.STELLERATE_STAR, None))
        empire.fleets.append(actor)
        galaxy.register_fleet(actor)

        planet_hex = system.global_location + planet.location
        bystander = Fleet(2, empire.id, planet_hex)
        empire.fleets.append(bystander)
        galaxy.register_fleet(bystander)

        proc = SuperweaponOrderProcessor()
        proc.process_stellerate_star(
            actor, empire, galaxy, [empire], _stellerator_registry()
        )

        assert bystander not in empire.fleets, (
            "Fleet orbiting a planet in the stellerated system survived. "
            "Likely cause: planets unregistered before fleet collection runs, "
            "so planet hexes are not in the 'system hexes' set."
        )

    def test_fleet_in_open_space_within_system_radius_is_destroyed(self):
        """Per user: a system has a 50-hex radius and everything inside
        dies. Place a fleet at a hex with no star/planet/warp point but
        within the system radius."""
        galaxy, system, planet, empire = _build_scenario()
        actor = Fleet(1, empire.id, system.global_location)
        _add_actor_ship(actor)
        actor.orders.append(Order(OrderType.STELLERATE_STAR, None))
        empire.fleets.append(actor)
        galaxy.register_fleet(actor)

        # Far from any placed entity but comfortably inside the 50-hex radius.
        open_space_hex = system.global_location + HexCoord(20, 15)
        bystander = Fleet(2, empire.id, open_space_hex)
        empire.fleets.append(bystander)
        galaxy.register_fleet(bystander)

        proc = SuperweaponOrderProcessor()
        proc.process_stellerate_star(
            actor, empire, galaxy, [empire], _stellerator_registry()
        )

        assert bystander not in empire.fleets, (
            "Fleet in open-space hex within the system radius survived."
        )

    def test_fleet_outside_system_radius_survives(self):
        """A fleet farther than the system radius (50) must NOT be caught
        in the explosion."""
        galaxy, system, planet, empire = _build_scenario()
        actor = Fleet(1, empire.id, system.global_location)
        _add_actor_ship(actor)
        actor.orders.append(Order(OrderType.STELLERATE_STAR, None))
        empire.fleets.append(actor)
        galaxy.register_fleet(actor)

        # Well outside the 50-hex radius.
        distant_hex = system.global_location + HexCoord(60, 0)
        bystander = Fleet(2, empire.id, distant_hex)
        empire.fleets.append(bystander)
        galaxy.register_fleet(bystander)

        proc = SuperweaponOrderProcessor()
        proc.process_stellerate_star(
            actor, empire, galaxy, [empire], _stellerator_registry()
        )

        assert bystander in empire.fleets, (
            "Fleet beyond the 50-hex radius was destroyed — system cleanup "
            "reached too far."
        )

    def test_actor_fleet_is_also_destroyed(self):
        """STELLERATE_STAR is a suicide weapon: the firing fleet dies too."""
        galaxy, system, planet, empire = _build_scenario()
        actor = Fleet(1, empire.id, system.global_location)
        _add_actor_ship(actor)
        actor.orders.append(Order(OrderType.STELLERATE_STAR, None))
        empire.fleets.append(actor)
        galaxy.register_fleet(actor)

        proc = SuperweaponOrderProcessor()
        proc.process_stellerate_star(
            actor, empire, galaxy, [empire], _stellerator_registry()
        )

        assert actor not in empire.fleets
