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
    OrbitBehavior - Circle around target
    StationaryFireBehavior - Fire without moving (test/debug)
    DoNothingBehavior - No action (test/debug)

Strategy (game.ai.strategy_manager):
    StrategyManager - Resolves AI strategy names to full definitions

Targeting (game.ai.target_evaluator):
    TargetEvaluator - Scores and prioritizes potential targets


Exception Handling
==================

The AI package uses defensive programming for combat robustness:

**Design Philosophy:**
- Combat must not crash due to individual entity errors
- All errors are logged with context for debugging
- Fallback behavior is used when possible

**Exception Types (from game.core.exceptions):**
- StateException: Used for singleton violations

**Logging Patterns:**
- WARNING: Recoverable errors (fallback used)
- DEBUG: Expected conditions (e.g., formation cleanup)
- Errors include entity IDs for traceability

**Fallback Behaviors:**
- Position access failures: Falls back to direct attribute
- Target evaluation failures: Target is skipped
- Missing data: Safe defaults used (e.g., distance = infinity)

Example error handling::

    from game.ai.target_evaluator import TargetEvaluator
    import logging

    logger = logging.getLogger(__name__)

    try:
        score = TargetEvaluator.evaluate(ship, target, rules)
    except (AttributeError, TypeError) as e:
        logger.warning("Evaluation failed for target %s: %s", target.id, e)
        score = -float('inf')  # Skip this target
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
    OrbitBehavior,
    StationaryFireBehavior,
    DoNothingBehavior,
)

# Strategy
from game.ai.strategy_manager import StrategyManager

# Targeting
from game.ai.target_evaluator import TargetEvaluator

# Factory (PROJ-126: moved from simulation layer to fix layer violation)
from game.ai.ai_factory import AIControllerFactory


__all__ = [
    # Controller
    'AIController',
    # Behaviors
    'AIBehavior',
    'KiteBehavior',
    'AttackRunBehavior',
    'RamBehavior',
    'FleeBehavior',
    'OrbitBehavior',
    'StationaryFireBehavior',
    'DoNothingBehavior',
    # Strategy
    'StrategyManager',
    # Targeting
    'TargetEvaluator',
    # Factory
    'AIControllerFactory',
]
