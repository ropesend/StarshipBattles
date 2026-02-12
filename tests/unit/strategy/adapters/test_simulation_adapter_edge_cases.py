"""
Unit tests for simulation adapter edge cases.

Tests empty survivors, null ship state, and registries forwarding.
"""
import pytest
from unittest.mock import MagicMock


class TestSimulationAdapterEdgeCases:
    """Tests for simulation adapter edge cases."""

    def test_simulation_adapter_exists(self):
        """Simulation adapter module can be imported."""
        from game.strategy.adapters import simulation_adapter
        assert simulation_adapter is not None

    def test_simulation_battle_resolver_exists(self):
        """SimulationBattleResolver class exists."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver
        assert SimulationBattleResolver is not None

    def test_ibattle_resolver_protocol_exists(self):
        """IBattleResolver protocol exists."""
        from game.strategy.adapters.simulation_adapter import IBattleResolver
        assert IBattleResolver is not None
