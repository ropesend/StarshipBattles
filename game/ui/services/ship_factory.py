"""
Ship Factory service for UI layer.

PROJ-43: This service provides a facade for Ship creation and configuration,
allowing UI code to work with ships without directly importing from
game.simulation.entities.ship.

The factory encapsulates:
- Ship creation from design data
- Ship property configuration (position, angle, team, etc.)
- Formation setup and linking
- Radius calculation without full ship instantiation
"""
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship


class ShipFactory:
    """Factory for creating and configuring Ship instances.

    This class provides a clean interface for UI code to create ships
    without directly importing the Ship class from the simulation layer.

    Usage:
        factory = ShipFactory()
        ship = factory.create_from_design(design_data)
        factory.configure_ship(ship, position, angle, team_id, ai_strategy, source_file)
    """

    def create_from_design(self, design_data: Dict[str, Any]) -> 'Ship':
        """Create a Ship instance from design dictionary data.

        Args:
            design_data: Dictionary containing ship design data with keys:
                - name: Ship name
                - ship_class: Vehicle class name
                - theme_id: Visual theme identifier
                - color: RGB color tuple
                - layers: Component layer definitions

        Returns:
            A new Ship instance created from the design data.

        Raises:
            KeyError: If required fields are missing from design_data.
            ValueError: If component or modifier IDs are invalid.
        """
        from game.simulation.entities.ship import Ship
        return Ship.from_dict(design_data)

    def get_ship_radius(self, design_data: Dict[str, Any]) -> float:
        """Get the radius a ship would have based on design data.

        Creates a temporary ship from the design and returns its radius
        after recalculating stats. This is useful for formation spacing
        calculations where only the radius is needed.

        Args:
            design_data: Dictionary containing ship design data.

        Returns:
            The calculated radius of the ship in world units.
        """
        from game.simulation.entities.ship import Ship
        temp_ship = Ship.from_dict(design_data)
        temp_ship.recalculate_stats()
        return temp_ship.radius

    def configure_ship(
        self,
        ship: 'Ship',
        position: pygame.math.Vector2,
        angle: float,
        team_id: int,
        ai_strategy: str,
        source_file: str
    ) -> None:
        """Configure ship properties after creation.

        Sets the position, angle, team membership, AI strategy, and
        source file reference for a ship instance.

        Args:
            ship: The Ship instance to configure.
            position: World position as Vector2.
            angle: Facing angle in degrees.
            team_id: Team identifier (0 or 1).
            ai_strategy: AI behavior strategy name.
            source_file: Path to the source design file.
        """
        ship.position = position
        ship.angle = angle
        ship.team_id = team_id
        ship.ai_strategy = ai_strategy
        ship.source_file = source_file

    def setup_formation(
        self,
        ships: List['Ship'],
        formation_data: List[Dict[str, Any]]
    ) -> None:
        """Set up formation links between ships.

        Links follower ships to their formation master based on the
        formation data. The first ship encountered with a given formation_id
        becomes the master; subsequent ships with the same ID become followers.

        Args:
            ships: List of Ship instances to link.
            formation_data: List of dicts with keys:
                - ship_index: Index into ships list
                - formation_id: Formation group identifier
                - rotation_mode: 'relative' or 'fixed'

        The formation offset is calculated as the vector from master to
        follower, rotated into the master's local space for relative mode.
        """
        formation_masters: Dict[str, 'Ship'] = {}

        for entry in formation_data:
            ship_index = entry['ship_index']
            formation_id = entry.get('formation_id')
            rotation_mode = entry.get('rotation_mode', 'relative')

            if formation_id is None:
                continue

            ship = ships[ship_index]

            if formation_id not in formation_masters:
                # First ship with this ID is the master
                formation_masters[formation_id] = ship
            else:
                # Subsequent ships are followers
                master = formation_masters[formation_id]
                ship.formation_master = master
                master.formation_members.append(ship)

                # Calculate offset from master to follower
                diff = ship.position - master.position
                ship.formation_rotation_mode = rotation_mode

                if rotation_mode == 'fixed':
                    ship.formation_offset = diff
                else:
                    # Rotate into master's local space
                    ship.formation_offset = diff.rotate(-master.angle)
