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

    def _setup_priority_weapon(self):
        """Build a beam weapon configured for the priority tests.

        PROJ-323 Task 5.10: shared setup for the split prioritization tests.
        """
        weapon = MagicMock()
        weapon.has_ability.side_effect = lambda a: a in ['BeamWeaponAbility', 'WeaponAbility']
        ab = MagicMock()
        ab.range = 100
        ab.damage = 10
        ab.base_accuracy = 2.0
        ab.accuracy_falloff = 0.001
        weapon.get_ability.return_value = ab
        self.builder.ship.get_total_sensor_score.return_value = 0.0
        return weapon

    # PROJ-323 Task 5.10: replaces single test_prioritization_logic with 3
    # split tests (one per priority class), removing the conditional asserts.

    def test_prioritization_endpoints_are_priority_zero(self):
        """Endpoints (0 and max range) must have priority 0 (always shown)."""
        weapon = self._setup_priority_weapon()
        points = self.viewmodel.get_points_of_interest(weapon, self.builder.ship)
        endpoints = [p for p in points if p['range'] in [0, 100]]
        assert endpoints, "Setup should produce endpoint points"
        assert all(p['priority'] == 0 for p in endpoints)

    def test_prioritization_intermediate_range_points_are_priority_two(self):
        """Intermediate range points have priority 2."""
        weapon = self._setup_priority_weapon()
        points = self.viewmodel.get_points_of_interest(weapon, self.builder.ship)
        intermediate_range = [
            p for p in points if p['type'] == 'range' and p['range'] not in [0, 100]
        ]
        assert intermediate_range, "Setup should produce intermediate range points"
        assert all(p['priority'] == 2 for p in intermediate_range)

    def test_prioritization_accuracy_threshold_points_are_priority_one(self):
        """Accuracy-threshold points (when present) have priority 1.

        The shallow-falloff setup used here (accuracy_falloff=0.001, range=100)
        may not yield any accuracy threshold points; this test only asserts
        the priority invariant when they exist (no false negatives if
        production decides not to emit them).
        """
        weapon = self._setup_priority_weapon()
        points = self.viewmodel.get_points_of_interest(weapon, self.builder.ship)
        accuracy_pts = [p for p in points if p['type'] == 'accuracy']
        # Don't assert presence — the steep-falloff variant lives in
        # test_get_points_of_interest_beam.
        assert all(p['priority'] == 1 for p in accuracy_pts)
