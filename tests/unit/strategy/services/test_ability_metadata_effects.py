"""Tests for the effect-aggregation facet of the unified ability registry.

Originally `test_effect_ability_metadata.py` (PROJ-362 Phase 2). PROJ-454
Phase 1 retired the `effect_ability_metadata.py` shim; these
behaviour pins were rewritten to read directly through the canonical
`ability_metadata` API (`get_ability_metadata(name).effect`) and the
file was renamed to match its target module.
"""
import pytest

from game.strategy.services.ability_metadata import (
    EffectFacet,
    get_ability_metadata,
)


def _effect_facet(name: str) -> EffectFacet | None:
    meta = get_ability_metadata(name)
    return meta.effect if meta is not None else None


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


class TestEffectFacetCoverage:
    """Every legacy effect ability must surface an EffectFacet."""

    @pytest.mark.parametrize("ability_name", LEGACY_ABILITY_NAMES)
    def test_each_legacy_ability_has_effect_facet(self, ability_name):
        facet = _effect_facet(ability_name)
        assert facet is not None, (
            f"no EffectFacet on AbilityMetadata for '{ability_name}'"
        )

    def test_registry_covers_exactly_the_legacy_effect_set(self):
        """The set of names carrying an EffectFacet equals the legacy set."""
        from game.strategy.services.ability_metadata import _ENTRIES
        registered = {m.name for m in _ENTRIES if m.effect is not None}
        assert registered == set(LEGACY_ABILITY_NAMES)


class TestKindAssignment:

    @pytest.mark.parametrize("ability_name", sorted(LEGACY_RATE_ABILITIES))
    def test_legacy_rate_abilities_have_kind_rate(self, ability_name):
        facet = _effect_facet(ability_name)
        assert facet is not None
        assert facet.kind == 'rate'
        assert facet.value_field_primary == 'rate'

    @pytest.mark.parametrize(
        "ability_name",
        sorted(n for n in LEGACY_ABILITY_NAMES if n not in LEGACY_RATE_ABILITIES),
    )
    def test_non_rate_abilities_have_kind_multiplier(self, ability_name):
        facet = _effect_facet(ability_name)
        assert facet is not None
        assert facet.kind == 'multiplier'
        assert facet.value_field_primary == 'multiplier'


class TestGroupingKeyField:

    @pytest.mark.parametrize("ability_name,expected_field", [
        ('ResourceHarvestBooster', 'resource_type'),
        ('QualityImprovement', 'resource_type'),
        ('EnvironmentalDamage', 'damage_type'),
    ])
    def test_per_field_grouping_set(self, ability_name, expected_field):
        facet = _effect_facet(ability_name)
        assert facet is not None
        assert facet.grouping_key_field == expected_field

    @pytest.mark.parametrize("ability_name", [
        'GeologicStabilizer', 'StellarStabilizer', 'WarpFieldStabilizer',
        'BuildRateBooster', 'ShieldModifier', 'DamageModifier',
        'ThrustModifier', 'StrategicSpeedModifier', 'FuelDrain',
    ])
    def test_plain_grouping_uses_ability_name(self, ability_name):
        facet = _effect_facet(ability_name)
        assert facet is not None
        assert facet.grouping_key_field is None


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
        facet = _effect_facet(ability_name)
        assert facet is not None
        assert facet.display_name == expected_label

    @pytest.mark.parametrize("ability_name", [
        'ResourceHarvestBooster', 'EnvironmentalDamage',
    ])
    def test_derived_display_names_are_none(self, ability_name):
        """Display name derived from grouping_key_field at render time."""
        facet = _effect_facet(ability_name)
        assert facet is not None
        assert facet.display_name is None


class TestActivatable:

    @pytest.mark.parametrize("ability_name", [
        'GeologicStabilizer', 'StellarStabilizer', 'WarpFieldStabilizer',
    ])
    def test_stabilizers_are_activatable(self, ability_name):
        facet = _effect_facet(ability_name)
        assert facet is not None
        assert facet.is_activatable_hint is True


class TestOwnerAwareScopes:

    def test_every_effect_facet_has_full_owner_aware_scope_set(self):
        for name in LEGACY_ABILITY_NAMES:
            facet = _effect_facet(name)
            assert facet is not None
            assert facet.owner_aware_scopes == LEGACY_OWNER_AWARE_SCOPES


class TestLookupHelpers:

    def test_get_ability_metadata_returns_none_for_unknown(self):
        assert get_ability_metadata('NotARealAbility') is None

    def test_unknown_ability_has_no_effect_facet(self):
        assert _effect_facet('NotARealAbility') is None


class TestImmutability:

    def test_effect_facets_are_frozen(self):
        facet = _effect_facet('GeologicStabilizer')
        assert facet is not None
        with pytest.raises(Exception):
            facet.kind = 'rate'  # type: ignore[misc]

    def test_value_fallback_is_improvement_rate(self):
        """Legacy schemas used `improvement_rate` instead of `multiplier`/`rate`."""
        for name in LEGACY_ABILITY_NAMES:
            facet = _effect_facet(name)
            assert facet is not None
            assert facet.value_field_fallback == 'improvement_rate'
