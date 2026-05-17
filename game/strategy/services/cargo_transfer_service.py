"""
CargoTransferService - Shared business logic for cargo transfer operations.

Extracts colony resolution, population extraction, and transfer command assembly
from UI dialogs (CargoQuickDialog, TransferDialog) into a testable service.

PROJ-162: Extract CargoTransferService from UI Dialogs
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING, Union

from game.strategy.data.order_types import OrderType
from game.strategy.engine.commands.order_metadata_view import order_metadata

if TYPE_CHECKING:
    from game.strategy.engine.commands import IssueTransferCommand
    from game.core.hex_math import HexCoord
    from game.strategy.facade.dto.fleet_dto import FleetInfo
    from game.strategy.facade.dto.planet_dto import PlanetInfo
    from game.strategy.data.fleet import Fleet


def project_fleet_position(fleet: 'Fleet') -> 'HexCoord':
    """Project where a fleet will be after executing all queued orders.

    Walks the order queue and tracks MOVE/WARP destinations. Returns the
    last movement destination, or the fleet's current location if no
    movement orders are queued.

    Args:
        fleet: Fleet with .location and .orders attributes.

    Returns:
        HexCoord of the fleet's projected position.
    """
    position = fleet.location
    for order in fleet.orders:
        if order.type in order_metadata.movement_order_types and order.type != OrderType.MOVE_TO_FLEET:
            from game.core.hex_math import HexCoord
            if isinstance(order.target, HexCoord):
                position = order.target
    return position


def _extract_population_items(
    planet_info,
    label_fn=None,
    planet_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Extract population items from a PlanetInfo object.

    Shared logic for get_load_items (colony->fleet) and
    get_inventory_items (planet inventory display).

    Args:
        planet_info: PlanetInfo with population_details and total_population.
        label_fn: Optional callable(race_id, count) -> str for custom labels.
                 Defaults to "Population: {race_id} ({count})".
        planet_id: Optional planet ID to include in item dicts.

    Returns:
        List of item dicts.
    """
    items = []
    if not planet_info:
        return items

    if planet_info.population_details:
        for race_id, count, happiness in planet_info.population_details:
            if count > 0:
                label = label_fn(race_id, count) if label_fn else f"Population: {race_id} ({count})"
                item = {
                    'label': label,
                    'cargo_type': 'passengers',
                    'species_id': race_id,
                    'max_amount': count,
                }
                if planet_id is not None:
                    item['planet_id'] = planet_id
                items.append(item)
    else:
        pop = planet_info.total_population
        if pop > 0:
            label = label_fn(None, pop) if label_fn else f"Population ({pop})"
            item = {
                'label': label,
                'cargo_type': 'passengers',
                'species_id': None,
                'max_amount': pop,
            }
            if planet_id is not None:
                item['planet_id'] = planet_id
            items.append(item)

    return items


class CargoTransferService:
    """Service for cargo transfer business logic.

    Provides static methods for:
    - Resolving colonies at a hex (with fleet location fallback)
    - Extracting unload/load items from fleets and colonies
    - Building transfer commands with engine conventions
    """

    @staticmethod
    def resolve_colonies(facade, hex_coord: 'HexCoord', fleet: 'Fleet') -> List['PlanetInfo']:
        """Resolve colonies at a hex, with fallback to fleet location and projected position.

        Tries in order:
        1. Primary hex (the explicitly specified location)
        2. Fleet's current location (handles relative hex from system view)
        3. Fleet's projected position after queued MOVE/WARP orders

        Args:
            facade: Strategy facade for planet lookup
            hex_coord: Primary hex coordinate to check
            fleet: Fleet object (used for location and order-queue fallback)

        Returns:
            List of PlanetInfo objects that are colonized (owner_id not None)
        """
        planets = facade.planets.at_hex(hex_coord)

        # Fallback 1: if no planets at clicked hex, try fleet's current location
        if not planets and fleet.location:
            planets = facade.planets.at_hex(fleet.location)

        # Fallback 2: try fleet's projected position from queued orders
        if not planets:
            projected = project_fleet_position(fleet)
            if projected != fleet.location:
                planets = facade.planets.at_hex(projected)

        # Filter to only colonized planets
        colonies = [p for p in planets if p.owner_id is not None]
        return colonies

    @staticmethod
    def get_unload_items(facade, fleet_id: int, colonies: List['PlanetInfo']) -> List[Dict[str, Any]]:
        """Get items that can be unloaded (dropped) from a fleet.

        Args:
            facade: Strategy facade for fleet lookup
            fleet_id: ID of the fleet to get cargo from
            colonies: List of colonies at the target location

        Returns:
            List of item dicts with keys: label, cargo_type, species_id, max_amount
        """
        items = []

        if not colonies:
            # No colony to unload to
            return items

        fleet_info = facade.fleets.get(fleet_id)
        if not fleet_info:
            return items

        # Get fleet passengers (FleetInfo always has passengers_current, default 0)
        passengers = fleet_info.passengers_current
        if passengers > 0:
            items.append({
                'label': f"Passengers ({passengers})",
                'cargo_type': 'passengers',
                'species_id': None,
                'max_amount': passengers
            })

        return items

    @staticmethod
    def get_load_items(facade, colonies: List['PlanetInfo']) -> List[Dict[str, Any]]:
        """Get items that can be loaded from colonies.

        Args:
            facade: Strategy facade for planet lookup
            colonies: List of colonies to get population from

        Returns:
            List of item dicts with keys: label, cargo_type, species_id, max_amount, planet_id
        """
        items = []

        for colony in colonies:
            planet_info = facade.planets.get(colony.planet_id)
            if not planet_info:
                continue

            def _label(race_id, count, _name=colony.name) -> str:
                if race_id:
                    return f"{_name}: {race_id} ({count})"
                return f"{_name}: Population ({count})"

            items.extend(_extract_population_items(
                planet_info, label_fn=_label, planet_id=colony.planet_id
            ))

        return items

    @staticmethod
    def get_inventory_items(obj_info: Union['FleetInfo', 'PlanetInfo', None]) -> List[Dict[str, Any]]:
        """Extract inventory items from a fleet or planet info object.

        Args:
            obj_info: A FleetInfo or PlanetInfo object

        Returns:
            List of item dicts with keys: label, cargo_type, species_id, max_amount
        """
        # Import here to avoid circular imports at module level
        from game.strategy.facade.dto.fleet_dto import FleetInfo
        from game.strategy.facade.dto.planet_dto import PlanetInfo

        items = []
        if not obj_info:
            return items

        # FleetInfo: passengers + cargo resources
        if isinstance(obj_info, FleetInfo):
            passengers = obj_info.passengers_current
            if passengers > 0:
                items.append({
                    'label': f"Passengers ({passengers})",
                    'cargo_type': 'passengers',
                    'species_id': None,
                    'max_amount': passengers
                })
            # Add all resource cargo types (show even if empty, per user preference)
            cap_map = dict(getattr(obj_info, 'cargo_capacities', ()))
            for res_type, amount in getattr(obj_info, 'cargo_resources', ()):
                capacity = cap_map.get(res_type, 0)
                if capacity > 0 or amount > 0:
                    display_name = res_type.capitalize()
                    items.append({
                        'label': f"{display_name} ({amount})",
                        'cargo_type': res_type,
                        'species_id': None,
                        'max_amount': amount,
                    })

        # PlanetInfo: population + stockpile resources
        elif isinstance(obj_info, PlanetInfo):
            items.extend(_extract_population_items(obj_info))
            # Add stockpile resources
            for res_type, amount in getattr(obj_info, 'stockpile', ()):
                if amount > 0:
                    display_name = res_type.capitalize()
                    items.append({
                        'label': f"{display_name} ({int(amount)})",
                        'cargo_type': res_type,
                        'species_id': None,
                        'max_amount': int(amount),
                    })

        return items

    @staticmethod
    def build_transfer_command(
        fleet_id: int,
        planet_id: int,
        cargo_type: str,
        direction: str,
        amount: int,
        max_amount: int,
        species_id: Optional[str] = None
    ) -> 'IssueTransferCommand':
        """Build a transfer command with engine conventions.

        Args:
            fleet_id: The fleet to transfer cargo to/from
            planet_id: The planet/colony to transfer cargo to/from
            cargo_type: Type of cargo (e.g., 'passengers')
            direction: 'load' or 'unload'
            amount: Units to transfer
            max_amount: Maximum available amount
            species_id: Optional species ID for population transfers

        Returns:
            IssueTransferCommand instance

        Note:
            Engine convention: amount=0 means "transfer all available"
            So if amount >= max_amount, we set amount to 0
        """
        # Engine convention: 0 means "all"
        if amount >= max_amount:
            amount = 0

        # PROJ-239: Late import to avoid services/→engine/ top-level dependency
        from game.strategy.engine.commands import IssueTransferCommand
        return IssueTransferCommand(
            fleet_id=fleet_id,
            planet_id=planet_id,
            cargo_type=cargo_type,
            direction=direction,
            amount=amount,
            species_id=species_id
        )
