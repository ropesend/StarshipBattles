"""
ShipIO - Ship file Input/Output operations.

Moved from game.simulation.systems.persistence to game.ui.services as part of PROJ-113
to fix layer violation: tkinter is a UI framework and doesn't belong in simulation layer.

DUP-UI2-001: Tkinter initialization now uses shared tkinter_utils module.
ADR-UI2-001: Uses DesignLoaderAdapter for ship loading (TYPE_CHECKING for Ship type hints).

PROJ-211: DesignLoaderAdapter now requires registry_provider. Uses lazy initialization.

This module handles:
- Saving ship designs to JSON files via file dialog
- Loading ship designs from JSON files via file dialog
"""
import json
import os
from typing import Any, Optional, Tuple, TYPE_CHECKING

from game.core.json_utils import load_json_required, save_json
from game.core.exceptions import ValidationException, ComponentException
import logging

logger = logging.getLogger(__name__)
from game.ui.services.design_loader_adapter import DesignLoaderAdapter
from game.ui.services.tkinter_utils import (
    is_tkinter_available,
    open_save_dialog,
    open_load_dialog,
)

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.core.registry import GameRegistries


# PROJ-211: Lazy registries initialization (not available at import time)
_cached_registries = None


def _get_registries() -> 'GameRegistries':
    """Get or create registries for DesignLoaderAdapter."""
    global _cached_registries
    if _cached_registries is None:
        from game.core.registry import get_default_registry_provider, GameRegistries
        provider = get_default_registry_provider()
        _cached_registries = GameRegistries(
            components=provider.get_components(),
            modifiers=provider.get_modifiers(),
            vehicle_classes=provider.get_vehicle_classes(),
            resources=provider.get_resources(),
        )
    return _cached_registries


class ShipIO:
    """Handles ship file Input/Output operations.

    Uses DesignLoaderAdapter for ship loading to maintain consistency with
    the adapter pattern used by other UI services. This reduces direct
    coupling to simulation layer entities.
    """

    # Configurable default directory (can be changed by builder)
    default_ships_folder = "ships"

    # Shared adapter instance (lazy-initialized)
    _design_loader: Optional[DesignLoaderAdapter] = None

    @classmethod
    def _get_design_loader(cls) -> DesignLoaderAdapter:
        """Get or create the shared DesignLoaderAdapter instance.

        PROJ-211: Now passes registries to DesignLoaderAdapter.
        """
        if cls._design_loader is None:
            cls._design_loader = DesignLoaderAdapter(registry_provider=_get_registries())
        return cls._design_loader

    @staticmethod
    def save_ship(ship: 'Ship') -> Tuple[bool, Optional[str]]:
        """Save ship design to file.

        Args:
            ship: The Ship object to save.

        Returns:
            Tuple of (success, message). Message is None if cancelled.
        """
        if not is_tkinter_available():
            return False, "Tkinter not initialized"

        try:
            data = ship.to_dict()
            ships_folder = os.path.join(os.getcwd(), ShipIO.default_ships_folder)
            if not os.path.exists(ships_folder):
                os.makedirs(ships_folder)

            # Sanitize filename
            safe_name = "".join([c for c in ship.name if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).strip()
            if not safe_name: safe_name = "New Ship"

            filename = open_save_dialog(
                initialdir=ships_folder,
                initialfile=safe_name,
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json")],
                title="Save Ship Design"
            )

            if filename:
                if save_json(filename, data, indent=4):
                    return True, f"Saved ship to {os.path.basename(filename)}"
                return False, "Failed to save ship file"
            return False, None  # Cancelled

        except PermissionError as e:
            logger.error(f"ShipIO: Permission denied saving ship: {e}")
            return False, "Save failed: Permission denied"
        except OSError as e:
            logger.error(f"ShipIO: OS error saving ship: {e}")
            return False, f"Save failed: {str(e)}"
        except ValidationException as e:
            logger.error(f"ShipIO: Serialization error saving ship: {e}")
            return False, "Save failed: Invalid ship data"

    @classmethod
    def load_ship(cls, screen_width: int, screen_height: int) -> Tuple[Optional[Any], Optional[str]]:
        """Load ship design from file.

        Args:
            screen_width: Screen width for positioning loaded ship.
            screen_height: Screen height for positioning loaded ship.

        Returns:
            Tuple of (ship, message). Ship is None if cancelled or on error.
        """
        if not is_tkinter_available():
            return None, "Tkinter not initialized"

        try:
            ships_folder = os.path.join(os.getcwd(), cls.default_ships_folder)
            if not os.path.exists(ships_folder):
                os.makedirs(ships_folder)

            filename = open_load_dialog(
                initialdir=ships_folder,
                filetypes=[("JSON Files", "*.json")],
                title="Load Ship Design"
            )

            if filename:
                data = load_json_required(filename)

                # Use DesignLoaderAdapter for ship creation (adapter pattern)
                loader = cls._get_design_loader()
                new_ship = loader.load_ship_from_design_data(
                    data,
                    center_x=screen_width // 2,
                    center_y=screen_height // 2
                )

                if new_ship is None:
                    return None, "Load failed: Could not create ship from design"

                msg = f"Loaded ship from {os.path.basename(filename)}"
                if new_ship._loading_warnings:
                    warn_count = len(new_ship._loading_warnings)
                    msg += f"\nSafe Loaded with {warn_count} stat mismatches (auto-corrected)."

                return new_ship, msg
            return None, None  # Cancelled

        except json.JSONDecodeError as e:
            logger.error(f"ShipIO: Corrupt JSON in ship file: {e}")
            return None, "Load failed: File contains invalid JSON"
        except KeyError as e:
            logger.error(f"ShipIO: Missing required field in ship file: {e}")
            return None, f"Load failed: Missing required field"
        except PermissionError as e:
            logger.error(f"ShipIO: Permission denied loading ship: {e}")
            return None, "Load failed: Permission denied"
        except OSError as e:
            logger.error(f"ShipIO: OS error loading ship: {e}")
            return None, f"Load failed: {str(e)}"
        except (TypeError, ValueError, ValidationException, ComponentException) as e:
            logger.error(f"ShipIO: Unexpected error loading ship: {e}")
            return None, f"Load failed: {str(e)}"
