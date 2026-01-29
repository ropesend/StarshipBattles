"""
AI package for Starship Battles.

Provides autonomous ship control, targeting, and movement behaviors for combat.

Public API
==========

Controller (game.ai.controller):
    AIController - Main AI decision-making controller for ships

Behaviors (game.ai.behaviors):
    AIBehavior - Base behavior class
    KiteBehavior - Maintain optimal weapon range
    AttackRunBehavior - Hit-and-run tactics
    RamBehavior - Direct collision course
    FleeBehavior - Retreat from combat
    FormationBehavior - Follow formation master
    OrbitBehavior - Circle around target
    StationaryFireBehavior - Fire without moving (test/debug)
    DoNothingBehavior - No action (test/debug)

Strategy (game.ai.strategy_manager):
    StrategyManager - Resolves AI strategy names to full definitions

Targeting (game.ai.target_evaluator):
    TargetEvaluator - Scores and prioritizes potential targets
"""

# Controller
from game.ai.controller import AIController

# Behaviors
from game.ai.behaviors import (
    AIBehavior,
    KiteBehavior,
    AttackRunBehavior,
    RamBehavior,
    FleeBehavior,
    FormationBehavior,
    OrbitBehavior,
    StationaryFireBehavior,
    DoNothingBehavior,
)

# Strategy
from game.ai.strategy_manager import StrategyManager

# Targeting
from game.ai.target_evaluator import TargetEvaluator


__all__ = [
    # Controller
    'AIController',
    # Behaviors
    'AIBehavior',
    'KiteBehavior',
    'AttackRunBehavior',
    'RamBehavior',
    'FleeBehavior',
    'FormationBehavior',
    'OrbitBehavior',
    'StationaryFireBehavior',
    'DoNothingBehavior',
    # Strategy
    'StrategyManager',
    # Targeting
    'TargetEvaluator',
]
