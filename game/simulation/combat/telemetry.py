"""TelemetryLevel — graduated event-bus subscription level.

Introduced by PROJ-269 Phase 1 Task 1.5. Phase 1 ships the enum only; the
opt-in `CombatEventBus` subscribers (`WeaponSummaryAggregator`,
`ShipStatsAggregator`, `HitLogRecorder`) land in Phase 5.

Levels (integer-ordered so callers can write `level >= NORMAL`):
  - MINIMAL (1)  — nothing attached; smallest overhead for batch runs.
  - NORMAL  (2)  — weapon summary + ship-stat aggregators attached.
  - DETAILED (3) — above, plus full hit-log recorder for forensic UI.

Defaults per context (set by each spec compiler):
  - Strategy    — NORMAL
  - Battle Setup — NORMAL
  - Combat Lab  — DETAILED (individual scenarios can override).
"""
from enum import IntEnum


class TelemetryLevel(IntEnum):
    """How much detail to capture into BattleOutcome.

    `IntEnum` so the engine can branch on `level >= NORMAL` without
    introducing a custom ordering helper.
    """

    MINIMAL = 1
    NORMAL = 2
    DETAILED = 3


__all__ = ["TelemetryLevel"]
