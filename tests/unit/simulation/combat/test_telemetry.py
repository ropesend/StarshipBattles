"""Tests for TelemetryLevel (PROJ-269 Phase 1 Task 1.5).

Phase 1 ships the enum only. Opt-in `CombatEventBus` subscribers
(`WeaponSummaryAggregator`, `ShipStatsAggregator`, `HitLogRecorder`)
and per-level performance measurement land in Phase 5.

Covers:
- `TelemetryLevel` is an `IntEnum` (ordered) with MINIMAL / NORMAL / DETAILED
- Ordering: MINIMAL < NORMAL < DETAILED
- Can compare against each other with `<`, `>`, `<=`, `>=`
"""
from enum import IntEnum

import pytest

from game.simulation.combat.telemetry import TelemetryLevel


def test_telemetry_level_is_enum_with_required_members():
    assert issubclass(TelemetryLevel, IntEnum)
    names = {m.name for m in TelemetryLevel}
    assert {"MINIMAL", "NORMAL", "DETAILED"}.issubset(names)


def test_telemetry_level_ordering():
    # Design intent (design.md §2.9) — NORMAL > MINIMAL, DETAILED > NORMAL.
    assert TelemetryLevel.NORMAL > TelemetryLevel.MINIMAL
    assert TelemetryLevel.DETAILED > TelemetryLevel.NORMAL
    assert TelemetryLevel.MINIMAL < TelemetryLevel.NORMAL
    assert TelemetryLevel.NORMAL < TelemetryLevel.DETAILED


def test_telemetry_level_supports_ge_le():
    # Useful for engine branch like `if spec.telemetry_level >= NORMAL: ...`
    assert TelemetryLevel.NORMAL >= TelemetryLevel.NORMAL
    assert TelemetryLevel.DETAILED >= TelemetryLevel.NORMAL
    assert TelemetryLevel.MINIMAL <= TelemetryLevel.DETAILED


def test_telemetry_level_integer_values_are_sequential():
    # design.md §2.9: MINIMAL=1, NORMAL=2, DETAILED=3.
    assert int(TelemetryLevel.MINIMAL) == 1
    assert int(TelemetryLevel.NORMAL) == 2
    assert int(TelemetryLevel.DETAILED) == 3
