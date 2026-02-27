"""
Unit tests for the Ability base class.

Tests AbilityLayer flag, AbilityScope enum, and Ability base class including:
- Initialization and data handling
- Scope parsing and validation
- Layer checking
- Tags and stack groups
- Default implementations of lifecycle methods
- Stat lookups and introspection
"""
import pytest
from unittest.mock import MagicMock

from game.core.exceptions import ValidationException
from game.simulation.components.abilities.base import (
    Ability,
    AbilityLayer,
    AbilityScope,
)
from game.simulation.components.abilities.stat_keys import (
    StatKey,
    AbilityStatBinding,
)


# =============================================================================
# AbilityLayer Tests
# =============================================================================


class TestAbilityLayer:
    """Tests for AbilityLayer Flag enum."""

    def test_combat_layer_exists(self):
        """COMBAT layer is defined."""
        assert AbilityLayer.COMBAT is not None

    def test_strategic_layer_exists(self):
        """STRATEGIC layer is defined."""
        assert AbilityLayer.STRATEGIC is not None

    def test_both_layer_is_combat_and_strategic(self):
        """BOTH layer combines COMBAT and STRATEGIC."""
        assert AbilityLayer.BOTH == (AbilityLayer.COMBAT | AbilityLayer.STRATEGIC)

    def test_combat_in_both(self):
        """COMBAT is part of BOTH."""
        assert AbilityLayer.COMBAT in AbilityLayer.BOTH

    def test_strategic_in_both(self):
        """STRATEGIC is part of BOTH."""
        assert AbilityLayer.STRATEGIC in AbilityLayer.BOTH

    def test_combat_not_equal_strategic(self):
        """COMBAT and STRATEGIC are distinct."""
        assert AbilityLayer.COMBAT != AbilityLayer.STRATEGIC

    def test_layer_bitwise_and_combat(self):
        """Bitwise AND with COMBAT works correctly."""
        assert bool(AbilityLayer.BOTH & AbilityLayer.COMBAT)
        assert bool(AbilityLayer.COMBAT & AbilityLayer.COMBAT)
        assert not bool(AbilityLayer.STRATEGIC & AbilityLayer.COMBAT)

    def test_layer_bitwise_and_strategic(self):
        """Bitwise AND with STRATEGIC works correctly."""
        assert bool(AbilityLayer.BOTH & AbilityLayer.STRATEGIC)
        assert bool(AbilityLayer.STRATEGIC & AbilityLayer.STRATEGIC)
        assert not bool(AbilityLayer.COMBAT & AbilityLayer.STRATEGIC)


# =============================================================================
# AbilityScope Tests
# =============================================================================


class TestAbilityScope:
    """Tests for AbilityScope Enum."""

    def test_self_scope_value(self):
        """SELF scope has value 'self'."""
        assert AbilityScope.SELF.value == "self"

    def test_sector_scope_value(self):
        """SECTOR scope has value 'sector'."""
        assert AbilityScope.SECTOR.value == "sector"

    def test_allied_sector_scope_value(self):
        """ALLIED_SECTOR scope has value 'allied_sector'."""
        assert AbilityScope.ALLIED_SECTOR.value == "allied_sector"

    def test_system_scope_value(self):
        """SYSTEM scope has value 'system'."""
        assert AbilityScope.SYSTEM.value == "system"

    def test_allied_system_scope_value(self):
        """ALLIED_SYSTEM scope has value 'allied_system'."""
        assert AbilityScope.ALLIED_SYSTEM.value == "allied_system"

    def test_planet_scope_value(self):
        """PLANET scope has value 'planet'."""
        assert AbilityScope.PLANET.value == "planet"

    def test_scope_from_string(self):
        """Scopes can be created from string values."""
        assert AbilityScope("self") == AbilityScope.SELF
        assert AbilityScope("sector") == AbilityScope.SECTOR
        assert AbilityScope("system") == AbilityScope.SYSTEM

    def test_invalid_scope_string_raises(self):
        """Invalid scope string raises ValueError."""
        with pytest.raises(ValueError):
            AbilityScope("invalid_scope")


# =============================================================================
# Ability Base Class Tests
# =============================================================================


class TestAbilityClassDefaults:
    """Tests for Ability class-level defaults."""

    def test_default_layer_is_combat(self):
        """Default layer is COMBAT."""
        assert Ability.layer == AbilityLayer.COMBAT

    def test_default_allowed_scopes_is_self_only(self):
        """Default allowed_scopes is [SELF]."""
        assert Ability.allowed_scopes == [AbilityScope.SELF]

    def test_default_scope_is_self(self):
        """Default scope is SELF."""
        assert Ability.default_scope == AbilityScope.SELF

    def test_default_stat_bindings_is_empty(self):
        """Default STAT_BINDINGS is empty list."""
        assert Ability.STAT_BINDINGS == []


class TestAbilityInitialization:
    """Tests for Ability.__init__."""

    @pytest.fixture
    def mock_component(self):
        """Create a mock component."""
        return MagicMock()

    def test_init_stores_component(self, mock_component):
        """Ability stores reference to component."""
        ability = Ability(mock_component, {})
        assert ability.component is mock_component

    def test_init_stores_data(self, mock_component):
        """Ability stores the data dict."""
        data = {"key": "value"}
        ability = Ability(mock_component, data)
        assert ability.data == data

    def test_init_with_empty_dict(self, mock_component):
        """Empty dict initializes with empty tags and no stack_group."""
        ability = Ability(mock_component, {})
        assert ability.tags == set()
        assert ability.stack_group is None

    def test_init_parses_tags(self, mock_component):
        """Tags are parsed from data dict."""
        data = {"tags": ["energy", "weapon"]}
        ability = Ability(mock_component, data)
        assert ability.tags == {"energy", "weapon"}

    def test_init_parses_stack_group(self, mock_component):
        """stack_group is parsed from data dict."""
        data = {"stack_group": "thrusters"}
        ability = Ability(mock_component, data)
        assert ability.stack_group == "thrusters"

    def test_init_with_non_dict_data(self, mock_component):
        """Non-dict data results in empty tags and no stack_group."""
        ability = Ability(mock_component, "primitive_value")
        assert ability.tags == set()
        assert ability.stack_group is None

    def test_init_with_none_data(self, mock_component):
        """None data results in empty tags and no stack_group."""
        ability = Ability(mock_component, None)
        assert ability.tags == set()
        assert ability.stack_group is None

    def test_init_default_scope(self, mock_component):
        """Scope defaults to SELF when not specified."""
        ability = Ability(mock_component, {})
        assert ability.scope == AbilityScope.SELF


class TestAbilityScopeParsing:
    """Tests for Ability._parse_scope method."""

    @pytest.fixture
    def mock_component(self):
        """Create a mock component."""
        return MagicMock()

    def test_parse_scope_non_dict_returns_default(self, mock_component):
        """Non-dict data returns default_scope."""
        ability = Ability(mock_component, "not_a_dict")
        assert ability.scope == AbilityScope.SELF

    def test_parse_scope_missing_key_returns_default(self, mock_component):
        """Missing 'scope' key returns default_scope."""
        ability = Ability(mock_component, {"other": "value"})
        assert ability.scope == AbilityScope.SELF

    def test_parse_scope_none_value_returns_default(self, mock_component):
        """None scope value returns default_scope."""
        ability = Ability(mock_component, {"scope": None})
        assert ability.scope == AbilityScope.SELF

    def test_parse_scope_valid_self(self, mock_component):
        """Valid 'self' scope is parsed correctly."""
        ability = Ability(mock_component, {"scope": "self"})
        assert ability.scope == AbilityScope.SELF

    def test_parse_scope_invalid_string_raises(self, mock_component):
        """Invalid scope string raises ValidationException."""
        with pytest.raises(ValidationException):
            Ability(mock_component, {"scope": "invalid"})

    def test_parse_scope_not_in_allowed_raises(self, mock_component):
        """Scope not in allowed_scopes raises ValidationException."""
        # Base Ability only allows SELF by default
        with pytest.raises(ValidationException):
            Ability(mock_component, {"scope": "sector"})


class TestAbilityWithCustomAllowedScopes:
    """Tests for abilities with custom allowed_scopes."""

    @pytest.fixture
    def mock_component(self):
        """Create a mock component."""
        return MagicMock()

    def test_custom_allowed_scopes(self, mock_component):
        """Subclass with custom allowed_scopes accepts those scopes."""

        class SectorAbility(Ability):
            allowed_scopes = [AbilityScope.SELF, AbilityScope.SECTOR]

        ability = SectorAbility(mock_component, {"scope": "sector"})
        assert ability.scope == AbilityScope.SECTOR

    def test_custom_default_scope(self, mock_component):
        """Subclass with custom default_scope uses that default."""

        class SystemAbility(Ability):
            allowed_scopes = [AbilityScope.SYSTEM, AbilityScope.ALLIED_SYSTEM]
            default_scope = AbilityScope.SYSTEM

        ability = SystemAbility(mock_component, {})
        assert ability.scope == AbilityScope.SYSTEM


class TestAbilityAppliesToLayer:
    """Tests for Ability.applies_to_layer method."""

    @pytest.fixture
    def mock_component(self):
        """Create a mock component."""
        return MagicMock()

    def test_combat_ability_applies_to_combat(self, mock_component):
        """Combat ability applies to COMBAT layer."""
        ability = Ability(mock_component, {})
        assert ability.layer == AbilityLayer.COMBAT
        assert ability.applies_to_layer(AbilityLayer.COMBAT) is True

    def test_combat_ability_not_applies_to_strategic(self, mock_component):
        """Combat ability does not apply to STRATEGIC layer."""
        ability = Ability(mock_component, {})
        assert ability.applies_to_layer(AbilityLayer.STRATEGIC) is False

    def test_combat_ability_applies_to_both(self, mock_component):
        """Combat ability applies when checking BOTH (has COMBAT in it)."""
        ability = Ability(mock_component, {})
        # COMBAT & BOTH = COMBAT, which is truthy
        assert ability.applies_to_layer(AbilityLayer.BOTH) is True

    def test_strategic_ability_applies_to_strategic(self, mock_component):
        """Strategic ability applies to STRATEGIC layer."""

        class StrategicAbility(Ability):
            layer = AbilityLayer.STRATEGIC

        ability = StrategicAbility(mock_component, {})
        assert ability.applies_to_layer(AbilityLayer.STRATEGIC) is True
        assert ability.applies_to_layer(AbilityLayer.COMBAT) is False

    def test_both_layer_ability_applies_to_both_layers(self, mock_component):
        """BOTH layer ability applies to both COMBAT and STRATEGIC."""

        class DualLayerAbility(Ability):
            layer = AbilityLayer.BOTH

        ability = DualLayerAbility(mock_component, {})
        assert ability.applies_to_layer(AbilityLayer.COMBAT) is True
        assert ability.applies_to_layer(AbilityLayer.STRATEGIC) is True
        assert ability.applies_to_layer(AbilityLayer.BOTH) is True


class TestAbilitySyncData:
    """Tests for Ability.sync_data method."""

    @pytest.fixture
    def mock_component(self):
        """Create a mock component."""
        return MagicMock()

    def test_sync_data_updates_data(self, mock_component):
        """sync_data updates the data attribute."""
        ability = Ability(mock_component, {"old": "data"})
        ability.sync_data({"new": "data"})
        assert ability.data == {"new": "data"}

    def test_sync_data_updates_tags(self, mock_component):
        """sync_data updates tags from new data."""
        ability = Ability(mock_component, {"tags": ["old"]})
        assert ability.tags == {"old"}

        ability.sync_data({"tags": ["new", "tags"]})
        assert ability.tags == {"new", "tags"}

    def test_sync_data_updates_stack_group(self, mock_component):
        """sync_data updates stack_group from new data."""
        ability = Ability(mock_component, {"stack_group": "old"})
        assert ability.stack_group == "old"

        ability.sync_data({"stack_group": "new"})
        assert ability.stack_group == "new"

    def test_sync_data_updates_scope(self, mock_component):
        """sync_data re-parses scope from new data."""

        class FlexibleAbility(Ability):
            allowed_scopes = [AbilityScope.SELF, AbilityScope.SECTOR]

        ability = FlexibleAbility(mock_component, {"scope": "self"})
        assert ability.scope == AbilityScope.SELF

        ability.sync_data({"scope": "sector"})
        assert ability.scope == AbilityScope.SECTOR

    def test_sync_data_with_non_dict(self, mock_component):
        """sync_data with non-dict preserves data but doesn't crash."""
        ability = Ability(mock_component, {"tags": ["original"]})
        ability.sync_data("primitive")
        assert ability.data == "primitive"
        # Tags remain from previous state (not cleared)
        assert ability.tags == {"original"}


class TestAbilityLifecycleMethods:
    """Tests for Ability lifecycle method defaults."""

    @pytest.fixture
    def mock_component(self):
        """Create a mock component."""
        return MagicMock()

    def test_update_returns_true(self, mock_component):
        """Default update() returns True (operational)."""
        ability = Ability(mock_component, {})
        assert ability.update() is True

    def test_on_activation_returns_true(self, mock_component):
        """Default on_activation() returns True (allowed)."""
        ability = Ability(mock_component, {})
        assert ability.on_activation() is True

    def test_recalculate_does_nothing(self, mock_component):
        """Default recalculate() does nothing (returns None)."""
        ability = Ability(mock_component, {})
        result = ability.recalculate()
        assert result is None

    def test_get_primary_value_returns_zero(self, mock_component):
        """Default get_primary_value() returns 0.0."""
        ability = Ability(mock_component, {})
        assert ability.get_primary_value() == 0.0
        assert isinstance(ability.get_primary_value(), float)

    def test_get_ui_rows_returns_empty_list(self, mock_component):
        """Default get_ui_rows() returns empty list."""
        ability = Ability(mock_component, {})
        assert ability.get_ui_rows() == []
        assert isinstance(ability.get_ui_rows(), list)


class TestAbilityGetEffectiveStat:
    """Tests for Ability.get_effective_stat method."""

    @pytest.fixture
    def mock_component(self):
        """Create a mock component with stats."""
        component = MagicMock()
        component.stats = {}
        component.ability_stats = {}
        return component

    def test_get_effective_stat_from_component_stats(self, mock_component):
        """Retrieves stat from component.stats."""
        mock_component.stats = {"damage_mult": 1.5}
        ability = Ability(mock_component, {})

        result = ability.get_effective_stat("damage_mult")
        assert result == 1.5

    def test_get_effective_stat_mult_default(self, mock_component):
        """Stats ending in '_mult' default to 1.0."""
        ability = Ability(mock_component, {})

        result = ability.get_effective_stat("unknown_mult")
        assert result == 1.0

    def test_get_effective_stat_add_default(self, mock_component):
        """Stats ending in '_add' default to 0.0."""
        ability = Ability(mock_component, {})

        result = ability.get_effective_stat("unknown_add")
        assert result == 0.0

    def test_get_effective_stat_other_default(self, mock_component):
        """Other stats default to None."""
        ability = Ability(mock_component, {})

        result = ability.get_effective_stat("arc_set")
        assert result is None

    def test_get_effective_stat_explicit_default(self, mock_component):
        """Explicit default overrides naming convention."""
        ability = Ability(mock_component, {})

        result = ability.get_effective_stat("unknown_mult", default=42)
        assert result == 42

    def test_get_effective_stat_ability_specific_override(self, mock_component):
        """Ability-specific stats override global component stats."""
        mock_component.stats = {"damage_mult": 1.5}
        mock_component.ability_stats = {"Ability": {"damage_mult": 2.0}}
        ability = Ability(mock_component, {})

        result = ability.get_effective_stat("damage_mult")
        assert result == 2.0

    def test_get_effective_stat_ability_specific_subclass(self, mock_component):
        """Ability-specific stats use class name for lookup."""

        class WeaponAbility(Ability):
            pass

        mock_component.ability_stats = {"WeaponAbility": {"damage_mult": 3.0}}
        ability = WeaponAbility(mock_component, {})

        result = ability.get_effective_stat("damage_mult")
        assert result == 3.0

    def test_get_effective_stat_component_with_empty_stats(self):
        """Handles component with empty stats dict gracefully.

        PROJ-190: Components must have stats per IComponent protocol.
        This test verifies empty stats work correctly.
        """
        component = MagicMock()
        component.stats = {}
        component.ability_stats = {}
        ability = Ability(component, {})

        result = ability.get_effective_stat("damage_mult")
        assert result == 1.0  # Uses default


class TestAbilityIntrospection:
    """Tests for Ability introspection methods."""

    @pytest.fixture
    def mock_component(self):
        """Create a mock component with stats."""
        component = MagicMock()
        component.stats = {}
        return component

    def test_get_consumed_stats_empty_by_default(self):
        """Base Ability has no consumed stats."""
        stats = Ability.get_consumed_stats()
        assert stats == set()

    def test_get_consumed_stats_with_bindings(self):
        """Subclass with STAT_BINDINGS returns those stats."""

        class BoundAbility(Ability):
            STAT_BINDINGS = [
                AbilityStatBinding(StatKey.DAMAGE_MULT, "damage"),
                AbilityStatBinding(StatKey.RANGE_MULT, "range"),
            ]

        stats = BoundAbility.get_consumed_stats()
        assert stats == {StatKey.DAMAGE_MULT, StatKey.RANGE_MULT}

    def test_get_stat_bindings_info_empty_by_default(self):
        """Base Ability has no binding info."""
        info = Ability.get_stat_bindings_info()
        assert info == []

    def test_get_stat_bindings_info_with_bindings(self):
        """Subclass with STAT_BINDINGS returns binding info."""

        class BoundAbility(Ability):
            STAT_BINDINGS = [
                AbilityStatBinding(StatKey.DAMAGE_MULT, "damage", "multiply"),
            ]

        info = BoundAbility.get_stat_bindings_info()
        assert len(info) == 1
        assert info[0]["stat_key"] == "damage_mult"
        assert info[0]["attribute"] == "damage"
        assert info[0]["operation"] == "multiply"


class TestAbilityEffectSummary:
    """Tests for Ability.get_effect_summary method."""

    @pytest.fixture
    def mock_component(self):
        """Create a mock component with stats."""
        component = MagicMock()
        component.stats = {}
        return component

    def test_get_effect_summary_empty_by_default(self, mock_component):
        """Base Ability has no effect summary."""
        ability = Ability(mock_component, {})
        summary = ability.get_effect_summary()
        assert summary == []

    def test_get_effect_summary_with_active_modifier(self, mock_component):
        """Effect summary includes active modifiers."""

        class DamageAbility(Ability):
            STAT_BINDINGS = [
                AbilityStatBinding(StatKey.DAMAGE_MULT, "damage", "multiply"),
            ]

        ability = DamageAbility(mock_component, {})
        ability._base_damage = 100.0
        ability.damage = 150.0
        mock_component.stats = {"damage_mult": 1.5}

        summary = ability.get_effect_summary()
        assert len(summary) == 1
        assert summary[0]["attribute"] == "damage"
        assert summary[0]["base"] == 100.0
        assert summary[0]["current"] == 150.0
        assert summary[0]["stat_key"] == "damage_mult"
        assert summary[0]["stat_value"] == 1.5
        assert summary[0]["operation"] == "multiply"

    def test_get_effect_summary_skips_default_mult(self, mock_component):
        """Effect summary skips multipliers at default (1.0)."""

        class DamageAbility(Ability):
            STAT_BINDINGS = [
                AbilityStatBinding(StatKey.DAMAGE_MULT, "damage", "multiply"),
            ]

        ability = DamageAbility(mock_component, {})
        ability._base_damage = 100.0
        mock_component.stats = {"damage_mult": 1.0}

        summary = ability.get_effect_summary()
        assert summary == []

    def test_get_effect_summary_skips_default_add(self, mock_component):
        """Effect summary skips additives at default (0.0)."""

        class AccuracyAbility(Ability):
            STAT_BINDINGS = [
                AbilityStatBinding(StatKey.ACCURACY_ADD, "accuracy", "add"),
            ]

        ability = AccuracyAbility(mock_component, {})
        ability._base_accuracy = 0.8
        mock_component.stats = {"accuracy_add": 0.0}

        summary = ability.get_effect_summary()
        assert summary == []

    def test_get_effect_summary_skips_missing_base(self, mock_component):
        """Effect summary skips bindings without base attribute."""

        class DamageAbility(Ability):
            STAT_BINDINGS = [
                AbilityStatBinding(StatKey.DAMAGE_MULT, "damage", "multiply"),
            ]

        ability = DamageAbility(mock_component, {})
        # No _base_damage attribute set
        mock_component.stats = {"damage_mult": 1.5}

        summary = ability.get_effect_summary()
        assert summary == []


class TestAbilitySubclassCustomization:
    """Tests for Ability subclass customization patterns."""

    @pytest.fixture
    def mock_component(self):
        """Create a mock component."""
        return MagicMock()

    def test_subclass_override_layer(self, mock_component):
        """Subclass can override layer."""

        class StrategicOnlyAbility(Ability):
            layer = AbilityLayer.STRATEGIC

        ability = StrategicOnlyAbility(mock_component, {})
        assert ability.layer == AbilityLayer.STRATEGIC
        assert ability.applies_to_layer(AbilityLayer.STRATEGIC) is True
        assert ability.applies_to_layer(AbilityLayer.COMBAT) is False

    def test_subclass_override_update(self, mock_component):
        """Subclass can override update to return False."""

        class FailingAbility(Ability):
            def update(self) -> bool:
                return False

        ability = FailingAbility(mock_component, {})
        assert ability.update() is False

    def test_subclass_override_on_activation(self, mock_component):
        """Subclass can override on_activation to return False."""

        class BlockedAbility(Ability):
            def on_activation(self) -> bool:
                return False

        ability = BlockedAbility(mock_component, {})
        assert ability.on_activation() is False

    def test_subclass_override_get_primary_value(self, mock_component):
        """Subclass can override get_primary_value."""

        class ValuedAbility(Ability):
            def get_primary_value(self) -> float:
                return 42.0

        ability = ValuedAbility(mock_component, {})
        assert ability.get_primary_value() == 42.0

    def test_subclass_override_get_ui_rows(self, mock_component):
        """Subclass can override get_ui_rows."""

        class UIAbility(Ability):
            def get_ui_rows(self):
                return [{"label": "Test", "value": "Value"}]

        ability = UIAbility(mock_component, {})
        rows = ability.get_ui_rows()
        assert len(rows) == 1
        assert rows[0]["label"] == "Test"


class TestAbilityEdgeCases:
    """Tests for edge cases and boundary conditions."""

    @pytest.fixture
    def mock_component(self):
        """Create a mock component."""
        return MagicMock()

    def test_empty_tags_list(self, mock_component):
        """Empty tags list results in empty set."""
        ability = Ability(mock_component, {"tags": []})
        assert ability.tags == set()

    def test_duplicate_tags_deduplicated(self, mock_component):
        """Duplicate tags in list are deduplicated."""
        ability = Ability(mock_component, {"tags": ["a", "a", "b"]})
        assert ability.tags == {"a", "b"}

    def test_tags_property_returns_internal_set(self, mock_component):
        """tags property returns the internal _tags set."""
        ability = Ability(mock_component, {"tags": ["x"]})
        assert ability.tags is ability._tags

    def test_data_with_numeric_values(self, mock_component):
        """Data dict with numeric values works correctly."""
        data = {"capacity": 100, "rate": 1.5}
        ability = Ability(mock_component, data)
        assert ability.data["capacity"] == 100
        assert ability.data["rate"] == 1.5

    def test_data_with_nested_dict(self, mock_component):
        """Data dict with nested structure works correctly."""
        data = {"config": {"nested": "value"}}
        ability = Ability(mock_component, data)
        assert ability.data["config"]["nested"] == "value"

    def test_scope_validation_error_message_contains_class_name(self, mock_component):
        """Scope validation error includes class name."""
        with pytest.raises(ValidationException) as exc_info:
            Ability(mock_component, {"scope": "sector"})
        assert "Ability" in str(exc_info.value)

    def test_invalid_scope_error_message_lists_valid_scopes(self, mock_component):
        """Invalid scope error lists all valid scope values."""
        with pytest.raises(ValidationException) as exc_info:
            Ability(mock_component, {"scope": "nonexistent"})
        # Check context contains the scopes
        assert exc_info.value.context.get("valid_scopes") is not None


# =============================================================================
# Additional Edge Case Tests
# =============================================================================


class TestAbilityStatBindingIntegration:
    """Tests for STAT_BINDINGS integration with Ability class."""

    @pytest.fixture
    def mock_component(self):
        """Create a mock component with stats."""
        component = MagicMock()
        component.stats = {}
        component.ability_stats = {}
        return component

    def test_stat_bindings_inherited_by_subclass(self, mock_component):
        """Subclass inherits empty STAT_BINDINGS and can override."""

        class SubAbility(Ability):
            STAT_BINDINGS = [
                AbilityStatBinding(StatKey.DAMAGE_MULT, "power"),
            ]

        assert len(SubAbility.STAT_BINDINGS) == 1
        assert SubAbility.STAT_BINDINGS[0].stat_key == StatKey.DAMAGE_MULT

    def test_get_consumed_stats_returns_set_of_stat_keys(self):
        """get_consumed_stats returns proper Set[StatKey]."""

        class MultiBindingAbility(Ability):
            STAT_BINDINGS = [
                AbilityStatBinding(StatKey.DAMAGE_MULT, "damage"),
                AbilityStatBinding(StatKey.RANGE_MULT, "range"),
                AbilityStatBinding(StatKey.DAMAGE_MULT, "secondary_damage"),  # Duplicate key
            ]

        stats = MultiBindingAbility.get_consumed_stats()
        assert isinstance(stats, set)
        assert len(stats) == 2  # Duplicates deduplicated
        assert StatKey.DAMAGE_MULT in stats
        assert StatKey.RANGE_MULT in stats

    def test_effect_summary_with_add_operation(self, mock_component):
        """Effect summary works with additive bindings."""

        class AccuracyAbility(Ability):
            STAT_BINDINGS = [
                AbilityStatBinding(StatKey.ACCURACY_ADD, "accuracy", "add"),
            ]

        ability = AccuracyAbility(mock_component, {})
        ability._base_accuracy = 0.5
        ability.accuracy = 0.7
        mock_component.stats = {"accuracy_add": 0.2}

        summary = ability.get_effect_summary()
        assert len(summary) == 1
        assert summary[0]["operation"] == "add"
        assert summary[0]["stat_value"] == 0.2


class TestAbilityLayerCombinations:
    """Tests for AbilityLayer flag combinations."""

    def test_layer_flag_value_comparison(self):
        """Layer flag values are distinct integers."""
        assert AbilityLayer.COMBAT.value != AbilityLayer.STRATEGIC.value

    def test_layer_or_combination(self):
        """OR combination of layers works correctly."""
        combined = AbilityLayer.COMBAT | AbilityLayer.STRATEGIC
        assert combined == AbilityLayer.BOTH

    def test_layer_membership_check(self):
        """Membership check for flags works correctly."""
        assert AbilityLayer.COMBAT in AbilityLayer.BOTH
        assert AbilityLayer.STRATEGIC in AbilityLayer.BOTH
        assert AbilityLayer.COMBAT not in AbilityLayer.STRATEGIC


class TestAbilityScopeEdgeCases:
    """Edge cases for AbilityScope."""

    def test_scope_value_uniqueness(self):
        """All scope values are unique."""
        values = [s.value for s in AbilityScope]
        assert len(values) == len(set(values))

    def test_scope_iteration(self):
        """AbilityScope can be iterated."""
        scopes = list(AbilityScope)
        assert len(scopes) == 6
        assert AbilityScope.SELF in scopes
        assert AbilityScope.PLANET in scopes


class TestAbilityRecalculateBehavior:
    """Tests for recalculate behavior in subclasses."""

    @pytest.fixture
    def mock_component(self):
        """Create a mock component with stats."""
        component = MagicMock()
        component.stats = {}
        return component

    def test_recalculate_called_multiple_times(self, mock_component):
        """recalculate can be called multiple times without error."""

        class RecalcAbility(Ability):
            def recalculate(self):
                self.calc_count = getattr(self, 'calc_count', 0) + 1

        ability = RecalcAbility(mock_component, {})
        ability.recalculate()
        ability.recalculate()
        ability.recalculate()

        assert ability.calc_count == 3

    def test_recalculate_with_changed_stats(self, mock_component):
        """recalculate responds to stats changes."""
        mock_component.stats = {"test_mult": 1.0}

        class DynamicAbility(Ability):
            def __init__(self, component, data):
                super().__init__(component, data)
                self._base_value = 10.0
                self.value = 10.0

            def recalculate(self):
                mult = self.component.stats.get("test_mult", 1.0)
                self.value = self._base_value * mult

        ability = DynamicAbility(mock_component, {})
        assert ability.value == 10.0

        mock_component.stats["test_mult"] = 2.0
        ability.recalculate()
        assert ability.value == 20.0

        mock_component.stats["test_mult"] = 0.5
        ability.recalculate()
        assert ability.value == 5.0


# =============================================================================
# _parse_primary_value Tests
# =============================================================================


class TestParsePrimaryValue:
    """Tests for Ability._parse_primary_value static method."""

    def test_int_input(self):
        """Integer input returns float equivalent."""
        assert Ability._parse_primary_value(42) == 42.0

    def test_float_input(self):
        """Float input returns same float."""
        assert Ability._parse_primary_value(3.14) == 3.14

    def test_zero_int(self):
        """Zero integer returns 0.0."""
        assert Ability._parse_primary_value(0) == 0.0

    def test_negative(self):
        """Negative float returns same negative float."""
        assert Ability._parse_primary_value(-5.5) == -5.5

    def test_dict_with_value_key(self):
        """Dict with 'value' key returns that value as float."""
        assert Ability._parse_primary_value({'value': 100}) == 100.0

    def test_dict_missing_key_returns_default(self):
        """Dict without 'value' key returns default (0.0)."""
        assert Ability._parse_primary_value({'other': 5}) == 0.0

    def test_dict_custom_key(self):
        """Dict with custom key parameter returns that key's value."""
        assert Ability._parse_primary_value({'amount': 7}, key='amount') == 7.0

    def test_dict_custom_default(self):
        """Empty dict with custom default returns that default."""
        assert Ability._parse_primary_value({}, default=99.0) == 99.0

    def test_string_returns_default(self):
        """String input returns default (0.0)."""
        assert Ability._parse_primary_value("hello") == 0.0

    def test_none_returns_default(self):
        """None input returns default (0.0)."""
        assert Ability._parse_primary_value(None) == 0.0

    def test_bool_treated_as_int(self):
        """Boolean True is treated as int(1) and returns 1.0."""
        assert Ability._parse_primary_value(True) == 1.0

    def test_dict_with_int_value(self):
        """Dict with integer 'value' returns float."""
        assert Ability._parse_primary_value({'value': 5}) == 5.0
