"""
Battle End Conditions System

This module defines configurable end conditions for battle simulations.
Different battle types require different win/loss conditions:

1. TIME_BASED: Run for fixed duration (weapon accuracy tests, statistics)
2. HP_BASED: Traditional combat until one side destroyed (default)
3. CAPABILITY_BASED: Tactical "mission kill" when team can't fight
4. MANUAL: Never end automatically (sandbox testing)

Usage:
    from game.simulation.systems.battle_end_conditions import (
        BattleEndMode, BattleEndCondition
    )

    # Time-based battle (runs for exactly 500 ticks)
    condition = BattleEndCondition(
        mode=BattleEndMode.TIME_BASED,
        max_ticks=500
    )
    engine.start(team1, team2, end_condition=condition)

    # HP-based battle (default, ends when team eliminated)
    condition = BattleEndCondition(mode=BattleEndMode.HP_BASED)
    engine.start(team1, team2, end_condition=condition)

    # Capability-based (ends when team can't fight)
    condition = BattleEndCondition(mode=BattleEndMode.CAPABILITY_BASED)
    engine.start(team1, team2, end_condition=condition)
"""

from enum import Enum
from typing import Optional


class BattleEndMode(Enum):
    """Defines how a battle should end."""

    TIME_BASED = "time_based"          # End after N ticks regardless of status
    HP_BASED = "hp_based"              # End when any team has 0 alive ships (default)
    CAPABILITY_BASED = "capability"    # End when any team can't fight/move
    MANUAL = "manual"                  # Never end automatically


class BattleEndCondition:
    """
    Configuration for battle end conditions.

    Attributes:
        mode: The end condition mode (TIME_BASED, HP_BASED, etc.)
        max_ticks: Maximum ticks for TIME_BASED mode (None = infinite)
        check_derelict: If True, count derelict ships as defeated (for HP_BASED)

    Examples:
        # Accuracy test: Run for exactly 500 ticks
        BattleEndCondition(mode=BattleEndMode.TIME_BASED, max_ticks=500)

        # Standard combat: End when team eliminated
        BattleEndCondition(mode=BattleEndMode.HP_BASED)

        # Tactical: End when team loses bridge/weapons
        BattleEndCondition(
            mode=BattleEndMode.HP_BASED,
            check_derelict=True  # Count derelict as defeated
        )

        # Mission kill: End when team can't fight
        BattleEndCondition(mode=BattleEndMode.CAPABILITY_BASED)

        # Sandbox: Never end
        BattleEndCondition(mode=BattleEndMode.MANUAL)
    """

    def __init__(
        self,
        mode: BattleEndMode = BattleEndMode.HP_BASED,
        max_ticks: Optional[int] = None,
        check_derelict: bool = False
    ):
        """
        Initialize battle end condition.

        Args:
            mode: The end condition mode (default: HP_BASED)
            max_ticks: Maximum ticks for TIME_BASED mode (None = infinite)
            check_derelict: Count derelict ships as defeated (HP_BASED only)
        """
        self.mode = mode
        self.max_ticks = max_ticks
        self.check_derelict = check_derelict

    def __repr__(self) -> str:
        """String representation for debugging."""
        if self.mode == BattleEndMode.TIME_BASED:
            return f"BattleEndCondition(TIME_BASED, max_ticks={self.max_ticks})"
        elif self.mode == BattleEndMode.HP_BASED:
            derelict_str = ", check_derelict=True" if self.check_derelict else ""
            return f"BattleEndCondition(HP_BASED{derelict_str})"
        elif self.mode == BattleEndMode.CAPABILITY_BASED:
            return "BattleEndCondition(CAPABILITY_BASED)"
        else:
            return "BattleEndCondition(MANUAL)"
