"""Direct unit tests for the decomposed `_aggregate` helpers (PROJ-362 Phase 3).

`_aggregate` was split into four helpers:
  - `_collect_providers` (covered indirectly by characterization tests)
  - `_aggregate_status`
  - `_aggregate_value`
  - `_format_rows`

These tests pin the contract of each helper in isolation so future edits
can target one concern at a time.
"""
import logging

import pytest

from game.strategy.services.system_effects_collector import (
    _aggregate_status,
    _aggregate_value,
    _format_rows,
)


def _provider(*, status: str, is_active: bool, value: float = 1.0,
              ability_data: dict | None = None) -> dict:
    """Build a minimal provider dict for status/value aggregation tests."""
    return {
        'status': status,
        'is_active': is_active,
        'value': value,
        'ability_data': ability_data if ability_data is not None else {'multiplier': value},
    }


# ---------------------------------------------------------------------------
# _aggregate_status
# ---------------------------------------------------------------------------


class TestAggregateStatus:

    def test_all_active_returns_active(self):
        providers = [
            _provider(status='Active', is_active=True),
            _provider(status='Active', is_active=True),
        ]
        assert _aggregate_status(providers) == "Active"

    def test_mixed_active_activating_deactivating_returns_active(self):
        providers = [
            _provider(status='Active', is_active=True),
            _provider(status='Activating (50)', is_active=False),
            _provider(status='Deactivating (3)', is_active=False),
        ]
        assert _aggregate_status(providers) == "Active"

    def test_only_activating_returns_first_activating_string(self):
        providers = [
            _provider(status='Activating (80)', is_active=False),
            _provider(status='Activating (50)', is_active=False),
            _provider(status='Inactive', is_active=False),
        ]
        # First activating provider's progress string wins.
        assert _aggregate_status(providers) == "Activating (80)"

    def test_only_deactivating_returns_deactivating(self):
        providers = [
            _provider(status='Deactivating (3)', is_active=False),
            _provider(status='Inactive', is_active=False),
        ]
        assert _aggregate_status(providers) == "Deactivating"

    def test_all_inactive_returns_inactive(self):
        providers = [
            _provider(status='Inactive', is_active=False),
            _provider(status='Inactive', is_active=False),
        ]
        assert _aggregate_status(providers) == "Inactive"

    def test_empty_providers_returns_inactive(self):
        # Defensive — _collect_providers would never produce an empty group,
        # but the helper should still terminate cleanly.
        assert _aggregate_status([]) == "Inactive"


# ---------------------------------------------------------------------------
# _aggregate_value
# ---------------------------------------------------------------------------


class TestAggregateValue:

    def test_rate_kind_sums_active_entries(self):
        """Rate-style: aggregate via `aggregate_rates` (additive)."""
        providers = [
            _provider(
                status='Active', is_active=True, value=0.5,
                ability_data={'rate': 0.5, 'damage_type': 'plasma',
                              'stack_group': 'plasma_a'},
            ),
            _provider(
                status='Active', is_active=True, value=0.3,
                ability_data={'rate': 0.3, 'damage_type': 'plasma',
                              'stack_group': 'plasma_b'},
            ),
        ]
        result = _aggregate_value(providers, kind='rate', group_key='EnvironmentalDamage:plasma')
        assert result == pytest.approx(0.8)

    def test_multiplier_kind_aggregates_via_aggregate_multipliers(self):
        """Multiplier-style: same-stack-group entries take MAX, not product."""
        providers = [
            _provider(
                status='Active', is_active=True, value=1.3,
                ability_data={'multiplier': 1.3, 'stack_group': 'harvest_metals'},
            ),
            _provider(
                status='Active', is_active=True, value=1.3,
                ability_data={'multiplier': 1.3, 'stack_group': 'harvest_metals'},
            ),
        ]
        # Same stack_group → MAX, not 1.3*1.3.
        result = _aggregate_value(
            providers, kind='multiplier',
            group_key='ResourceHarvestBooster:metals',
        )
        assert result == pytest.approx(1.3)

    def test_inactive_only_falls_back_to_would_be_value(self):
        """When no provider is active, all entries' values still aggregate."""
        providers = [
            _provider(
                status='Inactive', is_active=False, value=1.5,
                ability_data={'multiplier': 1.5, 'stack_group': 'shield'},
            ),
        ]
        result = _aggregate_value(
            providers, kind='multiplier', group_key='ShieldModifier',
        )
        assert result == pytest.approx(1.5)

    def test_mixed_kind_multiplier_in_rate_group_skipped_with_warning(self, caplog):
        """A multiplier-only entry in a rate group is skipped + logged (D16)."""
        providers = [
            _provider(
                status='Active', is_active=True, value=0.5,
                ability_data={'rate': 0.5, 'damage_type': 'plasma'},
            ),
            _provider(
                status='Active', is_active=True, value=0.7,
                ability_data={'multiplier': 0.7, 'damage_type': 'plasma'},  # bad
            ),
        ]
        with caplog.at_level(logging.WARNING):
            result = _aggregate_value(
                providers, kind='rate',
                group_key='EnvironmentalDamage:plasma',
            )
        # Only the rate-style entry survives → 0.5.
        assert result == pytest.approx(0.5)
        assert any('D16' in rec.message for rec in caplog.records)

    def test_mixed_kind_rate_in_multiplier_group_skipped_with_warning(self, caplog):
        providers = [
            _provider(
                status='Active', is_active=True, value=1.3,
                ability_data={'multiplier': 1.3, 'stack_group': 'shield'},
            ),
            _provider(
                status='Active', is_active=True, value=0.5,
                ability_data={'rate': 0.5},  # bad
            ),
        ]
        with caplog.at_level(logging.WARNING):
            result = _aggregate_value(
                providers, kind='multiplier', group_key='ShieldModifier',
            )
        # Only the multiplier survives → 1.3.
        assert result == pytest.approx(1.3)
        assert any('D16' in rec.message for rec in caplog.records)


# ---------------------------------------------------------------------------
# _format_rows
# ---------------------------------------------------------------------------


class TestFormatRows:

    def test_format_rows_emits_public_shape(self):
        raw_providers = {
            'GeologicStabilizer': {
                'ability_name': 'GeologicStabilizer',
                'display_name': 'Geologic Stabilizer',
                'resource_type': None,
                'damage_type': None,
                'kind': 'multiplier',
                'providers': [
                    {'source_kind': 'facility', 'source_id': 'f:1', 'is_active': True,
                     'status': 'Active', 'value': 1.0, 'ability_data': {}},
                ],
            },
        }
        status_per_group = {'GeologicStabilizer': 'Active'}
        value_per_group = {'GeologicStabilizer': 1.0}

        rows = _format_rows(raw_providers, status_per_group, value_per_group)

        assert len(rows) == 1
        row = rows[0]
        # Public return shape pinned by the docstring contract.
        for key in ('ability_name', 'display_name', 'group_key', 'status',
                    'resource_type', 'damage_type', 'kind', 'aggregate_value',
                    'providers'):
            assert key in row
        assert row['group_key'] == 'GeologicStabilizer'
        assert row['status'] == 'Active'
        assert row['aggregate_value'] == 1.0
        assert row['kind'] == 'multiplier'
        assert row['providers'] is raw_providers['GeologicStabilizer']['providers']

    def test_format_rows_empty_input_returns_empty_list(self):
        assert _format_rows({}, {}, {}) == []
