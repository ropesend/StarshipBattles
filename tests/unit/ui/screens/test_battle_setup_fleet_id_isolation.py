"""PROJ-471 Task 2.8 -- _next_fleet_id is per-state instance, not module global.

Pins that fleet-id generation no longer relies on an unbounded module-level
counter that leaks across states/tests, while still producing unique ids within
a single BattleSetupState (across both sides).
"""

from game.ui.screens import battle_setup_state as bss
from game.ui.screens.battle_setup_state import BattleSetupState, BattleSetupSide


def test_no_module_level_fleet_id_counter():
    assert not hasattr(bss, "_next_fleet_id")


def test_fresh_state_starts_id_sequence_independently():
    state_a = BattleSetupState(side_count=2)
    state_b = BattleSetupState(side_count=2)

    a_ids = [state_a.get_side(0).create_fleet().id for _ in range(3)]
    b_ids = [state_b.get_side(0).create_fleet().id for _ in range(3)]

    # Two independent states produce the SAME starting sequence -> the counter
    # is per-state, not a shared process-global that keeps climbing.
    assert a_ids == b_ids


def test_ids_unique_across_sides_within_one_state():
    state = BattleSetupState(side_count=2)
    ids = []
    for _ in range(3):
        ids.append(state.get_side(0).create_fleet().id)
        ids.append(state.get_side(1).create_fleet().id)
    assert len(set(ids)) == len(ids)


def test_standalone_side_create_fleet_still_works():
    side = BattleSetupSide(team_id=0)
    f1 = side.create_fleet()
    f2 = side.create_fleet()
    assert f1.id != f2.id


def test_create_fleet_after_load_does_not_collide_with_loaded_ids():
    """PROJ-471 Task 4.1 (Codex finding 1): post-load create_fleet must not
    reuse a fleet id that already exists in the loaded state."""
    state = BattleSetupState(side_count=2)
    state.get_side(0).create_fleet()
    state.get_side(1).create_fleet()

    loaded = BattleSetupState.from_dict(state.to_dict())
    existing = {f.id for sd in loaded.sides for f in sd.fleets}

    new_fleet = loaded.get_side(0).create_fleet()
    assert new_fleet.id not in existing
