"""
Simulation managers package.

Contains extracted manager classes for specific concerns:
- RetreatManager: Handles retreat and escape mechanics
- BattleStateManager: Handles state serialization
"""

from .retreat_manager import RetreatManager, RetreatState, RetreatMethod
from .battle_state_manager import BattleStateManager

__all__ = ['RetreatManager', 'RetreatState', 'RetreatMethod', 'BattleStateManager']
