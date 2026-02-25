"""
Tests for AI Controller capabilities cache optimization.

PROJ-49 Phase 6: O(n^2) Targeting Optimization

This module tests the _build_capabilities_cache helper and its integration
with _score_and_sort_enemies to batch compute expensive capability checks.
"""
import pytest
import pygame
from unittest.mock import MagicMock

from game.ai.controller import AIController
from game.ai.target_evaluator import TargetEvaluator
from game.engine.spatial import SpatialGrid


@pytest.fixture(autouse=True)
def pygame_init():
    """Initialize pygame for Vector2 usage."""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def mock_ship():
    """Create a mock ship for the AI controller."""
    ship = MagicMock()
    ship.id = 'test_ship'
    ship.position = pygame.math.Vector2(0, 0)
    ship.get_position = MagicMock(return_value=pygame.math.Vector2(0, 0))
    ship.get_team_id = MagicMock(return_value=0)
    ship.get_ai_strategy = MagicMock(return_value='standard_ranged')
    ship.get_formation_members = MagicMock(return_value=[])
    ship.is_in_formation = MagicMock(return_value=False)
    ship.get_formation_master = MagicMock(return_value=None)
    ship.get_max_targets = MagicMock(return_value=1)
    ship.get_current_target = MagicMock(return_value=None)
    ship.get_components_by_ability = MagicMock(return_value=[])
    ship.is_alive = MagicMock(return_value=True)
    return ship


@pytest.fixture
def mock_grid():
    """Create a mock spatial grid."""
    grid = MagicMock(spec=SpatialGrid)
    grid.query_radius = MagicMock(return_value=[])
    return grid


@pytest.fixture
def ai_controller(mock_ship, mock_grid):
    """Create an AI controller with mocked dependencies."""
    return AIController(mock_ship, mock_grid, enemy_team_id=1)


def create_mock_enemy(enemy_id, has_weapons=True, has_pdc=False):
    """Helper to create mock enemy ships."""
    enemy = MagicMock()
    # PROJ-192: Ship uses .name as identifier, not .id
    enemy.name = enemy_id
    enemy.position = pygame.math.Vector2(100, 0)
    enemy.is_alive = True
    enemy.team_id = 1

    # Mock weapon components
    if has_weapons:
        weapon = MagicMock()
        weapon.has_ability = MagicMock(return_value=has_pdc)
        enemy.get_components_by_ability = MagicMock(return_value=[weapon])
    else:
        enemy.get_components_by_ability = MagicMock(return_value=[])

    return enemy


class TestBuildCapabilitiesCache:
    """Tests for _build_capabilities_cache helper method."""

    def test_build_capabilities_cache_exists(self, ai_controller):
        """AIController should have _build_capabilities_cache method."""
        assert hasattr(ai_controller, '_build_capabilities_cache')
        assert callable(ai_controller._build_capabilities_cache)

    def test_build_capabilities_cache_returns_dict(self, ai_controller):
        """_build_capabilities_cache should return a dictionary."""
        enemies = [create_mock_enemy('enemy_1')]
        cache = ai_controller._build_capabilities_cache(enemies)

        assert isinstance(cache, dict)

    def test_build_capabilities_cache_includes_all_ships(self, ai_controller):
        """Cache should include entry for each ship."""
        enemies = [
            create_mock_enemy('enemy_1'),
            create_mock_enemy('enemy_2'),
            create_mock_enemy('enemy_3'),
        ]

        cache = ai_controller._build_capabilities_cache(enemies)

        assert 'enemy_1' in cache
        assert 'enemy_2' in cache
        assert 'enemy_3' in cache

    def test_build_capabilities_cache_has_weapons_true(self, ai_controller):
        """Cache should correctly detect armed ships."""
        enemy = create_mock_enemy('armed', has_weapons=True)

        cache = ai_controller._build_capabilities_cache([enemy])

        assert cache['armed']['has_weapons'] is True
        assert len(cache['armed']['weapon_components']) > 0

    def test_build_capabilities_cache_has_weapons_false(self, ai_controller):
        """Cache should correctly detect unarmed ships."""
        enemy = create_mock_enemy('unarmed', has_weapons=False)

        cache = ai_controller._build_capabilities_cache([enemy])

        assert cache['unarmed']['has_weapons'] is False
        assert len(cache['unarmed']['weapon_components']) == 0

    def test_build_capabilities_cache_has_pdc_true(self, ai_controller):
        """Cache should correctly detect ships with PDC."""
        enemy = create_mock_enemy('pdc_ship', has_weapons=True, has_pdc=True)

        cache = ai_controller._build_capabilities_cache([enemy])

        assert cache['pdc_ship']['has_pdc'] is True
        assert len(cache['pdc_ship']['pdc_components']) > 0

    def test_build_capabilities_cache_has_pdc_false(self, ai_controller):
        """Cache should correctly detect ships without PDC."""
        enemy = create_mock_enemy('no_pdc', has_weapons=True, has_pdc=False)

        cache = ai_controller._build_capabilities_cache([enemy])

        assert cache['no_pdc']['has_pdc'] is False
        assert len(cache['no_pdc']['pdc_components']) == 0

    def test_build_capabilities_cache_structure(self, ai_controller):
        """Cache entry should have correct structure."""
        enemy = create_mock_enemy('test', has_weapons=True, has_pdc=False)

        cache = ai_controller._build_capabilities_cache([enemy])
        entry = cache['test']

        assert 'has_weapons' in entry
        assert 'weapon_components' in entry
        assert 'has_pdc' in entry
        assert 'pdc_components' in entry
        assert isinstance(entry['has_weapons'], bool)
        assert isinstance(entry['weapon_components'], list)
        assert isinstance(entry['has_pdc'], bool)
        assert isinstance(entry['pdc_components'], list)


class TestScoreAndSortEnemiesWithCache:
    """Tests for _score_and_sort_enemies using capabilities cache."""

    def test_score_and_sort_uses_capabilities_cache(self, ai_controller):
        """_score_and_sort_enemies should use capabilities cache when evaluating."""
        enemy = create_mock_enemy('enemy_1')

        # Rules that use has_weapons check
        rules = [{'type': 'has_weapons', 'weight': 100}]

        # Get sorted enemies - this should build cache internally
        scored = ai_controller._score_and_sort_enemies([enemy], rules)

        assert len(scored) == 1
        assert scored[0] == enemy

    def test_score_and_sort_caches_reduces_component_lookups(self, ai_controller):
        """With caching, component lookups should happen once per ship, not per rule evaluation."""
        # Create multiple enemies
        enemies = [
            create_mock_enemy(f'enemy_{i}')
            for i in range(3)
        ]

        rules = [{'type': 'has_weapons', 'weight': 100}]

        # Reset mock call counts
        for e in enemies:
            e.get_components_by_ability.reset_mock()

        # Evaluate all enemies
        scored = ai_controller._score_and_sort_enemies(enemies, rules)

        # Each enemy's get_components_by_ability should be called at most once per ability type
        # during cache building, not during rule evaluation
        for e in enemies:
            # At most 1 call for WeaponAbility (could be 0 if no has_weapons rule evaluated)
            # The key is that it's NOT called multiple times per target
            call_count = e.get_components_by_ability.call_count
            assert call_count <= 1, f"Expected <= 1 call, got {call_count}"


class TestIntegrationWithTargetEvaluator:
    """Integration tests verifying cache flows correctly to TargetEvaluator."""

    def test_capabilities_cache_passed_to_evaluator(self, ai_controller, mock_ship):
        """Verify that built cache is passed to TargetEvaluator.evaluate."""
        enemy = create_mock_enemy('enemy_1')

        # Pre-build the cache to verify structure
        cache = ai_controller._build_capabilities_cache([enemy])

        # The cache should have correct structure for TargetEvaluator
        assert 'enemy_1' in cache
        assert 'has_weapons' in cache['enemy_1']

        # TargetEvaluator should accept this cache
        rules = [{'type': 'has_weapons', 'weight': 100}]
        score = TargetEvaluator.evaluate(
            mock_ship, enemy, rules,
            ship_capabilities_cache=cache
        )

        assert isinstance(score, (int, float))
        assert score == 100  # Armed ship with weight=100
