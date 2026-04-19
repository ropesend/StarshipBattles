"""Integration test pinning projector vs engine drain agreement (PROJ-292 H2).

`PlanetEconomyProjector._project_yard_drain` reaches into the
`_collect_planet_sources` private API from `build_queue_source.py` and
mirrors `ProductionEngine._process_queue_tick_dynamic` rate math. This
file pins that the two paths agree — if either refactors in a
signature-breaking way, these tests catch the drift loudly.

Contract under test:
    For every resource the queue item's `total_cost` declares,
        projector per-turn yard drain == engine per-tick drain × 100
when the queue item is too expensive to complete within a single turn
(so drain is rate-bound, not cost-capped).

Scope caveat (documented divergence): the projector sums `build_rate`
across EVERY resource declared in the queue's production rate —
including resources the current queue item doesn't cost. The engine
only drains resources the item's `total_cost` actually requires. So
pinning "projector == engine" requires restricting the comparison to
the resources the item costs; other projector entries are "would-drain
if the item needed them" ghost projections, not bugs.
"""
from __future__ import annotations

from unittest.mock import Mock

import pytest

from game.core.hex_math import HexCoord
from game.strategy.config.economy_config import EconomyConfig
from game.strategy.data.empire import Empire
from game.strategy.data.planet import Planet, PlanetType, PlanetaryFacility
from game.strategy.engine.production_engine import ProductionEngine
from game.strategy.services.planet_economy_projector import PlanetEconomyProjector


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_planetary_yard() -> PlanetaryFacility:
    """Operational PlanetaryYard — unlocks the planet-base queue for
    `ProductionEngine._process_queue_tick_dynamic`."""
    return PlanetaryFacility(
        instance_id="yard",
        design_id="colony_hub",
        name="Colony Hub",
        design_data={
            "layers": {
                "CORE": [{"id": "yard", "abilities": {"PlanetaryYard": True}}]
            }
        },
        is_operational=True,
    )


def _make_shipyard_facility() -> PlanetaryFacility:
    """Operational SpaceShipyard facility — unlocks a second queue source
    on the planet alongside the base PlanetaryYard."""
    return PlanetaryFacility(
        instance_id="shipyard",
        design_id="orbital_shipyard",
        name="Orbital Shipyard",
        design_data={
            "layers": {
                "CORE": [
                    {
                        "id": "shipyard",
                        "abilities": {
                            "SpaceShipyard": {
                                "construction_speed_bonus": 1.0,
                                "production_rates": {
                                    "metals": 1000.0, "organics": 500.0,
                                    "vapors": 300.0, "radioactives": 200.0,
                                    "exotics": 100.0,
                                },
                            }
                        },
                    }
                ]
            }
        },
        is_operational=True,
    )


def _make_planet_with_yard(*, facilities=None, owner_id: int = 0) -> Planet:
    planet = Planet(
        name="Earth",
        location=HexCoord(0, 0),
        orbit_distance=2,
        mass=5.97e24,
        radius=6.371e6,
        surface_area=5.1e14,
        density=5515.0,
        surface_gravity=9.81,
        surface_pressure=101325.0,
        surface_temperature=288.0,
        surface_water=0.71,
        tectonic_activity=0.3,
        magnetic_field=1.0,
        planet_type=PlanetType.CONTINENTAL,
        owner_id=owner_id,
    )
    planet.facilities = [_make_planetary_yard()] + (facilities or [])
    return planet


@pytest.fixture
def stub_race_registry():
    """Registry stub that returns None for every lookup — colonies with
    no populations fall through to `planet_habitability_multiplier = 1.0`.
    The projector-vs-engine comparison then isn't muddied by a
    habitability mismatch (the engine uses `_get_habitability_mult`'s
    None-fallback = 1.0 as well when constructed without a race
    registry)."""
    stub = Mock()
    stub.get_race.return_value = None
    return stub


@pytest.fixture
def economy():
    return EconomyConfig(population_consumption={"organics": 0.001})


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestProjectorMatchesEngineDrain:
    """Pin that `PlanetEconomyProjector._project_yard_drain` agrees with
    `ProductionEngine._process_queue_tick_dynamic`. PROJ-292 H2."""

    def test_yard_drain_projection_matches_engine_tick_for_planetary_yard(
        self, minimal_registries, stub_race_registry, economy,
    ):
        """Planet-base queue with a complex so expensive it cannot
        complete within a single tick: drain is rate-bound, so the
        projector's per-turn projection must equal the engine's per-tick
        drain × 100."""
        planet = _make_planet_with_yard()
        # Huge total_cost prevents the item from completing in one
        # tick — drain is purely rate-driven.
        planet.construction_queue = [{
            "design_id": "big_complex",
            "type": "complex",
            "total_cost": {"metals": 10_000_000.0},
            "resources_consumed": {},
        }]

        # Planet-context construction drains from the colony's local
        # stockpile (see ProductionEngine._check_affordability). Seed it
        # with plenty of metals so affordability never blocks the tick.
        planet.stockpile = {"metals": 10_000_000.0}

        empire = Empire(empire_id=0, name="Test", color=(255, 0, 0))
        empire.colonies = [planet]

        # 1. Project.
        projector = PlanetEconomyProjector(
            registries=minimal_registries,
            economy_config=economy,
            race_registry=stub_race_registry,
        )
        projection = projector.project(planet)
        projected_drain_per_turn = {
            r: proj.yard for r, proj in projection.items() if proj.yard > 0
        }

        assert projected_drain_per_turn, (
            "Projection produced no yard drain — fixture is degenerate."
        )

        # 2. Run one tick of the engine.
        pre_planet_stock = dict(planet.stockpile)
        engine = ProductionEngine(registries=minimal_registries)
        engine.process_construction_tick(tick=1, empires=[empire], galaxy=None)
        post_planet_stock = dict(planet.stockpile)

        actual_drain_per_tick = {
            res: pre_planet_stock.get(res, 0.0) - post_planet_stock.get(res, 0.0)
            for res in set(pre_planet_stock) | set(post_planet_stock)
        }

        # 3. Pin the contract for EACH resource the item actually costs.
        # The projector's `build_rate` dict reports rate-bound drain for
        # every resource the production_rate declares; the engine only
        # drains resources the specific item needs. So the contract
        # `projector == engine × 100` only holds for resources in
        # `item.total_cost`. See the module docstring's scope caveat.
        item_cost_resources = set(planet.construction_queue[0]["total_cost"])
        for res in item_cost_resources:
            projected = projected_drain_per_turn.get(res, 0.0)
            actual_tick = actual_drain_per_tick.get(res, 0.0)
            assert actual_tick * 100 == pytest.approx(projected, rel=0.01), (
                f"Projector-vs-engine drift for {res!r}: projector says "
                f"{projected}/turn, engine drained {actual_tick}/tick "
                f"({actual_tick * 100}/turn). If this fires, "
                f"`_collect_planet_sources` or `_process_queue_tick_dynamic` "
                f"refactored its rate math without updating the other path."
            )

    def test_yard_drain_zero_when_queue_empty(
        self, minimal_registries, stub_race_registry, economy,
    ):
        """A PlanetaryYard with an empty queue: projector predicts zero
        yard drain; engine drains zero. Pins the empty-queue short-circuit
        on both sides."""
        planet = _make_planet_with_yard()
        planet.construction_queue = []

        planet.stockpile = {"metals": 1_000_000.0}

        empire = Empire(empire_id=0, name="Test", color=(255, 0, 0))
        empire.colonies = [planet]

        projector = PlanetEconomyProjector(
            registries=minimal_registries,
            economy_config=economy,
            race_registry=stub_race_registry,
        )
        projection = projector.project(planet)
        projected_drain = {
            r: proj.yard for r, proj in projection.items() if proj.yard > 0
        }

        pre_stock = dict(planet.stockpile)
        engine = ProductionEngine(registries=minimal_registries)
        engine.process_construction_tick(tick=1, empires=[empire], galaxy=None)
        post_stock = dict(planet.stockpile)

        assert projected_drain == {}, (
            f"Projector projected yard drain on an empty queue: {projected_drain}"
        )
        assert pre_stock == post_stock, (
            f"Engine drained on an empty queue: pre={pre_stock}, post={post_stock}"
        )

    def test_multi_queue_drain_aggregates_across_yards(
        self, minimal_registries, stub_race_registry, economy,
    ):
        """Planet with both a PlanetaryYard + a shipyard, each with a
        queued item. Projector's drain must equal the engine's per-tick
        drain × 100 aggregated across both queues."""
        shipyard = _make_shipyard_facility()
        shipyard.construction_queue = [{
            "design_id": "battleship",
            "type": "ship",
            "total_cost": {"metals": 10_000_000.0},
            "resources_consumed": {},
        }]

        planet = _make_planet_with_yard(facilities=[shipyard])
        # Planet-base queue: a complex too expensive to finish in a tick.
        planet.construction_queue = [{
            "design_id": "mega_complex",
            "type": "complex",
            "total_cost": {"metals": 10_000_000.0},
            "resources_consumed": {},
        }]

        planet.stockpile = {"metals": 10_000_000.0}

        empire = Empire(empire_id=0, name="Test", color=(255, 0, 0))
        empire.colonies = [planet]

        projector = PlanetEconomyProjector(
            registries=minimal_registries,
            economy_config=economy,
            race_registry=stub_race_registry,
        )
        projection = projector.project(planet)
        projected_drain = {
            r: proj.yard for r, proj in projection.items() if proj.yard > 0
        }

        pre_stock = dict(planet.stockpile)
        engine = ProductionEngine(registries=minimal_registries)
        engine.process_construction_tick(tick=1, empires=[empire], galaxy=None)
        post_stock = dict(planet.stockpile)

        actual_drain_per_tick = {
            res: pre_stock.get(res, 0.0) - post_stock.get(res, 0.0)
            for res in set(pre_stock) | set(post_stock)
        }

        # Metals drain must aggregate across BOTH queues (PlanetaryYard
        # base rate = 3000/turn + SpaceShipyard custom rate = 1000/turn
        # = 4000/turn total). Both queue items cost only metals so the
        # comparison scope is just "metals".
        metals_projected = projected_drain.get("metals", 0.0)
        metals_actual_per_turn = actual_drain_per_tick.get("metals", 0.0) * 100
        assert metals_actual_per_turn == pytest.approx(metals_projected, rel=0.01), (
            f"Multi-queue drift: projector {metals_projected}/turn vs "
            f"engine {metals_actual_per_turn}/turn"
        )
