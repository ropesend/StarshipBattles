import pytest
from unittest.mock import MagicMock
import pygame

from game.ai import TargetEvaluator, AIController
from game.ai.interfaces.controllable import ShipControllableAdapter
from game.core.constants import AttackType


@pytest.fixture
def pygame_init():
    """Initialize pygame for tests that need it."""
    if not pygame.get_init():
        pygame.init()
    yield
    # Note: Don't quit pygame here - conftest manages session lifecycle


@pytest.fixture
def ship_setup(pygame_init):
    """Create a basic ship and targets for testing."""
    ship = MagicMock()
    ship.position = pygame.math.Vector2(0, 0)
    ship.angle = 0
    ship.team_id = 0

    target_near = MagicMock()
    target_near.position = pygame.math.Vector2(100, 0)
    target_near.mass = 100
    target_near.velocity = pygame.math.Vector2(0, 0)

    target_far = MagicMock()
    target_far.position = pygame.math.Vector2(1000, 0)
    target_far.mass = 500

    return ship, target_near, target_far


class TestTargetingRules:

    def test_rule_nearest(self, ship_setup):
        """Test 'nearest' rule scores closer targets higher."""
        ship, target_near, target_far = ship_setup
        # weight=1 => val = -dist
        rule = {'type': 'nearest', 'weight': 1}
        rules = [rule]

        score_near = TargetEvaluator.evaluate(ship, target_near, rules)
        score_far = TargetEvaluator.evaluate(ship, target_far, rules)

        # Near (-100) > Far (-1000)
        assert score_near > score_far

    def test_rule_most_damaged(self, pygame_init):
        """Test 'most_damaged' rule scores lower HP% higher."""
        ship = MagicMock()
        ship.position = pygame.math.Vector2(0, 0)
        ship.angle = 0
        ship.team_id = 0

        # Using a rule with weight > 0
        rule = {'type': 'most_damaged', 'weight': 1}
        rules = [rule]

        # Mock components with current_hp and max_hp attributes
        # TargetEvaluator._default_get_hp_percent calls get_all_components()
        # and sums current_hp / max_hp across all components

        # Target 1: 10/100 HP (10%)
        t1 = MagicMock()
        comp1 = MagicMock()
        comp1.max_hp = 100
        comp1.current_hp = 10
        t1.get_all_components.return_value = [comp1]

        # Target 2: 90/100 HP (90%)
        t2 = MagicMock()
        comp2 = MagicMock()
        comp2.max_hp = 100
        comp2.current_hp = 90
        t2.get_all_components.return_value = [comp2]

        # Rule: val = -hp_pct * weight * 100
        # T1 Score = -0.1 * 1 * 100 = -10
        # T2 Score = -0.9 * 1 * 100 = -90
        # T1 (Most damaged) should have higher score (-10 > -90)

        score_1 = TargetEvaluator.evaluate(ship, t1, rules)
        score_2 = TargetEvaluator.evaluate(ship, t2, rules)

        assert score_1 > score_2

    def test_rule_pdc_arc(self, pygame_init):
        """Test 'pdc_arc' rule filters by angle and type."""
        ship = MagicMock()
        ship.position = pygame.math.Vector2(0, 0)
        ship.angle = 0
        ship.team_id = 0

        # Rule expects target type to be 'missile'
        rule = {'type': 'pdc_arc', 'weight': 1, 'required': True}
        rules = [rule]

        missile = MagicMock()
        missile.type = AttackType.MISSILE
        missile.position = pygame.math.Vector2(100, 0)  # Directly ahead

        ship_not_missile = MagicMock()
        ship_not_missile.type = 'Ship'
        ship_not_missile.position = pygame.math.Vector2(100, 0)

        # Case 1: Non-missile target passes or is ignored?
        # Logic: if is_missile check...
        # "if is_missile: check arc... else: pass"
        # So non-missile gets score 0 (neutral).

        score_ship = TargetEvaluator.evaluate(ship, ship_not_missile, rules)
        assert score_ship == 0

        # Case 2: Missile in arc. Need to mock ship's PDC ability logic.
        # TargetEvaluator calls AIController._stat_is_in_pdc_arc(ship, target)
        # We need to set up ship with a mock weapon in arc.

        # Setup Ship with PDC Weapon
        ship.angle = 0

        # Mock Component
        comp = MagicMock()
        comp.has_ability.side_effect = lambda x: True if x == 'WeaponAbility' else False
        comp.is_active = True
        comp.has_pdc_ability.return_value = True

        # Mock WeaponAbility
        ab = MagicMock()
        ab.range = 500
        ab.facing_angle = 0
        ab.firing_arc = 90
        comp.get_ability.return_value = ab

        # Mock the Ship helper method to return our component
        ship.get_components_by_ability = MagicMock(return_value=[comp])

        # Now Check Missile (In Arc)
        score_missile = TargetEvaluator.evaluate(ship, missile, rules)
        assert score_missile > 0  # Should get weight val

        # Case 3: Missile Out of Arc (Behind)
        missile.position = pygame.math.Vector2(-100, 0)
        score_missile_out = TargetEvaluator.evaluate(ship, missile, rules)
        assert score_missile_out == -float('inf')  # Required rule failed

    def test_rule_required_flag(self, pygame_init):
        """Test that failure of a required rule returns -inf."""
        ship = MagicMock()
        ship.position = pygame.math.Vector2(0, 0)
        ship.angle = 0
        ship.team_id = 0

        # Example: 'has_weapons'
        rule = {'type': 'has_weapons', 'required': True, 'weight': 1}
        rules = [rule]

        # Target with no weapons
        target = MagicMock()
        # Mocking recursive attribute access for components... tricky.
        # TargetEvaluator iterates: for layer in getattr(candidate, 'layers'...
        target.layers = {}  # No components

        score = TargetEvaluator.evaluate(ship, target, rules)
        assert score == -float('inf')

    def test_secondary_targeting(self, pygame_init):
        """Test secondary targeting logic."""
        ship = MagicMock()
        ship.position = pygame.math.Vector2(0, 0)
        ship.angle = 0
        ship.team_id = 0

        # Mock AIController partial for test
        # We don't want the full grid query, just the filtering logic.
        # But find_secondary_targets is an instance method that calls grid.
        # We can construct a controller with a mock grid.

        mock_grid = MagicMock()
        # Use ShipControllableAdapter to match production behavior (battle_engine.py)
        controller = AIController(ShipControllableAdapter(ship), mock_grid, enemy_team_id=1)

        t1 = MagicMock()
        t1.team_id = 1
        t1.is_alive = True
        t1.name = "t1"
        t2 = MagicMock()
        t2.team_id = 1
        t2.is_alive = True
        t2.name = "t2"

        ship.current_target = t1
        ship.max_targets = 2

        mock_grid.query_radius.return_value = [ship, t1, t2]

        # Strategy mock logic is complex (get_resolved_strategy).
        # We can mock get_resolved_strategy on the controller instance.
        controller.get_resolved_strategy = MagicMock(return_value={
            'targeting': {'rules': [{'type': 'nearest', 'weight': 1}]}
        })

        # Helper evaluator mock to avoid layout issues?
        # Or just ensure targets have positions so evaluators work.
        t1.position = pygame.math.Vector2(100, 0)
        t2.position = pygame.math.Vector2(200, 0)
        ship.layers = {}
        t1.layers = {}
        t2.layers = {}

        secondary = controller.find_secondary_targets()

        # Should return [t2] because t1 is current_target
        assert len(secondary) == 1
        assert secondary[0] == t2
