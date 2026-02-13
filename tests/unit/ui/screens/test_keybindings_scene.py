"""Tests for KeybindingsScene (PROJ-71 Phase 4).

Verifies the full-screen keybinding editor scene:
- Scene creation with IScene protocol compliance
- Action list display with groups
- Key capture workflow
- Conflict detection
- Save/Reset/Close operations

Event Testing Pattern Notes:
- Key capture tests use MagicMock events for _handle_key_capture() since the method
  only accesses .type, .key, and .mod attributes. This is intentional as these
  internal methods don't require full pygame event semantics.
"""
import os
import json
import pytest
from unittest.mock import MagicMock, patch, call
from pathlib import Path

import pygame
import pygame_gui

from game.core.input_actions import InputAction, KeyBinding, ACTION_GROUPS, ACTION_DISPLAY_NAMES
from game.ui.services.input_mapper import InputMapper
from game.core.paths import Paths


@pytest.fixture
def mapper_with_defaults():
    """Create an InputMapper loaded with default keybindings."""
    mapper = InputMapper()
    mapper.load(Paths.DEFAULT_KEYBINDINGS_FILE)
    return mapper


@pytest.fixture
def close_callback():
    """Mock callback for scene close."""
    return MagicMock()


@pytest.fixture
def scene(mapper_with_defaults, close_callback):
    """Create a KeybindingsScene instance for testing."""
    from game.ui.screens.keybindings_scene import KeybindingsScene
    return KeybindingsScene(1280, 800, mapper_with_defaults, close_callback)


class TestSceneCreation:
    """KeybindingsScene should create without errors and implement IScene."""

    def test_scene_creates_without_error(self, mapper_with_defaults, close_callback):
        """Scene instantiation should not raise."""
        from game.ui.screens.keybindings_scene import KeybindingsScene
        scene = KeybindingsScene(1280, 800, mapper_with_defaults, close_callback)
        assert scene is not None

    def test_scene_has_iscene_methods(self, scene):
        """Scene must implement all IScene protocol methods."""
        assert hasattr(scene, 'handle_event')
        assert hasattr(scene, 'update')
        assert hasattr(scene, 'draw')
        assert hasattr(scene, 'handle_resize')
        assert callable(scene.handle_event)
        assert callable(scene.update)
        assert callable(scene.draw)
        assert callable(scene.handle_resize)

    def test_scene_has_ui_manager(self, scene):
        """Scene should create a pygame_gui UIManager."""
        assert scene._ui_manager is not None

    def test_scene_stores_dimensions(self, scene):
        """Scene should store width and height."""
        assert scene._width == 1280
        assert scene._height == 800

    def test_scene_stores_mapper(self, scene, mapper_with_defaults):
        """Scene should store reference to InputMapper."""
        assert scene._mapper is mapper_with_defaults

    def test_scene_stores_close_callback(self, scene, close_callback):
        """Scene should store the on_close callback."""
        assert scene._on_close_callback is close_callback


class TestActionListDisplay:
    """Scene should display all actions grouped by context."""

    def test_all_action_groups_represented(self, scene):
        """Every group from ACTION_GROUPS should be in the scene's row data."""
        for group_name in ACTION_GROUPS:
            assert group_name in scene._group_rows, f"Missing group: {group_name}"

    def test_all_actions_represented(self, scene):
        """Every action from ACTION_GROUPS should have a row."""
        for group_name, actions in ACTION_GROUPS.items():
            for action in actions:
                assert action in scene._action_rows, f"Missing action: {action}"

    def test_binding_display_text_matches_mapper(self, scene, mapper_with_defaults):
        """Each action row's displayed binding should match mapper state."""
        for action, row_data in scene._action_rows.items():
            expected = mapper_with_defaults.get_display_text(action)
            actual = row_data["binding_text"]
            if not expected:
                assert actual == "Unbound", f"{action}: expected 'Unbound', got '{actual}'"
            else:
                assert actual == expected, f"{action}: expected '{expected}', got '{actual}'"


class TestKeyCaptureWorkflow:
    """Key capture mode: click Rebind -> press key -> binding updates."""

    def test_starts_not_capturing(self, scene):
        """Scene should not be in capture mode initially."""
        assert scene._capturing_action is None

    def test_enter_capture_mode(self, scene):
        """Calling start_capture sets the capturing action."""
        scene._start_capture(InputAction.FLEET_MOVE)
        assert scene._capturing_action == InputAction.FLEET_MOVE

    def test_escape_cancels_capture(self, scene):
        """Pressing ESC during capture should cancel."""
        scene._start_capture(InputAction.FLEET_MOVE)
        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_ESCAPE
        event.mod = 0
        scene._handle_key_capture(event)
        assert scene._capturing_action is None

    def test_modifier_only_ignored(self, scene):
        """Pressing only a modifier key should NOT complete capture."""
        scene._start_capture(InputAction.FLEET_MOVE)
        for key in [pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_LCTRL,
                     pygame.K_RCTRL, pygame.K_LALT, pygame.K_RALT]:
            event = MagicMock()
            event.type = pygame.KEYDOWN
            event.key = key
            event.mod = 0
            scene._handle_key_capture(event)
            assert scene._capturing_action == InputAction.FLEET_MOVE

    def test_capture_creates_binding(self, scene, mapper_with_defaults):
        """Pressing a non-modifier key during capture creates a binding."""
        scene._start_capture(InputAction.DETAIL_PANEL_BUILD)
        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_b
        event.mod = 0
        # Mock the conflict check to return no conflicts
        with patch.object(mapper_with_defaults, 'get_conflicts', return_value=[]):
            scene._handle_key_capture(event)
        # Capture complete
        assert scene._capturing_action is None
        # Binding was set on mapper
        binding = mapper_with_defaults.get_binding(InputAction.DETAIL_PANEL_BUILD)
        assert binding is not None
        assert binding.key == "K_b"

    def test_capture_with_modifier(self, scene, mapper_with_defaults):
        """Pressing Ctrl+K during capture creates binding with modifier."""
        scene._start_capture(InputAction.DETAIL_PANEL_BUILD)
        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_k
        event.mod = pygame.KMOD_CTRL
        with patch.object(mapper_with_defaults, 'get_conflicts', return_value=[]):
            scene._handle_key_capture(event)
        binding = mapper_with_defaults.get_binding(InputAction.DETAIL_PANEL_BUILD)
        assert binding is not None
        assert binding.key == "K_k"
        assert "ctrl" in binding.modifiers

    def test_has_unsaved_changes_after_capture(self, scene, mapper_with_defaults):
        """Scene should track unsaved changes after rebinding."""
        assert not scene._has_unsaved_changes
        scene._start_capture(InputAction.DETAIL_PANEL_BUILD)
        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_b
        event.mod = 0
        with patch.object(mapper_with_defaults, 'get_conflicts', return_value=[]):
            scene._handle_key_capture(event)
        assert scene._has_unsaved_changes


class TestConflictDetection:
    """Conflict detection should trigger when binding overlaps."""

    def test_conflict_triggers_dialog(self, scene, mapper_with_defaults):
        """When conflicts exist, a pending conflict should be stored."""
        scene._start_capture(InputAction.DETAIL_PANEL_BUILD)
        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_m  # M is already bound to FLEET_MOVE
        event.mod = 0
        # Return a conflict
        with patch.object(mapper_with_defaults, 'get_conflicts',
                          return_value=[InputAction.FLEET_MOVE]):
            scene._handle_key_capture(event)
        # Should have a pending conflict instead of applying immediately
        assert scene._pending_conflict is not None
        assert scene._pending_conflict["action"] == InputAction.DETAIL_PANEL_BUILD


class TestSaveResetClose:
    """Save, Reset, and Close button workflows."""

    def test_save_and_close(self, scene, mapper_with_defaults, close_callback, tmp_path):
        """Save & Close should persist overrides and call callback."""
        save_path = str(tmp_path / "keybindings.json")
        with patch.object(mapper_with_defaults, 'save_user_overrides', return_value=True) as mock_save:
            scene._on_save_and_close()
        mock_save.assert_called_once()
        close_callback.assert_called_once()

    def test_reset_all(self, scene, mapper_with_defaults):
        """Reset All should call mapper.reset_to_defaults and refresh display."""
        with patch.object(mapper_with_defaults, 'reset_to_defaults') as mock_reset:
            scene._on_reset_confirmed()
        mock_reset.assert_called_once()
        assert not scene._has_unsaved_changes

    def test_close_no_changes_calls_callback(self, scene, close_callback):
        """Close with no unsaved changes calls callback directly."""
        scene._has_unsaved_changes = False
        scene._on_close()
        close_callback.assert_called_once()

    def test_close_with_changes_sets_pending_discard(self, scene, close_callback):
        """Close with unsaved changes should set pending discard flag."""
        scene._has_unsaved_changes = True
        scene._on_close()
        # Should not have called callback yet (needs confirmation)
        close_callback.assert_not_called()
        assert scene._pending_discard

    def test_reset_single_action(self, scene, mapper_with_defaults):
        """Resetting a single action restores its default binding."""
        # Change a binding first
        original = mapper_with_defaults.get_binding(InputAction.FLEET_MOVE)
        mapper_with_defaults.set_binding(InputAction.FLEET_MOVE,
                                          KeyBinding(key="K_x", modifiers=frozenset()))
        scene._has_unsaved_changes = True

        # Reset just that action
        scene._reset_single_action(InputAction.FLEET_MOVE)

        # Binding should be restored to default
        restored = mapper_with_defaults.get_binding(InputAction.FLEET_MOVE)
        assert restored == original
        assert scene._has_unsaved_changes  # Still has unsaved changes flag


class TestHandleResize:
    """Scene should handle window resize."""

    def test_handle_resize_updates_dimensions(self, scene):
        """handle_resize should update stored width and height."""
        scene.handle_resize(1920, 1080)
        assert scene._width == 1920
        assert scene._height == 1080


class TestUpdateAndDraw:
    """Scene update and draw should not raise errors."""

    def test_update_does_not_raise(self, scene):
        """update() should not raise."""
        scene.update(0.016)

    def test_draw_does_not_raise(self, scene):
        """draw() should not raise on a valid surface."""
        surface = pygame.Surface((1280, 800))
        scene.draw(surface)


class TestAppIntegration:
    """app.py should have start_keybindings and return methods."""

    def test_game_state_keybindings_exists(self):
        """GameState.KEYBINDINGS should exist."""
        from game.core.constants import GameState
        assert hasattr(GameState, 'KEYBINDINGS')
        assert GameState.KEYBINDINGS == 10
