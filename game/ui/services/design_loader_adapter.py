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
from game.core.registry import get_default_registries


class DesignLoaderAdapter:
    """Adapter for loading ship designs.

    This class provides a clean interface for UI code to load ship designs
    without directly using the SimulationDesignLoader class from the
    simulation layer.

    Usage:
        adapter = DesignLoaderAdapter()
        ship = adapter.load_ship_from_design_data(design_data, width, height)
        ship, message = adapter.load_ship_from_file(filepath, width, height)
    """

    def __init__(self, design_loader: Optional[Any] = None, *, registries: Optional[Any] = None):
        """Initialize the DesignLoaderAdapter.

        Args:
            design_loader: Optional SimulationDesignLoader instance for dependency
                injection. If None, creates a new SimulationDesignLoader.
            registries: Optional GameRegistries for DI (keyword-only).
                       Required if design_loader is None.
        """
        if design_loader is None:
            if registries is None:
                registries = get_default_registries()
            design_loader = SimulationDesignLoader(registries=registries)
        self._loader = design_loader

    def load_ship_from_design_data(
        self,
        design_data: dict,
        width: int,
        height: int
    ) -> Optional[Any]:
        """Load a Ship object from design data.

        Creates a Ship object from a design data dictionary and positions it
        at the center of the given screen dimensions.

        Args:
            design_data: Design data dictionary (as loaded from JSON).
            width: Screen width for centering the ship.
            height: Screen height for centering the ship.

        Returns:
            Ship object with stats recalculated, or None on error.
        """
        return self._loader.load_ship_from_design_data(
            design_data,
            center_x=width // 2,
            center_y=height // 2
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
