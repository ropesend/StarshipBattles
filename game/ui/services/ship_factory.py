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

PROJ-50: Supports optional registries parameter for strict DI compliance.
When registries is not provided, uses global RegistryManager (legacy behavior).
"""
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

from game.core.math import Vector2

if TYPE_CHECKING:
    import pygame
    from game.simulation.entities.ship import Ship
    from game.core.registry import GameRegistries


class ShipFactory:
    """Factory for creating and configuring Ship instances.

    This class provides a clean interface for UI code to create ships
    without directly importing the Ship class from the simulation layer.

    Usage:
        factory = ShipFactory(registry_provider=fresh_registries)
        ship = factory.create_from_design(design_data)
        factory.configure_ship(ship, position, angle, team_id, ai_strategy, source_file)

    PROJ-50/PROJ-58: Registries stored on instance; method-level override also supported.
    """

    def __init__(self, *, registry_provider: Optional['GameRegistries'] = None):
        """Initialize ShipFactory with optional registries.

        Args:
            registry_provider: GameRegistries for DI. If None, uses get_default_registry_provider()
                       at method call time.
        """
        self._registry_provider = registry_provider

    def _get_registries(self, registry_provider: Optional['GameRegistries'] = None) -> 'GameRegistries':
        """Resolve registries: explicit > stored > global default."""
        if registry_provider is not None:
            return registry_provider
        if self._registry_provider is not None:
            return self._registry_provider
        from game.core.registry import get_default_registry_provider, GameRegistries
        provider = get_default_registry_provider()
        return GameRegistries(
            components=provider.get_components(),
            modifiers=provider.get_modifiers(),
            vehicle_classes=provider.get_vehicle_classes(),
            resources=provider.get_resources(),
        )

    def create_from_design(
        self,
        design_data: Dict[str, Any],
        *,
        registry_provider: Optional['GameRegistries'] = None
    ) -> 'Ship':
        """Create a Ship instance from design dictionary data.

        Args:
            design_data: Dictionary containing ship design data with keys:
                - name: Ship name
                - ship_class: Vehicle class name
                - theme_id: Visual theme identifier
                - color: RGB color tuple
                - layers: Component layer definitions
            registry_provider: Optional GameRegistries override (keyword-only).
                       If None, uses stored registries or global default.

        Returns:
            A new Ship instance created from the design data.

        Raises:
            KeyError: If required fields are missing from design_data.
            ValueError: If component or modifier IDs are invalid.
        """
        from game.simulation.entities.ship import Ship
        return Ship.from_dict(design_data, registries=self._get_registries(registry_provider))

    def get_ship_radius(
        self,
        design_data: Dict[str, Any],
        *,
        registry_provider: Optional['GameRegistries'] = None
    ) -> float:
        """Get the radius a ship would have based on design data.

        Creates a temporary ship from the design and returns its radius
        after recalculating stats. This is useful for formation spacing
        calculations where only the radius is needed.

        Args:
            design_data: Dictionary containing ship design data.
            registry_provider: Optional GameRegistries override (keyword-only).
                       If None, uses stored registries or global default.

        Returns:
            The calculated radius of the ship in world units.
        """
        temp_ship = self.create_from_design(design_data, registry_provider=registry_provider)
        temp_ship.recalculate_stats()
        return temp_ship.radius

    def configure_ship(
        self,
        ship: 'Ship',
        position: Union[Vector2, 'pygame.math.Vector2'],
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
            position: World position as Vector2 (core or pygame compatible).
            angle: Facing angle in degrees.
            team_id: Team identifier (0 or 1).
            ai_strategy: AI behavior strategy name.
            source_file: Path to the source design file.
        """
        # Convert to core Vector2 for consistency with Ship.position type
        ship.position = Vector2(position)
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
                ship.formation.master = master
                master.formation.members.append(ship)

                # Calculate offset from master to follower
                diff = ship.position - master.position
                ship.formation.rotation_mode = rotation_mode

                if rotation_mode == 'fixed':
                    ship.formation.offset = diff
                else:
                    # Rotate into master's local space
                    ship.formation.offset = diff.rotate(-master.angle)
