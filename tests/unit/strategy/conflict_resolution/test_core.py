"""
Unit tests for ConflictResolutionEngine core functionality.

Tests initialization, conflict result dataclass, seed generation, and conflict detection.
"""

import pytest
from unittest.mock import MagicMock, patch

from game.strategy.data.hex_math import HexCoord


class TestConflictResolutionEngineInit:
    """Tests for ConflictResolutionEngine initialization."""

    def test_engine_can_be_created(self):
        """ConflictResolutionEngine can be instantiated."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine

        engine = ConflictResolutionEngine()

        assert engine is not None

    def test_engine_accepts_battle_resolver(self):
        """ConflictResolutionEngine accepts battle_resolver parameter."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        class MockResolver(IBattleResolver):
            def resolve_battle(self, fleet1, fleet2, seed=None, registries=None):
                return BattleResult(winner=0, tick_count=0, team0_survivors=[], team1_survivors=[])

        resolver = MockResolver()
        engine = ConflictResolutionEngine(battle_resolver=resolver)

        assert engine._battle_resolver is resolver

    def test_engine_defaults_to_simulation_resolver(self):
        """ConflictResolutionEngine defaults to SimulationBattleResolver."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        engine = ConflictResolutionEngine()

        assert isinstance(engine._battle_resolver, SimulationBattleResolver)


class TestConflictResult:
    """Tests for ConflictResult dataclass."""

    def test_conflict_result_can_be_created(self):
        """ConflictResult can be instantiated."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResult

        result = ConflictResult(combats_resolved=5, fleets_destroyed=[1, 2, 3])

        assert result.combats_resolved == 5
        assert result.fleets_destroyed == [1, 2, 3]

    def test_conflict_result_empty_destruction(self):
        """ConflictResult with no destroyed fleets."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResult

        result = ConflictResult(combats_resolved=0, fleets_destroyed=[])

        assert result.combats_resolved == 0
        assert result.fleets_destroyed == []


class TestBattleSeedGeneration:
    """Tests for battle seed counter."""

    def test_seed_counter_increments(self):
        """Battle seed counter increments each call."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine

        engine = ConflictResolutionEngine()

        seed1 = engine._generate_battle_seed()
        seed2 = engine._generate_battle_seed()
        seed3 = engine._generate_battle_seed()

        assert seed2 == seed1 + 1
        assert seed3 == seed2 + 1

    def test_seed_counter_starts_at_one(self):
        """First seed is 1."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine

        engine = ConflictResolutionEngine()

        seed = engine._generate_battle_seed()

        assert seed == 1

    def test_multiple_engines_independent(self):
        """Different engine instances have independent counters."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine

        engine1 = ConflictResolutionEngine()
        engine2 = ConflictResolutionEngine()

        seed1 = engine1._generate_battle_seed()
        seed2 = engine2._generate_battle_seed()

        assert seed1 == seed2 == 1

    def test_same_seed_produces_deterministic_result(self):
        """Same seed should produce the same battle result.

        PROJ-36 Phase 5: Edge case test for battle determinism.
        The battle resolver receives a seed that should make results reproducible.
        """
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        # Create a resolver that tracks the seed it receives
        class SeedTrackingResolver(IBattleResolver):
            def __init__(self):
                self.received_seeds = []

            def resolve_battle(self, fleet1, fleet2, seed=None, registries=None):
                self.received_seeds.append(seed)
                # Return deterministic result based on seed
                return BattleResult(
                    winner=seed % 2 if seed else 0,  # Deterministic based on seed
                    tick_count=seed or 0,
                    team0_survivors=[],
                    team1_survivors=[]
                )

        resolver = SeedTrackingResolver()
        engine = ConflictResolutionEngine(resolver)

        fleet1 = MagicMock()
        fleet1.location = HexCoord(0, 0)
        fleet1.owner_id = 0
        fleet1.ships = [MagicMock()]
        fleet1.ships[0].is_combat_capable = MagicMock(return_value=True)

        fleet2 = MagicMock()
        fleet2.location = HexCoord(0, 0)
        fleet2.owner_id = 1
        fleet2.ships = [MagicMock()]
        fleet2.ships[0].is_combat_capable = MagicMock(return_value=True)

        # Resolve combat
        result = engine._resolve_combat(fleet1, fleet2)

        # Verify seed was passed to resolver
        assert len(resolver.received_seeds) == 1
        assert resolver.received_seeds[0] is not None
        assert resolver.received_seeds[0] == 1  # First seed should be 1


class TestConflictDetection:
    """Tests for _resolve_conflicts method."""

    def test_resolve_conflicts_detects_collision(self):
        """Conflicts are detected when fleets share location."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine

        engine = ConflictResolutionEngine()

        empire1 = MagicMock()
        empire1.id = 0
        empire2 = MagicMock()
        empire2.id = 1

        fleet1 = MagicMock()
        fleet1.location = HexCoord(5, 5)
        fleet1.owner_id = 0

        fleet2 = MagicMock()
        fleet2.location = HexCoord(5, 5)  # Same location
        fleet2.owner_id = 1

        empire1.fleets = [fleet1]
        empire2.fleets = [fleet2]

        with patch.object(engine, '_resolve_combat_at_hex') as mock_resolve:
            engine._resolve_conflicts([empire1, empire2])

            mock_resolve.assert_called()

    def test_no_conflict_same_empire(self):
        """No conflict when same empire's fleets share location."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine

        engine = ConflictResolutionEngine()

        empire = MagicMock()
        empire.id = 0

        fleet1 = MagicMock()
        fleet1.location = HexCoord(5, 5)
        fleet1.owner_id = 0

        fleet2 = MagicMock()
        fleet2.location = HexCoord(5, 5)
        fleet2.owner_id = 0  # Same empire

        empire.fleets = [fleet1, fleet2]

        with patch.object(engine, '_resolve_combat_at_hex') as mock_resolve:
            engine._resolve_conflicts([empire])

            mock_resolve.assert_not_called()

    def test_three_way_conflict_detected(self):
        """Three empires at same hex triggers combat."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine

        engine = ConflictResolutionEngine()

        empire1 = MagicMock()
        empire1.id = 0
        empire2 = MagicMock()
        empire2.id = 1
        empire3 = MagicMock()
        empire3.id = 2

        fleet1 = MagicMock()
        fleet1.location = HexCoord(5, 5)
        fleet1.owner_id = 0

        fleet2 = MagicMock()
        fleet2.location = HexCoord(5, 5)
        fleet2.owner_id = 1

        fleet3 = MagicMock()
        fleet3.location = HexCoord(5, 5)
        fleet3.owner_id = 2

        empire1.fleets = [fleet1]
        empire2.fleets = [fleet2]
        empire3.fleets = [fleet3]

        with patch.object(engine, '_resolve_combat_at_hex') as mock_resolve:
            engine._resolve_conflicts([empire1, empire2, empire3])

            # Should be called with all three occupants
            mock_resolve.assert_called_once()
            call_args = mock_resolve.call_args[0][0]
            assert len(call_args) == 3


class TestCombatResolution:
    """Tests for _resolve_combat method."""

    def test_resolve_combat_rng_fallback_for_empty_fleet(self):
        """RNG fallback for empty fleets."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine

        engine = ConflictResolutionEngine()

        fleet1 = MagicMock()
        fleet1.ships = []  # Empty fleet

        fleet2 = MagicMock()
        fleet2.ships = []  # Empty fleet

        with patch('game.strategy.engine.conflict_resolution_engine.random.random') as mock_random:
            mock_random.return_value = 0.3  # < 0.5 means fleet2 wins

            result = engine._resolve_combat(fleet1, fleet2)

            assert result == fleet2

    def test_resolve_combat_rng_favors_fleet1_when_above_threshold(self):
        """RNG fallback favors fleet1 when random > 0.5."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine

        engine = ConflictResolutionEngine()

        fleet1 = MagicMock()
        fleet1.ships = []

        fleet2 = MagicMock()
        fleet2.ships = []

        with patch('game.strategy.engine.conflict_resolution_engine.random.random') as mock_random:
            mock_random.return_value = 0.7  # > 0.5 means fleet1 wins

            result = engine._resolve_combat(fleet1, fleet2)

            assert result == fleet1

    def test_resolve_combat_uses_simulation(self):
        """Full simulation used when both fleets have ships."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine

        engine = ConflictResolutionEngine()

        fleet1 = MagicMock()
        fleet1.ships = [MagicMock()]  # Has ships

        fleet2 = MagicMock()
        fleet2.ships = [MagicMock()]  # Has ships

        with patch.object(engine, '_resolve_combat_simulated') as mock_sim:
            mock_sim.return_value = fleet1

            result = engine._resolve_combat(fleet1, fleet2)

            mock_sim.assert_called_with(fleet1, fleet2)
            assert result == fleet1

    def test_empty_fleet_vs_fleet_with_ships(self):
        """Empty fleet vs fleet with ships uses RNG fallback."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine

        engine = ConflictResolutionEngine()

        fleet1 = MagicMock()
        fleet1.ships = []  # Empty

        fleet2 = MagicMock()
        fleet2.ships = [MagicMock()]  # Has ships

        with patch('game.strategy.engine.conflict_resolution_engine.random.random') as mock_random:
            mock_random.return_value = 0.3  # < 0.5 means fleet2 wins

            result = engine._resolve_combat(fleet1, fleet2)

            # RNG fallback should be used
            assert result == fleet2

    def test_fleet_with_ships_vs_empty(self):
        """Fleet with ships vs empty fleet uses RNG fallback."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine

        engine = ConflictResolutionEngine()

        fleet1 = MagicMock()
        fleet1.ships = [MagicMock()]  # Has ships

        fleet2 = MagicMock()
        fleet2.ships = []  # Empty

        with patch('game.strategy.engine.conflict_resolution_engine.random.random') as mock_random:
            mock_random.return_value = 0.7  # > 0.5 means fleet1 wins

            result = engine._resolve_combat(fleet1, fleet2)

            assert result == fleet1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
