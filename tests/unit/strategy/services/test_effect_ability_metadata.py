"""Tests for EffectAbilityMetadata registry (PROJ-362 Phase 2)."""
import pytest

from game.strategy.services.effect_ability_metadata import (
    EFFECT_ABILITY_METADATA,
    EffectAbilityMetadata,
    all_owner_aware_scopes,
    find_metadata,
    is_known_effect_ability,
)


# Legacy ability set previously hardcoded in
# `system_effects_collector.SYSTEM_EFFECT_ABILITIES`. Pinned here so the
# refactor cannot silently drop or rename an entry.
LEGACY_ABILITY_NAMES = (
    'GeologicStabilizer',
    'StellarStabilizer',
    'WarpFieldStabilizer',
    'ResourceHarvestBooster',
    'BuildRateBooster',
    'QualityImprovement',
    'ShieldModifier',
    'DamageModifier',
    'ThrustModifier',
    'StrategicSpeedModifier',
    'EnvironmentalDamage',
    'FuelDrain',
)


# Legacy `_OWNER_AWARE_SCOPES` set, pinned to detect drift.
LEGACY_OWNER_AWARE_SCOPES = frozenset({
    'allied_sector', 'enemy_sector', 'player_sector',
    'allied_system', 'enemy_system', 'player_system',
    'allied_empire',
})


# Legacy `_RATE_ABILITIES` set.
LEGACY_RATE_ABILITIES = frozenset({'EnvironmentalDamage', 'FuelDrain'})


class TestRegistryContract:
    """The registry must cover every ability name the legacy code recognized."""

    @pytest.mark.parametrize("ability_name", LEGACY_ABILITY_NAMES)
    def test_metadata_for_each_legacy_ability_name(self, ability_name):
        m = find_metadata(ability_name)
        assert m is not None, f"no EffectAbilityMetadata entry for '{ability_name}'"
        assert m.ability_name == ability_name

    def test_registry_covers_exactly_the_legacy_set(self):
        registered = {m.ability_name for m in EFFECT_ABILITY_METADATA}
        assert registered == set(LEGACY_ABILITY_NAMES)


class TestKindAssignment:

    @pytest.mark.parametrize("ability_name", sorted(LEGACY_RATE_ABILITIES))
    def test_legacy_rate_abilities_have_kind_rate(self, ability_name):
        m = find_metadata(ability_name)
        assert m is not None
        assert m.kind == 'rate'
        assert m.value_field_primary == 'rate'

    @pytest.mark.parametrize(
        "ability_name",
        sorted(n for n in LEGACY_ABILITY_NAMES if n not in LEGACY_RATE_ABILITIES),
    )
    def test_non_rate_abilities_have_kind_multiplier(self, ability_name):
        m = find_metadata(ability_name)
        assert m is not None
        assert m.kind == 'multiplier'
        assert m.value_field_primary == 'multiplier'


class TestGroupingKeyField:

    @pytest.mark.parametrize("ability_name,expected_field", [
        ('ResourceHarvestBooster', 'resource_type'),
        ('QualityImprovement', 'resource_type'),
        ('EnvironmentalDamage', 'damage_type'),
    ])
    def test_per_field_grouping_set(self, ability_name, expected_field):
        m = find_metadata(ability_name)
        assert m is not None
        assert m.grouping_key_field == expected_field

    @pytest.mark.parametrize("ability_name", [
        'GeologicStabilizer', 'StellarStabilizer', 'WarpFieldStabilizer',
        'BuildRateBooster', 'ShieldModifier', 'DamageModifier',
        'ThrustModifier', 'StrategicSpeedModifier', 'FuelDrain',
    ])
    def test_plain_grouping_uses_ability_name(self, ability_name):
        m = find_metadata(ability_name)
        assert m is not None
        assert m.grouping_key_field is None


class TestDisplayName:

    @pytest.mark.parametrize("ability_name,expected_label", [
        ('GeologicStabilizer', 'Geologic Stabilizer'),
        ('StellarStabilizer', 'Stellar Stabilizer'),
        ('WarpFieldStabilizer', 'Warp Field Stabilizer'),
        ('BuildRateBooster', 'Construction Acceleration'),
        ('QualityImprovement', 'Quality Enrichment'),
        ('ShieldModifier', 'Shield Modifier'),
        ('DamageModifier', 'Damage Modifier'),
        ('ThrustModifier', 'Thrust Modifier'),
        ('StrategicSpeedModifier', 'Strategic Speed Modifier'),
        ('FuelDrain', 'Fuel Drain'),
    ])
    def test_explicit_display_names_match_legacy_labels(self, ability_name, expected_label):
        m = find_metadata(ability_name)
        assert m is not None
        assert m.display_name == expected_label

    @pytest.mark.parametrize("ability_name", [
        'ResourceHarvestBooster', 'EnvironmentalDamage',
    ])
    def test_derived_display_names_are_none(self, ability_name):
        """Display name derived from grouping_key_field at render time."""
        m = find_metadata(ability_name)
        assert m is not None
        assert m.display_name is None


class TestActivatable:

    @pytest.mark.parametrize("ability_name", [
        'GeologicStabilizer', 'StellarStabilizer', 'WarpFieldStabilizer',
    ])
    def test_stabilizers_are_activatable(self, ability_name):
        m = find_metadata(ability_name)
        assert m is not None
        assert m.is_activatable is True


class TestOwnerAwareScopes:

    def test_every_entry_has_full_owner_aware_scope_set(self):
        for m in EFFECT_ABILITY_METADATA:
            assert m.owner_aware_scopes == LEGACY_OWNER_AWARE_SCOPES

    def test_all_owner_aware_scopes_returns_legacy_set(self):
        assert all_owner_aware_scopes() == LEGACY_OWNER_AWARE_SCOPES


class TestLookupHelpers:

    def test_find_metadata_returns_none_for_unknown(self):
        assert find_metadata('NotARealAbility') is None

    def test_is_known_effect_ability_true_for_registered(self):
        assert is_known_effect_ability('GeologicStabilizer') is True

    def test_is_known_effect_ability_false_for_unknown(self):
        assert is_known_effect_ability('NotARealAbility') is False


class TestImmutability:

    def test_metadata_entries_are_frozen(self):
        m = find_metadata('GeologicStabilizer')
        assert m is not None
        with pytest.raises(Exception):
            m.kind = 'rate'  # type: ignore[misc]

    def test_value_fallback_is_improvement_rate(self):
        """Legacy schemas used `improvement_rate` instead of `multiplier`/`rate`."""
        for m in EFFECT_ABILITY_METADATA:
            assert m.value_field_fallback == 'improvement_rate'
