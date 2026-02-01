"""
Galaxy layouts configuration loader.

Loads and processes galaxy layout configurations from JSON,
applying proper scaling for galaxy radius.
"""

import logging
import os
from typing import Dict, Any, List, Optional

from game.core.json_utils import load_json_required


log = logging.getLogger(__name__)


# Fields that should be scaled by galaxy radius
SCALING_FIELDS = {'sigma', 'radius', 'width', 'length', 'arm_width', 'edge_falloff'}

# Fields that represent positions relative to center (-1 to 1 range)
POSITION_FIELDS = {'center_q', 'center_r', 'offset_q', 'offset_r'}


class GalaxyLayoutsLoader:
    """Loader for galaxy layout configurations.

    Handles loading from JSON and scaling values appropriately
    for the target galaxy radius.
    """

    DEFAULT_PATH = os.path.join("data", "galaxy_layouts.json")

    @staticmethod
    def load(file_path: str = None) -> Dict[str, Any]:
        """Load galaxy layouts configuration from JSON file.

        Args:
            file_path: Path to JSON file (uses default if None)

        Returns:
            Parsed configuration dict

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is invalid JSON
            ValueError: If required 'layouts' key is missing
        """
        if file_path is None:
            file_path = GalaxyLayoutsLoader.DEFAULT_PATH

        log.info(f"Loading galaxy layouts from: {file_path}")
        data = load_json_required(file_path)

        if 'layouts' not in data:
            raise ValueError(f"Galaxy layouts file must contain 'layouts' key: {file_path}")

        log.info(f"Loaded {len(data['layouts'])} galaxy layout types")
        return data

    @staticmethod
    def get_layout_config(layout_type: str, layouts_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get configuration for a specific layout type.

        Args:
            layout_type: Name of the layout (e.g., 'spiral', 'cluster')
            layouts_data: Full layouts data from load()

        Returns:
            Configuration dict for the specified layout

        Raises:
            ValueError: If layout_type is not found
        """
        layouts = layouts_data.get('layouts', {})
        if layout_type not in layouts:
            available = list(layouts.keys())
            raise ValueError(
                f"Unknown layout type '{layout_type}'. "
                f"Available types: {available}"
            )
        return layouts[layout_type]

    @staticmethod
    def get_available_layouts(layouts_data: Dict[str, Any]) -> List[str]:
        """Get list of available layout type names.

        Args:
            layouts_data: Full layouts data from load()

        Returns:
            List of layout type names
        """
        return list(layouts_data.get('layouts', {}).keys())

    @staticmethod
    def scale_layout_for_radius(
        layout_config: Dict[str, Any],
        galaxy_radius: int
    ) -> Dict[str, Any]:
        """Scale a layout configuration for a specific galaxy radius.

        Values in the JSON are relative (0-1 range typically).
        This function converts them to absolute hex units.

        Args:
            layout_config: Raw layout configuration
            galaxy_radius: Target galaxy radius in hex units

        Returns:
            Scaled layout configuration with absolute values
        """
        scaled = {
            'name': layout_config.get('name', 'Unknown'),
            'description': layout_config.get('description', ''),
            'primitives': []
        }

        for prim_config in layout_config.get('primitives', []):
            scaled_prim = GalaxyLayoutsLoader._scale_primitive(prim_config, galaxy_radius)
            scaled['primitives'].append(scaled_prim)

        return scaled

    @staticmethod
    def _scale_primitive(
        prim_config: Dict[str, Any],
        galaxy_radius: int
    ) -> Dict[str, Any]:
        """Scale a single primitive configuration.

        Args:
            prim_config: Raw primitive configuration
            galaxy_radius: Target galaxy radius in hex units

        Returns:
            Scaled primitive configuration
        """
        scaled = {}

        for key, value in prim_config.items():
            # Skip comment fields
            if key.startswith('_'):
                continue

            if key in SCALING_FIELDS and isinstance(value, (int, float)):
                # Scale by galaxy radius
                scaled[key] = value * galaxy_radius
            elif key in POSITION_FIELDS and isinstance(value, (int, float)):
                # Position fields are relative to radius (-1 to 1)
                scaled[key] = value * galaxy_radius
            else:
                # Copy unchanged
                scaled[key] = value

        return scaled

    @staticmethod
    def load_and_scale(
        layout_type: str,
        galaxy_radius: int,
        file_path: str = None
    ) -> Dict[str, Any]:
        """Convenience method to load, lookup, and scale a layout.

        Args:
            layout_type: Name of the layout (e.g., 'spiral')
            galaxy_radius: Target galaxy radius in hex units
            file_path: Path to JSON file (uses default if None)

        Returns:
            Scaled layout configuration ready for DensityMap.from_config()
        """
        data = GalaxyLayoutsLoader.load(file_path)
        config = GalaxyLayoutsLoader.get_layout_config(layout_type, data)
        return GalaxyLayoutsLoader.scale_layout_for_radius(config, galaxy_radius)
