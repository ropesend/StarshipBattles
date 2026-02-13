"""
Game configuration management for the strategy layer.
Provides centralized configuration with sensible defaults.
"""
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig


def _get_default_asset_path() -> str:
    """
    Calculate default asset path relative to project root.
    Uses __file__ traversal to find project root reliably.
    """
    # Navigate: game_config.py -> engine -> strategy -> game -> StarshipBattles
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    return os.path.join(project_root, "assets", "ShipThemes")


# Theme defaults for auto-assignment based on player number
# Format: (theme_id, default_color)
# ARCHITECTURE NOTE: Colors here are game-semantic identifiers for empires,
# stored in save games, and used consistently across UI. Moving to UI layer
# would require save format changes. Colors are intentionally kept simple
# (RGB tuples) rather than pygame-specific types.
THEME_DEFAULTS = [
    ("Federation", (0, 100, 255)),    # Blue
    ("Atlantians", (0, 200, 150)),    # Teal
    ("Romulans", (0, 180, 0)),        # Green
    ("Klingons", (255, 50, 50)),      # Red
]


# Valid galaxy types for generation
# "random" uses the original uniform random placement
# Other types use density-based placement from galaxy_layouts.json
VALID_GALAXY_TYPES = frozenset([
    "random",           # Original uniform random placement
    "cluster",          # Multiple distinct star clusters
    "spiral",           # Classic spiral with core and arms
    "spiral_no_core",   # Spiral arms only, no central bulge
    "barred_spiral",    # Spiral with central bar
    "ring",             # Ring galaxy
    "irregular",        # Irregular/merger galaxy
    "diamond",          # Diamond-shaped distribution
    "uniform",          # Uniform distribution
])


@dataclass
class PlayerConfig:
    """
    Configuration for a single player/empire.

    Race visual properties (flag_id, portrait_id) are used when a player
    selects a custom race during game setup. If not set, default theme
    visuals are used.
    """
    name: str = "Empire"
    theme: str = "Federation"
    color: tuple = (128, 128, 128)
    is_human: bool = True
    # Race visual identity (optional - from RaceConfig selection)
    race_id: Optional[str] = None
    flag_id: str = ""
    portrait_id: str = ""
    # Full race configuration for habitability/growth calculations
    race_config: Optional['RaceConfig'] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize PlayerConfig to dict."""
        data = {
            'name': self.name,
            'theme': self.theme,
            'color': list(self.color),  # Tuple to list for JSON
            'is_human': self.is_human
        }
        # Only include race fields if set (backwards compatibility)
        if self.race_id:
            data['race_id'] = self.race_id
        if self.flag_id:
            data['flag_id'] = self.flag_id
        if self.portrait_id:
            data['portrait_id'] = self.portrait_id
        if self.race_config is not None:
            data['race_config'] = self.race_config.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'PlayerConfig':
        """Deserialize PlayerConfig from dict."""
        from game.strategy.data.race_config import RaceConfig

        # Deserialize race_config if present
        race_config = None
        if 'race_config' in data:
            race_config = RaceConfig.from_dict(data['race_config'])

        return cls(
            name=data.get('name', 'Empire'),
            theme=data.get('theme', 'Federation'),
            color=tuple(data.get('color', [128, 128, 128])),
            is_human=data.get('is_human', True),
            race_id=data.get('race_id'),
            flag_id=data.get('flag_id', ''),
            portrait_id=data.get('portrait_id', ''),
            race_config=race_config
        )


def _get_default_players() -> List[PlayerConfig]:
    """Create default 2-player setup."""
    return [
        PlayerConfig(
            name="Terran Command",
            theme=THEME_DEFAULTS[0][0],  # Federation
            color=THEME_DEFAULTS[0][1],
            is_human=True
        ),
        PlayerConfig(
            name="Xeno Hive",
            theme=THEME_DEFAULTS[1][0],  # Atlantians
            color=THEME_DEFAULTS[1][1],
            is_human=True
        )
    ]


@dataclass
class GameConfig:
    """
    Configuration for a game session.

    All paths use sensible defaults that work across environments.
    Override specific fields as needed for testing or deployment.
    """
    # Asset paths
    asset_base_path: str = field(default_factory=_get_default_asset_path)

    # Galaxy generation
    galaxy_radius: int = 4000
    system_count: int = 25
    galaxy_type: str = "random"
    galaxy_seed: Optional[int] = None

    # Save game name (user-provided)
    save_name: str = ""

    # Player configurations
    players: List[PlayerConfig] = field(default_factory=_get_default_players)

    def __post_init__(self):
        """Validate configuration after initialization."""
        if len(self.players) < 1:
            raise ValueError("GameConfig requires at least 1 player")
        if len(self.players) > 4:
            raise ValueError("GameConfig supports at most 4 players")
        if self.galaxy_type not in VALID_GALAXY_TYPES:
            raise ValueError(
                f"Invalid galaxy_type '{self.galaxy_type}'. "
                f"Valid types: {sorted(VALID_GALAXY_TYPES)}"
            )

    def get_player_theme_path(self, player_index: int) -> Optional[str]:
        """
        Get full path to a player's ship theme.

        Args:
            player_index: Index of player in players list

        Returns:
            Full path to theme folder, or None if index invalid
        """
        if 0 <= player_index < len(self.players):
            return os.path.join(self.asset_base_path, self.players[player_index].theme)
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize GameConfig to dict."""
        return {
            'asset_base_path': self.asset_base_path,
            'galaxy_radius': self.galaxy_radius,
            'system_count': self.system_count,
            'galaxy_type': self.galaxy_type,
            'galaxy_seed': self.galaxy_seed,
            'save_name': self.save_name,
            'players': [p.to_dict() for p in self.players]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'GameConfig':
        """Deserialize GameConfig from dict."""
        players_data = data.get('players', [])
        players = [PlayerConfig.from_dict(p) for p in players_data] if players_data else _get_default_players()

        return cls(
            asset_base_path=data.get('asset_base_path', _get_default_asset_path()),
            galaxy_radius=data.get('galaxy_radius', 4000),
            system_count=data.get('system_count', 25),
            galaxy_type=data.get('galaxy_type', 'random'),
            galaxy_seed=data.get('galaxy_seed'),
            save_name=data.get('save_name', ''),
            players=players
        )
