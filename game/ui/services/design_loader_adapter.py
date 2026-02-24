"""
Design Loader Adapter for UI layer.

PROJ-43: This adapter provides a facade for ship design loading operations,
allowing UI code to create Ship objects from design data without directly
importing from game.simulation.services.design_loader.

The adapter encapsulates:
- Loading Ship objects from design data dictionaries
- Loading Ship objects from design files
"""
from typing import Optional, Tuple, Any

from game.simulation.services.design_loader import SimulationDesignLoader
from game.core.registry import get_default_registry_provider, GameRegistries


class DesignLoaderAdapter:
    """Adapter for loading ship designs.

    This class provides a clean interface for UI code to load ship designs
    without directly using the SimulationDesignLoader class from the
    simulation layer.

    Usage:
        adapter = DesignLoaderAdapter()
        ship = adapter.load_ship_from_design_data(design_data, center_x, center_y)
        ship, message = adapter.load_ship_from_file(filepath, width, height)
    """

    def __init__(self, design_loader: Optional[Any] = None, *, registry_provider: Optional[Any] = None):
        """Initialize the DesignLoaderAdapter.

        Args:
            design_loader: Optional SimulationDesignLoader instance for dependency
                injection. If None, creates a new SimulationDesignLoader.
            registry_provider: Optional GameRegistries for DI (keyword-only).
                       Required if design_loader is None.
        """
        if design_loader is None:
            if registry_provider is None:
                provider = get_default_registry_provider()
                registry_provider = GameRegistries(
                    components=provider.get_components(),
                    modifiers=provider.get_modifiers(),
                    vehicle_classes=provider.get_vehicle_classes(),
                    resources=provider.get_resources(),
                )
            design_loader = SimulationDesignLoader(registries=registry_provider)
        self._loader = design_loader

    def load_ship_from_design_data(
        self,
        design_data: dict,
        center_x: int = 0,
        center_y: int = 0
    ) -> Optional[Any]:
        """Load a Ship object from design data.

        Creates a Ship object from a design data dictionary and positions it
        at the specified coordinates.

        Args:
            design_data: Design data dictionary (as loaded from JSON).
            center_x: X coordinate for ship positioning.
            center_y: Y coordinate for ship positioning.

        Returns:
            Ship object with stats recalculated, or None on error.
        """
        return self._loader.load_ship_from_design_data(
            design_data,
            center_x=center_x,
            center_y=center_y
        )

    def load_ship_from_file(
        self,
        filepath: str,
        width: int,
        height: int
    ) -> Tuple[Optional[Any], str]:
        """Load a Ship object from a design file.

        Args:
            filepath: Full path to the design JSON file.
            width: Screen width for centering (used for positioning).
            height: Screen height for centering (used for positioning).

        Returns:
            Tuple of (Ship object or None, message string).
        """
        return self._loader.load_ship_from_file(filepath, width, height)
