"""
Unit tests for game.strategy.facade.strategy_session_facade.

TCG-STR-002: Strategy Session Facade.
All tests use Mock GameSession - focus on facade logic, not session internals.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch

from game.core.hex_math import HexCoord
from game.core.validation import ValidationResult
from game.strategy.facade.strategy_session_facade import StrategySessionFacade


class TestFleetQueries:
    """Tests for fleet query methods."""

    def _make_mock_fleet(self, fleet_id: int, location: HexCoord = None, owner_id: int = 1):
        """Create a mock fleet that FleetInfo.from_fleet can handle."""
        fleet = Mock()
        fleet.id = fleet_id
        fleet.location = location or HexCoord(0, 0)
        fleet.name = f"Fleet {fleet_id}"
        fleet.ships = []
        fleet.owner_id = owner_id
        fleet.orders = []
        fleet.speed = 1.0
        fleet.can_use_warp = Mock(return_value=True)  # Method call
        fleet.path = []  # projected_path uses fleet.path
        fleet.is_building = False
        fleet.has_space_shipyard = False
        fleet.construction_queue = []  # Used for construction_queue_size
        fleet.get_fleet_cargo_capacity = Mock(return_value=0)
        fleet.get_fleet_cargo_current = Mock(return_value=0)
        # PROJ-208: capabilities.list_abilities() for FleetInfo.capabilities field
        fleet.capabilities = Mock()
        fleet.capabilities.list_abilities = Mock(return_value=[])
        return fleet

    def _make_mock_empire(self, empire_id: int, fleets: list = None, colonies: list = None):
        """Create a mock empire with fleets."""
        empire = Mock()
        empire.id = empire_id
        empire.fleets = fleets or []
        empire.colonies = colonies or []
        empire.name = f"Empire {empire_id}"
        empire.color = (255, 0, 0)
        empire.race_theme = Mock()
        empire.race_theme.theme_id = "test"
        empire.flag_id = 1
        return empire

    def _make_facade(self, empires: list = None):
        """Create facade with mock session."""
        session = Mock()
        session.empires = empires or []
        # Mock _get_fleet_by_id to search empires (like real implementation)
        def get_fleet_by_id(fleet_id):
            for empire in session.empires:
                for fleet in empire.fleets:
                    if fleet.id == fleet_id:
                        return fleet
            return None
        session._get_fleet_by_id = get_fleet_by_id
        return StrategySessionFacade(session)

    def test_get_fleet_found(self):
        """Returns FleetInfo DTO when fleet exists."""
        fleet = self._make_mock_fleet(42)
        empire = self._make_mock_empire(1, fleets=[fleet])
        facade = self._make_facade([empire])

        result = facade.get_fleet(42)

        assert result is not None
        assert result.fleet_id == 42

    def test_get_fleet_not_found(self):
        """Returns None when fleet not in any empire."""
        empire = self._make_mock_empire(1, fleets=[])
        facade = self._make_facade([empire])

        result = facade.get_fleet(999)

        assert result is None

    def test_get_fleets_at_hex_multiple(self):
        """Returns list of FleetInfo for fleets at hex."""
        target_hex = HexCoord(5, 5)
        fleet1 = self._make_mock_fleet(1, target_hex)
        fleet2 = self._make_mock_fleet(2, target_hex)
        fleet3 = self._make_mock_fleet(3, HexCoord(1, 1))  # Different location

        empire = self._make_mock_empire(1, fleets=[fleet1, fleet2, fleet3])
        facade = self._make_facade([empire])

        result = facade.get_fleets_at_hex(target_hex)

        assert len(result) == 2
        assert all(r.fleet_id in [1, 2] for r in result)

    def test_get_fleets_at_hex_empty(self):
        """Returns [] when no fleets at hex."""
        fleet = self._make_mock_fleet(1, HexCoord(0, 0))
        empire = self._make_mock_empire(1, fleets=[fleet])
        facade = self._make_facade([empire])

        result = facade.get_fleets_at_hex(HexCoord(100, 100))

        assert result == []

    def test_get_fleet_path_preview_found(self):
        """Delegates to session.preview_fleet_path."""
        fleet = self._make_mock_fleet(1)
        empire = self._make_mock_empire(1, fleets=[fleet])
        session = Mock()
        session.empires = [empire]
        session.preview_fleet_path = Mock(return_value=[HexCoord(0, 0), HexCoord(1, 0)])
        session._get_fleet_by_id = Mock(return_value=fleet)

        facade = StrategySessionFacade(session)
        target_hex = HexCoord(5, 5)

        result = facade.get_fleet_path_preview(1, target_hex)

        assert result == [HexCoord(0, 0), HexCoord(1, 0)]
        session.preview_fleet_path.assert_called_once_with(fleet, target_hex)

    def test_get_fleet_path_preview_not_found(self):
        """Returns None for unknown fleet."""
        facade = self._make_facade([])

        result = facade.get_fleet_path_preview(999, HexCoord(5, 5))

        assert result is None

    def test_get_fleet_path_projection_found(self):
        """Delegates to session.get_fleet_path_projection."""
        fleet = self._make_mock_fleet(1)
        empire = self._make_mock_empire(1, fleets=[fleet])
        session = Mock()
        session.empires = [empire]
        session.get_fleet_path_projection = Mock(return_value=[
            {"turn": 1, "hex": HexCoord(1, 0)},
            {"turn": 2, "hex": HexCoord(2, 0)},
        ])
        session._get_fleet_by_id = Mock(return_value=fleet)

        facade = StrategySessionFacade(session)
        result = facade.get_fleet_path_projection(1, max_turns=10)

        assert len(result) == 2
        session.get_fleet_path_projection.assert_called_once_with(fleet, 10)

    def test_get_fleet_path_projection_not_found(self):
        """Returns [] for unknown fleet."""
        facade = self._make_facade([])

        result = facade.get_fleet_path_projection(999)

        assert result == []


class TestSystemQueries:
    """Tests for system query methods."""

    def _make_mock_system(self, hex_coord: HexCoord, name: str = None):
        """Create a mock star system that SystemInfo.from_star_system can handle."""
        system = Mock()
        system.location = hex_coord
        system.name = name or f"System at {hex_coord}"
        system.stars = [Mock()]  # at least one star
        system.stars[0].star_type = Mock()
        system.stars[0].star_type.name = "MAIN_SEQUENCE"
        system.stars[0].temperature = 5778
        system.stars[0].radius = 1.0
        system.stars[0].mass = 1.0
        system.planets = []
        system.warp_points = []
        return system

    def test_get_all_systems(self):
        """Returns SystemInfo list from galaxy.systems."""
        sys1 = self._make_mock_system(HexCoord(0, 0))
        sys2 = self._make_mock_system(HexCoord(5, 5))

        session = Mock()
        session.empires = []
        session.galaxy = Mock()
        session.galaxy.systems = {HexCoord(0, 0): sys1, HexCoord(5, 5): sys2}

        facade = StrategySessionFacade(session)
        result = facade.get_all_systems()

        assert len(result) == 2

    def test_get_system_at_hex_found(self):
        """Returns SystemInfo for hex with system."""
        target_hex = HexCoord(3, 3)
        system = self._make_mock_system(target_hex, "Alpha Centauri")
        # SystemInfo.from_star_system needs system.planets to be iterable
        system.planets = []

        session = Mock()
        session.empires = []
        session.galaxy = Mock()
        session.galaxy.systems = {target_hex: system}
        session.galaxy.get_system_at_location.return_value = system

        facade = StrategySessionFacade(session)
        result = facade.get_system_at_hex(target_hex)

        assert result is not None
        assert result.name == "Alpha Centauri"

    def test_get_system_at_hex_not_found(self):
        """Returns None for empty hex."""
        session = Mock()
        session.empires = []
        session.galaxy = Mock()
        session.galaxy.systems = {}
        session.galaxy.get_system_at_location.return_value = None

        facade = StrategySessionFacade(session)

        result = facade.get_system_at_hex(HexCoord(100, 100))

        assert result is None


class TestPlanetQueries:
    """Tests for planet query methods."""

    def _make_mock_planet(self, planet_id: int, name: str = None):
        """Create a mock planet that PlanetInfo.from_planet can handle."""
        planet = Mock()
        planet.id = planet_id
        planet.name = name or f"Planet {planet_id}"
        planet.planet_type = Mock()
        planet.planet_type.name = "CONTINENTAL"
        planet.location = HexCoord(0, 1)
        planet.orbit_distance = 1
        planet.owner_id = None
        planet.has_space_shipyard = False
        planet.total_population = 0
        planet.max_population = 1000
        planet.populations = []  # Used for population_details
        planet.deposits = {}  # Required for PlanetInfo.from_planet
        return planet

    def _make_mock_system(self, hex_coord: HexCoord, planets: list = None):
        """Create a mock system with planets."""
        system = Mock()
        system.planets = planets or []
        system.location = hex_coord
        system.global_location = hex_coord  # Required for get_planets_at_hex
        system.name = "Test System"
        system.stars = []
        system.warp_points = []
        return system

    def test_get_planet_found(self):
        """Returns PlanetInfo DTO."""
        planet = self._make_mock_planet(42, "Earth")
        system = self._make_mock_system(HexCoord(0, 0), [planet])

        session = Mock()
        session.empires = []
        session.galaxy = Mock()
        session.galaxy.systems = {HexCoord(0, 0): system}

        facade = StrategySessionFacade(session)
        result = facade.get_planet(42)

        assert result is not None
        assert result.planet_id == 42
        assert result.name == "Earth"

    def test_get_planet_not_found(self):
        """Returns None for unknown planet_id."""
        session = Mock()
        session.empires = []
        session.galaxy = Mock()
        session.galaxy.systems = {}

        facade = StrategySessionFacade(session)

        result = facade.get_planet(999)

        assert result is None

    def test_get_planets_at_hex_found(self):
        """Returns PlanetInfo list for system at hex."""
        system_hex = HexCoord(3, 3)
        # Create planets at local (0, 0) so global = system_hex
        planet1 = self._make_mock_planet(1)
        planet1.location = HexCoord(0, 0)
        planet2 = self._make_mock_planet(2)
        planet2.location = HexCoord(0, 0)
        system = self._make_mock_system(system_hex, [planet1, planet2])

        session = Mock()
        session.empires = []
        session.galaxy = Mock()
        session.galaxy.systems = {system_hex: system}
        session.galaxy.get_system_at_location.return_value = system

        facade = StrategySessionFacade(session)
        # Query at system center where planets are located
        result = facade.get_planets_at_hex(system_hex)

        assert len(result) == 2

    def test_get_planets_at_hex_no_system(self):
        """Returns [] when no system at hex."""
        session = Mock()
        session.empires = []
        session.galaxy = Mock()
        session.galaxy.systems = {}
        session.galaxy.get_system_at_location.return_value = None

        facade = StrategySessionFacade(session)

        result = facade.get_planets_at_hex(HexCoord(100, 100))

        assert result == []


class TestEmpireQueries:
    """Tests for empire query methods."""

    def _make_mock_fleet(self, fleet_id: int):
        """Create a mock fleet for FleetSummary.from_fleet."""
        fleet = Mock()
        fleet.id = fleet_id
        fleet.name = f"Fleet {fleet_id}"
        fleet.location = HexCoord(0, 0)
        fleet.ships = []
        fleet.owner_id = 1
        fleet.orders = []
        return fleet

    def _make_mock_planet(self, planet_id: int):
        """Create a mock planet for colony that ColonySummary.from_planet can handle."""
        planet = Mock()
        planet.id = planet_id
        planet.name = f"Colony {planet_id}"
        planet.has_space_shipyard = False
        return planet

    def _make_mock_empire(self, empire_id: int, fleets=None, colonies=None, name=None):
        """Create a mock empire that EmpireInfo.from_empire can handle."""
        empire = Mock()
        empire.id = empire_id
        empire.name = name or f"Empire {empire_id}"
        empire.color = (255, 0, 0)
        empire.fleets = fleets or []
        empire.colonies = colonies or []
        empire.race_theme = Mock()
        empire.race_theme.theme_id = "test"
        empire.flag_id = 1
        return empire

    def test_get_all_empires(self):
        """Returns EmpireInfo list."""
        empire1 = self._make_mock_empire(1, name="Human Empire")
        empire2 = self._make_mock_empire(2, name="Alien Empire")

        session = Mock()
        session.empires = [empire1, empire2]

        facade = StrategySessionFacade(session)
        result = facade.get_all_empires()

        assert len(result) == 2

    def test_get_empire_found(self):
        """Returns EmpireInfo for valid ID."""
        empire = self._make_mock_empire(42, name="Test Empire")
        session = Mock()
        session.empires = [empire]

        facade = StrategySessionFacade(session)
        result = facade.get_empire(42)

        assert result is not None
        assert result.empire_id == 42
        assert result.name == "Test Empire"

    def test_get_empire_not_found(self):
        """Returns None for unknown ID."""
        session = Mock()
        session.empires = []

        facade = StrategySessionFacade(session)

        result = facade.get_empire(999)

        assert result is None

    def test_get_empire_colonies(self):
        """Returns ColonySummary list."""
        planet1 = self._make_mock_planet(1)
        planet2 = self._make_mock_planet(2)
        empire = self._make_mock_empire(1, colonies=[planet1, planet2])

        session = Mock()
        session.empires = [empire]

        facade = StrategySessionFacade(session)
        result = facade.get_empire_colonies(1)

        assert len(result) == 2

    def test_get_empire_colonies_not_found(self):
        """Returns [] for unknown empire."""
        session = Mock()
        session.empires = []

        facade = StrategySessionFacade(session)

        result = facade.get_empire_colonies(999)

        assert result == []

    def test_get_empire_fleets(self):
        """Returns FleetSummary list."""
        fleet1 = self._make_mock_fleet(1)
        fleet2 = self._make_mock_fleet(2)
        empire = self._make_mock_empire(1, fleets=[fleet1, fleet2])

        session = Mock()
        session.empires = [empire]

        facade = StrategySessionFacade(session)
        result = facade.get_empire_fleets(1)

        assert len(result) == 2

    def test_get_empire_fleets_not_found(self):
        """Returns [] for unknown empire."""
        session = Mock()
        session.empires = []

        facade = StrategySessionFacade(session)

        result = facade.get_empire_fleets(999)

        assert result == []


class TestGameStateQueries:
    """Tests for game state query methods."""

    def test_get_turn_number(self):
        """Returns session.turn_number."""
        session = Mock()
        session.turn_number = 42
        session.empires = []

        facade = StrategySessionFacade(session)

        result = facade.get_turn_number()

        assert result == 42

    def test_get_human_player_ids(self):
        """Returns list of human player empire IDs."""
        session = Mock()
        session.human_player_ids = {1, 3, 5}
        session.empires = []

        facade = StrategySessionFacade(session)

        result = facade.get_human_player_ids()

        assert set(result) == {1, 3, 5}


class TestValidationQueries:
    """Tests for validation query methods."""

    def _make_mock_fleet(self, fleet_id: int, location: HexCoord = None):
        """Create a mock fleet."""
        fleet = Mock()
        fleet.id = fleet_id
        fleet.location = location or HexCoord(0, 0)
        fleet.name = f"Fleet {fleet_id}"
        fleet.ships = []
        fleet.owner_id = 1
        return fleet

    def _make_mock_empire(self, empire_id: int, fleets: list = None):
        """Create a mock empire."""
        empire = Mock()
        empire.id = empire_id
        empire.fleets = fleets or []
        empire.colonies = []
        return empire

    def _make_mock_planet(self, planet_id: int):
        """Create a mock planet."""
        planet = Mock()
        planet.id = planet_id
        planet.name = f"Planet {planet_id}"
        return planet

    def _make_session_with_fleet_lookup(self, empires: list = None):
        """Create mock session with _get_fleet_by_id support."""
        session = Mock()
        session.empires = empires or []
        def get_fleet_by_id(fleet_id):
            for empire in session.empires:
                for fleet in empire.fleets:
                    if fleet.id == fleet_id:
                        return fleet
            return None
        session._get_fleet_by_id = get_fleet_by_id
        return session

    def test_can_colonize_fleet_not_found(self):
        """Returns invalid result when fleet not found."""
        session = self._make_session_with_fleet_lookup([])

        facade = StrategySessionFacade(session)

        result = facade.can_colonize(999, planet_id=1)

        assert not result.is_valid
        assert "Fleet not found" in result.errors[0]

    def test_can_colonize_planet_not_found(self):
        """Returns invalid result when planet not found."""
        fleet = self._make_mock_fleet(1)
        empire = self._make_mock_empire(1, fleets=[fleet])

        session = self._make_session_with_fleet_lookup([empire])
        session.galaxy = Mock()
        session.galaxy.systems = {}

        facade = StrategySessionFacade(session)

        result = facade.can_colonize(1, planet_id=999)

        assert not result.is_valid
        assert "Planet not found" in result.errors[0]

    def test_can_colonize_delegates_to_turn_engine(self):
        """Valid fleet/planet delegates to turn_engine."""
        fleet = self._make_mock_fleet(1)
        empire = self._make_mock_empire(1, fleets=[fleet])
        planet = self._make_mock_planet(42)

        system = Mock()
        system.planets = [planet]

        session = self._make_session_with_fleet_lookup([empire])
        session.galaxy = Mock()
        session.galaxy.systems = {HexCoord(0, 0): system}
        session.turn_engine = Mock()
        session.turn_engine.validate_colonize_order = Mock(
            return_value=ValidationResult.success()
        )

        facade = StrategySessionFacade(session)

        result = facade.can_colonize(1, planet_id=42)

        assert result.is_valid
        session.turn_engine.validate_colonize_order.assert_called_once()

    def test_can_move_to_fleet_not_found(self):
        """Returns invalid result when fleet not found."""
        session = self._make_session_with_fleet_lookup([])

        facade = StrategySessionFacade(session)

        result = facade.can_move_to(999, HexCoord(5, 5))

        assert not result.is_valid
        assert "Fleet not found" in result.errors[0]

    def test_can_move_to_no_path(self):
        """Returns invalid when no path exists."""
        fleet = self._make_mock_fleet(1)
        empire = self._make_mock_empire(1, fleets=[fleet])

        session = self._make_session_with_fleet_lookup([empire])
        session.preview_fleet_path = Mock(return_value=None)

        facade = StrategySessionFacade(session)

        result = facade.can_move_to(1, HexCoord(100, 100))

        assert not result.is_valid
        assert "No path" in result.errors[0]

    def test_can_move_to_valid_path(self):
        """Returns valid when path exists."""
        fleet = self._make_mock_fleet(1)
        empire = self._make_mock_empire(1, fleets=[fleet])

        session = self._make_session_with_fleet_lookup([empire])
        session.preview_fleet_path = Mock(return_value=[HexCoord(0, 0), HexCoord(1, 0)])

        facade = StrategySessionFacade(session)

        result = facade.can_move_to(1, HexCoord(1, 0))

        assert result.is_valid


class TestEventQueries:
    """Tests for event log query methods."""

    def _make_mock_event(self, turn: int, category: str = "COMBAT"):
        """Create a mock event."""
        event = Mock()
        event.turn = turn
        event.category = category
        event.to_dict = Mock(return_value={"turn": turn, "category": category})
        return event

    def test_get_turn_events_current_turn(self):
        """Delegates with current turn number when None."""
        event1 = self._make_mock_event(5)
        event2 = self._make_mock_event(5)

        session = Mock()
        session.empires = []
        session.turn_number = 5
        session.event_log = Mock()
        session.event_log.get_events_for_turn = Mock(return_value=[event1, event2])

        facade = StrategySessionFacade(session)

        result = facade.get_turn_events()  # No turn specified

        assert len(result) == 2
        session.event_log.get_events_for_turn.assert_called_once_with(5)

    def test_get_turn_events_specific_turn(self):
        """Delegates with specified turn."""
        event = self._make_mock_event(3)

        session = Mock()
        session.empires = []
        session.turn_number = 10
        session.event_log = Mock()
        session.event_log.get_events_for_turn = Mock(return_value=[event])

        facade = StrategySessionFacade(session)

        result = facade.get_turn_events(turn=3)

        assert len(result) == 1
        session.event_log.get_events_for_turn.assert_called_once_with(3)

    def test_get_all_events(self):
        """Returns all events as dicts."""
        event1 = self._make_mock_event(1)
        event2 = self._make_mock_event(2)
        event3 = self._make_mock_event(3)

        session = Mock()
        session.empires = []
        session.event_log = Mock()
        session.event_log.get_all_events = Mock(return_value=[event1, event2, event3])

        facade = StrategySessionFacade(session)

        result = facade.get_all_events()

        assert len(result) == 3
        assert all(isinstance(r, dict) for r in result)

    def test_get_events_by_category(self):
        """Filters by category."""
        combat_event = self._make_mock_event(1, "COMBAT")

        session = Mock()
        session.empires = []
        session.event_log = Mock()
        session.event_log.get_events_by_category = Mock(return_value=[combat_event])

        facade = StrategySessionFacade(session)

        result = facade.get_events_by_category("COMBAT")

        assert len(result) == 1
        session.event_log.get_events_by_category.assert_called_once_with("COMBAT")


class TestGameStateQueriesSavePath:
    """Tests for save path query methods (PROJ-208 Phase 4)."""

    def test_get_save_path_returns_session_save_path(self):
        """get_save_path returns session's save_path."""
        session = Mock()
        session.save_path = "/path/to/save.json"

        facade = StrategySessionFacade(session)

        result = facade.get_save_path()

        assert result == "/path/to/save.json"

    def test_get_save_path_returns_none_when_not_saved(self):
        """get_save_path returns None when no save path set."""
        session = Mock()
        session.save_path = None

        facade = StrategySessionFacade(session)

        result = facade.get_save_path()

        assert result is None



class TestStormQueries:
    """Tests for storm query methods (PROJ-215 Phase 5; rewritten for PROJ-300)."""

    def test_get_storm_names_at_hex_returns_storm_names(self):
        """PROJ-300: queries the galaxy zone index directly."""
        from game.core.hex_math import HexCoord
        from game.strategy.data.storm import Storm

        storm_a = Storm(
            name="Ion Storm Alpha",
            storm_type="ion_storm",
            location=HexCoord(0, 0),
            hex_offsets=frozenset({HexCoord(0, 0)}),
            abilities={"ShieldModifier": {"multiplier": 0.5, "scope": "sector"}},
        )
        storm_b = Storm(
            name="Plasma Storm",
            storm_type="plasma_storm",
            location=HexCoord(0, 0),
            hex_offsets=frozenset({HexCoord(0, 0)}),
            abilities={"ShieldModifier": {"multiplier": 0.7, "scope": "sector"}},
        )

        galaxy = Mock()
        galaxy.get_zones_at_global_hex = Mock(return_value=[storm_a, storm_b])
        session = Mock()
        session.galaxy = galaxy

        facade = StrategySessionFacade(session)
        result = facade.get_storm_names_at_hex(HexCoord(5, 3))
        assert result == ["Ion Storm Alpha", "Plasma Storm"]
        galaxy.get_zones_at_global_hex.assert_called_once_with(HexCoord(5, 3))

    def test_get_storm_names_at_hex_returns_empty_when_no_storms(self):
        from game.core.hex_math import HexCoord
        galaxy = Mock()
        galaxy.get_zones_at_global_hex = Mock(return_value=[])
        session = Mock()
        session.galaxy = galaxy

        facade = StrategySessionFacade(session)
        assert facade.get_storm_names_at_hex(HexCoord(0, 0)) == []


class TestRaceRegistryAccessor:
    """PROJ-287 Phase 2: facade.get_race_registry() lazy-init accessor."""

    def test_returns_iraceregistry(self):
        """Returns an object conforming to the IRaceRegistry protocol."""
        from game.core.protocols import IRaceRegistry

        facade = StrategySessionFacade(Mock())

        registry = facade.get_race_registry()

        assert isinstance(registry, IRaceRegistry)

    def test_two_calls_return_same_instance(self):
        """Subsequent calls return the cached registry (session-scoped)."""
        facade = StrategySessionFacade(Mock())

        first = facade.get_race_registry()
        second = facade.get_race_registry()

        assert first is second

    def test_two_facades_return_different_instances(self):
        """Each facade/session owns its own registry."""
        facade_a = StrategySessionFacade(Mock())
        facade_b = StrategySessionFacade(Mock())

        assert facade_a.get_race_registry() is not facade_b.get_race_registry()


class TestProcessTurnErrorConversion:
    """PROJ-408 C-02 / PROJ-381 Phase 3 (B-4):
    ``StrategySessionFacade.process_turn`` MUST convert a domain-engine
    ``EnginePhaseError`` into a facade-level ``TurnFailedError`` so the
    UI never has to import a sub-engine exception type.

    The conversion site lives at
    ``game/strategy/facade/strategy_session_facade.py:194-201``. Prior
    to PROJ-408 this conversion had no direct unit test — only an
    integration test at
    ``tests/integration/ui/test_strategy_turn_error_boundary.py``
    exercised the boundary, which conflated the UI catch with the
    facade conversion. These unit tests pin the conversion in
    isolation.
    """

    def _make_facade_raising(self, error):
        """Build a facade whose underlying session raises ``error`` from
        ``process_turn``."""
        session = Mock()
        session.process_turn = Mock(side_effect=error)
        facade = StrategySessionFacade(session)
        # Stub out the per-turn cache invalidation that the facade
        # would otherwise perform on a successful turn — it should not
        # be reached on the error path.
        facade._state.invalidate_all = Mock()
        return facade, session

    def test_engine_phase_error_is_re_raised_as_turn_failed_error(self):
        """An ``EnginePhaseError`` from the session is converted to a
        ``TurnFailedError`` at the facade boundary."""
        from game.core.exceptions import EnginePhaseError, TurnFailedError

        engine_err = EnginePhaseError(
            "harvesting failed",
            code="S102",
            context={
                "phase_name": "harvesting",
                "tick": 17,
                "turn_number": 5,
                "save_path": "/tmp/snap.json",
            },
        )
        facade, _ = self._make_facade_raising(engine_err)

        with pytest.raises(TurnFailedError) as exc_info:
            facade.process_turn()

        # Class identity check: the UI must never see EnginePhaseError.
        assert type(exc_info.value) is TurnFailedError

    def test_turn_failed_error_preserves_message_code_and_context(self):
        """The wrapper carries the original message, code, and context
        so UI dialogs (PROJ-395) can render turn_number, save_path, etc."""
        from game.core.exceptions import EnginePhaseError, TurnFailedError

        ctx = {
            "phase_name": "production",
            "tick": 42,
            "turn_number": 9,
            "save_path": "C:/saves/pre_turn_9.json",
            "original_type": "FormulaException",
        }
        engine_err = EnginePhaseError("production failed", code="S103", context=ctx)
        facade, _ = self._make_facade_raising(engine_err)

        with pytest.raises(TurnFailedError) as exc_info:
            facade.process_turn()

        wrapped: TurnFailedError = exc_info.value
        assert str(wrapped) == "production failed"
        assert wrapped.code == "S103"
        # Context is copied (defensive dict()) so it should equal but
        # not necessarily be the same object.
        assert wrapped.context == ctx
        # PROJ-395 convenience properties read from context.
        assert wrapped.phase_name == "production"
        assert wrapped.tick == 42
        assert wrapped.turn_number == 9
        assert wrapped.save_path == "C:/saves/pre_turn_9.json"

    def test_turn_failed_error_chains_from_engine_phase_error(self):
        """The wrapped error is preserved on ``__cause__`` so debug
        tooling (and tests) can recover the original engine exception."""
        from game.core.exceptions import EnginePhaseError, TurnFailedError

        engine_err = EnginePhaseError(
            "movement failed", code="S101", context={"phase_name": "movement"}
        )
        facade, _ = self._make_facade_raising(engine_err)

        with pytest.raises(TurnFailedError) as exc_info:
            facade.process_turn()

        assert exc_info.value.__cause__ is engine_err

    def test_invalidate_all_is_not_called_on_engine_phase_error(self):
        """When the session raises, the facade should NOT proceed to
        invalidate per-turn caches — the session has already rolled
        back and the caches still reflect the pre-turn state."""
        from game.core.exceptions import EnginePhaseError, TurnFailedError

        engine_err = EnginePhaseError("bang", context={})
        facade, _ = self._make_facade_raising(engine_err)

        with pytest.raises(TurnFailedError):
            facade.process_turn()

        facade._state.invalidate_all.assert_not_called()

    def test_non_engine_phase_error_propagates_unchanged(self):
        """Only ``EnginePhaseError`` is converted. A different exception
        type (e.g. a programmer-error ``RuntimeError``) must propagate
        unchanged so it surfaces as a real bug, not a recoverable turn
        failure."""
        original = RuntimeError("unexpected programmer error")
        facade, _ = self._make_facade_raising(original)

        with pytest.raises(RuntimeError) as exc_info:
            facade.process_turn()

        assert exc_info.value is original
