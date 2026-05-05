"""Characterization tests for system_effects_collector._aggregate (PROJ-362 Phase 1).

These tests pin the CURRENT behavior of `_aggregate` so the Phase 2-3 refactor
(EffectAbilityMetadata registry + decomposition into collect_providers /
aggregate_status / aggregate_value / format_rows) is protected by a green
baseline. They are characterization, not red-green TDD: they MUST pass against
the current pre-refactor code. If a test fails against current behavior,
the test is wrong (current behavior is the spec) — adjust the test.

Review finding #2 (P1 hotspot) — `_aggregate` CC=47, 193 LOC, hardcoded
ability metadata. Branches not previously exercised in isolation:
  - `get_abilities()` exception path (production logs + skips, never tested in isolation)
  - `affects_hex` exception path
  - DEACTIVATING activation phase
  - Mixed activation-state precedence (any_active > any_activating > any_deactivating)
  - Owned source filtered by empire_id mismatch
  - improvement_rate field fallback when neither rate nor multiplier is present

Tests bypass the public `collect_*` entry points (which iterate via
`iter_ability_sources_*`) and call `_aggregate` directly with hand-built
IAbilitySource-shaped objects. This isolates the aggregator from the iterator
plumbing — the contract under refactor is the aggregation pipeline, not the
iterator.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import logging

import pytest

from game.strategy.data.component_activation_state import (
    ActivationPhase,
    ComponentActivationState,
)
from game.strategy.services.system_effects_collector import (
    _SECTOR_SCOPES,
    _SYSTEM_SCOPES,
    _aggregate,
)


# ---------------------------------------------------------------------------
# Hand-rolled IAbilitySource fakes (avoid MagicMock so attribute access raises
# correctly when needed — `affects_hex` exception path is hard to express
# with the auto-attr behavior of MagicMock).
# ---------------------------------------------------------------------------


@dataclass
class _FakeSource:
    """Minimal IAbilitySource implementation for direct _aggregate testing."""
    source_kind: str = 'facility'
    source_label: str = 'fake-source'
    source_id: str = 'facility:fake-1'
    owner_id: Optional[int] = None
    abilities: Dict[str, Any] = field(default_factory=dict)
    activation_states: Dict[str, ComponentActivationState] = field(default_factory=dict)
    affects_hex_result: bool = True

    # facility/planet attrs read by _legacy_provider_fields
    facility: Any = None
    planet: Any = None

    def get_abilities(self) -> Dict[str, Any]:
        return self.abilities

    def affects_hex(self, hex_coord) -> bool:
        return self.affects_hex_result

    def get_activation_state(self, ability_name: str) -> Optional[ComponentActivationState]:
        return self.activation_states.get(ability_name)


class _RaisingGetAbilitiesSource(_FakeSource):
    """Source whose get_abilities() raises — exercises pipeline error tolerance."""
    def get_abilities(self) -> Dict[str, Any]:
        raise RuntimeError("simulated get_abilities failure")


class _RaisingAffectsHexSource(_FakeSource):
    """Source whose affects_hex() raises — exercises pipeline error tolerance."""
    def affects_hex(self, hex_coord) -> bool:
        raise RuntimeError("simulated affects_hex failure")


def _stabilizer_entry(scope: str = 'system') -> Dict[str, Any]:
    """Sample multiplier-style activatable entry."""
    return {
        'scope': scope,
        'energy_drain_rate': 50.0,
        'activation_time': 250,
        'deactivation_time': 150,
        'multiplier': 1.0,
    }


# ---------------------------------------------------------------------------
# Task 1.2: get_abilities() exception path
# ---------------------------------------------------------------------------


class TestGetAbilitiesException:

    def test_get_abilities_exception_skips_source_and_logs(self, caplog):
        bad = _RaisingGetAbilitiesSource(source_id='facility:bad')
        good = _FakeSource(
            source_id='facility:good',
            abilities={'GeologicStabilizer': _stabilizer_entry('system')},
            activation_states={
                'GeologicStabilizer': ComponentActivationState(
                    phase=ActivationPhase.ACTIVE,
                    ability_name='GeologicStabilizer',
                ),
            },
        )

        with caplog.at_level(logging.WARNING):
            result = _aggregate(
                [bad, good], _SYSTEM_SCOPES, empire_id=None, registries=None,
                hex_coord=None, system=None,
            )

        # The good source contributes; the bad source contributes nothing.
        assert len(result) == 1
        assert result[0]['ability_name'] == 'GeologicStabilizer'
        assert len(result[0]['providers']) == 1
        assert result[0]['providers'][0]['source_id'] == 'facility:good'
        # Warning was logged for the failing source.
        assert any('get_abilities' in rec.message for rec in caplog.records)


# ---------------------------------------------------------------------------
# Task 1.3: affects_hex exception path
# ---------------------------------------------------------------------------


class TestAffectsHexException:

    def test_affects_hex_exception_skips_source_and_logs(self, caplog):
        bad = _RaisingAffectsHexSource(source_id='facility:bad')
        good = _FakeSource(
            source_id='facility:good',
            abilities={'ShieldModifier': {'multiplier': 0.5, 'scope': 'sector'}},
        )

        with caplog.at_level(logging.WARNING):
            result = _aggregate(
                [bad, good], _SECTOR_SCOPES, empire_id=None, registries=None,
                hex_coord='HEX', system=None,
            )

        # Good contributes, bad does not.
        ability_names = {e['ability_name'] for e in result}
        assert 'ShieldModifier' in ability_names
        assert any('affects_hex' in rec.message for rec in caplog.records)

    def test_affects_hex_false_return_skips_source(self):
        """affects_hex returning False (no exception) silently filters the source."""
        denying = _FakeSource(
            source_id='facility:no-hex',
            affects_hex_result=False,
            abilities={'ShieldModifier': {'multiplier': 0.5, 'scope': 'sector'}},
        )
        result = _aggregate(
            [denying], _SECTOR_SCOPES, empire_id=None, registries=None,
            hex_coord='HEX', system=None,
        )
        assert result == []


# ---------------------------------------------------------------------------
# Task 1.4 + 1.5: DEACTIVATING and mixed activation-state precedence
# ---------------------------------------------------------------------------


class TestActivationStatePrecedence:

    def test_deactivating_ability_shows_progress_remaining(self):
        """A single DEACTIVATING activatable shows status string with remaining ticks."""
        source = _FakeSource(
            abilities={'GeologicStabilizer': _stabilizer_entry('system')},
            activation_states={
                'GeologicStabilizer': ComponentActivationState(
                    phase=ActivationPhase.DEACTIVATING,
                    progress_ticks=2,
                    required_ticks=5,
                    ability_name='GeologicStabilizer',
                ),
            },
        )
        result = _aggregate(
            [source], _SYSTEM_SCOPES, empire_id=None, registries=None,
            hex_coord=None, system=None,
        )
        assert len(result) == 1
        provider = result[0]['providers'][0]
        # Provider-level status preserves the per-source progress string.
        assert provider['status'] == 'Deactivating (3)'
        assert provider['is_active'] is False

    def test_any_active_overrides_activating_and_deactivating(self):
        """Mixed group: ACTIVE provider wins; status is 'Active'."""
        active_source = _FakeSource(
            source_id='f:active',
            abilities={'GeologicStabilizer': _stabilizer_entry('system')},
            activation_states={
                'GeologicStabilizer': ComponentActivationState(
                    phase=ActivationPhase.ACTIVE,
                    ability_name='GeologicStabilizer',
                ),
            },
        )
        activating_source = _FakeSource(
            source_id='f:activating',
            abilities={'GeologicStabilizer': _stabilizer_entry('system')},
            activation_states={
                'GeologicStabilizer': ComponentActivationState(
                    phase=ActivationPhase.ACTIVATING,
                    progress_ticks=10,
                    required_ticks=100,
                    ability_name='GeologicStabilizer',
                ),
            },
        )
        deactivating_source = _FakeSource(
            source_id='f:deactivating',
            abilities={'GeologicStabilizer': _stabilizer_entry('system')},
            activation_states={
                'GeologicStabilizer': ComponentActivationState(
                    phase=ActivationPhase.DEACTIVATING,
                    progress_ticks=2,
                    required_ticks=5,
                    ability_name='GeologicStabilizer',
                ),
            },
        )
        result = _aggregate(
            [active_source, activating_source, deactivating_source],
            _SYSTEM_SCOPES, empire_id=None, registries=None,
            hex_coord=None, system=None,
        )
        assert len(result) == 1
        assert result[0]['status'] == 'Active'

    def test_activating_when_no_active_uses_first_activating_status(self):
        """No ACTIVE provider; first ACTIVATING provider's status string wins."""
        a1 = _FakeSource(
            source_id='f:a1',
            abilities={'GeologicStabilizer': _stabilizer_entry('system')},
            activation_states={
                'GeologicStabilizer': ComponentActivationState(
                    phase=ActivationPhase.ACTIVATING,
                    progress_ticks=20,
                    required_ticks=100,
                    ability_name='GeologicStabilizer',
                ),
            },
        )
        a2 = _FakeSource(
            source_id='f:a2',
            abilities={'GeologicStabilizer': _stabilizer_entry('system')},
            activation_states={
                'GeologicStabilizer': ComponentActivationState(
                    phase=ActivationPhase.ACTIVATING,
                    progress_ticks=50,
                    required_ticks=100,
                    ability_name='GeologicStabilizer',
                ),
            },
        )
        inactive = _FakeSource(
            source_id='f:inactive',
            abilities={'GeologicStabilizer': _stabilizer_entry('system')},
            # No activation state — defaults to INACTIVE.
        )
        result = _aggregate(
            [a1, a2, inactive], _SYSTEM_SCOPES, empire_id=None, registries=None,
            hex_coord=None, system=None,
        )
        assert len(result) == 1
        # First Activating provider's progress string wins (a1: 100-20=80).
        assert result[0]['status'] == 'Activating (80)'

    def test_deactivating_when_no_active_or_activating(self):
        """Group with one DEACTIVATING and one INACTIVE → 'Deactivating'."""
        deact = _FakeSource(
            source_id='f:deact',
            abilities={'GeologicStabilizer': _stabilizer_entry('system')},
            activation_states={
                'GeologicStabilizer': ComponentActivationState(
                    phase=ActivationPhase.DEACTIVATING,
                    progress_ticks=1,
                    required_ticks=5,
                    ability_name='GeologicStabilizer',
                ),
            },
        )
        inactive = _FakeSource(
            source_id='f:inactive',
            abilities={'GeologicStabilizer': _stabilizer_entry('system')},
        )
        result = _aggregate(
            [deact, inactive], _SYSTEM_SCOPES, empire_id=None, registries=None,
            hex_coord=None, system=None,
        )
        assert len(result) == 1
        assert result[0]['status'] == 'Deactivating'


# ---------------------------------------------------------------------------
# Task 1.6: Owner / empire_id filtering
# ---------------------------------------------------------------------------


class TestOwnerFiltering:

    def test_owned_source_skipped_when_empire_id_mismatches_query(self):
        """owner_id=2 source contributes nothing to empire_id=1 query."""
        source = _FakeSource(
            owner_id=2,
            abilities={'ShieldModifier': {'multiplier': 0.5, 'scope': 'system'}},
        )
        result = _aggregate(
            [source], _SYSTEM_SCOPES, empire_id=1, registries=None,
            hex_coord=None, system=None,
        )
        assert result == []

    def test_ownerless_source_contributes_to_any_empire_query(self):
        """owner_id=None contributes regardless of empire_id."""
        source_template = lambda: _FakeSource(
            owner_id=None,
            source_kind='storm',
            source_label='Storm',
            source_id='storm:S',
            abilities={'ShieldModifier': {'multiplier': 0.5, 'scope': 'sector'}},
        )

        for empire_id in (1, 2):
            result = _aggregate(
                [source_template()], _SECTOR_SCOPES, empire_id=empire_id,
                registries=None, hex_coord='HEX', system=None,
            )
            ability_names = {e['ability_name'] for e in result}
            assert 'ShieldModifier' in ability_names, (
                f"empire_id={empire_id}: ownerless source did not contribute"
            )


# ---------------------------------------------------------------------------
# Task 1.6b: unknown abilities / malformed entries filter out cleanly
# ---------------------------------------------------------------------------


class TestAbilityEntryFiltering:

    def test_unknown_ability_and_non_dict_entries_are_skipped(self):
        source = _FakeSource(
            abilities={
                'NotARealEffectAbility': {'scope': 'system', 'multiplier': 0.5},
                'ShieldModifier': [
                    True,
                    {'multiplier': 0.8, 'scope': 'planet'},
                ],
            },
        )

        result = _aggregate(
            [source], _SYSTEM_SCOPES, empire_id=None, registries=None,
            hex_coord=None, system=None,
        )

        assert result == []


# ---------------------------------------------------------------------------
# Task 1.7: improvement_rate field fallback
# ---------------------------------------------------------------------------


class TestImprovementRateFallback:

    def test_improvement_rate_field_used_when_multiplier_missing(self):
        """For a multiplier-style ability with no `multiplier` field but a legacy
        `improvement_rate` field, _aggregate reads the value from improvement_rate.

        QualityImprovement is multiplier-style but historical schemas used
        `improvement_rate` instead of `multiplier`.
        """
        source = _FakeSource(
            source_id='facility:legacy',
            abilities={
                'QualityImprovement': {
                    'scope': 'system',
                    'resource_type': 'metals',
                    'improvement_rate': 0.15,
                },
            },
        )
        result = _aggregate(
            [source], _SYSTEM_SCOPES, empire_id=None, registries=None,
            hex_coord=None, system=None,
        )
        assert len(result) == 1
        # Provider value reads from improvement_rate (0.15).
        provider = result[0]['providers'][0]
        assert provider['value'] == pytest.approx(0.15)
