"""
Performance verification for dirty-flagged stats (PROJ-253 Phase 4).

Measures stat pipeline call count reduction with the dirty flag.
"""
from game.simulation.entities.ship import Ship


class TestStatsPipelineCallCount:
    """Verify dirty flag reduces redundant stat recalculations."""

    def test_stable_ship_skips_recalculation(self, fresh_registries):
        """A ship with no state changes should skip the stat pipeline on if_dirty calls."""
        ship = Ship("Test", 0, 0, (255, 0, 0), registries=fresh_registries)
        ship.recalculate_stats()  # First: runs pipeline, clears flag

        # Instrument the calculator
        call_count = [0]
        original = ship.stats_calculator.calculate

        def counting(s):
            call_count[0] += 1
            return original(s)

        ship.stats_calculator.calculate = counting

        # Simulate 100 ticks of combat manager calling recalculate_stats_if_dirty
        for _ in range(100):
            ship.recalculate_stats_if_dirty()

        # Should be 0 — no state changes occurred
        assert call_count[0] == 0, (
            f"Expected 0 recalculations on stable ship, got {call_count[0]}"
        )

    def test_damaged_ship_recalculates_once(self, fresh_registries):
        """A ship that takes damage should recalculate exactly once per damage event."""
        from tests.fixtures.ships import create_test_ship
        ship = create_test_ship(
            name="Test", x=0, y=0,
            add_bridge=True,
            add_weapons=1,
            registries=fresh_registries,
        )
        ship.recalculate_stats()  # Initial

        call_count = [0]
        original = ship.stats_calculator.calculate

        def counting(s):
            call_count[0] += 1
            return original(s)

        ship.stats_calculator.calculate = counting

        # 50 stable ticks
        for _ in range(50):
            ship.recalculate_stats_if_dirty()

        assert call_count[0] == 0, "Should skip during stable ticks"

        # Take damage (sets dirty)
        comps = ship.get_all_components()
        if comps:
            comps[0].take_damage(1)

        # Next recalculate_if_dirty should run
        ship.recalculate_stats_if_dirty()
        assert call_count[0] == 1, "Should recalculate once after damage"

        # 50 more stable ticks
        for _ in range(50):
            ship.recalculate_stats_if_dirty()

        assert call_count[0] == 1, "Should not recalculate again without more damage"
