"""
AI System - decision-making for autonomous entities.

This package provides AI behaviors and strategy management:
- AIController: Orchestrates ship decision-making
- StrategyManager: Manages combat strategies and policies
- TargetEvaluator: Scores targeting decisions
"""

from .controller import AIController
from .strategy_manager import (
    StrategyManager,
    get_strategy_names,
    reset_strategy_manager,
)
from .target_evaluator import TargetEvaluator

__all__ = [
    'AIController',
    'StrategyManager',
    'TargetEvaluator',
    'get_strategy_names',
    'reset_strategy_manager',
]
