"""PROJ-343 T1.3-combat — ownerful sector effects must NOT leak into the
opponent's modifier stack during combat.

Codex flagged this as a merge-blocker (discussion 20260505T020232Z) after the
env-hazard fix landed. The combat path takes a different route through
`_lookup_environmental_effects` → `resolve_battle` → `build_strategy_battle_spec`
→ `_build_modifier_stack` → `_entries_from_sector_effects`. The pre-fix
function emits every provider as a global entry with `owner_team=0`, so any
empire's facility-projected ShieldModifier / DamageModifier / ThrustModifier
ends up applying to BOTH combatants.

Fix shape (Option B with per-team split, agreed in arc01_004 + arc01_005):
- `_entries_from_sector_effects` accepts `empire_to_team_id` + `team_count`,
  returns `(global_entries, per_team_entries)`.
- Ownerless providers (storms) route to `global_entries`.
- Ownerful providers whose `owner_id` is in `empire_to_team_id` route to
  `per_team_entries[<team_id>]`.
- Ownerful providers whose owner is not a combatant are dropped (the effect
  has no relevant team to apply to in this battle).

This file pins that contract.
"""
from __future__ import annotations

from game.strategy.combat.spec_compiler import _entries_from_sector_effects


def _ownerful_facility_provider(owner_id: int, source_id: str, mult: float):
    """Build a facility provider as the collector would emit."""
    return {
        'source_kind': 'facility',
        'source_label': f'Facility {source_id}',
        'source_id': source_id,
        'owner_id': owner_id,
        'status': 'Active',
        'is_active': True,
        'value': mult,
        'ability_data': {'multiplier': mult, 'scope': 'sector'},
    }


def _storm_provider(label: str, mult: float):
    return {
        'source_kind': 'storm',
        'source_label': label,
        'source_id': f'storm:{label}',
        'owner_id': None,
        'status': 'Active',
        'is_active': True,
        'value': mult,
        'ability_data': {'multiplier': mult, 'scope': 'sector'},
    }


def _shield_effect(*providers):
    return {
        'ability_name': 'ShieldModifier',
        'display_name': 'Shield Modifier',
        'group_key': 'ShieldModifier',
        'status': 'Active',
        'resource_type': None,
        'damage_type': None,
        'kind': 'multiplier',
        'aggregate_value': 1.0,
        'providers': list(providers),
    }


class TestOwnerfulSectorEffectIsolation:
    """PROJ-343 T1.3-combat: ownerful sector effects route to the owning
    team only; ownerless storms still apply globally."""

    def test_ownerful_facility_routes_to_owning_team_only(self):
        """A ShieldModifier facility owned by empire 1 (team 0) must NOT
        produce any modifier entry that applies to empire 2 (team 1)."""
        effects = [_shield_effect(
            _ownerful_facility_provider(owner_id=1, source_id='fac_a', mult=0.5)
        )]

        global_entries, per_team_entries = _entries_from_sector_effects(
            effects,
            empire_to_team_id={1: 0, 2: 1},
            team_count=2,
        )

        # Ownerful provider emits to per-team[0] only.
        assert len(global_entries) == 0
        assert len(per_team_entries.get(0, [])) == 1
        assert len(per_team_entries.get(1, [])) == 0
        assert per_team_entries[0][0].effect.source_modifier_id == 'fac_a'

    def test_ownerless_storm_routes_to_global(self):
        """A storm with `owner_id=None` must still apply globally."""
        effects = [_shield_effect(_storm_provider('Ion Storm', 0.5))]

        global_entries, per_team_entries = _entries_from_sector_effects(
            effects,
            empire_to_team_id={1: 0, 2: 1},
            team_count=2,
        )

        assert len(global_entries) == 1
        assert global_entries[0].effect.source_modifier_id == 'storm:Ion Storm'
        # Storm should NOT contribute to any per-team bucket.
        assert all(len(entries) == 0 for entries in per_team_entries.values())

    def test_mixed_storm_and_ownerful_facility_split_correctly(self):
        """Both shapes coexist — storm goes global, facility goes to its team."""
        effects = [_shield_effect(
            _storm_provider('Storm A', 0.5),
            _ownerful_facility_provider(owner_id=1, source_id='fac_b', mult=0.7),
        )]

        global_entries, per_team_entries = _entries_from_sector_effects(
            effects,
            empire_to_team_id={1: 0, 2: 1},
            team_count=2,
        )

        assert len(global_entries) == 1
        assert global_entries[0].effect.source_modifier_id == 'storm:Storm A'
        assert len(per_team_entries.get(0, [])) == 1
        assert per_team_entries[0][0].effect.source_modifier_id == 'fac_b'
        assert len(per_team_entries.get(1, [])) == 0

    def test_ownerful_facility_with_non_combatant_owner_is_dropped(self):
        """If the owner empire isn't a combatant in this battle, the effect
        has no team to apply to and must NOT leak into global."""
        effects = [_shield_effect(
            _ownerful_facility_provider(owner_id=99, source_id='ghost', mult=0.5)
        )]

        global_entries, per_team_entries = _entries_from_sector_effects(
            effects,
            empire_to_team_id={1: 0, 2: 1},
            team_count=2,
        )

        assert len(global_entries) == 0
        assert all(len(entries) == 0 for entries in per_team_entries.values())

    def test_legacy_call_without_mapping_falls_back_to_all_global(self):
        """Backward-compat: callers that don't pass empire_to_team_id still
        get a single (global, empty-per-team) tuple. Existing pre-fix tests
        that don't know about the per-team split keep working."""
        effects = [_shield_effect(
            _storm_provider('S1', 0.5),
            _ownerful_facility_provider(owner_id=1, source_id='fac_c', mult=0.6),
        )]

        global_entries, per_team_entries = _entries_from_sector_effects(effects)

        # Without mapping, both providers fall through to global (preserving
        # pre-PROJ-343-T1.3-combat semantics for legacy callers).
        assert len(global_entries) == 2
        assert per_team_entries == {}
