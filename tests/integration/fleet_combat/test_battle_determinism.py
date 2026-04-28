"""
Tests for battle determinism and RNG isolation (PROJ-252 Phase 4).

Verifies that:
- Same seed produces identical battle outcomes
- Global random state does not contaminate battle results
- Different seeds produce different outcomes

PROJ-312 Phase 1 extends this harness with a state-hash regression
(``TestBattleStateHashRegression``) that fingerprints the full per-ship
final state and asserts bit-stability across runs. The hash catches subtle
divergences (a single position drift, an extra projectile) that the
coarser winner/tick/HP comparison would miss.
"""
import hashlib
import json
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


def _hash_battle_final_state(team0_ships, team1_ships, seed, max_ticks=500):
    """Run a seeded battle and return a stable SHA-256 of its full per-ship
    final state.

    The fingerprint includes per-ship name, alive status, derelict status,
    HP, position (rounded to 4 decimals to absorb pure float-noise from
    re-runs), rotation, and team_id. Sorted by ship name so iteration
    order can't perturb the hash.

    Used by ``TestBattleStateHashRegression`` (PROJ-312 Phase 1 Task 1.4).
    """
    factory = AIControllerFactory()
    engine = BattleEngine(ai_factory=factory)
    engine.start(team0_ships, team1_ships, seed=seed)

    while not engine.is_battle_over() and engine.tick_counter < max_ticks:
        engine.update()

    state = []
    for ship in sorted(engine.ships, key=lambda s: s.name):
        rotation = float(getattr(ship, "angle", 0.0) or 0.0)
        state.append({
            "name": ship.name,
            "team_id": ship.team_id,
            "is_alive": bool(ship.is_alive),
            "is_derelict": bool(getattr(ship, "is_derelict", False)),
            "hp": float(ship.hp),
            "x": round(float(ship.x), 4),
            "y": round(float(ship.y), 4),
            "rotation": round(rotation, 4),
        })
    state_blob = {
        "tick_counter": engine.tick_counter,
        "winner": engine.get_winner(),
        "ships": state,
    }
    canonical = json.dumps(state_blob, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class TestBattleStateHashRegression:
    """PROJ-312 Phase 1 Task 1.4 — bit-stable per-ship final state.

    Two runs of the same seeded battle must produce the same SHA-256 of the
    canonical state fingerprint. This is a stronger contract than the
    coarse winner/tick/HP comparison in ``TestBattleDeterminism``: it
    catches a single-pixel position drift, a stray projectile, or any
    other subtle divergence in the simulation hot path.
    """

    def test_seeded_battle_state_hash_stable_within_process(self, fresh_registries):
        """Bit-identical state hash across two runs in the same process."""
        t0a, t1a = _make_teams(fresh_registries)
        hash_a = _hash_battle_final_state(t0a, t1a, seed=42)

        t0b, t1b = _make_teams(fresh_registries)
        hash_b = _hash_battle_final_state(t0b, t1b, seed=42)

        assert hash_a == hash_b, (
            "Two seed=42 battles produced different state hashes within "
            "the same process. A non-seeded RNG consumer is leaking into "
            "the hot path. Re-run the AST guard "
            "(tests/unit/quality/test_no_unseeded_random.py)."
        )

    def test_seeded_battle_state_hash_stable_across_repeats(self, fresh_registries):
        """Run the same seeded battle 5 times; every hash must agree.

        Catches flakiness that a single re-run might miss — e.g., a
        non-deterministic dict iteration order that happens to be stable
        for two consecutive runs but drifts on the third.
        """
        hashes = []
        for _ in range(5):
            t0, t1 = _make_teams(fresh_registries)
            hashes.append(_hash_battle_final_state(t0, t1, seed=42))
        assert len(set(hashes)) == 1, (
            f"5 seed=42 runs produced {len(set(hashes))} distinct state "
            f"hashes (expected 1). Hashes: {hashes}"
        )

    # Note: a "different seeds → different state hash" assertion is
    # tempting here, but the simple 1v1 deterministic-kite scenario
    # converges on the same final ship positions regardless of seed.
    # Seed-sensitivity is verified at the RNG-sequence level by
    # ``test_different_seeds_produce_different_rng_sequences`` and at
    # the unit level by
    # ``tests/unit/ai/test_erratic_behavior_seeded.py::test_different_seeds_diverge``.
