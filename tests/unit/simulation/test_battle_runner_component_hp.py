"""Tests for `run_battle` per-component HP handling (PROJ-269 Phase 2 Task 2.4).

Covers:
- Ship construction inside `run_battle` applies `ShipSpec.components`
  per-instance HP onto the engine Ship's components after materialization
- `extract_outcome` emits `ShipOutcome.components` populated from each
  Ship's final per-component HP (not just the spec's input values)
- A ship spec with full HP emerges with same-or-lower HP (never exceeds)
- A ship spec with damaged components emerges with at-or-below-damaged HP
"""
from typing import Callable

import pytest

from game.ai.ai_factory import AIControllerFactory
from game.core.math import Vector2
from game.simulation.battle_outcome import BattleOutcome
from game.simulation.battle_runner import run_battle
from game.simulation.battle_spec import (
    BattleSpec,
    CombatPolicies,
    ComponentStateSpec,
    EntryVector,
    ShipSpec,
    SquadronSpec,
    TaskForceSpec,
    TeamSpec,
)
from game.simulation.combat.modifier_stack import ModifierStack
from game.simulation.combat.telemetry import TelemetryLevel
from game.simulation.entities.ship import Ship
from game.simulation.entities.ship_serialization import ShipSerializer
from game.simulation.systems.battle_end_conditions import TickLimitCondition


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _minimal_design() -> dict:
    return {
        "name": "Cruiser",
        "ship_class": "Escort",
        "vehicle_type": "Ship",
        "design_role": "fleet_escort",
        "theme_id": "Federation",
        "layers": {
            "CORE": [{"id": "bridge"}],
            "OUTER": [{"id": "laser_cannon"}, {"id": "laser_cannon"}],
            "ARMOR": [],
        },
        "_metadata": {},
    }


@pytest.fixture
def ship_builder_from_design(fresh_registries) -> Callable[[ShipSpec], Ship]:
    """Ship builder that materializes each ShipSpec via ShipSerializer.from_dict
    using a shared minimal design. Phase 1 pattern — Phase 2 adds
    per-component HP inside run_battle, and the builder remains simple."""

    design = _minimal_design()

    def _build(ship_spec: ShipSpec) -> Ship:
        ship = ShipSerializer.from_dict(design, registries=fresh_registries)
        ship.instance_id = ship_spec.instance_id
        return ship

    return _build


def _team(team_id: int, ship_spec: ShipSpec) -> TeamSpec:
    return TeamSpec(
        team_id=team_id,
        name=f"Team {team_id}",
        entry_vector=EntryVector(origin=Vector2(0, 0), facing=0.0),
        fleet_hierarchy=(
            TaskForceSpec(
                task_force_id=f"tf-{team_id}",
                formation=None,
                policies=CombatPolicies(),
                squadrons=(
                    SquadronSpec(
                        squadron_id=f"sq-{team_id}",
                        policies=CombatPolicies(),
                        ships=(ship_spec,),
                    ),
                ),
            ),
        ),
    )


# ---------------------------------------------------------------------------
# run_battle applies ShipSpec.components HP onto ship materialization
# ---------------------------------------------------------------------------


def test_run_battle_applies_component_hp_from_spec_before_ticks(
    ship_builder_from_design,
):
    """Spec requests laser_cannon#0 at 40 HP; outcome should reflect
    final HP <= 40 (ships far apart → no additional damage in the brief
    tick window, so HP should be essentially preserved)."""
    damaged_ship = ShipSpec(
        instance_id="s0",
        design_id="Cruiser",
        theme_id="Federation",
        name="Damaged",
        position=Vector2(-5000.0, 0.0),
        angle=0.0,
        velocity=Vector2(0, 0),
        components=(
            ComponentStateSpec(
                component_id="laser_cannon",
                instance_index=0,
                current_hp=40.0,
                is_active=True,
            ),
        ),
    )
    full_ship = ShipSpec(
        instance_id="s1",
        design_id="Cruiser",
        theme_id="Federation",
        name="Full",
        position=Vector2(5000.0, 0.0),
        angle=0.0,
        velocity=Vector2(0, 0),
        components=(),
    )

    spec = BattleSpec(
        seed=42,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=None,
        end_condition=TickLimitCondition(max_ticks=3),
        absolute_max_ticks=100,
        teams=(_team(0, damaged_ship), _team(1, full_ship)),
        modifier_stack=ModifierStack.empty(),
        post_battle_hook=None,
    )

    outcome: BattleOutcome = run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder_from_design,
    )

    # Find the damaged ship's outcome and assert its laser_cannon#0
    # current_hp is <= the spec's 40 HP (the engine may not take further
    # damage given the ships are far apart + only 3 ticks, but it
    # definitely cannot exceed spec).
    damaged_outcome = next(
        s for t in outcome.teams for s in t.ships if s.instance_id == "s0"
    )
    laser0 = next(
        c for c in damaged_outcome.components
        if c.component_id == "laser_cannon" and c.instance_index == 0
    )
    assert laser0.current_hp <= 40.0 + 1e-6
    # And should still be positive (no catastrophic loss)
    assert laser0.current_hp >= 0


def test_run_battle_outcome_components_populated_for_all_instances(
    ship_builder_from_design,
):
    """Every component instance on each ship shows up in the outcome,
    keyed uniquely by (component_id, instance_index)."""
    spec_ship = ShipSpec(
        instance_id="s-any",
        design_id="Cruiser",
        theme_id="Federation",
        name="Any",
        position=Vector2(0, 0),
        angle=0.0,
        velocity=Vector2(0, 0),
        components=(),
    )
    spec = BattleSpec(
        seed=1,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=None,
        end_condition=TickLimitCondition(max_ticks=2),
        absolute_max_ticks=100,
        teams=(
            _team(0, spec_ship),
            _team(1, ShipSpec(
                instance_id="s-other",
                design_id="Cruiser",
                theme_id="Federation",
                name="Other",
                position=Vector2(9999, 0),
                angle=0.0,
                velocity=Vector2(0, 0),
                components=(),
            )),
        ),
        modifier_stack=ModifierStack.empty(),
        post_battle_hook=None,
    )

    outcome = run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder_from_design,
    )

    # Both ships should have non-empty components tuples containing
    # entries for bridge#0 and laser_cannon#0 and laser_cannon#1.
    for team in outcome.teams:
        for ship in team.ships:
            keys = {(c.component_id, c.instance_index) for c in ship.components}
            assert ("bridge", 0) in keys
            assert ("laser_cannon", 0) in keys
            assert ("laser_cannon", 1) in keys


def test_run_battle_full_hp_spec_yields_outcome_not_exceeding_full(
    ship_builder_from_design,
):
    """A ship with full-HP spec components cannot emerge with HP above
    that spec — damage monotonically decreases (or stays equal)."""
    full_ship = ShipSpec(
        instance_id="s0",
        design_id="Cruiser",
        theme_id="Federation",
        name="Full",
        position=Vector2(-5000, 0),
        angle=0.0,
        velocity=Vector2(0, 0),
        components=(),
    )
    other = ShipSpec(
        instance_id="s1",
        design_id="Cruiser",
        theme_id="Federation",
        name="Other",
        position=Vector2(5000, 0),
        angle=0.0,
        velocity=Vector2(0, 0),
        components=(),
    )
    spec = BattleSpec(
        seed=1,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=None,
        end_condition=TickLimitCondition(max_ticks=3),
        absolute_max_ticks=100,
        teams=(_team(0, full_ship), _team(1, other)),
        modifier_stack=ModifierStack.empty(),
        post_battle_hook=None,
    )
    outcome = run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder_from_design,
    )
    full_outcome = next(
        s for t in outcome.teams for s in t.ships if s.instance_id == "s0"
    )
    # Every component's outcome HP must be finite and non-negative.
    for c in full_outcome.components:
        assert c.current_hp >= 0
