"""Speed-recalc invariant audit (PROJ-320 Phase 2).

The PROJ-320 round-budget model depends on `Fleet.speed` always reflecting
the slowest currently-equipped ship. Every code path that mutates
`Fleet.ships` must therefore either (a) go through `Fleet.add_ship` /
`Fleet.remove_ship` / `Fleet.merge_with` (which trigger recalc) or
(b) call `trigger_speed_recalculation()` itself.

The Phase 2 audit (Task 2.1) found 5 mutation sites in
`game/strategy/data/fleet.py`:
  * Line 157 (Fleet.add_ship)         → trigger_speed_recalculation at 158
  * Line 163 (Fleet.remove_ship)      → trigger_speed_recalculation at 164
  * Line 451 (Fleet.merge_with)       → trigger_speed_recalculation at 459
                                        (target fleet — guarded by
                                        test_order_processor_fleet_merge.py)
  * Line 452 (Fleet.merge_with)       → source fleet cleared, then removed
                                        from empire entirely; speed irrelevant
  * Line 541 (Fleet.from_dict)        → restores saved `speed` field; no
                                        recalc by design (see test below)

External callers (`post_battle_hook.py`, `order_processor.py`, etc.) all
go through Fleet methods. No suspect sites surfaced outside fleet.py.

This file pins the from_dict design choice so a future agent doesn't
reintroduce the recalc and break round-trip tests (we tried — see
decisions.md row dated 2026-05-02 about the 19-test regression).
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from game.strategy.data.fleet import Fleet


def test_from_dict_preserves_saved_speed_without_recalcing():
    """`Fleet.from_dict` must NOT call trigger_speed_recalculation.

    Round-trip tests rely on the saved `speed` field being preserved
    verbatim. Test fixtures don't supply ships with valid
    `get_calculated_stats()`, so a recalc would zero out the speed and
    break ~19 existing save/load tests.

    The saved speed IS the slowest-ship speed at save time; defensive
    recalc on load is unnecessary in normal play. If a future bug
    surfaces from a save-format mismatch, fix at the save-format layer,
    not by recalculating on every load.

    PROJ-320 Phase 2: audit pins this design choice.
    """
    save_data = {
        "id": 99,
        "owner_id": 0,
        "location": {"q": 0, "r": 0},
        "speed": 7.5,
        "display_name": "",
        "ships": [],
        "task_forces": [],
        "path": [],
        "orders": [],
        "construction_queue": [],
    }

    with patch.object(Fleet, "trigger_speed_recalculation") as mock_recalc:
        fleet = Fleet.from_dict(save_data, registries=MagicMock())

    mock_recalc.assert_not_called(), (
        "Fleet.from_dict must NOT recalc speed on load — the saved speed "
        "is authoritative and recalcing breaks round-trip tests when the "
        "loaded ships lack valid get_calculated_stats(). See "
        "decisions.md row dated 2026-05-02 for the audit history."
    )
    # Confirm the saved speed survived the load.
    assert fleet.speed == 7.5
