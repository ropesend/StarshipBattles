"""
Race Library - Manages race configuration files

This module provides the RaceLibrary class for saving, loading, listing,
and deleting race configuration files stored in the races/ folder.
"""
import os
import glob
import re
import uuid
from typing import List, Optional, Tuple

from game.core.logger import log_info, log_debug, log_error, log_warning
from game.core.paths import Paths
from game.strategy.data.race_config import RaceConfig


def _slugify(text: str) -> str:
    """
    Convert text to a filesystem-safe slug.

    Args:
        text: The text to convert

    Returns:
        Lowercase slug with only alphanumeric characters and underscores
    """
    # Convert to lowercase
    slug = text.lower()
    # Replace spaces and hyphens with underscores
    slug = re.sub(r'[\s\-]+', '_', slug)
    # Remove any characters that aren't alphanumeric or underscore
    slug = re.sub(r'[^\w]', '', slug)
    # Remove leading/trailing underscores
    slug = slug.strip('_')
    # Limit length
    return slug[:50] if slug else "race"


class RaceLibrary:
    """
    Manages race configuration files.

    Handles saving, loading, listing, and deleting race configurations
    stored as JSON files in the races/ folder.
    """

    def __init__(self, races_folder: Optional[str] = None):
        """
        Initialize the race library.

        Args:
            races_folder: Path to the races folder. If None, uses 'races/'
                         in the project root.
        """
        if races_folder is None:
            # Default to races/ in project root
            self.races_folder = Paths.RACES_DIR
        else:
            self.races_folder = races_folder

        log_debug(f"RaceLibrary initialized with folder: {self.races_folder}")

    def _ensure_folder_exists(self) -> bool:
        """
        Ensure the races folder exists, creating it if necessary.

        Returns:
            True if folder exists or was created, False on error
        """
        try:
            os.makedirs(self.races_folder, exist_ok=True)
            return True
        except Exception as e:
            log_error(f"Failed to create races folder: {e}")
            return False

    def get_all_races(self) -> List[RaceConfig]:
        """
        Load all race configurations from the races folder.

        Returns:
            List of RaceConfig objects, sorted by name
        """
        if not os.path.exists(self.races_folder):
            log_debug(f"Races folder does not exist: {self.races_folder}")
            return []

        races = []
        pattern = os.path.join(self.races_folder, "*.json")
        log_debug(f"Scanning for races: {pattern}")

        for filepath in glob.glob(pattern):
            try:
                race = RaceConfig.load(filepath)
                if race is not None:
                    # Ensure race_id matches filename if not set
                    if not race.race_id:
                        race.race_id = os.path.splitext(os.path.basename(filepath))[0]
                    races.append(race)
                    log_debug(f"Loaded race: {race.name} ({race.race_id})")
            except Exception as e:
                log_warning(f"Failed to load race from {filepath}: {e}")
                continue

        # Sort by name
        races.sort(key=lambda r: r.name.lower())
        log_info(f"Loaded {len(races)} races from library")
        return races

    def get_race(self, race_id: str) -> Optional[RaceConfig]:
        """
        Load a specific race configuration by ID.

        Args:
            race_id: The race identifier (filename without extension)

        Returns:
            RaceConfig if found, None otherwise
        """
        filepath = os.path.join(self.races_folder, f"{race_id}.json")

        if not os.path.exists(filepath):
            log_warning(f"Race not found: {race_id}")
            return None

        try:
            race = RaceConfig.load(filepath)
            if race is not None and not race.race_id:
                race.race_id = race_id
            return race
        except Exception as e:
            log_error(f"Failed to load race {race_id}: {e}")
            return None

    def save_race(self, config: RaceConfig) -> Tuple[bool, str]:
        """
        Save a race configuration to file.

        If the race has no race_id, one will be generated from the name.

        Args:
            config: The RaceConfig to save

        Returns:
            Tuple of (success, message)
        """
        # Ensure folder exists
        if not self._ensure_folder_exists():
            return False, "Failed to create races folder"

        # Generate race_id if not set
        if not config.race_id:
            config.race_id = self._generate_race_id(config.name)

        # Build filepath
        filepath = os.path.join(self.races_folder, f"{config.race_id}.json")

        # Save the configuration
        try:
            if config.save(filepath):
                log_info(f"Saved race: {config.name} ({config.race_id})")
                return True, f"Race '{config.name}' saved successfully"
            else:
                return False, "Failed to write race file"
        except Exception as e:
            log_error(f"Failed to save race: {e}")
            return False, f"Error saving race: {str(e)}"

    def delete_race(self, race_id: str) -> bool:
        """
        Delete a race configuration file.

        Args:
            race_id: The race identifier to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        filepath = os.path.join(self.races_folder, f"{race_id}.json")

        if not os.path.exists(filepath):
            log_warning(f"Cannot delete - race not found: {race_id}")
            return False

        try:
            os.remove(filepath)
            log_info(f"Deleted race: {race_id}")
            return True
        except Exception as e:
            log_error(f"Failed to delete race {race_id}: {e}")
            return False

    def _generate_race_id(self, name: str) -> str:
        """
        Generate a unique race ID from the name.

        Args:
            name: The race name

        Returns:
            A unique race ID string
        """
        # Create base slug from name
        base_slug = _slugify(name) if name else "race"

        # Add short UUID suffix for uniqueness
        suffix = uuid.uuid4().hex[:8]

        return f"{base_slug}_{suffix}"

    def race_exists(self, race_id: str) -> bool:
        """
        Check if a race with the given ID exists.

        Args:
            race_id: The race identifier to check

        Returns:
            True if the race exists, False otherwise
        """
        filepath = os.path.join(self.races_folder, f"{race_id}.json")
        return os.path.exists(filepath)

    def get_race_count(self) -> int:
        """
        Get the number of saved races.

        Returns:
            Number of race files in the library
        """
        if not os.path.exists(self.races_folder):
            return 0

        pattern = os.path.join(self.races_folder, "*.json")
        return len(glob.glob(pattern))
