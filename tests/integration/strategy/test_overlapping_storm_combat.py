"""PROJ-300 D18: balance regression test for overlapping-storm shield stacking.

Pre-PROJ-300 the spec compiler hardcoded `stack_group="storm_shield_interference"`
which caused overlapping storms to MAX. PROJ-300 D6 deliberately removed that
hardcoding — overlapping storms now MULTIPLY per-provider (no shared stack
group on storms). Two ion storms used to apply 0.5x shields; they now apply
0.25x.

This test locks in the new MULTIPLY behavior so a future contributor doesn't
silently reintroduce the shared stack_group.
"""
import pytest

from game.strategy.combat.strategy_modifier_stack_builder import StrategyModifierStackBuilder


def _storm_provider(name, mult):
    """Build a sector-effect provider entry as the collector would emit."""
    return {
        'source_kind': 'storm',
        'source_label': name,
        'source_id': f'storm:{name}',
        'owner_id': None,
        'status': 'Active',
        'is_active': True,
        'value': mult,
        'ability_data': {'multiplier': mult, 'scope': 'sector'},  # No stack_group on storms
    }


def _shield_effect(*providers):
    """Build a sector-effect dict for ShieldModifier with the given providers."""
    return {
        'ability_name': 'ShieldModifier',
        'display_name': 'Shield Modifier',
        'group_key': 'ShieldModifier',
        'status': 'Active',
        'resource_type': None,
        'damage_type': None,
        'kind': 'multiplier',
        'aggregate_value': 1.0,  # Aggregator computes; not used by spec_compiler
        'providers': list(providers),
    }


class TestOverlappingStormShieldStacking:
    """PROJ-300 D6 + D18 — overlapping storms MULTIPLY, do NOT MAX."""

    def test_single_ion_storm_emits_one_shield_entry(self):
        effects = [_shield_effect(_storm_provider("Ion Storm Alpha", 0.5))]
        # PROJ-343 T1.3-combat: function now returns (global, per_team).
        # All providers here are ownerless (storms) so they go to global.
        entries, _per_team = StrategyModifierStackBuilder().entries_from_sector_effects(effects)
        assert len(entries) == 1
        assert entries[0].effect.value == pytest.approx(0.5)
        assert entries[0].stack_group is None

    def test_two_overlapping_ion_storms_emit_two_independent_entries(self):
        """Locked-in MULTIPLY: two storms = two ungrouped entries.

        Each entry's stack_group is None (from storm ability_data). The combat
        aggregator MULTIPLIES across non-shared groups: 0.5 x 0.5 = 0.25.
        """
        effects = [_shield_effect(
            _storm_provider("Ion Storm Alpha", 0.5),
            _storm_provider("Ion Storm Beta", 0.5),
        )]
        # PROJ-343 T1.3-combat: function now returns (global, per_team).
        # All providers here are ownerless (storms) so they go to global.
        entries, _per_team = StrategyModifierStackBuilder().entries_from_sector_effects(effects)
        assert len(entries) == 2
        for entry in entries:
            assert entry.effect.value == pytest.approx(0.5)
            assert entry.stack_group is None
        # Each provider is its own source so the combat-side aggregator
        # treats them as distinct ungrouped entries.
        source_ids = sorted(e.effect.source_modifier_id for e in entries)
        assert source_ids == sorted(['storm:Ion Storm Alpha', 'storm:Ion Storm Beta'])

    def test_three_overlapping_ion_storms_emit_three_independent_entries(self):
        effects = [_shield_effect(
            _storm_provider("A", 0.5),
            _storm_provider("B", 0.5),
            _storm_provider("C", 0.5),
        )]
        # PROJ-343 T1.3-combat: function now returns (global, per_team).
        # All providers here are ownerless (storms) so they go to global.
        entries, _per_team = StrategyModifierStackBuilder().entries_from_sector_effects(effects)
        assert len(entries) == 3
        for entry in entries:
            assert entry.effect.value == pytest.approx(0.5)
            assert entry.stack_group is None

    def test_facility_with_stack_group_keeps_grouping(self):
        """Facilities CAN declare a stack_group; only storms emit ungrouped."""
        facility_provider = {
            'source_kind': 'facility',
            'source_label': 'Shield Generator',
            'source_id': 'facility:abc',
            'owner_id': 1,
            'status': 'Active',
            'is_active': True,
            'value': 0.8,
            'ability_data': {
                'multiplier': 0.8,
                'scope': 'sector',
                'stack_group': 'planetary_shields',
            },
        }
        effects = [_shield_effect(facility_provider)]
        # PROJ-343 T1.3-combat: function now returns (global, per_team).
        # All providers here are ownerless (storms) so they go to global.
        entries, _per_team = StrategyModifierStackBuilder().entries_from_sector_effects(effects)
        assert len(entries) == 1
        assert entries[0].stack_group == 'planetary_shields'

    def test_inactive_provider_is_skipped(self):
        active = _storm_provider("Active Storm", 0.5)
        inactive = _storm_provider("Inactive Storm", 0.5)
        inactive['is_active'] = False
        effects = [_shield_effect(active, inactive)]
        # PROJ-343 T1.3-combat: function now returns (global, per_team).
        # All providers here are ownerless (storms) so they go to global.
        entries, _per_team = StrategyModifierStackBuilder().entries_from_sector_effects(effects)
        assert len(entries) == 1
        assert entries[0].effect.source_modifier_id == 'storm:Active Storm'

    def test_thrust_modifier_emits_entry_per_d14(self):
        """PROJ-300 D14: ThrustModifier flows through spec_compiler now."""
        effects = [{
            'ability_name': 'ThrustModifier',
            'display_name': 'Thrust Modifier',
            'group_key': 'ThrustModifier',
            'status': 'Active',
            'resource_type': None,
            'damage_type': None,
            'kind': 'multiplier',
            'aggregate_value': 0.6,
            'providers': [_storm_provider("Gravity Anomaly", 0.6)],
        }]
        # PROJ-343 T1.3-combat: function now returns (global, per_team).
        # All providers here are ownerless (storms) so they go to global.
        entries, _per_team = StrategyModifierStackBuilder().entries_from_sector_effects(effects)
        assert len(entries) == 1
        assert entries[0].effect.value == pytest.approx(0.6)
        assert entries[0].effect.stat_key == 'thrust_mult'  # ABILITY_STAT_REGISTRY mapping

    def test_two_overlapping_thrust_modifiers_multiply(self):
        """Two storms with ThrustModifier 0.6 each = 0.36x effective thrust."""
        effects = [{
            'ability_name': 'ThrustModifier',
            'display_name': 'Thrust Modifier',
            'group_key': 'ThrustModifier',
            'status': 'Active',
            'resource_type': None,
            'damage_type': None,
            'kind': 'multiplier',
            'aggregate_value': 0.36,
            'providers': [
                _storm_provider("A", 0.6),
                _storm_provider("B", 0.6),
            ],
        }]
        # PROJ-343 T1.3-combat: function now returns (global, per_team).
        # All providers here are ownerless (storms) so they go to global.
        entries, _per_team = StrategyModifierStackBuilder().entries_from_sector_effects(effects)
        assert len(entries) == 2
        for entry in entries:
            assert entry.effect.value == pytest.approx(0.6)
            assert entry.stack_group is None  # Multiply, not max
