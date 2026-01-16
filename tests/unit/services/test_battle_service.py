"""
Tests for BattleService.

This service provides an abstraction layer between UI and BattleEngine,
handling battle creation, ship management, and battle state queries.
"""
import pytest

from game.simulation.services.battle_service import BattleService, BattleResult
from game.simulation.entities.ship import Ship
from game.simulation.systems.battle_end_conditions import BattleEndMode


@pytest.fixture
def service():
    """Create a BattleService instance."""
    return BattleService()


@pytest.fixture
def team1_ship():
    """Create a ship for team 1."""
    ship = Ship(
        name="Team1 Ship",
        x=100,
        y=100,
        color=(255, 0, 0),
        team_id=0,
        ship_class="Escort"
    )
    ship.recalculate_stats()
    return ship


@pytest.fixture
def team2_ship():
    """Create a ship for team 2."""
    ship = Ship(
        name="Team2 Ship",
        x=500,
        y=100,
        color=(0, 0, 255),
        team_id=1,
        ship_class="Escort"
    )
    ship.recalculate_stats()
    return ship


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


class TestBattleServiceAddShip:
    """Tests for BattleService.add_ship()."""

    def test_add_ship_to_team(self, service, team1_ship):
        """add_ship() adds ship to specified team."""
        service.create_battle()

        result = service.add_ship(team1_ship, team_id=0)

        assert result.success is True
        state = service.get_battle_state()
        assert team1_ship in state['team_0_ships']

    def test_add_ship_updates_team_id(self, service, team1_ship):
        """add_ship() sets ship's team_id to match specified team."""
        service.create_battle()
        team1_ship.team_id = 99  # Different team

        service.add_ship(team1_ship, team_id=1)

        assert team1_ship.team_id == 1

    def test_add_ship_no_active_battle(self, service, team1_ship):
        """add_ship() fails gracefully when no battle exists."""
        # Don't create a battle

        result = service.add_ship(team1_ship, team_id=0)

        assert result.success is False


class TestBattleServiceStartBattle:
    """Tests for BattleService.start_battle()."""

    def test_start_battle_success(self, service, team1_ship, team2_ship):
        """start_battle() begins the simulation."""
        service.create_battle()
        service.add_ship(team1_ship, team_id=0)
        service.add_ship(team2_ship, team_id=1)

        result = service.start_battle()

        assert result.success is True
        state = service.get_battle_state()
        assert state['is_started'] is True

    def test_start_battle_with_end_condition(self, service, team1_ship, team2_ship):
        """start_battle() accepts end condition configuration."""
        service.create_battle()
        service.add_ship(team1_ship, team_id=0)
        service.add_ship(team2_ship, team_id=1)

        result = service.start_battle(
            end_mode=BattleEndMode.TIME_BASED,
            max_ticks=1000
        )

        assert result.success is True

    def test_start_battle_no_ships_fails(self, service):
        """start_battle() fails when no ships added."""
        service.create_battle()

        result = service.start_battle()

        assert result.success is False


class TestBattleServiceUpdate:
    """Tests for BattleService.update()."""

    def test_update_advances_tick(self, service, team1_ship, team2_ship):
        """update() advances the battle simulation by one tick."""
        service.create_battle()
        service.add_ship(team1_ship, team_id=0)
        service.add_ship(team2_ship, team_id=1)
        service.start_battle()

        initial_tick = service.get_battle_state()['tick_count']
        service.update()
        new_tick = service.get_battle_state()['tick_count']

        assert new_tick == initial_tick + 1

    def test_update_multiple_ticks(self, service, team1_ship, team2_ship):
        """update() can be called multiple times."""
        service.create_battle()
        service.add_ship(team1_ship, team_id=0)
        service.add_ship(team2_ship, team_id=1)
        service.start_battle()

        for _ in range(10):
            service.update()

        state = service.get_battle_state()
        assert state['tick_count'] == 10


class TestBattleServiceGetBattleState:
    """Tests for BattleService.get_battle_state()."""

    def test_get_battle_state_structure(self, service, team1_ship, team2_ship):
        """get_battle_state() returns expected structure."""
        service.create_battle()
        service.add_ship(team1_ship, team_id=0)
        service.add_ship(team2_ship, team_id=1)
        service.start_battle()

        state = service.get_battle_state()

        assert 'is_started' in state
        assert 'is_over' in state
        assert 'tick_count' in state
        assert 'team_0_ships' in state
        assert 'team_1_ships' in state
        assert 'winner' in state

    def test_get_battle_state_no_battle(self, service):
        """get_battle_state() returns empty state when no battle."""
        state = service.get_battle_state()

        assert state.get('is_started') is False


class TestBattleServiceIsBattleOver:
    """Tests for BattleService.is_battle_over()."""

    def test_is_battle_over_initial(self, service, team1_ship, team2_ship):
        """is_battle_over() returns False for new battle."""
        service.create_battle()
        service.add_ship(team1_ship, team_id=0)
        service.add_ship(team2_ship, team_id=1)
        service.start_battle()

        assert service.is_battle_over() is False


class TestBattleResult:
    """Tests for BattleResult dataclass."""

    def test_result_success(self):
        """BattleResult stores success state correctly."""
        result = BattleResult(success=True)

        assert result.success is True
        assert result.errors == []

    def test_result_with_errors(self):
        """BattleResult stores errors correctly."""
        result = BattleResult(
            success=False,
            errors=["Error 1", "Error 2"]
        )

        assert result.success is False
        assert len(result.errors) == 2
