"""
BattleSetupState — data model for the fleet-based battle setup.

Holds the complete state for a battle setup: two sides, each with
multiple fleets (real Fleet objects with full hierarchy support),
system-scope complex selections, and sector-scope complex selections.
"""

import logging
import uuid
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.ship_instance import ShipInstance

if TYPE_CHECKING:
    from game.core.registry import GameRegistries

logger = logging.getLogger(__name__)

# Counter for generating unique fleet IDs
_next_fleet_id = 1000


def _generate_fleet_id() -> int:
    """Generate a unique fleet ID for battle setup fleets."""
    global _next_fleet_id
    _next_fleet_id += 1
    return _next_fleet_id


class BattleSetupSide:
    """One side of a battle setup.

    Holds multiple fleets and complex selections for a team (0 or 1).
    """

    def __init__(self, team_id: int):
        self.team_id = team_id
        self.fleets: List[Fleet] = []
        self.system_complexes: List[Dict[str, Any]] = []  # Toggled system-scope complex designs
        self.sector_complexes: List[Dict[str, Any]] = []  # Toggled sector-scope complex designs

    def create_fleet(self, name: str = "New Fleet") -> Fleet:
        """Create a new empty fleet and add it to this side.

        Args:
            name: Display name for the fleet.

        Returns:
            The newly created Fleet.
        """
        fleet_id = _generate_fleet_id()
        fleet = Fleet(fleet_id, self.team_id, HexCoord(0, 0))
        # Store the display name on the fleet for UI purposes
        fleet._battle_setup_name = name
        self.fleets.append(fleet)
        return fleet

    def add_fleet(self, fleet: Fleet) -> None:
        """Add an existing fleet to this side."""
        if fleet not in self.fleets:
            self.fleets.append(fleet)

    def remove_fleet(self, fleet: Fleet) -> bool:
        """Remove a fleet from this side. Returns True if found."""
        if fleet in self.fleets:
            self.fleets.remove(fleet)
            return True
        return False

    @property
    def all_ships(self) -> List[ShipInstance]:
        """All ships across all fleets on this side."""
        ships = []
        for fleet in self.fleets:
            ships.extend(fleet.ships)
        return ships

    @property
    def ship_count(self) -> int:
        """Total number of ships across all fleets."""
        return sum(len(f.ships) for f in self.fleets)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for save/load."""
        return {
            "team_id": self.team_id,
            "fleets": [
                {
                    "fleet": f.to_dict(),
                    "name": getattr(f, '_battle_setup_name', f"Fleet {f.id}"),
                }
                for f in self.fleets
            ],
            "system_complexes": list(self.system_complexes),
            "sector_complexes": list(self.sector_complexes),
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
        registries: Optional['GameRegistries'] = None,
    ) -> 'BattleSetupSide':
        """Deserialize from save/load."""
        side = cls(team_id=data.get("team_id", 0))

        for fleet_entry in data.get("fleets", []):
            fleet_data = fleet_entry.get("fleet", {})
            fleet = Fleet.from_dict(fleet_data, registries=registries)
            fleet._battle_setup_name = fleet_entry.get("name", f"Fleet {fleet.id}")
            side.fleets.append(fleet)

        side.system_complexes = data.get("system_complexes", [])
        side.sector_complexes = data.get("sector_complexes", [])
        return side


class BattleSetupState:
    """Complete state for a fleet-based battle setup.

    Holds two sides (team 0 and team 1), each with fleets and complex
    selections. Provides methods for adding ships, serialization, and
    conversion to battle-ready Ship objects.
    """

    def __init__(self):
        self.side_0 = BattleSetupSide(team_id=0)
        self.side_1 = BattleSetupSide(team_id=1)

    def get_side(self, team_id: int) -> BattleSetupSide:
        """Get the side for a team ID."""
        return self.side_0 if team_id == 0 else self.side_1

    def add_ship_from_design(
        self,
        fleet: Fleet,
        design_data: Dict[str, Any],
        registries: Optional['GameRegistries'] = None,
        name: Optional[str] = None,
    ) -> ShipInstance:
        """Create a ShipInstance from design data and add it to a fleet.

        Args:
            fleet: The fleet to add the ship to.
            design_data: Ship design dictionary.
            registries: GameRegistries for stats calculation.
            name: Optional override name.

        Returns:
            The newly created ShipInstance.
        """
        ship = ShipInstance.create(
            design_data=design_data,
            owner_id=fleet.owner_id,
            name=name,
            registries=registries,
        )
        fleet.add_ship(ship)
        return ship

    def clear(self) -> None:
        """Reset to empty state."""
        self.side_0 = BattleSetupSide(team_id=0)
        self.side_1 = BattleSetupSide(team_id=1)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the full setup for save/load."""
        return {
            "side_0": self.side_0.to_dict(),
            "side_1": self.side_1.to_dict(),
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
        registries: Optional['GameRegistries'] = None,
    ) -> 'BattleSetupState':
        """Deserialize from save/load."""
        state = cls()
        if "side_0" in data:
            state.side_0 = BattleSetupSide.from_dict(data["side_0"], registries=registries)
        if "side_1" in data:
            state.side_1 = BattleSetupSide.from_dict(data["side_1"], registries=registries)
        return state
