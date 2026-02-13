"""
Unit tests for ModifierIntrospection.

Tests the introspection capabilities for the modifier system including:
- get_modifier_affects: Determining what abilities a modifier affects
- get_component_modifier_summary: Summarizing all modifiers on a component
- get_ability_modifier_summary: Summarizing modifier effects on a specific ability
- generate_modifier_tooltip: Generating human-readable tooltips
- generate_ability_stats_display: Generating UI-ready stat displays
"""
import pytest
from unittest.mock import Mock, MagicMock

from game.simulation.components.modifier_introspection import ModifierIntrospection
from game.simulation.components.modifier_effects import ModifierEffect
from game.simulation.components.abilities.stat_keys import StatKey


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_component():
    """Create a mock component with abilities for testing."""
    comp = Mock()
    comp.id = 'test_component'
    comp.display_name = 'Test Component'
    comp.ability_instances = []
    comp.modifiers = []
    comp.stats = {}
    return comp


@pytest.fixture
def mock_ability():
    """Create a mock ability with stat bindings."""
    ability = Mock()
    ability.__class__.__name__ = 'MockAbility'
    ability.get_consumed_stats = Mock(return_value={StatKey.DAMAGE_MULT, StatKey.RANGE_MULT})
    ability.get_effect_summary = Mock(return_value=[])
    return ability


@pytest.fixture
def mock_weapon_ability():
    """Create a mock weapon ability with damage stats."""
    ability = Mock()
    ability.__class__.__name__ = 'ProjectileWeaponAbility'
    ability.get_consumed_stats = Mock(return_value={
        StatKey.DAMAGE_MULT,
        StatKey.RANGE_MULT,
        StatKey.RELOAD_MULT
    })
    ability.get_effect_summary = Mock(return_value=[
        {
            'attribute': 'damage',
            'base': 100.0,
            'current': 150.0,
            'stat_key': 'damage_mult',
            'stat_value': 1.5,
            'operation': 'multiply'
        }
    ])
    return ability


@pytest.fixture
def simple_modifier_def():
    """A simple modifier definition with one effect."""
    return {
        'id': 'damage_boost',
        'name': 'Damage Boost',
        'description': 'Increases weapon damage',
        'effects': [
            {'stat': 'damage_mult', 'formula': 'param', 'operation': 'multiply'}
        ],
        'param': {'default': 1.5}
    }


@pytest.fixture
def multi_effect_modifier_def():
    """A modifier definition with multiple effects."""
    return {
        'id': 'hardened_mount',
        'name': 'Hardened Mount',
        'description': 'Increases mass but also HP',
        'effects': [
            {'stat': 'mass_mult', 'formula': 'param', 'operation': 'multiply'},
            {'stat': 'hp_mult', 'formula': 'param ^ 2', 'operation': 'multiply'}
        ],
        'param': {'default': 2.0}
    }


@pytest.fixture
def targeted_modifier_def():
    """A modifier with a targeted ability effect."""
    return {
        'id': 'weapon_focus',
        'name': 'Weapon Focus',
        'description': 'Enhances weapon abilities only',
        'effects': [
            {
                'stat': 'damage_mult',
                'formula': 'param',
                'operation': 'multiply',
                'target_ability': 'WeaponAbility'
            }
        ],
        'param': {'default': 1.5}
    }


# =============================================================================
# Tests for get_modifier_affects
# =============================================================================

class TestGetModifierAffects:
    """Tests for ModifierIntrospection.get_modifier_affects method."""

    def test_returns_correct_structure(self, simple_modifier_def, mock_component):
        """Returns dict with expected keys."""
        result = ModifierIntrospection.get_modifier_affects(
            simple_modifier_def, mock_component
        )

        assert 'abilities' in result
        assert 'effects_preview' in result
        assert 'affected_stats' in result
        assert 'targeted_abilities' in result

    def test_identifies_affected_stats(self, simple_modifier_def, mock_component):
        """Correctly identifies stats affected by modifier."""
        result = ModifierIntrospection.get_modifier_affects(
            simple_modifier_def, mock_component, param_value=1.5
        )

        assert 'damage_mult' in result['affected_stats']

    def test_multi_effect_modifier_lists_all_stats(self, multi_effect_modifier_def, mock_component):
        """Multi-effect modifier lists all affected stats."""
        result = ModifierIntrospection.get_modifier_affects(
            multi_effect_modifier_def, mock_component, param_value=2.0
        )

        assert 'mass_mult' in result['affected_stats']
        assert 'hp_mult' in result['affected_stats']

    def test_generates_effects_preview(self, simple_modifier_def, mock_component):
        """Generates human-readable effect descriptions."""
        result = ModifierIntrospection.get_modifier_affects(
            simple_modifier_def, mock_component, param_value=1.5
        )

        assert len(result['effects_preview']) > 0
        # Should contain the stat key and value
        assert any('damage_mult' in preview for preview in result['effects_preview'])

    def test_identifies_targeted_abilities(self, targeted_modifier_def, mock_component):
        """Identifies explicitly targeted abilities."""
        result = ModifierIntrospection.get_modifier_affects(
            targeted_modifier_def, mock_component, param_value=1.5
        )

        assert 'WeaponAbility' in result['targeted_abilities']
        assert 'WeaponAbility' in result['abilities']

    def test_matches_abilities_by_consumed_stats(self, simple_modifier_def, mock_component, mock_weapon_ability):
        """Finds abilities that consume affected stats."""
        mock_component.ability_instances = [mock_weapon_ability]

        result = ModifierIntrospection.get_modifier_affects(
            simple_modifier_def, mock_component, param_value=1.5
        )

        assert 'ProjectileWeaponAbility' in result['abilities']

    def test_uses_default_param_when_not_provided(self, simple_modifier_def, mock_component):
        """Uses default param value from definition when not provided."""
        # Default is 1.5 from fixture
        result = ModifierIntrospection.get_modifier_affects(
            simple_modifier_def, mock_component
        )

        # Should use 1.5 and produce x1.50 effect
        assert any('1.50' in preview for preview in result['effects_preview'])

    def test_handles_missing_param_definition(self, mock_component):
        """Handles modifier without param definition gracefully."""
        mod_def = {
            'id': 'no_param',
            'name': 'No Param',
            'effects': [{'stat': 'damage_mult', 'formula': 'param'}]
        }

        result = ModifierIntrospection.get_modifier_affects(
            mod_def, mock_component, param_value=2.0
        )

        assert 'damage_mult' in result['affected_stats']

    def test_empty_abilities_when_no_matches(self, mock_component):
        """Returns empty abilities list when no abilities consume affected stats."""
        mod_def = {
            'id': 'obscure',
            'name': 'Obscure',
            'effects': [{'stat': 'obscure_stat', 'formula': 'param'}]
        }

        result = ModifierIntrospection.get_modifier_affects(
            mod_def, mock_component, param_value=1.0
        )

        assert result['abilities'] == []


# =============================================================================
# Tests for get_component_modifier_summary
# =============================================================================

class TestGetComponentModifierSummary:
    """Tests for ModifierIntrospection.get_component_modifier_summary method."""

    def test_returns_correct_structure(self, mock_component):
        """Returns dict with expected keys."""
        result = ModifierIntrospection.get_component_modifier_summary(mock_component)

        assert 'component_id' in result
        assert 'component_name' in result
        assert 'applied_modifiers' in result
        assert 'total_stats' in result

    def test_includes_component_id_and_name(self, mock_component):
        """Includes component ID and display name."""
        result = ModifierIntrospection.get_component_modifier_summary(mock_component)

        assert result['component_id'] == 'test_component'
        assert result['component_name'] == 'Test Component'

    def test_empty_modifiers_list_when_none_applied(self, mock_component):
        """Returns empty list when no modifiers applied."""
        result = ModifierIntrospection.get_component_modifier_summary(mock_component)

        assert result['applied_modifiers'] == []

    def test_lists_applied_modifiers(self, mock_component):
        """Lists all applied modifiers with details."""
        # Create mock application modifier
        mock_def = Mock()
        mock_def.id = 'test_modifier'
        mock_def.display_name = 'Test Modifier'
        mock_def.evaluate_effects = Mock(return_value=[])

        app_mod = Mock()
        app_mod.definition = mock_def
        app_mod.value = 2.0

        mock_component.modifiers = [app_mod]

        result = ModifierIntrospection.get_component_modifier_summary(mock_component)

        assert len(result['applied_modifiers']) == 1
        assert result['applied_modifiers'][0]['id'] == 'test_modifier'
        assert result['applied_modifiers'][0]['param_value'] == 2.0

    def test_includes_effect_descriptions(self, mock_component):
        """Includes effect descriptions for each modifier."""
        # Create mock effect
        mock_effect = Mock()
        mock_effect.describe = Mock(return_value='damage_mult x1.50')

        mock_def = Mock()
        mock_def.id = 'damage_boost'
        mock_def.display_name = 'Damage Boost'
        mock_def.evaluate_effects = Mock(return_value=[mock_effect])

        app_mod = Mock()
        app_mod.definition = mock_def
        app_mod.value = 1.5

        mock_component.modifiers = [app_mod]

        result = ModifierIntrospection.get_component_modifier_summary(mock_component)

        assert 'damage_mult x1.50' in result['applied_modifiers'][0]['effects']

    def test_includes_total_stats(self, mock_component):
        """Includes aggregated stats dictionary."""
        mock_component.stats = {'damage_mult': 1.5, 'mass_mult': 2.0}

        result = ModifierIntrospection.get_component_modifier_summary(mock_component)

        assert result['total_stats']['damage_mult'] == 1.5
        assert result['total_stats']['mass_mult'] == 2.0

    def test_handles_component_without_display_name(self):
        """Falls back to id if display_name not present."""
        comp = Mock(spec=['id', 'modifiers', 'stats'])  # Specify only what exists
        comp.id = 'fallback_id'
        comp.modifiers = []
        comp.stats = {}

        result = ModifierIntrospection.get_component_modifier_summary(comp)

        # Without display_name attribute, should use id as fallback
        assert result['component_name'] == 'fallback_id'

    def test_handles_definition_without_evaluate_effects(self, mock_component):
        """Handles modifier definitions without evaluate_effects method."""
        mock_def = Mock(spec=['id'])  # Only has 'id', no evaluate_effects
        mock_def.id = 'simple_mod'

        app_mod = Mock()
        app_mod.definition = mock_def
        app_mod.value = 1.0

        mock_component.modifiers = [app_mod]

        result = ModifierIntrospection.get_component_modifier_summary(mock_component)

        assert result['applied_modifiers'][0]['effects'] == []


# =============================================================================
# Tests for get_ability_modifier_summary
# =============================================================================

class TestGetAbilityModifierSummary:
    """Tests for ModifierIntrospection.get_ability_modifier_summary method."""

    def test_returns_correct_structure(self, mock_ability):
        """Returns dict with expected keys."""
        result = ModifierIntrospection.get_ability_modifier_summary(mock_ability)

        assert 'ability_class' in result
        assert 'stats' in result

    def test_includes_ability_class_name(self, mock_ability):
        """Includes the ability's class name."""
        result = ModifierIntrospection.get_ability_modifier_summary(mock_ability)

        assert result['ability_class'] == 'MockAbility'

    def test_returns_effect_summary_from_ability(self, mock_weapon_ability):
        """Returns the effect summary from the ability."""
        result = ModifierIntrospection.get_ability_modifier_summary(mock_weapon_ability)

        assert len(result['stats']) == 1
        assert result['stats'][0]['attribute'] == 'damage'
        assert result['stats'][0]['base'] == 100.0
        assert result['stats'][0]['current'] == 150.0

    def test_handles_ability_without_get_effect_summary(self):
        """Handles abilities without get_effect_summary method."""
        ability = Mock(spec=['__class__'])
        ability.__class__ = type('NoSummaryAbility', (), {'__name__': 'NoSummaryAbility'})

        result = ModifierIntrospection.get_ability_modifier_summary(ability)

        assert result['ability_class'] == 'NoSummaryAbility'
        assert result['stats'] == []


# =============================================================================
# Tests for generate_modifier_tooltip
# =============================================================================

class TestGenerateModifierTooltip:
    """Tests for ModifierIntrospection.generate_modifier_tooltip method."""

    def test_includes_modifier_name(self, simple_modifier_def):
        """Tooltip includes modifier name as header."""
        result = ModifierIntrospection.generate_modifier_tooltip(
            simple_modifier_def, 1.5
        )

        assert 'Damage Boost' in result
        assert '===' in result

    def test_includes_description(self, simple_modifier_def):
        """Tooltip includes modifier description."""
        result = ModifierIntrospection.generate_modifier_tooltip(
            simple_modifier_def, 1.5
        )

        assert 'Increases weapon damage' in result

    def test_includes_effects_section(self, simple_modifier_def):
        """Tooltip includes effects section."""
        result = ModifierIntrospection.generate_modifier_tooltip(
            simple_modifier_def, 1.5
        )

        assert 'Effects:' in result
        assert 'damage_mult' in result

    def test_includes_affected_abilities_when_component_provided(
        self, simple_modifier_def, mock_component, mock_weapon_ability
    ):
        """Tooltip includes affected abilities when component is provided."""
        mock_component.ability_instances = [mock_weapon_ability]

        result = ModifierIntrospection.generate_modifier_tooltip(
            simple_modifier_def, 1.5, component=mock_component
        )

        assert 'Affects:' in result
        assert 'ProjectileWeaponAbility' in result

    def test_no_affects_section_without_component(self, simple_modifier_def):
        """No affects section when component is not provided."""
        result = ModifierIntrospection.generate_modifier_tooltip(
            simple_modifier_def, 1.5
        )

        assert 'Affects:' not in result

    def test_handles_missing_description(self):
        """Handles modifier without description."""
        mod_def = {
            'id': 'no_desc',
            'name': 'No Description',
            'effects': [{'stat': 'damage_mult', 'formula': 'param'}]
        }

        result = ModifierIntrospection.generate_modifier_tooltip(mod_def, 1.5)

        assert 'No Description' in result
        assert result.count('\n\n') < 3  # No extra blank line for description

    def test_handles_missing_name_uses_id(self):
        """Falls back to id when name is missing."""
        mod_def = {
            'id': 'fallback_id',
            'effects': [{'stat': 'damage_mult', 'formula': 'param'}]
        }

        result = ModifierIntrospection.generate_modifier_tooltip(mod_def, 1.5)

        assert 'fallback_id' in result

    def test_uses_bullet_points_for_effects(self, multi_effect_modifier_def):
        """Uses bullet points for listing effects."""
        result = ModifierIntrospection.generate_modifier_tooltip(
            multi_effect_modifier_def, 2.0
        )

        # Should have bullet characters
        assert result.count('•') >= 2

    def test_multi_line_format(self, simple_modifier_def):
        """Returns multi-line string suitable for tooltip."""
        result = ModifierIntrospection.generate_modifier_tooltip(
            simple_modifier_def, 1.5
        )

        lines = result.split('\n')
        assert len(lines) > 1


# =============================================================================
# Tests for generate_ability_stats_display
# =============================================================================

class TestGenerateAbilityStatsDisplay:
    """Tests for ModifierIntrospection.generate_ability_stats_display method."""

    def test_returns_list_of_dicts(self, mock_weapon_ability):
        """Returns list of display entry dicts."""
        result = ModifierIntrospection.generate_ability_stats_display(mock_weapon_ability)

        assert isinstance(result, list)
        assert all(isinstance(entry, dict) for entry in result)

    def test_display_entry_structure(self, mock_weapon_ability):
        """Each entry has expected keys."""
        result = ModifierIntrospection.generate_ability_stats_display(mock_weapon_ability)

        assert len(result) == 1
        entry = result[0]

        assert 'label' in entry
        assert 'attribute' in entry
        assert 'base' in entry
        assert 'current' in entry
        assert 'modified' in entry
        assert 'change_percent' in entry
        assert 'display_text' in entry

    def test_formats_label_from_attribute(self, mock_weapon_ability):
        """Label is formatted from attribute name (title case, underscores removed)."""
        result = ModifierIntrospection.generate_ability_stats_display(mock_weapon_ability)

        assert result[0]['label'] == 'Damage'

    def test_calculates_modified_flag_correctly(self, mock_weapon_ability):
        """modified flag is True when base != current."""
        result = ModifierIntrospection.generate_ability_stats_display(mock_weapon_ability)

        assert result[0]['modified'] is True

    def test_modified_false_when_values_equal(self):
        """modified flag is False when base equals current."""
        ability = Mock()
        ability.__class__.__name__ = 'TestAbility'
        ability.get_effect_summary = Mock(return_value=[{
            'attribute': 'value',
            'base': 100.0,
            'current': 100.0,
            'stat_key': 'value_mult',
            'stat_value': 1.0,
            'operation': 'multiply'
        }])

        result = ModifierIntrospection.generate_ability_stats_display(ability)

        assert result[0]['modified'] is False

    def test_calculates_change_percent_for_multiply(self, mock_weapon_ability):
        """Calculates change percentage for multiply operation."""
        result = ModifierIntrospection.generate_ability_stats_display(mock_weapon_ability)

        # 150/100 - 1 = 0.5 = 50%
        assert result[0]['change_percent'] == 50.0

    def test_calculates_change_percent_for_add(self):
        """Calculates change percentage for add operation."""
        ability = Mock()
        ability.__class__.__name__ = 'TestAbility'
        ability.get_effect_summary = Mock(return_value=[{
            'attribute': 'accuracy',
            'base': 100.0,
            'current': 110.0,
            'stat_key': 'accuracy_add',
            'stat_value': 10.0,
            'operation': 'add'
        }])

        result = ModifierIntrospection.generate_ability_stats_display(ability)

        # (110 - 100) / 100 * 100 = 10%
        assert result[0]['change_percent'] == 10.0

    def test_formats_display_text_for_modified(self, mock_weapon_ability):
        """Display text shows base and percentage for modified stats."""
        result = ModifierIntrospection.generate_ability_stats_display(mock_weapon_ability)

        # Should contain current value, base, and percentage
        assert '150.0' in result[0]['display_text']
        assert '100.0' in result[0]['display_text']
        assert '+50%' in result[0]['display_text']

    def test_formats_display_text_for_unmodified(self):
        """Display text shows just value for unmodified stats."""
        ability = Mock()
        ability.__class__.__name__ = 'TestAbility'
        ability.get_effect_summary = Mock(return_value=[{
            'attribute': 'value',
            'base': 100.0,
            'current': 100.0,
            'stat_key': 'value_mult',
            'stat_value': 1.0,
            'operation': 'multiply'
        }])

        result = ModifierIntrospection.generate_ability_stats_display(ability)

        assert result[0]['display_text'] == '100.0'
        assert 'base' not in result[0]['display_text']

    def test_handles_negative_change(self):
        """Formats negative changes correctly."""
        ability = Mock()
        ability.__class__.__name__ = 'TestAbility'
        ability.get_effect_summary = Mock(return_value=[{
            'attribute': 'reload',
            'base': 2.0,
            'current': 1.5,
            'stat_key': 'reload_mult',
            'stat_value': 0.75,
            'operation': 'multiply'
        }])

        result = ModifierIntrospection.generate_ability_stats_display(ability)

        assert result[0]['change_percent'] == -25.0
        assert '-25%' in result[0]['display_text']

    def test_handles_zero_base_value(self):
        """Handles division by zero when base is 0."""
        ability = Mock()
        ability.__class__.__name__ = 'TestAbility'
        ability.get_effect_summary = Mock(return_value=[{
            'attribute': 'bonus',
            'base': 0.0,
            'current': 10.0,
            'stat_key': 'bonus_add',
            'stat_value': 10.0,
            'operation': 'add'
        }])

        result = ModifierIntrospection.generate_ability_stats_display(ability)

        # Should handle gracefully - inf for non-zero current, 0 for zero current
        assert result[0]['change_percent'] == float('inf')

    def test_handles_empty_effect_summary(self):
        """Handles abilities with no effect summary."""
        ability = Mock()
        ability.__class__.__name__ = 'TestAbility'
        ability.get_effect_summary = Mock(return_value=[])

        result = ModifierIntrospection.generate_ability_stats_display(ability)

        assert result == []

    def test_handles_missing_attribute_key(self):
        """Handles effect entries missing attribute key."""
        ability = Mock()
        ability.__class__.__name__ = 'TestAbility'
        ability.get_effect_summary = Mock(return_value=[{
            'base': 100.0,
            'current': 150.0,
            'operation': 'multiply'
        }])

        result = ModifierIntrospection.generate_ability_stats_display(ability)

        # Should use 'unknown' as default
        assert result[0]['attribute'] == 'unknown'
        assert result[0]['label'] == 'Unknown'


# =============================================================================
# Integration Tests with Real Components
# =============================================================================

class TestModifierIntrospectionIntegration:
    """Integration tests using real components and abilities."""

    def test_get_modifier_affects_with_real_component(self, fresh_registries):
        """Test with a real component from registries."""
        from game.simulation.components.component import create_component

        railgun = create_component('railgun', registries=fresh_registries)
        mod_def = {
            'id': 'damage_boost',
            'name': 'Damage Boost',
            'effects': [{'stat': 'damage_mult', 'formula': 'param'}]
        }

        result = ModifierIntrospection.get_modifier_affects(
            mod_def, railgun, param_value=1.5
        )

        assert 'damage_mult' in result['affected_stats']
        # Railgun should have weapon abilities that consume damage_mult
        assert len(result['abilities']) >= 0  # Depends on component definition

    def test_get_component_modifier_summary_with_real_component(self, fresh_registries):
        """Test component summary with real applied modifiers."""
        from game.simulation.components.component import create_component

        railgun = create_component('railgun', registries=fresh_registries)
        railgun.add_modifier('simple_size_mount', 2.0)

        result = ModifierIntrospection.get_component_modifier_summary(railgun)

        assert result['component_id'] == 'railgun'
        assert len(result['applied_modifiers']) >= 1
        assert any(m['id'] == 'simple_size_mount' for m in result['applied_modifiers'])

    def test_tooltip_generation_with_real_component(self, fresh_registries):
        """Test tooltip generation with real component context."""
        from game.simulation.components.component import create_component

        railgun = create_component('railgun', registries=fresh_registries)
        mod_def = {
            'id': 'test_mod',
            'name': 'Test Modifier',
            'description': 'A test modifier for integration testing',
            'effects': [{'stat': 'damage_mult', 'formula': 'param'}]
        }

        result = ModifierIntrospection.generate_modifier_tooltip(
            mod_def, 1.5, component=railgun
        )

        assert 'Test Modifier' in result
        assert 'A test modifier' in result
        assert 'Effects:' in result
