"""PROJ-471 Task 1.2 -- per-battle CombatSubsystems determinism characterization.

The class-level ShipCombatEngine subsystems were load-bearing: ``battle_setup``
installed a seeded ``DamageCalculator(rng=engine.rng)`` so the per-battle RNG
reached every ship, and ram/mine resolvers read that shared calculator. After
the per-instance refactor the BattleEngine owns a per-battle ``CombatSubsystems``
bundle. These tests pin that:

1. The engine exposes a per-battle bundle whose DamageCalculator is seeded with
   the engine's RNG (determinism wiring preserved).
2. Every ship's combat engine uses that same per-battle bundle within the battle.
3. Two engines started with the same seed produce the same RNG sequence
   (combat behavior / RNG draws unchanged).
4. The bundle is rebuilt per ``start`` -> no cross-battle leakage of the prior
   battle's seeded calculator.
"""

from game.ai.ai_factory import AIControllerFactory
from game.simulation.systems.battle_engine import BattleEngine
from game.simulation.systems.battle_end_conditions import TickLimitCondition


def _ship(fresh_registries, name: str, team_id: int, x: float = 0.0):
    from game.simulation.entities.ship import Ship

    return Ship(
        name=name,
        x=x,
        y=0.0,
        color=(255, 255, 255),
        team_id=team_id,
        ship_class="Escort",
        theme_id="Federation",
        registries=fresh_registries,
    )


def test_engine_owns_per_battle_bundle_seeded_with_engine_rng(fresh_registries):
    engine = BattleEngine(ai_factory=AIControllerFactory())
    engine.start(
        [_ship(fresh_registries, "A", 0, 100)],
        [_ship(fresh_registries, "B", 1, -100)],
        seed=7,
        end_condition=TickLimitCondition(max_ticks=1),
    )

    bundle = engine.combat_subsystems
    assert bundle is not None
    # The per-battle damage calculator must be keyed to the engine's seeded RNG.
    assert bundle.damage_calculator.rng is engine.rng


def test_all_ship_engines_share_the_per_battle_bundle(fresh_registries):
    engine = BattleEngine(ai_factory=AIControllerFactory())
    ships = [
        _ship(fresh_registries, "A", 0, 100),
        _ship(fresh_registries, "B", 1, -100),
    ]
    engine.start([ships[0]], [ships[1]], seed=7,
                 end_condition=TickLimitCondition(max_ticks=1))

    bundle = engine.combat_subsystems
    for s in ships:
        assert s.combat_engine._damage_calculator is bundle.damage_calculator
        assert s.combat_engine._weapon_firing_system is bundle.weapon_firing_system


def test_same_seed_produces_identical_rng_sequence(fresh_registries):
    """Determinism: identical seed -> identical per-battle RNG stream."""
    def run_seeded():
        engine = BattleEngine(ai_factory=AIControllerFactory())
        engine.start(
            [_ship(fresh_registries, "A", 0, 100)],
            [_ship(fresh_registries, "B", 1, -100)],
            seed=999,
            end_condition=TickLimitCondition(max_ticks=1),
        )
        rng = engine.combat_subsystems.damage_calculator.rng
        return [rng.random() for _ in range(10)]

    assert run_seeded() == run_seeded()


def test_same_seed_produces_identical_battle_outcome(fresh_registries):
    """PROJ-471 Task 4.3 (Codex finding 3): prove COMBAT BEHAVIOR -- not just
    raw rng draws -- is unchanged through the CombatSubsystems path. Run a real
    seeded battle to completion twice and assert identical winner + survivor HP.
    """
    from tests.fixtures.ships import create_test_ship

    def run_battle():
        team0 = [create_test_ship(
            name="Alpha", x=500, y=400, team_id=0,
            add_bridge=True, add_engine=True, add_weapons=2,
            registries=fresh_registries,
        )]
        team1 = [create_test_ship(
            name="Bravo", x=2000, y=400, team_id=1,
            add_bridge=True, add_engine=True, add_weapons=2,
            registries=fresh_registries,
        )]
        engine = BattleEngine(ai_factory=AIControllerFactory())
        engine.start(team0, team1, seed=4242)
        while not engine.is_battle_over() and engine.tick_counter < 500:
            engine.update()
        survivors = sorted((s.name, round(s.hp, 6)) for s in engine.ships if s.is_alive)
        return engine.get_winner(), engine.tick_counter, survivors

    assert run_battle() == run_battle()


def test_bundle_rebuilt_per_start_no_cross_battle_leak(fresh_registries):
    engine = BattleEngine(ai_factory=AIControllerFactory())
    engine.start([_ship(fresh_registries, "A", 0, 100)],
                 [_ship(fresh_registries, "B", 1, -100)],
                 seed=1, end_condition=TickLimitCondition(max_ticks=1))
    first_calc = engine.combat_subsystems.damage_calculator

    engine.start([_ship(fresh_registries, "C", 0, 100)],
                 [_ship(fresh_registries, "D", 1, -100)],
                 seed=2, end_condition=TickLimitCondition(max_ticks=1))
    second_calc = engine.combat_subsystems.damage_calculator

    assert first_calc is not second_calc
    assert second_calc.rng is engine.rng
