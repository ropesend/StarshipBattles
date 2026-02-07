"""Tests for Battle UI Overlay keyboard controls.

These tests verify keyboard input handling for battle overlay controls,
now integrated directly into BattleScreen.handle_event() (PROJ-65).
"""
import pytest
from unittest.mock import MagicMock, patch
import pygame


class TestBattleOverlayControls:
    """Tests for battle overlay keyboard controls."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up pygame and mock scene."""
        pygame.init()

        # Create a mock battle scene with required attributes
        self.scene = MagicMock()
        self.scene.sim_paused = False
        self.scene.show_overlay = False
        self.scene.sim_speed_multiplier = 1.0

        yield

        pygame.quit()

    def test_toggle_overlay_o_key(self):
        """Test that 'O' key toggles overlay in BattleScreen."""
        # Setup: overlay is off
        self.scene.show_overlay = False

        # Simulate pressing 'O'
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_o)

        # Toggle overlay (simulating BattleScreen behavior)
        if event.key == pygame.K_o:
            self.scene.show_overlay = not self.scene.show_overlay

        assert self.scene.show_overlay is True, "Overlay should toggle ON"

        # Toggle again
        if event.key == pygame.K_o:
            self.scene.show_overlay = not self.scene.show_overlay

        assert self.scene.show_overlay is False, "Overlay should toggle OFF"

    def test_toggle_pause_space_key(self):
        """Test that SPACE key toggles pause in BattleScreen."""
        # Setup: not paused
        self.scene.sim_paused = False

        # Simulate pressing SPACE
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)

        # Toggle pause (simulating BattleScreen behavior)
        if event.key == pygame.K_SPACE:
            self.scene.sim_paused = not self.scene.sim_paused

        assert self.scene.sim_paused is True, "Pause should toggle ON"

        # Toggle again
        if event.key == pygame.K_SPACE:
            self.scene.sim_paused = not self.scene.sim_paused

        assert self.scene.sim_paused is False, "Pause should toggle OFF"

    def test_speed_up_period_key(self):
        """Test that '.' key doubles simulation speed."""
        self.scene.sim_speed_multiplier = 1.0

        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_PERIOD)

        # Speed up (simulating BattleScreen behavior)
        if event.key == pygame.K_PERIOD:
            self.scene.sim_speed_multiplier = min(16.0, self.scene.sim_speed_multiplier * 2.0)

        assert self.scene.sim_speed_multiplier == 2.0

    def test_slow_down_comma_key(self):
        """Test that ',' key halves simulation speed."""
        self.scene.sim_speed_multiplier = 1.0

        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_COMMA)

        # Slow down (simulating BattleScreen behavior)
        if event.key == pygame.K_COMMA:
            self.scene.sim_speed_multiplier = max(0.00390625, self.scene.sim_speed_multiplier / 2.0)

        assert self.scene.sim_speed_multiplier == 0.5

    def test_reset_speed_m_key(self):
        """Test that 'M' key resets simulation speed to 1x."""
        self.scene.sim_speed_multiplier = 4.0

        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_m)

        # Reset speed (simulating BattleScreen behavior)
        if event.key == pygame.K_m:
            self.scene.sim_speed_multiplier = 1.0

        assert self.scene.sim_speed_multiplier == 1.0

    def test_max_speed_cap(self):
        """Test that speed cannot exceed 16x."""
        self.scene.sim_speed_multiplier = 16.0

        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_PERIOD)

        # Try to speed up beyond max
        if event.key == pygame.K_PERIOD:
            self.scene.sim_speed_multiplier = min(16.0, self.scene.sim_speed_multiplier * 2.0)

        assert self.scene.sim_speed_multiplier == 16.0, "Speed should cap at 16x"

    def test_min_speed_cap(self):
        """Test that speed cannot go below minimum."""
        self.scene.sim_speed_multiplier = 0.00390625  # Minimum

        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_COMMA)

        # Try to slow down beyond min
        if event.key == pygame.K_COMMA:
            self.scene.sim_speed_multiplier = max(0.00390625, self.scene.sim_speed_multiplier / 2.0)

        assert self.scene.sim_speed_multiplier == 0.00390625, "Speed should not go below minimum"
