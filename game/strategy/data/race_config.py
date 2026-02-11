"""
Race Configuration - Data model for custom race definitions

This module provides the RaceConfig dataclass for storing and managing
race configuration data including visual selections (flags, portraits, themes),
environmental preferences, and descriptive text.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime

from game.core.json_utils import load_json, save_json


# Government types for race factions
GOVERNMENT_TYPES = [
    "Empire", "Hegemony", "Alliance", "Federation", "Republic",
    "Confederacy", "Monarchy", "Principality", "Dictatorship", "Oligarchy",
    "Theocracy", "Collective", "Hive", "Consortium"
]

# Government organization styles
GOVERNMENT_ORGANIZATIONS = [
    "Anarchy", "Democracy", "Republic", "Oligarchy", "Autocracy",
    "Theocracy", "Technocracy", "Meritocracy", "Plutocracy", "Corporatocracy",
    "Military Junta", "Tribalism", "Feudalism"
]

# Leader titles
LEADER_TITLES = [
    "Central Speaker", "Chairman", "Chancellor", "Chief", "Consul",
    "Director", "Emperor", "Empress", "First Citizen", "Grand Admiral",
    "Grand Master", "High King", "High Priest", "Imperator", "King",
    "Lord Protector", "Overlord", "President", "Prime Minister", "Primarch",
    "Prince", "Queen", "Regent", "Supreme Leader", "Tyrant",
    "Warlord", "Hierarch"
]

# Physical species types
PHYSICAL_TYPES = [
    "Felinoid", "Caninoid", "Reptilian", "Insectoid", "Avian",
    "Aquatic", "Amphibian", "Humanoid", "Silicon-Based", "Energy Being",
    "Cybernetic", "Plant-Based", "Fungoid", "Amoeboid"
]

# Society types
SOCIETY_TYPES = [
    "Artisans", "Berserkers", "Builders", "Conquerors", "Diplomats",
    "Ecologists", "Expansionists", "Explorers", "Farmers", "Industrialists",
    "Isolationists", "Merchants", "Militarists", "Pacifists", "Scientists",
    "Spiritualists", "Survivalists"
]

# Aptitude attribute names
APTITUDE_NAMES = [
    "strength", "intelligence", "constitution", "dexterity",
    "tolerance_other_species", "cooperation", "happiness",
    "population_growth", "conflict_tolerance"
]


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
    name: str = ""  # Display name (legacy, used as faction_name fallback)
    faction_name: str = ""  # Full faction name (e.g., "Rossarian Empire")
    race_name: str = ""  # Species name (e.g., "Rossarian")
    race_name_plural: str = ""  # Plural form (e.g., "Rossarians")
    government_type: str = ""  # From GOVERNMENT_TYPES
    government_organization: str = ""  # From GOVERNMENT_ORGANIZATIONS
    leader_title: str = ""  # From LEADER_TITLES
    leader_name: str = ""  # Actual name of the leader (e.g., "Zara IV")
    physical_type: str = ""  # From PHYSICAL_TYPES
    society_type: str = ""  # From SOCIETY_TYPES

    # Visual selections
    flag_id: str = ""  # Flag directory name (e.g., "flag_2fl0bh2fl0bh2fl0")
    portrait_id: str = ""  # Portrait filename
    theme_id: str = "Federation"  # Ship theme name

    # Homeworld type
    homeworld_type: str = ""  # PlanetType name (e.g., "CONTINENTAL")

    # Environmental preferences
    gravity_ideal: float = 1.0  # Ideal gravity in g (0.1-3.0)
    gravity_tolerance: float = 0.3  # Tolerance range in g (0.0-1.0)
    temperature_ideal: float = 293.0  # Ideal temperature in Kelvin (200-400)
    temperature_tolerance: float = 50.0  # Tolerance in Kelvin (0-100)

    # Water preferences
    water_ideal: float = 0.5  # Ideal water coverage (0.0-1.0)
    water_tolerance: float = 0.2  # Tolerance range (0.0-1.0)

    # Atmosphere preferences: gas name -> rating (-100 toxic to +100 beneficial)
    atmosphere_preferences: Dict[str, float] = field(
        default_factory=lambda: DEFAULT_ATMOSPHERE_PREFERENCES.copy()
    )

    # Radiation tolerance: -100 (very sensitive) to +100 (radiation resistant)
    radiation_tolerance: float = 0.0

    # Aptitude attributes (1-100 scale, 50 is average)
    aptitude_strength: int = 50
    aptitude_intelligence: int = 50
    aptitude_constitution: int = 50
    aptitude_dexterity: int = 50
    aptitude_tolerance_other_species: int = 50
    aptitude_cooperation: int = 50
    aptitude_happiness: int = 50
    aptitude_population_growth: int = 50
    aptitude_conflict_tolerance: int = 50

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

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to JSON-compatible dictionary."""
        return {
            # Identity
            "race_id": self.race_id,
            "name": self.name,
            "faction_name": self.faction_name,
            "race_name": self.race_name,
            "race_name_plural": self.race_name_plural,
            "government_type": self.government_type,
            "government_organization": self.government_organization,
            "leader_title": self.leader_title,
            "leader_name": self.leader_name,
            "physical_type": self.physical_type,
            "society_type": self.society_type,
            # Visuals
            "flag_id": self.flag_id,
            "portrait_id": self.portrait_id,
            "theme_id": self.theme_id,
            # Homeworld & Environment
            "homeworld_type": self.homeworld_type,
            "gravity_ideal": self.gravity_ideal,
            "gravity_tolerance": self.gravity_tolerance,
            "temperature_ideal": self.temperature_ideal,
            "temperature_tolerance": self.temperature_tolerance,
            "water_ideal": self.water_ideal,
            "water_tolerance": self.water_tolerance,
            "atmosphere_preferences": self.atmosphere_preferences,
            "radiation_tolerance": self.radiation_tolerance,
            # Aptitudes
            "aptitude_strength": self.aptitude_strength,
            "aptitude_intelligence": self.aptitude_intelligence,
            "aptitude_constitution": self.aptitude_constitution,
            "aptitude_dexterity": self.aptitude_dexterity,
            "aptitude_tolerance_other_species": self.aptitude_tolerance_other_species,
            "aptitude_cooperation": self.aptitude_cooperation,
            "aptitude_happiness": self.aptitude_happiness,
            "aptitude_population_growth": self.aptitude_population_growth,
            "aptitude_conflict_tolerance": self.aptitude_conflict_tolerance,
            # Descriptions
            "bio_description": self.bio_description,
            "socio_description": self.socio_description,
            # Timestamps
            "created_date": self.created_date,
            "modified_date": self.modified_date,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'RaceConfig':
        """Deserialize from dictionary with backward-compatible defaults."""
        return cls(
            # Identity
            race_id=data.get("race_id", ""),
            name=data.get("name", ""),
            faction_name=data.get("faction_name", ""),
            race_name=data.get("race_name", ""),
            race_name_plural=data.get("race_name_plural", ""),
            government_type=data.get("government_type", ""),
            government_organization=data.get("government_organization", ""),
            leader_title=data.get("leader_title", ""),
            leader_name=data.get("leader_name", ""),
            physical_type=data.get("physical_type", ""),
            society_type=data.get("society_type", ""),
            # Visuals
            flag_id=data.get("flag_id", ""),
            portrait_id=data.get("portrait_id", ""),
            theme_id=data.get("theme_id", "Federation"),
            # Homeworld & Environment
            homeworld_type=data.get("homeworld_type", ""),
            gravity_ideal=data.get("gravity_ideal", 1.0),
            gravity_tolerance=data.get("gravity_tolerance", 0.3),
            temperature_ideal=data.get("temperature_ideal", 293.0),
            temperature_tolerance=data.get("temperature_tolerance", 50.0),
            water_ideal=data.get("water_ideal", 0.5),
            water_tolerance=data.get("water_tolerance", 0.2),
            atmosphere_preferences=data.get("atmosphere_preferences",
                                            DEFAULT_ATMOSPHERE_PREFERENCES.copy()),
            radiation_tolerance=data.get("radiation_tolerance", 0.0),
            # Aptitudes
            aptitude_strength=data.get("aptitude_strength", 50),
            aptitude_intelligence=data.get("aptitude_intelligence", 50),
            aptitude_constitution=data.get("aptitude_constitution", 50),
            aptitude_dexterity=data.get("aptitude_dexterity", 50),
            aptitude_tolerance_other_species=data.get("aptitude_tolerance_other_species", 50),
            aptitude_cooperation=data.get("aptitude_cooperation", 50),
            aptitude_happiness=data.get("aptitude_happiness", 50),
            aptitude_population_growth=data.get("aptitude_population_growth", 50),
            aptitude_conflict_tolerance=data.get("aptitude_conflict_tolerance", 50),
            # Descriptions
            bio_description=data.get("bio_description", ""),
            socio_description=data.get("socio_description", ""),
            # Timestamps
            created_date=data.get("created_date", ""),
            modified_date=data.get("modified_date", ""),
        )

    def save(self, file_path: str) -> bool:
        """
        Save race configuration to JSON file.

        Args:
            file_path: Path to save the JSON file

        Returns:
            True if save succeeded, False otherwise
        """
        # Update modified timestamp
        self.modified_date = datetime.now().isoformat()

        # Set created date if not set
        if not self.created_date:
            self.created_date = self.modified_date

        return save_json(file_path, self.to_dict(), indent=2)

    @classmethod
    def load(cls, file_path: str) -> Optional['RaceConfig']:
        """
        Load race configuration from JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            RaceConfig instance or None if load failed
        """
        data = load_json(file_path)
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

        # Validate water preferences
        if not (0.0 <= self.water_ideal <= 1.0):
            return False, "Water ideal must be between 0.0 and 1.0"

        if not (0.0 <= self.water_tolerance <= 1.0):
            return False, "Water tolerance must be between 0.0 and 1.0"

        # Validate aptitudes (1-100 range)
        aptitude_fields = [
            ("strength", self.aptitude_strength),
            ("intelligence", self.aptitude_intelligence),
            ("constitution", self.aptitude_constitution),
            ("dexterity", self.aptitude_dexterity),
            ("tolerance_other_species", self.aptitude_tolerance_other_species),
            ("cooperation", self.aptitude_cooperation),
            ("happiness", self.aptitude_happiness),
            ("population_growth", self.aptitude_population_growth),
            ("conflict_tolerance", self.aptitude_conflict_tolerance),
        ]
        for apt_name, apt_value in aptitude_fields:
            if not (1 <= apt_value <= 100):
                return False, f"Aptitude {apt_name} must be between 1 and 100"

        # Validate identity fields if set (optional, but must be valid if provided)
        if self.government_type and self.government_type not in GOVERNMENT_TYPES:
            return False, f"Invalid government type: {self.government_type}"

        if self.government_organization and self.government_organization not in GOVERNMENT_ORGANIZATIONS:
            return False, f"Invalid government organization: {self.government_organization}"

        if self.leader_title and self.leader_title not in LEADER_TITLES:
            return False, f"Invalid leader title: {self.leader_title}"

        if self.physical_type and self.physical_type not in PHYSICAL_TYPES:
            return False, f"Invalid physical type: {self.physical_type}"

        if self.society_type and self.society_type not in SOCIETY_TYPES:
            return False, f"Invalid society type: {self.society_type}"

        # Validate homeworld type if set
        if self.homeworld_type:
            from game.strategy.data.planet import PlanetType
            valid_planet_types = [p.name for p in PlanetType]
            if self.homeworld_type not in valid_planet_types:
                return False, f"Invalid homeworld type: {self.homeworld_type}"

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
