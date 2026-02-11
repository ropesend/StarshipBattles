"""
Simulation Design Loader - Load ship designs from files into Ship objects.

This module handles the instantiation of Ship objects from design data files.
This belongs in the simulation layer because it creates simulation entities (Ships).

Part of PROJ-30: Strategy Mode Layer Boundary Cleanup (STRAT-01 fix).
Previously, this functionality was incorrectly placed in DesignLibrary (strategy layer),
which violated the architectural boundary between strategy and simulation layers.

PROJ-45: Added specific exception handling with exception chaining.
PROJ-50: Added registries parameter for strict DI compliance.
"""
import json
import os
from typing import Optional, Tuple, TYPE_CHECKING

from game.core.json_utils import load_json_required
from game.core.logger import log_info, log_error
from game.core.exceptions import PersistenceException, ValidationException
from game.core.math import Vector2
from game.simulation.entities.ship import Ship

if TYPE_CHECKING:
    from game.core.registries import GameRegistries


class SimulationDesignLoader:
    """
    Loads ship designs from files and creates Ship simulation entities.

    This class handles the simulation layer concern of instantiating Ship objects
    from design data. It should be used by UI/simulation layer code that needs
    to load ships for editing or display, NOT by strategy layer code.

    Strategy layer code should use DesignLibrary.load_design_data() to get
    raw design data without creating Ship objects.

    PROJ-50: Accepts registries for strict DI compliance.
    """

    def __init__(self, *, registries: 'GameRegistries'):
        """
        Initialize the loader with registries.

        Args:
            registries: GameRegistries for DI (required).
        """
        if registries is None:
            raise TypeError("registries is required for SimulationDesignLoader")
        self._registries = registries

    def load_ship_from_design_data(
        self,
        design_data: dict,
        center_x: int = 0,
        center_y: int = 0
    ) -> Optional[Ship]:
        """
        Create a Ship object from design data dictionary.

        Args:
            design_data: Design data dictionary (as loaded from JSON)
            center_x: X coordinate for ship position (default 0)
            center_y: Y coordinate for ship position (default 0)

        Returns:
            Ship object with stats recalculated, or None on error
        """
        try:
            ship = Ship.from_dict(design_data, registries=self._registries)
            ship.position = Vector2(center_x, center_y)
            ship.recalculate_stats()
            return ship
        except (KeyError, TypeError, ValueError) as e:
            # Data validation errors
            log_error(f"SimulationDesignLoader: Invalid design data - {type(e).__name__}: {e}")
            return None
        except (AttributeError, ImportError, OSError) as e:
            # Unexpected errors - log with full context
            log_error(f"SimulationDesignLoader: Failed to create Ship from data - {type(e).__name__}: {e}")
            return None

    def load_ship_from_file(
        self,
        file_path: str,
        width: int = 1920,
        height: int = 1080
    ) -> Tuple[Optional[Ship], str]:
        """
        Load a ship design from a JSON file.

        Args:
            file_path: Full path to design JSON file
            width: Screen width for centering (default 1920)
            height: Screen height for centering (default 1080)

        Returns:
            Tuple of (Ship object or None, message string)
        """
        if not os.path.exists(file_path):
            return None, f"Design file not found: {file_path}"

        try:
            data = load_json_required(file_path)
            ship = self.load_ship_from_design_data(
                data,
                center_x=width // 2,
                center_y=height // 2
            )

            if ship is None:
                return None, "Failed to create ship from design data"

            log_info(f"SimulationDesignLoader: Loaded design '{ship.name}' from {file_path}")
            return ship, f"Loaded design: {ship.name}"

        except json.JSONDecodeError as e:
            # Invalid JSON format
            log_error(f"SimulationDesignLoader: Invalid JSON in {file_path}: {e}")
            return None, f"Failed to load design: Invalid JSON format"
        except (KeyError, TypeError, ValueError) as e:
            # Data validation errors
            log_error(f"SimulationDesignLoader: Invalid design data in {file_path} - {type(e).__name__}: {e}")
            return None, f"Failed to load design: Invalid design data"
        except OSError as e:
            # File I/O errors
            log_error(f"SimulationDesignLoader: I/O error loading {file_path}: {e}")
            return None, f"Failed to load design: {str(e)}"
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as e:
            # Unexpected errors - log with full context
            log_error(f"SimulationDesignLoader: Failed to load design from {file_path} - {type(e).__name__}: {e}")
            return None, f"Failed to load design: {str(e)}"
