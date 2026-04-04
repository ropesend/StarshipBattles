"""Tests for MANDATORY_MODIFIERS consistency.

Verifies that the canonical MANDATORY_MODIFIERS list in ModifierService
is a non-empty list of strings, and that the dead duplicate in ModifierLogic
has been removed (regression guard).
"""
import pytest
from game.simulation.services.modifier_service import ModifierService


class TestMandatoryModifiers:
    """Ensure MANDATORY_MODIFIERS is defined in exactly one place."""

    def test_modifier_service_has_mandatory_modifiers(self):
        """ModifierService should define MANDATORY_MODIFIERS as a non-empty list."""
        assert hasattr(ModifierService, 'MANDATORY_MODIFIERS')
        assert isinstance(ModifierService.MANDATORY_MODIFIERS, list)
        assert len(ModifierService.MANDATORY_MODIFIERS) > 0

    def test_mandatory_modifiers_are_strings(self):
        """All entries in MANDATORY_MODIFIERS should be strings."""
        for mod_id in ModifierService.MANDATORY_MODIFIERS:
            assert isinstance(mod_id, str), f"Expected str, got {type(mod_id)}: {mod_id}"

    def test_modifier_logic_no_duplicate_constant(self):
        """ModifierLogic should NOT have its own MANDATORY_MODIFIERS list (removed as dead code)."""
        from game.ui.screens.builder.modifier_logic import ModifierLogic
        # The class should not have a MANDATORY_MODIFIERS attribute that is a list
        # (it may have a comment reference, but not the actual data)
        attr = getattr(ModifierLogic, 'MANDATORY_MODIFIERS', None)
        assert attr is None or not isinstance(attr, list), (
            "ModifierLogic.MANDATORY_MODIFIERS should not be a list — "
            "the canonical source is ModifierService.MANDATORY_MODIFIERS"
        )

    def test_expected_mandatory_modifiers(self):
        """MANDATORY_MODIFIERS should contain the known set of mandatory modifier IDs."""
        expected = {'simple_size_mount', 'range_mount', 'facing', 'turret_mount'}
        actual = set(ModifierService.MANDATORY_MODIFIERS)
        assert actual == expected, f"Expected {expected}, got {actual}"
