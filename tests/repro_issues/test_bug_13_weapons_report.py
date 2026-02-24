"""
Bug 13 Regression Tests - Weapons Report Panel

Tests for PROJ-172 MVVM refactoring of weapons panel.
Now tests the ViewModel directly instead of panel internal methods.
"""
import os
import pygame
import pygame_gui
import pytest
from unittest.mock import MagicMock, patch

from game.ui.screens.builder.weapons_panel import WeaponsReportPanel
from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel
from game.ui.screens.builder.weapons_renderer import WeaponsRenderer
from game.ui.screens.builder.event_bus import EventBus


class TestBug13Fix:
    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        self.surface = pygame.display.set_mode((800, 600))
        self.manager = pygame_gui.UIManager((800, 600))

        self.builder = MagicMock()
        self.builder.ship = MagicMock()
        self.sprite_mgr = MagicMock()
        self.rect = pygame.Rect(0, 0, 800, 600)

        # Create ViewModel directly for testing calculations
        self.event_bus = EventBus()
        self.viewmodel = WeaponsViewModel(self.event_bus)

        # Also create panel for integration tests
        self.panel = WeaponsReportPanel(self.builder, self.manager, self.rect, self.sprite_mgr)

        yield

        # CRITICAL: Clean up ALL mocks first (prevents mock object pollution)
        patch.stopall()

        pygame.quit()
        # fresh_registries fixture handles registry isolation - no manual clear needed

    def test_unified_drawing_structure(self):
        """Verify MVVM architecture is in place."""
        # Panel should use ViewModel and Renderer
        assert hasattr(self.panel, '_viewmodel')
        assert hasattr(self.panel, '_renderer')
        # Old internal methods should not exist on panel
        assert not hasattr(self.panel, '_draw_beam_weapon_bar')
        assert not hasattr(self.panel, '_draw_projectile_weapon_bar')

    def test_get_points_of_interest_projectile(self):
        """Verify points of interest for a projectile weapon."""
        weapon = MagicMock()
        # Mocking has_ability for ProjectileWeaponAbility
        weapon.has_ability.side_effect = lambda a: a == 'ProjectileWeaponAbility' or a == 'WeaponAbility'

        ab = MagicMock()
        ab.range = 500
        ab.damage = 50
        weapon.get_ability.return_value = ab

        # Use ViewModel directly
        points = self.viewmodel.get_points_of_interest(weapon, self.builder.ship)

        # Should have 6 points from INTEREST_POINTS_RANGE (0.0 to 1.0)
        assert len(points) == 6
        assert points[0]['range'] == 0
        assert points[0]['priority'] == 0
        assert points[-1]['range'] == 500
        assert points[-1]['priority'] == 0
        assert points[1]['range'] == 100  # 20%
        assert points[1]['priority'] == 2

    def test_get_points_of_interest_beam(self):
        """Verify points of interest for a beam weapon including accuracy thresholds."""
        weapon = MagicMock()
        weapon.has_ability.side_effect = lambda a: a in ['BeamWeaponAbility', 'WeaponAbility']

        ab = MagicMock()
        ab.range = 1000
        ab.damage = 100
        ab.base_accuracy = 2.0
        ab.accuracy_falloff = 0.005  # Steep falloff for testing thresholds
        weapon.get_ability.return_value = ab

        # Mock ship to return baseline sensor score
        self.builder.ship.get_total_sensor_score.return_value = 0.0

        points = self.viewmodel.get_points_of_interest(weapon, self.builder.ship)

        # Verify we have both types
        has_acc = any(p['type'] == 'accuracy' for p in points)
        has_range = any(p['type'] == 'range' for p in points)

        assert has_acc, "Should have accuracy based points for beams"
        assert has_range, "Should have range percentage points"

        # Check order
        ranges = [p['range'] for p in points]
        assert ranges == sorted(ranges), "Points should be sorted by range"

    def test_prioritization_logic(self):
        """Verify that high priority points (0 and Max range) are kept even if crowded."""
        weapon = MagicMock()
        weapon.has_ability.side_effect = lambda a: a in ['BeamWeaponAbility', 'WeaponAbility']
        ab = MagicMock()
        ab.range = 100
        ab.damage = 10
        ab.base_accuracy = 2.0
        ab.accuracy_falloff = 0.001
        weapon.get_ability.return_value = ab

        # Mock ship to return baseline sensor score
        self.builder.ship.get_total_sensor_score.return_value = 0.0

        # Test that ViewModel produces points with correct priorities
        points = self.viewmodel.get_points_of_interest(weapon, self.builder.ship)

        # Endpoints should have priority 0 (must show)
        endpoints = [p for p in points if p['range'] in [0, 100]]
        assert all(p['priority'] == 0 for p in endpoints), "Endpoints should have priority 0"

        # Intermediate range points should have priority 2
        intermediate_range = [p for p in points if p['type'] == 'range' and p['range'] not in [0, 100]]
        if intermediate_range:
            assert all(p['priority'] == 2 for p in intermediate_range), "Intermediate range points should have priority 2"

        # Accuracy threshold points should have priority 1
        accuracy_pts = [p for p in points if p['type'] == 'accuracy']
        if accuracy_pts:
            assert all(p['priority'] == 1 for p in accuracy_pts), "Accuracy points should have priority 1"
