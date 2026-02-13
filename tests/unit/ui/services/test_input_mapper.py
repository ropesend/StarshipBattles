"""Tests for InputMapper service."""
import json
import os
from unittest.mock import MagicMock

import pygame
import pytest

from game.core.input_actions import InputAction, KeyBinding
from game.ui.services.input_mapper import InputMapper
from game.core.paths import Paths


@pytest.fixture
def mapper():
    """Create a fresh InputMapper loaded with defaults."""
    m = InputMapper()
    m.load(defaults_path=Paths.DEFAULT_KEYBINDINGS_FILE)
    return m


@pytest.fixture
def make_keydown():
    """Factory for creating mock KEYDOWN events."""
    def _make(key: int, mod: int = 0):
        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = key
        event.mod = mod
        return event
    return _make


class TestInputMapperLoad:
    """Tests for loading bindings."""

    def test_load_defaults(self, mapper):
        """Loading defaults file populates bindings."""
        binding = mapper.get_binding(InputAction.FLEET_MOVE)
        assert binding is not None
        assert binding.key == "K_m"

    def test_load_nonexistent_defaults_gives_empty(self):
        """Loading a missing defaults file gives no bindings."""
        m = InputMapper()
        m.load(defaults_path="/nonexistent/path.json")
        assert m.get_binding(InputAction.FLEET_MOVE) is None

    def test_load_user_overrides(self, mapper, tmp_path):
        """User overrides replace specific default bindings."""
        overrides_file = tmp_path / "keybindings.json"
        overrides_file.write_text(json.dumps({
            "bindings": {
                "fleet.move": {"key": "K_n", "modifiers": []}
            }
        }))
        mapper.load(
            defaults_path=Paths.DEFAULT_KEYBINDINGS_FILE,
            overrides_path=str(overrides_file),
        )
        binding = mapper.get_binding(InputAction.FLEET_MOVE)
        assert binding is not None
        assert binding.key == "K_n"

    def test_override_preserves_other_defaults(self, tmp_path):
        """Overriding one action leaves others at defaults."""
        overrides_file = tmp_path / "keybindings.json"
        overrides_file.write_text(json.dumps({
            "bindings": {
                "fleet.move": {"key": "K_n", "modifiers": []}
            }
        }))
        m = InputMapper()
        m.load(
            defaults_path=Paths.DEFAULT_KEYBINDINGS_FILE,
            overrides_path=str(overrides_file),
        )
        # fleet.join should still be at default
        join_binding = m.get_binding(InputAction.FLEET_JOIN)
        assert join_binding is not None
        assert join_binding.key == "K_j"


class TestInputMapperResolve:
    """Tests for event resolution."""

    def test_resolve_simple_key(self, mapper, make_keydown):
        """M key resolves to FLEET_MOVE."""
        event = make_keydown(pygame.K_m)
        result = mapper.resolve(event, contexts=["fleet"])
        assert result == InputAction.FLEET_MOVE

    def test_resolve_with_modifier(self, mapper, make_keydown):
        """Shift+G resolves to STRATEGY_ZOOM_GALAXY."""
        event = make_keydown(pygame.K_g, pygame.KMOD_SHIFT)
        result = mapper.resolve(event, contexts=["strategy"])
        assert result == InputAction.STRATEGY_ZOOM_GALAXY

    def test_resolve_with_lshift(self, mapper, make_keydown):
        """Left Shift normalizes to 'shift' modifier."""
        event = make_keydown(pygame.K_g, pygame.KMOD_LSHIFT)
        result = mapper.resolve(event, contexts=["strategy"])
        assert result == InputAction.STRATEGY_ZOOM_GALAXY

    def test_resolve_with_rshift(self, mapper, make_keydown):
        """Right Shift normalizes to 'shift' modifier."""
        event = make_keydown(pygame.K_g, pygame.KMOD_RSHIFT)
        result = mapper.resolve(event, contexts=["strategy"])
        assert result == InputAction.STRATEGY_ZOOM_GALAXY

    def test_resolve_returns_none_for_unbound(self, mapper, make_keydown):
        """Unbound keys return None."""
        event = make_keydown(pygame.K_q)
        result = mapper.resolve(event, contexts=["strategy", "fleet"])
        assert result is None

    def test_resolve_context_filtering_blocks_wrong_context(self, mapper, make_keydown):
        """Fleet action doesn't resolve when only 'strategy' context is active."""
        event = make_keydown(pygame.K_m)
        # M is fleet.move - should not match when only "build_queue" context is given
        result = mapper.resolve(event, contexts=["build_queue"])
        assert result is None

    def test_resolve_global_always_matches(self, mapper, make_keydown):
        """Global actions match regardless of context filter."""
        event = make_keydown(pygame.K_F12)
        result = mapper.resolve(event, contexts=["strategy"])
        assert result == InputAction.GLOBAL_SCREENSHOT_FULL

    def test_resolve_global_with_no_context(self, mapper, make_keydown):
        """Global actions match even when no contexts provided."""
        event = make_keydown(pygame.K_F12)
        result = mapper.resolve(event, contexts=[])
        assert result == InputAction.GLOBAL_SCREENSHOT_FULL

    def test_resolve_non_keydown_returns_none(self, mapper):
        """Non-KEYDOWN events return None."""
        event = MagicMock()
        event.type = pygame.MOUSEBUTTONDOWN
        result = mapper.resolve(event, contexts=["strategy"])
        assert result is None

    def test_resolve_alt_modifier(self, mapper, make_keydown):
        """Alt+X resolves to GLOBAL_EXIT."""
        event = make_keydown(pygame.K_x, pygame.KMOD_ALT)
        result = mapper.resolve(event, contexts=["strategy"])
        assert result == InputAction.GLOBAL_EXIT

    def test_resolve_ctrl_modifier(self, mapper, make_keydown):
        """Ctrl+S resolves to STRATEGY_SAVE_GAME."""
        event = make_keydown(pygame.K_s, pygame.KMOD_CTRL)
        result = mapper.resolve(event, contexts=["strategy"])
        assert result == InputAction.STRATEGY_SAVE_GAME


class TestInputMapperGetBinding:
    """Tests for get_binding and get_display_text."""

    def test_get_binding_returns_keybinding(self, mapper):
        """get_binding returns the current KeyBinding for an action."""
        binding = mapper.get_binding(InputAction.FLEET_MOVE)
        assert isinstance(binding, KeyBinding)
        assert binding.key == "K_m"

    def test_get_binding_unbound_returns_none(self, mapper):
        """get_binding for unbound action returns None."""
        binding = mapper.get_binding(InputAction.DETAIL_PANEL_BUILD)
        assert binding is None

    def test_get_display_text_bound(self, mapper):
        """get_display_text returns readable text for bound action."""
        text = mapper.get_display_text(InputAction.FLEET_MOVE)
        assert text == "M"

    def test_get_display_text_with_modifier(self, mapper):
        """get_display_text includes modifier text."""
        text = mapper.get_display_text(InputAction.STRATEGY_ZOOM_GALAXY)
        assert text == "Shift+G"

    def test_get_display_text_unbound(self, mapper):
        """get_display_text returns empty string for unbound action."""
        text = mapper.get_display_text(InputAction.DETAIL_PANEL_BUILD)
        assert text == ""

    def test_get_default_binding_returns_original(self, mapper):
        """get_default_binding returns the default even after user override."""
        # Override the binding
        mapper.set_binding(
            InputAction.FLEET_MOVE,
            KeyBinding(key="K_n", modifiers=frozenset()),
        )
        # Current binding should be the override
        assert mapper.get_binding(InputAction.FLEET_MOVE).key == "K_n"
        # Default binding should still be the original
        default = mapper.get_default_binding(InputAction.FLEET_MOVE)
        assert default is not None
        assert default.key == "K_m"

    def test_get_default_binding_unbound_returns_none(self, mapper):
        """get_default_binding for unbound-by-default action returns None."""
        default = mapper.get_default_binding(InputAction.DETAIL_PANEL_BUILD)
        assert default is None


class TestInputMapperSetBinding:
    """Tests for set_binding."""

    def test_set_binding_updates_resolution(self, mapper, make_keydown):
        """set_binding changes what the action resolves to."""
        new_binding = KeyBinding(key="K_n", modifiers=frozenset())
        mapper.set_binding(InputAction.FLEET_MOVE, new_binding)

        # New key should resolve
        event = make_keydown(pygame.K_n)
        assert mapper.resolve(event, contexts=["fleet"]) == InputAction.FLEET_MOVE

        # Old key should no longer resolve
        event = make_keydown(pygame.K_m)
        assert mapper.resolve(event, contexts=["fleet"]) is None

    def test_set_binding_none_unbinds(self, mapper, make_keydown):
        """set_binding with None clears the binding."""
        mapper.set_binding(InputAction.FLEET_MOVE, None)
        assert mapper.get_binding(InputAction.FLEET_MOVE) is None

        event = make_keydown(pygame.K_m)
        assert mapper.resolve(event, contexts=["fleet"]) is None


class TestInputMapperConflicts:
    """Tests for conflict detection."""

    def test_find_conflict_same_context(self, mapper):
        """get_conflicts finds actions in the same context with same key."""
        # K_m is fleet.move in "fleet" context
        binding = KeyBinding(key="K_m", modifiers=frozenset())
        conflicts = mapper.get_conflicts(binding, context="fleet")
        assert InputAction.FLEET_MOVE in conflicts

    def test_no_conflict_different_context(self, mapper):
        """Same key in different context doesn't conflict."""
        # K_a is build_queue.add in "build_queue" context
        binding = KeyBinding(key="K_a", modifiers=frozenset())
        conflicts = mapper.get_conflicts(binding, context="fleet")
        # build_queue.add should not appear as a conflict in fleet context
        assert InputAction.BUILD_QUEUE_ADD not in conflicts

    def test_global_conflicts_with_everything(self, mapper):
        """Global actions conflict with any context."""
        # F12 is global.screenshot_full
        binding = KeyBinding(key="K_F12", modifiers=frozenset())
        conflicts = mapper.get_conflicts(binding, context="strategy")
        assert InputAction.GLOBAL_SCREENSHOT_FULL in conflicts

    def test_conflict_with_global_context(self, mapper):
        """Binding in global context conflicts with all actions on same key."""
        # Try to bind something to Alt+X (which is global.exit)
        binding = KeyBinding(key="K_x", modifiers=frozenset({"alt"}))
        conflicts = mapper.get_conflicts(binding, context="global")
        assert InputAction.GLOBAL_EXIT in conflicts


class TestInputMapperSaveLoad:
    """Tests for saving and loading user overrides."""

    def test_save_user_overrides(self, mapper, tmp_path):
        """save_user_overrides creates a file with only diffs."""
        output_file = tmp_path / "keybindings.json"
        new_binding = KeyBinding(key="K_n", modifiers=frozenset())
        mapper.set_binding(InputAction.FLEET_MOVE, new_binding)
        result = mapper.save_user_overrides(str(output_file))
        assert result is True
        assert output_file.exists()

        data = json.loads(output_file.read_text())
        # Only the changed binding should be saved
        assert "fleet.move" in data["bindings"]
        assert data["bindings"]["fleet.move"]["key"] == "K_n"
        # Unchanged bindings should NOT be saved
        assert "fleet.join" not in data["bindings"]

    def test_save_load_roundtrip(self, tmp_path):
        """Save overrides then load them produces the same bindings."""
        output_file = tmp_path / "keybindings.json"

        # First mapper: change a binding and save
        m1 = InputMapper()
        m1.load(defaults_path=Paths.DEFAULT_KEYBINDINGS_FILE)
        m1.set_binding(
            InputAction.FLEET_MOVE,
            KeyBinding(key="K_n", modifiers=frozenset()),
        )
        m1.save_user_overrides(str(output_file))

        # Second mapper: load defaults + overrides
        m2 = InputMapper()
        m2.load(
            defaults_path=Paths.DEFAULT_KEYBINDINGS_FILE,
            overrides_path=str(output_file),
        )
        binding = m2.get_binding(InputAction.FLEET_MOVE)
        assert binding is not None
        assert binding.key == "K_n"

    def test_reset_to_defaults(self, mapper, make_keydown):
        """reset_to_defaults reverts all bindings to default values."""
        # Change a binding
        mapper.set_binding(
            InputAction.FLEET_MOVE,
            KeyBinding(key="K_n", modifiers=frozenset()),
        )
        assert mapper.get_binding(InputAction.FLEET_MOVE).key == "K_n"

        # Reset
        mapper.reset_to_defaults()
        binding = mapper.get_binding(InputAction.FLEET_MOVE)
        assert binding is not None
        assert binding.key == "K_m"

    def test_save_unbound_action(self, mapper, tmp_path):
        """Saving an unbound action stores it as empty dict."""
        output_file = tmp_path / "keybindings.json"
        mapper.set_binding(InputAction.FLEET_MOVE, None)
        mapper.save_user_overrides(str(output_file))

        data = json.loads(output_file.read_text())
        assert data["bindings"]["fleet.move"] == {}


class TestInputMapperGetAllBindings:
    """Tests for get_all_bindings."""

    def test_returns_all_actions(self, mapper):
        """get_all_bindings returns an entry for every InputAction."""
        all_bindings = mapper.get_all_bindings()
        for action in InputAction:
            assert action in all_bindings

    def test_bound_actions_have_keybinding(self, mapper):
        """Bound actions return KeyBinding instances."""
        all_bindings = mapper.get_all_bindings()
        assert isinstance(all_bindings[InputAction.FLEET_MOVE], KeyBinding)

    def test_unbound_actions_have_none(self, mapper):
        """Unbound actions return None."""
        all_bindings = mapper.get_all_bindings()
        assert all_bindings[InputAction.DETAIL_PANEL_BUILD] is None


class TestInputMapperEdgeCases:
    """Tests for edge case handling and resilience."""

    def test_corrupt_user_keybindings_falls_back_to_defaults(self, tmp_path):
        """Corrupt user keybindings JSON falls back gracefully to defaults."""
        corrupt_file = tmp_path / "keybindings.json"
        corrupt_file.write_text("{this is not valid json!!!")

        m = InputMapper()
        m.load(
            defaults_path=Paths.DEFAULT_KEYBINDINGS_FILE,
            overrides_path=str(corrupt_file),
        )
        # Defaults should still be loaded
        binding = m.get_binding(InputAction.FLEET_MOVE)
        assert binding is not None
        assert binding.key == "K_m"

    def test_empty_user_keybindings_file_falls_back_to_defaults(self, tmp_path):
        """Empty user keybindings file falls back to defaults."""
        empty_file = tmp_path / "keybindings.json"
        empty_file.write_text("")

        m = InputMapper()
        m.load(
            defaults_path=Paths.DEFAULT_KEYBINDINGS_FILE,
            overrides_path=str(empty_file),
        )
        # Defaults should still be loaded
        binding = m.get_binding(InputAction.FLEET_MOVE)
        assert binding is not None
        assert binding.key == "K_m"

    def test_empty_bindings_dict_preserves_defaults(self, tmp_path):
        """User file with empty bindings dict preserves all defaults."""
        overrides_file = tmp_path / "keybindings.json"
        overrides_file.write_text(json.dumps({"bindings": {}}))

        m = InputMapper()
        m.load(
            defaults_path=Paths.DEFAULT_KEYBINDINGS_FILE,
            overrides_path=str(overrides_file),
        )
        binding = m.get_binding(InputAction.FLEET_MOVE)
        assert binding is not None
        assert binding.key == "K_m"

    def test_save_creates_parent_directories(self, tmp_path):
        """save_user_overrides creates missing parent directories."""
        deep_path = tmp_path / "a" / "b" / "c" / "keybindings.json"
        assert not deep_path.parent.exists()

        m = InputMapper()
        m.load(defaults_path=Paths.DEFAULT_KEYBINDINGS_FILE)
        m.set_binding(
            InputAction.FLEET_MOVE,
            KeyBinding(key="K_n", modifiers=frozenset()),
        )
        result = m.save_user_overrides(str(deep_path))
        assert result is True
        assert deep_path.exists()

    def test_unknown_actions_in_file_are_skipped(self, tmp_path):
        """Unknown action names in user file are ignored without crashing."""
        overrides_file = tmp_path / "keybindings.json"
        overrides_file.write_text(json.dumps({
            "bindings": {
                "nonexistent.action": {"key": "K_z", "modifiers": []},
                "fleet.move": {"key": "K_n", "modifiers": []},
            }
        }))

        m = InputMapper()
        m.load(
            defaults_path=Paths.DEFAULT_KEYBINDINGS_FILE,
            overrides_path=str(overrides_file),
        )
        # Valid override applied
        binding = m.get_binding(InputAction.FLEET_MOVE)
        assert binding is not None
        assert binding.key == "K_n"

    def test_all_actions_unbound_no_crash(self):
        """An InputMapper with all actions unbound doesn't crash."""
        m = InputMapper()
        m.load()  # No defaults, no overrides

        # Resolve should return None
        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_m
        event.mod = 0
        assert m.resolve(event, contexts=["fleet"]) is None

        # Display text should be empty
        assert m.get_display_text(InputAction.FLEET_MOVE) == ""

        # get_all_bindings should have all actions as None
        all_bindings = m.get_all_bindings()
        for action in InputAction:
            assert all_bindings[action] is None

    def test_save_no_overrides_returns_true(self, mapper, tmp_path):
        """Saving with no changes returns True without creating a file."""
        output_file = tmp_path / "keybindings.json"
        result = mapper.save_user_overrides(str(output_file))
        assert result is True
        assert not output_file.exists()

    def test_resolve_no_contexts_returns_first_match(self, mapper, make_keydown):
        """Resolve with contexts=None returns first matching action."""
        event = make_keydown(pygame.K_m)
        result = mapper.resolve(event, contexts=None)
        assert result is not None

    def test_invalid_pygame_key_in_binding_skipped(self, tmp_path):
        """Binding with invalid pygame key name is silently skipped."""
        overrides_file = tmp_path / "keybindings.json"
        overrides_file.write_text(json.dumps({
            "bindings": {
                "fleet.move": {"key": "K_INVALID_KEY_NAME", "modifiers": []}
            }
        }))

        m = InputMapper()
        m.load(
            defaults_path=Paths.DEFAULT_KEYBINDINGS_FILE,
            overrides_path=str(overrides_file),
        )
        # The binding is stored but won't resolve because key is invalid
        binding = m.get_binding(InputAction.FLEET_MOVE)
        assert binding is not None
        assert binding.key == "K_INVALID_KEY_NAME"

        # Should not resolve to any action
        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_m
        event.mod = 0
        result = m.resolve(event, contexts=["fleet"])
        # M no longer maps to fleet.move since it was overridden
        assert result is None


# =============================================================================
# Additional Coverage Tests (TCG-FND-004)
# =============================================================================

class TestConflictDetectionExpanded:
    """Additional tests for conflict detection edge cases."""

    def test_get_conflicts_same_key_overlapping_context(self, mapper):
        """Fleet/strategy contexts conflict (both can be active together)."""
        # Find an action in strategy context with a specific key
        # K_g + Shift is strategy.zoom_galaxy
        binding = KeyBinding(key="K_g", modifiers=frozenset({"shift"}))
        conflicts = mapper.get_conflicts(binding, context="strategy")
        assert InputAction.STRATEGY_ZOOM_GALAXY in conflicts

    def test_get_conflicts_same_key_nonoverlapping_context(self, mapper):
        """build_queue/transfer don't conflict (never active together)."""
        # These contexts are isolated and don't overlap
        binding = KeyBinding(key="K_a", modifiers=frozenset())
        conflicts = mapper.get_conflicts(binding, context="transfer")
        # build_queue.add should NOT appear as conflict in transfer context
        assert InputAction.BUILD_QUEUE_ADD not in conflicts

    def test_get_conflicts_with_modifiers(self, mapper):
        """Same key, same modifiers = conflict."""
        # Ctrl+S is strategy.save_game
        binding = KeyBinding(key="K_s", modifiers=frozenset({"ctrl"}))
        conflicts = mapper.get_conflicts(binding, context="strategy")
        assert InputAction.STRATEGY_SAVE_GAME in conflicts

    def test_get_conflicts_no_conflicts_for_different_keys(self, mapper):
        """Different keys never conflict."""
        # Use a key that definitely isn't bound
        binding = KeyBinding(key="K_BACKSLASH", modifiers=frozenset())
        conflicts = mapper.get_conflicts(binding, context="fleet")
        # No actions should be using backslash
        assert len(conflicts) == 0


class TestContextOverlap:
    """Tests for context overlap detection."""

    def test_contexts_overlap_global_always_true(self, mapper):
        """global overlaps with any context."""
        # Try to bind to a key used by global action
        binding = KeyBinding(key="K_F12", modifiers=frozenset())
        # When checking from any context, global should conflict
        conflicts = mapper.get_conflicts(binding, context="fleet")
        assert InputAction.GLOBAL_SCREENSHOT_FULL in conflicts

        conflicts = mapper.get_conflicts(binding, context="build_queue")
        assert InputAction.GLOBAL_SCREENSHOT_FULL in conflicts

    def test_contexts_overlap_fleet_strategy(self, mapper):
        """fleet and strategy overlap (both can be active together)."""
        # If we bind something in fleet context that uses same key as strategy action,
        # they should conflict since these contexts overlap
        from game.ui.services.input_mapper import _CONTEXT_OVERLAP
        assert "strategy" in _CONTEXT_OVERLAP.get("fleet", set())
        assert "fleet" in _CONTEXT_OVERLAP.get("strategy", set())

    def test_contexts_overlap_build_queue_isolated(self, mapper):
        """build_queue doesn't overlap fleet."""
        from game.ui.services.input_mapper import _CONTEXT_OVERLAP
        assert "fleet" not in _CONTEXT_OVERLAP.get("build_queue", set())

    def test_contexts_overlap_none_context_always_true(self, mapper):
        """None context treated as overlap with everything."""
        # When context is None, all same-key actions should conflict
        binding = KeyBinding(key="K_m", modifiers=frozenset())
        conflicts = mapper.get_conflicts(binding, context=None)
        # Should find fleet.move
        assert InputAction.FLEET_MOVE in conflicts

    def test_contexts_overlap_same_context(self, mapper):
        """fleet overlaps with itself."""
        from game.ui.services.input_mapper import _CONTEXT_OVERLAP
        assert "fleet" in _CONTEXT_OVERLAP.get("fleet", set())


class TestModifierExtraction:
    """Tests for modifier extraction from pygame events."""

    def test_extract_modifiers_ctrl(self, make_keydown):
        """KMOD_CTRL -> frozenset({'ctrl'})."""
        from game.ui.services.input_mapper import InputMapper
        event = make_keydown(pygame.K_a, pygame.KMOD_CTRL)
        mods = InputMapper._extract_modifiers(event.mod)
        assert mods == frozenset({"ctrl"})

    def test_extract_modifiers_shift(self, make_keydown):
        """KMOD_SHIFT -> frozenset({'shift'})."""
        from game.ui.services.input_mapper import InputMapper
        event = make_keydown(pygame.K_a, pygame.KMOD_SHIFT)
        mods = InputMapper._extract_modifiers(event.mod)
        assert mods == frozenset({"shift"})

    def test_extract_modifiers_alt(self, make_keydown):
        """KMOD_ALT -> frozenset({'alt'})."""
        from game.ui.services.input_mapper import InputMapper
        event = make_keydown(pygame.K_a, pygame.KMOD_ALT)
        mods = InputMapper._extract_modifiers(event.mod)
        assert mods == frozenset({"alt"})

    def test_extract_modifiers_multiple(self, make_keydown):
        """KMOD_CTRL|KMOD_SHIFT -> frozenset({'ctrl', 'shift'})."""
        from game.ui.services.input_mapper import InputMapper
        event = make_keydown(pygame.K_a, pygame.KMOD_CTRL | pygame.KMOD_SHIFT)
        mods = InputMapper._extract_modifiers(event.mod)
        assert mods == frozenset({"ctrl", "shift"})

    def test_extract_modifiers_none(self, make_keydown):
        """0 -> frozenset()."""
        from game.ui.services.input_mapper import InputMapper
        mods = InputMapper._extract_modifiers(0)
        assert mods == frozenset()


class TestLookupTable:
    """Tests for lookup table building and resolution."""

    def test_build_lookup_multiple_actions_same_key(self, mapper, make_keydown):
        """Multiple actions indexed correctly when sharing key+modifiers."""
        # ESC is used by multiple contexts (fleet.cancel_mode, build_queue.close, etc.)
        # These should all be in the lookup
        event = make_keydown(pygame.K_ESCAPE)

        # With fleet context, should get fleet action
        result = mapper.resolve(event, contexts=["fleet"])
        assert result is not None

        # With build_queue context, should get build_queue action
        result = mapper.resolve(event, contexts=["build_queue"])
        assert result is not None

    def test_resolve_returns_first_matching_context(self, mapper, make_keydown):
        """Context filter picks correct action from multiple possibilities."""
        # Test that when multiple actions share a key, context filtering works
        event = make_keydown(pygame.K_ESCAPE)

        # Fleet context should return fleet action
        result = mapper.resolve(event, contexts=["fleet"])
        if result:
            assert "fleet" in result.value or "global" in result.value

        # Build queue context should return build_queue action
        result = mapper.resolve(event, contexts=["build_queue"])
        if result:
            assert "build_queue" in result.value or "global" in result.value
