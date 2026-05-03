"""Tests for ModifierEditorPanel.

BUG-89: Verify that the panel has an update(dt) method,
which workshop_screen.py calls every frame.

PROJ-322 Task 2.12 (S10-CAT5-001): the 3 tests collapsed into a
single parametrized test exercising update(dt) at 0 and a typical
frame delta. The `modifier_panel` fixture remains at function scope
because each test instantiates a real ModifierEditorPanel and the
panel records mutable state during update().
"""
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def modifier_panel():
    """Create a ModifierEditorPanel with mocked dependencies."""
    from game.ui.panels.builder_widgets import ModifierEditorPanel

    manager = MagicMock()
    container = MagicMock()
    registries = MagicMock()

    panel = ModifierEditorPanel(
        manager=manager,
        container=container,
        width=300,
        on_change_callback=MagicMock(),
        registries=registries,
    )
    return panel


class TestModifierEditorPanelUpdate:
    """BUG-89: ModifierEditorPanel must have update(dt) method."""

    def test_update_method_exists(self, modifier_panel):
        """The panel must have an update method callable with dt argument."""
        assert hasattr(modifier_panel, 'update'), (
            "ModifierEditorPanel must have an update(dt) method"
        )
        assert callable(modifier_panel.update)

    @pytest.mark.parametrize('dt', [0, 0.016])
    def test_update_does_not_raise(self, modifier_panel, dt):
        """Calling update(dt) must not raise for either zero or a typical
        ~60fps frame delta. Parametrized in PROJ-322 Task 2.12 from two
        near-identical method-shape tests."""
        modifier_panel.update(dt)
