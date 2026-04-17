"""Tests for ABBattleRunner — the PROJ-277 first-class A/B runner.

These tests drive the design: they describe exactly what the runner
must do (call run_battle twice in order, forward identical plumbing,
package paired results). Written BEFORE implementation per Strict TDD.
Phase 1 expects all tests to FAIL (skeleton raises NotImplementedError);
Phase 2 brings them green.
"""
from __future__ import annotations

import dataclasses
from unittest.mock import MagicMock, patch

import pytest

from combat_lab.scenarios.ab_outcome import ABBattleOutcome
from combat_lab.services.ab_battle_runner import ABBattleRunner
from combat_lab.telemetry import CombatLabTelemetry


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


def _stub_spec(tag: str) -> MagicMock:
    """Make a lightweight stand-in for a BattleSpec; we only need identity."""
    spec = MagicMock()
    spec._tag = tag  # easy identification in assertions
    return spec


def _mock_outcomes():
    """Two distinct BattleOutcome stubs for baseline and variant."""
    baseline = MagicMock(name="baseline_outcome")
    variant = MagicMock(name="variant_outcome")
    return baseline, variant


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestABBattleRunnerRun:
    @patch("combat_lab.services.ab_battle_runner.run_battle")
    def test_run_calls_run_battle_exactly_twice(self, mock_run_battle):
        """run() must invoke run_battle once for baseline, once for variant."""
        baseline_outcome, variant_outcome = _mock_outcomes()
        mock_run_battle.side_effect = [baseline_outcome, variant_outcome]

        runner = ABBattleRunner(ai_factory=MagicMock())
        baseline_spec = _stub_spec("baseline")
        variant_spec = _stub_spec("variant")

        runner.run(baseline_spec, variant_spec)

        assert mock_run_battle.call_count == 2

    @patch("combat_lab.services.ab_battle_runner.run_battle")
    def test_run_order_is_baseline_then_variant(self, mock_run_battle):
        """Baseline must execute first; variant second. Order matters
        because scenarios may set stateful assertions that depend on
        seeing the baseline's observed values before the variant runs."""
        baseline_outcome, variant_outcome = _mock_outcomes()
        mock_run_battle.side_effect = [baseline_outcome, variant_outcome]

        runner = ABBattleRunner(ai_factory=MagicMock())
        baseline_spec = _stub_spec("baseline")
        variant_spec = _stub_spec("variant")

        runner.run(baseline_spec, variant_spec)

        # First call: baseline; second call: variant.
        assert mock_run_battle.call_args_list[0].args[0] is baseline_spec
        assert mock_run_battle.call_args_list[1].args[0] is variant_spec

    @patch("combat_lab.services.ab_battle_runner.run_battle")
    def test_run_returns_ab_battle_outcome_with_paired_results(
        self, mock_run_battle
    ):
        baseline_outcome, variant_outcome = _mock_outcomes()
        mock_run_battle.side_effect = [baseline_outcome, variant_outcome]

        runner = ABBattleRunner(ai_factory=MagicMock())
        ab = runner.run(_stub_spec("b"), _stub_spec("v"))

        assert isinstance(ab, ABBattleOutcome)
        assert ab.baseline_outcome is baseline_outcome
        assert ab.variant_outcome is variant_outcome

    @patch("combat_lab.services.ab_battle_runner.run_battle")
    def test_run_forwards_ai_factory_and_ship_builder_to_both_calls(
        self, mock_run_battle
    ):
        baseline_outcome, variant_outcome = _mock_outcomes()
        mock_run_battle.side_effect = [baseline_outcome, variant_outcome]

        ai_factory = MagicMock(name="ai_factory")
        ship_builder = MagicMock(name="ship_builder")
        runner = ABBattleRunner(
            ai_factory=ai_factory, ship_builder=ship_builder,
        )
        runner.run(_stub_spec("b"), _stub_spec("v"))

        # Both calls receive identical plumbing — roles therefore map
        # equivalently across the two runs, so validators can compare
        # like-for-like without remapping.
        for call in mock_run_battle.call_args_list:
            assert call.kwargs["ai_factory"] is ai_factory
            assert call.kwargs["ship_builder"] is ship_builder

    @patch("combat_lab.services.ab_battle_runner.run_battle")
    def test_run_captures_separate_telemetry_per_run(self, mock_run_battle):
        """Telemetry is captured PER RUN; roles with the same key in
        baseline and variant appear in their respective telemetry
        bundles independently — no role-prefix remapping."""
        baseline_outcome, variant_outcome = _mock_outcomes()
        mock_run_battle.side_effect = [baseline_outcome, variant_outcome]

        runner = ABBattleRunner(ai_factory=MagicMock())
        ab = runner.run(_stub_spec("b"), _stub_spec("v"))

        assert isinstance(ab.baseline_telemetry, CombatLabTelemetry)
        assert isinstance(ab.variant_telemetry, CombatLabTelemetry)
        # Distinct instances — the baseline telemetry must not be the
        # same object as the variant telemetry (otherwise the roles
        # would clobber each other mid-run).
        assert ab.baseline_telemetry is not ab.variant_telemetry

    def test_ab_battle_outcome_is_frozen(self):
        baseline_outcome, variant_outcome = _mock_outcomes()
        ab = ABBattleOutcome(
            baseline_outcome=baseline_outcome,
            baseline_telemetry=CombatLabTelemetry(),
            variant_outcome=variant_outcome,
            variant_telemetry=CombatLabTelemetry(),
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            ab.baseline_outcome = MagicMock()  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Parity — identical specs produce identical outcomes (Task 2.3)
# ---------------------------------------------------------------------------


def _design_dict() -> dict:
    return {
        "name": "ParityCruiser",
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


def _parity_spec(seed: int):
    """Build a minimal 1v1 BattleSpec with a fixed seed."""
    from game.core.math import Vector2
    from game.simulation.battle_spec import (
        BattleSpec,
        CombatPolicies,
        EntryVector,
        ShipSpec,
        SquadronSpec,
        TaskForceSpec,
        TeamSpec,
    )
    from game.simulation.combat.modifier_stack import ModifierStack
    from game.simulation.combat.telemetry import TelemetryLevel
    from game.simulation.systems.battle_end_conditions import TickLimitCondition

    def _ship(tag: str, x: float) -> ShipSpec:
        return ShipSpec(
            instance_id=f"parity-{tag}",
            design_id="Cruiser",
            theme_id="Federation",
            name=tag,
            position=Vector2(x, 0),
            angle=0.0,
            velocity=Vector2(0, 0),
            components=(),
        )

    def _team(team_id: int, ship: ShipSpec) -> TeamSpec:
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
                            ships=(ship,),
                        ),
                    ),
                ),
            ),
        )

    return BattleSpec(
        seed=seed,
        telemetry_level=TelemetryLevel.MINIMAL,
        boundary=None,
        end_condition=TickLimitCondition(max_ticks=5),
        absolute_max_ticks=50,
        teams=(
            _team(0, _ship("a", -500)),
            _team(1, _ship("b", 500)),
        ),
        modifier_stack=ModifierStack.empty(),
        post_battle_hook=None,
    )


def test_parity_identical_specs_produce_identical_outcomes(fresh_registries):
    """Given two structurally identical specs with the same seed, the A/B
    runner should produce outcomes whose observable state agrees on the
    deterministic invariants (duration, end reason, surviving ships)."""
    from game.ai.ai_factory import AIControllerFactory
    from game.simulation.entities.ship_serialization import ShipSerializer

    def ship_builder(ship_spec, team_id):
        ship = ShipSerializer.from_dict(
            _design_dict(), registries=fresh_registries,
        )
        ship.instance_id = ship_spec.instance_id
        return ship

    runner = ABBattleRunner(
        ai_factory=AIControllerFactory(), ship_builder=ship_builder,
    )
    baseline_spec = _parity_spec(seed=4242)
    variant_spec = _parity_spec(seed=4242)  # structurally identical, same seed

    ab = runner.run(baseline_spec, variant_spec)

    # Deterministic invariants: same seed + same spec → same duration
    # and end reason.
    assert ab.baseline_outcome.duration_ticks == ab.variant_outcome.duration_ticks
    assert ab.baseline_outcome.end_reason == ab.variant_outcome.end_reason
    # Same ship identities in the outcome (role keys match without any
    # baseline-prefix remapping).
    baseline_ids = {s.instance_id for t in ab.baseline_outcome.teams for s in t.ships}
    variant_ids = {s.instance_id for t in ab.variant_outcome.teams for s in t.ships}
    assert baseline_ids == variant_ids
