"""
Tests for BattleService.

This service provides an abstraction layer between UI and BattleEngine,
handling battle creation, ship management, and battle state queries.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from game.simulation.services.battle_service import BattleService, BattleServiceResult
from game.simulation.entities.ship import Ship
from game.simulation.systems.battle_end_conditions import BattleEndMode


@pytest.fixture
def service():
    """Create a BattleService instance."""
    return BattleService()


@pytest.fixture
def team0_ship(fresh_registries):
    """Create a ship for team 0."""
    ship = Ship(
        name="Team0 Ship",
        x=100,
        y=100,
        color=(255, 0, 0),
        team_id=0,
        ship_class="Escort",
        registries=fresh_registries
    )
    ship.recalculate_stats()
    return ship


@pytest.fixture
def team1_ship(fresh_registries):
    """Create a ship for team 1."""
    ship = Ship(
        name="Team1 Ship",
        x=500,
        y=100,
        color=(0, 0, 255),
        team_id=1,
        ship_class="Escort",
        registries=fresh_registries
    )
    ship.recalculate_stats()
    return ship


@pytest.fixture
def started_battle(service, team0_ship, team1_ship):
    """Create a battle service with a started battle."""
    service.create_battle()
    service.add_ship(team0_ship, team_id=0)
    service.add_ship(team1_ship, team_id=1)
    service.start_battle()
    return service


# =============================================================================
# BattleServiceResult Tests
# =============================================================================


class TestBattleServiceResult:
    """Tests for BattleServiceResult dataclass."""

    def test_result_success(self):
        """BattleServiceResult stores success state correctly."""
        result = BattleServiceResult(success=True)

        assert result.success is True
        assert result.errors == []
        assert result.warnings == []

    def test_result_with_errors(self):
        """BattleServiceResult stores errors correctly."""
        result = BattleServiceResult(
            success=False,
            errors=["Error 1", "Error 2"]
        )

        assert result.success is False
        assert len(result.errors) == 2
        assert "Error 1" in result.errors
        assert "Error 2" in result.errors

    def test_result_with_warnings(self):
        """BattleServiceResult stores warnings correctly."""
        result = BattleServiceResult(
            success=True,
            warnings=["Warning 1"]
        )

        assert result.success is True
        assert len(result.warnings) == 1
        assert "Warning 1" in result.warnings

    def test_result_with_engine(self):
        """BattleServiceResult stores engine reference correctly."""
        mock_engine = Mock()
        result = BattleServiceResult(success=True, engine=mock_engine)

        assert result.engine is mock_engine

    def test_result_defaults(self):
        """BattleServiceResult has correct defaults."""
        result = BattleServiceResult(success=True)

        assert result.errors == []
        assert result.warnings == []
        assert result.engine is None


# =============================================================================
# BattleService.create_battle() Tests
# =============================================================================


class TestBattleServiceCreateBattle:
    """Tests for BattleService.create_battle()."""

    def test_create_battle_returns_engine(self, service):
        """create_battle() returns a result with BattleEngine."""
        result = service.create_battle()

        assert result.success is True
        assert result.engine is not None

    def test_create_battle_with_seed(self, service):
        """create_battle() accepts random seed for reproducibility."""
        result = service.create_battle(seed=42)

        assert result.success is True
        assert result.engine is not None
        # Verify seed is stored
        assert service._seed == 42

    def test_create_battle_with_logging_enabled(self, service):
        """create_battle() accepts enable_logging flag."""
        result = service.create_battle(enable_logging=True)

        assert result.success is True
        assert result.engine is not None
        # Logger should be enabled
        assert result.engine.logger.enabled is True

    def test_create_battle_with_logging_disabled(self, service):
        """create_battle() with logging disabled creates disabled logger."""
        result = service.create_battle(enable_logging=False)

        assert result.success is True
        # Logger should be disabled by default
        assert result.engine.logger.enabled is False

    def test_create_battle_initializes_state(self, service):
        """create_battle() initializes service state correctly."""
        service.create_battle()

        assert service._engine is not None
        assert service._team0_ships == []
        assert service._team1_ships == []
        assert service._is_started is False

    def test_create_battle_resets_previous_state(self, service, team0_ship, team1_ship):
        """create_battle() resets state from previous battle."""
        # Set up a battle with ships
        service.create_battle()
        service.add_ship(team0_ship, team_id=0)
        service.add_ship(team1_ship, team_id=1)
        service.start_battle()

        # Create new battle
        result = service.create_battle()

        assert result.success is True
        assert service._team0_ships == []
        assert service._team1_ships == []
        assert service._is_started is False


# =============================================================================
# BattleService.add_ship() Tests
# =============================================================================


class TestBattleServiceAddShip:
    """Tests for BattleService.add_ship()."""

    def test_add_ship_to_team0(self, service, team0_ship):
        """add_ship() adds ship to team 0."""
        service.create_battle()

        result = service.add_ship(team0_ship, team_id=0)

        assert result.success is True
        state = service.get_battle_state()
        assert team0_ship in state['team_0_ships']

    def test_add_ship_to_team1(self, service, team1_ship):
        """add_ship() adds ship to team 1."""
        service.create_battle()

        result = service.add_ship(team1_ship, team_id=1)

        assert result.success is True
        state = service.get_battle_state()
        assert team1_ship in state['team_1_ships']

    def test_add_ship_updates_team_id(self, service, team0_ship):
        """add_ship() sets ship's team_id to match specified team."""
        service.create_battle()
        team0_ship.team_id = 99  # Different team

        service.add_ship(team0_ship, team_id=1)

        assert team0_ship.team_id == 1

    def test_add_ship_no_active_battle(self, service, team0_ship):
        """add_ship() fails gracefully when no battle exists."""
        result = service.add_ship(team0_ship, team_id=0)

        assert result.success is False
        assert "No active battle" in result.errors[0]

    def test_add_ship_after_battle_started(self, started_battle, fresh_registries):
        """add_ship() fails after battle has started."""
        new_ship = Ship(
            name="Late Ship",
            x=200,
            y=200,
            color=(255, 255, 0),
            team_id=0,
            ship_class="Escort",
            registries=fresh_registries
        )

        result = started_battle.add_ship(new_ship, team_id=0)

        assert result.success is False
        assert "Cannot add ships after battle has started" in result.errors[0]

    def test_add_multiple_ships_to_same_team(self, service, team0_ship, fresh_registries):
        """add_ship() can add multiple ships to same team."""
        service.create_battle()
        second_ship = Ship(
            name="Second Ship",
            x=150,
            y=150,
            color=(255, 128, 0),
            team_id=0,
            ship_class="Escort",
            registries=fresh_registries
        )

        service.add_ship(team0_ship, team_id=0)
        result = service.add_ship(second_ship, team_id=0)

        assert result.success is True
        state = service.get_battle_state()
        assert len(state['team_0_ships']) == 2


# =============================================================================
# BattleService.remove_ship() Tests
# =============================================================================


class TestBattleServiceRemoveShip:
    """Tests for BattleService.remove_ship()."""

    def test_remove_ship_from_team0(self, service, team0_ship):
        """remove_ship() removes ship from team 0."""
        service.create_battle()
        service.add_ship(team0_ship, team_id=0)

        result = service.remove_ship(team0_ship)

        assert result.success is True
        state = service.get_battle_state()
        assert team0_ship not in state['team_0_ships']

    def test_remove_ship_from_team1(self, service, team1_ship):
        """remove_ship() removes ship from team 1."""
        service.create_battle()
        service.add_ship(team1_ship, team_id=1)

        result = service.remove_ship(team1_ship)

        assert result.success is True
        state = service.get_battle_state()
        assert team1_ship not in state['team_1_ships']

    def test_remove_ship_no_active_battle(self, service, team0_ship):
        """remove_ship() fails when no battle exists."""
        result = service.remove_ship(team0_ship)

        assert result.success is False
        assert "No active battle" in result.errors[0]

    def test_remove_ship_after_battle_started(self, started_battle, team0_ship):
        """remove_ship() fails after battle has started."""
        result = started_battle.remove_ship(team0_ship)

        assert result.success is False
        assert "Cannot remove ships after battle has started" in result.errors[0]

    def test_remove_ship_not_found(self, service, team0_ship, team1_ship):
        """remove_ship() fails when ship not in battle."""
        service.create_battle()
        service.add_ship(team0_ship, team_id=0)

        result = service.remove_ship(team1_ship)  # Not added

        assert result.success is False
        assert "not found in battle" in result.errors[0]


# =============================================================================
# BattleService.start_battle() Tests
# =============================================================================


class TestBattleServiceStartBattle:
    """Tests for BattleService.start_battle()."""

    def test_start_battle_success(self, service, team0_ship, team1_ship):
        """start_battle() begins the simulation."""
        service.create_battle()
        service.add_ship(team0_ship, team_id=0)
        service.add_ship(team1_ship, team_id=1)

        result = service.start_battle()

        assert result.success is True
        state = service.get_battle_state()
        assert state['is_started'] is True

    def test_start_battle_with_end_mode(self, service, team0_ship, team1_ship):
        """start_battle() accepts end condition mode."""
        service.create_battle()
        service.add_ship(team0_ship, team_id=0)
        service.add_ship(team1_ship, team_id=1)

        result = service.start_battle(end_mode=BattleEndMode.TIME_BASED, max_ticks=1000)

        assert result.success is True

    def test_start_battle_with_max_ticks(self, service, team0_ship, team1_ship):
        """start_battle() accepts max_ticks for time-based battles."""
        service.create_battle()
        service.add_ship(team0_ship, team_id=0)
        service.add_ship(team1_ship, team_id=1)

        result = service.start_battle(max_ticks=500)

        assert result.success is True

    def test_start_battle_no_ships_fails(self, service):
        """start_battle() fails when no ships added."""
        service.create_battle()

        result = service.start_battle()

        assert result.success is False
        assert "Cannot start battle with no ships" in result.errors[0]

    def test_start_battle_no_active_battle(self, service):
        """start_battle() fails when no battle created."""
        result = service.start_battle()

        assert result.success is False
        assert "No active battle" in result.errors[0]

    def test_start_battle_already_started(self, started_battle):
        """start_battle() fails if already started."""
        result = started_battle.start_battle()

        assert result.success is False
        assert "Battle already started" in result.errors[0]

    def test_start_battle_with_only_team0_ships(self, service, team0_ship):
        """start_battle() succeeds with ships on only one team."""
        service.create_battle()
        service.add_ship(team0_ship, team_id=0)

        result = service.start_battle()

        assert result.success is True

    def test_start_battle_with_only_team1_ships(self, service, team1_ship):
        """start_battle() succeeds with ships on only one team."""
        service.create_battle()
        service.add_ship(team1_ship, team_id=1)

        result = service.start_battle()

        assert result.success is True


# =============================================================================
# BattleService.update() Tests
# =============================================================================


class TestBattleServiceUpdate:
    """Tests for BattleService.update()."""

    def test_update_advances_tick(self, started_battle):
        """update() advances the battle simulation by one tick."""
        initial_tick = started_battle.get_battle_state()['tick_count']

        started_battle.update()

        new_tick = started_battle.get_battle_state()['tick_count']
        assert new_tick == initial_tick + 1

    def test_update_multiple_ticks(self, started_battle):
        """update() can be called multiple times."""
        for _ in range(10):
            started_battle.update()

        state = started_battle.get_battle_state()
        assert state['tick_count'] == 10

    def test_update_no_active_battle(self, service):
        """update() fails when no battle exists."""
        result = service.update()

        assert result.success is False
        assert "No active battle" in result.errors[0]

    def test_update_battle_not_started(self, service, team0_ship, team1_ship):
        """update() fails when battle not started."""
        service.create_battle()
        service.add_ship(team0_ship, team_id=0)
        service.add_ship(team1_ship, team_id=1)

        result = service.update()

        assert result.success is False
        assert "Battle not started" in result.errors[0]

    def test_update_returns_engine(self, started_battle):
        """update() returns result with engine reference."""
        result = started_battle.update()

        assert result.success is True
        assert result.engine is not None


# =============================================================================
# BattleService.run_ticks() Tests
# =============================================================================


class TestBattleServiceRunTicks:
    """Tests for BattleService.run_ticks()."""

    def test_run_ticks_advances_multiple_ticks(self, started_battle):
        """run_ticks() advances by specified count."""
        started_battle.run_ticks(5)

        state = started_battle.get_battle_state()
        assert state['tick_count'] == 5

    def test_run_ticks_no_active_battle(self, service):
        """run_ticks() fails when no battle exists."""
        result = service.run_ticks(10)

        assert result.success is False
        assert "No active battle" in result.errors[0]

    def test_run_ticks_battle_not_started(self, service, team0_ship, team1_ship):
        """run_ticks() fails when battle not started."""
        service.create_battle()
        service.add_ship(team0_ship, team_id=0)
        service.add_ship(team1_ship, team_id=1)

        result = service.run_ticks(10)

        assert result.success is False
        assert "Battle not started" in result.errors[0]

    def test_run_ticks_returns_engine(self, started_battle):
        """run_ticks() returns result with engine reference."""
        result = started_battle.run_ticks(1)

        assert result.success is True
        assert result.engine is not None

    def test_run_ticks_zero_ticks(self, started_battle):
        """run_ticks() with zero does nothing."""
        initial_tick = started_battle.get_battle_state()['tick_count']

        started_battle.run_ticks(0)

        state = started_battle.get_battle_state()
        assert state['tick_count'] == initial_tick


# =============================================================================
# BattleService.is_battle_over() Tests
# =============================================================================


class TestBattleServiceIsBattleOver:
    """Tests for BattleService.is_battle_over()."""

    def test_is_battle_over_initial(self, started_battle):
        """is_battle_over() returns False for new battle."""
        assert started_battle.is_battle_over() is False

    def test_is_battle_over_no_engine(self, service):
        """is_battle_over() returns True when no engine exists."""
        assert service.is_battle_over() is True

    def test_is_battle_over_when_team_eliminated(self, service, team0_ship, team1_ship):
        """is_battle_over() returns True when one team is eliminated."""
        service.create_battle()
        service.add_ship(team0_ship, team_id=0)
        service.add_ship(team1_ship, team_id=1)
        service.start_battle()

        # Eliminate team 1 ship by setting is_alive to False
        team1_ship.is_alive = False

        assert service.is_battle_over() is True


# =============================================================================
# BattleService.get_winner() Tests
# =============================================================================


class TestBattleServiceGetWinner:
    """Tests for BattleService.get_winner()."""

    def test_get_winner_no_engine(self, service):
        """get_winner() returns None when no engine exists."""
        assert service.get_winner() is None

    def test_get_winner_team0_wins(self, service, team0_ship, team1_ship):
        """get_winner() returns 0 when team 0 wins."""
        service.create_battle()
        service.add_ship(team0_ship, team_id=0)
        service.add_ship(team1_ship, team_id=1)
        service.start_battle()

        # Eliminate team 1 by setting is_alive to False
        team1_ship.is_alive = False

        assert service.get_winner() == 0

    def test_get_winner_team1_wins(self, service, team0_ship, team1_ship):
        """get_winner() returns 1 when team 1 wins."""
        service.create_battle()
        service.add_ship(team0_ship, team_id=0)
        service.add_ship(team1_ship, team_id=1)
        service.start_battle()

        # Eliminate team 0 by setting is_alive to False
        team0_ship.is_alive = False

        assert service.get_winner() == 1

    def test_get_winner_draw(self, started_battle):
        """get_winner() returns -1 for draw (both teams alive)."""
        # Both ships still alive
        assert started_battle.get_winner() == -1


# =============================================================================
# BattleService.get_battle_state() Tests
# =============================================================================


class TestBattleServiceGetBattleState:
    """Tests for BattleService.get_battle_state()."""

    def test_get_battle_state_structure(self, started_battle):
        """get_battle_state() returns expected structure."""
        state = started_battle.get_battle_state()

        assert 'is_started' in state
        assert 'is_over' in state
        assert 'tick_count' in state
        assert 'team_0_ships' in state
        assert 'team_1_ships' in state
        assert 'winner' in state
        assert 'projectile_count' in state
        assert 'recent_beams' in state

    def test_get_battle_state_no_battle(self, service):
        """get_battle_state() returns empty state when no battle."""
        state = service.get_battle_state()

        assert state['is_started'] is False
        assert state['is_over'] is False
        assert state['tick_count'] == 0
        assert state['team_0_ships'] == []
        assert state['team_1_ships'] == []
        assert state['winner'] is None
        assert state['projectile_count'] == 0

    def test_get_battle_state_before_start(self, service, team0_ship, team1_ship):
        """get_battle_state() returns ships before battle start."""
        service.create_battle()
        service.add_ship(team0_ship, team_id=0)
        service.add_ship(team1_ship, team_id=1)

        state = service.get_battle_state()

        assert state['is_started'] is False
        assert team0_ship in state['team_0_ships']
        assert team1_ship in state['team_1_ships']

    def test_get_battle_state_after_start(self, started_battle):
        """get_battle_state() returns correct state after start."""
        state = started_battle.get_battle_state()

        assert state['is_started'] is True
        assert state['tick_count'] == 0
        assert len(state['team_0_ships']) == 1
        assert len(state['team_1_ships']) == 1


# =============================================================================
# BattleService.get_all_ships() Tests
# =============================================================================


class TestBattleServiceGetAllShips:
    """Tests for BattleService.get_all_ships()."""

    def test_get_all_ships_no_engine(self, service):
        """get_all_ships() returns empty list when no engine."""
        assert service.get_all_ships() == []

    def test_get_all_ships_before_start(self, service, team0_ship, team1_ship):
        """get_all_ships() returns added ships before battle start."""
        service.create_battle()
        service.add_ship(team0_ship, team_id=0)
        service.add_ship(team1_ship, team_id=1)

        ships = service.get_all_ships()

        assert len(ships) == 2
        assert team0_ship in ships
        assert team1_ship in ships

    def test_get_all_ships_after_start(self, started_battle):
        """get_all_ships() returns ships from engine after start."""
        ships = started_battle.get_all_ships()

        assert len(ships) == 2


# =============================================================================
# BattleService.get_alive_ships() Tests
# =============================================================================


class TestBattleServiceGetAliveShips:
    """Tests for BattleService.get_alive_ships()."""

    def test_get_alive_ships_no_engine(self, service):
        """get_alive_ships() returns empty list when no engine."""
        assert service.get_alive_ships() == []

    def test_get_alive_ships_all_alive(self, started_battle):
        """get_alive_ships() returns all ships when all alive."""
        ships = started_battle.get_alive_ships()

        assert len(ships) == 2

    def test_get_alive_ships_excludes_dead(self, started_battle):
        """get_alive_ships() excludes dead ships."""
        # Get the team0 ship from the battle state
        state = started_battle.get_battle_state()
        team0_ship = state['team_0_ships'][0]

        # Kill team0 ship by setting is_alive to False
        team0_ship.is_alive = False

        ships = started_battle.get_alive_ships()

        assert len(ships) == 1
        assert team0_ship not in ships


# =============================================================================
# BattleService.get_engine() Tests
# =============================================================================


class TestBattleServiceGetEngine:
    """Tests for BattleService.get_engine()."""

    def test_get_engine_no_battle(self, service):
        """get_engine() returns None when no battle."""
        assert service.get_engine() is None

    def test_get_engine_after_create(self, service):
        """get_engine() returns engine after creation."""
        service.create_battle()

        engine = service.get_engine()

        assert engine is not None

    def test_get_engine_after_start(self, started_battle):
        """get_engine() returns engine after start."""
        engine = started_battle.get_engine()

        assert engine is not None


# =============================================================================
# BattleService.reset() Tests
# =============================================================================


class TestBattleServiceReset:
    """Tests for BattleService.reset()."""

    def test_reset_clears_engine(self, started_battle):
        """reset() clears the engine."""
        started_battle.reset()

        assert started_battle._engine is None

    def test_reset_clears_ships(self, started_battle):
        """reset() clears ship lists."""
        started_battle.reset()

        assert started_battle._team0_ships == []
        assert started_battle._team1_ships == []

    def test_reset_clears_started_flag(self, started_battle):
        """reset() clears is_started flag."""
        started_battle.reset()

        assert started_battle._is_started is False

    def test_reset_clears_seed(self, service):
        """reset() clears seed."""
        service.create_battle(seed=42)
        assert service._seed == 42

        service.reset()

        assert service._seed is None

    def test_reset_no_battle(self, service):
        """reset() works when no battle exists."""
        # Should not raise
        service.reset()

        assert service._engine is None

    def test_reset_closes_logger(self, service):
        """reset() closes the battle logger."""
        service.create_battle(enable_logging=True)
        engine = service.get_engine()

        service.reset()

        # Logger file should be None after close
        assert engine.logger.file is None


# =============================================================================
# Integration / Edge Case Tests
# =============================================================================


class TestBattleServiceIntegration:
    """Integration and edge case tests for BattleService."""

    def test_full_battle_lifecycle(self, service, team0_ship, team1_ship):
        """Test complete battle lifecycle from creation to reset."""
        # Create
        result = service.create_battle(seed=12345)
        assert result.success is True

        # Add ships
        service.add_ship(team0_ship, team_id=0)
        service.add_ship(team1_ship, team_id=1)

        # Start
        result = service.start_battle()
        assert result.success is True

        # Run simulation
        for _ in range(5):
            if service.is_battle_over():
                break
            service.update()

        # Get state
        state = service.get_battle_state()
        assert state['tick_count'] == 5

        # Reset
        service.reset()
        assert service._engine is None

    def test_create_multiple_battles(self, service, team0_ship, team1_ship, fresh_registries):
        """Test creating multiple battles sequentially."""
        # First battle
        service.create_battle(seed=1)
        service.add_ship(team0_ship, team_id=0)
        service.start_battle()
        service.update()

        # Second battle (should reset first)
        second_ship = Ship(
            name="Second Team Ship",
            x=300,
            y=300,
            color=(128, 128, 128),
            team_id=0,
            ship_class="Escort",
            registries=fresh_registries
        )
        second_ship.recalculate_stats()

        result = service.create_battle(seed=2)
        assert result.success is True

        service.add_ship(second_ship, team_id=0)
        result = service.start_battle()
        assert result.success is True

        state = service.get_battle_state()
        assert state['tick_count'] == 0
        assert len(state['team_0_ships']) == 1

    def test_battle_state_consistency(self, service, team0_ship, team1_ship):
        """Test that battle state remains consistent through operations."""
        service.create_battle()
        service.add_ship(team0_ship, team_id=0)
        service.add_ship(team1_ship, team_id=1)

        # Before start
        state1 = service.get_battle_state()
        assert state1['is_started'] is False

        service.start_battle()

        # After start
        state2 = service.get_battle_state()
        assert state2['is_started'] is True

        service.update()

        # After update
        state3 = service.get_battle_state()
        assert state3['tick_count'] == 1


# =============================================================================
# Additional Edge Case Tests (PROJ-118 Phase 2)
# =============================================================================


class TestBattleServiceEdgeCases:
    """Additional edge case tests for BattleService."""

    def test_run_ticks_stops_at_battle_end(self, service, team0_ship, team1_ship):
        """run_ticks() stops early when battle ends mid-run."""
        service.create_battle()
        service.add_ship(team0_ship, team_id=0)
        service.add_ship(team1_ship, team_id=1)
        service.start_battle()

        # Kill team1 ship to end battle quickly
        team1_ship.is_alive = False

        # Try to run 1000 ticks, but battle should end immediately
        result = service.run_ticks(1000)

        assert result.success is True
        # Battle ended, so should not have run all 1000 ticks
        state = service.get_battle_state()
        assert state['tick_count'] < 1000

    def test_run_ticks_negative_count(self, started_battle):
        """run_ticks() with negative count does nothing."""
        initial_tick = started_battle.get_battle_state()['tick_count']

        started_battle.run_ticks(-5)

        state = started_battle.get_battle_state()
        # Negative range produces empty iterator, so no ticks run
        assert state['tick_count'] == initial_tick

    def test_add_ship_to_arbitrary_team_id(self, service, team0_ship):
        """add_ship() with team_id > 1 still adds to team1 list."""
        service.create_battle()

        # Team ID 5 should go to team1 list (non-0)
        result = service.add_ship(team0_ship, team_id=5)

        assert result.success is True
        assert team0_ship.team_id == 5
        # Check ship is in team1 list (anything non-0 goes there)
        assert team0_ship in service._team1_ships

    def test_get_battle_state_projectile_count_initially_zero(self, started_battle):
        """get_battle_state() returns zero projectile count initially."""
        state = started_battle.get_battle_state()
        assert state['projectile_count'] == 0

    def test_get_alive_ships_empty_when_all_dead(self, started_battle):
        """get_alive_ships() returns empty list when all ships dead."""
        state = started_battle.get_battle_state()

        # Kill all ships
        for ship in state['team_0_ships'] + state['team_1_ships']:
            ship.is_alive = False

        alive = started_battle.get_alive_ships()
        assert alive == []

    def test_multiple_resets(self, service, team0_ship, team1_ship):
        """reset() can be called multiple times without error."""
        service.create_battle()
        service.add_ship(team0_ship, team_id=0)
        service.add_ship(team1_ship, team_id=1)
        service.start_battle()

        # Multiple resets should work
        service.reset()
        service.reset()
        service.reset()

        assert service._engine is None
        assert service._team0_ships == []
        assert service._team1_ships == []

    def test_get_winner_both_teams_dead_is_draw(self, service, team0_ship, team1_ship):
        """get_winner() returns -1 (draw) when both teams eliminated."""
        service.create_battle()
        service.add_ship(team0_ship, team_id=0)
        service.add_ship(team1_ship, team_id=1)
        service.start_battle()

        # Kill both teams
        team0_ship.is_alive = False
        team1_ship.is_alive = False

        # Both eliminated = draw
        assert service.get_winner() == -1

    def test_battle_state_recent_beams_field(self, started_battle):
        """get_battle_state() includes recent_beams field."""
        state = started_battle.get_battle_state()
        assert 'recent_beams' in state
        # Initially should be empty
        assert state['recent_beams'] == []
