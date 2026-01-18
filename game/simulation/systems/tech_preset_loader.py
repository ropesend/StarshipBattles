"""
Tech Preset Loader

Loads and manages technology presets for standalone workshop mode.
Presets define which components/modifiers are available for ship design.

In standalone mode, the workshop uses tech presets (JSON files) to simulate
different stages of tech progression without running a full strategy game.

In integrated mode, the workshop uses the empire's unlocked tech list instead.
"""
import os
import glob
from typing import List, Dict
from game.core.json_utils import load_json_required


# Path to tech presets directory
TECH_PRESETS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "tech_presets")


class TechPresetLoader:
    """
    Loads and manages tech presets for standalone workshop mode.

    Tech presets are JSON files in data/tech_presets/ that define:
    - name: Display name of the preset
    - description: What stage of game this represents
    - unlocked_components: List of component IDs (or ["*"] for all)
    - unlocked_modifiers: List of modifier IDs (or ["*"] for all)

    Example preset (early_game.json):
    {
        "name": "Early Game Tech",
        "description": "Basic components available at game start",
        "unlocked_components": ["hull_escort", "laser_cannon", "railgun"],
        "unlocked_modifiers": ["simple_size_mount"]
    }

    Usage:
        # List available presets
        presets = TechPresetLoader.list_presets()
        # ['default', 'early_game', 'mid_game']

        # Load preset data
        data = TechPresetLoader.load_preset("early_game")
        # {'name': 'Early Game Tech', 'unlocked_components': [...], ...}

        # Get component IDs
        components = TechPresetLoader.get_available_components("early_game")
        # ['hull_escort', 'laser_cannon', 'railgun', ...]
    """

    @staticmethod
    def list_presets() -> List[str]:
        """
        List all available preset names.

        Returns:
            List of preset names (without .json extension)

        Example:
            >>> TechPresetLoader.list_presets()
            ['default', 'early_game', 'mid_game']
        """
        # Find all .json files in tech presets directory
        pattern = os.path.join(TECH_PRESETS_DIR, "*.json")
        json_files = glob.glob(pattern)

        # Extract preset names (filename without .json)
        preset_names = [
            os.path.splitext(os.path.basename(filepath))[0]
            for filepath in json_files
        ]

        return sorted(preset_names)

    @staticmethod
    def load_preset(preset_name: str) -> Dict:
        """
        Load tech preset data from JSON file.

        Args:
            preset_name: Name of preset (without .json extension)

        Returns:
            Dictionary containing preset data with keys:
            - name: Display name
            - description: Preset description
            - unlocked_components: List of component IDs
            - unlocked_modifiers: List of modifier IDs

        Raises:
            FileNotFoundError: If preset file doesn't exist

        Example:
            >>> data = TechPresetLoader.load_preset("early_game")
            >>> data['name']
            'Early Game Tech'
        """
        filepath = os.path.join(TECH_PRESETS_DIR, f"{preset_name}.json")

        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"Tech preset '{preset_name}' not found at {filepath}"
            )

        return load_json_required(filepath)

    @staticmethod
    def get_available_components(preset_name: str) -> List[str]:
        """
        Get list of component IDs available in this preset.

        Args:
            preset_name: Name of preset to load

        Returns:
            List of component IDs (or ['*'] for all components)

        Raises:
            FileNotFoundError: If preset file doesn't exist

        Example:
            >>> components = TechPresetLoader.get_available_components("early_game")
            >>> "laser_cannon" in components
            True
        """
        data = TechPresetLoader.load_preset(preset_name)
        return data.get("unlocked_components", [])

    @staticmethod
    def get_available_modifiers(preset_name: str) -> List[str]:
        """
        Get list of modifier IDs available in this preset.

        Args:
            preset_name: Name of preset to load

        Returns:
            List of modifier IDs (or ['*'] for all modifiers)

        Raises:
            FileNotFoundError: If preset file doesn't exist

        Example:
            >>> modifiers = TechPresetLoader.get_available_modifiers("early_game")
            >>> "simple_size_mount" in modifiers
            True
        """
        data = TechPresetLoader.load_preset(preset_name)
        return data.get("unlocked_modifiers", [])

    @staticmethod
    def is_component_available(component_id: str, preset_name: str) -> bool:
        """
        Check if a specific component is available in this preset.

        Args:
            component_id: ID of component to check
            preset_name: Name of preset to check against

        Returns:
            True if component is available, False otherwise

        Example:
            >>> TechPresetLoader.is_component_available("laser_cannon", "early_game")
            True
            >>> TechPresetLoader.is_component_available("plasma_cannon", "early_game")
            False
        """
        available = TechPresetLoader.get_available_components(preset_name)

        # Wildcard means all components are available
        if "*" in available:
            return True

        return component_id in available

    @staticmethod
    def is_modifier_available(modifier_id: str, preset_name: str) -> bool:
        """
        Check if a specific modifier is available in this preset.

        Args:
            modifier_id: ID of modifier to check
            preset_name: Name of preset to check against

        Returns:
            True if modifier is available, False otherwise

        Example:
            >>> TechPresetLoader.is_modifier_available("simple_size_mount", "early_game")
            True
        """
        available = TechPresetLoader.get_available_modifiers(preset_name)

        # Wildcard means all modifiers are available
        if "*" in available:
            return True

        return modifier_id in available
