"""Tests for schematic view weapon arc cache key behavior.

Task 12.18: Verify cache keys include weapon stats values (not just ID),
ensuring modified weapons with different stats are cached separately.
"""
import pytest
from unittest.mock import MagicMock, patch
import pygame


@pytest.fixture
def mock_weapon_with_ability():
    """Create a mock weapon with configurable ability stats."""
    def _create(weapon_id: str, weapon_range: float, firing_arc: float, facing: float,
                is_beam: bool = False):
        weapon = MagicMock()
        weapon.id = weapon_id

        # Create ability mock
        ability = MagicMock()
        ability.range = weapon_range
        ability.firing_arc = firing_arc
        ability.facing_angle = facing

        def has_ability(name):
            if name == 'WeaponAbility':
                return True
            if name == 'BeamWeaponAbility':
                return is_beam
            return False

        def get_ability(name):
            if name == 'WeaponAbility':
                return ability
            return None

        weapon.has_ability = has_ability
        weapon.get_ability = get_ability

        return weapon
    return _create


class TestSchematicCacheKey:
    """Verify weapon arc cache key correctly distinguishes weapons."""

    @patch('game.ui.screens.builder.schematic_view.VEHICLE_CLASSES', {})
    def test_same_id_different_range_creates_different_cache_keys(
        self, mock_weapon_with_ability
    ):
        """Two weapons with same ID but different range should have different cache keys."""
        from game.ui.screens.builder.schematic_view import SchematicView

        pygame.init()
        pygame.display.set_mode((100, 100))

        rect = pygame.Rect(0, 0, 200, 200)
        view = SchematicView(rect, MagicMock(), MagicMock())

        # Same weapon ID, different ranges
        weapon1 = mock_weapon_with_ability("laser_mk1", weapon_range=1000, firing_arc=45, facing=0)
        weapon2 = mock_weapon_with_ability("laser_mk1", weapon_range=1500, firing_arc=45, facing=0)

        screen = pygame.Surface((200, 200), pygame.SRCALPHA)

        # Draw both weapons - should create two different cache entries
        view._get_cached_arc(screen.get_size(), weapon1)
        view._get_cached_arc(screen.get_size(), weapon2)

        # Verify we have 2 different cache entries
        assert len(view.arc_cache) == 2

    @patch('game.ui.screens.builder.schematic_view.VEHICLE_CLASSES', {})
    def test_same_id_different_arc_creates_different_cache_keys(
        self, mock_weapon_with_ability
    ):
        """Two weapons with same ID but different arc should have different cache keys."""
        from game.ui.screens.builder.schematic_view import SchematicView

        pygame.init()
        pygame.display.set_mode((100, 100))

        rect = pygame.Rect(0, 0, 200, 200)
        view = SchematicView(rect, MagicMock(), MagicMock())

        # Same weapon ID, different arcs (e.g., one has Extended Arc modifier)
        weapon1 = mock_weapon_with_ability("laser_mk1", weapon_range=1000, firing_arc=45, facing=0)
        weapon2 = mock_weapon_with_ability("laser_mk1", weapon_range=1000, firing_arc=90, facing=0)

        screen = pygame.Surface((200, 200), pygame.SRCALPHA)

        view._get_cached_arc(screen.get_size(), weapon1)
        view._get_cached_arc(screen.get_size(), weapon2)

        assert len(view.arc_cache) == 2

    @patch('game.ui.screens.builder.schematic_view.VEHICLE_CLASSES', {})
    def test_same_id_same_stats_reuses_cache(self, mock_weapon_with_ability):
        """Two weapons with same ID and same stats should reuse cache."""
        from game.ui.screens.builder.schematic_view import SchematicView

        pygame.init()
        pygame.display.set_mode((100, 100))

        rect = pygame.Rect(0, 0, 200, 200)
        view = SchematicView(rect, MagicMock(), MagicMock())

        # Same weapon ID AND same stats - should share cache
        weapon1 = mock_weapon_with_ability("laser_mk1", weapon_range=1000, firing_arc=45, facing=0)
        weapon2 = mock_weapon_with_ability("laser_mk1", weapon_range=1000, firing_arc=45, facing=0)

        screen = pygame.Surface((200, 200), pygame.SRCALPHA)

        view._get_cached_arc(screen.get_size(), weapon1)
        view._get_cached_arc(screen.get_size(), weapon2)

        # Should only have 1 cache entry (reused)
        assert len(view.arc_cache) == 1

    @patch('game.ui.screens.builder.schematic_view.VEHICLE_CLASSES', {})
    def test_different_id_same_stats_creates_different_cache_keys(
        self, mock_weapon_with_ability
    ):
        """Two different weapons with same stats should have different cache keys."""
        from game.ui.screens.builder.schematic_view import SchematicView

        pygame.init()
        pygame.display.set_mode((100, 100))

        rect = pygame.Rect(0, 0, 200, 200)
        view = SchematicView(rect, MagicMock(), MagicMock())

        # Different weapon IDs but same stats
        weapon1 = mock_weapon_with_ability("laser_mk1", weapon_range=1000, firing_arc=45, facing=0)
        weapon2 = mock_weapon_with_ability("laser_mk2", weapon_range=1000, firing_arc=45, facing=0)

        screen = pygame.Surface((200, 200), pygame.SRCALPHA)

        view._get_cached_arc(screen.get_size(), weapon1)
        view._get_cached_arc(screen.get_size(), weapon2)

        # Should have 2 different cache entries (different weapon IDs)
        assert len(view.arc_cache) == 2

    @patch('game.ui.screens.builder.schematic_view.VEHICLE_CLASSES', {})
    def test_invalidate_cache_clears_all_entries(self, mock_weapon_with_ability):
        """invalidate_cache() should clear all cached arc surfaces."""
        from game.ui.screens.builder.schematic_view import SchematicView

        pygame.init()
        pygame.display.set_mode((100, 100))

        rect = pygame.Rect(0, 0, 200, 200)
        view = SchematicView(rect, MagicMock(), MagicMock())

        weapon = mock_weapon_with_ability("laser_mk1", weapon_range=1000, firing_arc=45, facing=0)
        screen = pygame.Surface((200, 200), pygame.SRCALPHA)

        view._get_cached_arc(screen.get_size(), weapon)
        assert len(view.arc_cache) == 1

        view.invalidate_cache()
        assert len(view.arc_cache) == 0
