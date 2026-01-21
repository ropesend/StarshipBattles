"""
Race Configuration - Data model for custom race definitions

This module provides the RaceConfig dataclass for storing and managing
race configuration data including visual selections (flags, portraits, themes),
environmental preferences, and descriptive text.
"""
from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime

from game.core.json_utils import load_json, save_json


# Default atmosphere gases with neutral preferences
DEFAULT_ATMOSPHERE_PREFERENCES = {
    "Oxygen": 0.0,
    "Nitrogen": 0.0,
    "Carbon Dioxide": 0.0,
    "Methane": 0.0,
    "Hydrogen": 0.0,
    "Helium": 0.0,
}


@dataclass
class RaceConfig:
    """
    Configuration for a custom playable race/faction.

    Stores all race customization options including visual identity,
    environmental preferences, and descriptive text.
    """
    # Identity
    race_id: str = ""  # Unique identifier (generated if empty)
    name: str = ""  # Display name

    # Visual selections
    flag_id: str = ""  # Flag directory name (e.g., "flag_2fl0bh2fl0bh2fl0")
    portrait_id: str = ""  # Portrait filename
    theme_id: str = "Federation"  # Ship theme name

    # Environmental preferences
    gravity_ideal: float = 1.0  # Ideal gravity in g (0.1-3.0)
    gravity_tolerance: float = 0.3  # Tolerance range in g (0.0-1.0)
    temperature_ideal: float = 293.0  # Ideal temperature in Kelvin (200-400)
    temperature_tolerance: float = 50.0  # Tolerance in Kelvin (0-100)

    # Atmosphere preferences: gas name -> rating (-100 toxic to +100 beneficial)
    atmosphere_preferences: Dict[str, float] = field(
        default_factory=lambda: DEFAULT_ATMOSPHERE_PREFERENCES.copy()
    )

    # Radiation tolerance: -100 (very sensitive) to +100 (radiation resistant)
    radiation_tolerance: float = 0.0

    # Descriptions
    bio_description: str = ""  # Biological description (max 500 chars)
    socio_description: str = ""  # Sociological description (max 500 chars)

    # Timestamps
    created_date: str = ""  # ISO timestamp
    modified_date: str = ""  # ISO timestamp

    def __post_init__(self):
        """Ensure atmosphere_preferences has all required keys."""
        if self.atmosphere_preferences is None:
            self.atmosphere_preferences = DEFAULT_ATMOSPHERE_PREFERENCES.copy()
        else:
            # Ensure all default gases are present
            for gas in DEFAULT_ATMOSPHERE_PREFERENCES:
                if gas not in self.atmosphere_preferences:
                    self.atmosphere_preferences[gas] = 0.0

    def to_dict(self) -> dict:
        """Serialize to JSON-compatible dictionary."""
        return {
            "race_id": self.race_id,
            "name": self.name,
            "flag_id": self.flag_id,
            "portrait_id": self.portrait_id,
            "theme_id": self.theme_id,
            "gravity_ideal": self.gravity_ideal,
            "gravity_tolerance": self.gravity_tolerance,
            "temperature_ideal": self.temperature_ideal,
            "temperature_tolerance": self.temperature_tolerance,
            "atmosphere_preferences": self.atmosphere_preferences,
            "radiation_tolerance": self.radiation_tolerance,
            "bio_description": self.bio_description,
            "socio_description": self.socio_description,
            "created_date": self.created_date,
            "modified_date": self.modified_date,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'RaceConfig':
        """Deserialize from dictionary."""
        return cls(
            race_id=data.get("race_id", ""),
            name=data.get("name", ""),
            flag_id=data.get("flag_id", ""),
            portrait_id=data.get("portrait_id", ""),
            theme_id=data.get("theme_id", "Federation"),
            gravity_ideal=data.get("gravity_ideal", 1.0),
            gravity_tolerance=data.get("gravity_tolerance", 0.3),
            temperature_ideal=data.get("temperature_ideal", 293.0),
            temperature_tolerance=data.get("temperature_tolerance", 50.0),
            atmosphere_preferences=data.get("atmosphere_preferences",
                                            DEFAULT_ATMOSPHERE_PREFERENCES.copy()),
            radiation_tolerance=data.get("radiation_tolerance", 0.0),
            bio_description=data.get("bio_description", ""),
            socio_description=data.get("socio_description", ""),
            created_date=data.get("created_date", ""),
            modified_date=data.get("modified_date", ""),
        )

    def save(self, filepath: str) -> bool:
        """
        Save race configuration to JSON file.

        Args:
            filepath: Path to save the JSON file

        Returns:
            True if save succeeded, False otherwise
        """
        # Update modified timestamp
        self.modified_date = datetime.now().isoformat()

        # Set created date if not set
        if not self.created_date:
            self.created_date = self.modified_date

        return save_json(filepath, self.to_dict(), indent=2)

    @classmethod
    def load(cls, filepath: str) -> Optional['RaceConfig']:
        """
        Load race configuration from JSON file.

        Args:
            filepath: Path to the JSON file

        Returns:
            RaceConfig instance or None if load failed
        """
        data = load_json(filepath)
        if data is None:
            return None
        return cls.from_dict(data)

    def validate(self) -> tuple[bool, str]:
        """
        Validate the race configuration.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.name or not self.name.strip():
            return False, "Race name is required"

        if not self.flag_id:
            return False, "Flag selection is required"

        if not self.portrait_id:
            return False, "Portrait selection is required"

        if not self.theme_id:
            return False, "Ship theme selection is required"

        # Validate ranges
        if not (0.1 <= self.gravity_ideal <= 3.0):
            return False, "Gravity ideal must be between 0.1 and 3.0"

        if not (0.0 <= self.gravity_tolerance <= 1.0):
            return False, "Gravity tolerance must be between 0.0 and 1.0"

        if not (200 <= self.temperature_ideal <= 400):
            return False, "Temperature ideal must be between 200K and 400K"

        if not (0 <= self.temperature_tolerance <= 100):
            return False, "Temperature tolerance must be between 0 and 100K"

        if not (-100 <= self.radiation_tolerance <= 100):
            return False, "Radiation tolerance must be between -100 and 100"

        # Validate atmosphere preferences
        for gas, value in self.atmosphere_preferences.items():
            if not (-100 <= value <= 100):
                return False, f"Atmosphere preference for {gas} must be between -100 and 100"

        # Validate description lengths
        if len(self.bio_description) > 500:
            return False, "Biological description exceeds 500 characters"

        if len(self.socio_description) > 500:
            return False, "Sociological description exceeds 500 characters"

        return True, ""

    def is_complete(self) -> bool:
        """Check if all required fields are filled."""
        is_valid, _ = self.validate()
        return is_valid
