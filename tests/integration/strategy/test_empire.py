"""
Tests for fleet ID generation (Galaxy-level) and per-empire display numbering.
"""
from game.strategy.data.empire import Empire
from tests.fixtures.galaxy_fixtures import make_galaxy_stub


class TestEmpire:
    def test_fleet_id_sequential(self):
        """Test that fleet IDs from Galaxy are sequential."""
        galaxy = make_galaxy_stub()
        id1 = galaxy.get_next_fleet_id()
        id2 = galaxy.get_next_fleet_id()
        assert id2 == id1 + 1

    def test_fleet_id_starts_at_1(self):
        """Test that Galaxy fleet IDs start at 1."""
        galaxy = make_galaxy_stub()
        id1 = galaxy.get_next_fleet_id()
        assert id1 == 1

    def test_fleet_id_persists_across_save(self):
        """Test that Galaxy fleet ID counter survives serialization."""
        galaxy = make_galaxy_stub()
        galaxy.get_next_fleet_id()  # 1
        galaxy.get_next_fleet_id()  # 2

        # Counter should now be at 3
        assert galaxy._next_fleet_id == 3

        # Simulate round-trip via to_dict/from_dict field
        saved_counter = galaxy._next_fleet_id

        galaxy2 = make_galaxy_stub()
        galaxy2._state.next_fleet_id = saved_counter

        next_id = galaxy2.get_next_fleet_id()
        assert next_id == 3  # Should continue from where we left off

    def test_multiple_empires_share_single_counter(self):
        """Test that all empires share the Galaxy fleet ID counter (no collisions)."""
        galaxy = make_galaxy_stub()

        # Two empires getting fleet IDs from the same galaxy
        id1 = galaxy.get_next_fleet_id()  # For empire 0
        id2 = galaxy.get_next_fleet_id()  # For empire 1
        id3 = galaxy.get_next_fleet_id()  # For empire 0

        # All IDs should be unique and sequential
        assert id1 == 1
        assert id2 == 2
        assert id3 == 3

    def test_empire_display_numbers_are_independent(self):
        """Test that per-empire display numbers are independent."""
        empire1 = Empire(0, "Empire 1", (255, 0, 0))
        empire2 = Empire(1, "Empire 2", (0, 255, 0))

        dn1a = empire1.get_next_fleet_display_number()
        dn2a = empire2.get_next_fleet_display_number()
        dn1b = empire1.get_next_fleet_display_number()
        dn2b = empire2.get_next_fleet_display_number()

        # Both empires should start at 1
        assert dn1a == 1
        assert dn2a == 1

        # Each should increment independently
        assert dn1b == 2
        assert dn2b == 2
