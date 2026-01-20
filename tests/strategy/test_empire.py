"""
Tests for Empire class, particularly fleet ID generation.
"""

import unittest
from game.strategy.data.empire import Empire


class TestEmpire(unittest.TestCase):
    def test_fleet_id_sequential(self):
        """Test that fleet IDs are sequential."""
        empire = Empire(0, "Test", (255, 0, 0))
        id1 = empire.get_next_fleet_id()
        id2 = empire.get_next_fleet_id()
        self.assertEqual(id2, id1 + 1)

    def test_fleet_id_starts_at_10000(self):
        """Test that fleet IDs start at 10000."""
        empire = Empire(0, "Test", (255, 0, 0))
        id1 = empire.get_next_fleet_id()
        self.assertEqual(id1, 10000)

    def test_fleet_id_persists_across_save(self):
        """Test that fleet ID counter survives serialization."""
        empire = Empire(0, "Test", (255, 0, 0))
        empire.get_next_fleet_id()  # 10000
        empire.get_next_fleet_id()  # 10001

        # Serialize and deserialize
        data = empire.to_dict()
        restored = Empire.from_dict(data)

        # Next ID should continue from last ID
        next_id = restored.get_next_fleet_id()
        self.assertEqual(next_id, 10002)  # Should continue from 10001

    def test_multiple_empires_have_independent_counters(self):
        """Test that each empire has its own fleet ID counter."""
        empire1 = Empire(0, "Empire 1", (255, 0, 0))
        empire2 = Empire(1, "Empire 2", (0, 255, 0))

        id1a = empire1.get_next_fleet_id()
        id2a = empire2.get_next_fleet_id()
        id1b = empire1.get_next_fleet_id()
        id2b = empire2.get_next_fleet_id()

        # Both empires should start at 10000
        self.assertEqual(id1a, 10000)
        self.assertEqual(id2a, 10000)

        # Each should increment independently
        self.assertEqual(id1b, 10001)
        self.assertEqual(id2b, 10001)


if __name__ == '__main__':
    unittest.main()
