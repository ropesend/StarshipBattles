"""
PROJ-343 T1.3 — Failing API test: env-hazard tick must pass the querying
empire's id so owned facility hazards don't leak across teams.

Bug shape (verified by planning instance 2026-05-04):
- `environmental_hazard_engine.py:111-113` calls
  `collect_sector_effects(..., empire_id=None)`.
- `system_effects_collector.py:298` skips owned-source filtering when
  `empire_id is None` — owned sources contribute to ALL queries.
- Result: a colony's defensive EnvironmentalDamage facility damages enemy
  fleets too.
- Same shape at `conflict_resolution_engine.py:509-511` per Codex.

Fix shape (PROJ-343 Phase 5): pass the querying fleet's `owner_id` as
`empire_id` at both call sites. Then the collector's gate
`if owner_id is not None and empire_id is not None and owner_id != empire_id`
correctly filters owned hazards out of cross-team queries.

Currently FAILS: env-hazard engine calls `collect_sector_effects` with
`empire_id=None`, NOT the fleet's owner_id. After fix: it passes
`fleet.owner_id`.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from game.strategy.engine.environmental_hazard_engine import (
    EnvironmentalHazardEngine,
)


def test_env_hazard_tick_passes_querying_fleet_owner_id_to_collect_sector_effects():
    """Pin: env-hazard `_process_tick` (or whatever entry point) passes the
    fleet's owner_id as `empire_id` to `collect_sector_effects`, so the
    collector's owner filter correctly excludes other empires' owned hazards.

    Currently FAILS: every call uses `empire_id=None` (see env_hazard_engine.py:113).
    """
    # Fleet owned by empire 7.
    fleet = MagicMock()
    fleet.id = 1
    fleet.owner_id = 7
    fleet.location = (4, 4)

    empire = MagicMock()
    empire.id = 7
    empire.fleets = [fleet]

    galaxy = MagicMock()
    fake_system = MagicMock()
    galaxy.get_system_at_location = MagicMock(return_value=fake_system)

    engine = EnvironmentalHazardEngine()

    # Patch at the source module — env_hazard imports `collect_sector_effects`
    # function-locally inside the tick method, so the consumer-side patch
    # target doesn't exist.
    with patch(
        'game.strategy.services.system_effects_collector.collect_sector_effects',
        return_value=[],
    ) as mock_collect:
        engine.process_environmental_tick(tick=1, empires=[empire], galaxy=galaxy)

    # At least one call expected (one fleet, one system).
    assert mock_collect.call_count >= 1, (
        "Expected env-hazard engine to call collect_sector_effects at least once"
    )

    # Every call must pass the querying fleet's owner_id, NOT None.
    # Currently FAILS: all calls use `empire_id=None`.
    for call in mock_collect.call_args_list:
        passed_empire_id = call.kwargs.get('empire_id', 'KW_NOT_PRESENT')
        # Fall back to positional if the implementation passed positionally.
        if passed_empire_id == 'KW_NOT_PRESENT':
            # Signature: collect_sector_effects(system, hex, empire_id=, registries=)
            # Positional in some call shapes; safest: assert kwargs explicitly used.
            passed_empire_id = None
        assert passed_empire_id == fleet.owner_id, (
            f"env-hazard tick must pass querying empire_id={fleet.owner_id}, "
            f"got empire_id={passed_empire_id!r} (full call: {call!r})"
        )
