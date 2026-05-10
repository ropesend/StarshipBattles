import pytest
from unittest.mock import MagicMock
import pygame
from game.ui.screens.builder.drop_target import DropTarget
from game.ui.screens.builder.interaction_controller import InteractionController


class MockDropTarget(DropTarget):
    def __init__(self):
        self.accepted = False
        self.last_pos = None
        self.last_comp = None

    def can_accept_drop(self, pos):
        return pos[0] > 100 # Accept if x > 100

    def accept_drop(self, pos, component, count=1):
        if self.can_accept_drop(pos):
            self.accepted = True
            self.last_pos = pos
            self.last_comp = component
            return True
        return False

    def suppress_toggle(self):
        """Suppress toggle events for a short duration."""
        pass


@pytest.fixture
def interaction_setup():
    builder = MagicMock()
    builder.detail_panel.rect = pygame.Rect(0, 0, 0, 0)  # Mock rect
    builder.left_panel.get_add_count.return_value = 1
    view = MagicMock()
    view.rect = pygame.Rect(0, 0, 100, 100)

    controller = InteractionController(builder, view)
    return controller


class TestBuilderInteraction:
    def test_drop_delegation(self, interaction_setup):
        controller = interaction_setup
        target = MockDropTarget()
        controller.register_drop_target(target)

        # Simulate Drop at (150, 150) - Should accept
        comp = MagicMock()
        controller.dragged_item = comp
        controller._handle_drop((150, 150))

        assert target.accepted is True
        assert target.last_comp == comp

    def test_drop_rejection(self, interaction_setup):
        controller = interaction_setup
        target = MockDropTarget()
        controller.register_drop_target(target)

        # Simulate Drop at (50, 50) - Should reject (x < 100)
        comp = MagicMock()
        controller.dragged_item = comp
        controller._handle_drop((50, 50))

        assert target.accepted is False
