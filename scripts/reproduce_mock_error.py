
import unittest
from unittest.mock import MagicMock

class TestMocking(unittest.TestCase):
    def test_mock_attribute(self):
        m = MagicMock()
        # This is what we have in code
        m.get_engage_distance_multiplier.return_value = 1.0
        m.check_avoidance.return_value = None
        print("Mock check passed")
        
        # What if we inadvertently touched a builtin?
        # m.ship.position = pygame.math.Vector2(0,0) <-- Real object
        # m.ship.position.distance_to.return_value = 1 <-- This would fail
        
if __name__ == '__main__':
    unittest.main()
