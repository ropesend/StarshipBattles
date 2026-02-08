"""Tests for engine event emission (PROJ-77 Phase 3).

Verifies that ProductionEngine, FleetOrderProcessor, and ConflictResolutionEngine
emit the correct events via log_event() when significant actions occur.
"""

import pytest
from unittest.mock import MagicMock, patch, call

from game.strategy.events import EventType, EventCategory


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _capture_log_event_calls():
    """Return a list that accumulates (event_type, kwargs) tuples."""
    calls = []

    def _fake_log_event(event_type, **kwargs):
        calls.append((event_type, kwargs))

    return calls, _fake_log_event


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
    from game.strategy.data.hex_math import HexCoord

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
    from game.strategy.data.planet import PlanetaryFacility

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

    def test_spawn_ship_emits_ship_built_event(self):
        """_spawn_ship() calls log_event with ship_built type."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        empire = _make_mock_empire()
        planet = _make_mock_planet()
        galaxy = _make_mock_galaxy()

        calls, fake = _capture_log_event_calls()

        with patch('game.strategy.engine.production_engine.DesignLibrary') as mock_lib_cls:
            mock_lib = MagicMock()
            mock_lib.load_design_data.return_value = {"name": "Scout Ship"}
            mock_lib_cls.return_value = mock_lib

            with patch('game.strategy.engine.production_engine.ShipInstance') as mock_si:
                mock_ship = MagicMock()
                mock_si.create.return_value = mock_ship

                with patch('game.strategy.engine.production_engine.Fleet') as mock_fleet_cls:
                    mock_fleet = MagicMock()
                    mock_fleet.id = 1
                    mock_fleet_cls.return_value = mock_fleet

                    with patch('game.strategy.engine.production_engine.log_event', fake):
                        engine._spawn_ship(planet, "scout_design", empire, galaxy, save_path="/test")

        assert len(calls) == 1
        etype, kw = calls[0]
        assert etype == EventType.SHIP_BUILT
        assert kw["category"] == EventCategory.PRODUCTION
        assert kw["empire_id"] == 0
        assert "Scout Ship" in kw["message"]
        assert "Alpha Prime" in kw["message"]

    def test_spawn_ship_event_includes_details(self):
        """ship_built event includes design_id, planet_id, fleet_id."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        empire = _make_mock_empire()
        planet = _make_mock_planet(planet_id=42, name="Beta")
        galaxy = _make_mock_galaxy()

        calls, fake = _capture_log_event_calls()

        with patch('game.strategy.engine.production_engine.DesignLibrary') as mock_lib_cls:
            mock_lib = MagicMock()
            mock_lib.load_design_data.return_value = {"name": "Cruiser"}
            mock_lib_cls.return_value = mock_lib

            with patch('game.strategy.engine.production_engine.ShipInstance') as mock_si:
                mock_ship = MagicMock()
                mock_si.create.return_value = mock_ship

                with patch('game.strategy.engine.production_engine.Fleet') as mock_fleet_cls:
                    mock_fleet = MagicMock()
                    mock_fleet.id = 1
                    mock_fleet_cls.return_value = mock_fleet

                    with patch('game.strategy.engine.production_engine.log_event', fake):
                        engine._spawn_ship(planet, "cruiser_design", empire, galaxy, save_path="/test")

        assert len(calls) == 1
        _, kw = calls[0]
        assert kw["design_id"] == "cruiser_design"
        assert kw["planet_id"] == 42

    def test_spawn_ship_no_event_when_no_save_path(self):
        """No event emitted when save_path is None (ship not actually spawned)."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        empire = _make_mock_empire()
        planet = _make_mock_planet()
        galaxy = _make_mock_galaxy()

        calls, fake = _capture_log_event_calls()

        with patch('game.strategy.engine.production_engine.log_event', fake):
            engine._spawn_ship(planet, "scout", empire, galaxy, save_path=None)

        assert len(calls) == 0

    def test_spawn_ship_no_event_when_design_not_found(self):
        """No event emitted when design data can't be loaded."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        empire = _make_mock_empire()
        planet = _make_mock_planet()
        galaxy = _make_mock_galaxy()

        calls, fake = _capture_log_event_calls()

        with patch('game.strategy.engine.production_engine.DesignLibrary') as mock_lib_cls:
            mock_lib = MagicMock()
            mock_lib.load_design_data.return_value = None
            mock_lib_cls.return_value = mock_lib

            with patch('game.strategy.engine.production_engine.log_event', fake):
                engine._spawn_ship(planet, "bad_design", empire, galaxy, save_path="/test")

        assert len(calls) == 0


# ===========================================================================
# Production: Fleet Ship Built
# ===========================================================================


class TestFleetShipBuiltEvent:
    """ProductionEngine emits ship_built event for fleet yard production."""

    def test_spawn_fleet_ship_emits_ship_built_event(self):
        """_spawn_fleet_ship() calls log_event with ship_built type."""
        from game.strategy.engine.production_engine import ProductionEngine
        from game.strategy.data.fleet import Fleet

        engine = ProductionEngine()
        empire = _make_mock_empire()
        fleet = MagicMock(spec=Fleet)
        fleet.id = 7

        calls, fake = _capture_log_event_calls()

        with patch('game.strategy.engine.production_engine.DesignLibrary') as mock_lib_cls:
            mock_lib = MagicMock()
            mock_lib.load_design_data.return_value = {"name": "Fighter"}
            mock_lib_cls.return_value = mock_lib

            with patch('game.strategy.engine.production_engine.ShipInstance') as mock_si:
                mock_ship = MagicMock()
                mock_si.create.return_value = mock_ship

                with patch('game.strategy.engine.production_engine.log_event', fake):
                    engine._spawn_fleet_ship(fleet, "fighter_design", empire, save_path="/test")

        assert len(calls) == 1
        etype, kw = calls[0]
        assert etype == EventType.SHIP_BUILT
        assert kw["category"] == EventCategory.PRODUCTION
        assert kw["empire_id"] == 0
        assert kw["fleet_id"] == 7
        assert kw["is_fleet_production"] is True
        assert "Fighter" in kw["message"]

    def test_spawn_fleet_ship_no_event_when_no_save_path(self):
        """No event when save_path is None."""
        from game.strategy.engine.production_engine import ProductionEngine
        from game.strategy.data.fleet import Fleet

        engine = ProductionEngine()
        empire = _make_mock_empire()
        fleet = MagicMock(spec=Fleet)
        fleet.id = 7

        calls, fake = _capture_log_event_calls()

        with patch('game.strategy.engine.production_engine.log_event', fake):
            engine._spawn_fleet_ship(fleet, "fighter", empire, save_path=None)

        assert len(calls) == 0


# ===========================================================================
# Production: Complex Built
# ===========================================================================


class TestComplexBuiltEvent:
    """ProductionEngine emits complex_built event when a complex is spawned."""

    def test_spawn_complex_emits_complex_built_event(self):
        """_spawn_complex() calls log_event with complex_built type."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        empire = _make_mock_empire()
        planet = _make_mock_planet(name="Gamma Station")

        calls, fake = _capture_log_event_calls()

        with patch('game.strategy.engine.production_engine.DesignLibrary') as mock_lib_cls:
            mock_lib = MagicMock()
            mock_lib.load_design_data.return_value = {"name": "Mining Complex"}
            mock_lib_cls.return_value = mock_lib

            with patch('game.strategy.engine.production_engine.log_event', fake):
                engine._spawn_complex(planet, "mining_complex", empire, save_path="/test")

        assert len(calls) == 1
        etype, kw = calls[0]
        assert etype == EventType.COMPLEX_BUILT
        assert kw["category"] == EventCategory.PRODUCTION
        assert kw["empire_id"] == 0
        assert "Mining Complex" in kw["message"]
        assert "Gamma Station" in kw["message"]

    def test_spawn_complex_event_includes_details(self):
        """complex_built event includes design_id and planet_id."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        empire = _make_mock_empire()
        planet = _make_mock_planet(planet_id=99, name="Delta")

        calls, fake = _capture_log_event_calls()

        with patch('game.strategy.engine.production_engine.DesignLibrary') as mock_lib_cls:
            mock_lib = MagicMock()
            mock_lib.load_design_data.return_value = {"name": "Shipyard"}
            mock_lib_cls.return_value = mock_lib

            with patch('game.strategy.engine.production_engine.log_event', fake):
                engine._spawn_complex(planet, "shipyard_design", empire, save_path="/test")

        _, kw = calls[0]
        assert kw["design_id"] == "shipyard_design"
        assert kw["planet_id"] == 99

    def test_spawn_complex_emits_event_even_without_save_path(self):
        """Complex still gets created (empty design data) and event emitted."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        empire = _make_mock_empire()
        planet = _make_mock_planet()

        calls, fake = _capture_log_event_calls()

        with patch('game.strategy.engine.production_engine.log_event', fake):
            engine._spawn_complex(planet, "basic_factory", empire, save_path=None)

        # Complex is still created even without save_path, so event should fire
        assert len(calls) == 1
        etype, _ = calls[0]
        assert etype == EventType.COMPLEX_BUILT


# ===========================================================================
# Colony: Colony Founded
# ===========================================================================


class TestColonyFoundedEvent:
    """FleetOrderProcessor emits colony_founded event on colonization."""

    def _make_colonize_fleet(self):
        """Create a fleet with a COLONIZE order."""
        from game.strategy.data.fleet import Fleet, FleetOrder, OrderType

        fleet = MagicMock(spec=Fleet)
        fleet.id = 3
        fleet.owner_id = 0
        fleet.ships = [MagicMock()]

        target_planet = _make_mock_planet(planet_id=10, name="New Earth")
        target_planet.owner_id = None
        target_planet.populations = []

        order = FleetOrder(OrderType.COLONIZE, target=target_planet)
        fleet.get_current_order.return_value = order
        fleet.pop_order = MagicMock()
        fleet.get_fleet_cargo_current = MagicMock(return_value=0)
        fleet.unload_cargo_from_fleet = MagicMock(return_value=0)

        return fleet, target_planet

    def test_process_colonize_emits_colony_founded_event(self):
        """process_colonize() emits colony_founded on success."""
        from game.strategy.engine.fleet_order_processor import FleetOrderProcessor

        processor = FleetOrderProcessor()
        fleet, target_planet = self._make_colonize_fleet()
        empire = _make_mock_empire(name="Human Empire")
        galaxy = _make_mock_galaxy()

        calls, fake = _capture_log_event_calls()

        with patch('game.strategy.validation.ColonizeValidator') as mock_val:
            mock_result = MagicMock()
            mock_result.is_valid = True
            mock_val.validate.return_value = mock_result

            with patch('game.strategy.engine.fleet_order_processor.log_event', fake):
                result = processor.process_colonize(fleet, empire, galaxy)

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
        from game.strategy.engine.fleet_order_processor import FleetOrderProcessor

        processor = FleetOrderProcessor()
        fleet, target_planet = self._make_colonize_fleet()
        empire = _make_mock_empire()
        galaxy = _make_mock_galaxy()

        calls, fake = _capture_log_event_calls()

        with patch('game.strategy.validation.ColonizeValidator') as mock_val:
            mock_result = MagicMock()
            mock_result.is_valid = False
            mock_result.message = "Invalid"
            mock_val.validate.return_value = mock_result

            with patch('game.strategy.engine.fleet_order_processor.log_event', fake):
                result = processor.process_colonize(fleet, empire, galaxy)

        assert result.colonized is False
        assert len(calls) == 0

    def test_colonize_any_planet_emits_event_with_resolved_name(self):
        """Colonizing 'any planet' emits event with the resolved planet name."""
        from game.strategy.engine.fleet_order_processor import FleetOrderProcessor
        from game.strategy.data.fleet import Fleet, FleetOrder, OrderType

        processor = FleetOrderProcessor()
        empire = _make_mock_empire()
        galaxy = _make_mock_galaxy()

        # Fleet with COLONIZE target=None (any planet)
        fleet = MagicMock(spec=Fleet)
        fleet.id = 5
        fleet.owner_id = 0
        fleet.ships = [MagicMock()]
        fleet.get_fleet_cargo_current = MagicMock(return_value=0)
        fleet.unload_cargo_from_fleet = MagicMock(return_value=0)

        order = FleetOrder(OrderType.COLONIZE, target=None)
        fleet.get_current_order.return_value = order
        fleet.pop_order = MagicMock()
        from game.strategy.data.hex_math import HexCoord
        fleet.location = HexCoord(0, 0)

        # Galaxy returns a planet at fleet's location
        resolved_planet = _make_mock_planet(planet_id=20, name="Wild Planet")
        resolved_planet.owner_id = None
        resolved_planet.populations = []
        galaxy.get_planets_at_global_hex.return_value = [resolved_planet]

        calls, fake = _capture_log_event_calls()

        with patch('game.strategy.validation.ColonizeValidator') as mock_val:
            mock_result = MagicMock()
            mock_result.is_valid = True
            mock_val.validate.return_value = mock_result

            with patch('game.strategy.engine.fleet_order_processor.log_event', fake):
                result = processor.process_colonize(fleet, empire, galaxy)

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
        """_resolve_combat_simulated() emits combat_resolved event."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.data.fleet import Fleet
        from game.strategy.data.hex_math import HexCoord

        mock_resolver = MagicMock()
        mock_result = MagicMock()
        mock_result.winner = 0
        mock_result.team0_survivors = [MagicMock()]
        mock_result.team1_survivors = []
        mock_resolver.resolve_battle.return_value = mock_result

        engine = ConflictResolutionEngine(battle_resolver=mock_resolver)

        f1 = MagicMock(spec=Fleet)
        f1.id = 1
        f1.owner_id = 0
        f1.location = HexCoord(3, 4)
        f1.ships = [MagicMock()]
        f1.update_from_battle_results = MagicMock()

        f2 = MagicMock(spec=Fleet)
        f2.id = 2
        f2.owner_id = 1
        f2.location = HexCoord(3, 4)
        f2.ships = [MagicMock()]
        f2.update_from_battle_results = MagicMock()

        calls, fake = _capture_log_event_calls()

        with patch('game.strategy.engine.conflict_resolution_engine.log_event', fake):
            winner = engine._resolve_combat_simulated(f1, f2)

        assert winner == f1
        assert len(calls) == 1
        etype, kw = calls[0]
        assert etype == EventType.COMBAT_RESOLVED
        assert kw["category"] == EventCategory.COMBAT
        assert kw["winner_fleet_id"] == 1
        assert kw["loser_fleet_id"] == 2

    def test_combat_event_when_team1_wins(self):
        """combat_resolved event reflects correct winner when team 1 wins."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.data.fleet import Fleet
        from game.strategy.data.hex_math import HexCoord

        mock_resolver = MagicMock()
        mock_result = MagicMock()
        mock_result.winner = 1
        mock_result.team0_survivors = []
        mock_result.team1_survivors = [MagicMock()]
        mock_resolver.resolve_battle.return_value = mock_result

        engine = ConflictResolutionEngine(battle_resolver=mock_resolver)

        f1 = MagicMock(spec=Fleet)
        f1.id = 10
        f1.owner_id = 0
        f1.location = HexCoord(0, 0)
        f1.ships = [MagicMock()]
        f1.update_from_battle_results = MagicMock()

        f2 = MagicMock(spec=Fleet)
        f2.id = 20
        f2.owner_id = 1
        f2.location = HexCoord(0, 0)
        f2.ships = [MagicMock()]
        f2.update_from_battle_results = MagicMock()

        calls, fake = _capture_log_event_calls()

        with patch('game.strategy.engine.conflict_resolution_engine.log_event', fake):
            winner = engine._resolve_combat_simulated(f1, f2)

        assert winner == f2
        assert len(calls) == 1
        _, kw = calls[0]
        assert kw["winner_fleet_id"] == 20
        assert kw["loser_fleet_id"] == 10

    def test_rng_combat_emits_combat_resolved_event(self):
        """_resolve_combat() RNG fallback also emits combat_resolved event."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.data.fleet import Fleet
        from game.strategy.data.hex_math import HexCoord

        engine = ConflictResolutionEngine()

        # Empty fleets -> RNG fallback
        f1 = MagicMock(spec=Fleet)
        f1.id = 100
        f1.owner_id = 0
        f1.location = HexCoord(0, 0)
        f1.ships = []  # empty -> triggers RNG

        f2 = MagicMock(spec=Fleet)
        f2.id = 200
        f2.owner_id = 1
        f2.location = HexCoord(0, 0)
        f2.ships = []

        calls, fake = _capture_log_event_calls()

        with patch('game.strategy.engine.conflict_resolution_engine.log_event', fake):
            with patch('game.strategy.engine.conflict_resolution_engine.random') as mock_rng:
                mock_rng.random.return_value = 0.8  # f1 wins
                winner = engine._resolve_combat(f1, f2)

        assert winner == f1
        assert len(calls) == 1
        etype, kw = calls[0]
        assert etype == EventType.COMBAT_RESOLVED
        assert kw["category"] == EventCategory.COMBAT

    def test_combat_event_includes_empire_id(self):
        """combat_resolved event includes the winner's empire_id."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.data.fleet import Fleet
        from game.strategy.data.hex_math import HexCoord

        mock_resolver = MagicMock()
        mock_result = MagicMock()
        mock_result.winner = 0
        mock_result.team0_survivors = [MagicMock()]
        mock_result.team1_survivors = []
        mock_resolver.resolve_battle.return_value = mock_result

        engine = ConflictResolutionEngine(battle_resolver=mock_resolver)

        f1 = MagicMock(spec=Fleet)
        f1.id = 1
        f1.owner_id = 5
        f1.location = HexCoord(0, 0)
        f1.ships = [MagicMock()]
        f1.update_from_battle_results = MagicMock()

        f2 = MagicMock(spec=Fleet)
        f2.id = 2
        f2.owner_id = 8
        f2.location = HexCoord(0, 0)
        f2.ships = [MagicMock()]
        f2.update_from_battle_results = MagicMock()

        calls, fake = _capture_log_event_calls()

        with patch('game.strategy.engine.conflict_resolution_engine.log_event', fake):
            engine._resolve_combat_simulated(f1, f2)

        _, kw = calls[0]
        assert kw["empire_id"] == 5  # Winner's empire_id
