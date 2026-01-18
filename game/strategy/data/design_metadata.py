"""
Design Metadata - Lightweight metadata about ship designs

This module provides the DesignMetadata class for tracking ship design information
without loading the full ship data. Used by the design library system for filtering,
sorting, and displaying designs in the UI.
"""
from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime
import os
from game.core.json_utils import load_json_required, save_json


@dataclass
class DesignMetadata:
    """Lightweight metadata about a ship design"""
    design_id: str  # Unique ID (filename without extension)
    name: str
    ship_class: str  # "Escort", "Frigate", etc.
    vehicle_type: str  # "Ship", "Fighter", "Satellite", "Planetary Complex"
    mass: float
    combat_power: float  # Calculated metric for sorting/filtering
    resource_cost: Dict[str, int] = field(default_factory=dict)

    created_date: str = ""  # ISO timestamp
    last_modified: str = ""
    is_obsolete: bool = False
    times_built: int = 0

    # Thumbnail data (optional)
    theme_id: str = ""
    sprite_preview: Optional[str] = None  # Base64 encoded image (future)

    def to_dict(self) -> dict:
        """Serialize to JSON"""
        return {
            "design_id": self.design_id,
            "name": self.name,
            "ship_class": self.ship_class,
            "vehicle_type": self.vehicle_type,
            "mass": self.mass,
            "combat_power": self.combat_power,
            "resource_cost": self.resource_cost,
            "created_date": self.created_date,
            "last_modified": self.last_modified,
            "is_obsolete": self.is_obsolete,
            "times_built": self.times_built,
            "theme_id": self.theme_id,
            "sprite_preview": self.sprite_preview
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'DesignMetadata':
        """Deserialize from JSON"""
        return cls(
            design_id=data.get("design_id", ""),
            name=data.get("name", "Unnamed"),
            ship_class=data.get("ship_class", "Unknown"),
            vehicle_type=data.get("vehicle_type", "Ship"),
            mass=data.get("mass", 0.0),
            combat_power=data.get("combat_power", 0.0),
            resource_cost=data.get("resource_cost", {}),
            created_date=data.get("created_date", ""),
            last_modified=data.get("last_modified", ""),
            is_obsolete=data.get("is_obsolete", False),
            times_built=data.get("times_built", 0),
            theme_id=data.get("theme_id", ""),
            sprite_preview=data.get("sprite_preview")
        )

    @classmethod
    def from_design_file(cls, filepath: str, design_id: str) -> 'DesignMetadata':
        """
        Load metadata from ship JSON file.

        Reads the ship design file and extracts metadata without fully
        instantiating the Ship object.
        """
        data = load_json_required(filepath)

        # Extract basic info
        name = data.get("name", "Unnamed")
        ship_class = data.get("ship_class", "Unknown")
        vehicle_type = data.get("vehicle_type", "Ship")
        mass = data.get("mass", 0.0)
        theme_id = data.get("theme_id", "")

        # Calculate combat power (simplified metric)
        combat_power = cls._calculate_combat_power(data)

        # Calculate resource costs
        resource_cost = cls._calculate_resource_cost(data)

        # Get file timestamps
        stat = os.stat(filepath)
        created_date = datetime.fromtimestamp(stat.st_ctime).isoformat()
        last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()

        # Check for embedded metadata
        embedded_metadata = data.get("_metadata", {})

        return cls(
            design_id=design_id,
            name=name,
            ship_class=ship_class,
            vehicle_type=vehicle_type,
            mass=mass,
            combat_power=combat_power,
            resource_cost=resource_cost,
            created_date=created_date,
            last_modified=last_modified,
            is_obsolete=embedded_metadata.get("is_obsolete", False),
            times_built=embedded_metadata.get("times_built", 0),
            theme_id=theme_id
        )

    @classmethod
    def from_ship(cls, ship, design_id: str) -> 'DesignMetadata':
        """
        Create metadata from Ship object.

        Used when saving a new design to create initial metadata.
        """
        # Calculate combat power
        combat_power = cls._calculate_combat_power_from_ship(ship)

        # Calculate resource costs
        resource_cost = cls._calculate_resource_cost_from_ship(ship)

        now = datetime.now().isoformat()

        return cls(
            design_id=design_id,
            name=ship.name,
            ship_class=ship.ship_class,
            vehicle_type=getattr(ship, 'vehicle_type', 'Ship'),
            mass=ship.mass,
            combat_power=combat_power,
            resource_cost=resource_cost,
            created_date=now,
            last_modified=now,
            is_obsolete=False,
            times_built=0,
            theme_id=getattr(ship, 'theme_id', '')
        )

    @staticmethod
    def _calculate_combat_power(data: dict) -> float:
        """
        Calculate simplified combat power metric from ship data dict.

        This is a rough estimate for sorting/filtering purposes.
        """
        power = 0.0

        # Add component contributions
        layers = data.get("layers", {})
        for layer_data in layers.values():
            # Handle both old format (dict with "components" key) and new format (direct list)
            if isinstance(layer_data, list):
                # New format: layers[layer_name] = [comp1, comp2, ...]
                components = layer_data
            elif isinstance(layer_data, dict):
                # Old format: layers[layer_name] = {"components": [comp1, comp2, ...]}
                components = layer_data.get("components", [])
            else:
                components = []

            for comp_data in components:
                # Weapon components contribute heavily
                if comp_data.get("category") == "weapon":
                    power += comp_data.get("damage", 0) * 10
                    power += comp_data.get("rate_of_fire", 0) * 5

                # Defensive components
                if comp_data.get("category") == "armor":
                    power += comp_data.get("hp", 0) * 0.5

        return power

    @staticmethod
    def _calculate_combat_power_from_ship(ship) -> float:
        """Calculate combat power from Ship instance"""
        power = 0.0

        # Sum weapon damage
        for layer_type, layer_data in ship.layers.items():
            for comp in layer_data.get('components', []):
                if hasattr(comp, 'category') and comp.category == 'weapon':
                    power += getattr(comp, 'damage', 0) * 10
                    power += getattr(comp, 'rate_of_fire', 0) * 5

                if hasattr(comp, 'category') and comp.category == 'armor':
                    power += getattr(comp, 'hp', 0) * 0.5

        return power

    @staticmethod
    def _calculate_resource_cost(data: dict) -> Dict[str, int]:
        """Calculate resource costs from ship data dict"""
        costs = {}

        # Sum component costs
        layers = data.get("layers", {})
        for layer_data in layers.values():
            # Handle both old format (dict with "components" key) and new format (direct list)
            if isinstance(layer_data, list):
                components = layer_data
            elif isinstance(layer_data, dict):
                components = layer_data.get("components", [])
            else:
                components = []

            for comp_data in components:
                comp_cost = comp_data.get("cost", {})
                for resource, amount in comp_cost.items():
                    costs[resource] = costs.get(resource, 0) + amount

        return costs

    @staticmethod
    def _calculate_resource_cost_from_ship(ship) -> Dict[str, int]:
        """Calculate resource costs from Ship instance"""
        costs = {}

        for layer_type, layer_data in ship.layers.items():
            for comp in layer_data.get('components', []):
                if hasattr(comp, 'cost'):
                    comp_cost = comp.cost

                    # Handle both integer costs and dictionary costs
                    if isinstance(comp_cost, dict):
                        # Dictionary of resource: amount
                        for resource, amount in comp_cost.items():
                            costs[resource] = costs.get(resource, 0) + amount
                    elif isinstance(comp_cost, (int, float)):
                        # Single integer cost (assume it's "minerals" or generic cost)
                        costs['minerals'] = costs.get('minerals', 0) + int(comp_cost)

        return costs

    def embed_in_ship_data(self, ship_data: dict) -> dict:
        """
        Embed this metadata into ship data dict for saving.

        This allows metadata to be stored with the ship file.
        """
        ship_data["_metadata"] = {
            "is_obsolete": self.is_obsolete,
            "times_built": self.times_built,
            "created_date": self.created_date,
            "last_modified": self.last_modified
        }
        return ship_data
