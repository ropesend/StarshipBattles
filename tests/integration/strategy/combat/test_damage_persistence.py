"""End-to-end Phase 2 acceptance test: damage persists across battles.

Creates two fleets, runs two consecutive battles using the unified
`build_strategy_battle_spec → run_battle → PostBattleHook` pipeline,
and verifies that component damage accumulates across them (it does
NOT reset between battles).

This is the acceptance criterion for PROJ-269 Phase 2. If this test
fails, something in the ShipInstance.components ↔ BattleSpec.components
↔ run_battle ↔ BattleOutcome.components ↔ apply_outcome_to_fleets
chain is broken.
"""
import pytest

from game.ai.ai_factory import AIControllerFactory
from game.core.hex_math import HexCoord
from game.core.math import Vector2
from game.simulation.battle_outcome import ShipStatus
from game.simulation.battle_runner import run_battle
from game.strategy.combat.spec_compiler import build_strategy_battle_spec
from game.strategy.data.component_state import ComponentState, component_state_key
from game.strategy.data.fleet import Fleet


def _design() -> dict:
    return {
        "name": "Cruiser",
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
def fleets(session_registries, ship_factory):
    fa = Fleet(fleet_id=10, owner_id=0, location=HexCoord(0, 0))
    fa.add_ship(ship_factory(_design(), owner_id=0))

    fb = Fleet(fleet_id=20, owner_id=1, location=HexCoord(0, 0))
    fb.add_ship(ship_factory(_design(), owner_id=1))

    return fa, fb


def _make_ship_builder(fresh_registries):
    """Build a ship_builder that materializes each spec via its fleets'
    ShipInstance (reads design_data from registries-injected instance)."""
    from game.simulation.entities.ship_serialization import ShipSerializer

    # Cache ship_instance by instance_id so builder can use the correct
    # `to_ship` with per-component HP.
    def _build(ship_spec):
        # Recreate via a raw design — the strategy compiler already
        # wrote per-component HP into `ShipSpec.components`, which
        # `run_battle` applies after the builder returns. So the builder
        # just materializes the base ship from design data.
        ship = ShipSerializer.from_dict(_design(), registries=fresh_registries)
        ship.instance_id = ship_spec.instance_id
        return ship

    return _build


def test_damage_persists_across_two_strategy_battles(
    fleets, session_registries, fresh_registries
):
    fleet_a, fleet_b = fleets
    ship_a = fleet_a.ships[0]
    bridge_key = component_state_key("bridge", 0)
    laser_key = component_state_key("laser_cannon", 0)

    # Sanity: both components start at their design-defined HP.
    initial_bridge_hp = ship_a.components[bridge_key].current_hp
    initial_laser_hp = ship_a.components[laser_key].current_hp
    assert initial_bridge_hp > 0
    assert initial_laser_hp > 0

    # --- Battle 1 ---
    # Manually pre-damage ship_a's laser before the first battle to
    # simulate damage that should persist and accumulate.
    pre_damage_hp = initial_laser_hp * 0.6
    ship_a.components[laser_key] = ComponentState(
        component_id="laser_cannon",
        instance_index=0,
        current_hp=pre_damage_hp,
        is_active=True,
    )

    spec1 = build_strategy_battle_spec(
        [fleet_a, fleet_b],
        sector=None,
        system=None,
        empires={},
        settings=None,
        registries=session_registries,
        seed=42,
    )

    # ShipSpec from compiler must carry ship_a's pre-damaged laser.
    ship_spec_a = spec1.teams[0].fleet_hierarchy[0].squadrons[0].ships[0]
    laser_spec = next(
        c for c in ship_spec_a.components
        if c.component_id == "laser_cannon" and c.instance_index == 0
    )
    assert laser_spec.current_hp == pytest.approx(pre_damage_hp, abs=0.5)

    outcome1 = run_battle(
        spec1,
        ai_factory=AIControllerFactory(),
        ship_builder=_make_ship_builder(fresh_registries),
    )

    # After battle 1: hook should have written outcome back to ship_a.
    # laser HP must still be <= pre_damage_hp (can only decrease or stay).
    post_battle1_laser_hp = ship_a.components[laser_key].current_hp
    assert post_battle1_laser_hp <= pre_damage_hp + 1e-6, (
        f"Battle 1 shouldn't have increased HP: "
        f"before={pre_damage_hp}, after={post_battle1_laser_hp}"
    )

    # --- Battle 2 ---
    # Using the SAME fleets. The second compiled spec must carry the
    # damage from battle 1.
    spec2 = build_strategy_battle_spec(
        [fleet_a, fleet_b],
        sector=None,
        system=None,
        empires={},
        settings=None,
        registries=session_registries,
        seed=42,
    )

    ship_spec_a_2 = spec2.teams[0].fleet_hierarchy[0].squadrons[0].ships[0]
    laser_spec_2 = next(
        c for c in ship_spec_a_2.components
        if c.component_id == "laser_cannon" and c.instance_index == 0
    )
    assert laser_spec_2.current_hp == pytest.approx(
        post_battle1_laser_hp, abs=0.5
    ), (
        "Spec for battle 2 must reflect damage persisted from battle 1 "
        f"(after battle 1: {post_battle1_laser_hp}, spec says: "
        f"{laser_spec_2.current_hp})"
    )

    outcome2 = run_battle(
        spec2,
        ai_factory=AIControllerFactory(),
        ship_builder=_make_ship_builder(fresh_registries),
    )

    post_battle2_laser_hp = ship_a.components[laser_key].current_hp
    # Laser HP monotonically decreases across both battles (or stays
    # equal if the ship was never engaged in either).
    assert post_battle2_laser_hp <= post_battle1_laser_hp + 1e-6, (
        f"Battle 2 shouldn't have increased HP: "
        f"before={post_battle1_laser_hp}, after={post_battle2_laser_hp}"
    )

    # Outcomes must reference the same ship_a by instance_id.
    for outcome in (outcome1, outcome2):
        ship_ids = {
            s.instance_id
            for team in outcome.teams
            for s in team.ships
        }
        assert ship_a.instance_id in ship_ids
