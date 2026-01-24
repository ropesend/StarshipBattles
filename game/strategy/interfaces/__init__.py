"""
Strategy layer interfaces for clean dependency management.

PROJ-11 Phase 4: Defines explicit interfaces between layers.
This allows the strategy layer to depend on abstractions rather than
concrete simulation implementations.
"""

from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

__all__ = ['IBattleResolver', 'BattleResult']
