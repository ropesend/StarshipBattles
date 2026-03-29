"""
Configuration for planet orbital generation parameters.

Loads orbital slot placement, mass distribution, moon system, and surface
flag parameters from astrophysics.json. Provides accessor methods for the
planet generation system.
"""
import logging
from typing import Dict, Any, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)


class OrbitalGenerationConfig:
    """
    Configuration container for planet orbital generation parameters.

    Loads values from astrophysics.json orbital_generation section
    or uses hardcoded defaults if the file is not available.
    """

    DEFAULT_ORBITAL = {
        "safe_start_offset": 2,
        "max_orbital_distance": 20,
        "default_planet_min": 3,
        "default_planet_max": 10,
        "orbital_distribution_mode": 0.3,
        "max_placement_attempts": 20,
        "hot_jupiter_log_mass_min": 26.7,
        "hot_jupiter_log_mass_max": 28.0,
        "hot_jupiter_orbit_min": 2,
        "hot_jupiter_orbit_max": 3,
    }

    DEFAULT_MASS_GENERATION = {
        "small_bias_mu": 24.0,
        "small_bias_sigma": 0.8,
        "large_bias_mu": 26.5,
        "large_bias_sigma": 0.8,
        "default_mu": 24.0,
        "default_sigma": 1.0,
        "max_iterations": 100,
    }

    DEFAULT_MOON_SYSTEM = {
        "jupiter_threshold_log": 27.27,
        "earth_threshold_log": 24.77,
        "ceres_threshold_log": 20.97,
        "jupiter_chance": 0.88,
        "earth_chance": 0.35,
        "ceres_chance": 0.02,
        "max_chance_cap": 0.95,
        "mass_ratio_min": 0.00001,
        "mass_ratio_max": 0.05,
        "max_moons_per_body": 50,
    }

    DEFAULT_SURFACE = {
        "active_body_activity_min": 0.1,
        "active_body_activity_max": 0.8,
        "active_body_mag_min": 0.5,
        "active_body_mag_max": 2.0,
        "small_body_activity_min": 0.0,
        "small_body_activity_max": 0.2,
        "small_body_mag_min": 0.0,
        "small_body_mag_max": 0.5,
        "water_temp_min": 250,
        "water_temp_max": 350,
    }

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        """
        Initialize configuration from JSON data or defaults.

        Args:
            data: Optional astrophysics.json data. If None, uses defaults.
        """
        if data and "orbital_generation" in data:
            self._load_from_json(data["orbital_generation"])
        else:
            self._use_defaults()

    def _load_from_json(self, orbital_gen: Dict[str, Any]) -> None:
        """Load parameters from JSON orbital_generation section."""
        orb = orbital_gen.get("orbital", {})
        mg = orbital_gen.get("mass_generation", {})
        ms = orbital_gen.get("moon_system", {})
        sf = orbital_gen.get("surface", {})

        # Orbital parameters
        self.safe_start_offset = orb.get("safe_start_offset", self.DEFAULT_ORBITAL["safe_start_offset"])
        self.max_orbital_distance = orb.get("max_orbital_distance", self.DEFAULT_ORBITAL["max_orbital_distance"])
        self.default_planet_min = orb.get("default_planet_min", self.DEFAULT_ORBITAL["default_planet_min"])
        self.default_planet_max = orb.get("default_planet_max", self.DEFAULT_ORBITAL["default_planet_max"])
        self.orbital_distribution_mode = orb.get("orbital_distribution_mode", self.DEFAULT_ORBITAL["orbital_distribution_mode"])
        self.max_placement_attempts = orb.get("max_placement_attempts", self.DEFAULT_ORBITAL["max_placement_attempts"])
        self.hot_jupiter_log_mass_min = orb.get("hot_jupiter_log_mass_min", self.DEFAULT_ORBITAL["hot_jupiter_log_mass_min"])
        self.hot_jupiter_log_mass_max = orb.get("hot_jupiter_log_mass_max", self.DEFAULT_ORBITAL["hot_jupiter_log_mass_max"])
        self.hot_jupiter_orbit_min = orb.get("hot_jupiter_orbit_min", self.DEFAULT_ORBITAL["hot_jupiter_orbit_min"])
        self.hot_jupiter_orbit_max = orb.get("hot_jupiter_orbit_max", self.DEFAULT_ORBITAL["hot_jupiter_orbit_max"])

        # Mass generation
        self.small_bias_mu = mg.get("small_bias_mu", self.DEFAULT_MASS_GENERATION["small_bias_mu"])
        self.small_bias_sigma = mg.get("small_bias_sigma", self.DEFAULT_MASS_GENERATION["small_bias_sigma"])
        self.large_bias_mu = mg.get("large_bias_mu", self.DEFAULT_MASS_GENERATION["large_bias_mu"])
        self.large_bias_sigma = mg.get("large_bias_sigma", self.DEFAULT_MASS_GENERATION["large_bias_sigma"])
        self.default_mu = mg.get("default_mu", self.DEFAULT_MASS_GENERATION["default_mu"])
        self.default_sigma = mg.get("default_sigma", self.DEFAULT_MASS_GENERATION["default_sigma"])
        self.mass_max_iterations = mg.get("max_iterations", self.DEFAULT_MASS_GENERATION["max_iterations"])

        # Moon system
        self.jupiter_threshold_log = ms.get("jupiter_threshold_log", self.DEFAULT_MOON_SYSTEM["jupiter_threshold_log"])
        self.earth_threshold_log = ms.get("earth_threshold_log", self.DEFAULT_MOON_SYSTEM["earth_threshold_log"])
        self.ceres_threshold_log = ms.get("ceres_threshold_log", self.DEFAULT_MOON_SYSTEM["ceres_threshold_log"])
        self.jupiter_chance = ms.get("jupiter_chance", self.DEFAULT_MOON_SYSTEM["jupiter_chance"])
        self.earth_chance = ms.get("earth_chance", self.DEFAULT_MOON_SYSTEM["earth_chance"])
        self.ceres_chance = ms.get("ceres_chance", self.DEFAULT_MOON_SYSTEM["ceres_chance"])
        self.max_chance_cap = ms.get("max_chance_cap", self.DEFAULT_MOON_SYSTEM["max_chance_cap"])
        self.mass_ratio_min = ms.get("mass_ratio_min", self.DEFAULT_MOON_SYSTEM["mass_ratio_min"])
        self.mass_ratio_max = ms.get("mass_ratio_max", self.DEFAULT_MOON_SYSTEM["mass_ratio_max"])
        self.max_moons_per_body = ms.get("max_moons_per_body", self.DEFAULT_MOON_SYSTEM["max_moons_per_body"])

        # Surface flags
        self.active_body_activity_min = sf.get("active_body_activity_min", self.DEFAULT_SURFACE["active_body_activity_min"])
        self.active_body_activity_max = sf.get("active_body_activity_max", self.DEFAULT_SURFACE["active_body_activity_max"])
        self.active_body_mag_min = sf.get("active_body_mag_min", self.DEFAULT_SURFACE["active_body_mag_min"])
        self.active_body_mag_max = sf.get("active_body_mag_max", self.DEFAULT_SURFACE["active_body_mag_max"])
        self.small_body_activity_min = sf.get("small_body_activity_min", self.DEFAULT_SURFACE["small_body_activity_min"])
        self.small_body_activity_max = sf.get("small_body_activity_max", self.DEFAULT_SURFACE["small_body_activity_max"])
        self.small_body_mag_min = sf.get("small_body_mag_min", self.DEFAULT_SURFACE["small_body_mag_min"])
        self.small_body_mag_max = sf.get("small_body_mag_max", self.DEFAULT_SURFACE["small_body_mag_max"])
        self.water_temp_min = sf.get("water_temp_min", self.DEFAULT_SURFACE["water_temp_min"])
        self.water_temp_max = sf.get("water_temp_max", self.DEFAULT_SURFACE["water_temp_max"])

    def _use_defaults(self) -> None:
        """Use default hardcoded values."""
        self.safe_start_offset = self.DEFAULT_ORBITAL["safe_start_offset"]
        self.max_orbital_distance = self.DEFAULT_ORBITAL["max_orbital_distance"]
        self.default_planet_min = self.DEFAULT_ORBITAL["default_planet_min"]
        self.default_planet_max = self.DEFAULT_ORBITAL["default_planet_max"]
        self.orbital_distribution_mode = self.DEFAULT_ORBITAL["orbital_distribution_mode"]
        self.max_placement_attempts = self.DEFAULT_ORBITAL["max_placement_attempts"]
        self.hot_jupiter_log_mass_min = self.DEFAULT_ORBITAL["hot_jupiter_log_mass_min"]
        self.hot_jupiter_log_mass_max = self.DEFAULT_ORBITAL["hot_jupiter_log_mass_max"]
        self.hot_jupiter_orbit_min = self.DEFAULT_ORBITAL["hot_jupiter_orbit_min"]
        self.hot_jupiter_orbit_max = self.DEFAULT_ORBITAL["hot_jupiter_orbit_max"]

        self.small_bias_mu = self.DEFAULT_MASS_GENERATION["small_bias_mu"]
        self.small_bias_sigma = self.DEFAULT_MASS_GENERATION["small_bias_sigma"]
        self.large_bias_mu = self.DEFAULT_MASS_GENERATION["large_bias_mu"]
        self.large_bias_sigma = self.DEFAULT_MASS_GENERATION["large_bias_sigma"]
        self.default_mu = self.DEFAULT_MASS_GENERATION["default_mu"]
        self.default_sigma = self.DEFAULT_MASS_GENERATION["default_sigma"]
        self.mass_max_iterations = self.DEFAULT_MASS_GENERATION["max_iterations"]

        self.jupiter_threshold_log = self.DEFAULT_MOON_SYSTEM["jupiter_threshold_log"]
        self.earth_threshold_log = self.DEFAULT_MOON_SYSTEM["earth_threshold_log"]
        self.ceres_threshold_log = self.DEFAULT_MOON_SYSTEM["ceres_threshold_log"]
        self.jupiter_chance = self.DEFAULT_MOON_SYSTEM["jupiter_chance"]
        self.earth_chance = self.DEFAULT_MOON_SYSTEM["earth_chance"]
        self.ceres_chance = self.DEFAULT_MOON_SYSTEM["ceres_chance"]
        self.max_chance_cap = self.DEFAULT_MOON_SYSTEM["max_chance_cap"]
        self.mass_ratio_min = self.DEFAULT_MOON_SYSTEM["mass_ratio_min"]
        self.mass_ratio_max = self.DEFAULT_MOON_SYSTEM["mass_ratio_max"]
        self.max_moons_per_body = self.DEFAULT_MOON_SYSTEM["max_moons_per_body"]

        self.active_body_activity_min = self.DEFAULT_SURFACE["active_body_activity_min"]
        self.active_body_activity_max = self.DEFAULT_SURFACE["active_body_activity_max"]
        self.active_body_mag_min = self.DEFAULT_SURFACE["active_body_mag_min"]
        self.active_body_mag_max = self.DEFAULT_SURFACE["active_body_mag_max"]
        self.small_body_activity_min = self.DEFAULT_SURFACE["small_body_activity_min"]
        self.small_body_activity_max = self.DEFAULT_SURFACE["small_body_activity_max"]
        self.small_body_mag_min = self.DEFAULT_SURFACE["small_body_mag_min"]
        self.small_body_mag_max = self.DEFAULT_SURFACE["small_body_mag_max"]
        self.water_temp_min = self.DEFAULT_SURFACE["water_temp_min"]
        self.water_temp_max = self.DEFAULT_SURFACE["water_temp_max"]


@lru_cache(maxsize=1)
def get_orbital_generation_config() -> OrbitalGenerationConfig:
    """
    Get the global orbital generation configuration (cached).

    Returns:
        OrbitalGenerationConfig instance loaded from astrophysics.json.
    """
    try:
        from game.strategy.generation.loaders.astrophysics_loader import AstrophysicsLoader
        loader = AstrophysicsLoader()
        data = loader.load()
        return OrbitalGenerationConfig(data)
    except (ImportError, FileNotFoundError, OSError, KeyError, TypeError, ValueError) as e:
        logger.warning(f"Failed to load orbital generation config: {e}")
        return OrbitalGenerationConfig(None)
