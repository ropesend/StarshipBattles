"""End-to-end regression tests for stabilizer-blocks-superweapon.

User report (PROJ-277): built QS Stellar/Warp/Geologic Stabilizer
complexes, activated them, saw "Active" in the System Effects panel for
several turns, then issued STELLERATE_STAR / CLOSE_WARP_POINT /
IMPLODE_PLANET orders against their own targets — none were blocked.

Root cause: `SuperweaponOrderProcessor` called `find_abilities_in_scope`
without threading the component registry. Real QS designs store
`{"id": "stellar_stabilizer"}` with no inline abilities dict — ability
data is resolved by registry lookup, which the scanner could not do when
`registries is None`. The UI's `system_effects_collector` DID thread the
registry, which is why the "Active" label was correct while the actual
check silently found nothing.

Fix: `StabilizerRegistry` (data-driven ability→superweapon map) consumed
by `SuperweaponOrderProcessor._check_blocking_stabilizer`, with
`component_registry` threaded through every superweapon handler.

These tests set up the exact post-activation state (facility with
`component_states[composite_key] = ACTIVE`) using the REALISTIC
design_data shape (bare `{"id": ...}` entries), and exercise the real
scanner + `StabilizerRegistry` + superweapon handlers. If any assertion
fails, the registry is no longer threaded through some path.
"""
from __future__ import annotations

from game.core.hex_math import HexCoord
from game.core.patterns.layer_iterator import generate_component_key
from game.strategy.data.component_activation_state import (
    ActivationPhase,
    ComponentActivationState,
)
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.data.galaxy import Galaxy, StarSystem, WarpPoint
from game.strategy.data.order_types import Order, OrderType
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.planetary_facility import PlanetaryFacility
from game.strategy.data.spectrum import Spectrum
from game.strategy.data.stars import Star, StarType
from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor
from game.strategy.services.stabilizer_registry import find_blocking_stabilizer


def _make_component_registry(comp_id: str, ability_name: str) -> dict:
    """Build the minimal component-registry dict the scanner needs.

    Real games load this from `data/components.json`; for tests we emit
    just the component(s) under test. The scanner accepts either
    `GameRegistries` or a plain components dict (see component_inspector).
    """
    return {
        comp_id: {
            "id": comp_id,
            "abilities": {
                ability_name: {
                    "scope": "system",
                    "activation_time": 250,
                    "deactivation_time": 150,
                    "energy_drain_rate": 100.0,
                }
            },
        }
    }


# ---------------------------------------------------------------------------
# Fixtures — build a real galaxy/system/planet/stabilizer-facility
# ---------------------------------------------------------------------------


def _spectrum() -> Spectrum:
    return Spectrum(0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0)


def _make_planet(name: str, local_loc: HexCoord, owner_id: int) -> Planet:
    p = Planet(
        name=name,
        location=local_loc,
        orbit_distance=3,
        mass=1e24,
        radius=6e6,
        surface_area=5e14,
        density=5500,
        surface_gravity=9.8,
        surface_pressure=101325,
        surface_temperature=288,
        surface_water=0.7,
        tectonic_activity=0.5,
        magnetic_field=1.0,
        planet_type=PlanetType.CONTINENTAL,
        image_id="test.png",
    )
    p.owner_id = owner_id
    return p


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


def _make_stabilizer_facility(ability_name: str, comp_id: str) -> tuple[PlanetaryFacility, str]:
    """Build a facility with a stabilizer component already in ACTIVE phase.

    Uses the REALISTIC design_data shape saved by the Workshop / QS starter
    designs: `{"id": "...", "modifiers": [...]}` with no inline `abilities`
    dict. Ability data lives in the component registry — the scanner must
    fall back to the registry via `extract_abilities_from_component`.

    Returns (facility, composite_component_key).
    """
    design_data = {
        "layers": {
            "CORE": [
                {"id": comp_id, "modifiers": []}
            ]
        }
    }
    facility = PlanetaryFacility(
        instance_id=f"fac_{comp_id}",
        design_id=f"design_{comp_id}",
        name=f"{comp_id} Complex",
        design_data=design_data,
        is_operational=True,
    )
    comp_key = generate_component_key("CORE", 0, comp_id)
    # Post-activation state: ACTIVE (player has waited for ACTIVATING → ACTIVE).
    active_state = ComponentActivationState(
        phase=ActivationPhase.ACTIVE,
        progress_ticks=250,
        required_ticks=250,
        ability_name=ability_name,
        energy_drain_rate=100.0,
    )
    facility.set_activation_state(comp_key, active_state)
    assert facility.get_activation_state(comp_key).phase == ActivationPhase.ACTIVE
    return facility, comp_key


def _make_galaxy_with_active_stabilizer(
    ability_name: str,
    comp_id: str,
    owner_empire_id: int = 1,
) -> tuple[Galaxy, StarSystem, Planet, Empire, PlanetaryFacility, str]:
    """Build a full galaxy with one system, one colony, one ACTIVE stabilizer."""
    galaxy = Galaxy(radius=100)
    star = _make_star("Stabilized Star")
    system = StarSystem("Stabilized System", HexCoord(0, 0), stars=[star])
    galaxy.add_system(system)

    planet = _make_planet("Stabilizer Host", HexCoord(3, 0), owner_id=owner_empire_id)
    system.planets.append(planet)
    galaxy.register_planet(system, planet)

    facility, comp_key = _make_stabilizer_facility(ability_name, comp_id)
    planet.facilities.append(facility)

    empire = Empire(owner_empire_id, "Player", (255, 0, 0))
    empire.colonies.append(planet)
    return galaxy, system, planet, empire, facility, comp_key


# ---------------------------------------------------------------------------
# Phase A — direct `find_blocking_stabilizer` checks.
# If these fail, the registry-threading or scanner lookup is broken.
# ---------------------------------------------------------------------------


class TestStabilizerCheckRecognizesActiveState:
    """Direct verification that `find_blocking_stabilizer` sees an ACTIVE stabilizer.

    Asserts the integration between:
      - PlanetaryFacility.component_states (storage)
      - strategic_ability_scanner.find_abilities_in_scope (lookup, with registries)
      - stabilizer_registry.find_blocking_stabilizer (order→spec mapping)
    """

    def test_geologic_stabilizer_blocks_implode_planet(self):
        galaxy, system, planet, empire, _, _ = _make_galaxy_with_active_stabilizer(
            "GeologicStabilizer", "geologic_stabilizer_system_scope"
        )
        registry = _make_component_registry(
            "geologic_stabilizer_system_scope", "GeologicStabilizer"
        )

        spec = find_blocking_stabilizer(
            OrderType.IMPLODE_PLANET, planet, galaxy, [empire], registry
        )

        assert spec is not None, (
            "GeologicStabilizer is ACTIVE on the planet's facility but "
            "find_blocking_stabilizer returned None — registry is not being "
            "threaded into the scanner."
        )
        assert spec.ability_name == "GeologicStabilizer"

    def test_stellar_stabilizer_blocks_stellerate(self):
        galaxy, system, planet, empire, _, _ = _make_galaxy_with_active_stabilizer(
            "StellarStabilizer", "stellar_stabilizer"
        )
        registry = _make_component_registry("stellar_stabilizer", "StellarStabilizer")

        spec = find_blocking_stabilizer(
            OrderType.STELLERATE_STAR, planet, galaxy, [empire], registry
        )

        assert spec is not None, (
            "StellarStabilizer is ACTIVE in the system but "
            "find_blocking_stabilizer returned None."
        )
        assert spec.ability_name == "StellarStabilizer"

    def test_warp_field_stabilizer_blocks_close_warp_point(self):
        galaxy, system, planet, empire, _, _ = _make_galaxy_with_active_stabilizer(
            "WarpFieldStabilizer", "warp_field_stabilizer"
        )
        registry = _make_component_registry("warp_field_stabilizer", "WarpFieldStabilizer")

        spec = find_blocking_stabilizer(
            OrderType.CLOSE_WARP_POINT, planet, galaxy, [empire], registry
        )

        assert spec is not None, (
            "WarpFieldStabilizer is ACTIVE in the system but "
            "find_blocking_stabilizer returned None."
        )
        assert spec.ability_name == "WarpFieldStabilizer"

    def test_without_component_registry_no_stabilizer_found(self):
        """Guard against regression: registry is REQUIRED — realistic designs
        store only the component id, so the scanner must look up abilities in
        the registry. Omitting registries must NOT fall back to "blocked"
        (silent false positive) but MUST return None (silent false negative).
        This test codifies the failure mode we just fixed so handlers that
        forget to thread the registry are caught immediately."""
        galaxy, system, planet, empire, _, _ = _make_galaxy_with_active_stabilizer(
            "StellarStabilizer", "stellar_stabilizer"
        )

        spec = find_blocking_stabilizer(
            OrderType.STELLERATE_STAR, planet, galaxy, [empire],
            component_registry=None,
        )

        assert spec is None, (
            "find_blocking_stabilizer returned a spec without a registry. "
            "A registry-less call should return None (caller forgot to thread) "
            "so handlers that omit it are loudly broken, not silently blocked."
        )


# ---------------------------------------------------------------------------
# Phase A (continued) — full superweapon-handler round trips.
# The handler must cancel the order and leave the target intact.
# ---------------------------------------------------------------------------


class TestStabilizerBlocksSuperweaponExecution:
    """Full-handler round trips: order issued, handler runs, target intact."""

    def test_implode_planet_blocked_by_geologic_stabilizer(self):
        galaxy, system, target_planet, empire, _, _ = _make_galaxy_with_active_stabilizer(
            "GeologicStabilizer", "geologic_stabilizer_system_scope"
        )
        # Separate target planet (imploder aims at different planet in same system).
        victim = _make_planet("Victim", HexCoord(5, 0), owner_id=empire.id)
        system.planets.append(victim)
        galaxy.register_planet(system, victim)
        empire.colonies.append(victim)

        victim_hex = system.global_location + victim.location
        fleet = Fleet(1, empire.id, victim_hex)
        fleet.orders.append(Order(OrderType.IMPLODE_PLANET, victim))
        empire.fleets.append(fleet)

        registry = _make_component_registry(
            "geologic_stabilizer_system_scope", "GeologicStabilizer"
        )
        proc = SuperweaponOrderProcessor()
        result = proc.process_implode_planet(fleet, empire, galaxy, [empire], registry)

        assert victim in system.planets, "IMPLODE_PLANET executed despite active stabilizer"
        assert result.success is False
        assert len(fleet.orders) == 0, "Order should be popped after cancellation"

    def test_stellerate_star_blocked_by_stellar_stabilizer(self):
        galaxy, system, planet, empire, _, _ = _make_galaxy_with_active_stabilizer(
            "StellarStabilizer", "stellar_stabilizer"
        )
        fleet = Fleet(1, empire.id, system.global_location)
        fleet.orders.append(Order(OrderType.STELLERATE_STAR, None))
        empire.fleets.append(fleet)

        assert len(system.stars) == 1
        registry = _make_component_registry("stellar_stabilizer", "StellarStabilizer")
        proc = SuperweaponOrderProcessor()
        result = proc.process_stellerate_star(fleet, empire, galaxy, [empire], registry)

        assert len(system.stars) == 1, "STELLERATE_STAR executed despite active stabilizer"
        assert result.success is False
        assert len(fleet.orders) == 0

    def test_close_warp_point_blocked_by_warp_stabilizer(self):
        galaxy, system, planet, empire, _, _ = _make_galaxy_with_active_stabilizer(
            "WarpFieldStabilizer", "warp_field_stabilizer"
        )
        # Add a second system + a warp point to close. Warp points are
        # keyed by destination system's global_location.
        system2 = StarSystem("Other", HexCoord(50, 50), stars=[_make_star("Other Star")])
        galaxy.add_system(system2)
        wp1 = WarpPoint(destination_id=system2.global_location, location=HexCoord(2, 0))
        wp2 = WarpPoint(destination_id=system.global_location, location=HexCoord(-2, 0))
        system.warp_points.append(wp1)
        system2.warp_points.append(wp2)

        wp_hex = system.global_location + wp1.location
        fleet = Fleet(1, empire.id, wp_hex)
        fleet.orders.append(Order(OrderType.CLOSE_WARP_POINT, wp1))
        empire.fleets.append(fleet)

        registry = _make_component_registry(
            "warp_field_stabilizer", "WarpFieldStabilizer"
        )
        proc = SuperweaponOrderProcessor()
        result = proc.process_close_warp_point(fleet, empire, galaxy, [empire], registry)

        assert wp1 in system.warp_points, "CLOSE_WARP_POINT executed despite active stabilizer"
        assert result.success is False
        assert len(fleet.orders) == 0
