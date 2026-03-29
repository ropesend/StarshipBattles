"""
Astrophysics configuration loader.

Loads physics parameters for planet classification, habitable zones,
and atmospheric retention from JSON configuration.
"""
from pathlib import Path
from typing import Dict, Any, Optional

from game.core.json_utils import load_json_required
from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode


class AstrophysicsLoader:
    """
    Loader for astrophysics.json.

    Contains physical parameters used for:
    - Mass distributions (rocky, gas giant, ice giant, dwarf)
    - Orbit zone calculations (hot, habitable, cold, outer)
    - Habitable zone formula
    - Ice line calculations
    - Atmospheric retention thresholds
    - Planet classification thresholds (including chthonian stripping)
    - Resource generation parameters (mass scaling, quality, affinities, ramp_c)
    - Star generation parameters (type weights, mass distribution, system probabilities, companion spacing, Stefan-Boltzmann type properties)
    - Orbital generation parameters (orbital placement, planet mass distribution, moon system, surface flags)
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
            ValidationException: If schema validation fails.
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
            raise ValidationException(
                f"Unknown mass distribution: {category}",
                code=ErrorCode.VALIDATION_FAILED.value,
                context={"category": category, "available": list(distributions.keys())}
            )
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
            raise ValidationException(
                f"Unknown orbit zone: {zone}",
                code=ErrorCode.VALIDATION_FAILED.value,
                context={"zone": zone, "available": list(zones.keys())}
            )
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
            ValidationException: If schema is invalid.
        """
        required_sections = [
            "mass_distributions",
            "orbit_zones",
            "habitable_zone",
            "ice_line",
            "atmosphere_retention",
            "classification",
            "resource_generation",
            "star_generation",
            "orbital_generation",
        ]

        for section in required_sections:
            if section not in data:
                raise ValidationException(
                    f"Missing required section: {section}",
                    code=ErrorCode.SCHEMA_VALIDATION_ERROR.value,
                    context={"missing_section": section, "required_sections": required_sections}
                )

        # Validate mass_distributions
        distributions = data["mass_distributions"]
        required_dist = ["rocky", "gas_giant", "ice_giant", "dwarf"]
        for name in required_dist:
            if name not in distributions:
                raise ValidationException(
                    f"Missing mass distribution: {name}",
                    code=ErrorCode.SCHEMA_VALIDATION_ERROR.value,
                    context={"section": "mass_distributions", "missing_distribution": name, "required_distributions": required_dist}
                )

        # Validate orbit_zones
        zones = data["orbit_zones"]
        required_zones = ["hot", "habitable", "cold", "outer"]
        for name in required_zones:
            if name not in zones:
                raise ValidationException(
                    f"Missing orbit zone: {name}",
                    code=ErrorCode.SCHEMA_VALIDATION_ERROR.value,
                    context={"section": "orbit_zones", "missing_zone": name, "required_zones": required_zones}
                )

        # Validate habitable_zone
        hz = data["habitable_zone"]
        if "inner_factor" not in hz or "outer_factor" not in hz:
            raise ValidationException(
                "habitable_zone missing inner_factor or outer_factor",
                code=ErrorCode.SCHEMA_VALIDATION_ERROR.value,
                context={"section": "habitable_zone", "reason": "missing_factors", "required_keys": ["inner_factor", "outer_factor"]}
            )

        # Validate atmosphere_retention
        atm = data["atmosphere_retention"]
        if "thresholds" not in atm:
            raise ValidationException(
                "atmosphere_retention missing thresholds",
                code=ErrorCode.SCHEMA_VALIDATION_ERROR.value,
                context={"section": "atmosphere_retention", "missing_key": "thresholds"}
            )

        # Validate classification
        classification = data["classification"]
        if "mass_thresholds" not in classification:
            raise ValidationException(
                "classification missing mass_thresholds",
                code=ErrorCode.SCHEMA_VALIDATION_ERROR.value,
                context={"section": "classification", "missing_key": "mass_thresholds"}
            )
        if "temperature_thresholds" not in classification:
            raise ValidationException(
                "classification missing temperature_thresholds",
                code=ErrorCode.SCHEMA_VALIDATION_ERROR.value,
                context={"section": "classification", "missing_key": "temperature_thresholds"}
            )

        # Validate resource_generation
        res_gen = data["resource_generation"]
        for key in ["mass_scaling", "quantity", "quality", "planet_type_affinities"]:
            if key not in res_gen:
                raise ValidationException(
                    f"resource_generation missing {key}",
                    code=ErrorCode.SCHEMA_VALIDATION_ERROR.value,
                    context={"section": "resource_generation", "missing_key": key}
                )
