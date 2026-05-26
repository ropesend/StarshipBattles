"""
Game configuration management for the strategy layer.
Provides centralized configuration with sensible defaults.
"""
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from game.core.paths import Paths
from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode

if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig


def _get_default_asset_path() -> str:
    """Return the path to the ship_themes asset directory."""
    return Paths.SHIP_THEMES_DIR


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


# FEAT-27: single source of truth for the new-game default galaxy size.
# Both `GameConfig.system_count` and the New Game Setup UI slider read
# from this constant — bump it here and both update together.
DEFAULT_SYSTEM_COUNT: int = 2

# FEAT-27: hard bounds on the galaxy slider / GameConfig.system_count.
MIN_SYSTEM_COUNT: int = 1
MAX_SYSTEM_COUNT: int = 150


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
        # Only include optional race fields when set (sparse serialization)
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

    FEAT-27 — Galaxy size contract:
      * `system_count` is bounded `MIN_SYSTEM_COUNT ≤ N ≤ MAX_SYSTEM_COUNT`
        (1–150). The dataclass default is `DEFAULT_SYSTEM_COUNT` (2) and
        is the single source of truth — the New Game Setup UI imports it
        rather than hardcoding a default.
      * **N = 1 (shared-system mode):** all empires colonise the lone
        system on different planets. No warp lanes are generated. The
        empire-count limit (≤ 4) still applies.
      * **N ≥ 2 (separated mode):** every empire owns a distinct system.
        Configurations with `len(players) > system_count` are rejected.
    """
    # Asset paths
    asset_base_path: str = field(default_factory=_get_default_asset_path)

    # Galaxy generation
    galaxy_radius: int = 4000
    system_count: int = DEFAULT_SYSTEM_COUNT
    galaxy_type: str = "random"
    galaxy_seed: Optional[int] = None

    # Save game name (user-provided)
    save_name: str = ""

    # Player configurations
    players: List[PlayerConfig] = field(default_factory=_get_default_players)

    def __post_init__(self):
        """Validate configuration after initialization."""
        if len(self.players) < 1:
            raise ValidationException(
                "Player count below minimum",
                code=ErrorCode.OUT_OF_RANGE.value,
                context={"field": "player_count", "value": len(self.players), "minimum": 1}
            )
        if len(self.players) > 4:
            raise ValidationException(
                "Player count above maximum",
                code=ErrorCode.OUT_OF_RANGE.value,
                context={"field": "player_count", "value": len(self.players), "maximum": 4}
            )
        if self.galaxy_type not in VALID_GALAXY_TYPES:
            raise ValidationException(
                f"Invalid galaxy type '{self.galaxy_type}'",
                code=ErrorCode.VALIDATION_FAILED.value,
                context={"galaxy_type": self.galaxy_type, "valid_types": sorted(VALID_GALAXY_TYPES)}
            )
        # FEAT-27: galaxy size bounds.
        if not (MIN_SYSTEM_COUNT <= self.system_count <= MAX_SYSTEM_COUNT):
            raise ValidationException(
                f"system_count {self.system_count} out of range",
                code=ErrorCode.OUT_OF_RANGE.value,
                context={
                    "field": "system_count",
                    "value": self.system_count,
                    "valid_range": f"{MIN_SYSTEM_COUNT}-{MAX_SYSTEM_COUNT}",
                },
            )
        # FEAT-27: at N=1 every empire shares the single system on a
        # different planet (intentional). At N≥2 we require one distinct
        # system per empire, so reject E > N to surface the misconfig
        # early instead of silently colliding empires onto the same hex.
        if self.system_count >= 2 and len(self.players) > self.system_count:
            raise ValidationException(
                "More empires than star systems",
                code=ErrorCode.VALIDATION_FAILED.value,
                context={
                    "empires": len(self.players),
                    "system_count": self.system_count,
                    "rule": "N>=2 requires len(players) <= system_count",
                },
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
            system_count=data.get('system_count', DEFAULT_SYSTEM_COUNT),
            galaxy_type=data.get('galaxy_type', 'random'),
            galaxy_seed=data.get('galaxy_seed'),
            save_name=data.get('save_name', ''),
            players=players
        )
