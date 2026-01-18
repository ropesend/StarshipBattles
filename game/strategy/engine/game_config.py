"""
Game configuration management for the strategy layer.
Provides centralized configuration with sensible defaults.
"""
import os
from dataclasses import dataclass, field
from typing import Optional


def _get_default_asset_path() -> str:
    """
    Calculate default asset path relative to project root.
    Uses __file__ traversal to find project root reliably.
    """
    # Navigate: game_config.py -> engine -> strategy -> game -> StarshipBattles
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    return os.path.join(project_root, "assets", "ShipThemes")


@dataclass
class GameConfig:
    """
    Configuration for a game session.

    All paths use sensible defaults that work across environments.
    Override specific fields as needed for testing or deployment.
    """
    # Asset paths
    asset_base_path: str = field(default_factory=_get_default_asset_path)
    player_theme: str = "Atlantians"
    enemy_theme: str = "Federation"

    # Galaxy generation
    galaxy_radius: int = 4000
    system_count: int = 25

    # Empire configuration
    player_name: str = "Terran Command"
    player_color: tuple = (0, 0, 255)
    enemy_name: str = "Xeno Hive"
    enemy_color: tuple = (255, 0, 0)

    @property
    def player_theme_path(self) -> str:
        """Full path to player empire's ship theme."""
        return os.path.join(self.asset_base_path, self.player_theme)

    @property
    def enemy_theme_path(self) -> str:
        """Full path to enemy empire's ship theme."""
        return os.path.join(self.asset_base_path, self.enemy_theme)

    def to_dict(self) -> dict:
        """Serialize GameConfig to dict."""
        return {
            'asset_base_path': self.asset_base_path,
            'player_theme': self.player_theme,
            'enemy_theme': self.enemy_theme,
            'galaxy_radius': self.galaxy_radius,
            'system_count': self.system_count,
            'player_name': self.player_name,
            'player_color': list(self.player_color),  # Tuple to list
            'enemy_name': self.enemy_name,
            'enemy_color': list(self.enemy_color)  # Tuple to list
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'GameConfig':
        """Deserialize GameConfig from dict."""
        return cls(
            asset_base_path=data.get('asset_base_path', _get_default_asset_path()),
            player_theme=data.get('player_theme', 'Atlantians'),
            enemy_theme=data.get('enemy_theme', 'Federation'),
            galaxy_radius=data.get('galaxy_radius', 4000),
            system_count=data.get('system_count', 25),
            player_name=data.get('player_name', 'Terran Command'),
            player_color=tuple(data.get('player_color', [0, 0, 255])),
            enemy_name=data.get('enemy_name', 'Xeno Hive'),
            enemy_color=tuple(data.get('enemy_color', [255, 0, 0]))
        )
