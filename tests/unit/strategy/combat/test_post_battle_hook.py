"""Tests for `apply_outcome_to_fleets` (PROJ-269 Phase 2 Task 2.5).

The strategy PostBattleHook writes battle outcome state back to the
ShipInstance / Fleet / Empire graph:
  - Surviving / derelict ships: update per-component HP + status flags
  - Destroyed ships: remove from parent fleet
  - Retreated ships: remove from parent fleet (MVP — see decisions.md)
  - Empty fleets pruned from their owning empire
"""
from typing import Dict, List

import pytest

from game.core.hex_math import HexCoord
from game.core.math import Vector2
from game.simulation.battle_outcome import (
    BattleOutcome,
    EndReason,
    ShipOutcome,
    ShipStats,
    ShipStatus,
    TeamOutcome,
    WeaponSummary,
)
from game.simulation.battle_spec import ComponentStateSpec
from game.strategy.combat.post_battle_hook import apply_outcome_to_fleets
from game.strategy.data.component_state import ComponentState, component_state_key
from game.strategy.data.fleet import Fleet


# ---------------------------------------------------------------------------
# Fixtures — a pair of single-ship fleets, with a helper to craft a
# matching ShipOutcome by instance_id and status.
# ---------------------------------------------------------------------------


def _design() -> dict:
    return {
        "name": "TestShip",
        "ship_class": "Escort",
        "vehicle_type": "Ship",
        "design_role": "fleet_escort",
        "theme_id": "Federation",
        "layers": {
            "CORE": [{"id": "bridge"}],
            "OUTER": [{"id": "laser_cannon"}],
            "ARMOR": [],
        },
        "_metadata": {},
    }


@pytest.fixture
def two_fleets(session_registries, ship_factory):
    fleet_a = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
    fleet_a.add_ship(ship_factory(_design(), owner_id=0))
    fleet_a.add_ship(ship_factory(_design(), owner_id=0))

    fleet_b = Fleet(fleet_id=2, owner_id=1, location=HexCoord(0, 0))
    fleet_b.add_ship(ship_factory(_design(), owner_id=1))
    return fleet_a, fleet_b


def _make_ship_outcome(
    *, instance_id: str, status: ShipStatus, bridge_hp: float = 100.0
) -> ShipOutcome:
    return ShipOutcome(
        instance_id=instance_id,
        status=status,
        final_position=Vector2(0, 0),
        final_angle=0.0,
        final_velocity=Vector2(0, 0),
        components=(
            ComponentStateSpec(
                component_id="bridge",
                instance_index=0,
                current_hp=bridge_hp,
                is_active=True,
            ),
            ComponentStateSpec(
                component_id="laser_cannon",
                instance_index=0,
                current_hp=10.0,
                is_active=True,
            ),
        ),
        weapons=(),
        hits_taken=(),
        stats=ShipStats(
            total_damage_taken=0.0,
            peak_speed=0.0,
            ticks_derelict=0,
            ticks_alive=0,
        ),
    )


def _make_outcome(
    team_ship_outcomes: Dict[int, List[ShipOutcome]],
) -> BattleOutcome:
    teams = tuple(
        TeamOutcome(
            team_id=tid,
            name=f"Team {tid}",
            ships=tuple(ships),
        )
        for tid, ships in team_ship_outcomes.items()
    )
    return BattleOutcome(
        end_reason=EndReason.TEAM_ELIMINATED,
        duration_ticks=100,
        seed=1,
        teams=teams,
        telemetry_level="NORMAL",
    )


# ---------------------------------------------------------------------------
# Surviving ship → components updated
# ---------------------------------------------------------------------------


def test_surviving_ship_gets_components_updated(two_fleets):
    fleet_a, fleet_b = two_fleets
    survivor = fleet_a.ships[0]
    # Pre-condition: ship was at full HP.
    bridge_key = component_state_key("bridge", 0)
    pre_hp = survivor.components[bridge_key].current_hp
    assert pre_hp > 50.0

    outcome = _make_outcome({
        0: [_make_ship_outcome(
            instance_id=survivor.instance_id,
            status=ShipStatus.SURVIVED,
            bridge_hp=55.0,
        )],
        1: [_make_ship_outcome(
            instance_id=fleet_b.ships[0].instance_id,
            status=ShipStatus.SURVIVED,
        )],
    })

    apply_outcome_to_fleets(
        outcome,
        fleets_by_team_id={0: [fleet_a], 1: [fleet_b]},
    )

    assert survivor.components[bridge_key].current_hp == pytest.approx(55.0, abs=0.5)
    assert survivor.is_alive is True


# ---------------------------------------------------------------------------
# Stats cache must be invalidated after outcome applied
# (PROJ-270 Phase 7.2 — replacement for deleted
# `test_update_from_battle_results_triggers_speed_recalc`)
# ---------------------------------------------------------------------------


def test_apply_outcome_to_fleets_invalidates_stats_cache(two_fleets):
    """After outcome apply, the ship's `_cached_stats` is cleared so
    downstream stat-read code (including strategic_movement / speed)
    triggers a fresh recalculation rather than returning stale pre-battle
    values."""
    fleet_a, fleet_b = two_fleets
    survivor = fleet_a.ships[0]

    # Warm the cache — mimics pre-battle stat queries populating it.
    survivor._cached_stats = {"strategic_movement": 999, "warmed": True}
    assert survivor._cached_stats is not None

    outcome = _make_outcome({
        0: [_make_ship_outcome(
            instance_id=survivor.instance_id,
            status=ShipStatus.SURVIVED,
            bridge_hp=55.0,
        )],
        1: [_make_ship_outcome(
            instance_id=fleet_b.ships[0].instance_id,
            status=ShipStatus.SURVIVED,
        )],
    })

    apply_outcome_to_fleets(
        outcome,
        fleets_by_team_id={0: [fleet_a], 1: [fleet_b]},
    )

    # Cache must have been invalidated so subsequent stat reads
    # recalculate from the post-battle components.
    assert survivor._cached_stats is None, (
        "apply_outcome_to_fleets must invalidate ShipInstance._cached_stats "
        "so strategic_movement / speed read post-battle component HP."
    )


# ---------------------------------------------------------------------------
# Destroyed ship → removed from fleet
# ---------------------------------------------------------------------------


def test_destroyed_ship_removed_from_fleet(two_fleets):
    fleet_a, fleet_b = two_fleets
    victim = fleet_a.ships[0]
    survivor = fleet_a.ships[1]
    victim_id = victim.instance_id

    outcome = _make_outcome({
        0: [
            _make_ship_outcome(
                instance_id=victim.instance_id, status=ShipStatus.DESTROYED
            ),
            _make_ship_outcome(
                instance_id=survivor.instance_id, status=ShipStatus.SURVIVED
            ),
        ],
        1: [_make_ship_outcome(
            instance_id=fleet_b.ships[0].instance_id,
            status=ShipStatus.SURVIVED,
        )],
    })

    apply_outcome_to_fleets(
        outcome,
        fleets_by_team_id={0: [fleet_a], 1: [fleet_b]},
    )

    remaining_ids = {s.instance_id for s in fleet_a.ships}
    assert victim_id not in remaining_ids
    assert survivor.instance_id in remaining_ids


# ---------------------------------------------------------------------------
# Retreated ship → removed from fleet (MVP per Phase 2 decision)
# ---------------------------------------------------------------------------


def test_retreated_ship_removed_from_fleet(two_fleets):
    fleet_a, fleet_b = two_fleets
    retreater = fleet_a.ships[0]
    survivor = fleet_a.ships[1]

    outcome = _make_outcome({
        0: [
            _make_ship_outcome(
                instance_id=retreater.instance_id, status=ShipStatus.RETREATED
            ),
            _make_ship_outcome(
                instance_id=survivor.instance_id, status=ShipStatus.SURVIVED
            ),
        ],
        1: [_make_ship_outcome(
            instance_id=fleet_b.ships[0].instance_id,
            status=ShipStatus.SURVIVED,
        )],
    })
    apply_outcome_to_fleets(
        outcome,
        fleets_by_team_id={0: [fleet_a], 1: [fleet_b]},
    )

    remaining_ids = {s.instance_id for s in fleet_a.ships}
    assert retreater.instance_id not in remaining_ids


# ---------------------------------------------------------------------------
# Empty fleet pruned from empire when empires provided
# ---------------------------------------------------------------------------


def test_empty_fleet_removed_from_empire_when_provided(two_fleets):
    fleet_a, fleet_b = two_fleets
    # Destroy every ship on fleet_a.
    outcomes_team0 = [
        _make_ship_outcome(instance_id=s.instance_id, status=ShipStatus.DESTROYED)
        for s in list(fleet_a.ships)
    ]

    class _FakeEmpire:
        def __init__(self):
            self.fleets = [fleet_a, fleet_b]

    empire = _FakeEmpire()

    outcome = _make_outcome({
        0: outcomes_team0,
        1: [_make_ship_outcome(
            instance_id=fleet_b.ships[0].instance_id,
            status=ShipStatus.SURVIVED,
        )],
    })
    apply_outcome_to_fleets(
        outcome,
        fleets_by_team_id={0: [fleet_a], 1: [fleet_b]},
        empires={0: empire, 1: empire},
    )

    assert fleet_a not in empire.fleets
    assert fleet_b in empire.fleets


def test_missing_empires_param_does_not_crash(two_fleets):
    """`empires` defaults to None; hook must not crash when pruning
    empty fleets without an empire reference."""
    fleet_a, fleet_b = two_fleets
    outcomes_team0 = [
        _make_ship_outcome(instance_id=s.instance_id, status=ShipStatus.DESTROYED)
        for s in list(fleet_a.ships)
    ]
    outcome = _make_outcome({
        0: outcomes_team0,
        1: [_make_ship_outcome(
            instance_id=fleet_b.ships[0].instance_id,
            status=ShipStatus.SURVIVED,
        )],
    })
    # Should complete without error.
    apply_outcome_to_fleets(
        outcome,
        fleets_by_team_id={0: [fleet_a], 1: [fleet_b]},
    )
    assert fleet_a.ships == []


# ---------------------------------------------------------------------------
# build_strategy_battle_spec attaches a live hook (not the Phase-1 no-op)
# ---------------------------------------------------------------------------


def test_strategy_spec_post_battle_hook_applies_outcome(
    two_fleets, session_registries
):
    """`build_strategy_battle_spec` returns a spec whose `post_battle_hook`
    closes over the caller's fleets dict and actually applies outcome
    updates when invoked."""
    from game.strategy.combat.spec_compiler import build_strategy_battle_spec

    fleet_a, fleet_b = two_fleets
    spec = build_strategy_battle_spec(
        [fleet_a, fleet_b],
        empires={},
        settings=None,
        registries=session_registries,
    )
    assert callable(spec.post_battle_hook)

    outcome = _make_outcome({
        0: [
            _make_ship_outcome(
                instance_id=fleet_a.ships[0].instance_id,
                status=ShipStatus.SURVIVED,
                bridge_hp=42.0,
            ),
            _make_ship_outcome(
                instance_id=fleet_a.ships[1].instance_id,
                status=ShipStatus.SURVIVED,
            ),
        ],
        1: [_make_ship_outcome(
            instance_id=fleet_b.ships[0].instance_id,
            status=ShipStatus.SURVIVED,
        )],
    })

    # Invoke hook — should apply outcome updates.
    spec.post_battle_hook(outcome)

    bridge_key = component_state_key("bridge", 0)
    assert fleet_a.ships[0].components[bridge_key].current_hp == pytest.approx(
        42.0, abs=0.5
    )
