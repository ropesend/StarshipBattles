import unittest
from unittest.mock import MagicMock
import pygame
from ui.builder.drop_target import DropTarget
from ui.builder.interaction_controller import InteractionController

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

class TestBuilderInteraction(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.builder = MagicMock()
        self.builder.detail_panel.rect = pygame.Rect(0, 0, 0, 0) # Mock rect
        self.builder.left_panel.get_add_count.return_value = 1
        self.view = MagicMock()
        self.view.rect = pygame.Rect(0, 0, 100, 100)
        
        self.controller = InteractionController(self.builder, self.view)
        
    def tearDown(self):
        pygame.quit()
        
    def test_drop_delegation(self):
        target = MockDropTarget()
        self.controller.register_drop_target(target)
        
        # Simulate Drop at (150, 150) - Should accept
        comp = MagicMock()
        self.controller.dragged_item = comp
        self.controller._handle_drop((150, 150))
        
        self.assertTrue(target.accepted)
        self.assertEqual(target.last_comp, comp)
        
    def test_drop_rejection(self):
        target = MockDropTarget()
        self.controller.register_drop_target(target)
        
        # Simulate Drop at (50, 50) - Should reject (x < 100)
        comp = MagicMock()
        self.controller.dragged_item = comp
        self.controller._handle_drop((50, 50))
        
        self.assertFalse(target.accepted)

if __name__ == '__main__':
    unittest.main()
