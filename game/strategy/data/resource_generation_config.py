"""
Configuration for data-driven planet resource generation.

Loads resource generation parameters from astrophysics.json and provides
accessor methods for the planet generation system. Follows the same
pattern as ClassificationConfig.
"""
import logging
from typing import Dict, Any, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)


class ResourceGenerationConfig:
    """
    Configuration container for planet resource generation parameters.

    Loads values from astrophysics.json resource_generation section
    or uses hardcoded defaults if the file is not available.
    """

    # Hardcoded defaults matching original planet_gen.py values
    DEFAULT_MASS_SCALING = {
        "min_log_mass": 20.0,
        "max_log_mass": 28.0,
    }

    DEFAULT_QUANTITY = {
        "earth_mass_baseline": 10_000_000,
        "determinism_weight": 0.7,
        "randomness_weight": 0.3,
        "minimum_floor": 10_000,
        "ramp_c": 24.8,
    }

    DEFAULT_QUALITY = {
        "max_quality": 100.0,
        "determinism_weight": 0.7,
        "randomness_weight": 0.3,
        "minimum_floor": 5.0,
    }

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        """
        Initialize configuration from JSON data or defaults.

        Args:
            data: Optional astrophysics.json data. If None, uses defaults.
        """
        if data and "resource_generation" in data:
            self._load_from_json(data["resource_generation"])
        else:
            self._use_defaults()

    def _load_from_json(self, res_gen: Dict[str, Any]) -> None:
        """Load parameters from JSON resource_generation section."""
        mass = res_gen.get("mass_scaling", {})
        qty = res_gen.get("quantity", {})
        qual = res_gen.get("quality", {})

        # Mass scaling
        self.min_log_mass = mass.get("min_log_mass", self.DEFAULT_MASS_SCALING["min_log_mass"])
        self.max_log_mass = mass.get("max_log_mass", self.DEFAULT_MASS_SCALING["max_log_mass"])

        # Quantity parameters
        self.earth_mass_baseline = qty.get(
            "earth_mass_baseline", self.DEFAULT_QUANTITY["earth_mass_baseline"]
        )
        self.qty_determinism = qty.get(
            "determinism_weight", self.DEFAULT_QUANTITY["determinism_weight"]
        )
        self.qty_randomness = qty.get(
            "randomness_weight", self.DEFAULT_QUANTITY["randomness_weight"]
        )
        self.qty_minimum_floor = qty.get(
            "minimum_floor", self.DEFAULT_QUANTITY["minimum_floor"]
        )
        self.ramp_c = qty.get("ramp_c", self.DEFAULT_QUANTITY["ramp_c"])

        # Quality parameters
        self.max_quality = qual.get("max_quality", self.DEFAULT_QUALITY["max_quality"])
        self.qual_determinism = qual.get(
            "determinism_weight", self.DEFAULT_QUALITY["determinism_weight"]
        )
        self.qual_randomness = qual.get(
            "randomness_weight", self.DEFAULT_QUALITY["randomness_weight"]
        )
        self.qual_minimum_floor = qual.get(
            "minimum_floor", self.DEFAULT_QUALITY["minimum_floor"]
        )

        # Planet type affinities
        self._affinities = res_gen.get("planet_type_affinities", {})

    def _use_defaults(self) -> None:
        """Use default hardcoded values."""
        self.min_log_mass = self.DEFAULT_MASS_SCALING["min_log_mass"]
        self.max_log_mass = self.DEFAULT_MASS_SCALING["max_log_mass"]

        self.earth_mass_baseline = self.DEFAULT_QUANTITY["earth_mass_baseline"]
        self.qty_determinism = self.DEFAULT_QUANTITY["determinism_weight"]
        self.qty_randomness = self.DEFAULT_QUANTITY["randomness_weight"]
        self.qty_minimum_floor = self.DEFAULT_QUANTITY["minimum_floor"]
        self.ramp_c = self.DEFAULT_QUANTITY["ramp_c"]

        self.max_quality = self.DEFAULT_QUALITY["max_quality"]
        self.qual_determinism = self.DEFAULT_QUALITY["determinism_weight"]
        self.qual_randomness = self.DEFAULT_QUALITY["randomness_weight"]
        self.qual_minimum_floor = self.DEFAULT_QUALITY["minimum_floor"]

        self._affinities = {}

    def get_affinity(self, planet_type_name: str, resource_name: str) -> float:
        """
        Get the affinity multiplier for a planet type and resource.

        Args:
            planet_type_name: PlanetType enum name (e.g., "MAGMA", "JOVIAN").
            resource_name: Resource name (e.g., "Metals", "Vapors").

        Returns:
            Multiplier float. Defaults to 1.0 if not specified.
        """
        type_affinities = self._affinities.get(planet_type_name, {})
        return type_affinities.get(resource_name, 1.0)


@lru_cache(maxsize=1)
def get_resource_generation_config() -> ResourceGenerationConfig:
    """
    Get the global resource generation configuration (cached).

    Returns:
        ResourceGenerationConfig instance loaded from astrophysics.json.
    """
    try:
        from game.strategy.generation.loaders.astrophysics_loader import AstrophysicsLoader
        loader = AstrophysicsLoader()
        data = loader.load()
        return ResourceGenerationConfig(data)
    except (ImportError, FileNotFoundError, OSError, KeyError, TypeError, ValueError) as e:
        logger.warning(f"Failed to load resource generation config: {e}")
        return ResourceGenerationConfig(None)
