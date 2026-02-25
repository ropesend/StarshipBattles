"""
CargoTransferService - Shared business logic for cargo transfer operations.

Extracts colony resolution, population extraction, and transfer command assembly
from UI dialogs (CargoQuickDialog, TransferDialog) into a testable service.

PROJ-162: Extract CargoTransferService from UI Dialogs
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING, Union

from game.strategy.engine.commands import IssueTransferCommand

if TYPE_CHECKING:
    from game.core.hex_math import HexCoord
    from game.strategy.facade.dto.fleet_dto import FleetInfo
    from game.strategy.facade.dto.planet_dto import PlanetInfo
    from game.strategy.data.fleet import Fleet


class CargoTransferService:
    """Service for cargo transfer business logic.

    Provides static methods for:
    - Resolving colonies at a hex (with fleet location fallback)
    - Extracting unload/load items from fleets and colonies
    - Building transfer commands with engine conventions
    """

    @staticmethod
    def resolve_colonies(facade, hex_coord: 'HexCoord', fleet: 'Fleet') -> List['PlanetInfo']:
        """Resolve colonies at a hex, with fallback to fleet location.

        Args:
            facade: Strategy facade for planet lookup
            hex_coord: Primary hex coordinate to check
            fleet: Fleet object (used for location fallback)

        Returns:
            List of PlanetInfo objects that are colonized (owner_id not None)
        """
        planets = facade.get_planets_at_hex(hex_coord)

        # Fallback: if no planets at clicked hex, try fleet's location
        # This handles relative hex from system view
        if not planets and hasattr(fleet, 'location') and fleet.location:
            planets = facade.get_planets_at_hex(fleet.location)

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

        fleet_info = facade.get_fleet(fleet_id)
        if not fleet_info:
            return items

        # Get fleet passengers
        passengers = getattr(fleet_info, 'passengers_current', 0)
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
            planet_info = facade.get_planet(colony.planet_id)
            if not planet_info:
                continue

            # Population details: tuple of (race_id, count, happiness)
            if hasattr(planet_info, 'population_details') and planet_info.population_details:
                for race_id, count, happiness in planet_info.population_details:
                    if count > 0:
                        items.append({
                            'label': f"{colony.name}: {race_id} ({count})",
                            'cargo_type': 'passengers',
                            'species_id': race_id,
                            'max_amount': count,
                            'planet_id': colony.planet_id
                        })
            else:
                # Fallback to total_population
                pop = getattr(planet_info, 'total_population', 0)
                if pop > 0:
                    items.append({
                        'label': f"{colony.name}: Population ({pop})",
                        'cargo_type': 'passengers',
                        'species_id': None,
                        'max_amount': pop,
                        'planet_id': colony.planet_id
                    })

        return items

    @staticmethod
    def get_inventory_items(obj_info: Union['FleetInfo', 'PlanetInfo', None]) -> List[Dict[str, Any]]:
        """Extract inventory items from a fleet or planet object via duck typing.

        Args:
            obj_info: A fleet info or planet info object

        Returns:
            List of item dicts with keys: label, cargo_type, species_id, max_amount
        """
        items = []
        if not obj_info:
            return items

        # Fleet: has passengers_current
        if hasattr(obj_info, 'passengers_current'):
            passengers = getattr(obj_info, 'passengers_current', 0)
            if passengers > 0:
                items.append({
                    'label': f"Passengers ({passengers})",
                    'cargo_type': 'passengers',
                    'species_id': None,
                    'max_amount': passengers
                })
        # Colony/Planet: has population_details
        elif hasattr(obj_info, 'population_details') and obj_info.population_details:
            for race_id, count, happiness in obj_info.population_details:
                if count > 0:
                    items.append({
                        'label': f"Population: {race_id} ({count})",
                        'cargo_type': 'passengers',
                        'species_id': race_id,
                        'max_amount': count
                    })
        # Planet fallback: has total_population
        elif hasattr(obj_info, 'total_population'):
            passengers = getattr(obj_info, 'total_population', 0)
            if passengers > 0:
                items.append({
                    'label': f"Population ({passengers})",
                    'cargo_type': 'passengers',
                    'species_id': None,
                    'max_amount': passengers
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
    ) -> IssueTransferCommand:
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

        return IssueTransferCommand(
            fleet_id=fleet_id,
            planet_id=planet_id,
            cargo_type=cargo_type,
            direction=direction,
            amount=amount,
            species_id=species_id
        )
