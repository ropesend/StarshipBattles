"""
Strategy layer adapters.

PROJ-11 Phase 4: Adapters that bridge strategy layer interfaces
to concrete implementations in other layers.
"""

from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

__all__ = ['SimulationBattleResolver']
