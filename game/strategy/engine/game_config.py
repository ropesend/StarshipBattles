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
