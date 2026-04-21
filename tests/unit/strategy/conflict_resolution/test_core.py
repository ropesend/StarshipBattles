"""
Unit tests for ConflictResolutionEngine core functionality.

Tests initialization, conflict result dataclass, seed generation, and conflict detection.
"""

import pytest
from unittest.mock import MagicMock, patch

from game.core.hex_math import HexCoord


class TestConflictResolutionEngineInit:
    """Tests for ConflictResolutionEngine initialization."""

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

        engine = ConflictResolutionEngine(battle_resolver=MagicMock())

        seed1 = engine._generate_battle_seed()
        seed2 = engine._generate_battle_seed()
        seed3 = engine._generate_battle_seed()

        assert seed2 == seed1 + 1
        assert seed3 == seed2 + 1

    def test_seed_counter_starts_at_one(self):
        """First seed is 1."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine

        engine = ConflictResolutionEngine(battle_resolver=MagicMock())

        seed = engine._generate_battle_seed()

        assert seed == 1

    def test_multiple_engines_independent(self):
        """Different engine instances have independent counters."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine

        engine1 = ConflictResolutionEngine(battle_resolver=MagicMock())
        engine2 = ConflictResolutionEngine(battle_resolver=MagicMock())

        seed1 = engine1._generate_battle_seed()
        seed2 = engine2._generate_battle_seed()

        assert seed1 == seed2 == 1

    def test_same_seed_produces_deterministic_result(self):
        """Battle resolver receives a seed for reproducibility (PROJ-36 Phase 5).

        PROJ-275 Phase 7: now exercised through `_resolve_combat_at_hex`
        (single-call N-team), since `_resolve_combat`/`_resolve_combat_simulated`
        were removed with the sequential decomposition.
        """
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        class SeedTrackingResolver(IBattleResolver):
            def __init__(self):
                self.received_seeds = []

            def resolve_battle(self, fleets, modifiers=None, seed=None,
                               registries=None, environmental_effects=None):
                self.received_seeds.append(seed)
                return BattleResult(
                    winner=0,
                    tick_count=seed or 0,
                    team_survivors={i: [] for i in range(len(list(fleets)))},
                )

        resolver = SeedTrackingResolver()
        engine = ConflictResolutionEngine(resolver)

        empire1 = MagicMock(); empire1.id = 0
        empire2 = MagicMock(); empire2.id = 1
        fleet1 = MagicMock()
        fleet1.location = HexCoord(0, 0); fleet1.owner_id = 0; fleet1.ships = [MagicMock()]
        fleet2 = MagicMock()
        fleet2.location = HexCoord(0, 0); fleet2.owner_id = 1; fleet2.ships = [MagicMock()]

        engine._resolve_combat_at_hex([(empire1, fleet1), (empire2, fleet2)])

        assert len(resolver.received_seeds) == 1
        assert resolver.received_seeds[0] == 1  # First seed


class TestConflictDetection:
    """Tests for _resolve_conflicts method."""

    def test_resolve_conflicts_detects_collision(self):
        """Conflicts are detected when fleets share location."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine

        engine = ConflictResolutionEngine(battle_resolver=MagicMock())

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

        engine = ConflictResolutionEngine(battle_resolver=MagicMock())

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

        engine = ConflictResolutionEngine(battle_resolver=MagicMock())

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


# PROJ-275 Phase 7: deleted `TestCombatResolution`. Its tests exercised
# the now-removed `_resolve_combat`/`_resolve_combat_simulated` helpers
# (sequential 2-fleet decomposition with RNG fallback for empty fleets).
# Empty-fleet handling is now the responsibility of
# `SimulationBattleResolver.resolve_battle`, which short-circuits when
# fewer than two teams are combat-capable. The N-team battle path itself
# is covered by `tests/integration/strategy/test_three_empire_battle.py`.


class TestBuildingFleetsCombat:
    """Tests for building fleets participating in combat (PROJ-67 Phase 6)."""

    def test_building_fleet_participates_in_combat(self):
        """Building fleet can still be attacked (no special protection)."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.data.fleet import Fleet
        from game.strategy.data.order_types import FleetOrder, OrderType

        engine = ConflictResolutionEngine(battle_resolver=MagicMock())

        # Building fleet (has BUILD order)
        building_fleet = MagicMock(spec=Fleet)
        building_fleet.location = HexCoord(5, 5)
        building_fleet.owner_id = 0
        building_fleet.id = 1
        building_fleet.orders = [FleetOrder(OrderType.BUILD)]
        building_fleet.construction_queue = [{"design_id": "ship", "turns_remaining": 5}]

        # Attacker fleet
        attacker_fleet = MagicMock(spec=Fleet)
        attacker_fleet.location = HexCoord(5, 5)  # Same location
        attacker_fleet.owner_id = 1
        attacker_fleet.id = 2

        empire1 = MagicMock()
        empire1.id = 0
        empire1.fleets = [building_fleet]

        empire2 = MagicMock()
        empire2.id = 1
        empire2.fleets = [attacker_fleet]

        # Conflict detection should still work
        with patch.object(engine, '_resolve_combat_at_hex') as mock_resolve:
            engine._resolve_conflicts([empire1, empire2])

            # Combat should be triggered despite BUILD order
            mock_resolve.assert_called_once()
            call_args = mock_resolve.call_args[0][0]
            fleet_ids = [f.id for _, f in call_args]
            assert 1 in fleet_ids  # Building fleet participates
            assert 2 in fleet_ids  # Attacker participates

    def test_building_fleet_in_hex_collision_detection(self):
        """Fleet with BUILD order is included in hex collision detection."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.data.order_types import OrderType

        engine = ConflictResolutionEngine(battle_resolver=MagicMock())

        # Create building fleet
        building_fleet = MagicMock()
        building_fleet.location = HexCoord(10, 10)
        building_fleet.owner_id = 0
        building_fleet.id = "building_fleet"
        building_fleet.orders = [MagicMock(type=OrderType.BUILD)]

        # Enemy fleet at same location
        enemy_fleet = MagicMock()
        enemy_fleet.location = HexCoord(10, 10)
        enemy_fleet.owner_id = 1
        enemy_fleet.id = "enemy_fleet"

        empire1 = MagicMock()
        empire1.id = 0
        empire1.fleets = [building_fleet]

        empire2 = MagicMock()
        empire2.id = 1
        empire2.fleets = [enemy_fleet]

        # Verify both fleets are mapped to the hex
        with patch.object(engine, '_resolve_combat_at_hex') as mock_resolve:
            engine._resolve_conflicts([empire1, empire2])

            mock_resolve.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
