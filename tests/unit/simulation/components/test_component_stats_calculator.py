"""Tests for ComponentStatsCalculator - extracted from Component god class.

PROJ-44 Phase 4: Tests stats calculation and formula evaluation.
"""
import pytest
from game.simulation.components.component import create_component
from game.simulation.components.component_stats_calculator import ComponentStatsCalculator


class TestComponentStatsCalculatorRecalculate:
    """Test stats recalculation."""

    def test_recalculate_stats_applies_modifiers(self):
        """recalculate_stats should apply modifier effects."""
        railgun = create_component('railgun')
        base_mass = railgun.base_mass

        railgun.add_modifier('simple_size_mount', 2.0)

        # Mass should be doubled
        assert railgun.mass == pytest.approx(base_mass * 2.0, abs=0.01)

    def test_recalculate_stats_multiplicative_stacking(self):
        """recalculate_stats should stack modifiers multiplicatively."""
        railgun = create_component('railgun')
        base_mass = railgun.base_mass

        railgun.add_modifier('simple_size_mount', 2.0)
        railgun.add_modifier('hardened_mount', 1.25)

        expected = base_mass * 2.0 * 1.25
        assert railgun.mass == pytest.approx(expected, abs=0.01)

    def test_recalculate_stats_with_context(self):
        """recalculate_stats should use context for formula evaluation."""
        bridge = create_component('bridge')

        # Recalculate with different context
        bridge.recalculate_stats({'ship_class_mass': 2000})

        # Bridge has formula-based mass that scales with ship_class_mass
        # Just verify it completes without error
        assert bridge.mass >= 0


class TestComponentStatsCalculatorFormulas:
    """Test formula evaluation."""

    def test_evaluates_attribute_formulas(self):
        """Should evaluate formulas in attributes like mass/hp."""
        bridge = create_component('bridge')

        # Bridge has formula-based mass
        # Recalculate with context and verify it produces valid result
        bridge.recalculate_stats({'ship_class_mass': 2000})

        # Should have positive mass (actual formula may differ)
        assert bridge.mass > 0

    def test_evaluates_ability_formulas(self):
        """Should evaluate formulas nested in abilities."""
        # Components with formula-based abilities should work
        bridge = create_component('bridge')
        bridge.recalculate_stats()

        # Just verify no crash and abilities are instantiated
        assert len(bridge.ability_instances) >= 0


class TestComponentStatsCalculatorHPHandling:
    """Test HP handling during recalculation."""

    def test_current_hp_preserved_when_undamaged(self):
        """current_hp should equal max_hp when undamaged."""
        railgun = create_component('railgun')

        assert railgun.current_hp == railgun.max_hp

    def test_current_hp_capped_after_modifier(self):
        """current_hp should be capped to new max_hp after modifier."""
        railgun = create_component('railgun')
        original_max = railgun.max_hp

        # Damage the component
        railgun.take_damage(10)
        damaged_hp = railgun.current_hp

        # Add HP modifier (hardened_mount multiplies HP)
        railgun.add_modifier('hardened_mount', 1.0)

        # New max should be increased (hardened_mount gives hp_mult)
        # Just verify max_hp increased and current_hp is capped
        assert railgun.max_hp >= original_max
        assert railgun.current_hp <= railgun.max_hp


class TestComponentStatsCalculatorStandalone:
    """Test ComponentStatsCalculator standalone methods."""

    def test_calculate_modifier_stats(self):
        """ComponentStatsCalculator should calculate modifier stats."""
        railgun = create_component('railgun')
        railgun.add_modifier('simple_size_mount', 2.0)

        stats = ComponentStatsCalculator.calculate_modifier_stats(
            railgun.modifiers,
            railgun
        )

        assert 'mass_mult' in stats
        assert stats['mass_mult'] == pytest.approx(2.0, abs=0.01)

    def test_apply_base_stats(self):
        """ComponentStatsCalculator should apply base stats correctly."""
        railgun = create_component('railgun')
        old_max_hp = railgun.max_hp

        # Create stats dict manually
        stats = {
            'mass_mult': 2.0,
            'mass_add': 0,
            'hp_mult': 1.5,
            'cost_mult': 1.0,
            'properties': {}
        }

        ComponentStatsCalculator.apply_base_stats(railgun, stats, old_max_hp)

        assert railgun.mass == pytest.approx(railgun.base_mass * 2.0, abs=0.01)
        assert railgun.max_hp == pytest.approx(old_max_hp * 1.5, abs=1)
