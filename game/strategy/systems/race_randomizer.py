"""
Race Randomizer - Generates random race configuration values.

Provides static methods for randomizing identity fields, visual selections,
and ship themes in the Species Setup dialog. Uses pre-generated race name
data from game/data/race_names.json when a portrait is selected.
"""
import os
import random
from typing import Dict, List, Optional

from game.core.json_utils import load_json
from game.core.paths import Paths
from game.strategy.data.race_config import (
    GOVERNMENT_TYPES,
    GOVERNMENT_ORGANIZATIONS,
    LEADER_TITLES,
    PHYSICAL_TYPES,
    SOCIETY_TYPES,
)


class RaceRandomizer:
    """Generates random values for race configuration fields."""

    _race_names_cache: Optional[Dict] = None

    @staticmethod
    def _load_race_names() -> Dict:
        """Load and cache the race names data file."""
        if RaceRandomizer._race_names_cache is not None:
            return RaceRandomizer._race_names_cache

        path = os.path.join(Paths.GAME_DIR, "data", "race_names.json")
        data = load_json(path, default={})
        RaceRandomizer._race_names_cache = data
        return data

    @staticmethod
    def randomize_identity(portrait_id: Optional[str] = None) -> Dict[str, str]:
        """
        Generate random identity fields for a race.

        Args:
            portrait_id: If provided, use portrait-specific names from data file.

        Returns:
            Dict with keys: race_name, race_name_plural, leader_name,
            physical_type, government_type, government_organization,
            leader_title, society_type, faction_name
        """
        data = RaceRandomizer._load_race_names()

        # Pick name + plural from portrait-specific or fallback pool
        name_entry = RaceRandomizer._pick_name_entry(data, portrait_id)
        race_name = name_entry["name"]
        race_name_plural = name_entry["plural"]

        # Pick leader name from portrait-specific or fallback pool
        leader_name = RaceRandomizer._pick_leader(data, portrait_id)

        # Pick from dropdown lists
        physical_type = random.choice(PHYSICAL_TYPES)
        government_type = random.choice(GOVERNMENT_TYPES)
        government_org = random.choice(GOVERNMENT_ORGANIZATIONS)
        leader_title = random.choice(LEADER_TITLES)
        society_type = random.choice(SOCIETY_TYPES)

        # Generate faction name
        faction_name = f"{race_name} {government_type}"

        return {
            "race_name": race_name,
            "race_name_plural": race_name_plural,
            "leader_name": leader_name,
            "physical_type": physical_type,
            "government_type": government_type,
            "government_organization": government_org,
            "leader_title": leader_title,
            "society_type": society_type,
            "faction_name": faction_name,
        }

    @staticmethod
    def _pick_name_entry(data: Dict, portrait_id: Optional[str]) -> Dict[str, str]:
        """Pick a name entry (name + plural) from portrait data or fallback."""
        if portrait_id and "portraits" in data:
            portrait_data = data["portraits"].get(portrait_id)
            if portrait_data and portrait_data.get("names"):
                return random.choice(portrait_data["names"])

        fallback = data.get("fallback_names", [])
        if fallback:
            return random.choice(fallback)

        return {"name": "Unknown", "plural": "Unknown"}

    @staticmethod
    def _pick_leader(data: Dict, portrait_id: Optional[str]) -> str:
        """Pick a leader name from portrait data or fallback."""
        if portrait_id and "portraits" in data:
            portrait_data = data["portraits"].get(portrait_id)
            if portrait_data and portrait_data.get("leaders"):
                return random.choice(portrait_data["leaders"])

        fallback = data.get("fallback_leaders", [])
        if fallback:
            return random.choice(fallback)

        return "Leader"

    @staticmethod
    def randomize_flag(available_flags: List[str]) -> str:
        """Pick a random flag from available flag IDs."""
        if not available_flags:
            return ""
        return random.choice(available_flags)

    @staticmethod
    def randomize_portrait(available_portraits: List[str]) -> str:
        """Pick a random portrait from available portrait IDs."""
        if not available_portraits:
            return ""
        return random.choice(available_portraits)

    @staticmethod
    def randomize_theme(available_themes: List[str]) -> str:
        """Pick a random ship theme from available theme IDs."""
        if not available_themes:
            return ""
        return random.choice(available_themes)
