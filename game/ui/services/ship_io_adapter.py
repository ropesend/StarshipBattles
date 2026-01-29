"""
Ship IO Adapter for UI layer.

PROJ-43: This adapter provides a facade for ship file I/O operations,
allowing UI code to work with ship persistence without directly importing
from game.simulation.systems.persistence.

The adapter encapsulates:
- Setting the ships folder location
- Saving ship designs to file
- Loading ship designs from file
"""
from typing import Optional, Tuple, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from game.simulation.systems.persistence import ShipIO as ShipIOType


class ShipIOAdapter:
    """Adapter for ship file I/O operations.

    This class provides a clean interface for UI code to save and load
    ship designs without directly using the ShipIO class from the
    simulation layer.

    Usage:
        adapter = ShipIOAdapter()
        adapter.set_ships_folder("custom_ships")
        success, message = adapter.save_ship(ship)
        loaded_ship, message = adapter.load_ship(width, height)
    """

    def __init__(self, ship_io_class: Optional[Any] = None):
        """Initialize the ShipIOAdapter.

        Args:
            ship_io_class: Optional ShipIO class for dependency injection.
                If None, uses the real ShipIO class.
        """
        if ship_io_class is None:
            from game.simulation.systems.persistence import ShipIO
            ship_io_class = ShipIO
        self._ship_io = ship_io_class

    def set_ships_folder(self, folder_path: str) -> None:
        """Set the default folder for ship designs.

        Args:
            folder_path: Path to the ships folder (relative or absolute).
        """
        self._ship_io.default_ships_folder = folder_path

    def get_ships_folder(self) -> str:
        """Get the current ships folder path.

        Returns:
            The current default ships folder path.
        """
        return self._ship_io.default_ships_folder

    def save_ship(self, ship: Any) -> Tuple[bool, Optional[str]]:
        """Save a ship design to file.

        Opens a file dialog for the user to choose the save location.

        Args:
            ship: The ship object to save.

        Returns:
            Tuple of (success, message).
            - On success: (True, success_message)
            - On failure: (False, error_message)
            - On cancel: (False, None)
        """
        return self._ship_io.save_ship(ship)

    def load_ship(self, width: int, height: int) -> Tuple[Optional[Any], Optional[str]]:
        """Load a ship design from file.

        Opens a file dialog for the user to choose the file to load.

        Args:
            width: Screen width for positioning the loaded ship.
            height: Screen height for positioning the loaded ship.

        Returns:
            Tuple of (ship, message).
            - On success: (ship_object, success_message)
            - On failure: (None, error_message)
            - On cancel: (None, None)
        """
        return self._ship_io.load_ship(width, height)
