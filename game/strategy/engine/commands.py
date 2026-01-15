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

@dataclass
class IssueMoveCommand(Command):
    """Command to move a fleet to a target hex."""
    fleet_id: int
    target_hex: Any # HexCoord
    
    def __init__(self, fleet_id: int, target_hex: Any):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id
        self.target_hex = target_hex

@dataclass
class IssueBuildShipCommand(Command):
    """Command to build a ship at a colony."""
    planet_id: int
    design_name: str
    
    def __init__(self, planet_id: int, design_name: str):
        self.type = CommandType.ISSUE_ORDER
        self.planet_id = planet_id
        self.design_name = design_name
