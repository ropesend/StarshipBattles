"""
Composable Battle End Conditions System

Protocol-based system for configuring when battles end. Conditions are
composable via AnyCondition (OR) and AllCondition (AND) to support
complex scenarios like "destroy flagship OR time limit reached."

Leaf conditions:
    TickLimitCondition     -- end after N ticks
    TeamEliminatedCondition -- end when a team has 0 alive ships
    TeamIncapacitatedCondition -- end when a team can't fight or move
    EscapeCondition        -- end when ships escape beyond a radius
    ShipDestroyedCondition -- end when a named ship is destroyed
    NeverCondition         -- never end automatically

Composite conditions:
    AnyCondition           -- OR: first child met triggers end
    AllCondition           -- AND: all children must be met

Serialization:
    All conditions support to_dict() / from_dict() with a "type"
    discriminator for JSON persistence. Use end_condition_from_dict()
    to deserialize.

Usage:
    # Standard combat (default)
    cond = TeamEliminatedCondition()

    # Time limit OR team eliminated
    cond = AnyCondition([
        TeamEliminatedCondition(),
        TickLimitCondition(max_ticks=10000),
    ])

    # Flagship must die within time limit
    cond = AllCondition([
        ShipDestroyedCondition(ship_name="Boss Ship"),
        TickLimitCondition(max_ticks=5000),
    ])

    # Escape scenario
    cond = EscapeCondition(
        escape_radius=5000.0,
        arena_center=(500.0, 500.0),
        escape_team=1,
    )

    engine.start(team1, team2, end_condition=cond)
"""
import logging
from typing import Any, Dict, List, Optional, Protocol, Tuple, runtime_checkable, TYPE_CHECKING

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship

logger = logging.getLogger(__name__)


# ============================================================================
# Protocol
# ============================================================================

@runtime_checkable
class IEndCondition(Protocol):
    """Protocol for battle end conditions.

    All end conditions must implement:
    - is_met(ships, tick) -> bool: Check if the condition is satisfied
    - to_dict() -> dict: Serialize for persistence
    - description (property): Human-readable summary
    """

    def is_met(self, ships: List['Ship'], tick: int) -> bool:
        """Return True if the battle should end."""
        ...

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary with 'type' discriminator."""
        ...

    @property
    def description(self) -> str:
        """Human-readable description for UI/logging."""
        ...


# ============================================================================
# Leaf Conditions
# ============================================================================

class TickLimitCondition:
    """End battle after a fixed number of ticks."""

    def __init__(self, max_ticks: int):
        self.max_ticks = max_ticks

    def is_met(self, ships: List['Ship'], tick: int) -> bool:
        return tick >= self.max_ticks

    def to_dict(self) -> Dict[str, Any]:
        return {"type": "tick_limit", "max_ticks": self.max_ticks}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TickLimitCondition':
        return cls(max_ticks=data["max_ticks"])

    @property
    def description(self) -> str:
        return f"End after {self.max_ticks:,} ticks"

    def __repr__(self) -> str:
        return f"TickLimitCondition(max_ticks={self.max_ticks})"


class TeamEliminatedCondition:
    """End battle when any team has 0 alive ships.

    Args:
        check_derelict: If True, derelict ships count as eliminated.
    """

    def __init__(self, check_derelict: bool = False):
        self.check_derelict = check_derelict

    def is_met(self, ships: List['Ship'], tick: int) -> bool:
        if not ships:
            return False

        team_ids = {s.team_id for s in ships}
        for team_id in team_ids:
            alive = sum(
                1 for s in ships
                if s.team_id == team_id and s.is_alive
                and (not self.check_derelict or not s.is_derelict)
            )
            if alive == 0:
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "team_eliminated",
            "check_derelict": self.check_derelict,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TeamEliminatedCondition':
        return cls(check_derelict=data.get("check_derelict", False))

    @property
    def description(self) -> str:
        suffix = " (derelict = eliminated)" if self.check_derelict else ""
        return f"End when a team is eliminated{suffix}"

    def __repr__(self) -> str:
        d = ", check_derelict=True" if self.check_derelict else ""
        return f"TeamEliminatedCondition({d.lstrip(', ')})"


class TeamIncapacitatedCondition:
    """End battle when any team loses combat capability.

    A team is incapacitated when no alive ship on that team has
    operational weapons OR movement capability.
    """

    def is_met(self, ships: List['Ship'], tick: int) -> bool:
        if not ships:
            return False

        team_ids = {s.team_id for s in ships}
        for team_id in team_ids:
            if not self._team_has_capability(ships, team_id):
                return True
        return False

    @staticmethod
    def _team_has_capability(ships: List['Ship'], team_id: int) -> bool:
        """Check if team has any ships that can fight or move."""
        for ship in ships:
            if ship.team_id != team_id or not ship.is_alive:
                continue

            has_weapons = any(
                comp.is_operational and comp.type == "Weapon"
                for comp in ship.get_all_components()
            )
            has_engines = ship.total_thrust > 0
            has_thrusters = ship.turn_speed > 0

            if has_weapons or has_engines or has_thrusters:
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {"type": "team_incapacitated"}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TeamIncapacitatedCondition':
        return cls()

    @property
    def description(self) -> str:
        return "End when a team loses combat capability"

    def __repr__(self) -> str:
        return "TeamIncapacitatedCondition()"


class EscapeCondition:
    """End battle when ships escape beyond a radius from arena center.

    Args:
        escape_radius: Distance threshold from arena_center.
        arena_center: Center point for distance measurement (default origin).
        escape_team: Only check this team (None = any team).
        escape_all_ships: If True, ALL alive ships must escape. If False, ANY ship counts.
    """

    def __init__(
        self,
        escape_radius: float,
        arena_center: Tuple[float, float] = (0.0, 0.0),
        escape_team: Optional[int] = None,
        escape_all_ships: bool = False,
    ):
        self.escape_radius = escape_radius
        self.arena_center = arena_center
        self.escape_team = escape_team
        self.escape_all_ships = escape_all_ships

    def is_met(self, ships: List['Ship'], tick: int) -> bool:
        cx, cy = self.arena_center

        ships_to_check = [
            s for s in ships
            if s.is_alive and (self.escape_team is None or s.team_id == self.escape_team)
        ]

        if not ships_to_check:
            return False

        def _is_outside(s: 'Ship') -> bool:
            dx = s.position.x - cx
            dy = s.position.y - cy
            return (dx * dx + dy * dy) > self.escape_radius * self.escape_radius

        if self.escape_all_ships:
            return all(_is_outside(s) for s in ships_to_check)
        else:
            return any(_is_outside(s) for s in ships_to_check)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "escape",
            "escape_radius": self.escape_radius,
            "arena_center": list(self.arena_center),
            "escape_team": self.escape_team,
            "escape_all_ships": self.escape_all_ships,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EscapeCondition':
        center = data.get("arena_center", [0.0, 0.0])
        return cls(
            escape_radius=data["escape_radius"],
            arena_center=tuple(center),
            escape_team=data.get("escape_team"),
            escape_all_ships=data.get("escape_all_ships", False),
        )

    @property
    def description(self) -> str:
        team_str = f" (team {self.escape_team})" if self.escape_team is not None else ""
        all_str = " (all ships)" if self.escape_all_ships else ""
        return f"End when ships{team_str} escape beyond {self.escape_radius:.0f}{all_str}"

    def __repr__(self) -> str:
        return (
            f"EscapeCondition(radius={self.escape_radius}, "
            f"center={self.arena_center}, team={self.escape_team}, "
            f"all_ships={self.escape_all_ships})"
        )


class ShipDestroyedCondition:
    """End battle when a named ship is destroyed.

    Uses ship name (case-sensitive) for matching. If the named ship is
    not found in the battle, the condition is never met.
    """

    def __init__(self, ship_name: str):
        self.ship_name = ship_name

    def is_met(self, ships: List['Ship'], tick: int) -> bool:
        return any(
            s.name == self.ship_name and not s.is_alive
            for s in ships
        )

    def to_dict(self) -> Dict[str, Any]:
        return {"type": "ship_destroyed", "ship_name": self.ship_name}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ShipDestroyedCondition':
        return cls(ship_name=data["ship_name"])

    @property
    def description(self) -> str:
        return f"End when '{self.ship_name}' is destroyed"

    def __repr__(self) -> str:
        return f"ShipDestroyedCondition(ship_name='{self.ship_name}')"


class NeverCondition:
    """Never end the battle automatically.

    Used for sandbox/manual testing. The safety ceiling on BattleEngine
    still applies.
    """

    def is_met(self, ships: List['Ship'], tick: int) -> bool:
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {"type": "never"}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NeverCondition':
        return cls()

    @property
    def description(self) -> str:
        return "Never end automatically"

    def __repr__(self) -> str:
        return "NeverCondition()"


# ============================================================================
# Composite Conditions
# ============================================================================

class AnyCondition:
    """OR composite: met when ANY child condition is met."""

    def __init__(self, conditions: List[IEndCondition]):
        self.conditions = list(conditions)

    def is_met(self, ships: List['Ship'], tick: int) -> bool:
        return any(c.is_met(ships, tick) for c in self.conditions)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "any",
            "conditions": [c.to_dict() for c in self.conditions],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnyCondition':
        children = [end_condition_from_dict(d) for d in data["conditions"]]
        return cls(conditions=children)

    @property
    def description(self) -> str:
        if not self.conditions:
            return "No conditions (never met)"
        parts = [c.description for c in self.conditions]
        return " OR ".join(parts)

    def __repr__(self) -> str:
        return f"AnyCondition({self.conditions!r})"


class AllCondition:
    """AND composite: met when ALL child conditions are met."""

    def __init__(self, conditions: List[IEndCondition]):
        self.conditions = list(conditions)

    def is_met(self, ships: List['Ship'], tick: int) -> bool:
        return all(c.is_met(ships, tick) for c in self.conditions)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "all",
            "conditions": [c.to_dict() for c in self.conditions],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AllCondition':
        children = [end_condition_from_dict(d) for d in data["conditions"]]
        return cls(conditions=children)

    @property
    def description(self) -> str:
        if not self.conditions:
            return "No conditions (always met)"
        parts = [c.description for c in self.conditions]
        return " AND ".join(parts)

    def __repr__(self) -> str:
        return f"AllCondition({self.conditions!r})"


# ============================================================================
# Deserialization Factory
# ============================================================================

_CONDITION_TYPES: Dict[str, type] = {
    "tick_limit": TickLimitCondition,
    "team_eliminated": TeamEliminatedCondition,
    "team_incapacitated": TeamIncapacitatedCondition,
    "escape": EscapeCondition,
    "ship_destroyed": ShipDestroyedCondition,
    "never": NeverCondition,
    "any": AnyCondition,
    "all": AllCondition,
}


def end_condition_from_dict(data: Dict[str, Any]) -> IEndCondition:
    """Deserialize an end condition from a dictionary.

    Args:
        data: Dictionary with 'type' discriminator and condition-specific fields.

    Returns:
        An IEndCondition instance.

    Raises:
        KeyError: If 'type' is missing or unknown.
    """
    condition_type = data["type"]
    cls = _CONDITION_TYPES[condition_type]
    return cls.from_dict(data)
