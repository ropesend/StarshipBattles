import unittest
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from game.ui.screens.builder.event_bus import EventBus

class TestEventBus(unittest.TestCase):
    def test_subprocess_communication(self):
        bus = EventBus()
        self.received = None
        
        def handler(data):
            self.received = data
            
        bus.subscribe("TEST_EVENT", handler)
        bus.emit("TEST_EVENT", "Hello")
        
        self.assertEqual(self.received, "Hello")
        
    def test_unsubscribe(self):
        bus = EventBus()
        self.counter = 0
        
        def handler(data):
            self.counter += 1
            
        bus.subscribe("PING", handler)
        bus.emit("PING")
        self.assertEqual(self.counter, 1)
        
        bus.unsubscribe("PING", handler)
        bus.emit("PING")
        self.assertEqual(self.counter, 1) # Should not increment

if __name__ == '__main__':
    unittest.main()
