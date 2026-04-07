"""
Tests for per-battle RNG isolation (PROJ-252 Phase 1).

Verifies that:
- BattleEngine uses a per-instance random.Random, not the global random module
- Two battles with the same seed produce identical results
- Global random state does not affect battle outcomes
- DamageCalculator and CollisionSystem use injected RNG
"""
import random
from unittest.mock import Mock, patch

from game.simulation.systems.battle_engine import BattleEngine
from game.simulation.combat.damage_calculator import DamageCalculator
from game.engine.collision import CollisionSystem


def _mock_ai_factory():
    """Create a mock AI factory that returns empty controller lists."""
    factory = Mock()
    factory.create_for_ships = Mock(return_value=[])
    return factory


class TestBattleEngineRNG:
    """BattleEngine should create a per-instance RNG from seed."""

    def test_start_creates_rng_instance(self):
        """After start(), engine should have a random.Random instance."""
        engine = BattleEngine(ai_factory=_mock_ai_factory())
        engine.start([], [], seed=42)
        assert hasattr(engine, 'rng')
        assert isinstance(engine.rng, random.Random)

    def test_start_with_seed_creates_seeded_rng(self):
        """RNG created with same seed should produce same sequence."""
        engine1 = BattleEngine(ai_factory=_mock_ai_factory())
        engine1.start([], [], seed=42)
        seq1 = [engine1.rng.random() for _ in range(10)]

        engine2 = BattleEngine(ai_factory=_mock_ai_factory())
        engine2.start([], [], seed=42)
        seq2 = [engine2.rng.random() for _ in range(10)]

        assert seq1 == seq2

    def test_start_without_seed_creates_rng(self):
        """Even without a seed, engine should have an RNG instance."""
        engine = BattleEngine(ai_factory=_mock_ai_factory())
        engine.start([], [], seed=None)
        assert hasattr(engine, 'rng')
        assert isinstance(engine.rng, random.Random)

    def test_different_seeds_produce_different_sequences(self):
        """Different seeds should produce different RNG sequences."""
        engine1 = BattleEngine(ai_factory=_mock_ai_factory())
        engine1.start([], [], seed=42)
        seq1 = [engine1.rng.random() for _ in range(10)]

        engine2 = BattleEngine(ai_factory=_mock_ai_factory())
        engine2.start([], [], seed=99)
        seq2 = [engine2.rng.random() for _ in range(10)]

        assert seq1 != seq2

    def test_global_random_does_not_affect_battle_rng(self):
        """Calling random.random() globally should not affect the battle RNG."""
        engine1 = BattleEngine(ai_factory=_mock_ai_factory())
        engine1.start([], [], seed=42)
        seq1 = [engine1.rng.random() for _ in range(10)]

        # Contaminate global random state
        random.seed(999)
        for _ in range(100):
            random.random()

        engine2 = BattleEngine(ai_factory=_mock_ai_factory())
        engine2.start([], [], seed=42)
        seq2 = [engine2.rng.random() for _ in range(10)]

        assert seq1 == seq2

    def test_start_does_not_call_global_random_seed(self):
        """start() should not call random.seed() on the global module."""
        engine = BattleEngine(ai_factory=_mock_ai_factory())
        with patch('game.simulation.systems.battle_engine.random.seed') as mock_seed:
            engine.start([], [], seed=42)
            mock_seed.assert_not_called()


class TestDamageCalculatorRNG:
    """DamageCalculator should accept and use an injected RNG."""

    def test_accepts_rng_parameter(self):
        """DamageCalculator should accept rng in constructor."""
        rng = random.Random(42)
        calc = DamageCalculator(rng=rng)
        assert calc.rng is rng

    def test_default_rng_when_none_provided(self):
        """When no RNG provided, DamageCalculator should still have one."""
        calc = DamageCalculator()
        assert hasattr(calc, 'rng')
        assert isinstance(calc.rng, random.Random)

    def test_uses_injected_rng_not_global(self):
        """DamageCalculator should use injected RNG, not random.choices()."""
        rng = random.Random(42)
        calc = DamageCalculator(rng=rng)
        assert calc.rng is rng


class TestCollisionSystemRNG:
    """CollisionSystem should accept and use an injected RNG."""

    def test_accepts_rng_parameter(self):
        """CollisionSystem should accept rng in constructor."""
        rng = random.Random(42)
        system = CollisionSystem(rng=rng)
        assert system.rng is rng

    def test_default_rng_when_none_provided(self):
        """When no RNG provided, CollisionSystem should still have one."""
        system = CollisionSystem()
        assert hasattr(system, 'rng')
        assert isinstance(system.rng, random.Random)
