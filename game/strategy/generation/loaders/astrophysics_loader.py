"""
Astrophysics configuration loader.

Loads physics parameters for planet classification, habitable zones,
and atmospheric retention from JSON configuration.
"""
from pathlib import Path
from typing import Dict, Any, Optional

from game.core.json_utils import load_json_required


class AstrophysicsLoader:
    """
    Loader for astrophysics.json.

    Contains physical parameters used for:
    - Mass distributions (rocky, gas giant, ice giant, dwarf)
    - Orbit zone calculations (hot, habitable, cold, outer)
    - Habitable zone formula
    - Ice line calculations
    - Atmospheric retention thresholds
    - Planet classification thresholds
    """

    DEFAULT_PATH = Path("data/astrophysics.json")

    def __init__(self, file_path: Optional[Path] = None):
        """
        Initialize loader with optional custom path.

        Args:
            file_path: Optional path to astrophysics JSON. Uses default if None.
        """
        self.file_path = file_path or self.DEFAULT_PATH

    def load(self) -> Dict[str, Any]:
        """
        Load and validate astrophysics configuration from JSON file.

        Returns:
            Dict containing all astrophysics parameters.

        Raises:
            FileNotFoundError: If file doesn't exist.
            json.JSONDecodeError: If file isn't valid JSON.
            ValueError: If schema validation fails.
        """
        data = load_json_required(str(self.file_path))
        self._validate_schema(data)
        return data

    def get_mass_distribution(self, category: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get mass distribution parameters for a category.

        Args:
            category: Distribution category ('rocky', 'gas_giant', etc.)
            data: Loaded astrophysics data from load().

        Returns:
            Distribution parameters dict.
        """
        distributions = data.get("mass_distributions", {})
        if category not in distributions:
            raise KeyError(f"Unknown mass distribution: {category}")
        return distributions[category]

    def get_orbit_zone(self, zone: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get orbit zone parameters.

        Args:
            zone: Zone name ('hot', 'habitable', 'cold', 'outer')
            data: Loaded astrophysics data from load().

        Returns:
            Zone parameters dict.
        """
        zones = data.get("orbit_zones", {})
        if zone not in zones:
            raise KeyError(f"Unknown orbit zone: {zone}")
        return zones[zone]

    def get_habitable_zone_factors(self, data: Dict[str, Any]) -> tuple:
        """
        Get habitable zone inner/outer factors.

        Args:
            data: Loaded astrophysics data from load().

        Returns:
            Tuple of (inner_factor, outer_factor)
        """
        hz = data.get("habitable_zone", {})
        return (hz.get("inner_factor", 0.95), hz.get("outer_factor", 1.37))

    def _validate_schema(self, data: Dict[str, Any]) -> None:
        """
        Validate astrophysics schema.

        Args:
            data: Loaded JSON data.

        Raises:
            ValueError: If schema is invalid.
        """
        required_sections = [
            "mass_distributions",
            "orbit_zones",
            "habitable_zone",
            "ice_line",
            "atmosphere_retention",
            "classification"
        ]

        for section in required_sections:
            if section not in data:
                raise ValueError(f"Missing required section: {section}")

        # Validate mass_distributions
        distributions = data["mass_distributions"]
        required_dist = ["rocky", "gas_giant", "ice_giant", "dwarf"]
        for name in required_dist:
            if name not in distributions:
                raise ValueError(f"Missing mass distribution: {name}")

        # Validate orbit_zones
        zones = data["orbit_zones"]
        required_zones = ["hot", "habitable", "cold", "outer"]
        for name in required_zones:
            if name not in zones:
                raise ValueError(f"Missing orbit zone: {name}")

        # Validate habitable_zone
        hz = data["habitable_zone"]
        if "inner_factor" not in hz or "outer_factor" not in hz:
            raise ValueError("habitable_zone missing inner_factor or outer_factor")

        # Validate atmosphere_retention
        atm = data["atmosphere_retention"]
        if "thresholds" not in atm:
            raise ValueError("atmosphere_retention missing thresholds")

        # Validate classification
        classification = data["classification"]
        if "mass_thresholds" not in classification:
            raise ValueError("classification missing mass_thresholds")
        if "temperature_thresholds" not in classification:
            raise ValueError("classification missing temperature_thresholds")
