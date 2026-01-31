"""
Battle End Conditions System

This module defines configurable end conditions for battle simulations.
Different battle types require different win/loss conditions:

1. TIME_BASED: Run for fixed duration (weapon accuracy tests, statistics)
2. HP_BASED: Traditional combat until one side destroyed (default)
3. CAPABILITY_BASED: Tactical "mission kill" when team can't fight
4. MANUAL: Never end automatically (sandbox testing)
5. ESCAPE_BASED: End when ships escape beyond a distance threshold

All modes respect an absolute_max_ticks safety ceiling to prevent infinite loops.

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

    # Escape-based (ends when ships exceed distance threshold)
    condition = BattleEndCondition(
        mode=BattleEndMode.ESCAPE_BASED,
        escape_radius=5000.0,
        escape_team=1,  # Only team 1 escaping ends battle
        escape_all_ships=True  # All ships must escape
    )
    engine.start(team1, team2, end_condition=condition)
"""

from enum import Enum
from typing import Optional

from game.core.constants import SimulationConstants


class BattleEndMode(Enum):
    """Defines how a battle should end."""

    TIME_BASED = "time_based"          # End after N ticks regardless of status
    HP_BASED = "hp_based"              # End when any team has 0 alive ships (default)
    CAPABILITY_BASED = "capability"    # End when any team can't fight/move
    MANUAL = "manual"                  # Never end automatically (but respects absolute ceiling)
    ESCAPE_BASED = "escape"            # End when ships exceed escape_radius from center


class BattleEndCondition:
    """
    Configuration for battle end conditions.

    Attributes:
        mode: The end condition mode (TIME_BASED, HP_BASED, etc.)
        max_ticks: Maximum ticks for TIME_BASED mode (None = infinite)
        check_derelict: If True, count derelict ships as defeated (for HP_BASED)
        absolute_max_ticks: Hard ceiling to prevent infinite loops (safety net)
        escape_radius: Distance from origin for ESCAPE_BASED mode
        escape_team: Which team must escape (None = any team, 0 or 1 = specific team)
        escape_all_ships: If True, all ships must escape; if False, any ship escaping counts

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

        # Escape scenario: End when team 1 ships escape beyond 5000 units
        BattleEndCondition(
            mode=BattleEndMode.ESCAPE_BASED,
            escape_radius=5000.0,
            escape_team=1
        )

        # Sandbox: Never end (but still respects absolute_max_ticks)
        BattleEndCondition(mode=BattleEndMode.MANUAL)

        # Custom safety ceiling
        BattleEndCondition(
            mode=BattleEndMode.MANUAL,
            absolute_max_ticks=100_000  # End after 100k ticks instead of 1M
        )
    """

    def __init__(
        self,
        mode: BattleEndMode = BattleEndMode.HP_BASED,
        max_ticks: Optional[int] = None,
        check_derelict: bool = False,
        absolute_max_ticks: Optional[int] = None,
        escape_radius: Optional[float] = None,
        escape_team: Optional[int] = None,
        escape_all_ships: bool = False
    ):
        """
        Initialize battle end condition.

        Args:
            mode: The end condition mode (default: HP_BASED)
            max_ticks: Maximum ticks for TIME_BASED mode (None = infinite)
            check_derelict: Count derelict ships as defeated (HP_BASED only)
            absolute_max_ticks: Hard ceiling for all modes (default: ABSOLUTE_MAX_TICKS)
            escape_radius: Distance threshold for ESCAPE_BASED mode
            escape_team: Which team must escape (None = any, 0 or 1 = specific)
            escape_all_ships: Require all ships to escape (default: False, any ship counts)
        """
        self.mode = mode
        self.max_ticks = max_ticks
        self.check_derelict = check_derelict
        self.absolute_max_ticks = (
            absolute_max_ticks
            if absolute_max_ticks is not None
            else SimulationConstants.ABSOLUTE_MAX_TICKS
        )
        self.escape_radius = escape_radius
        self.escape_team = escape_team
        self.escape_all_ships = escape_all_ships

    def __repr__(self) -> str:
        """String representation for debugging."""
        # Build base representation
        if self.mode == BattleEndMode.TIME_BASED:
            base = f"BattleEndCondition(TIME_BASED, max_ticks={self.max_ticks})"
        elif self.mode == BattleEndMode.HP_BASED:
            derelict_str = ", check_derelict=True" if self.check_derelict else ""
            base = f"BattleEndCondition(HP_BASED{derelict_str})"
        elif self.mode == BattleEndMode.CAPABILITY_BASED:
            base = "BattleEndCondition(CAPABILITY_BASED)"
        elif self.mode == BattleEndMode.ESCAPE_BASED:
            team_str = f", team={self.escape_team}" if self.escape_team is not None else ""
            all_str = ", all_ships=True" if self.escape_all_ships else ""
            base = f"BattleEndCondition(ESCAPE_BASED, radius={self.escape_radius}{team_str}{all_str})"
        else:
            base = "BattleEndCondition(MANUAL)"

        # Add absolute_max_ticks if custom value
        if self.absolute_max_ticks != SimulationConstants.ABSOLUTE_MAX_TICKS:
            base = base[:-1] + f", absolute_max={self.absolute_max_ticks})"

        return base
