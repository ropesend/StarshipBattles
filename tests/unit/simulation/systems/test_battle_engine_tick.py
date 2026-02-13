"""
Tests for BattleEngine.update() tick processing.

PROJ-118 Phase 2 Task 2.14: Comprehensive unit tests for:
- update() method tick processing
- System update order
- Delta time handling (tick-based simulation)
- Edge cases (battle already over, early returns)
- Mock external dependencies appropriately
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, call
import pygame

from game.simulation.systems.battle_engine import BattleEngine
from game.simulation.systems.battle_end_conditions import BattleEndMode, BattleEndCondition
from game.core.constants import AttackType


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_ship():
    """Create a mock ship for testing."""
    ship = Mock()
    ship.name = "TestShip"
    ship.is_alive = True
    ship.is_derelict = False
    ship.team_id = 0
    ship.position = pygame.math.Vector2(0, 0)
    ship.velocity = pygame.math.Vector2(0, 0)
    ship.angle = 0
    ship.total_thrust = 100
    ship.turn_speed = 10
    ship.hp = 100
    ship.max_hp = 100
    ship.radius = 20
    ship.get_all_components = Mock(return_value=[])
    ship.just_fired_projectiles = []
    ship.update = Mock()
    return ship


@pytest.fixture
def mock_ship_team1():
    """Create a mock ship for team 1."""
    ship = Mock()
    ship.name = "EnemyShip"
    ship.is_alive = True
    ship.is_derelict = False
    ship.team_id = 1
    ship.position = pygame.math.Vector2(500, 0)
    ship.velocity = pygame.math.Vector2(0, 0)
    ship.angle = 0
    ship.total_thrust = 100
    ship.turn_speed = 10
    ship.hp = 100
    ship.max_hp = 100
    ship.radius = 20
    ship.get_all_components = Mock(return_value=[])
    ship.just_fired_projectiles = []
    ship.update = Mock()
    return ship


@pytest.fixture
def mock_ai_controller():
    """Create a mock AI controller."""
    ai = Mock()
    ai.update = Mock()
    ai.ship = Mock()
    ai.ship.ship = Mock()  # ShipControllableAdapter wrapping
    return ai


@pytest.fixture
def mock_projectile():
    """Create a mock projectile."""
    proj = Mock()
    proj.is_alive = True
    proj.position = pygame.math.Vector2(100, 100)
    proj.velocity = pygame.math.Vector2(10, 0)
    proj.team_id = 0
    proj.type = AttackType.PROJECTILE
    return proj


@pytest.fixture
def battle_engine():
    """Create a BattleEngine instance for testing with mocked dependencies."""
    with patch('game.simulation.systems.battle_engine.BattleLogger'):
        engine = BattleEngine()
        # Initialize minimal state
        engine.ships = []
        engine.ai_controllers = []
        engine.tick_counter = 0
        engine.end_condition = BattleEndCondition(mode=BattleEndMode.HP_BASED)
        engine.recent_beams = []
        return engine


@pytest.fixture
def battle_engine_with_ships(battle_engine, mock_ship, mock_ship_team1, mock_ai_controller):
    """Create a BattleEngine with ships and AI controllers set up."""
    # Create two AI controllers
    ai1 = Mock()
    ai1.update = Mock()
    ai1.ship = Mock()
    ai1.ship.ship = mock_ship

    ai2 = Mock()
    ai2.update = Mock()
    ai2.ship = Mock()
    ai2.ship.ship = mock_ship_team1

    battle_engine.ships = [mock_ship, mock_ship_team1]
    battle_engine.ai_controllers = [ai1, ai2]
    return battle_engine


# =============================================================================
# Test: Tick Counter Increment
# =============================================================================

class TestTickCounterIncrement:
    """Tests for tick_counter behavior during update()."""

    def test_tick_counter_increments_on_update(self, battle_engine_with_ships):
        """tick_counter should increment by 1 on each update() call."""
        engine = battle_engine_with_ships

        assert engine.tick_counter == 0

        engine.update()
        assert engine.tick_counter == 1

        engine.update()
        assert engine.tick_counter == 2

        engine.update()
        assert engine.tick_counter == 3

    def test_tick_counter_not_incremented_when_battle_over(self, battle_engine):
        """tick_counter should NOT increment if battle is already over."""
        # Set up battle-over condition (no ships)
        battle_engine.ships = []
        battle_engine.tick_counter = 100
        battle_engine.end_condition = BattleEndCondition(mode=BattleEndMode.HP_BASED)

        # Manually mark as over by having no ships (HP_BASED will trigger)
        assert battle_engine.is_battle_over() is True

        engine_tick_before = battle_engine.tick_counter
        battle_engine.update()

        assert battle_engine.tick_counter == engine_tick_before

    def test_tick_counter_starts_at_zero(self, battle_engine):
        """Fresh engine should have tick_counter at 0."""
        assert battle_engine.tick_counter == 0


# =============================================================================
# Test: Early Return When Battle Over
# =============================================================================

class TestEarlyReturnWhenBattleOver:
    """Tests for early return behavior when battle is over."""

    def test_update_returns_immediately_when_battle_over(
        self, battle_engine, mock_ship
    ):
        """update() should return immediately if is_battle_over() is True."""
        # Set up time-based end condition
        battle_engine.ships = [mock_ship]
        battle_engine.end_condition = BattleEndCondition(
            mode=BattleEndMode.TIME_BASED,
            max_ticks=10
        )
        battle_engine.tick_counter = 10  # At limit

        # Verify battle is over
        assert battle_engine.is_battle_over() is True

        # Create mock to track if ship.update is called
        mock_ship.update = Mock()

        battle_engine.update()

        # Ship.update should NOT be called since battle is over
        mock_ship.update.assert_not_called()

    def test_systems_not_updated_when_battle_over(
        self, battle_engine_with_ships
    ):
        """No systems should be updated when battle is over."""
        engine = battle_engine_with_ships
        engine.end_condition = BattleEndCondition(
            mode=BattleEndMode.TIME_BASED,
            max_ticks=5
        )
        engine.tick_counter = 5  # At limit

        # Track calls
        for ai in engine.ai_controllers:
            ai.update.reset_mock()
        for ship in engine.ships:
            ship.update.reset_mock()

        engine.update()

        # Nothing should be updated
        for ai in engine.ai_controllers:
            ai.update.assert_not_called()
        for ship in engine.ships:
            ship.update.assert_not_called()


# =============================================================================
# Test: Recent Beams Cleared
# =============================================================================

class TestRecentBeamsCleared:
    """Tests for recent_beams clearing behavior."""

    def test_recent_beams_cleared_at_start_of_tick(self, battle_engine_with_ships):
        """recent_beams should be cleared at the start of each tick."""
        engine = battle_engine_with_ships

        # Pre-populate with some beam data
        engine.recent_beams = [
            {'origin': (0, 0), 'target': (100, 100)},
            {'origin': (50, 50), 'target': (200, 200)},
        ]

        engine.update()

        # Should be cleared
        assert engine.recent_beams == []

    def test_recent_beams_not_cleared_when_battle_over(self, battle_engine):
        """recent_beams should NOT be cleared when battle is already over."""
        battle_engine.ships = []  # No ships = battle over
        battle_engine.recent_beams = [{'test': 'data'}]

        battle_engine.update()

        # Should remain unchanged since update() returns early
        assert battle_engine.recent_beams == [{'test': 'data'}]


# =============================================================================
# Test: Grid Update
# =============================================================================

class TestGridUpdate:
    """Tests for spatial grid updates during tick."""

    def test_grid_cleared_each_tick(self, battle_engine_with_ships):
        """Spatial grid should be cleared at the start of each tick."""
        engine = battle_engine_with_ships

        # Spy on grid.clear
        engine.grid.clear = Mock()

        engine.update()

        engine.grid.clear.assert_called_once()

    def test_alive_ships_inserted_into_grid(self, battle_engine_with_ships):
        """All alive ships should be inserted into the grid."""
        engine = battle_engine_with_ships

        # Spy on grid.insert
        engine.grid.insert = Mock()

        engine.update()

        # Both ships are alive, so both should be inserted
        assert engine.grid.insert.call_count == 2

    def test_dead_ships_not_inserted_into_grid(
        self, battle_engine, mock_ship, mock_ship_team1
    ):
        """Dead ships should NOT be inserted into the grid."""
        # Create a third ship on team 1 so battle doesn't end when one dies
        ship_team1_extra = Mock()
        ship_team1_extra.name = "EnemyShip2"
        ship_team1_extra.is_alive = True
        ship_team1_extra.is_derelict = False
        ship_team1_extra.team_id = 1
        ship_team1_extra.position = pygame.math.Vector2(600, 0)
        ship_team1_extra.velocity = pygame.math.Vector2(0, 0)
        ship_team1_extra.total_thrust = 100
        ship_team1_extra.turn_speed = 10
        ship_team1_extra.get_all_components = Mock(return_value=[])
        ship_team1_extra.just_fired_projectiles = []
        ship_team1_extra.update = Mock()

        # Set up engine with ships (one dead)
        mock_ship_team1.is_alive = False  # This ship is dead

        battle_engine.ships = [mock_ship, mock_ship_team1, ship_team1_extra]
        battle_engine.ai_controllers = []
        battle_engine.end_condition = BattleEndCondition(mode=BattleEndMode.MANUAL)

        # Track inserts by wrapping the original insert
        insert_calls = []
        original_insert = battle_engine.grid.insert
        def tracking_insert(entity):
            insert_calls.append(entity)
            return original_insert(entity)
        battle_engine.grid.insert = tracking_insert

        battle_engine.update()

        # Only alive ships should be inserted (2 out of 3)
        assert len(insert_calls) == 2
        assert mock_ship in insert_calls
        assert ship_team1_extra in insert_calls
        assert mock_ship_team1 not in insert_calls

    def test_alive_projectiles_inserted_into_grid(
        self, battle_engine_with_ships, mock_projectile
    ):
        """Alive projectiles should be inserted into the grid."""
        engine = battle_engine_with_ships
        engine.projectile_manager.projectiles = [mock_projectile]

        # Spy on grid.insert
        engine.grid.insert = Mock()

        engine.update()

        # 2 ships + 1 projectile = 3 inserts
        assert engine.grid.insert.call_count == 3

    def test_dead_projectiles_not_inserted_into_grid(
        self, battle_engine_with_ships, mock_projectile
    ):
        """Dead projectiles should NOT be inserted into the grid."""
        engine = battle_engine_with_ships
        mock_projectile.is_alive = False
        engine.projectile_manager.projectiles = [mock_projectile]

        # Spy on grid.insert
        engine.grid.insert = Mock()

        engine.update()

        # Only 2 ships, no projectile
        assert engine.grid.insert.call_count == 2


# =============================================================================
# Test: System Update Order
# =============================================================================

class TestSystemUpdateOrder:
    """Tests for the correct order of system updates."""

    def test_ai_updated_before_ships(self, battle_engine_with_ships):
        """AI controllers should be updated before ships."""
        engine = battle_engine_with_ships

        call_order = []

        def ai_update():
            call_order.append('ai')

        def ship_update(context=None):
            call_order.append('ship')

        for ai in engine.ai_controllers:
            ai.update = ai_update
        for ship in engine.ships:
            ship.update = ship_update

        engine.update()

        # AI should come before ships
        ai_indices = [i for i, x in enumerate(call_order) if x == 'ai']
        ship_indices = [i for i, x in enumerate(call_order) if x == 'ship']

        assert len(ai_indices) > 0
        assert len(ship_indices) > 0
        assert max(ai_indices) < min(ship_indices)

    def test_all_ai_controllers_updated(self, battle_engine_with_ships):
        """All AI controllers should be updated each tick."""
        engine = battle_engine_with_ships

        engine.update()

        for ai in engine.ai_controllers:
            ai.update.assert_called_once()

    def test_all_ships_updated(self, battle_engine_with_ships):
        """All ships (including dead ones) should have update() called."""
        engine = battle_engine_with_ships

        engine.update()

        for ship in engine.ships:
            ship.update.assert_called_once()

    def test_ships_receive_combat_context(self, battle_engine_with_ships):
        """Ships should receive combat context with projectiles and grid."""
        engine = battle_engine_with_ships

        engine.update()

        for ship in engine.ships:
            # Verify update was called with context
            ship.update.assert_called_once()
            call_kwargs = ship.update.call_args[1]
            assert 'context' in call_kwargs
            context = call_kwargs['context']
            assert 'projectiles' in context
            assert 'grid' in context


# =============================================================================
# Test: Attack Processing
# =============================================================================

class TestAttackProcessing:
    """Tests for processing new attacks during tick."""

    def test_projectile_attacks_added_to_manager(self, battle_engine_with_ships):
        """Projectile attacks should be added to projectile manager."""
        engine = battle_engine_with_ships

        # Create mock projectile attack
        projectile = Mock()
        projectile.type = AttackType.PROJECTILE
        projectile.position = pygame.math.Vector2(0, 0)

        # Ship fires projectile
        engine.ships[0].just_fired_projectiles = [projectile]

        engine.projectile_manager.add_projectile = Mock()

        engine.update()

        engine.projectile_manager.add_projectile.assert_called_once_with(projectile)

    def test_missile_attacks_added_to_manager(self, battle_engine_with_ships):
        """Missile attacks should be added to projectile manager."""
        engine = battle_engine_with_ships

        # Create mock missile attack
        missile = Mock()
        missile.type = AttackType.MISSILE
        missile.target = Mock()

        # Ship fires missile
        engine.ships[0].just_fired_projectiles = [missile]

        engine.projectile_manager.add_projectile = Mock()

        engine.update()

        engine.projectile_manager.add_projectile.assert_called_once_with(missile)

    def test_just_fired_projectiles_cleared_after_processing(
        self, battle_engine_with_ships
    ):
        """just_fired_projectiles should be cleared after processing."""
        engine = battle_engine_with_ships

        projectile = Mock()
        projectile.type = AttackType.PROJECTILE
        projectile.position = pygame.math.Vector2(0, 0)
        projectile.velocity = pygame.math.Vector2(10, 0)
        projectile.is_alive = True
        projectile.team_id = 0
        projectile.radius = 5
        projectile.damage = 10
        projectile.distance_traveled = 0

        engine.ships[0].just_fired_projectiles = [projectile]

        # Mock projectile manager's update to avoid processing issues
        engine.projectile_manager.update = Mock()

        engine.update()

        assert engine.ships[0].just_fired_projectiles == []

    def test_beam_attacks_processed_by_collision_system(
        self, battle_engine_with_ships
    ):
        """Beam attacks should be processed by collision system."""
        engine = battle_engine_with_ships

        # Create mock beam attack dict
        beam = {'type': AttackType.BEAM, 'origin': (0, 0), 'target': (100, 0)}

        engine.ships[0].just_fired_projectiles = [beam]
        engine.collision_system.process_beam_attack = Mock()

        engine.update()

        engine.collision_system.process_beam_attack.assert_called_once()

    def test_string_attack_types_converted_to_enum(self, battle_engine_with_ships):
        """String attack types should be converted to AttackType enum."""
        engine = battle_engine_with_ships

        # Create attack with string type (legacy format)
        projectile = Mock()
        projectile.type = 'projectile'  # String instead of enum
        projectile.position = pygame.math.Vector2(0, 0)

        engine.ships[0].just_fired_projectiles = [projectile]
        engine.projectile_manager.add_projectile = Mock()

        engine.update()

        # Should still be processed correctly
        engine.projectile_manager.add_projectile.assert_called_once()

    def test_dict_attack_types_handled(self, battle_engine_with_ships):
        """Dictionary-style attacks should be handled correctly."""
        engine = battle_engine_with_ships

        # Beam attack as dict
        beam_dict = {
            'type': AttackType.BEAM,
            'origin': (0, 0),
            'target': (100, 0),
            'damage': 10
        }

        engine.ships[0].just_fired_projectiles = [beam_dict]
        engine.collision_system.process_beam_attack = Mock()

        engine.update()

        engine.collision_system.process_beam_attack.assert_called_once()


# =============================================================================
# Test: Collision Processing
# =============================================================================

class TestCollisionProcessing:
    """Tests for ramming collision processing during tick."""

    def test_ramming_processed_each_tick(self, battle_engine_with_ships):
        """Ramming collisions should be processed each tick."""
        engine = battle_engine_with_ships
        engine.collision_system.process_ramming = Mock()

        engine.update()

        engine.collision_system.process_ramming.assert_called_once()

    def test_ramming_receives_ships_and_logger(self, battle_engine_with_ships):
        """process_ramming should receive ships list and logger."""
        engine = battle_engine_with_ships
        engine.collision_system.process_ramming = Mock()

        engine.update()

        call_args = engine.collision_system.process_ramming.call_args[0]
        assert call_args[0] == engine.ships
        assert call_args[1] == engine.logger


# =============================================================================
# Test: Projectile Manager Update
# =============================================================================

class TestProjectileManagerUpdate:
    """Tests for projectile manager updates during tick."""

    def test_projectile_manager_updated_each_tick(self, battle_engine_with_ships):
        """Projectile manager should be updated each tick."""
        engine = battle_engine_with_ships
        engine.projectile_manager.update = Mock()

        engine.update()

        engine.projectile_manager.update.assert_called_once()

    def test_projectile_manager_receives_grid(self, battle_engine_with_ships):
        """Projectile manager update should receive the spatial grid."""
        engine = battle_engine_with_ships
        engine.projectile_manager.update = Mock()

        engine.update()

        engine.projectile_manager.update.assert_called_once_with(engine.grid)


# =============================================================================
# Test: Multiple Ticks
# =============================================================================

class TestMultipleTicks:
    """Tests for behavior across multiple ticks."""

    def test_multiple_ticks_increment_counter(self, battle_engine_with_ships):
        """Multiple update() calls should increment tick_counter correctly."""
        engine = battle_engine_with_ships

        for i in range(10):
            engine.update()

        assert engine.tick_counter == 10

    def test_state_persists_across_ticks(self, battle_engine_with_ships):
        """State changes should persist across ticks."""
        engine = battle_engine_with_ships

        engine.update()

        # Modify state
        engine.ships[0].is_alive = False

        engine.update()

        # State should still be modified
        assert engine.ships[0].is_alive is False

    def test_attacks_from_multiple_ships_processed(
        self, battle_engine_with_ships
    ):
        """Attacks from multiple ships should all be processed in one tick."""
        engine = battle_engine_with_ships

        proj1 = Mock()
        proj1.type = AttackType.PROJECTILE
        proj1.position = pygame.math.Vector2(0, 0)

        proj2 = Mock()
        proj2.type = AttackType.PROJECTILE
        proj2.position = pygame.math.Vector2(100, 0)

        engine.ships[0].just_fired_projectiles = [proj1]
        engine.ships[1].just_fired_projectiles = [proj2]

        engine.projectile_manager.add_projectile = Mock()

        engine.update()

        assert engine.projectile_manager.add_projectile.call_count == 2


# =============================================================================
# Test: Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases in tick processing."""

    def test_no_ships_update_completes(self, battle_engine):
        """update() should handle empty ships list gracefully."""
        battle_engine.ships = []
        battle_engine.ai_controllers = []

        # Should not raise
        battle_engine.update()

        # But battle is over (HP_BASED with no ships)
        assert battle_engine.is_battle_over() is True

    def test_no_ai_controllers_update_completes(self, battle_engine, mock_ship):
        """update() should handle empty AI controller list."""
        battle_engine.ships = [mock_ship]
        battle_engine.ai_controllers = []

        # Make sure battle doesn't end immediately
        battle_engine.end_condition = BattleEndCondition(mode=BattleEndMode.MANUAL)

        # Should not raise
        battle_engine.update()

        # Ship should still be updated
        mock_ship.update.assert_called_once()

    def test_ship_with_no_just_fired_projectiles_attr(
        self, battle_engine_with_ships
    ):
        """Ships without just_fired_projectiles attribute should be handled."""
        engine = battle_engine_with_ships

        # Remove the attribute from one ship
        del engine.ships[0].just_fired_projectiles

        # Should not raise
        engine.update()

    def test_many_projectiles_processed(self, battle_engine_with_ships):
        """Large number of projectiles should be handled."""
        engine = battle_engine_with_ships

        # Create many projectiles
        projectiles = []
        for i in range(100):
            proj = Mock()
            proj.type = AttackType.PROJECTILE
            proj.position = pygame.math.Vector2(i, i)
            projectiles.append(proj)

        engine.ships[0].just_fired_projectiles = projectiles
        engine.projectile_manager.add_projectile = Mock()

        engine.update()

        assert engine.projectile_manager.add_projectile.call_count == 100

    def test_mixed_attack_types_in_single_tick(self, battle_engine_with_ships):
        """Mixed attack types from same ship should all be processed."""
        engine = battle_engine_with_ships

        proj = Mock()
        proj.type = AttackType.PROJECTILE
        proj.position = pygame.math.Vector2(0, 0)

        missile = Mock()
        missile.type = AttackType.MISSILE
        missile.target = Mock()

        beam = {'type': AttackType.BEAM, 'origin': (0, 0), 'target': (100, 0)}

        engine.ships[0].just_fired_projectiles = [proj, missile, beam]

        engine.projectile_manager.add_projectile = Mock()
        engine.collision_system.process_beam_attack = Mock()

        engine.update()

        # Projectile and missile should be added
        assert engine.projectile_manager.add_projectile.call_count == 2
        # Beam should be processed
        engine.collision_system.process_beam_attack.assert_called_once()

    def test_rapid_succession_ticks(self, battle_engine_with_ships):
        """Many rapid ticks should work correctly."""
        engine = battle_engine_with_ships
        engine.end_condition = BattleEndCondition(
            mode=BattleEndMode.TIME_BASED,
            max_ticks=1000
        )

        for _ in range(100):
            engine.update()

        assert engine.tick_counter == 100


# =============================================================================
# Test: Tick Processing Order (Full Sequence)
# =============================================================================

class TestTickProcessingOrder:
    """Tests for the complete tick processing sequence."""

    def test_full_tick_sequence_order(self, battle_engine_with_ships):
        """Verify the complete tick processing order."""
        engine = battle_engine_with_ships

        call_sequence = []

        # Spy on all major operations
        original_grid_clear = engine.grid.clear
        def track_grid_clear():
            call_sequence.append('grid_clear')
            original_grid_clear()
        engine.grid.clear = track_grid_clear

        original_grid_insert = engine.grid.insert
        def track_grid_insert(entity):
            if 'grid_insert' not in call_sequence:
                call_sequence.append('grid_insert')
            original_grid_insert(entity)
        engine.grid.insert = track_grid_insert

        for ai in engine.ai_controllers:
            def track_ai_update():
                if 'ai_update' not in call_sequence:
                    call_sequence.append('ai_update')
            ai.update = track_ai_update

        for ship in engine.ships:
            def track_ship_update(context=None):
                if 'ship_update' not in call_sequence:
                    call_sequence.append('ship_update')
            ship.update = track_ship_update

        engine.collision_system.process_ramming = Mock(
            side_effect=lambda *args: call_sequence.append('ramming')
        )
        engine.projectile_manager.update = Mock(
            side_effect=lambda *args: call_sequence.append('projectile_update')
        )

        engine.update()

        # Verify order: grid_clear -> grid_insert -> ai_update -> ship_update
        #               -> ramming -> projectile_update
        expected_order = [
            'grid_clear',
            'grid_insert',
            'ai_update',
            'ship_update',
            'ramming',
            'projectile_update'
        ]

        assert call_sequence == expected_order


# =============================================================================
# Test: Fighter Launch Processing
# =============================================================================

class TestFighterLaunchProcessing:
    """Tests for LAUNCH attack type (fighter spawning) during tick."""

    def test_launch_attack_spawns_fighter_ship(self, battle_engine_with_ships):
        """LAUNCH attack should create a new fighter ship."""
        engine = battle_engine_with_ships

        # Set up factory for fighter creation
        mock_factory = Mock()
        mock_ai = Mock()
        mock_ai.update = Mock()
        mock_ai.ship = Mock()
        mock_factory.create_for_ship = Mock(return_value=mock_ai)
        engine._ai_factory = mock_factory

        source_ship = engine.ships[0]
        source_ship.color = (255, 0, 0)
        source_ship.theme_id = "test_theme"
        source_ship.registries = Mock()
        source_ship.velocity = pygame.math.Vector2(0, 0)
        source_ship.angle = 0

        # Create LAUNCH attack dict
        launch_attack = {
            'type': AttackType.LAUNCH,
            'source': source_ship,
            'hangar': Mock(),
            'fighter_class': 'Fighter (Small)',
            'origin': pygame.math.Vector2(100, 100)
        }

        source_ship.just_fired_projectiles = [launch_attack]
        initial_ship_count = len(engine.ships)

        # Mock Ship class to avoid full initialization
        with patch('game.simulation.systems.battle_engine.Ship') as MockShip:
            mock_fighter = Mock()
            mock_fighter.team_id = source_ship.team_id
            mock_fighter.velocity = pygame.math.Vector2(0, 0)
            mock_fighter.angle = 0
            mock_fighter.is_alive = True
            mock_fighter.position = pygame.math.Vector2(100, 100)
            mock_fighter.just_fired_projectiles = []
            mock_fighter.update = Mock()
            MockShip.return_value = mock_fighter

            engine.update()

            # Fighter should be added to ships
            assert mock_fighter in engine.ships
            assert len(engine.ships) == initial_ship_count + 1

    def test_launch_attack_creates_ai_controller_for_fighter(
        self, battle_engine_with_ships
    ):
        """LAUNCH attack should create AI controller for spawned fighter."""
        engine = battle_engine_with_ships

        mock_factory = Mock()
        mock_ai = Mock()
        mock_ai.update = Mock()
        mock_ai.ship = Mock()
        mock_factory.create_for_ship = Mock(return_value=mock_ai)
        engine._ai_factory = mock_factory

        source_ship = engine.ships[0]
        source_ship.color = (255, 0, 0)
        source_ship.theme_id = "test_theme"
        source_ship.registries = Mock()
        source_ship.velocity = pygame.math.Vector2(0, 0)
        source_ship.angle = 0

        launch_attack = {
            'type': AttackType.LAUNCH,
            'source': source_ship,
            'hangar': Mock(),
            'origin': pygame.math.Vector2(0, 0)
        }

        source_ship.just_fired_projectiles = [launch_attack]

        with patch('game.simulation.systems.battle_engine.Ship') as MockShip:
            mock_fighter = Mock()
            mock_fighter.team_id = source_ship.team_id
            mock_fighter.velocity = pygame.math.Vector2(0, 0)
            mock_fighter.angle = 0
            mock_fighter.is_alive = True
            mock_fighter.position = pygame.math.Vector2(0, 0)
            mock_fighter.just_fired_projectiles = []
            mock_fighter.update = Mock()
            MockShip.return_value = mock_fighter

            engine.update()

            # Factory should be called to create AI for fighter
            mock_factory.create_for_ship.assert_called_once()
            # AI should be added to controllers
            assert mock_ai in engine.ai_controllers

    def test_launch_attack_fighter_inherits_team_id(self, battle_engine_with_ships):
        """Spawned fighter should inherit team_id from source ship."""
        engine = battle_engine_with_ships

        mock_factory = Mock()
        mock_ai = Mock()
        mock_ai.update = Mock()
        mock_ai.ship = Mock()
        mock_factory.create_for_ship = Mock(return_value=mock_ai)
        engine._ai_factory = mock_factory

        source_ship = engine.ships[0]
        source_ship.team_id = 0
        source_ship.color = (255, 0, 0)
        source_ship.theme_id = "test_theme"
        source_ship.registries = Mock()
        source_ship.velocity = pygame.math.Vector2(0, 0)
        source_ship.angle = 0

        launch_attack = {
            'type': AttackType.LAUNCH,
            'source': source_ship,
            'hangar': Mock(),
            'origin': pygame.math.Vector2(0, 0)
        }

        source_ship.just_fired_projectiles = [launch_attack]

        with patch('game.simulation.systems.battle_engine.Ship') as MockShip:
            mock_fighter = Mock()
            mock_fighter.team_id = source_ship.team_id  # Must match for enemy_team calc
            mock_fighter.velocity = pygame.math.Vector2(0, 0)
            mock_fighter.angle = 0
            mock_fighter.is_alive = True
            mock_fighter.position = pygame.math.Vector2(0, 0)
            mock_fighter.just_fired_projectiles = []
            mock_fighter.update = Mock()
            MockShip.return_value = mock_fighter

            engine.update()

            # Verify Ship was called with correct team_id
            MockShip.assert_called_once()
            call_kwargs = MockShip.call_args[1]
            assert call_kwargs['team_id'] == source_ship.team_id

    def test_launch_attack_without_ai_factory_raises_error(
        self, battle_engine_with_ships
    ):
        """LAUNCH without ai_factory should raise ValueError."""
        engine = battle_engine_with_ships
        engine._ai_factory = None

        source_ship = engine.ships[0]
        source_ship.color = (255, 0, 0)
        source_ship.theme_id = "test_theme"
        source_ship.registries = Mock()
        source_ship.velocity = pygame.math.Vector2(0, 0)
        source_ship.angle = 0

        launch_attack = {
            'type': AttackType.LAUNCH,
            'source': source_ship,
            'hangar': Mock(),
            'origin': pygame.math.Vector2(0, 0)
        }

        source_ship.just_fired_projectiles = [launch_attack]

        with patch('game.simulation.systems.battle_engine.Ship'):
            with pytest.raises(ValueError, match="ai_factory"):
                engine.update()

    def test_launch_attack_fighter_velocity_boosted(self, battle_engine_with_ships):
        """Spawned fighter should have launch velocity boost."""
        engine = battle_engine_with_ships

        mock_factory = Mock()
        mock_ai = Mock()
        mock_ai.update = Mock()
        mock_ai.ship = Mock()
        mock_factory.create_for_ship = Mock(return_value=mock_ai)
        engine._ai_factory = mock_factory

        source_ship = engine.ships[0]
        source_ship.color = (255, 0, 0)
        source_ship.theme_id = "test_theme"
        source_ship.registries = Mock()
        source_ship.velocity = pygame.math.Vector2(10, 5)
        source_ship.angle = 0  # Facing right

        launch_attack = {
            'type': AttackType.LAUNCH,
            'source': source_ship,
            'hangar': Mock(),
            'origin': pygame.math.Vector2(0, 0)
        }

        source_ship.just_fired_projectiles = [launch_attack]

        with patch('game.simulation.systems.battle_engine.Ship') as MockShip:
            mock_fighter = Mock()
            mock_fighter.team_id = 0
            mock_fighter.velocity = pygame.math.Vector2(0, 0)
            mock_fighter.angle = 0
            mock_fighter.is_alive = True
            mock_fighter.position = pygame.math.Vector2(0, 0)
            mock_fighter.just_fired_projectiles = []
            mock_fighter.update = Mock()
            MockShip.return_value = mock_fighter

            engine.update()

            # Fighter velocity should be set (inherits + boost)
            # Check that velocity was modified (not zero)
            assert mock_fighter.velocity != pygame.math.Vector2(0, 0)


# =============================================================================
# Test: Unknown Attack Type Handling
# =============================================================================

class TestUnknownAttackTypeHandling:
    """Tests for handling unknown or invalid attack types."""

    def test_unknown_string_attack_type_ignored(self, battle_engine_with_ships):
        """Unknown string attack types should be silently ignored."""
        engine = battle_engine_with_ships

        attack = Mock()
        attack.type = 'unknown_type'
        attack.position = pygame.math.Vector2(0, 0)

        engine.ships[0].just_fired_projectiles = [attack]
        engine.projectile_manager.add_projectile = Mock()
        engine.collision_system.process_beam_attack = Mock()

        # Should not raise
        engine.update()

        # Neither projectile nor beam should be processed
        engine.projectile_manager.add_projectile.assert_not_called()
        engine.collision_system.process_beam_attack.assert_not_called()

    def test_none_attack_type_handled(self, battle_engine_with_ships):
        """Attack with None type should be handled gracefully."""
        engine = battle_engine_with_ships

        attack = Mock()
        attack.type = None
        attack.position = pygame.math.Vector2(0, 0)

        engine.ships[0].just_fired_projectiles = [attack]
        engine.projectile_manager.add_projectile = Mock()

        # Should not raise
        engine.update()

        # Should not add as projectile
        engine.projectile_manager.add_projectile.assert_not_called()

    def test_empty_just_fired_projectiles_handled(self, battle_engine_with_ships):
        """Empty just_fired_projectiles should be handled gracefully."""
        engine = battle_engine_with_ships

        engine.ships[0].just_fired_projectiles = []
        engine.ships[1].just_fired_projectiles = []

        # Should not raise
        engine.update()

        # Tick counter should still increment
        assert engine.tick_counter == 1


# =============================================================================
# Test: Dict-based Attack Processing
# =============================================================================

class TestDictBasedAttackProcessing:
    """Tests for dictionary-style attack data handling."""

    def test_dict_projectile_not_added_to_manager(self, battle_engine_with_ships):
        """Dict-style projectile attacks should NOT be added to projectile manager.

        Note: The engine checks 'if not is_dict' before adding projectiles.
        This is intentional - dict attacks are older format, object attacks are new.
        """
        engine = battle_engine_with_ships

        projectile_dict = {
            'type': AttackType.PROJECTILE,
            'position': (0, 0),
            'velocity': (10, 0),
            'damage': 10
        }

        engine.ships[0].just_fired_projectiles = [projectile_dict]
        engine.projectile_manager.add_projectile = Mock()

        engine.update()

        # Dict projectiles are NOT added (code checks 'if not is_dict')
        engine.projectile_manager.add_projectile.assert_not_called()

    def test_dict_missile_not_added_to_manager(self, battle_engine_with_ships):
        """Dict-style missile attacks should NOT be added to projectile manager."""
        engine = battle_engine_with_ships

        missile_dict = {
            'type': AttackType.MISSILE,
            'position': (0, 0),
            'target': Mock()
        }

        engine.ships[0].just_fired_projectiles = [missile_dict]
        engine.projectile_manager.add_projectile = Mock()

        engine.update()

        # Dict missiles are NOT added (code checks 'if not is_dict')
        engine.projectile_manager.add_projectile.assert_not_called()

    def test_dict_launch_attack_processed(self, battle_engine_with_ships):
        """Dict-style LAUNCH attacks should still spawn fighters."""
        engine = battle_engine_with_ships

        mock_factory = Mock()
        mock_ai = Mock()
        mock_ai.update = Mock()
        mock_ai.ship = Mock()
        mock_factory.create_for_ship = Mock(return_value=mock_ai)
        engine._ai_factory = mock_factory

        source_ship = engine.ships[0]
        source_ship.color = (255, 0, 0)
        source_ship.theme_id = "test_theme"
        source_ship.registries = Mock()
        source_ship.velocity = pygame.math.Vector2(0, 0)
        source_ship.angle = 0

        # LAUNCH is always dict-based
        launch_dict = {
            'type': AttackType.LAUNCH,
            'source': source_ship,
            'hangar': Mock(),
            'origin': pygame.math.Vector2(0, 0)
        }

        source_ship.just_fired_projectiles = [launch_dict]
        initial_count = len(engine.ships)

        with patch('game.simulation.systems.battle_engine.Ship') as MockShip:
            mock_fighter = Mock()
            mock_fighter.team_id = 0
            mock_fighter.velocity = pygame.math.Vector2(0, 0)
            mock_fighter.angle = 0
            mock_fighter.is_alive = True
            mock_fighter.position = pygame.math.Vector2(0, 0)
            mock_fighter.just_fired_projectiles = []
            mock_fighter.update = Mock()
            MockShip.return_value = mock_fighter

            engine.update()

            assert len(engine.ships) == initial_count + 1


# =============================================================================
# Test: Logger Integration
# =============================================================================

class TestLoggerIntegration:
    """Tests for battle logger integration during tick processing."""

    def test_projectile_fired_logged(self, battle_engine_with_ships):
        """Projectile firing should be logged."""
        engine = battle_engine_with_ships
        engine.logger = Mock()
        engine.logger.log = Mock()

        projectile = Mock()
        projectile.type = AttackType.PROJECTILE
        projectile.position = pygame.math.Vector2(50, 50)

        engine.ships[0].just_fired_projectiles = [projectile]
        engine.projectile_manager.add_projectile = Mock()

        engine.update()

        # Verify log was called with projectile message
        log_calls = [str(c) for c in engine.logger.log.call_args_list]
        assert any('Projectile' in str(c) for c in log_calls)

    def test_missile_fired_logged(self, battle_engine_with_ships):
        """Missile firing should be logged."""
        engine = battle_engine_with_ships
        engine.logger = Mock()
        engine.logger.log = Mock()

        missile = Mock()
        missile.type = AttackType.MISSILE
        missile.target = Mock()

        engine.ships[0].just_fired_projectiles = [missile]
        engine.projectile_manager.add_projectile = Mock()

        engine.update()

        # Verify log was called with missile message
        log_calls = [str(c) for c in engine.logger.log.call_args_list]
        assert any('Missile' in str(c) for c in log_calls)

    def test_fighter_launch_logged(self, battle_engine_with_ships):
        """Fighter launch should be logged."""
        engine = battle_engine_with_ships
        engine.logger = Mock()
        engine.logger.log = Mock()

        mock_factory = Mock()
        mock_ai = Mock()
        mock_ai.update = Mock()
        mock_ai.ship = Mock()
        mock_factory.create_for_ship = Mock(return_value=mock_ai)
        engine._ai_factory = mock_factory

        source_ship = engine.ships[0]
        source_ship.color = (255, 0, 0)
        source_ship.theme_id = "test_theme"
        source_ship.registries = Mock()
        source_ship.velocity = pygame.math.Vector2(0, 0)
        source_ship.angle = 0

        launch_attack = {
            'type': AttackType.LAUNCH,
            'source': source_ship,
            'hangar': Mock(),
            'origin': pygame.math.Vector2(0, 0)
        }

        source_ship.just_fired_projectiles = [launch_attack]

        with patch('game.simulation.systems.battle_engine.Ship') as MockShip:
            mock_fighter = Mock()
            mock_fighter.team_id = 0
            mock_fighter.velocity = pygame.math.Vector2(0, 0)
            mock_fighter.angle = 0
            mock_fighter.is_alive = True
            mock_fighter.position = pygame.math.Vector2(0, 0)
            mock_fighter.just_fired_projectiles = []
            mock_fighter.update = Mock()
            MockShip.return_value = mock_fighter

            engine.update()

        # Verify log was called with LAUNCH message
        log_calls = [str(c) for c in engine.logger.log.call_args_list]
        assert any('LAUNCH' in str(c) for c in log_calls)
