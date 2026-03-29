"""
Configuration for star generation parameters.

Loads star type weights, mass generation parameters, system probabilities,
companion spacing, and Stefan-Boltzmann type property tables from
astrophysics.json. Provides accessor methods for the star generation system.
"""
import logging
from typing import Dict, Any, Optional, List
from functools import lru_cache

logger = logging.getLogger(__name__)


class StarGenerationConfig:
    """
    Configuration container for star generation parameters.

    Loads values from astrophysics.json star_generation section
    or uses hardcoded defaults if the file is not available.
    """

    DEFAULT_TYPE_WEIGHTS = {
        "MAIN_SEQUENCE": 0.525,
        "RED_DWARF": 0.250,
        "RED_GIANT": 0.070,
        "BLUE_GIANT": 0.060,
        "BROWN_DWARF": 0.030,
        "WHITE_DWARF": 0.030,
        "NEUTRON_STAR": 0.020,
        "BLACK_HOLE": 0.015,
    }

    DEFAULT_MASS_GENERATION = {
        "sigma": 0.8,
        "min_mass": 0.1,
        "max_mass": 100.0,
        "max_attempts": 1000,
    }

    DEFAULT_SYSTEM_PROBABILITIES = {
        "count_thresholds": [
            {"count": 4, "cumulative": 0.001},
            {"count": 3, "cumulative": 0.011},
            {"count": 2, "cumulative": 0.111},
        ],
        "default_count": 1,
        "age_min": 0.1,
        "age_max": 10.0,
        "age_unit": 1e9,
    }

    DEFAULT_COMPANION_SPACING = {
        "ring_multiplier": 10,
        "jitter_min": 2,
        "jitter_max": 8,
        "min_offset": 2,
        "collision_limit": 100,
    }

    # Stefan-Boltzmann types: RED_GIANT, BROWN_DWARF, WHITE_DWARF
    # These share the formula: luminosity = radius^2 * (temp / SOLAR_TEMP_K)^4
    DEFAULT_STEFAN_BOLTZMANN_TYPES = {
        "RED_GIANT": {
            "mass_mode": "max",         # max(mass, uniform(min, max))
            "mass_range": (0.8, 5.0),
            "radius_power": 0.8,
            "radius_multiplier_range": (10, 100),
            "temp_range": (3000, 4500),
            "color": (255, 60, 60),
        },
        "BROWN_DWARF": {
            "mass_mode": "replace",     # uniform(min, max), ignores input
            "mass_range": (0.01, 0.08),
            "radius_power": None,       # Not mass-dependent
            "radius_range": (0.08, 0.15),
            "temp_range": (500, 2500),
            "color": (140, 60, 40),
        },
        "WHITE_DWARF": {
            "mass_mode": "clamp",       # max(min(mass, upper), lower)
            "mass_clamp_upper": 1.4,    # Chandrasekhar limit
            "mass_clamp_lower": 0.5,
            "radius_fixed": 0.01,       # Earth-sized
            "temp_range": (8000, 40000),
            "color": (220, 220, 255),
        },
    }

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        """
        Initialize configuration from JSON data or defaults.

        Args:
            data: Optional astrophysics.json data. If None, uses defaults.
        """
        if data and "star_generation" in data:
            self._load_from_json(data["star_generation"])
        else:
            self._use_defaults()

    def _load_from_json(self, star_gen: Dict[str, Any]) -> None:
        """Load parameters from JSON star_generation section."""
        tw = star_gen.get("type_weights", {})
        mg = star_gen.get("mass_generation", {})
        sp = star_gen.get("system_probabilities", {})
        cs = star_gen.get("companion_spacing", {})

        # Type weights — merge JSON over defaults
        self.type_weights = dict(self.DEFAULT_TYPE_WEIGHTS)
        self.type_weights.update(tw)

        # Mass generation
        self.mass_sigma = mg.get("sigma", self.DEFAULT_MASS_GENERATION["sigma"])
        self.mass_min = mg.get("min_mass", self.DEFAULT_MASS_GENERATION["min_mass"])
        self.mass_max = mg.get("max_mass", self.DEFAULT_MASS_GENERATION["max_mass"])
        self.mass_max_attempts = mg.get(
            "max_attempts", self.DEFAULT_MASS_GENERATION["max_attempts"]
        )

        # System probabilities
        self.system_count_thresholds = sp.get(
            "count_thresholds",
            self.DEFAULT_SYSTEM_PROBABILITIES["count_thresholds"],
        )
        self.system_default_count = sp.get(
            "default_count", self.DEFAULT_SYSTEM_PROBABILITIES["default_count"]
        )
        self.age_min = sp.get("age_min", self.DEFAULT_SYSTEM_PROBABILITIES["age_min"])
        self.age_max = sp.get("age_max", self.DEFAULT_SYSTEM_PROBABILITIES["age_max"])
        self.age_unit = sp.get("age_unit", self.DEFAULT_SYSTEM_PROBABILITIES["age_unit"])

        # Companion spacing
        self.companion_ring_multiplier = cs.get(
            "ring_multiplier", self.DEFAULT_COMPANION_SPACING["ring_multiplier"]
        )
        self.companion_jitter_min = cs.get(
            "jitter_min", self.DEFAULT_COMPANION_SPACING["jitter_min"]
        )
        self.companion_jitter_max = cs.get(
            "jitter_max", self.DEFAULT_COMPANION_SPACING["jitter_max"]
        )
        self.companion_min_offset = cs.get(
            "min_offset", self.DEFAULT_COMPANION_SPACING["min_offset"]
        )
        self.companion_collision_limit = cs.get(
            "collision_limit", self.DEFAULT_COMPANION_SPACING["collision_limit"]
        )

        # Stefan-Boltzmann types — use defaults (complex nested structure)
        self.stefan_boltzmann_types = dict(self.DEFAULT_STEFAN_BOLTZMANN_TYPES)

    def _use_defaults(self) -> None:
        """Use default hardcoded values."""
        self.type_weights = dict(self.DEFAULT_TYPE_WEIGHTS)

        self.mass_sigma = self.DEFAULT_MASS_GENERATION["sigma"]
        self.mass_min = self.DEFAULT_MASS_GENERATION["min_mass"]
        self.mass_max = self.DEFAULT_MASS_GENERATION["max_mass"]
        self.mass_max_attempts = self.DEFAULT_MASS_GENERATION["max_attempts"]

        self.system_count_thresholds = list(
            self.DEFAULT_SYSTEM_PROBABILITIES["count_thresholds"]
        )
        self.system_default_count = self.DEFAULT_SYSTEM_PROBABILITIES["default_count"]
        self.age_min = self.DEFAULT_SYSTEM_PROBABILITIES["age_min"]
        self.age_max = self.DEFAULT_SYSTEM_PROBABILITIES["age_max"]
        self.age_unit = self.DEFAULT_SYSTEM_PROBABILITIES["age_unit"]

        self.companion_ring_multiplier = self.DEFAULT_COMPANION_SPACING["ring_multiplier"]
        self.companion_jitter_min = self.DEFAULT_COMPANION_SPACING["jitter_min"]
        self.companion_jitter_max = self.DEFAULT_COMPANION_SPACING["jitter_max"]
        self.companion_min_offset = self.DEFAULT_COMPANION_SPACING["min_offset"]
        self.companion_collision_limit = self.DEFAULT_COMPANION_SPACING["collision_limit"]

        self.stefan_boltzmann_types = dict(self.DEFAULT_STEFAN_BOLTZMANN_TYPES)


@lru_cache(maxsize=1)
def get_star_generation_config() -> StarGenerationConfig:
    """
    Get the global star generation configuration (cached).

    Returns:
        StarGenerationConfig instance loaded from astrophysics.json.
    """
    try:
        from game.strategy.generation.loaders.astrophysics_loader import AstrophysicsLoader
        loader = AstrophysicsLoader()
        data = loader.load()
        return StarGenerationConfig(data)
    except (ImportError, FileNotFoundError, OSError, KeyError, TypeError, ValueError) as e:
        logger.warning(f"Failed to load star generation config: {e}")
        return StarGenerationConfig(None)
