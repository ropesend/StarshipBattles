"""End-to-end smoke test for ``make_minimal_spec`` (PROJ-281 Phase 1).

Proves the helper produces a spec that ``BattleController.start_from_spec``
accepts without error and produces a populated ``BattleOutcome`` after a
brief tick loop. This is the critical contract for the ~47 test callers
that will migrate off ``BattleScreen.start(team0, team1)`` in Phase 2.
"""
from __future__ import annotations


def test_minimal_spec_feeds_battle_controller(fresh_registries):
    from game.ai.ai_factory import AIControllerFactory
    from game.simulation.battle_controller import BattleController
    from tests.fixtures.battle import make_minimal_spec
    from tests.fixtures.ships import create_test_ship

    s1 = create_test_ship(registries=fresh_registries)
    s2 = create_test_ship(registries=fresh_registries)
    s1.x, s1.y = -500.0, 0.0
    s2.x, s2.y = 500.0, 0.0

    spec = make_minimal_spec({0: [s1], 1: [s2]}, max_ticks=10)

    # Test pattern: pass a ship_builder that returns the pre-built ships.
    # This is the recommended migration pattern for the ~47 legacy callers.
    ships_ordered = [s1, s2]

    def _ship_builder(ship_spec, team_id):
        _ = ship_spec
        return ships_ordered[team_id]

    controller = BattleController()
    result, ships_by_role = controller.start_from_spec(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=_ship_builder,
    )

    assert result.success is True

    # Drive the controller for the full spec duration
    for _ in range(spec.absolute_max_ticks):
        if controller.is_battle_over():
            break
        controller.update()

    outcome = controller.get_outcome()
    assert outcome is not None
    assert len(outcome.teams) == 2
    assert outcome.seed == 0


def test_minimal_spec_headless_via_run_battle(fresh_registries):
    """Alternate path: the same spec works with the headless
    ``run_battle(spec)`` entry point."""
    from game.ai.ai_factory import AIControllerFactory
    from game.simulation.battle_runner import run_battle
    from tests.fixtures.battle import make_minimal_spec
    from tests.fixtures.ships import create_test_ship

    s1 = create_test_ship(registries=fresh_registries)
    s2 = create_test_ship(registries=fresh_registries)
    s1.x, s1.y = -500.0, 0.0
    s2.x, s2.y = 500.0, 0.0

    spec = make_minimal_spec({0: [s1], 1: [s2]}, max_ticks=5)

    outcome = run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=lambda ship_spec, team_id: (
            s1 if team_id == 0 else s2
        ),
    )

    assert outcome is not None
    assert len(outcome.teams) == 2
