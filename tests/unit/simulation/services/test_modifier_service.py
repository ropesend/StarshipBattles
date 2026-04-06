"""
Unit tests for ModifierService.

Tests the simulation-layer service for managing component modifiers including:
- Modifier allowance checks (restrictions, deny_types, allow_abilities)
- Mandatory modifier detection and application
- Initial value calculation
- Min/max value constraints

PROJ-118: Phase 2 comprehensive test coverage for simulation services.
"""
import pytest
from unittest.mock import MagicMock, PropertyMock

from game.core.exceptions import ValidationException
from game.simulation.services.modifier_service import ModifierService
from game.simulation.components.component_constants import Modifier


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_modifier_unrestricted():
    """Create a modifier with no restrictions."""
    return Modifier({
        'id': 'test_unrestricted',
        'name': 'Unrestricted Modifier',
        'param': {'min': 0.0, 'max': 100.0, 'default': 50.0},
        'restrictions': {},
        'effects': []
    })


@pytest.fixture
def mock_modifier_allow_types():
    """Create a modifier with allow_types restriction."""
    return Modifier({
        'id': 'weapon_only',
        'name': 'Weapon Only',
        'param': {'min': 0.0, 'max': 10.0, 'default': 1.0},
        'restrictions': {'allow_types': ['weapon']},
        'effects': []
    })


@pytest.fixture
def mock_modifier_deny_types():
    """Create a modifier with deny_types restriction."""
    return Modifier({
        'id': 'not_for_armor',
        'name': 'Not For Armor',
        'param': {'min': 0.0, 'max': 50.0, 'default': 25.0},
        'restrictions': {'deny_types': ['armor', 'shield']},
        'effects': []
    })


@pytest.fixture
def mock_modifier_allow_abilities():
    """Create a modifier with allow_abilities restriction."""
    return Modifier({
        'id': 'beam_only',
        'name': 'Beam Only',
        'param': {'min': 0.0, 'max': 5.0, 'default': 0.0},
        'restrictions': {'allow_abilities': ['BeamWeaponAbility']},
        'effects': []
    })


@pytest.fixture
def mock_turret_mount():
    """Create turret_mount modifier (has arc_set effect for generic detection)."""
    return Modifier({
        'id': 'turret_mount',
        'name': 'Turret Mount',
        'param': {'min': 15.0, 'max': 180.0, 'default': 45.0},
        'restrictions': {'allow_abilities': ['ProjectileWeaponAbility', 'BeamWeaponAbility']},
        'effects': [{'stat': 'arc_set', 'formula': 'param', 'operation': 'set'}]
    })


@pytest.fixture
def mock_simple_size_mount():
    """Create simple_size_mount modifier (has special handling)."""
    return Modifier({
        'id': 'simple_size_mount',
        'name': 'Size',
        'param': {'min': 1.0, 'max': 1024.0, 'default': 1.0},
        'restrictions': {},
        'effects': []
    })


@pytest.fixture
def mock_range_mount():
    """Create range_mount modifier (has special handling)."""
    return Modifier({
        'id': 'range_mount',
        'name': 'Range',
        'param': {'min': 0.0, 'max': 3.0, 'default': 0.0},
        'restrictions': {},
        'effects': []
    })


@pytest.fixture
def mock_facing():
    """Create facing modifier (has special handling)."""
    return Modifier({
        'id': 'facing',
        'name': 'Facing',
        'param': {'min': 0.0, 'max': 359.0, 'default': 0.0},
        'restrictions': {},
        'effects': []
    })


@pytest.fixture
def mock_precision_mount():
    """Create precision_mount modifier (has special handling)."""
    return Modifier({
        'id': 'precision_mount',
        'name': 'Precision',
        'param': {'min': 0.0, 'max': 5.0, 'default': 1.0},
        'restrictions': {},
        'effects': []
    })


@pytest.fixture
def mock_hardened_mount():
    """Create hardened_mount modifier (has special handling)."""
    return Modifier({
        'id': 'hardened_mount',
        'name': 'Hardened',
        'param': {'min': 0.5, 'max': 2.0, 'default': 1.0},
        'restrictions': {},
        'effects': []
    })


@pytest.fixture
def mock_efficiency_mount():
    """Create efficiency_mount modifier (has special handling)."""
    return Modifier({
        'id': 'efficiency_mount',
        'name': 'Efficiency',
        'param': {'min': 0.5, 'max': 2.0, 'default': 1.0},
        'restrictions': {},
        'effects': []
    })


@pytest.fixture
def mock_weapon_component():
    """Create a mock weapon component."""
    comp = MagicMock()
    comp.type_str = 'weapon'
    comp.abilities = {'ProjectileWeaponAbility': {}}
    comp.data = {
        'abilities': {
            'ProjectileWeaponAbility': {'firing_arc': 30}
        }
    }
    comp.modifiers = []
    comp.get_modifier = MagicMock(return_value=None)
    comp.add_modifier = MagicMock()
    return comp


@pytest.fixture
def mock_beam_component():
    """Create a mock beam weapon component."""
    comp = MagicMock()
    comp.type_str = 'weapon'
    comp.abilities = {'BeamWeaponAbility': {}}
    comp.data = {
        'abilities': {
            'BeamWeaponAbility': {'firing_arc': 45}
        }
    }
    comp.modifiers = []
    comp.get_modifier = MagicMock(return_value=None)
    comp.add_modifier = MagicMock()
    return comp


@pytest.fixture
def mock_engine_component():
    """Create a mock engine component."""
    comp = MagicMock()
    comp.type_str = 'engine'
    comp.abilities = {'ThrustAbility': {}}
    comp.data = {'abilities': {'ThrustAbility': {'thrust': 100}}}
    comp.modifiers = []
    comp.get_modifier = MagicMock(return_value=None)
    comp.add_modifier = MagicMock()
    return comp


@pytest.fixture
def mock_armor_component():
    """Create a mock armor component."""
    comp = MagicMock()
    comp.type_str = 'armor'
    comp.abilities = {'ArmorAbility': {}}
    comp.data = {'abilities': {'ArmorAbility': {}}}
    comp.modifiers = []
    comp.get_modifier = MagicMock(return_value=None)
    comp.add_modifier = MagicMock()
    return comp


@pytest.fixture
def basic_registry(mock_modifier_unrestricted, mock_simple_size_mount):
    """Create a minimal modifier registry."""
    return {
        'test_unrestricted': mock_modifier_unrestricted,
        'simple_size_mount': mock_simple_size_mount,
    }


@pytest.fixture
def full_registry(
    mock_modifier_unrestricted,
    mock_modifier_allow_types,
    mock_modifier_deny_types,
    mock_modifier_allow_abilities,
    mock_turret_mount,
    mock_simple_size_mount,
    mock_range_mount,
    mock_facing,
    mock_precision_mount,
    mock_hardened_mount,
    mock_efficiency_mount,
):
    """Create a complete modifier registry for comprehensive testing."""
    return {
        'test_unrestricted': mock_modifier_unrestricted,
        'weapon_only': mock_modifier_allow_types,
        'not_for_armor': mock_modifier_deny_types,
        'beam_only': mock_modifier_allow_abilities,
        'turret_mount': mock_turret_mount,
        'simple_size_mount': mock_simple_size_mount,
        'range_mount': mock_range_mount,
        'facing': mock_facing,
        'precision_mount': mock_precision_mount,
        'hardened_mount': mock_hardened_mount,
        'efficiency_mount': mock_efficiency_mount,
    }


# =============================================================================
# Test: Constructor and Initialization
# =============================================================================

class TestModifierServiceInit:
    """Tests for ModifierService initialization."""

    def test_init_with_valid_registry(self, basic_registry):
        """Service accepts a valid modifier registry."""
        service = ModifierService(modifier_registry=basic_registry)
        assert service._modifiers is basic_registry

    def test_init_with_none_raises_validation_exception(self):
        """Service raises ValidationException when registry is None."""
        with pytest.raises(ValidationException):
            ModifierService(modifier_registry=None)

    def test_init_with_empty_registry(self):
        """Service accepts an empty registry (edge case)."""
        service = ModifierService(modifier_registry={})
        assert service._modifiers == {}


# =============================================================================
# Test: is_modifier_allowed
# =============================================================================

class TestIsModifierAllowed:
    """Tests for is_modifier_allowed method."""

    def test_unknown_modifier_returns_false(self, basic_registry, mock_weapon_component):
        """Non-existent modifier returns False."""
        service = ModifierService(modifier_registry=basic_registry)
        assert service.is_modifier_allowed('nonexistent_mod', mock_weapon_component) is False

    def test_unrestricted_modifier_allowed_for_any_component(
        self, basic_registry, mock_weapon_component, mock_engine_component, mock_armor_component
    ):
        """Modifier with no restrictions is allowed for all components."""
        service = ModifierService(modifier_registry=basic_registry)
        assert service.is_modifier_allowed('test_unrestricted', mock_weapon_component) is True
        assert service.is_modifier_allowed('test_unrestricted', mock_engine_component) is True
        assert service.is_modifier_allowed('test_unrestricted', mock_armor_component) is True

    def test_allow_types_restriction_allows_matching_type(
        self, full_registry, mock_weapon_component
    ):
        """allow_types restriction allows matching component types."""
        service = ModifierService(modifier_registry=full_registry)
        assert service.is_modifier_allowed('weapon_only', mock_weapon_component) is True

    def test_allow_types_restriction_denies_non_matching_type(
        self, full_registry, mock_engine_component
    ):
        """allow_types restriction denies non-matching component types."""
        service = ModifierService(modifier_registry=full_registry)
        assert service.is_modifier_allowed('weapon_only', mock_engine_component) is False

    def test_deny_types_restriction_allows_non_matching_type(
        self, full_registry, mock_weapon_component, mock_engine_component
    ):
        """deny_types restriction allows non-matching component types."""
        service = ModifierService(modifier_registry=full_registry)
        assert service.is_modifier_allowed('not_for_armor', mock_weapon_component) is True
        assert service.is_modifier_allowed('not_for_armor', mock_engine_component) is True

    def test_deny_types_restriction_denies_matching_type(
        self, full_registry, mock_armor_component
    ):
        """deny_types restriction denies matching component types."""
        service = ModifierService(modifier_registry=full_registry)
        assert service.is_modifier_allowed('not_for_armor', mock_armor_component) is False

    def test_allow_abilities_restriction_allows_component_with_ability(
        self, full_registry, mock_beam_component
    ):
        """allow_abilities restriction allows component with matching ability."""
        service = ModifierService(modifier_registry=full_registry)
        assert service.is_modifier_allowed('beam_only', mock_beam_component) is True

    def test_allow_abilities_restriction_denies_component_without_ability(
        self, full_registry, mock_weapon_component
    ):
        """allow_abilities restriction denies component without matching ability."""
        service = ModifierService(modifier_registry=full_registry)
        # mock_weapon_component has ProjectileWeaponAbility, not BeamWeaponAbility
        assert service.is_modifier_allowed('beam_only', mock_weapon_component) is False

    def test_allow_abilities_checks_data_abilities_dict(self, full_registry):
        """allow_abilities also checks component.data['abilities'] dict."""
        comp = MagicMock()
        comp.type_str = 'weapon'
        comp.abilities = {}  # Empty abilities dict
        comp.data = {'abilities': {'BeamWeaponAbility': {'damage': 10}}}

        service = ModifierService(modifier_registry=full_registry)
        assert service.is_modifier_allowed('beam_only', comp) is True

    def test_allow_abilities_checks_both_ability_sources(self, full_registry):
        """allow_abilities checks both component.abilities and component.data['abilities']."""
        comp = MagicMock()
        comp.type_str = 'weapon'
        comp.abilities = {'ProjectileWeaponAbility': {}}
        comp.data = {'abilities': {'BeamWeaponAbility': {}}}

        service = ModifierService(modifier_registry=full_registry)
        # beam_only requires BeamWeaponAbility - found in data['abilities']
        assert service.is_modifier_allowed('beam_only', comp) is True

    def test_modifier_with_null_restrictions_allowed(self, mock_weapon_component):
        """Modifier with None/empty restrictions is allowed."""
        mod = Modifier({
            'id': 'null_restrictions',
            'name': 'Null',
            'param': {'min': 0, 'max': 10, 'default': 0},
            'restrictions': None,
            'effects': []
        })
        service = ModifierService(modifier_registry={'null_restrictions': mod})
        # Should handle None restrictions gracefully
        # The actual implementation checks `if not mod_def.restrictions`
        assert service.is_modifier_allowed('null_restrictions', mock_weapon_component) is True


# =============================================================================
# Test: get_mandatory_modifiers
# =============================================================================

class TestGetMandatoryModifiers:
    """Tests for get_mandatory_modifiers method."""

    def test_returns_list(self, basic_registry, mock_weapon_component):
        """Returns a list type."""
        service = ModifierService(modifier_registry=basic_registry)
        result = service.get_mandatory_modifiers(mock_weapon_component)
        assert isinstance(result, list)

    def test_returns_all_allowed_modifiers(self, basic_registry, mock_weapon_component):
        """Returns all modifiers that pass is_modifier_allowed check."""
        service = ModifierService(modifier_registry=basic_registry)
        result = service.get_mandatory_modifiers(mock_weapon_component)
        # Both modifiers in basic_registry are unrestricted
        assert 'test_unrestricted' in result
        assert 'simple_size_mount' in result

    def test_excludes_disallowed_modifiers(self, full_registry, mock_engine_component):
        """Excludes modifiers that fail is_modifier_allowed check."""
        service = ModifierService(modifier_registry=full_registry)
        result = service.get_mandatory_modifiers(mock_engine_component)
        # weapon_only requires type 'weapon'
        assert 'weapon_only' not in result
        # beam_only requires BeamWeaponAbility
        assert 'beam_only' not in result
        # turret_mount requires ProjectileWeaponAbility or BeamWeaponAbility
        assert 'turret_mount' not in result

    def test_empty_registry_returns_empty_list(self, mock_weapon_component):
        """Empty registry returns empty mandatory list."""
        service = ModifierService(modifier_registry={})
        result = service.get_mandatory_modifiers(mock_weapon_component)
        assert result == []


# =============================================================================
# Test: is_modifier_mandatory
# =============================================================================

class TestIsModifierMandatory:
    """Tests for is_modifier_mandatory method."""

    def test_returns_true_for_mandatory_modifier(self, basic_registry, mock_weapon_component):
        """Returns True if modifier is in mandatory list."""
        service = ModifierService(modifier_registry=basic_registry)
        assert service.is_modifier_mandatory('simple_size_mount', mock_weapon_component) is True

    def test_returns_false_for_non_mandatory_modifier(
        self, full_registry, mock_engine_component
    ):
        """Returns False if modifier is not in mandatory list."""
        service = ModifierService(modifier_registry=full_registry)
        # weapon_only is not mandatory for engines
        assert service.is_modifier_mandatory('weapon_only', mock_engine_component) is False

    def test_returns_false_for_unknown_modifier(self, basic_registry, mock_weapon_component):
        """Returns False for modifier not in registry."""
        service = ModifierService(modifier_registry=basic_registry)
        assert service.is_modifier_mandatory('unknown_mod', mock_weapon_component) is False


# =============================================================================
# Test: get_initial_value
# =============================================================================

class TestGetInitialValue:
    """Tests for get_initial_value method."""

    def test_unknown_modifier_returns_zero(self, basic_registry, mock_weapon_component):
        """Unknown modifier returns 0."""
        service = ModifierService(modifier_registry=basic_registry)
        assert service.get_initial_value('nonexistent', mock_weapon_component) == 0

    def test_simple_size_mount_returns_1(self, full_registry, mock_weapon_component):
        """simple_size_mount has special initial value of 1.0."""
        service = ModifierService(modifier_registry=full_registry)
        assert service.get_initial_value('simple_size_mount', mock_weapon_component) == 1.0

    def test_hardened_mount_returns_1(self, full_registry, mock_weapon_component):
        """hardened_mount has special initial value of 1.0."""
        service = ModifierService(modifier_registry=full_registry)
        assert service.get_initial_value('hardened_mount', mock_weapon_component) == 1.0

    def test_efficiency_mount_returns_1(self, full_registry, mock_weapon_component):
        """efficiency_mount has special initial value of 1.0."""
        service = ModifierService(modifier_registry=full_registry)
        assert service.get_initial_value('efficiency_mount', mock_weapon_component) == 1.0

    def test_range_mount_returns_0(self, full_registry, mock_weapon_component):
        """range_mount has special initial value of 0.0."""
        service = ModifierService(modifier_registry=full_registry)
        assert service.get_initial_value('range_mount', mock_weapon_component) == 0.0

    def test_facing_returns_0(self, full_registry, mock_weapon_component):
        """facing has special initial value of 0.0."""
        service = ModifierService(modifier_registry=full_registry)
        assert service.get_initial_value('facing', mock_weapon_component) == 0.0

    def test_precision_mount_returns_0(self, full_registry, mock_weapon_component):
        """precision_mount has special initial value of 0.0."""
        service = ModifierService(modifier_registry=full_registry)
        assert service.get_initial_value('precision_mount', mock_weapon_component) == 0.0

    def test_turret_mount_uses_base_firing_arc_from_abilities(
        self, full_registry, mock_weapon_component
    ):
        """turret_mount initial value comes from component's firing_arc in abilities."""
        service = ModifierService(modifier_registry=full_registry)
        # mock_weapon_component has ProjectileWeaponAbility with firing_arc: 30
        value = service.get_initial_value('turret_mount', mock_weapon_component)
        assert value == 30.0

    def test_turret_mount_uses_beam_ability_firing_arc(self, full_registry, mock_beam_component):
        """turret_mount checks BeamWeaponAbility for firing_arc."""
        service = ModifierService(modifier_registry=full_registry)
        # mock_beam_component has BeamWeaponAbility with firing_arc: 45
        value = service.get_initial_value('turret_mount', mock_beam_component)
        assert value == 45.0

    def test_turret_mount_uses_root_firing_arc(self, full_registry):
        """turret_mount checks root-level firing_arc first."""
        comp = MagicMock()
        comp.data = {'firing_arc': 60, 'abilities': {}}
        service = ModifierService(modifier_registry=full_registry)
        value = service.get_initial_value('turret_mount', comp)
        assert value == 60.0

    def test_turret_mount_fallback_to_min_val(self, full_registry):
        """turret_mount uses modifier min_val if no firing_arc found."""
        comp = MagicMock()
        comp.data = {'abilities': {}}  # No firing_arc anywhere
        service = ModifierService(modifier_registry=full_registry)
        value = service.get_initial_value('turret_mount', comp)
        assert value == 15.0  # min_val of turret_mount

    def test_turret_mount_finds_firing_arc_in_novel_weapon_ability(self, full_registry):
        """turret_mount should find firing_arc in ANY ability, not just hardcoded weapon names."""
        comp = MagicMock()
        comp.data = {
            'abilities': {
                'TorpedoLauncherAbility': {'firing_arc': 90, 'damage': 500}
            }
        }
        service = ModifierService(modifier_registry=full_registry)
        value = service.get_initial_value('turret_mount', comp)
        assert value == 90.0, (
            "_get_base_firing_arc should search ALL abilities for firing_arc, "
            "not just a hardcoded list of weapon ability names"
        )

    def test_default_modifier_uses_default_val(self, basic_registry, mock_weapon_component):
        """Generic modifier uses its default_val from definition."""
        service = ModifierService(modifier_registry=basic_registry)
        value = service.get_initial_value('test_unrestricted', mock_weapon_component)
        assert value == 50.0  # default_val of test_unrestricted


# =============================================================================
# Test: ensure_mandatory_modifiers
# =============================================================================

class TestEnsureMandatoryModifiers:
    """Tests for ensure_mandatory_modifiers method."""

    def test_adds_missing_modifiers(self, basic_registry, mock_weapon_component):
        """Adds mandatory modifiers that are not present."""
        service = ModifierService(modifier_registry=basic_registry)

        service.ensure_mandatory_modifiers(mock_weapon_component)

        # add_modifier should be called for each mandatory modifier
        assert mock_weapon_component.add_modifier.call_count == 2

    def test_does_not_add_existing_modifiers(self, basic_registry):
        """Does not add modifiers that already exist on component."""
        comp = MagicMock()
        comp.type_str = 'weapon'
        comp.abilities = {}
        comp.data = {'abilities': {}}

        # Pretend simple_size_mount already exists
        existing_mod = MagicMock()
        comp.get_modifier = MagicMock(side_effect=lambda m: existing_mod if m == 'simple_size_mount' else None)
        comp.add_modifier = MagicMock()

        service = ModifierService(modifier_registry=basic_registry)
        service.ensure_mandatory_modifiers(comp)

        # Should only add test_unrestricted (simple_size_mount already exists)
        calls = [call[0][0] for call in comp.add_modifier.call_args_list]
        assert 'simple_size_mount' not in calls
        assert 'test_unrestricted' in calls

    def test_sets_initial_value_on_added_modifiers(self, basic_registry):
        """Sets initial value on newly added modifiers."""
        comp = MagicMock()
        comp.type_str = 'weapon'
        comp.abilities = {}
        comp.data = {'abilities': {}}

        # Track modifier values
        added_modifiers = {}

        def add_mod(mod_id):
            m = MagicMock()
            m.value = None
            added_modifiers[mod_id] = m

        def get_mod(mod_id):
            return added_modifiers.get(mod_id)

        comp.add_modifier = add_mod
        comp.get_modifier = get_mod

        service = ModifierService(modifier_registry=basic_registry)
        service.ensure_mandatory_modifiers(comp)

        # simple_size_mount should have value 1.0
        assert added_modifiers['simple_size_mount'].value == 1.0
        # test_unrestricted should have value 50.0 (its default_val)
        assert added_modifiers['test_unrestricted'].value == 50.0


# =============================================================================
# Test: get_local_min_max
# =============================================================================

class TestGetLocalMinMax:
    """Tests for get_local_min_max method."""

    def test_returns_tuple(self, basic_registry, mock_weapon_component):
        """Returns a tuple of (min, max)."""
        service = ModifierService(modifier_registry=basic_registry)
        result = service.get_local_min_max('simple_size_mount', mock_weapon_component)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_unknown_modifier_returns_default_range(self, basic_registry, mock_weapon_component):
        """Unknown modifier returns (0, 100)."""
        service = ModifierService(modifier_registry=basic_registry)
        min_val, max_val = service.get_local_min_max('nonexistent', mock_weapon_component)
        assert min_val == 0
        assert max_val == 100

    def test_standard_modifier_uses_definition_values(self, basic_registry, mock_weapon_component):
        """Standard modifier uses min/max from definition."""
        service = ModifierService(modifier_registry=basic_registry)
        min_val, max_val = service.get_local_min_max('simple_size_mount', mock_weapon_component)
        assert min_val == 1.0
        assert max_val == 1024.0

    def test_turret_mount_min_uses_base_firing_arc(self, full_registry, mock_weapon_component):
        """turret_mount min is constrained by component's base firing_arc."""
        service = ModifierService(modifier_registry=full_registry)
        min_val, max_val = service.get_local_min_max('turret_mount', mock_weapon_component)
        # mock_weapon_component has ProjectileWeaponAbility with firing_arc: 30
        assert min_val == 30.0
        assert max_val == 180.0

    def test_turret_mount_min_uses_beam_firing_arc(self, full_registry, mock_beam_component):
        """turret_mount min uses BeamWeaponAbility firing_arc."""
        service = ModifierService(modifier_registry=full_registry)
        min_val, max_val = service.get_local_min_max('turret_mount', mock_beam_component)
        # mock_beam_component has BeamWeaponAbility with firing_arc: 45
        assert min_val == 45.0
        assert max_val == 180.0

    def test_turret_mount_min_uses_root_firing_arc(self, full_registry):
        """turret_mount checks root-level firing_arc for min."""
        comp = MagicMock()
        comp.data = {'firing_arc': 60, 'abilities': {}}
        service = ModifierService(modifier_registry=full_registry)
        min_val, max_val = service.get_local_min_max('turret_mount', comp)
        assert min_val == 60.0

    def test_turret_mount_fallback_to_modifier_min(self, full_registry):
        """turret_mount uses modifier min_val if no firing_arc found."""
        comp = MagicMock()
        comp.data = {'abilities': {}}  # No firing_arc
        service = ModifierService(modifier_registry=full_registry)
        min_val, max_val = service.get_local_min_max('turret_mount', comp)
        assert min_val == 15.0  # turret_mount min_val


# =============================================================================
# Test: Edge Cases and Error Handling
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_modifier_with_empty_restrictions_dict(self, mock_weapon_component):
        """Modifier with empty restrictions dict is allowed."""
        mod = Modifier({
            'id': 'empty_restrictions',
            'name': 'Empty',
            'param': {'min': 0, 'max': 10, 'default': 0},
            'restrictions': {},
            'effects': []
        })
        service = ModifierService(modifier_registry={'empty_restrictions': mod})
        assert service.is_modifier_allowed('empty_restrictions', mock_weapon_component) is True

    def test_component_with_empty_abilities_dict(self, full_registry):
        """Component with empty abilities dict handles allow_abilities check."""
        comp = MagicMock()
        comp.type_str = 'weapon'
        comp.abilities = {}
        comp.data = {'abilities': {}}

        service = ModifierService(modifier_registry=full_registry)
        # beam_only requires BeamWeaponAbility - should fail
        assert service.is_modifier_allowed('beam_only', comp) is False

    def test_component_with_no_data_abilities_key(self, full_registry):
        """Component without 'abilities' key in data handles gracefully."""
        comp = MagicMock()
        comp.type_str = 'weapon'
        comp.abilities = {'BeamWeaponAbility': {}}
        comp.data = {}  # No 'abilities' key

        service = ModifierService(modifier_registry=full_registry)
        # Should still find ability in comp.abilities
        assert service.is_modifier_allowed('beam_only', comp) is True

    def test_multiple_allow_abilities_any_match_succeeds(self, mock_weapon_component):
        """If multiple abilities in allow_abilities, any one match succeeds."""
        mod = Modifier({
            'id': 'multi_ability',
            'name': 'Multi',
            'param': {'min': 0, 'max': 10, 'default': 0},
            'restrictions': {'allow_abilities': ['BeamWeaponAbility', 'ProjectileWeaponAbility']},
            'effects': []
        })
        service = ModifierService(modifier_registry={'multi_ability': mod})
        # mock_weapon_component has ProjectileWeaponAbility
        assert service.is_modifier_allowed('multi_ability', mock_weapon_component) is True

    def test_combined_restrictions_all_must_pass(self, mock_weapon_component):
        """When multiple restriction types present, all must pass."""
        mod = Modifier({
            'id': 'combined',
            'name': 'Combined',
            'param': {'min': 0, 'max': 10, 'default': 0},
            'restrictions': {
                'allow_types': ['weapon'],
                'allow_abilities': ['BeamWeaponAbility']
            },
            'effects': []
        })
        service = ModifierService(modifier_registry={'combined': mod})
        # mock_weapon_component has type 'weapon' but ProjectileWeaponAbility, not BeamWeaponAbility
        assert service.is_modifier_allowed('combined', mock_weapon_component) is False

    def test_combined_restrictions_pass_when_all_match(self, mock_beam_component):
        """Combined restrictions pass when all conditions are met."""
        mod = Modifier({
            'id': 'combined',
            'name': 'Combined',
            'param': {'min': 0, 'max': 10, 'default': 0},
            'restrictions': {
                'allow_types': ['weapon'],
                'allow_abilities': ['BeamWeaponAbility']
            },
            'effects': []
        })
        service = ModifierService(modifier_registry={'combined': mod})
        # mock_beam_component has type 'weapon' AND BeamWeaponAbility
        assert service.is_modifier_allowed('combined', mock_beam_component) is True


# =============================================================================
# Test: Integration with Real Registry
# =============================================================================

class TestWithRealRegistry:
    """Tests using the real modifier registry for validation."""

    def test_service_works_with_fresh_registries(self, fresh_registries):
        """Service works with fresh_registries fixture."""
        service = ModifierService(modifier_registry=fresh_registries.modifiers)
        assert service._modifiers is not None
        assert len(service._modifiers) > 0

    def test_simple_size_mount_exists_in_real_registry(self, fresh_registries):
        """simple_size_mount exists in real registry."""
        service = ModifierService(modifier_registry=fresh_registries.modifiers)
        assert 'simple_size_mount' in service._modifiers

    def test_real_component_with_service(self, fresh_registries):
        """Service works with real components from registry."""
        from game.simulation.components.component import create_component

        service = ModifierService(modifier_registry=fresh_registries.modifiers)
        comp = create_component("laser_cannon", registries=fresh_registries)

        # Should get mandatory modifiers
        mandatory = service.get_mandatory_modifiers(comp)
        assert isinstance(mandatory, list)
        assert 'simple_size_mount' in mandatory


# =============================================================================
# Test: Additional Edge Cases (PROJ-118 Phase 2)
# =============================================================================

class TestAdditionalModifierEdgeCases:
    """Additional edge case tests for ModifierService."""

    def test_is_modifier_allowed_with_deny_and_allow_types(self, mock_weapon_component):
        """Modifier with both allow_types and deny_types respects both."""
        mod = Modifier({
            'id': 'allow_deny_combo',
            'name': 'Combo Test',
            'param': {'min': 0, 'max': 10, 'default': 0},
            'restrictions': {
                'allow_types': ['weapon', 'engine'],
                'deny_types': ['armor']
            },
            'effects': []
        })
        service = ModifierService(modifier_registry={'allow_deny_combo': mod})

        # weapon is in allow_types and not in deny_types
        assert service.is_modifier_allowed('allow_deny_combo', mock_weapon_component) is True

    def test_get_initial_value_seeker_weapon_ability(self, full_registry):
        """turret_mount finds SeekerWeaponAbility firing_arc."""
        comp = MagicMock()
        comp.data = {
            'abilities': {
                'SeekerWeaponAbility': {'firing_arc': 90}
            }
        }
        service = ModifierService(modifier_registry=full_registry)
        value = service.get_initial_value('turret_mount', comp)
        assert value == 90.0

    def test_get_initial_value_weapon_ability_generic(self, full_registry):
        """turret_mount finds WeaponAbility firing_arc."""
        comp = MagicMock()
        comp.data = {
            'abilities': {
                'WeaponAbility': {'firing_arc': 75}
            }
        }
        service = ModifierService(modifier_registry=full_registry)
        value = service.get_initial_value('turret_mount', comp)
        assert value == 75.0

    def test_get_local_min_max_seeker_weapon_ability(self, full_registry):
        """turret_mount min respects SeekerWeaponAbility firing_arc."""
        comp = MagicMock()
        comp.data = {
            'abilities': {
                'SeekerWeaponAbility': {'firing_arc': 50}
            }
        }
        service = ModifierService(modifier_registry=full_registry)
        min_val, max_val = service.get_local_min_max('turret_mount', comp)
        assert min_val == 50.0
        assert max_val == 180.0

    def test_ensure_mandatory_modifiers_idempotent(self, basic_registry):
        """ensure_mandatory_modifiers is idempotent (calling twice has no extra effect)."""
        comp = MagicMock()
        comp.type_str = 'weapon'
        comp.abilities = {}
        comp.data = {'abilities': {}}

        added_modifiers = {}

        def add_mod(mod_id):
            if mod_id not in added_modifiers:
                m = MagicMock()
                m.value = None
                added_modifiers[mod_id] = m

        def get_mod(mod_id):
            return added_modifiers.get(mod_id)

        comp.add_modifier = add_mod
        comp.get_modifier = get_mod

        service = ModifierService(modifier_registry=basic_registry)

        # First call
        service.ensure_mandatory_modifiers(comp)
        first_count = len(added_modifiers)

        # Second call - should not add more
        service.ensure_mandatory_modifiers(comp)
        second_count = len(added_modifiers)

        assert first_count == second_count

    def test_is_modifier_mandatory_returns_bool(self, basic_registry, mock_weapon_component):
        """is_modifier_mandatory always returns a boolean."""
        service = ModifierService(modifier_registry=basic_registry)

        result = service.is_modifier_mandatory('simple_size_mount', mock_weapon_component)
        assert isinstance(result, bool)

        result = service.is_modifier_mandatory('nonexistent', mock_weapon_component)
        assert isinstance(result, bool)

    def test_get_mandatory_modifiers_order_consistency(self, full_registry, mock_weapon_component):
        """get_mandatory_modifiers returns consistent order on repeated calls."""
        service = ModifierService(modifier_registry=full_registry)

        first_call = service.get_mandatory_modifiers(mock_weapon_component)
        second_call = service.get_mandatory_modifiers(mock_weapon_component)

        # Order should be consistent (same iteration order over dict keys)
        assert first_call == second_call

    def test_service_handles_component_with_missing_data_key(self, full_registry):
        """Service handles component with no 'abilities' in data gracefully."""
        comp = MagicMock()
        comp.type_str = 'weapon'
        comp.abilities = {}
        comp.data = {}  # No 'abilities' key at all

        service = ModifierService(modifier_registry=full_registry)

        # Should not crash
        mandatory = service.get_mandatory_modifiers(comp)
        assert isinstance(mandatory, list)

    def test_get_local_min_max_returns_floats(self, basic_registry, mock_weapon_component):
        """get_local_min_max returns float values."""
        service = ModifierService(modifier_registry=basic_registry)
        min_val, max_val = service.get_local_min_max('simple_size_mount', mock_weapon_component)

        assert isinstance(min_val, float)
        assert isinstance(max_val, float)

    def test_modifier_with_single_effect(self, mock_weapon_component):
        """Modifier with effects list is allowed if restrictions pass."""
        mod = Modifier({
            'id': 'with_effect',
            'name': 'Effect Mod',
            'param': {'min': 0, 'max': 10, 'default': 5},
            'restrictions': {},
            'effects': [{'type': 'damage_mult', 'amount': 1.5}]
        })
        service = ModifierService(modifier_registry={'with_effect': mod})

        assert service.is_modifier_allowed('with_effect', mock_weapon_component) is True
        assert service.get_initial_value('with_effect', mock_weapon_component) == 5


# =============================================================================
# Test: Generic arc_set detection (effect-based, not ID-based)
# =============================================================================

class TestArcSetEffectDetection:
    """Tests that any modifier with an arc_set effect defaults to the weapon's
    base firing arc, regardless of modifier ID.

    This replaces the hardcoded 'turret_mount' check with generic effect-based
    detection, so custom modifiers (e.g. test_turret) behave correctly.
    """

    @pytest.fixture
    def custom_arc_modifier(self):
        """A non-turret_mount modifier that uses arc_set effect."""
        return Modifier({
            'id': 'custom_arc',
            'name': 'Custom Arc Override',
            'param': {'min': 0, 'max': 360, 'default': 0},
            'restrictions': {},
            'effects': [{'stat': 'arc_set', 'formula': 'param', 'operation': 'set'}]
        })

    @pytest.fixture
    def no_arc_modifier(self):
        """A modifier with no arc_set effect (damage only)."""
        return Modifier({
            'id': 'damage_only',
            'name': 'Damage Only',
            'param': {'min': 1, 'max': 10, 'default': 0},
            'restrictions': {},
            'effects': [{'stat': 'damage_mult', 'formula': 'param'}]
        })

    def test_custom_arc_modifier_defaults_to_base_arc_from_abilities(
        self, custom_arc_modifier, mock_weapon_component
    ):
        """Custom arc_set modifier defaults to weapon's base firing_arc."""
        service = ModifierService(modifier_registry={'custom_arc': custom_arc_modifier})
        # mock_weapon_component has ProjectileWeaponAbility with firing_arc: 30
        value = service.get_initial_value('custom_arc', mock_weapon_component)
        assert value == 30.0

    def test_custom_arc_modifier_defaults_to_beam_arc(
        self, custom_arc_modifier, mock_beam_component
    ):
        """Custom arc_set modifier finds BeamWeaponAbility firing_arc."""
        service = ModifierService(modifier_registry={'custom_arc': custom_arc_modifier})
        # mock_beam_component has BeamWeaponAbility with firing_arc: 45
        value = service.get_initial_value('custom_arc', mock_beam_component)
        assert value == 45.0

    def test_custom_arc_modifier_defaults_to_root_firing_arc(self, custom_arc_modifier):
        """Custom arc_set modifier checks root-level firing_arc first."""
        comp = MagicMock()
        comp.data = {'firing_arc': 120, 'abilities': {}}
        service = ModifierService(modifier_registry={'custom_arc': custom_arc_modifier})
        value = service.get_initial_value('custom_arc', comp)
        assert value == 120.0

    def test_custom_arc_modifier_fallback_to_min_val(self, custom_arc_modifier):
        """Custom arc_set modifier falls back to min_val if no firing_arc."""
        comp = MagicMock()
        comp.data = {'abilities': {}}
        service = ModifierService(modifier_registry={'custom_arc': custom_arc_modifier})
        value = service.get_initial_value('custom_arc', comp)
        assert value == 0.0  # min_val of custom_arc

    def test_non_arc_modifier_uses_default_val(
        self, no_arc_modifier, mock_weapon_component
    ):
        """Modifier without arc_set effect still uses default_val."""
        service = ModifierService(modifier_registry={'damage_only': no_arc_modifier})
        value = service.get_initial_value('damage_only', mock_weapon_component)
        assert value == 0  # default_val of damage_only

    def test_turret_mount_still_works_with_generic_detection(
        self, mock_weapon_component
    ):
        """turret_mount (hardcoded case removed) still works via effect detection.

        Note: mock_turret_mount fixture has no effects list, so it falls through
        to default_val. This test uses a turret_mount WITH an arc_set effect.
        """
        turret_with_effect = Modifier({
            'id': 'turret_mount',
            'name': 'Turret Mount',
            'param': {'min': 15.0, 'max': 180.0, 'default': 45.0},
            'restrictions': {'allow_abilities': ['ProjectileWeaponAbility', 'BeamWeaponAbility']},
            'effects': [{'stat': 'arc_set', 'formula': 'param', 'operation': 'set'}]
        })
        service = ModifierService(modifier_registry={'turret_mount': turret_with_effect})
        # mock_weapon_component has ProjectileWeaponAbility with firing_arc: 30
        value = service.get_initial_value('turret_mount', mock_weapon_component)
        assert value == 30.0

    def test_arc_set_detection_in_get_local_min_max(
        self, custom_arc_modifier, mock_weapon_component
    ):
        """Custom arc_set modifier also clamps min to base firing_arc."""
        service = ModifierService(modifier_registry={'custom_arc': custom_arc_modifier})
        min_val, max_val = service.get_local_min_max('custom_arc', mock_weapon_component)
        # mock_weapon_component has firing_arc: 30
        assert min_val == 30.0
        assert max_val == 360.0

    def test_non_arc_modifier_min_max_unchanged(
        self, no_arc_modifier, mock_weapon_component
    ):
        """Non-arc modifier min/max are not affected by base firing_arc."""
        service = ModifierService(modifier_registry={'damage_only': no_arc_modifier})
        min_val, max_val = service.get_local_min_max('damage_only', mock_weapon_component)
        assert min_val == 1.0  # from modifier definition
        assert max_val == 10.0
