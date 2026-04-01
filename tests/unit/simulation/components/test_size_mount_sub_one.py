"""Tests for Size Mount below 1.0 functionality.

Phase 1: Verify size_mount can go below 1.0 with correct scaling.
- Minimum value is 0.1
- cost_mult uses param ^ 0.75 formula (non-linear)
- All other stats scale linearly with param
"""
import pytest
from game.simulation.components.component import create_component


class TestSizeMountMinimum:
    """Test that size_mount allows sub-1.0 values."""

    def test_size_mount_min_is_0_1(self, fresh_registries):
        """Size mount minimum should be 0.1, not 1.0."""
        mod_def = fresh_registries.modifiers.get('simple_size_mount')
        assert mod_def is not None
        assert mod_def.min_val == 0.1

    def test_size_mount_at_0_2_mass_scales_linearly(self, fresh_registries):
        """At size 0.2, mass should be 20% of base."""
        railgun = create_component('railgun', registries=fresh_registries)
        base_mass = railgun.base_mass

        railgun.add_modifier('simple_size_mount', 0.2)
        railgun.recalculate_stats()

        assert railgun.mass == pytest.approx(base_mass * 0.2, rel=0.01)

    def test_size_mount_at_0_2_hp_scales_linearly(self, fresh_registries):
        """At size 0.2, HP should be 20% of base."""
        railgun = create_component('railgun', registries=fresh_registries)
        base_hp = railgun.base_max_hp

        railgun.add_modifier('simple_size_mount', 0.2)
        railgun.recalculate_stats()

        assert railgun.max_hp == int(base_hp * 0.2)

    def test_size_mount_at_0_5_mass_scales_linearly(self, fresh_registries):
        """At size 0.5, mass should be 50% of base."""
        railgun = create_component('railgun', registries=fresh_registries)
        base_mass = railgun.base_mass

        railgun.add_modifier('simple_size_mount', 0.5)
        railgun.recalculate_stats()

        assert railgun.mass == pytest.approx(base_mass * 0.5, rel=0.01)


class TestSizeMountCostFormula:
    """Test non-linear cost scaling: cost_mult = param ^ 0.75."""

    def test_cost_at_size_0_2(self, fresh_registries):
        """At size 0.2, cost should be ~30% (0.2^0.75 ≈ 0.299)."""
        mod_def = fresh_registries.modifiers.get('simple_size_mount')

        effects = mod_def.evaluate_effects(0.2)
        cost_effect = next(e for e in effects if e.stat_key == 'cost_mult')

        expected = 0.2 ** 0.75
        assert cost_effect.value == pytest.approx(expected, rel=0.01)

    def test_cost_at_size_0_5(self, fresh_registries):
        """At size 0.5, cost should be ~59% (0.5^0.75 ≈ 0.594)."""
        mod_def = fresh_registries.modifiers.get('simple_size_mount')

        effects = mod_def.evaluate_effects(0.5)
        cost_effect = next(e for e in effects if e.stat_key == 'cost_mult')

        expected = 0.5 ** 0.75
        assert cost_effect.value == pytest.approx(expected, rel=0.01)

    def test_cost_at_size_1_is_1(self, fresh_registries):
        """At size 1.0, cost should still be 1.0 (1^0.75 = 1)."""
        mod_def = fresh_registries.modifiers.get('simple_size_mount')

        effects = mod_def.evaluate_effects(1.0)
        cost_effect = next(e for e in effects if e.stat_key == 'cost_mult')

        assert cost_effect.value == pytest.approx(1.0, rel=0.01)

    def test_cost_at_size_2(self, fresh_registries):
        """At size 2.0, cost should be ~168% (2^0.75 ≈ 1.682)."""
        mod_def = fresh_registries.modifiers.get('simple_size_mount')

        effects = mod_def.evaluate_effects(2.0)
        cost_effect = next(e for e in effects if e.stat_key == 'cost_mult')

        expected = 2.0 ** 0.75
        assert cost_effect.value == pytest.approx(expected, rel=0.01)

    def test_mass_still_linear_at_0_2(self, fresh_registries):
        """Mass should remain linear (param) even with new cost formula."""
        mod_def = fresh_registries.modifiers.get('simple_size_mount')

        effects = mod_def.evaluate_effects(0.2)
        mass_effect = next(e for e in effects if e.stat_key == 'mass_mult')

        assert mass_effect.value == pytest.approx(0.2, rel=0.01)


class TestSmartFloorSubOne:
    """Test smart_floor logic allows values below 1.0."""

    def test_snap_down_from_1_to_0_9(self):
        """Decrementing from 1.0 by 0.1 should give 0.9, not clamp at 1.0."""
        from game.ui.screens.builder.modifier_logic import ModifierLogic

        result = ModifierLogic.calculate_snap_value(
            current=1.0, step=0.1, direction=-1,
            min_val=0.1, max_val=1024.0, smart_floor=True
        )
        assert result == pytest.approx(0.9, abs=0.01)

    def test_snap_down_from_0_2_to_0_1(self):
        """Decrementing from 0.2 by 0.1 should give 0.1."""
        from game.ui.screens.builder.modifier_logic import ModifierLogic

        result = ModifierLogic.calculate_snap_value(
            current=0.2, step=0.1, direction=-1,
            min_val=0.1, max_val=1024.0, smart_floor=True
        )
        assert result == pytest.approx(0.1, abs=0.01)

    def test_snap_down_from_0_1_clamps_at_min(self):
        """Decrementing from 0.1 should clamp at 0.1 (min_val)."""
        from game.ui.screens.builder.modifier_logic import ModifierLogic

        result = ModifierLogic.calculate_snap_value(
            current=0.1, step=0.1, direction=-1,
            min_val=0.1, max_val=1024.0, smart_floor=True
        )
        assert result == pytest.approx(0.1, abs=0.01)

    def test_snap_down_by_1_from_1_stays_at_min(self):
        """Decrementing from 1.0 by 1.0 step with smart_floor should clamp at 0.1."""
        from game.ui.screens.builder.modifier_logic import ModifierLogic

        result = ModifierLogic.calculate_snap_value(
            current=1.0, step=1.0, direction=-1,
            min_val=0.1, max_val=1024.0, smart_floor=True
        )
        # current (1.0) <= step (1.0) and direction < 0, so smart_floor activates
        assert result >= 0.1
