"""Tests for engine event emission (PROJ-77 Phase 3).

Verifies that ProductionEngine, OrderProcessor, and ConflictResolutionEngine
emit the correct events via EventBus when significant actions occur.
"""

import pytest
from unittest.mock import MagicMock, patch, call

from game.core.event_logging import EventBus
from game.strategy.data.order_types import OrderType
from game.strategy.events import EventType, EventCategory
from game.strategy.systems.design_repository import DesignLoadResult  # noqa: F401


def _wire_catalog_on(engine, empire_id, data):
    """PROJ-427 Phase 3 helper: wire a per-empire catalog map onto the
    engine's spawner with ``data`` available under all test design_ids.
    """
    from game.strategy.systems.design_catalog import DesignCatalog
    cat = DesignCatalog(empire_id=empire_id)
    for did in (
        "scout_design", "cruiser_design", "bad_design", "scout",
        "fighter_design", "complex_design", "complex_xyz", "shipyard",
    ):
        cat._data_by_id[did] = data
    engine._spawner.set_design_catalogs_by_empire({empire_id: cat})
    return cat


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _capture_log_event_calls():
    """Return a (calls_list, fake_handler, EventBus) tuple.

    The EventBus routes events through the fake handler so engines that use
    ``self._event_bus.log_event(...)`` will populate the calls list.
    """
    calls = []

    def _fake_log_event(event_type, **kwargs):
        calls.append((event_type, kwargs))

    bus = EventBus(_fake_log_event)
    return calls, _fake_log_event, bus


def _make_mock_empire(empire_id: int = 0, name: str = "Test Empire"):
    empire = MagicMock()
    empire.id = empire_id
    empire.name = name
    empire.colonies = []
    empire.fleets = []
    empire.add_fleet = MagicMock()
    empire.get_next_fleet_id = MagicMock(return_value=1)
    return empire


def _make_mock_planet(planet_id: int = 1, name: str = "Alpha Prime"):
    from game.core.hex_math import HexCoord

    planet = MagicMock()
    planet.id = planet_id
    planet.name = name
    planet.owner_id = 0
    planet.location = HexCoord(5, 5)
    planet.construction_queue = []
    planet.facilities = []
    return planet


def _make_mock_galaxy():
    galaxy = MagicMock()
    galaxy.get_system_of_planet = MagicMock(return_value=None)
    return galaxy


def _make_shipyard_facility():
    from game.strategy.data.planetary_facility import PlanetaryFacility

    return PlanetaryFacility(
        instance_id="yard_test",
        design_id="shipyard_complex",
        name="Space Shipyard",
        design_data={
            "layers": {
                "CORE": [{
                    "id": "space_shipyard",
                    "abilities": {"SpaceShipyard": {"value": 1}}
                }]
            }
        },
        is_operational=True,
    )


# ===========================================================================
# Production: Ship Built
# ===========================================================================


class TestShipBuiltEvent:
    """ProductionEngine emits ship_built event when a ship is spawned."""

    def test_spawn_ship_emits_ship_built_event(self, fresh_registries):
        """_spawn_ship() calls log_event with ship_built type."""
        from game.strategy.engine.production_engine import ProductionEngine

        calls, fake, bus = _capture_log_event_calls()
        engine = ProductionEngine(registries=fresh_registries, event_bus=bus)
        empire = _make_mock_empire()
        planet = _make_mock_planet()
        galaxy = _make_mock_galaxy()


        # PROJ-323 Task 2.16: flattened triple-nested with-patch via patch.multiple
        from unittest.mock import DEFAULT
        with patch.multiple(
            'game.strategy.engine.production_spawner',
            ShipInstance=DEFAULT, Fleet=DEFAULT,
        ) as mocks:

            mock_ship = MagicMock()
            mock_ship.name = "Scout Ship"
            mocks['ShipInstance'].create.return_value = mock_ship

            mock_fleet = MagicMock()
            mock_fleet.id = 1
            mocks['Fleet'].return_value = mock_fleet

            _wire_catalog_on(engine, empire.id, {"name": "Scout Ship"})
            engine._spawner._spawn_ship(planet, "scout_design", empire, galaxy)

        assert len(calls) == 1
        etype, kw = calls[0]
        assert etype == EventType.SHIP_BUILT
        assert kw["category"] == EventCategory.PRODUCTION
        assert kw["empire_id"] == 0
        assert "Scout Ship" in kw["message"]
        assert "Alpha Prime" in kw["message"]

    def test_spawn_ship_event_includes_details(self, fresh_registries):
        """ship_built event includes design_id, planet_id, fleet_id."""
        from game.strategy.engine.production_engine import ProductionEngine

        calls, fake, bus = _capture_log_event_calls()
        engine = ProductionEngine(registries=fresh_registries, event_bus=bus)
        empire = _make_mock_empire()
        planet = _make_mock_planet(planet_id=42, name="Beta")
        galaxy = _make_mock_galaxy()


        # PROJ-323 Task 2.16: flattened triple-nested with-patch via patch.multiple
        from unittest.mock import DEFAULT
        with patch.multiple(
            'game.strategy.engine.production_spawner',
            ShipInstance=DEFAULT, Fleet=DEFAULT,
        ) as mocks:

            mock_ship = MagicMock()
            mocks['ShipInstance'].create.return_value = mock_ship

            mock_fleet = MagicMock()
            mock_fleet.id = 1
            mocks['Fleet'].return_value = mock_fleet

            _wire_catalog_on(engine, empire.id, {"name": "Scout Ship"})
            engine._spawner._spawn_ship(planet, "cruiser_design", empire, galaxy)

        assert len(calls) == 1
        _, kw = calls[0]
        assert kw["design_id"] == "cruiser_design"
        assert kw["planet_id"] == 42

    def test_spawn_ship_no_event_when_no_catalog(self, fresh_registries):
        """PROJ-427 Phase 3: no event when no catalog is wired."""
        from game.strategy.engine.production_engine import ProductionEngine

        calls, fake, bus = _capture_log_event_calls()
        engine = ProductionEngine(registries=fresh_registries, event_bus=bus)
        empire = _make_mock_empire()
        planet = _make_mock_planet()
        galaxy = _make_mock_galaxy()

        # No catalog wired — spawn should skip without emitting an event.
        engine._spawner._spawn_ship(planet, "scout", empire, galaxy)

        assert len(calls) == 0

    def test_spawn_ship_no_event_when_design_not_in_catalog(self, fresh_registries):
        """No event emitted when design isn't in the catalog."""
        from game.strategy.engine.production_engine import ProductionEngine
        from game.strategy.systems.design_catalog import DesignCatalog

        calls, fake, bus = _capture_log_event_calls()
        engine = ProductionEngine(registries=fresh_registries, event_bus=bus)
        empire = _make_mock_empire()
        planet = _make_mock_planet()
        galaxy = _make_mock_galaxy()

        # Wire an empty catalog (no design entries).
        empty_cat = DesignCatalog(empire_id=empire.id)
        engine._spawner.set_design_catalogs_by_empire({empire.id: empty_cat})

        engine._spawner._spawn_ship(planet, "missing_design", empire, galaxy)

        assert len(calls) == 0


# ===========================================================================
# Production: Fleet Ship Built
# ===========================================================================


class TestFleetShipBuiltEvent:
    """ProductionEngine emits ship_built event for fleet yard production."""

    def test_spawn_fleet_ship_emits_ship_built_event(self, fresh_registries):
        """_spawn_fleet_ship() calls log_event with ship_built type."""
        from game.strategy.engine.production_engine import ProductionEngine
        from game.strategy.data.fleet import Fleet

        calls, fake, bus = _capture_log_event_calls()
        engine = ProductionEngine(registries=fresh_registries, event_bus=bus)
        empire = _make_mock_empire()
        fleet = MagicMock(spec=Fleet)
        fleet.id = 7
        fleet.location = MagicMock(q=5, r=-3)


        if True:

            with patch('game.strategy.engine.production_spawner.ShipInstance') as mock_si:
                mock_ship = MagicMock()
                mock_ship.name = "Fighter"
                mock_si.create.return_value = mock_ship

                _wire_catalog_on(engine, empire.id, {"name": "Scout Ship"})
                engine._spawner._spawn_fleet_ship(fleet, "fighter_design", empire)

        assert len(calls) == 1
        etype, kw = calls[0]
        assert etype == EventType.SHIP_BUILT
        assert kw["category"] == EventCategory.PRODUCTION
        assert kw["empire_id"] == 0
        assert kw["fleet_id"] == 7
        assert kw["is_fleet_production"] is True
        assert "Fighter" in kw["message"]
        assert kw["location_hex"] == [5, -3]

    def test_spawn_fleet_ship_no_event_when_no_catalog(self, fresh_registries):
        """PROJ-427 Phase 3: no event when no catalog wired."""
        from game.strategy.engine.production_engine import ProductionEngine
        from game.strategy.data.fleet import Fleet

        calls, fake, bus = _capture_log_event_calls()
        engine = ProductionEngine(registries=fresh_registries, event_bus=bus)
        empire = _make_mock_empire()
        fleet = MagicMock(spec=Fleet)
        fleet.id = 7

        # No catalog wired.
        engine._spawner._spawn_fleet_ship(fleet, "fighter", empire)

        assert len(calls) == 0


# ===========================================================================
# Production: Complex Built
# ===========================================================================


class TestComplexBuiltEvent:
    """ProductionEngine emits complex_built event when a complex is spawned."""

    def test_spawn_complex_emits_complex_built_event(self, fresh_registries):
        """_spawn_complex() calls log_event with complex_built type."""
        from game.strategy.engine.production_engine import ProductionEngine

        calls, fake, bus = _capture_log_event_calls()
        engine = ProductionEngine(registries=fresh_registries, event_bus=bus)
        empire = _make_mock_empire()
        planet = _make_mock_planet(name="Gamma Station")


        # PROJ-427 Phase 3: catalog supplies "Mining Complex" so the
        # COMPLEX_BUILT event message includes that human-readable name.
        from game.strategy.systems.design_catalog import DesignCatalog
        cat = DesignCatalog(empire_id=empire.id)
        cat._data_by_id["mining_complex"] = {"name": "Mining Complex"}
        engine._spawner.set_design_catalogs_by_empire({empire.id: cat})
        engine._spawner._create_and_place_facility(planet, "mining_complex", empire)

        assert len(calls) == 1
        etype, kw = calls[0]
        assert etype == EventType.COMPLEX_BUILT
        assert kw["category"] == EventCategory.PRODUCTION
        assert kw["empire_id"] == 0
        assert "Mining Complex" in kw["message"]
        assert "Gamma Station" in kw["message"]

    def test_spawn_complex_event_includes_details(self, fresh_registries):
        """complex_built event includes design_id and planet_id."""
        from game.strategy.engine.production_engine import ProductionEngine

        calls, fake, bus = _capture_log_event_calls()
        engine = ProductionEngine(registries=fresh_registries, event_bus=bus)
        empire = _make_mock_empire()
        planet = _make_mock_planet(planet_id=99, name="Delta")


        if True:

            _wire_catalog_on(engine, empire.id, {"name": "Scout Ship"})
            engine._spawner._create_and_place_facility(planet, "shipyard_design", empire)

        _, kw = calls[0]
        assert kw["design_id"] == "shipyard_design"
        assert kw["planet_id"] == 99

    def test_spawn_complex_emits_event_even_without_save_path(self, fresh_registries):
        """Complex still gets created (empty design data) and event emitted."""
        from game.strategy.engine.production_engine import ProductionEngine

        calls, fake, bus = _capture_log_event_calls()
        engine = ProductionEngine(registries=fresh_registries, event_bus=bus)
        empire = _make_mock_empire()
        planet = _make_mock_planet()


        _wire_catalog_on(engine, empire.id, {"name": "Scout Ship"})
        engine._spawner._create_and_place_facility(planet, "basic_factory", empire)

        # Complex is still created even without save_path, so event should fire
        assert len(calls) == 1
        etype, _ = calls[0]
        assert etype == EventType.COMPLEX_BUILT


# ===========================================================================
# Production: Fleet Complex Built
# ===========================================================================


class TestFleetComplexBuiltEvent:
    """ProductionEngine emits complex_built event for fleet yard complex production."""

    def test_spawn_fleet_complex_emits_complex_built_event(self, fresh_registries):
        """_spawn_fleet_complex() calls log_event with complex_built type."""
        from game.strategy.engine.production_engine import ProductionEngine
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        calls, fake, bus = _capture_log_event_calls()
        engine = ProductionEngine(registries=fresh_registries, event_bus=bus)
        empire = _make_mock_empire()
        fleet = MagicMock(spec=Fleet)
        fleet.id = 9
        fleet.location = HexCoord(5, 5)

        planet = _make_mock_planet(planet_id=42, name="Forge World")
        galaxy = _make_mock_galaxy()
        galaxy.get_planets_at_global_hex.return_value = [planet]


        from game.strategy.systems.design_catalog import DesignCatalog
        cat = DesignCatalog(empire_id=empire.id)
        cat._data_by_id["refinery_design"] = {"name": "Orbital Refinery"}
        engine._spawner.set_design_catalogs_by_empire({empire.id: cat})
        engine._spawner._spawn_fleet_complex(fleet, "refinery_design", empire, galaxy)

        assert len(calls) == 1
        etype, kw = calls[0]
        assert etype == EventType.COMPLEX_BUILT
        assert kw["category"] == EventCategory.PRODUCTION
        assert kw["empire_id"] == 0
        assert "Orbital Refinery" in kw["message"]
        assert "Forge World" in kw["message"]
        assert "fleet yard" in kw["message"]
        assert kw["design_id"] == "refinery_design"
        assert kw["planet_id"] == 42

    def test_spawn_fleet_complex_no_event_when_no_galaxy(self, fresh_registries):
        """No event emitted when galaxy is None."""
        from game.strategy.engine.production_engine import ProductionEngine
        from game.strategy.data.fleet import Fleet

        calls, fake, bus = _capture_log_event_calls()
        engine = ProductionEngine(registries=fresh_registries, event_bus=bus)
        empire = _make_mock_empire()
        fleet = MagicMock(spec=Fleet)
        fleet.id = 9


        _wire_catalog_on(engine, empire.id, {"name": "Scout Ship"})
        engine._spawner._spawn_fleet_complex(fleet, "design_x", empire, galaxy=None)

        assert len(calls) == 0

    def test_spawn_fleet_complex_no_event_when_no_planet_at_hex(self, fresh_registries):
        """No event emitted when fleet is not at a planet hex."""
        from game.strategy.engine.production_engine import ProductionEngine
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        calls, fake, bus = _capture_log_event_calls()
        engine = ProductionEngine(registries=fresh_registries, event_bus=bus)
        empire = _make_mock_empire()
        fleet = MagicMock(spec=Fleet)
        fleet.id = 9
        fleet.location = HexCoord(0, 0)

        galaxy = _make_mock_galaxy()
        galaxy.get_planets_at_global_hex.return_value = []


        _wire_catalog_on(engine, empire.id, {"name": "Scout Ship"})
        engine._spawner._spawn_fleet_complex(fleet, "design_y", empire, galaxy)

        assert len(calls) == 0


# ===========================================================================
# Colony: Colony Founded
# ===========================================================================


class TestColonyFoundedEvent:
    """OrderProcessor emits colony_founded event on colonization."""

    def _make_colonize_fleet(self):
        """Create a fleet with a COLONIZE order."""
        from game.strategy.data.fleet import Fleet
        from game.strategy.data.order_types import Order, OrderType
        from enum import Enum

        class MockPlanetType(Enum):
            CONTINENTAL = "CONTINENTAL"

        fleet = MagicMock(spec=Fleet)
        fleet.id = 3
        fleet.owner_id = 0
        fleet.location = MagicMock(q=2, r=-1)

        # Mock ship with drop pod in carried_items
        mock_ship = MagicMock()
        mock_ship.name = "Colony Ship"
        mock_ship.carried_items = [{"vehicle_type": "drop_pod", "design_id": "test_pod", "name": "Test Pod", "design_data": {"layers": {"CORE": []}}, "mass": 500}]
        fleet.ships = [mock_ship]

        target_planet = _make_mock_planet(planet_id=10, name="New Earth")
        target_planet.owner_id = None
        target_planet.populations = []
        target_planet.planet_type = MockPlanetType.CONTINENTAL

        order = Order(OrderType.COLONIZE, target=target_planet)
        fleet.get_current_order.return_value = order
        fleet.pop_order = MagicMock()

        return fleet, target_planet

    def _make_component_registry(self):
        """Create component registry for tests."""
        return {
            'colony_pod': {
                'id': 'colony_pod',
                'abilities': {'ColonizePlanet': True}
            },
        }

    def test_process_colonize_emits_colony_founded_event(self):
        """process_colonize() emits colony_founded on success."""
        from game.strategy.engine.order_processor import OrderProcessor

        calls, fake, bus = _capture_log_event_calls()
        processor = OrderProcessor(event_bus=bus)
        fleet, target_planet = self._make_colonize_fleet()
        empire = _make_mock_empire(name="Human Empire")
        galaxy = _make_mock_galaxy()
        component_registry = self._make_component_registry()

        with patch('game.strategy.validation.ColonizeValidator') as mock_val:
            mock_result = MagicMock()
            mock_result.is_valid = True
            mock_val.validate.return_value = mock_result
            mock_val.fleet_has_drop_pod.return_value = True
            mock_val.find_ship_with_drop_pod.return_value = (fleet.ships[0], 0)

            with patch.object(processor._handler_registry.get(OrderType.COLONIZE), '_deploy_drop_pod'):
                result = processor.process_colonize(
                    fleet, empire, galaxy,
                    component_registry=component_registry
                )

        assert result.colonized is True
        assert len(calls) == 1
        etype, kw = calls[0]
        assert etype == EventType.COLONY_FOUNDED
        assert kw["category"] == EventCategory.COLONIES
        assert kw["empire_id"] == 0
        assert "New Earth" in kw["message"]
        assert kw["planet_id"] == 10
        assert kw["planet_name"] == "New Earth"

    def test_process_colonize_no_event_on_failure(self):
        """No event emitted when colonization fails validation."""
        from game.strategy.engine.order_processor import OrderProcessor

        calls, fake, bus = _capture_log_event_calls()
        processor = OrderProcessor(event_bus=bus)
        fleet, target_planet = self._make_colonize_fleet()
        empire = _make_mock_empire()
        galaxy = _make_mock_galaxy()
        component_registry = self._make_component_registry()

        with patch('game.strategy.validation.ColonizeValidator') as mock_val:
            mock_result = MagicMock()
            mock_result.is_valid = False
            mock_result.message = "Invalid"
            mock_val.validate.return_value = mock_result

            result = processor.process_colonize(
                    fleet, empire, galaxy,
                    component_registry=component_registry
                )

        assert result.colonized is False
        assert len(calls) == 0

    def test_colonize_any_planet_emits_event_with_resolved_name(self):
        """Colonizing 'any planet' emits event with the resolved planet name."""
        from game.strategy.engine.order_processor import OrderProcessor
        from game.strategy.data.fleet import Fleet
        from game.strategy.data.order_types import Order, OrderType
        from game.strategy.data.planet import Planet
        from enum import Enum

        class MockPlanetType(Enum):
            CONTINENTAL = "CONTINENTAL"

        calls, fake, bus = _capture_log_event_calls()
        processor = OrderProcessor(event_bus=bus)
        empire = _make_mock_empire()
        galaxy = _make_mock_galaxy()
        component_registry = self._make_component_registry()

        # Fleet with COLONIZE target=None (any planet)
        fleet = MagicMock(spec=Fleet)
        fleet.id = 5
        fleet.owner_id = 0

        # Mock ship with drop pod
        mock_ship = MagicMock()
        mock_ship.name = "Colony Ship"
        mock_ship.carried_items = [{"vehicle_type": "drop_pod", "design_id": "test_pod", "name": "Test Pod", "design_data": {"layers": {"CORE": []}}, "mass": 500}]
        fleet.ships = [mock_ship]

        order = Order(OrderType.COLONIZE, target=None)
        fleet.get_current_order.return_value = order
        fleet.pop_order = MagicMock()
        from game.core.hex_math import HexCoord
        fleet.location = HexCoord(0, 0)

        # Galaxy returns a planet at fleet's location - use spec=Planet for isinstance checks
        resolved_planet = MagicMock(spec=Planet)
        resolved_planet.id = 20
        resolved_planet.name = "Wild Planet"
        resolved_planet.owner_id = None
        resolved_planet.populations = []
        resolved_planet.planet_type = MockPlanetType.CONTINENTAL
        galaxy.get_planets_at_global_hex.return_value = [resolved_planet]
        galaxy.get_zones_at_global_hex.return_value = []

        # Patch the validator module where it's imported
        with patch('game.strategy.validation.ColonizeValidator') as mock_val:
            mock_result = MagicMock()
            mock_result.is_valid = True
            mock_val.validate.return_value = mock_result
            mock_val.fleet_has_drop_pod.return_value = True
            mock_val.find_ship_with_drop_pod.return_value = (mock_ship, 0)

            with patch.object(processor._handler_registry.get(OrderType.COLONIZE), '_deploy_drop_pod'):
                result = processor.process_colonize(
                    fleet, empire, galaxy,
                    component_registry=component_registry
                )

        assert result.colonized is True
        assert len(calls) == 1
        _, kw = calls[0]
        assert kw["planet_name"] == "Wild Planet"
        assert kw["planet_id"] == 20


# ===========================================================================
# Combat: Combat Resolved
# ===========================================================================


class TestCombatResolvedEvent:
    """ConflictResolutionEngine emits combat_resolved event on combat."""

    def test_simulated_combat_emits_combat_resolved_event(self):
        """`_resolve_combat_at_hex` emits one combat_resolved event per
        battle (BUG-126: schema migrated to `participating_fleet_ids` /
        `surviving_fleet_ids` / `destroyed_fleet_ids`)."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        mock_resolver = MagicMock()
        mock_result = MagicMock()
        mock_result.winner = 0
        mock_result.team_survivors = {0: [MagicMock()], 1: []}

        # Simulate the PostBattleHook wiping team 1's fleet.
        def _resolve_battle(fleets, **_kw):
            list(fleets)[1].ships = []
            return mock_result

        mock_resolver.resolve_battle.side_effect = _resolve_battle

        calls, fake, bus = _capture_log_event_calls()
        engine = ConflictResolutionEngine(battle_resolver=mock_resolver, event_bus=bus)
        engine._empires = []
        engine._combats_resolved = 0
        engine._fleets_destroyed = []

        emp1 = MagicMock(); emp1.id = 0; emp1.remove_fleet = MagicMock()
        emp2 = MagicMock(); emp2.id = 1; emp2.remove_fleet = MagicMock()
        f1 = MagicMock(spec=Fleet); f1.id = 1; f1.owner_id = 0
        f1.location = HexCoord(3, 4); f1.ships = [MagicMock()]
        f2 = MagicMock(spec=Fleet); f2.id = 2; f2.owner_id = 1
        f2.location = HexCoord(3, 4); f2.ships = [MagicMock()]

        engine._resolve_combat_at_hex([(emp1, f1), (emp2, f2)])

        assert len(calls) == 1
        etype, kw = calls[0]
        assert etype == EventType.COMBAT_RESOLVED
        assert kw["category"] == EventCategory.COMBAT
        assert sorted(kw["participating_fleet_ids"]) == [1, 2]
        assert kw["surviving_fleet_ids"] == [1]
        assert kw["destroyed_fleet_ids"] == [2]

    def test_combat_event_emitted_even_when_no_fleet_destroyed(self):
        """A draw still emits exactly one event; both fleets are
        reported as participants AND survivors."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        mock_resolver = MagicMock()
        mock_result = MagicMock()
        mock_result.winner = None
        mock_result.team_survivors = {0: [MagicMock()], 1: [MagicMock()]}
        mock_resolver.resolve_battle.return_value = mock_result

        calls, fake, bus = _capture_log_event_calls()
        engine = ConflictResolutionEngine(battle_resolver=mock_resolver, event_bus=bus)
        engine._empires = []
        engine._combats_resolved = 0
        engine._fleets_destroyed = []

        emp1 = MagicMock(); emp1.id = 0; emp1.remove_fleet = MagicMock()
        emp2 = MagicMock(); emp2.id = 1; emp2.remove_fleet = MagicMock()
        f1 = MagicMock(spec=Fleet); f1.id = 10; f1.owner_id = 0
        f1.location = HexCoord(0, 0); f1.ships = [MagicMock()]
        f2 = MagicMock(spec=Fleet); f2.id = 20; f2.owner_id = 1
        f2.location = HexCoord(0, 0); f2.ships = [MagicMock()]

        engine._resolve_combat_at_hex([(emp1, f1), (emp2, f2)])

        assert len(calls) == 1
        _, kw = calls[0]
        assert sorted(kw["participating_fleet_ids"]) == [10, 20]
        assert sorted(kw["surviving_fleet_ids"]) == [10, 20]
        assert kw["destroyed_fleet_ids"] == []

    def test_combat_event_includes_empire_id(self):
        """The event's `empire_id` carries the lowest participating
        empire id — the strategy layer no longer designates a 'winning'
        empire (BUG-126)."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        mock_resolver = MagicMock()
        mock_result = MagicMock()
        mock_result.winner = None
        mock_result.team_survivors = {0: [MagicMock()], 1: [MagicMock()]}
        mock_resolver.resolve_battle.return_value = mock_result

        calls, fake, bus = _capture_log_event_calls()
        engine = ConflictResolutionEngine(battle_resolver=mock_resolver, event_bus=bus)
        engine._empires = []
        engine._combats_resolved = 0
        engine._fleets_destroyed = []

        emp1 = MagicMock(); emp1.id = 5; emp1.remove_fleet = MagicMock()
        emp2 = MagicMock(); emp2.id = 8; emp2.remove_fleet = MagicMock()
        f1 = MagicMock(spec=Fleet); f1.id = 1; f1.owner_id = 5
        f1.location = HexCoord(0, 0); f1.ships = [MagicMock()]
        f2 = MagicMock(spec=Fleet); f2.id = 2; f2.owner_id = 8
        f2.location = HexCoord(0, 0); f2.ships = [MagicMock()]

        engine._resolve_combat_at_hex([(emp1, f1), (emp2, f2)])

        _, kw = calls[0]
        assert kw["empire_id"] == 5  # Lowest participating empire id


# ===========================================================================
# PROJ-215: Event Location Enrichment (system_name, local_hex)
# ===========================================================================


class TestProductionEventLocationEnrichment:
    """Production events include system_name and local_hex fields (PROJ-215)."""

    def test_spawn_ship_event_includes_system_name(self, fresh_registries):
        """ship_built event includes system_name from parent system."""
        from game.strategy.engine.production_engine import ProductionEngine
        from game.core.hex_math import HexCoord

        calls, fake, bus = _capture_log_event_calls()
        engine = ProductionEngine(registries=fresh_registries, event_bus=bus)
        empire = _make_mock_empire()
        planet = _make_mock_planet()
        planet.location = HexCoord(2, 3)
        galaxy = _make_mock_galaxy()

        # Mock system with name
        mock_system = MagicMock()
        mock_system.name = "Sol"
        mock_system.global_location = HexCoord(100, 200)
        galaxy.get_system_of_planet.return_value = mock_system


        # PROJ-323 Task 2.16: flattened triple-nested with-patch via patch.multiple
        from unittest.mock import DEFAULT
        with patch.multiple(
            'game.strategy.engine.production_spawner',
            ShipInstance=DEFAULT, Fleet=DEFAULT,
        ) as mocks:

            mock_ship = MagicMock()
            mocks['ShipInstance'].create.return_value = mock_ship

            mock_fleet = MagicMock()
            mock_fleet.id = 1
            mocks['Fleet'].return_value = mock_fleet

            _wire_catalog_on(engine, empire.id, {"name": "Scout Ship"})
            engine._spawner._spawn_ship(planet, "scout", empire, galaxy)

        assert len(calls) == 1
        _, kw = calls[0]
        assert kw["system_name"] == "Sol"
        assert kw["local_hex"] == [2, 3]

    def test_spawn_ship_event_empty_system_name_when_no_system(self, fresh_registries):
        """ship_built event has empty system_name when no parent system found."""
        from game.strategy.engine.production_engine import ProductionEngine
        from game.core.hex_math import HexCoord

        calls, fake, bus = _capture_log_event_calls()
        engine = ProductionEngine(registries=fresh_registries, event_bus=bus)
        empire = _make_mock_empire()
        planet = _make_mock_planet()
        planet.location = HexCoord(2, 3)
        galaxy = _make_mock_galaxy()
        galaxy.get_system_of_planet.return_value = None


        # PROJ-323 Task 2.16: flattened triple-nested with-patch via patch.multiple
        from unittest.mock import DEFAULT
        with patch.multiple(
            'game.strategy.engine.production_spawner',
            ShipInstance=DEFAULT, Fleet=DEFAULT,
        ) as mocks:

            mock_ship = MagicMock()
            mocks['ShipInstance'].create.return_value = mock_ship

            mock_fleet = MagicMock()
            mock_fleet.id = 1
            mocks['Fleet'].return_value = mock_fleet

            _wire_catalog_on(engine, empire.id, {"name": "Scout Ship"})
            engine._spawner._spawn_ship(planet, "scout", empire, galaxy)

        _, kw = calls[0]
        assert kw["system_name"] == ""
        assert kw["local_hex"] is None

    def test_spawn_complex_event_includes_system_name_and_local_hex(self, fresh_registries):
        """complex_built event includes system_name and local_hex."""
        from game.strategy.engine.production_engine import ProductionEngine
        from game.core.hex_math import HexCoord

        calls, fake, bus = _capture_log_event_calls()
        engine = ProductionEngine(registries=fresh_registries, event_bus=bus)
        empire = _make_mock_empire()
        planet = _make_mock_planet()
        planet.location = HexCoord(1, -2)

        # Mock galaxy and system
        mock_system = MagicMock()
        mock_system.name = "Alpha Centauri"
        mock_system.global_location = HexCoord(50, 50)
        galaxy = _make_mock_galaxy()
        galaxy.get_system_of_planet.return_value = mock_system


        _wire_catalog_on(engine, empire.id, {"name": "Scout Ship"})
        engine._spawner._create_and_place_facility(planet, "factory", empire, galaxy=galaxy)

        _, kw = calls[0]
        assert kw["system_name"] == "Alpha Centauri"
        assert kw["local_hex"] == [1, -2]

    def test_spawn_fleet_ship_event_has_empty_system_name(self, fresh_registries):
        """Fleet production (deep space) has empty system_name and local_hex=None."""
        from game.strategy.engine.production_engine import ProductionEngine
        from game.strategy.data.fleet import Fleet

        calls, fake, bus = _capture_log_event_calls()
        engine = ProductionEngine(registries=fresh_registries, event_bus=bus)
        empire = _make_mock_empire()
        fleet = MagicMock(spec=Fleet)
        fleet.id = 7
        fleet.location = MagicMock(q=5, r=-3)


        if True:

            with patch('game.strategy.engine.production_spawner.ShipInstance') as mock_si:
                mock_ship = MagicMock()
                mock_si.create.return_value = mock_ship

                _wire_catalog_on(engine, empire.id, {"name": "Scout Ship"})
                engine._spawner._spawn_fleet_ship(fleet, "fighter_design", empire)

        _, kw = calls[0]
        assert kw["system_name"] == ""
        assert kw["local_hex"] is None


class TestCombatEventLocationEnrichment:
    """Combat events include system_name field (PROJ-215)."""

    def test_combat_event_includes_system_name(self):
        """combat_resolved event includes system_name from fleet location."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        mock_resolver = MagicMock()
        mock_result = MagicMock()
        mock_result.winner = 0
        mock_result.team_survivors = {0: [MagicMock()], 1: []}
        mock_resolver.resolve_battle.return_value = mock_result

        mock_galaxy = _make_mock_galaxy()
        mock_system = MagicMock()
        mock_system.name = "Orion"
        mock_galaxy.get_system_at_location.return_value = mock_system

        calls, fake, bus = _capture_log_event_calls()
        engine = ConflictResolutionEngine(battle_resolver=mock_resolver, event_bus=bus)
        engine._galaxy = mock_galaxy
        engine._empires = []
        engine._combats_resolved = 0
        engine._fleets_destroyed = []

        emp1 = MagicMock(); emp1.id = 0; emp1.remove_fleet = MagicMock()
        emp2 = MagicMock(); emp2.id = 1; emp2.remove_fleet = MagicMock()
        f1 = MagicMock(spec=Fleet); f1.id = 1; f1.owner_id = 0
        f1.location = HexCoord(10, 20); f1.ships = [MagicMock()]
        f2 = MagicMock(spec=Fleet); f2.id = 2; f2.owner_id = 1
        f2.location = HexCoord(10, 20); f2.ships = [MagicMock()]

        engine._resolve_combat_at_hex([(emp1, f1), (emp2, f2)])

        _, kw = calls[0]
        assert kw["system_name"] == "Orion"

    def test_combat_event_empty_system_name_when_no_system(self):
        """combat_resolved event has empty system_name when not at a system."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        mock_resolver = MagicMock()
        mock_result = MagicMock()
        mock_result.winner = 0
        mock_result.team_survivors = {0: [MagicMock()], 1: []}
        mock_resolver.resolve_battle.return_value = mock_result

        mock_galaxy = _make_mock_galaxy()
        mock_galaxy.get_system_at_location.return_value = None

        calls, fake, bus = _capture_log_event_calls()
        engine = ConflictResolutionEngine(battle_resolver=mock_resolver, event_bus=bus)
        engine._galaxy = mock_galaxy
        engine._empires = []
        engine._combats_resolved = 0
        engine._fleets_destroyed = []

        emp1 = MagicMock(); emp1.id = 0; emp1.remove_fleet = MagicMock()
        emp2 = MagicMock(); emp2.id = 1; emp2.remove_fleet = MagicMock()
        f1 = MagicMock(spec=Fleet); f1.id = 1; f1.owner_id = 0
        f1.location = HexCoord(10, 20); f1.ships = [MagicMock()]
        f2 = MagicMock(spec=Fleet); f2.id = 2; f2.owner_id = 1
        f2.location = HexCoord(10, 20); f2.ships = [MagicMock()]

        engine._resolve_combat_at_hex([(emp1, f1), (emp2, f2)])

        _, kw = calls[0]
        assert kw["system_name"] == ""


class TestColonizationEventLocationEnrichment:
    """Colonization events include system_name and local_hex (PROJ-215)."""

    def test_colonize_event_includes_system_name_and_local_hex(self):
        """colony_founded event includes system_name and local_hex."""
        from game.strategy.engine.order_processor import OrderProcessor
        from game.strategy.data.fleet import Fleet
        from game.strategy.data.order_types import Order, OrderType
        from game.core.hex_math import HexCoord
        from enum import Enum

        class MockPlanetType(Enum):
            CONTINENTAL = "CONTINENTAL"

        calls, fake, bus = _capture_log_event_calls()
        processor = OrderProcessor(event_bus=bus)
        empire = _make_mock_empire()
        galaxy = _make_mock_galaxy()

        # Mock system
        mock_system = MagicMock()
        mock_system.name = "Kepler"
        galaxy.get_system_of_planet.return_value = mock_system

        # Fleet with COLONIZE order
        fleet = MagicMock(spec=Fleet)
        fleet.id = 3
        fleet.owner_id = 0
        fleet.location = HexCoord(5, 5)

        mock_ship = MagicMock()
        mock_ship.name = "Colony Ship"
        mock_ship.carried_items = [{"vehicle_type": "drop_pod", "design_id": "test_pod", "name": "Test Pod", "design_data": {"layers": {"CORE": []}}, "mass": 500}]
        fleet.ships = [mock_ship]

        target_planet = _make_mock_planet(planet_id=10, name="New Earth")
        target_planet.owner_id = None
        target_planet.populations = []
        target_planet.planet_type = MockPlanetType.CONTINENTAL
        target_planet.location = HexCoord(3, -1)

        order = Order(OrderType.COLONIZE, target=target_planet)
        fleet.get_current_order.return_value = order
        fleet.pop_order = MagicMock()

        component_registry = {}

        with patch('game.strategy.validation.ColonizeValidator') as mock_val:
            mock_result = MagicMock()
            mock_result.is_valid = True
            mock_val.validate.return_value = mock_result
            mock_val.fleet_has_drop_pod.return_value = True
            mock_val.find_ship_with_drop_pod.return_value = (mock_ship, 0)

            with patch.object(processor._handler_registry.get(OrderType.COLONIZE), '_deploy_drop_pod'):
                processor.process_colonize(fleet, empire, galaxy, component_registry=component_registry)

        _, kw = calls[0]
        assert kw["system_name"] == "Kepler"
        assert kw["local_hex"] == [3, -1]

    def test_colonize_event_empty_system_name_when_no_system(self):
        """colony_founded event has empty system_name when no parent system."""
        from game.strategy.engine.order_processor import OrderProcessor
        from game.strategy.data.fleet import Fleet
        from game.strategy.data.order_types import Order, OrderType
        from game.core.hex_math import HexCoord
        from enum import Enum

        class MockPlanetType(Enum):
            CONTINENTAL = "CONTINENTAL"

        calls, fake, bus = _capture_log_event_calls()
        processor = OrderProcessor(event_bus=bus)
        empire = _make_mock_empire()
        galaxy = _make_mock_galaxy()
        galaxy.get_system_of_planet.return_value = None

        fleet = MagicMock(spec=Fleet)
        fleet.id = 3
        fleet.owner_id = 0
        fleet.location = HexCoord(5, 5)

        mock_ship = MagicMock()
        mock_ship.name = "Colony Ship"
        mock_ship.carried_items = [{"vehicle_type": "drop_pod", "design_id": "test_pod", "name": "Test Pod", "design_data": {"layers": {"CORE": []}}, "mass": 500}]
        fleet.ships = [mock_ship]

        target_planet = _make_mock_planet(planet_id=10, name="Lone Rock")
        target_planet.owner_id = None
        target_planet.populations = []
        target_planet.planet_type = MockPlanetType.CONTINENTAL
        target_planet.location = HexCoord(2, 0)

        order = Order(OrderType.COLONIZE, target=target_planet)
        fleet.get_current_order.return_value = order
        fleet.pop_order = MagicMock()

        component_registry = {}

        with patch('game.strategy.validation.ColonizeValidator') as mock_val:
            mock_result = MagicMock()
            mock_result.is_valid = True
            mock_val.validate.return_value = mock_result
            mock_val.fleet_has_drop_pod.return_value = True
            mock_val.find_ship_with_drop_pod.return_value = (mock_ship, 0)

            with patch.object(processor._handler_registry.get(OrderType.COLONIZE), '_deploy_drop_pod'):
                processor.process_colonize(fleet, empire, galaxy, component_registry=component_registry)

        _, kw = calls[0]
        assert kw["system_name"] == ""
        assert kw["local_hex"] is None
