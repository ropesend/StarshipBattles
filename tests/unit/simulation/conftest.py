"""Shared helpers for tests/unit/simulation/.

Hosts BattleSpec construction helpers that were previously duplicated
byte-for-byte in `test_battle_runner.py` and `test_battle_runner_di.py`.

Consolidated in PROJ-322 Task 1.5 (S09-CAT4-003 / HLP-002).
"""
from __future__ import annotations

import pytest

from game.core.math import Vector2
from game.simulation.battle_spec import (
    CombatPolicies,
    EntryVector,
    ShipSpec,
    SquadronSpec,
    TaskForceSpec,
    TeamSpec,
)


def _make_ship_spec(instance_id: str, x: float, y: float) -> ShipSpec:
    return ShipSpec(
        instance_id=instance_id,
        design_id="Escort",
        theme_id="Federation",
        name=instance_id,
        position=Vector2(x, y),
        angle=0.0,
        velocity=Vector2(0.0, 0.0),
        components=(),
    )


def _make_team(team_id: int, ships: tuple) -> TeamSpec:
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
                        ships=ships,
                    ),
                ),
            ),
        ),
    )


@pytest.fixture
def make_ship_spec():
    """Fixture wrapper for the module-level helper, for import-free callers."""
    return _make_ship_spec


@pytest.fixture
def make_team():
    """Fixture wrapper for the module-level helper, for import-free callers."""
    return _make_team
