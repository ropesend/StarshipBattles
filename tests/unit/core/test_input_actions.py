"""Tests for InputAction enum and KeyBinding dataclass."""
import pytest

from game.core.input_actions import (
    InputAction,
    KeyBinding,
    ACTION_DISPLAY_NAMES,
    ACTION_GROUPS,
)


class TestInputAction:
    """Tests for the InputAction enum."""

    def test_all_values_use_dot_notation(self):
        """Every InputAction value must contain a dot separator."""
        for action in InputAction:
            assert "." in action.value, (
                f"{action.name} value '{action.value}' missing dot notation"
            )

    def test_all_values_have_valid_context_prefix(self):
        """Every action value must start with a known context prefix."""
        valid_prefixes = {
            "global", "strategy", "fleet", "build_queue",
            "fleet_orders", "transfer", "detail_panel",
            "planet",  # PROJ-238
        }
        for action in InputAction:
            prefix = action.value.split(".")[0]
            assert prefix in valid_prefixes, (
                f"{action.name} has unknown context prefix '{prefix}'"
            )

    def test_all_values_are_unique(self):
        """No two InputAction members should share the same value."""
        values = [a.value for a in InputAction]
        assert len(values) == len(set(values))

    def test_enum_is_string_based(self):
        """InputAction should be a string enum for JSON serialization."""
        for action in InputAction:
            assert isinstance(action.value, str)
            # String enum comparison
            assert action == action.value

    def test_known_actions_exist(self):
        """Verify key actions exist in the enum."""
        assert InputAction.FLEET_MOVE.value == "fleet.move"
        assert InputAction.FLEET_JOIN.value == "fleet.join"
        assert InputAction.FLEET_COLONIZE.value == "fleet.colonize"
        assert InputAction.FLEET_TRANSFER.value == "fleet.transfer"
        assert InputAction.FLEET_CANCEL_MODE.value == "fleet.cancel_mode"
        assert InputAction.STRATEGY_NEXT_TURN.value == "strategy.next_turn"
        assert InputAction.STRATEGY_ZOOM_GALAXY.value == "strategy.zoom_galaxy"
        assert InputAction.STRATEGY_ZOOM_SYSTEM.value == "strategy.zoom_system"
        assert InputAction.GLOBAL_EXIT.value == "global.exit"


class TestActionDisplayNames:
    """Tests for ACTION_DISPLAY_NAMES mapping."""

    def test_covers_all_actions(self):
        """Every InputAction must have a display name."""
        for action in InputAction:
            assert action in ACTION_DISPLAY_NAMES, (
                f"{action.name} missing from ACTION_DISPLAY_NAMES"
            )

    def test_display_names_are_non_empty_strings(self):
        """All display names must be non-empty strings."""
        for action, name in ACTION_DISPLAY_NAMES.items():
            assert isinstance(name, str)
            assert len(name) > 0, f"{action.name} has empty display name"

    def test_display_names_are_human_readable(self):
        """Spot-check that display names are readable."""
        assert ACTION_DISPLAY_NAMES[InputAction.FLEET_MOVE] == "Move Fleet"
        assert ACTION_DISPLAY_NAMES[InputAction.STRATEGY_NEXT_TURN] == "End Turn"
        assert ACTION_DISPLAY_NAMES[InputAction.GLOBAL_EXIT] == "Exit Game"


class TestActionGroups:
    """Tests for ACTION_GROUPS mapping."""

    def test_covers_all_actions(self):
        """Every InputAction must appear in exactly one group."""
        all_in_groups = []
        for actions in ACTION_GROUPS.values():
            all_in_groups.extend(actions)

        for action in InputAction:
            assert action in all_in_groups, (
                f"{action.name} missing from ACTION_GROUPS"
            )

    def test_no_duplicates_across_groups(self):
        """No action should appear in more than one group."""
        all_in_groups = []
        for actions in ACTION_GROUPS.values():
            all_in_groups.extend(actions)
        assert len(all_in_groups) == len(set(all_in_groups))

    def test_group_keys_are_human_readable(self):
        """Group keys should be readable category names."""
        for key in ACTION_GROUPS:
            assert isinstance(key, str)
            assert len(key) > 0


class TestKeyBinding:
    """Tests for the KeyBinding frozen dataclass."""

    def test_creation(self):
        """KeyBinding can be created with key and modifiers."""
        binding = KeyBinding(key="K_m", modifiers=frozenset())
        assert binding.key == "K_m"
        assert binding.modifiers == frozenset()

    def test_frozen(self):
        """KeyBinding instances should be immutable."""
        binding = KeyBinding(key="K_m", modifiers=frozenset())
        with pytest.raises(AttributeError):
            binding.key = "K_j"

    def test_display_text_simple_letter(self):
        """display_text for a simple letter key."""
        binding = KeyBinding(key="K_m", modifiers=frozenset())
        assert binding.display_text() == "M"

    def test_display_text_with_shift(self):
        """display_text for Shift+G."""
        binding = KeyBinding(key="K_g", modifiers=frozenset({"shift"}))
        assert binding.display_text() == "Shift+G"

    def test_display_text_with_ctrl(self):
        """display_text for Ctrl+S."""
        binding = KeyBinding(key="K_s", modifiers=frozenset({"ctrl"}))
        assert binding.display_text() == "Ctrl+S"

    def test_display_text_with_alt(self):
        """display_text for Alt+X."""
        binding = KeyBinding(key="K_x", modifiers=frozenset({"alt"}))
        assert binding.display_text() == "Alt+X"

    def test_display_text_with_multiple_modifiers(self):
        """display_text for Ctrl+Shift+S."""
        binding = KeyBinding(key="K_s", modifiers=frozenset({"ctrl", "shift"}))
        text = binding.display_text()
        # Order is: Ctrl, Shift, Alt, then key
        assert text == "Ctrl+Shift+S"

    def test_display_text_function_key(self):
        """display_text for F12."""
        binding = KeyBinding(key="K_F12", modifiers=frozenset())
        assert binding.display_text() == "F12"

    def test_display_text_special_keys(self):
        """display_text for special keys like Escape, Space, Return."""
        assert KeyBinding(key="K_ESCAPE", modifiers=frozenset()).display_text() == "Esc"
        assert KeyBinding(key="K_SPACE", modifiers=frozenset()).display_text() == "Space"
        assert KeyBinding(key="K_RETURN", modifiers=frozenset()).display_text() == "Enter"
        assert KeyBinding(key="K_TAB", modifiers=frozenset()).display_text() == "Tab"
        assert KeyBinding(key="K_DELETE", modifiers=frozenset()).display_text() == "Del"

    def test_from_dict_simple(self):
        """from_dict creates a KeyBinding from a dict."""
        data = {"key": "K_m", "modifiers": []}
        binding = KeyBinding.from_dict(data)
        assert binding.key == "K_m"
        assert binding.modifiers == frozenset()

    def test_from_dict_with_modifiers(self):
        """from_dict handles modifiers list."""
        data = {"key": "K_g", "modifiers": ["shift"]}
        binding = KeyBinding.from_dict(data)
        assert binding.key == "K_g"
        assert binding.modifiers == frozenset({"shift"})

    def test_from_dict_empty_returns_none(self):
        """from_dict with empty dict returns None (unbound action)."""
        assert KeyBinding.from_dict({}) is None

    def test_from_dict_missing_key_returns_none(self):
        """from_dict with missing key field returns None."""
        assert KeyBinding.from_dict({"modifiers": ["shift"]}) is None

    def test_to_dict_simple(self):
        """to_dict produces a serializable dict."""
        binding = KeyBinding(key="K_m", modifiers=frozenset())
        d = binding.to_dict()
        assert d == {"key": "K_m", "modifiers": []}

    def test_to_dict_with_modifiers(self):
        """to_dict includes modifiers as sorted list."""
        binding = KeyBinding(key="K_s", modifiers=frozenset({"ctrl", "shift"}))
        d = binding.to_dict()
        assert d["key"] == "K_s"
        assert sorted(d["modifiers"]) == ["ctrl", "shift"]

    def test_roundtrip(self):
        """from_dict(to_dict()) produces an equal KeyBinding."""
        original = KeyBinding(key="K_g", modifiers=frozenset({"shift"}))
        roundtripped = KeyBinding.from_dict(original.to_dict())
        assert roundtripped == original

    def test_equality(self):
        """Two KeyBindings with same key and modifiers are equal."""
        a = KeyBinding(key="K_m", modifiers=frozenset())
        b = KeyBinding(key="K_m", modifiers=frozenset())
        assert a == b

    def test_inequality_different_key(self):
        """KeyBindings with different keys are not equal."""
        a = KeyBinding(key="K_m", modifiers=frozenset())
        b = KeyBinding(key="K_j", modifiers=frozenset())
        assert a != b

    def test_inequality_different_modifiers(self):
        """KeyBindings with different modifiers are not equal."""
        a = KeyBinding(key="K_s", modifiers=frozenset())
        b = KeyBinding(key="K_s", modifiers=frozenset({"ctrl"}))
        assert a != b
