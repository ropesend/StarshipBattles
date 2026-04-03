"""
Design Metadata - Lightweight metadata about ship designs

This module provides the DesignMetadata class for tracking ship design information
without loading the full ship data. Used by the design library system for filtering,
sorting, and displaying designs in the UI.
"""
import logging
from dataclasses import dataclass, field
from typing import Any, Dict
from datetime import datetime
import os
import warnings
from game.core.json_utils import load_json_required, save_json
from game.core.patterns.layer_iterator import iter_layers_and_components
from game.core.validation_helpers import require_keys

logger = logging.getLogger(__name__)


@dataclass
class DesignMetadata:
    """Lightweight metadata about a ship design"""
    design_id: str  # Unique ID (filename without extension)
    name: str
    ship_class: str  # "Escort", "Frigate", etc.
    vehicle_type: str  # "Ship", "Fighter", "Satellite", "Planetary Complex"
    mass: float
    combat_power: float  # Calculated metric for sorting/filtering
    construction_cost: Dict[str, int] = field(default_factory=dict)

    created_date: str = ""  # ISO timestamp
    last_modified: str = ""
    is_obsolete: bool = False
    times_built: int = 0

    # Validity
    mass_valid: bool = True  # False if design exceeds mass budget

    # Thumbnail data (optional)
    theme_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to JSON"""
        return {
            "design_id": self.design_id,
            "name": self.name,
            "ship_class": self.ship_class,
            "vehicle_type": self.vehicle_type,
            "mass": self.mass,
            "combat_power": self.combat_power,
            "construction_cost": self.construction_cost,
            "created_date": self.created_date,
            "last_modified": self.last_modified,
            "is_obsolete": self.is_obsolete,
            "times_built": self.times_built,
            "theme_id": self.theme_id,
            "mass_valid": self.mass_valid
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'DesignMetadata':
        """Deserialize from JSON.

        Required fields: design_id, name
        Optional fields: all others with sensible defaults

        Raises:
            PersistenceException: If required keys are missing
        """
        require_keys(data, ['design_id', 'name'], 'DesignMetadata')
        return cls(
            design_id=data["design_id"],
            name=data["name"],
            ship_class=data.get("ship_class", "Unknown"),
            vehicle_type=data.get("vehicle_type", "Ship"),
            mass=data.get("mass", 0.0),
            combat_power=data.get("combat_power", 0.0),
            construction_cost=data.get("construction_cost", {}),
            created_date=data.get("created_date", ""),
            last_modified=data.get("last_modified", ""),
            is_obsolete=data.get("is_obsolete", False),
            times_built=data.get("times_built", 0),
            theme_id=data.get("theme_id", ""),
            mass_valid=data.get("mass_valid", True)
        )

    @classmethod
    def from_design_file(cls, file_path: str, design_id: str) -> 'DesignMetadata':
        """
        Load metadata from ship JSON file.

        Reads the ship design file and extracts metadata without fully
        instantiating the Ship object.
        """
        data = load_json_required(file_path)

        # Extract basic info
        name = data.get("name", "Unnamed")
        ship_class = data.get("ship_class", "Unknown")
        vehicle_type = data.get("vehicle_type", "Ship")
        theme_id = data.get("theme_id", "")

        # Mass and validity stored in expected_stats
        expected_stats = data.get("expected_stats", {})
        mass = expected_stats.get("mass", 0.0)
        mass_valid = expected_stats.get("mass_valid", True)

        # Calculate combat power (simplified metric)
        combat_power = cls._calculate_combat_power(data)

        # Calculate construction costs
        construction_cost = cls._calculate_construction_cost(data)

        # Get file timestamps
        stat = os.stat(file_path)
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
            construction_cost=construction_cost,
            created_date=created_date,
            last_modified=last_modified,
            is_obsolete=embedded_metadata.get("is_obsolete", False),
            times_built=embedded_metadata.get("times_built", 0),
            mass_valid=mass_valid,
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

        # Calculate construction costs
        construction_cost = cls._calculate_construction_cost_from_ship(ship)

        now = datetime.now().isoformat()

        return cls(
            design_id=design_id,
            name=ship.name,
            ship_class=ship.ship_class,
            vehicle_type=ship.vehicle_type,  # Ship always has vehicle_type
            mass=ship.mass,
            combat_power=combat_power,
            construction_cost=construction_cost,
            created_date=now,
            last_modified=now,
            is_obsolete=False,
            times_built=0,
            mass_valid=getattr(ship, 'mass_limits_ok', True),
            theme_id=ship.theme_id  # Ship always has theme_id
        )

    @staticmethod
    def _calculate_combat_power(data: dict) -> float:
        """
        Calculate simplified combat power metric from ship data dict.

        This is a rough estimate for sorting/filtering purposes.
        """
        from game.core.patterns.layer_iterator import iter_components

        power = 0.0

        for comp_data in iter_components(data):
            if not isinstance(comp_data, dict):
                continue
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
        """Calculate combat power from Ship instance.

        Uses Component.major_classification to identify weapon/armor components.
        Weapon damage is extracted from WeaponAbility instances.
        """
        power = 0.0

        # Sum weapon damage (Component always has major_classification, get_abilities, max_hp)
        for layer_type, layer_data in ship.layers.items():
            for comp in layer_data.components:
                # Weapon components: use major_classification and WeaponAbility
                if comp.major_classification == 'Weapons':
                    weapon_abilities = comp.get_abilities('WeaponAbility')
                    for weapon in weapon_abilities:
                        # WeaponAbility always has damage, reload_time
                        damage = weapon.damage
                        reload_time = weapon.reload_time if weapon.reload_time > 0 else 1.0
                        rate_of_fire = 1.0 / reload_time
                        power += damage * 10
                        power += rate_of_fire * 5

                # Armor components: use major_classification and max_hp
                if comp.major_classification == 'Armor':
                    power += comp.max_hp * 0.5

        return power

    @staticmethod
    def _calculate_construction_cost(data: dict) -> Dict[str, int]:
        """Calculate construction costs from ship data dict.

        Note: This method looks for inline 'resource_cost' fields on component
        entries, but actual design files only contain component references
        (e.g., {"id": "bridge"}). The real costs are in the component registry.

        For accurate costs, use _calculate_construction_cost_from_ship() with a
        loaded Ship object, or DesignCostCalculator.calculate_total_cost()
        which uses Ship loading.

        PROJ-218: Fixed field name from 'cost' to 'resource_cost' for consistency.
        """
        from game.core.patterns.layer_iterator import iter_components

        costs = {}

        for comp_data in iter_components(data):
            if not isinstance(comp_data, dict):
                continue
            # PROJ-218: Use 'resource_cost' not 'cost' for consistency
            comp_cost = comp_data.get("resource_cost", {})
            for resource, amount in comp_cost.items():
                costs[resource] = costs.get(resource, 0) + amount

        return costs

    @staticmethod
    def _calculate_construction_cost_from_ship(ship) -> Dict[str, int]:
        """Calculate construction costs from Ship instance.

        Component.cost always exists (defaults to 0 in Component.__init__).
        """
        costs = {}

        for layer_type, layer_data in ship.layers.items():
            for comp in layer_data.components:
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
