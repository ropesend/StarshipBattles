from dataclasses import dataclass
from typing import Optional, Any
from enum import Enum, auto

class CommandType(Enum):
    ISSUE_ORDER = auto()
    # Add other types as needed (e.g., GAME_SETTINGS, CHEAT_CODE)

@dataclass
class Command:
    """Base class for all game commands."""
    type: CommandType
    
    @property
    def name(self) -> str:
        return self.__class__.__name__

@dataclass
class IssueColonizeCommand(Command):
    """Command to issue a colonization order to a fleet."""
    fleet_id: int
    planet_id: Optional[int] # None for 'Any Planet'
    
    def __init__(self, fleet_id: int, planet_id: Optional[int] = None):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id
        self.planet_id = planet_id
