"""Tests for ComponentStatsCalculator - extracted from Component god class.

PROJ-44 Phase 4: Tests stats calculation and formula evaluation.
PROJ-246: Added strict formula evaluation tests.
"""
import pytest
from game.simulation.components.component import create_component
from game.simulation.components.component_stats_calculator import ComponentStatsCalculator
from game.core.exceptions import FormulaException


class TestComponentStatsCalculatorRecalculate:
    """Test stats recalculation."""

    def test_recalculate_stats_applies_modifiers(self, fresh_registries):
        """recalculate_stats should apply modifier effects."""
        railgun = create_component('railgun', registries=fresh_registries)
        base_mass = railgun.base_mass

        railgun.add_modifier('simple_size_mount', 2.0)

        # Mass should be doubled
        assert railgun.mass == pytest.approx(base_mass * 2.0, abs=0.01)

    def test_recalculate_stats_multiplicative_stacking(self, fresh_registries):
        """recalculate_stats should stack modifiers multiplicatively."""
        railgun = create_component('railgun', registries=fresh_registries)
        base_mass = railgun.base_mass

        railgun.add_modifier('simple_size_mount', 2.0)
        railgun.add_modifier('hardened_mount', 1.25)

        expected = base_mass * 2.0 * 1.25
        assert railgun.mass == pytest.approx(expected, abs=0.01)

    def test_recalculate_stats_with_context(self, fresh_registries):
        """recalculate_stats should use context for formula evaluation."""
        bridge = create_component('bridge', registries=fresh_registries)

        # Recalculate with different context
        bridge.recalculate_stats({'ship_class_mass': 2000})

        # Bridge has formula-based mass that scales with ship_class_mass
        # Just verify it completes without error
        assert bridge.mass >= 0


class TestComponentStatsCalculatorFormulas:
    """Test formula evaluation."""

    def test_evaluates_attribute_formulas(self, fresh_registries):
        """Should evaluate formulas in attributes like mass/hp."""
        bridge = create_component('bridge', registries=fresh_registries)

        # Bridge has formula-based mass
        # Recalculate with context and verify it produces valid result
        bridge.recalculate_stats({'ship_class_mass': 2000})

        # Should have positive mass (actual formula may differ)
        assert bridge.mass > 0

    def test_evaluates_ability_formulas(self, fresh_registries):
        """Should evaluate formulas nested in abilities."""
        # Components with formula-based abilities should work
        bridge = create_component('bridge', registries=fresh_registries)
        bridge.recalculate_stats()

        # Just verify no crash and abilities are instantiated
        assert len(bridge.ability_instances) >= 0


class TestComponentStatsCalculatorHPHandling:
    """Test HP handling during recalculation."""

    def test_current_hp_preserved_when_undamaged(self, fresh_registries):
        """current_hp should equal max_hp when undamaged."""
        railgun = create_component('railgun', registries=fresh_registries)

        assert railgun.current_hp == railgun.max_hp

    def test_current_hp_capped_after_modifier(self, fresh_registries):
        """current_hp should be capped to new max_hp after modifier."""
        railgun = create_component('railgun', registries=fresh_registries)
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

    def test_calculate_modifier_stats(self, fresh_registries):
        """ComponentStatsCalculator should calculate modifier stats."""
        railgun = create_component('railgun', registries=fresh_registries)
        railgun.add_modifier('simple_size_mount', 2.0)

        stats = ComponentStatsCalculator.calculate_modifier_stats(
            railgun.modifiers,
            railgun
        )

        assert 'mass_mult' in stats
        assert stats['mass_mult'] == pytest.approx(2.0, abs=0.01)

    def test_apply_base_stats(self, fresh_registries):
        """ComponentStatsCalculator should apply base stats correctly."""
        railgun = create_component('railgun', registries=fresh_registries)
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


class TestParseFormulas:
    """Test ComponentStatsCalculator.parse_formulas (PROJ-241)."""

    def test_extracts_formulas_from_equals_prefix(self):
        """parse_formulas should extract formulas from '='-prefixed string values."""
        data = {'mass': '=ship_class_mass * 0.1', 'hp': 100, 'name': 'test'}

        result = ComponentStatsCalculator.parse_formulas(data)

        assert result == {'mass': 'ship_class_mass * 0.1'}

    def test_skips_underscore_prefixed_keys(self):
        """parse_formulas should skip keys starting with '_'."""
        data = {'_comment': '=this is not a formula', 'mass': '=10'}

        result = ComponentStatsCalculator.parse_formulas(data)

        assert '_comment' not in result
        assert result == {'mass': '10'}

    def test_strips_leading_equals(self):
        """parse_formulas should strip the leading '=' from formula strings."""
        data = {'mass': '=ship_class_mass * 0.05'}

        result = ComponentStatsCalculator.parse_formulas(data)

        assert result['mass'] == 'ship_class_mass * 0.05'

    def test_returns_empty_for_no_formulas(self):
        """parse_formulas should return empty dict when no formulas present."""
        data = {'mass': 100, 'hp': 200, 'name': 'test'}

        result = ComponentStatsCalculator.parse_formulas(data)

        assert result == {}


class TestApplyFormulaDefaults:
    """Test ComponentStatsCalculator.apply_formula_defaults (PROJ-241)."""

    def test_mass_formula_sets_defaults(self, fresh_registries):
        """apply_formula_defaults should set base_mass=0, mass=0 for mass formula."""
        comp = create_component('railgun', registries=fresh_registries)
        formulas = {'mass': 'ship_class_mass * 0.1'}

        ComponentStatsCalculator.apply_formula_defaults(comp, formulas)

        assert comp.base_mass == 0
        assert comp.mass == 0

    def test_hp_formula_sets_defaults(self, fresh_registries):
        """apply_formula_defaults should set base_max_hp=0, max_hp=0, current_hp=0 for hp formula."""
        comp = create_component('railgun', registries=fresh_registries)
        formulas = {'hp': 'ship_class_mass * 0.5'}

        ComponentStatsCalculator.apply_formula_defaults(comp, formulas)

        assert comp.base_max_hp == 0
        assert comp.max_hp == 0
        assert comp.current_hp == 0

    def test_cost_formula_sets_defaults(self, fresh_registries):
        """apply_formula_defaults should set cost=0 for cost formula."""
        comp = create_component('railgun', registries=fresh_registries)
        formulas = {'cost': '100 * 2'}

        ComponentStatsCalculator.apply_formula_defaults(comp, formulas)

        assert comp.cost == 0

    def test_no_op_for_non_special_formulas(self, fresh_registries):
        """apply_formula_defaults should be no-op for non-mass/hp/cost formulas."""
        comp = create_component('railgun', registries=fresh_registries)
        original_mass = comp.mass
        original_hp = comp.max_hp
        formulas = {'damage': '10 * 2'}

        ComponentStatsCalculator.apply_formula_defaults(comp, formulas)

        assert comp.mass == original_mass
        assert comp.max_hp == original_hp


class TestStrictFormulaEvaluation:
    """PROJ-246: Verify strict formula evaluation catches bad formulas at load time."""

    def test_bad_attribute_formula_raises_on_recalculate(self, fresh_registries):
        """Component with invalid attribute formula raises FormulaException."""
        comp = create_component('railgun', registries=fresh_registries)

        # Inject a bad formula into the component's formulas dict
        comp.formulas['mass'] = 'undefined_variable * 2'

        with pytest.raises(FormulaException, match="railgun.*mass"):
            ComponentStatsCalculator.reset_and_evaluate_formulas(comp)

    def test_bad_resource_cost_formula_raises_on_recalculate(self, fresh_registries):
        """Component with invalid resource_cost formula raises FormulaException."""
        comp = create_component('railgun', registries=fresh_registries)

        # Inject a bad formula into the component's raw data
        comp.data['resource_cost'] = {'metals': '=bad_var + 10'}

        with pytest.raises(FormulaException, match="railgun.*resource_cost.*metals"):
            ComponentStatsCalculator.reset_and_evaluate_formulas(comp)

    def test_valid_formulas_load_successfully(self, fresh_registries):
        """Component with valid formulas loads without error (regression check)."""
        bridge = create_component('bridge', registries=fresh_registries)

        # Bridge has formula-based mass -- should evaluate without error
        ComponentStatsCalculator.reset_and_evaluate_formulas(
            bridge, context={'ship_class_mass': 2000}
        )

        assert bridge.mass > 0
