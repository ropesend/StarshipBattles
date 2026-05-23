"""Tests for AI Controller behavior."""
import pytest
import pygame
import math
import inspect

from game.simulation.entities.ship import Ship, LayerType
from game.ai.controller import AIController
from game.ai.policy_manager import get_default_policy_manager
from game.ai.interfaces.controllable import ShipControllableAdapter
from game.engine.spatial import SpatialGrid
from game.simulation.components.component import load_components, create_component
from game.core.registry import get_default_registry_provider
from tests.fixtures.paths import get_data_dir, get_unit_test_data_dir


# PROJ-479 Task 2.2: module-scoped cache marker for one-time JSON-loads.
# The expensive `load_components` + `load_vehicle_classes` + policy
# `load_data` calls are read-only-from-disk and only need to happen once
# per session. Per-test we still build fresh Ships from fresh_registries
# (Ship objects mutate during tests so they cannot be reused).
_AI_TEST_DATA_LOADED = False


def _ensure_ai_test_data_loaded():
    global _AI_TEST_DATA_LOADED
    if _AI_TEST_DATA_LOADED:
        return
    data_dir = get_data_dir()
    unit_test_data_dir = get_unit_test_data_dir()
    provider = get_default_registry_provider()
    load_components(str(data_dir / "components.json"), registry_provider=provider)
    from game.simulation.entities.ship_loader import load_vehicle_classes
    load_vehicle_classes(str(unit_test_data_dir / "test_vehicleclasses.json"), registry_provider=provider)
    manager = get_default_policy_manager()
    manager.load_data(
        str(unit_test_data_dir),
        targeting_file="test_targeting_policies.json",
        movement_file="test_movement_policies.json",
    )
    manager._loaded = True
    _AI_TEST_DATA_LOADED = True


@pytest.fixture
def ai_setup(fresh_registries):
    """Setup fixture for AI controller tests."""
    _ensure_ai_test_data_loaded()
    unit_test_data_dir = get_unit_test_data_dir()  # noqa: F841  (kept for future use)

    grid = SpatialGrid(cell_size=2000)

    # Create two ships with full crew infrastructure
    ship1 = Ship("Ally", 0, 0, (0, 255, 0), team_id=0, ship_class="TestM_4L", registries=fresh_registries)
    ship1.add_component(create_component('bridge', registries=fresh_registries), LayerType.CORE)
    ship1.add_component(create_component('crew_quarters', registries=fresh_registries), LayerType.CORE)
    ship1.add_component(create_component('life_support', registries=fresh_registries), LayerType.CORE)
    ship1.add_component(create_component('standard_engine', registries=fresh_registries), LayerType.OUTER)
    ship1.add_component(create_component('thruster', registries=fresh_registries), LayerType.INNER)
    ship1.recalculate_stats()

    ship2 = Ship("Enemy", 1000, 0, (255, 0, 0), team_id=1, ship_class="TestM_4L", registries=fresh_registries)
    ship2.add_component(create_component('bridge', registries=fresh_registries), LayerType.CORE)
    ship2.add_component(create_component('crew_quarters', registries=fresh_registries), LayerType.CORE)
    ship2.add_component(create_component('life_support', registries=fresh_registries), LayerType.CORE)
    ship2.add_component(create_component('standard_engine', registries=fresh_registries), LayerType.OUTER)
    ship2.add_component(create_component('thruster', registries=fresh_registries), LayerType.INNER)
    ship2.recalculate_stats()

    # Insert ships into grid
    grid.insert(ship1)
    grid.insert(ship2)

    # Create AI controller for ship1 targeting team 1
    # Use ShipControllableAdapter to match production behavior (battle_engine.py)
    ai_controller = AIController(ShipControllableAdapter(ship1), grid, enemy_team_id=1)

    yield {
        'grid': grid,
        'ship1': ship1,
        'ship2': ship2,
        'ai': ai_controller,
        'registries': fresh_registries
    }

    # Per-test cleanup: invalidate cache so next test reloads.
    global _AI_TEST_DATA_LOADED
    _AI_TEST_DATA_LOADED = False
    get_default_policy_manager().clear()


class TestAIController:
    """Tests for AIController target selection and combat behavior."""

    def test_find_target(self, ai_setup):
        """AI should find nearest enemy."""
        target = ai_setup['ai'].find_target()
        assert target == ai_setup['ship2']

    def test_find_target_ignores_dead(self, ai_setup):
        """AI should not target dead ships."""
        ai_setup['ship2'].is_alive = False
        target = ai_setup['ai'].find_target()
        assert target is None

    def test_find_target_ignores_friendly(self, ai_setup):
        """AI should not target friendly ships."""
        ai_setup['ship2'].team_id = 0  # Same team as ship1
        target = ai_setup['ai'].find_target()
        assert target is None

    def test_update_sets_target(self, ai_setup):
        """AI update should set current_target."""
        ai_setup['ai'].update()
        assert ai_setup['ship1'].current_target == ai_setup['ship2']

    def test_strategy_dispatch_max_range(self, ai_setup):
        """AI should use max_range strategy by default."""
        ai_setup['ship1'].movement_policy = 'kite_max'
        ai_setup['ship1'].comp_trigger_pulled = False  # Initialize attribute
        ai_setup['ai'].update()
        # Should have trigger pulled for firing
        assert ai_setup['ship1'].comp_trigger_pulled is True

    def test_strategy_dispatch_flee(self, ai_setup):
        """AI flee strategy should fire while retreating (per config)."""
        ai_setup['ship1'].movement_policy = 'flee_panic'
        ai_setup['ship1'].comp_trigger_pulled = False  # Initialize to check it gets set True
        ai_setup['ai'].update()
        # Flee strategy has fire_while_retreating=true (per user config)
        assert ai_setup['ship1'].comp_trigger_pulled is True

    def test_strategy_dispatch_kamikaze(self, ai_setup):
        """AI kamikaze should fire and charge."""
        ai_setup['ship1'].movement_policy = 'ramming_speed'
        ai_setup['ai'].update()
        # Kamikaze always fires
        assert ai_setup['ship1'].comp_trigger_pulled is True

    def test_check_avoidance_returns_none_when_clear(self, ai_setup):
        """Avoidance check should return None when no obstacles nearby."""
        # Move ship2 far away
        ai_setup['ship2'].position = pygame.math.Vector2(10000, 10000)
        ai_setup['grid'].clear()
        ai_setup['grid'].insert(ai_setup['ship1'])
        ai_setup['grid'].insert(ai_setup['ship2'])

        override = ai_setup['ai'].check_avoidance()
        assert override is None


@pytest.fixture
def strategy_setup(fresh_registries):
    """Setup fixture for AI strategy state tests."""
    data_dir = get_data_dir()
    unit_test_data_dir = get_unit_test_data_dir()

    # PROJ-211: Pass registry_provider explicitly
    provider = get_default_registry_provider()
    load_components(str(data_dir / "components.json"), registry_provider=provider)
    from game.simulation.entities.ship_loader import load_vehicle_classes
    load_vehicle_classes(str(unit_test_data_dir / "test_vehicleclasses.json"), registry_provider=provider)
    # Load test data for AI strategies to ensure reproducible tests
    manager = get_default_policy_manager()
    manager.load_data(
        str(unit_test_data_dir),
        targeting_file="test_targeting_policies.json",
        movement_file="test_movement_policies.json",
    )
    manager._loaded = True
    grid = SpatialGrid(cell_size=2000)

    ship = Ship("Attacker", 0, 0, (0, 255, 0), team_id=0, ship_class="TestM_4L", registries=fresh_registries)
    ship.add_component(create_component('bridge', registries=fresh_registries), LayerType.CORE)
    ship.add_component(create_component('crew_quarters', registries=fresh_registries), LayerType.CORE)
    ship.add_component(create_component('life_support', registries=fresh_registries), LayerType.CORE)
    ship.add_component(create_component('standard_engine', registries=fresh_registries), LayerType.OUTER)
    ship.add_component(create_component('railgun', registries=fresh_registries), LayerType.OUTER)
    ship.recalculate_stats()

    target = Ship("Target", 500, 0, (255, 0, 0), team_id=1, ship_class="TestM_4L", registries=fresh_registries)
    target.add_component(create_component('bridge', registries=fresh_registries), LayerType.CORE)
    target.add_component(create_component('crew_quarters', registries=fresh_registries), LayerType.CORE)
    target.add_component(create_component('life_support', registries=fresh_registries), LayerType.CORE)
    target.add_component(create_component('standard_engine', registries=fresh_registries), LayerType.OUTER)
    target.add_component(create_component('thruster', registries=fresh_registries), LayerType.INNER)
    target.recalculate_stats()

    grid.insert(ship)
    grid.insert(target)

    # Use ShipControllableAdapter to match production behavior (battle_engine.py)
    ai_controller = AIController(ShipControllableAdapter(ship), grid, enemy_team_id=1)

    yield {
        'grid': grid,
        'ship': ship,
        'target': target,
        'ai': ai_controller,
        'registries': fresh_registries
    }

    # Per-test cleanup: invalidate cache so next test reloads.
    global _AI_TEST_DATA_LOADED
    _AI_TEST_DATA_LOADED = False
    get_default_policy_manager().clear()


class TestAIStrategyStates:
    """Test AI attack run state machine."""

    def test_attack_run_state_initialization(self, strategy_setup):
        """Attack run should initialize state on first update."""
        strategy_setup['ship'].movement_policy = 'move_attack_run'
        strategy_setup['ship'].comp_trigger_pulled = False
        # Move ship far away so it starts in approach mode
        strategy_setup['ship'].position = pygame.math.Vector2(0, 0)
        strategy_setup['target'].position = pygame.math.Vector2(5000, 0)  # Far away
        strategy_setup['grid'].clear()
        strategy_setup['grid'].insert(strategy_setup['ship'])
        strategy_setup['grid'].insert(strategy_setup['target'])

        strategy_setup['grid'].insert(strategy_setup['target'])

        strategy_setup['ai'].update()

        assert strategy_setup['ai'].current_behavior is not None
        # Check if behavior has state
        assert hasattr(strategy_setup['ai'].current_behavior, 'attack_state')
        assert strategy_setup['ai'].current_behavior.attack_state == 'approach'

    def test_attack_run_transitions_to_retreat(self, strategy_setup):
        """Attack run should transition to retreat when close.

        PROJ-322 Task 3.2 (S01-CAT6-001): position the target a fraction
        of the ship's actual weapon_range away (instead of hardcoding
        the 150-unit value), so the test no longer breaks when the
        approach_distance constant is tuned.
        """
        ship = strategy_setup['ship']
        ship.movement_policy = 'move_attack_run'
        ship.position = pygame.math.Vector2(0, 0)

        weapon_range = getattr(ship, 'weapon_range', None) or 1000
        # Place target well inside the retreat threshold (a quarter of
        # weapon range is comfortably below any reasonable approach
        # distance the AI uses).
        strategy_setup['target'].position = pygame.math.Vector2(
            weapon_range * 0.25, 0,
        )

        strategy_setup['ai'].update()
        # After being very close, should switch to retreat
        assert strategy_setup['ai'].current_behavior is not None
        assert strategy_setup['ai'].current_behavior.attack_state == 'retreat'


class TestTargetingHelpers:
    """Test AI targeting helper methods (CQ-007 refactoring)."""

    def test_find_enemies_in_radius_returns_alive_enemies(self, ai_setup):
        """_find_enemies_in_radius should return alive enemies within radius."""
        enemies = ai_setup['ai']._find_enemies_in_radius()
        assert len(enemies) == 1
        assert ai_setup['ship2'] in enemies

    def test_find_enemies_in_radius_excludes_dead(self, ai_setup):
        """_find_enemies_in_radius should exclude dead ships."""
        ai_setup['ship2'].is_alive = False
        enemies = ai_setup['ai']._find_enemies_in_radius()
        assert len(enemies) == 0

    def test_find_enemies_in_radius_excludes_same_team(self, ai_setup):
        """_find_enemies_in_radius should exclude ships on same team."""
        ai_setup['ship2'].team_id = 0  # Same team
        enemies = ai_setup['ai']._find_enemies_in_radius()
        assert len(enemies) == 0

    def test_find_enemies_in_radius_excludes_specified_ship(self, ai_setup):
        """_find_enemies_in_radius should exclude specified ship."""
        enemies = ai_setup['ai']._find_enemies_in_radius(exclude=ai_setup['ship2'])
        assert len(enemies) == 0

    def test_find_enemies_in_radius_includes_missiles_when_needed(self, ai_setup):
        """_find_enemies_in_radius should include missiles when targeting policy requires."""
        # Set up strategy with missile targeting rules
        ai_setup['ship1'].movement_policy = 'kite_max'

        # Create a mock missile
        class MockMissile:
            def __init__(self):
                self.position = pygame.math.Vector2(500, 0)
                self.type = 'missile'
                self.is_alive = True
                self.team_id = 1  # Enemy team
                self.radius = 10

        missile = MockMissile()
        ai_setup['grid'].insert(missile)

        # Get enemies with include_missiles=True
        enemies = ai_setup['ai']._find_enemies_in_radius(include_missiles=True)
        assert missile in enemies

    def test_score_and_sort_enemies_returns_sorted_list(self, ai_setup):
        """_score_and_sort_enemies should return enemies sorted by score (highest first)."""
        enemies = [ai_setup['ship2']]
        rules = []  # Empty rules = equal scores

        scored = ai_setup['ai']._score_and_sort_enemies(enemies, rules)
        assert len(scored) == 1
        assert scored[0] == ai_setup['ship2']

    def test_score_and_sort_enemies_excludes_negative_infinity(self, ai_setup):
        """_score_and_sort_enemies should exclude targets with -inf score."""
        # Create a third ship
        from game.simulation.entities.ship import Ship
        from game.simulation.components.component import create_component
        registries = ai_setup['registries']

        ship3 = Ship("Enemy2", 2000, 0, (255, 0, 0), team_id=1, ship_class="TestM_4L", registries=registries)
        ship3.add_component(create_component('bridge', registries=registries), LayerType.CORE)
        ship3.add_component(create_component('crew_quarters', registries=registries), LayerType.CORE)
        ship3.add_component(create_component('life_support', registries=registries), LayerType.CORE)
        ship3.recalculate_stats()
        ai_setup['grid'].insert(ship3)

        enemies = [ai_setup['ship2'], ship3]
        rules = []  # Empty rules

        scored = ai_setup['ai']._score_and_sort_enemies(enemies, rules)
        # Both should be included with empty rules (score is 0, not -inf)
        assert len(scored) == 2
