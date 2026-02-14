"""
ShipIO - Ship file Input/Output operations.

Moved from game.simulation.systems.persistence to game.ui.services as part of PROJ-113
to fix layer violation: tkinter is a UI framework and doesn't belong in simulation layer.

DUP-UI2-001: Tkinter initialization now uses shared tkinter_utils module.

This module handles:
- Saving ship designs to JSON files via file dialog
- Loading ship designs from JSON files via file dialog
"""
import json
import os

from game.core.math import Vector2
from game.simulation.entities.ship import Ship
from game.core.json_utils import load_json_required, save_json
from game.core.logger import log_error
from game.ui.services.tkinter_utils import (
    is_tkinter_available,
    open_save_dialog,
    open_load_dialog,
)


class ShipIO:
    """Handles ship file Input/Output operations."""

    # Configurable default directory (can be changed by builder)
    default_ships_folder = "ships"

    @staticmethod
    def save_ship(ship):
        """Save ship design to file. Returns True if successful."""
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
            log_error(f"ShipIO: Permission denied saving ship: {e}")
            return False, "Save failed: Permission denied"
        except OSError as e:
            log_error(f"ShipIO: OS error saving ship: {e}")
            return False, f"Save failed: {str(e)}"
        except (TypeError, ValueError) as e:
            log_error(f"ShipIO: Serialization error saving ship: {e}")
            return False, "Save failed: Invalid ship data"

    @staticmethod
    def load_ship(screen_width, screen_height):
        """Load ship design from file. Returns (Ship, message) or (None, error/message)."""
        if not is_tkinter_available():
            return None, "Tkinter not initialized"

        try:
            ships_folder = os.path.join(os.getcwd(), ShipIO.default_ships_folder)
            if not os.path.exists(ships_folder):
                os.makedirs(ships_folder)

            filename = open_load_dialog(
                initialdir=ships_folder,
                filetypes=[("JSON Files", "*.json")],
                title="Load Ship Design"
            )

            if filename:
                data = load_json_required(filename)
                new_ship = Ship.from_dict(data)
                new_ship.position = Vector2(screen_width // 2, screen_height // 2)
                new_ship.recalculate_stats()

                msg = f"Loaded ship from {os.path.basename(filename)}"
                if getattr(new_ship, '_loading_warnings', []):
                    warn_count = len(new_ship._loading_warnings)
                    msg += f"\nSafe Loaded with {warn_count} stat mismatches (auto-corrected)."

                return new_ship, msg
            return None, None  # Cancelled

        except json.JSONDecodeError as e:
            log_error(f"ShipIO: Corrupt JSON in ship file: {e}")
            return None, "Load failed: File contains invalid JSON"
        except KeyError as e:
            log_error(f"ShipIO: Missing required field in ship file: {e}")
            return None, f"Load failed: Missing required field"
        except PermissionError as e:
            log_error(f"ShipIO: Permission denied loading ship: {e}")
            return None, "Load failed: Permission denied"
        except OSError as e:
            log_error(f"ShipIO: OS error loading ship: {e}")
            return None, f"Load failed: {str(e)}"
        except (TypeError, ValueError) as e:
            log_error(f"ShipIO: Unexpected error loading ship: {e}")
            return None, f"Load failed: {str(e)}"
