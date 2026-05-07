"""PROJ-366 Phase 0 — replay_ship_builder registry-provider contract repair.

Codex review (20260505T150757Z PROJ-366 plan-review, r001) identified that
`game/strategy/services/replay_ship_builder.py:58` calls
`registry_provider.get_registries()`, but the `IRegistryProvider` protocol
(`game/core/protocols/registry.py:23-39`) only exposes individual getters
(`get_components`, `get_modifiers`, `get_vehicle_classes`, `get_resources`).
There is even a regression guard at `tests/integration/test_app_integration.py:158-170`
enforcing that `DefaultRegistryProvider` must NOT grow `get_registries`.

This test pins the protocol-contract usage by passing a real
`DefaultRegistryProvider` (production) into `build_replay_ship_builder`
and asserting the function does not raise `AttributeError`.

Reference fix pattern: `build_context_ship_builder` at
`game/simulation/battle_runner.py:240-247` constructs `GameRegistries` from
the protocol's individual getters.
"""
from __future__ import annotations

import pytest

from game.core.registry import DefaultRegistryProvider
from game.simulation.replay import REPLAY_SCHEMA_VERSION, ReplayOutcome, ReplayRecord, ReplaySpec
from game.strategy.services.replay_ship_builder import build_replay_ship_builder


def _make_record() -> ReplayRecord:
    """Build a minimal ReplayRecord for the contract test.

    Uses the same pattern as
    `tests/unit/strategy/services/test_replay_verification_coordinator.py::_make_record`.
    """
    from tests.unit.simulation.replay.test_serialization import (
        _make_minimal_battle_spec,
        _make_minimal_outcome,
    )
    spec = _make_minimal_battle_spec()
    outcome = _make_minimal_outcome()
    return ReplayRecord(
        schema_version=REPLAY_SCHEMA_VERSION,
        replay_id="contract-1",
        captured_at="2026-05-05T00:00:00Z",
        sector_name="test",
        sector_coords=(0, 0),
        turn_number=1,
        participating_empires=("A", "B"),
        components_registry_hash="sha256:t",
        spec=ReplaySpec.from_battle_spec(spec),
        outcome=ReplayOutcome.from_battle_outcome(outcome),
    )


def test_build_replay_ship_builder_uses_protocol_getters_only() -> None:
    """`build_replay_ship_builder` must construct via protocol getters,
    not via a non-existent `get_registries()` method.

    Pre-fix this raises ``AttributeError: 'DefaultRegistryProvider' object
    has no attribute 'get_registries'``. Post-fix the call returns a
    builder closure without raising.
    """
    record = _make_record()
    provider = DefaultRegistryProvider()

    # The bug: this raises AttributeError on the broken implementation.
    builder = build_replay_ship_builder(record, registry_provider=provider)

    assert callable(builder)


def _first_ship_spec(record: ReplayRecord):
    spec = record.spec.to_battle_spec()
    return spec.teams[0].fleet_hierarchy[0].squadrons[0].ships[0]


def test_builder_uses_fallback_when_snapshot_is_missing() -> None:
    record = _make_record()
    provider = DefaultRegistryProvider()
    ship_spec = _first_ship_spec(record)
    calls = []
    sentinel_ship = object()

    def fallback_builder(passed_spec, team_id):
        calls.append((passed_spec, team_id))
        return sentinel_ship

    builder = build_replay_ship_builder(
        record,
        registry_provider=provider,
        fallback_builder=fallback_builder,
    )

    assert builder(ship_spec, 3) is sentinel_ship
    assert calls == [(ship_spec, 3)]


def test_builder_raises_when_snapshot_and_fallback_are_missing() -> None:
    record = _make_record()
    provider = DefaultRegistryProvider()
    ship_spec = _first_ship_spec(record)
    builder = build_replay_ship_builder(record, registry_provider=provider)

    with pytest.raises(ValueError, match="no instance snapshot"):
        builder(ship_spec, 0)
