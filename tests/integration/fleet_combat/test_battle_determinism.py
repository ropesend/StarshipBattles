"""
Tests for battle determinism and RNG isolation (PROJ-252 Phase 4).

Verifies that:
- Same seed produces identical battle outcomes
- Global random state does not contaminate battle results
- Different seeds produce different outcomes
"""
import random

from game.simulation.systems.battle_engine import BattleEngine
from game.ai.ai_factory import AIControllerFactory
from tests.fixtures.ships import create_test_ship


def _run_battle(team0_ships, team1_ships, seed, max_ticks=500):
    """Run a battle and return (winner, tick_count, survivor_hp_list)."""
    factory = AIControllerFactory()
    engine = BattleEngine(ai_factory=factory)
    engine.start(team0_ships, team1_ships, seed=seed)

    while not engine.is_battle_over() and engine.tick_counter < max_ticks:
        engine.update()

    survivor_hps = []
    for ship in engine.ships:
        if ship.is_alive:
            survivor_hps.append((ship.name, ship.hp))

    return engine.get_winner(), engine.tick_counter, survivor_hps


def _make_teams(fresh_registries):
    """Create two small teams of ships for determinism testing."""
    team0 = [
        create_test_ship(
            name="Alpha",
            x=500, y=400,
            team_id=0,
            add_bridge=True,
            add_engine=True,
            add_weapons=2,
            registries=fresh_registries,
        )
    ]
    team1 = [
        create_test_ship(
            name="Bravo",
            x=2000, y=400,
            team_id=1,
            add_bridge=True,
            add_engine=True,
            add_weapons=2,
            registries=fresh_registries,
        )
    ]
    return team0, team1


class TestBattleDeterminism:
    """Same seed must produce identical battle results."""

    def test_same_seed_same_outcome(self, fresh_registries):
        """Two battles with identical seed produce identical results."""
        t0a, t1a = _make_teams(fresh_registries)
        winner1, ticks1, survivors1 = _run_battle(t0a, t1a, seed=42)

        t0b, t1b = _make_teams(fresh_registries)
        winner2, ticks2, survivors2 = _run_battle(t0b, t1b, seed=42)

        assert winner1 == winner2
        assert ticks1 == ticks2
        assert survivors1 == survivors2

    def test_different_seeds_produce_different_rng_sequences(self):
        """Battles with different seeds use different RNG sequences."""
        factory1 = AIControllerFactory()
        engine1 = BattleEngine(ai_factory=factory1)
        engine1.start([], [], seed=42)
        seq1 = [engine1.rng.random() for _ in range(10)]

        factory2 = AIControllerFactory()
        engine2 = BattleEngine(ai_factory=factory2)
        engine2.start([], [], seed=99)
        seq2 = [engine2.rng.random() for _ in range(10)]

        assert seq1 != seq2

    def test_global_random_contamination_has_no_effect(self, fresh_registries):
        """Global random.random() calls between battles should not affect outcomes."""
        # Run battle 1 cleanly
        t0a, t1a = _make_teams(fresh_registries)
        winner1, ticks1, survivors1 = _run_battle(t0a, t1a, seed=42)

        # Contaminate global random state heavily
        random.seed(999999)
        for _ in range(10000):
            random.random()

        # Run battle 2 with same seed
        t0b, t1b = _make_teams(fresh_registries)
        winner2, ticks2, survivors2 = _run_battle(t0b, t1b, seed=42)

        assert winner1 == winner2
        assert ticks1 == ticks2
        assert survivors1 == survivors2

    def test_interleaved_global_calls_no_effect(self, fresh_registries):
        """Global random calls before start() don't affect the battle."""
        # Call global random, then run battle
        random.seed(12345)
        [random.random() for _ in range(500)]

        t0a, t1a = _make_teams(fresh_registries)
        winner1, ticks1, survivors1 = _run_battle(t0a, t1a, seed=42)

        # Different global state, same battle seed
        random.seed(99999)
        [random.random() for _ in range(999)]

        t0b, t1b = _make_teams(fresh_registries)
        winner2, ticks2, survivors2 = _run_battle(t0b, t1b, seed=42)

        assert winner1 == winner2
        assert ticks1 == ticks2
        assert survivors1 == survivors2
