"""Regression test: MANDATORY_MODIFIERS must live only in ModifierService.

Fix 7: ModifierLogic (now ModifierLogicService) previously defined an identical
MANDATORY_MODIFIERS list, creating a silent sync hazard. The duplicate was
removed; ModifierService is now the sole owner. This test catches any regression
where the constant is re-added to the UI-layer service.

PROJ-388: ``ModifierLogic`` static wrapper deleted; assertion now targets
``ModifierLogicService`` (the canonical instance-based service).
"""
from game.simulation.services.modifier_service import ModifierService
from game.ui.screens.builder.modifier_logic import ModifierLogicService


def test_modifier_logic_service_has_no_own_mandatory_modifiers_constant():
    """ModifierLogicService must not define MANDATORY_MODIFIERS itself.

    The constant belongs to ModifierService. If someone re-adds it to the
    UI-layer service the values can silently diverge, which is exactly the
    bug this fix addresses.
    """
    assert 'MANDATORY_MODIFIERS' not in ModifierLogicService.__dict__, (
        "ModifierLogicService must not define its own MANDATORY_MODIFIERS constant. "
        "Use ModifierService.MANDATORY_MODIFIERS as the single source of truth."
    )


def test_modifier_service_owns_mandatory_modifiers():
    """ModifierService is the single source of truth for MANDATORY_MODIFIERS."""
    assert hasattr(ModifierService, 'MANDATORY_MODIFIERS')
    assert isinstance(ModifierService.MANDATORY_MODIFIERS, list)
    assert len(ModifierService.MANDATORY_MODIFIERS) > 0


def test_mandatory_modifiers_contains_known_keys():
    """Spot-check the expected modifier IDs are present."""
    expected = {'simple_size_mount', 'range_mount', 'facing', 'turret_mount'}
    actual = set(ModifierService.MANDATORY_MODIFIERS)
    assert expected.issubset(actual), (
        f"Expected {expected} to be a subset of MANDATORY_MODIFIERS, got {actual}"
    )
