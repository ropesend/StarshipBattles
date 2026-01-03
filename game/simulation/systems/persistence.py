import json
import os
import tkinter
from tkinter import filedialog
import pygame
from game.simulation.entities.ship import Ship

# Initialize Tkinter root and hide it (for file dialogs)
try:
    tk_root = tkinter.Tk()
    tk_root.withdraw()
except Exception:
    tk_root = None

class ShipIO:
    """Handles ship file Input/Output operations."""
    
    # Configurable default directory (can be changed by builder)
    default_ships_folder = "ships"
    
    @staticmethod
    def save_ship(ship):
        """Save ship design to file. Returns True if successful."""
        if not tk_root:
            return False, "Tkinter not initialized"
            
        try:
            data = ship.to_dict()
            ships_folder = os.path.join(os.getcwd(), ShipIO.default_ships_folder)
            if not os.path.exists(ships_folder):
                os.makedirs(ships_folder)
                
            # Sanitize filename
            safe_name = "".join([c for c in ship.name if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).strip()
            if not safe_name: safe_name = "New Ship"
            
            filename = filedialog.asksaveasfilename(
                initialdir=ships_folder,
                initialfile=safe_name,
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json")],
                title="Save Ship Design"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=4)
                return True, f"Saved ship to {os.path.basename(filename)}"
            return False, None  # Cancelled
            
        except Exception as e:
            return False, f"Save failed: {e}"

    @staticmethod
    def load_ship(screen_width, screen_height):
        """Load ship design from file. Returns (Ship, message) or (None, error/message)."""
        if not tk_root:
            return None, "Tkinter not initialized"
            
        try:
            ships_folder = os.path.join(os.getcwd(), ShipIO.default_ships_folder)
            if not os.path.exists(ships_folder):
                os.makedirs(ships_folder)
                
            filename = filedialog.askopenfilename(
                initialdir=ships_folder,
                filetypes=[("JSON Files", "*.json")],
                title="Load Ship Design"
            )
            
            if filename:
                with open(filename, 'r') as f:
                    data = json.load(f)
                    
                new_ship = Ship.from_dict(data)
                new_ship.position = pygame.math.Vector2(screen_width // 2, screen_height // 2)
                new_ship.recalculate_stats()
                
                msg = f"Loaded ship from {os.path.basename(filename)}"
                if getattr(new_ship, '_loading_warnings', []):
                    warn_count = len(new_ship._loading_warnings)
                    msg += f"\nSafe Loaded with {warn_count} stat mismatches (auto-corrected)."
                
                return new_ship, msg
            return None, None  # Cancelled
            
        except Exception as e:
            return None, f"Load failed: {e}"
