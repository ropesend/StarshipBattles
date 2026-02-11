"""
Classification configuration for planet type determination.

Loads classification thresholds from astrophysics.json and provides
convenient accessor methods for the planet generation system.
"""
from typing import Dict, Any, Optional
from functools import lru_cache


class ClassificationConfig:
    """
    Configuration container for planet classification thresholds.

    Loads values from astrophysics.json or uses hardcoded defaults
    if the file is not available.
    """

    # Hardcoded defaults matching original planet_gen.py values
    # Used if JSON loading fails
    DEFAULT_MASS = {
        "dwarf_max": 2.0e23,
        "giant_min": 6.0e24,
        "gas_giant_min": 1.0e26,
    }

    DEFAULT_TEMPERATURE = {
        "ice_dwarf_max": 170,
        "cryo_max": 255,
        "cold_limit": 200,
        "magma": 700,
        "magma_activity": 350,  # temp > 350 and activity > 0.7
        "hot_limit": 400,
        "continental_min": 255,
        "continental_max": 330,
    }

    DEFAULT_PRESSURE = {
        "vacuum": 500,
        "chthonian_max": 10000,
        "continental_min": 5000,
    }

    DEFAULT_WATER = {
        "arid": 0.20,
        "ocean_world": 0.85,
        "continental_min": 0.10,
    }

    DEFAULT_ACTIVITY = {
        "magma_threshold": 0.7,
    }

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        """
        Initialize configuration from JSON data or defaults.

        Args:
            data: Optional astrophysics.json data. If None, uses defaults.
        """
        if data and "classification" in data:
            self._load_from_json(data["classification"])
        else:
            self._use_defaults()

    def _load_from_json(self, classification: Dict[str, Any]) -> None:
        """Load thresholds from JSON classification section."""
        mass = classification.get("mass_thresholds", {})
        temp = classification.get("temperature_thresholds", {})
        pressure = classification.get("pressure_thresholds", {})
        water = classification.get("water_coverage_thresholds", {})

        # Mass thresholds
        self.dwarf_max = mass.get("dwarf_max", self.DEFAULT_MASS["dwarf_max"])
        self.giant_min = mass.get("giant_min", self.DEFAULT_MASS["giant_min"])
        self.gas_giant_min = mass.get("gas_giant_min", self.DEFAULT_MASS["gas_giant_min"])

        # Temperature thresholds
        self.ice_dwarf_max = temp.get("ice_dwarf_max", self.DEFAULT_TEMPERATURE["ice_dwarf_max"])
        self.cryo_max = temp.get("cryo_max", self.DEFAULT_TEMPERATURE["cryo_max"])
        self.cold_limit = temp.get("cold_limit", self.DEFAULT_TEMPERATURE["cold_limit"])
        self.magma = temp.get("magma", self.DEFAULT_TEMPERATURE["magma"])
        self.magma_activity = temp.get("magma_activity", self.DEFAULT_TEMPERATURE["magma_activity"])
        self.hot_limit = temp.get("hot_limit", self.DEFAULT_TEMPERATURE["hot_limit"])
        self.continental_temp_min = temp.get("continental_min", self.DEFAULT_TEMPERATURE["continental_min"])
        self.continental_temp_max = temp.get("continental_max", self.DEFAULT_TEMPERATURE["continental_max"])

        # Pressure thresholds
        self.vacuum = pressure.get("vacuum", self.DEFAULT_PRESSURE["vacuum"])
        self.chthonian_max = pressure.get("chthonian_max", self.DEFAULT_PRESSURE["chthonian_max"])
        self.continental_pressure_min = pressure.get("continental_min", self.DEFAULT_PRESSURE["continental_min"])

        # Water thresholds
        self.arid = water.get("arid", self.DEFAULT_WATER["arid"])
        self.ocean_world = water.get("ocean_world", self.DEFAULT_WATER["ocean_world"])
        self.continental_water_min = water.get("continental_min", self.DEFAULT_WATER["continental_min"])

        # Activity threshold
        self.activity_magma_threshold = self.DEFAULT_ACTIVITY["magma_threshold"]

    def _use_defaults(self) -> None:
        """Use default hardcoded values."""
        self.dwarf_max = self.DEFAULT_MASS["dwarf_max"]
        self.giant_min = self.DEFAULT_MASS["giant_min"]
        self.gas_giant_min = self.DEFAULT_MASS["gas_giant_min"]

        self.ice_dwarf_max = self.DEFAULT_TEMPERATURE["ice_dwarf_max"]
        self.cryo_max = self.DEFAULT_TEMPERATURE["cryo_max"]
        self.cold_limit = self.DEFAULT_TEMPERATURE["cold_limit"]
        self.magma = self.DEFAULT_TEMPERATURE["magma"]
        self.magma_activity = self.DEFAULT_TEMPERATURE["magma_activity"]
        self.hot_limit = self.DEFAULT_TEMPERATURE["hot_limit"]
        self.continental_temp_min = self.DEFAULT_TEMPERATURE["continental_min"]
        self.continental_temp_max = self.DEFAULT_TEMPERATURE["continental_max"]

        self.vacuum = self.DEFAULT_PRESSURE["vacuum"]
        self.chthonian_max = self.DEFAULT_PRESSURE["chthonian_max"]
        self.continental_pressure_min = self.DEFAULT_PRESSURE["continental_min"]

        self.arid = self.DEFAULT_WATER["arid"]
        self.ocean_world = self.DEFAULT_WATER["ocean_world"]
        self.continental_water_min = self.DEFAULT_WATER["continental_min"]

        self.activity_magma_threshold = self.DEFAULT_ACTIVITY["magma_threshold"]


@lru_cache(maxsize=1)
def get_classification_config() -> ClassificationConfig:
    """
    Get the global classification configuration (cached).

    Returns:
        ClassificationConfig instance loaded from astrophysics.json.
    """
    try:
        from game.strategy.generation.loaders.astrophysics_loader import AstrophysicsLoader
        loader = AstrophysicsLoader()
        data = loader.load()
        return ClassificationConfig(data)
    except (ImportError, FileNotFoundError, OSError, KeyError, TypeError, ValueError) as e:
        # Fall back to defaults if loading fails
        from game.core.logger import log_warning
        log_warning(f"Failed to load classification config: {e}")
        return ClassificationConfig(None)
