"""Game settings service.

Manages user-configurable game settings with persistence.
Settings are loaded from a JSON file and saved on change.
"""
import logging
import os
from typing import Any, Dict, Optional

from game.core.json_utils import load_json, save_json
from game.core.paths import Paths

logger = logging.getLogger(__name__)

# Default values for all settings
DEFAULTS: Dict[str, Any] = {
    'background_brightness': 0.25,
}

SETTINGS_FILE = os.path.join(Paths.SETTINGS_DIR, 'game_settings.json')

_default_game_settings: Optional['GameSettings'] = None


class GameSettings:
    """Service for user-configurable game settings.

    Settings persist to output/settings/game_settings.json.
    Access values via get()/set(), changes auto-save.
    """

    def __init__(self) -> None:
        self._data: Dict[str, Any] = dict(DEFAULTS)
        self._load()

    @classmethod
    def instance(cls) -> 'GameSettings':
        """PROJ-258 compatibility shim — returns module-level instance."""
        global _default_game_settings
        if _default_game_settings is None:
            _default_game_settings = cls()
        return _default_game_settings

    @classmethod
    def reset(cls) -> None:
        """PROJ-258 compatibility shim — replaces module-level instance."""
        global _default_game_settings
        _default_game_settings = cls()

    def _load(self) -> None:
        """Load settings from disk, merging with defaults."""
        saved = load_json(SETTINGS_FILE, default={})
        if saved:
            self._data.update(saved)
            logger.info(f"Loaded game settings from {SETTINGS_FILE}")

    def save(self) -> None:
        """Persist current settings to disk."""
        save_json(SETTINGS_FILE, self._data)

    def get(self, key: str) -> Any:
        """Get a setting value.

        Args:
            key: Setting key (e.g., 'background_brightness')

        Returns:
            Setting value, or the default if key exists in DEFAULTS, or None.
        """
        return self._data.get(key, DEFAULTS.get(key))

    def set(self, key: str, value: Any) -> None:
        """Set a setting value and save to disk.

        Args:
            key: Setting key
            value: New value
        """
        self._data[key] = value
        self.save()

    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults and save."""
        self._data = dict(DEFAULTS)
        self.save()

    @property
    def background_brightness(self) -> float:
        """Background image brightness (0.0 = black, 1.0 = full brightness)."""
        return float(self._data.get('background_brightness', DEFAULTS['background_brightness']))

    @background_brightness.setter
    def background_brightness(self, value: float) -> None:
        self.set('background_brightness', max(0.0, min(1.0, value)))
