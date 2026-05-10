"""
Race Library - Manages race configuration files

This module provides the RaceLibrary class for saving, loading, listing,
and deleting race configuration files stored in the races/ folder.

PROJ-287: CachedRaceRegistry wraps RaceLibrary with a session-scoped
in-memory cache. It implements the IRaceRegistry protocol so consumers
(UI panels, formulas) can resolve race_id -> RaceConfig without hitting
the filesystem on every call. Both hits and misses (None results) are
cached. Invalidation is manual via invalidate(race_id=None) and is the
race editor's responsibility on save.
"""
# PROJ-382 Phase 3 (Pattern #12): the bare ``json`` import is preserved
# solely for the ``json.JSONDecodeError`` exception type used in the load
# paths below; ``RaceConfig.load`` performs the actual deserialization
# through ``json_utils``, so race_library itself does not call json.dump /
# json.loads.  Same pattern documented in
# system_blueprints_loader.py (audit PAT-01-CFG-003).
import json
import logging
import os
import glob
import uuid
from typing import Dict, List, Optional, Tuple

from game.core.paths import Paths
from game.core.string_utils import slugify
from game.strategy.data.race_config import RaceConfig
from game.core.exceptions import ValidationException

logger = logging.getLogger(__name__)



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

        logger.debug(f"RaceLibrary initialized with folder: {self.races_folder}")

    def _ensure_folder_exists(self) -> bool:
        """
        Ensure the races folder exists, creating it if necessary.

        Returns:
            True if folder exists or was created, False on error
        """
        try:
            os.makedirs(self.races_folder, exist_ok=True)
            return True
        except PermissionError as e:
            logger.error(f"Permission denied creating races folder '{self.races_folder}': {e}")
            return False
        except OSError as e:
            logger.error(f"OS error creating races folder '{self.races_folder}': {e}")
            return False

    def get_all_races(self) -> List[RaceConfig]:
        """
        Load all race configurations from the races folder.

        Returns:
            List of RaceConfig objects, sorted by name
        """
        if not os.path.exists(self.races_folder):
            logger.debug(f"Races folder does not exist: {self.races_folder}")
            return []

        races = []
        pattern = os.path.join(self.races_folder, "*.json")
        logger.debug(f"Scanning for races: {pattern}")

        for filepath in glob.glob(pattern):
            try:
                race = RaceConfig.load(filepath)
                if race is not None:
                    # Ensure race_id matches filename if not set
                    if not race.race_id:
                        race.race_id = os.path.splitext(os.path.basename(filepath))[0]
                    races.append(race)
                    logger.debug(f"Loaded race: {race.name} ({race.race_id})")
            except json.JSONDecodeError as e:
                logger.warning(f"Corrupt JSON in race file {filepath}: {e}")
                continue
            except KeyError as e:
                logger.warning(f"Missing required field in race file {filepath}: {e}")
                continue
            except (PermissionError, OSError) as e:
                logger.warning(f"Cannot read race file {filepath}: {e}")
                continue
            except (AttributeError, TypeError, ValueError, ValidationException) as e:
                logger.warning(f"Unexpected error loading race from {filepath}: {e}")
                continue

        # Sort by name
        races.sort(key=lambda r: r.name.lower())
        logger.info(f"Loaded {len(races)} races from library")
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
            logger.warning(f"Race not found: {race_id}")
            return None

        try:
            race = RaceConfig.load(filepath)
            if race is not None and not race.race_id:
                race.race_id = race_id
            return race
        except json.JSONDecodeError as e:
            logger.error(f"Corrupt JSON in race '{race_id}' at {filepath}: {e}")
            return None
        except KeyError as e:
            logger.error(f"Missing required field in race '{race_id}': {e}")
            return None
        except (PermissionError, OSError) as e:
            logger.error(f"Cannot read race '{race_id}' from {filepath}: {e}")
            return None
        except (AttributeError, TypeError, ValueError, ValidationException) as e:
            logger.error(f"Unexpected error loading race '{race_id}': {e}")
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
                logger.info(f"Saved race: {config.name} ({config.race_id})")
                return True, f"Race '{config.name}' saved successfully"
            else:
                return False, "Failed to write race file"
        except PermissionError as e:
            logger.error(f"Permission denied saving race '{config.race_id}' to {filepath}")
            return False, "Error saving race: Permission denied"
        except OSError as e:
            logger.error(f"OS error saving race '{config.race_id}' to {filepath}: {e}")
            return False, f"Error saving race: {str(e)}"
        except ValidationException as e:
            logger.error(f"Serialization error saving race '{config.race_id}': {e}")
            return False, "Error saving race: Invalid race data"
        except (AttributeError, KeyError) as e:
            logger.error(f"Unexpected error saving race '{config.race_id}': {e}")
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
            logger.warning(f"Cannot delete - race not found: {race_id}")
            return False

        try:
            os.remove(filepath)
            logger.info(f"Deleted race: {race_id}")
            return True
        except PermissionError as e:
            logger.error(f"Permission denied deleting race '{race_id}' at {filepath}")
            return False
        except OSError as e:
            logger.error(f"OS error deleting race '{race_id}' at {filepath}: {e}")
            return False
        except (RuntimeError, IOError) as e:
            logger.error(f"Unexpected error deleting race '{race_id}': {e}")
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
        base_slug = slugify(name)[:50] if name else "race"

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


class CachedRaceRegistry:
    """Session-scoped in-memory cache over RaceLibrary (PROJ-287).

    Implements the IRaceRegistry protocol. The first get_race(race_id)
    call delegates to the backing library; subsequent calls return the
    cached result without hitting disk. None results are cached too, so
    repeated lookups of an unknown race_id (extinct species, save drift,
    typos) don't re-stat the filesystem.

    Invalidation is manual: callers must invoke invalidate(race_id) after
    a race is saved (the only mid-game mutation path). External file edits
    require a game restart — by design.
    """

    def __init__(self, backing: RaceLibrary):
        self._backing = backing
        self._cache: Dict[str, Optional[RaceConfig]] = {}

    def get_race(self, race_id: str) -> Optional[RaceConfig]:
        """Resolve race_id -> RaceConfig, caching both hits and misses."""
        if race_id not in self._cache:
            self._cache[race_id] = self._backing.get_race(race_id)
        return self._cache[race_id]

    def invalidate(self, race_id: Optional[str] = None) -> None:
        """Clear cached entries. None clears all; otherwise clears one id."""
        if race_id is None:
            self._cache.clear()
        else:
            self._cache.pop(race_id, None)
