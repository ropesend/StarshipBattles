"""CREATE_DYSON_SPHERE superweapon handler (PROJ-396 Phase 3, ex Task 5.4).

Removes star and nearby planets (within zone radius), creates a Dyson
Sphere planet at system center using the race's ideal environmental
conditions (or sensible defaults). Ship preserved.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from game.core.hex_math import HexCoord, hex_distance
from game.strategy.data.fleet import Fleet
from game.strategy.data.galaxy import Galaxy
from game.strategy.data.order_types import OrderType
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.services.superweapon_registry import find_superweapon_spec

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.engine.superweapon_order_processor import (
        SuperweaponOrderProcessor,
        SuperweaponResult,
    )


def process_create_dyson_sphere(
    processor: "SuperweaponOrderProcessor",
    fleet: Fleet,
    empire: "Empire",
    galaxy: Galaxy,
    empires: list["Empire"],
    component_registry: dict[str, Any] | None = None,
) -> "SuperweaponResult":
    """Process a CREATE_DYSON_SPHERE order via spec-driven dispatch."""
    from game.strategy.engine.superweapon_order_processor import SuperweaponResult

    spec = find_superweapon_spec(OrderType.CREATE_DYSON_SPHERE)

    def _precheck(*, fleet, empire, galaxy, empires, order, component_registry) -> "SuperweaponResult | None":
        system = processor._get_system_at_hex(galaxy, fleet.location)
        if system is None:
            return SuperweaponResult(
                success=False, message="Fleet not at a star system"
            )
        if not system.stars:
            return SuperweaponResult(
                success=False, message="System has no stars"
            )
        return None

    def _effect(*, fleet, empire, galaxy, empires, order, ship, component_registry) -> "dict[str, Any]":
        system = processor._get_system_at_hex(galaxy, fleet.location)
        primary_star = system.stars[0]
        star_loc = primary_star.location

        # Remove planets within zone radius (radius_hexes=6 -> 91 hexes,
        # center + 5 rings).
        dyson_radius = 5
        planets_to_remove = [
            planet for planet in system.planets
            if hex_distance(planet.location, star_loc) <= dyson_radius
        ]
        mutator = processor._get_empire_mutator()
        for planet in planets_to_remove:
            if planet.owner_id is not None:
                # PROJ-370 Phase 4: route through IEmpireMutator.
                for emp in empires:
                    mutator.remove_colony(emp, planet)
            galaxy.unregister_planet(planet)

        system.stars = []

        # PROJ-283 Phase 4: registry-driven preferences.
        race = empire.race_config if empire else None
        if race:
            prefs = race.preferences
            gravity = prefs["gravity"].setpoint
            temperature = prefs["temperature"].setpoint
            water = prefs["water"].setpoint
            atmosphere = {
                factor_id.split(".", 1)[1]: pref.setpoint
                for factor_id, pref in prefs.items()
                if factor_id.startswith("gas.") and pref.setpoint > 0
            }
        else:
            gravity = 9.81  # 1g
            temperature = 288.0  # ~15°C
            water = 0.3
            atmosphere = {"O2": 21000.0, "N2": 79000.0}  # Earth-like (Pa)

        dyson = Planet(
            name=f"Dyson Sphere ({system.name})",
            location=HexCoord(0, 0),
            orbit_distance=0,
            mass=2e30,
            radius=1.5e11,
            surface_area=1e18,
            density=1.0,
            surface_gravity=gravity,
            surface_pressure=101325.0,
            surface_temperature=temperature,
            surface_water=water,
            atmosphere=atmosphere,
            tectonic_activity=0.0,
            magnetic_field=1.0,
            planet_type=PlanetType.DYSON_SPHERE,
            image_id="Sphereworld_Portrait.png",
            radius_hexes=6,
        )
        system.planets.append(dyson)
        galaxy.register_planet(system, dyson)

        return {
            "event_message": f"Dyson Sphere created in {system.name}",
            "log_message": f"Dyson Sphere created in {system.name}",
            "system_name": system.name,
            "planet_id": dyson.id,
            "planet_name": dyson.name,
        }

    return processor.execute_superweapon(
        fleet, empire, galaxy, empires, spec, _effect, component_registry,
        precheck_fn=_precheck,
    )
