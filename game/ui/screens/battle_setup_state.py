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
from game.core.validation_helpers import require_keys
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
        # Materialized list of toggled-on complexes (spec-compiler input).
        # Rebuilt from `*_complex_toggles` at battle-launch time.
        self.system_complexes: List[Dict[str, Any]] = []
        self.sector_complexes: List[Dict[str, Any]] = []
        # PROJ-282 Phase 2: per-side source-of-truth for complex toggle UI
        # state. Replaces the old screen-level `_complex_toggles` dict.
        # Keyed by design_id; value is the on/off boolean (off entries are
        # retained so the UI can render the [  ] checkbox state explicitly).
        self.system_complex_toggles: Dict[str, bool] = {}
        self.sector_complex_toggles: Dict[str, bool] = {}

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
            "system_complex_toggles": dict(self.system_complex_toggles),
            "sector_complex_toggles": dict(self.sector_complex_toggles),
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
        registries: Optional['GameRegistries'] = None,
    ) -> 'BattleSetupSide':
        """Deserialize from save/load.

        Requires the canonical PROJ-282 Phase 2 shape: both
        `system_complex_toggles` and `sector_complex_toggles` keys must
        be present. Missing keys raise `PersistenceException`.
        """
        require_keys(
            data,
            ['system_complex_toggles', 'sector_complex_toggles'],
            'BattleSetupSide',
        )
        side = cls(team_id=data.get("team_id", 0))

        for fleet_entry in data.get("fleets", []):
            fleet_data = fleet_entry.get("fleet", {})
            fleet = Fleet.from_dict(fleet_data, registries=registries)
            fleet._battle_setup_name = fleet_entry.get("name", f"Fleet {fleet.id}")
            side.fleets.append(fleet)

        side.system_complexes = data.get("system_complexes", [])
        side.sector_complexes = data.get("sector_complexes", [])
        side.system_complex_toggles = dict(data["system_complex_toggles"])
        side.sector_complex_toggles = dict(data["sector_complex_toggles"])
        return side


MIN_SIDES = 2
MAX_SIDES = 8


class BattleSetupState:
    """Complete state for a fleet-based battle setup.

    PROJ-275 Phase 4+5: migrated from fixed `side_0` / `side_1` attributes
    to a dynamic `sides: List[BattleSetupSide]` (min 2, max 8). The
    `side_0` / `side_1` properties remain as backwards-compat shims that
    read/write `sides[0]` / `sides[1]` — some callers use those names and
    will be migrated incrementally.

    Holds N sides (team 0..N-1), each with fleets and complex
    selections. Provides methods for adding ships, add/remove sides,
    serialization, and conversion to battle-ready Ship objects.
    """

    def __init__(self, side_count: int = 2):
        if side_count < MIN_SIDES or side_count > MAX_SIDES:
            raise ValueError(
                f"BattleSetupState side_count must be in "
                f"[{MIN_SIDES}, {MAX_SIDES}]; got {side_count}"
            )
        self.sides: List[BattleSetupSide] = [
            BattleSetupSide(team_id=i) for i in range(side_count)
        ]

    # --- Backcompat shims for side_0 / side_1 --------------------------------
    # Existing callers (battle_setup_screen.py, some tests) reference
    # `state.side_0` / `state.side_1` directly. The properties route to
    # `sides[0]` / `sides[1]`. Writing `state.side_0 = ...` updates the
    # same slot — preserves legacy behavior for tests that assign.

    @property
    def side_0(self) -> BattleSetupSide:
        return self.sides[0]

    @side_0.setter
    def side_0(self, value: BattleSetupSide) -> None:
        self.sides[0] = value

    @property
    def side_1(self) -> BattleSetupSide:
        return self.sides[1]

    @side_1.setter
    def side_1(self, value: BattleSetupSide) -> None:
        self.sides[1] = value

    # --- N-side API ----------------------------------------------------------

    def get_side(self, team_id: int) -> BattleSetupSide:
        """Get the side for a team ID."""
        return self.sides[team_id]

    def add_side(self) -> BattleSetupSide:
        """Append a new empty side and return it.

        Raises:
            ValueError: if the state is already at MAX_SIDES.
        """
        if len(self.sides) >= MAX_SIDES:
            raise ValueError(
                f"BattleSetupState: cannot add more than {MAX_SIDES} sides"
            )
        new_side = BattleSetupSide(team_id=len(self.sides))
        self.sides.append(new_side)
        return new_side

    def remove_side(self, index: int) -> None:
        """Remove the side at the given index; subsequent team_ids shift down.

        Raises:
            ValueError: if removing would drop below MIN_SIDES.
            IndexError: if `index` is out of range.
        """
        if len(self.sides) <= MIN_SIDES:
            raise ValueError(
                f"BattleSetupState: cannot remove; already at minimum of {MIN_SIDES} sides"
            )
        if index < 0 or index >= len(self.sides):
            raise IndexError(f"BattleSetupState: side index {index} out of range")
        del self.sides[index]
        # Renumber remaining team_ids so they stay contiguous [0..N-1].
        for new_id, side in enumerate(self.sides):
            side.team_id = new_id

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
        """Reset to empty 2-side state."""
        self.sides = [
            BattleSetupSide(team_id=0),
            BattleSetupSide(team_id=1),
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the full setup for save/load.

        PROJ-275: writes `sides: [side0_dict, side1_dict, ...]`.
        """
        return {"sides": [side.to_dict() for side in self.sides]}

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
        registries: Optional['GameRegistries'] = None,
    ) -> 'BattleSetupState':
        """Deserialize from save/load. Requires the N-side `sides` list."""
        sides_raw = data["sides"]
        count = max(MIN_SIDES, min(MAX_SIDES, len(sides_raw)))
        state = cls(side_count=count)
        for i, side_data in enumerate(sides_raw[:count]):
            state.sides[i] = BattleSetupSide.from_dict(
                side_data, registries=registries
            )
        return state
