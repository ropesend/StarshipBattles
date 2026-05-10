"""
Tests for dirty-flagged ship stat invalidation (PROJ-253 Phase 1).

Verifies that:
- Ship starts with stats dirty (first recalculate always runs)
- After recalculate, stats are clean (second call is a no-op)
- Component state changes set stats dirty
- Dirty flag prevents unnecessary stat pipeline runs
"""
from game.simulation.entities.ship import Ship


class TestShipStatsDirtyFlag:
    """Ship should track whether stats need recalculation."""

    def test_ship_starts_with_stats_dirty(self, fresh_registries):
        """New ship should have _stats_dirty = True."""
        ship = Ship("Test", 0, 0, (255, 0, 0), registries=fresh_registries)
        assert ship._stats_dirty is True

    def test_recalculate_clears_dirty_flag(self, fresh_registries):
        """After recalculate_stats(), _stats_dirty should be False."""
        ship = Ship("Test", 0, 0, (255, 0, 0), registries=fresh_registries)
        ship.recalculate_stats()
        assert ship._stats_dirty is False

    def test_recalculate_if_dirty_is_noop_when_clean(self, fresh_registries):
        """recalculate_stats_if_dirty() with clean flag should skip the pipeline."""
        ship = Ship("Test", 0, 0, (255, 0, 0), registries=fresh_registries)
        ship.recalculate_stats()  # First: runs pipeline, clears flag

        # Spy on the stats calculator
        assert ship.stats_calculator is not None
        original_calculate = ship.stats_calculator.calculate
        call_count = [0]

        def counting_calculate(s):
            call_count[0] += 1
            return original_calculate(s)

        ship.stats_calculator.calculate = counting_calculate

        ship.recalculate_stats_if_dirty()  # Should skip — stats are clean

        assert call_count[0] == 0, "Pipeline should not run when stats are clean"

    def test_mark_stats_dirty_sets_flag(self, fresh_registries):
        """mark_stats_dirty() should set _stats_dirty = True."""
        ship = Ship("Test", 0, 0, (255, 0, 0), registries=fresh_registries)
        ship.recalculate_stats()
        assert ship._stats_dirty is False

        ship.mark_stats_dirty()
        assert ship._stats_dirty is True

    def test_dirty_flag_causes_recalculate_to_run(self, fresh_registries):
        """After mark_stats_dirty(), recalculate_stats() should run the pipeline."""
        ship = Ship("Test", 0, 0, (255, 0, 0), registries=fresh_registries)
        ship.recalculate_stats()  # First run

        call_count = [0]
        original_calculate = ship.stats_calculator.calculate

        def counting_calculate(s):
            call_count[0] += 1
            return original_calculate(s)

        ship.stats_calculator.calculate = counting_calculate

        ship.mark_stats_dirty()
        ship.recalculate_stats()  # Should run because dirty

        assert call_count[0] == 1

    def test_invalidate_components_cache_sets_dirty(self, fresh_registries):
        """_invalidate_components_cache() should also set _stats_dirty."""
        ship = Ship("Test", 0, 0, (255, 0, 0), registries=fresh_registries)
        ship.recalculate_stats()
        assert ship._stats_dirty is False

        ship._invalidate_components_cache()
        assert ship._stats_dirty is True
