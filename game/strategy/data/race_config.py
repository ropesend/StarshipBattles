"""
Race Configuration - Data model for custom race definitions

This module provides the RaceConfig dataclass for storing and managing
race configuration data including visual selections (flags, portraits, themes),
environmental preferences, and descriptive text.

PROJ-283 Phase 4: deleted the legacy `gravity_ideal/_tolerance`,
`temperature_ideal/_tolerance`, `water_ideal/_tolerance`,
`atmosphere_preferences`, `radiation_tolerance`, `aptitude_happiness`,
`aptitude_population_growth` fields. Environmental preferences are now
expressed via `preferences: Dict[str, EnvironmentalPreference]` keyed by
`FACTOR_REGISTRY` ids; reproduction & happiness via `base_reproduction_rate`
and `base_happiness`.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime

from game.core.json_utils import load_json, save_json
from game.core.validation import ValidationResult
from game.strategy.data.environmental_preference import EnvironmentalPreference
from game.strategy.data.habitability_factors import FACTOR_REGISTRY


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

# Aptitude attribute names (the 7 paid aptitudes after PROJ-283 dropped
# `happiness` and `population_growth`).
APTITUDE_NAMES = [
    "strength", "intelligence", "constitution", "dexterity",
    "tolerance_other_species", "cooperation", "conflict_tolerance"
]


# Mapping kept for the few callers that still translate between display
# names and chemical formulas (UI labels, race randomizer presets).
# Phase 5 UI rebuild will likely retire most of these usages.
GAS_NAME_TO_FORMULA = {
    "Oxygen": "O2",
    "Nitrogen": "N2",
    "Carbon Dioxide": "CO2",
    "Methane": "CH4",
    "Hydrogen": "H2",
    "Helium": "He",
}

# Reverse mapping: chemical formula -> display name
GAS_FORMULA_TO_NAME = {v: k for k, v in GAS_NAME_TO_FORMULA.items()}


@dataclass
class RaceConfig:
    """
    Configuration for a custom playable race/faction.

    Stores all race customization options including visual identity,
    environmental preferences, and descriptive text.
    """
    # Identity
    race_id: str = ""  # Unique identifier (generated if empty)
    name: str = ""  # Primary display name; used as fallback for faction_name and race_name
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

    # Aptitude attributes (1-100 scale, 50 is average) — 7 paid aptitudes
    # after PROJ-283 dropped `happiness` and `population_growth` (now
    # expressed via `base_happiness` and `base_reproduction_rate`).
    aptitude_strength: int = 50
    aptitude_intelligence: int = 50
    aptitude_constitution: int = 50
    aptitude_dexterity: int = 50
    aptitude_tolerance_other_species: int = 50
    aptitude_cooperation: int = 50
    aptitude_conflict_tolerance: int = 50

    # PROJ-283: Registry-driven environmental preferences. Populated from
    # FACTOR_REGISTRY defaults in __post_init__ when not explicitly
    # supplied. Replaces the legacy field pairs that lived here pre-Phase 4.
    preferences: Dict[str, EnvironmentalPreference] = field(default_factory=dict)

    # PROJ-283: Replaces aptitude_population_growth. 0.03 = 3%/turn base
    # reproduction. Exponential cost to raise; linear refund to 0.5% floor.
    base_reproduction_rate: float = 0.03

    # PROJ-283: Replaces aptitude_happiness. Seed value for the (PROJ-284)
    # derived-happiness engine. 0.5 = neutral disposition.
    base_happiness: float = 0.5

    # Descriptions
    bio_description: str = ""  # Biological description (max 500 chars)
    socio_description: str = ""  # Sociological description (max 500 chars)

    # Timestamps
    created_date: str = ""  # ISO timestamp
    modified_date: str = ""  # ISO timestamp

    def __post_init__(self):
        """Backfill missing `preferences` entries from FACTOR_REGISTRY defaults."""
        if self.preferences is None:
            self.preferences = {}
        for factor_id, factor in FACTOR_REGISTRY.items():
            if factor_id not in self.preferences:
                self.preferences[factor_id] = EnvironmentalPreference(
                    setpoint=factor.default_setpoint,
                    tolerance=factor.default_tolerance,
                    min_value=factor.min_value,
                    max_value=factor.max_value,
                    step=factor.step,
                )

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
            # Homeworld
            "homeworld_type": self.homeworld_type,
            # Aptitudes (7 paid)
            "aptitude_strength": self.aptitude_strength,
            "aptitude_intelligence": self.aptitude_intelligence,
            "aptitude_constitution": self.aptitude_constitution,
            "aptitude_dexterity": self.aptitude_dexterity,
            "aptitude_tolerance_other_species": self.aptitude_tolerance_other_species,
            "aptitude_cooperation": self.aptitude_cooperation,
            "aptitude_conflict_tolerance": self.aptitude_conflict_tolerance,
            # PROJ-283 environment + repro/happiness
            "preferences": {
                factor_id: pref.to_dict()
                for factor_id, pref in self.preferences.items()
            },
            "base_reproduction_rate": self.base_reproduction_rate,
            "base_happiness": self.base_happiness,
            # Descriptions
            "bio_description": self.bio_description,
            "socio_description": self.socio_description,
            # Timestamps
            "created_date": self.created_date,
            "modified_date": self.modified_date,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'RaceConfig':
        """Deserialize from dictionary.

        PROJ-283 Phase 4: legacy environment/aptitude keys (`gravity_ideal`,
        `atmosphere_preferences`, `aptitude_happiness`, ...) are silently
        ignored if present in old save files. Per CLAUDE.md System Migration
        Policy, save files are disposable — no migration shim is provided.
        """
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
            # Homeworld
            homeworld_type=data.get("homeworld_type", ""),
            # Aptitudes
            aptitude_strength=data.get("aptitude_strength", 50),
            aptitude_intelligence=data.get("aptitude_intelligence", 50),
            aptitude_constitution=data.get("aptitude_constitution", 50),
            aptitude_dexterity=data.get("aptitude_dexterity", 50),
            aptitude_tolerance_other_species=data.get("aptitude_tolerance_other_species", 50),
            aptitude_cooperation=data.get("aptitude_cooperation", 50),
            aptitude_conflict_tolerance=data.get("aptitude_conflict_tolerance", 50),
            # PROJ-283 fields
            preferences={
                factor_id: EnvironmentalPreference.from_dict(pref_data)
                for factor_id, pref_data in (data.get("preferences") or {}).items()
            },
            base_reproduction_rate=float(data.get("base_reproduction_rate", 0.03)),
            base_happiness=float(data.get("base_happiness", 0.5)),
            # Descriptions
            bio_description=data.get("bio_description", ""),
            socio_description=data.get("socio_description", ""),
            # Timestamps
            created_date=data.get("created_date", ""),
            modified_date=data.get("modified_date", ""),
        )

    def save(self, file_path: str) -> bool:
        """Save race configuration to JSON file."""
        self.modified_date = datetime.now().isoformat()
        if not self.created_date:
            self.created_date = self.modified_date
        return save_json(file_path, self.to_dict(), indent=2)

    @classmethod
    def load(cls, file_path: str) -> Optional['RaceConfig']:
        """Load race configuration from JSON file."""
        data = load_json(file_path)
        if data is None:
            return None
        return cls.from_dict(data)

    def validate(self) -> ValidationResult:
        """Validate the race configuration."""
        result = ValidationResult.success()
        for check in [
            self._validate_required_fields,
            self._validate_aptitudes,
            self._validate_identity_enums,
            self._validate_homeworld,
            self._validate_descriptions,
            self._validate_preferences,
            self._validate_reproduction_and_happiness,
        ]:
            ok, msg = check()
            if not ok:
                result.add_error(msg)
                return result
        return result

    # -- validation helpers (private) --

    _IDENTITY_ENUM_CHECKS = [
        ("government_type", GOVERNMENT_TYPES, "government type"),
        ("government_organization", GOVERNMENT_ORGANIZATIONS, "government organization"),
        ("leader_title", LEADER_TITLES, "leader title"),
        ("physical_type", PHYSICAL_TYPES, "physical type"),
        ("society_type", SOCIETY_TYPES, "society type"),
    ]

    def _validate_required_fields(self) -> tuple[bool, str]:
        if not self.name or not self.name.strip():
            return False, "Race name is required"
        if not self.flag_id:
            return False, "Flag selection is required"
        if not self.portrait_id:
            return False, "Portrait selection is required"
        if not self.theme_id:
            return False, "Ship theme selection is required"
        return True, ""

    def _validate_aptitudes(self) -> tuple[bool, str]:
        for apt_name in APTITUDE_NAMES:
            value = getattr(self, f"aptitude_{apt_name}")
            if not (1 <= value <= 100):
                return False, f"Aptitude {apt_name} must be between 1 and 100"
        return True, ""

    def _validate_identity_enums(self) -> tuple[bool, str]:
        for attr, valid_list, label in self._IDENTITY_ENUM_CHECKS:
            value = getattr(self, attr)
            if value and value not in valid_list:
                return False, f"Invalid {label}: {value}"
        return True, ""

    def _validate_homeworld(self) -> tuple[bool, str]:
        if self.homeworld_type:
            from game.strategy.data.planet import PlanetType
            valid_planet_types = [p.name for p in PlanetType]
            if self.homeworld_type not in valid_planet_types:
                return False, f"Invalid homeworld type: {self.homeworld_type}"
        return True, ""

    def _validate_descriptions(self) -> tuple[bool, str]:
        if len(self.bio_description) > 500:
            return False, "Biological description exceeds 500 characters"
        if len(self.socio_description) > 500:
            return False, "Sociological description exceeds 500 characters"
        return True, ""

    def _validate_preferences(self) -> tuple[bool, str]:
        """PROJ-283: Each EnvironmentalPreference self-validates at construction,
        so this only defends against preferences that have been mutated
        in-place to invalid values after creation."""
        from game.core.exceptions import ValidationException
        for factor_id, pref in self.preferences.items():
            try:
                pref.validate()
            except ValidationException as exc:
                return False, f"preferences[{factor_id!r}]: {exc}"
        return True, ""

    def _validate_reproduction_and_happiness(self) -> tuple[bool, str]:
        """PROJ-283 Phase 4: enforce non-negative reproduction rate and
        happiness in [0, 1]. The point-budget system enforces tighter
        bounds (floor 0.5%); this is the bare-minimum data sanity check."""
        if self.base_reproduction_rate < 0:
            return False, (
                f"base_reproduction_rate must be non-negative, "
                f"got {self.base_reproduction_rate}"
            )
        if not (0.0 <= self.base_happiness <= 1.0):
            return False, (
                f"base_happiness must be between 0.0 and 1.0, "
                f"got {self.base_happiness}"
            )
        return True, ""

    def is_complete(self) -> bool:
        """Check if all required fields are filled."""
        return self.validate().is_valid
