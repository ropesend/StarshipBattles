"""
Resource Catalog and Loading
============================

Provides the unified ResourceCatalog for all resource definitions (planetary
materials and operational consumables), loaded from data/resources.json.

Error Handling:
    All loading errors (FileNotFoundError, JSONDecodeError, PermissionError,
    TypeError) are caught and logged, with graceful fallback to default resources.
"""

import json
import logging
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

from game.core.json_utils import load_json_required
from game.core.paths import Paths

logger = logging.getLogger(__name__)


# =============================================================================
# Resource Catalog (Unified Resource System)
# =============================================================================

@dataclass(frozen=True)
class ResourceDefinition:
    """Immutable definition of a resource type.

    Attributes:
        id: Lowercase unique identifier (e.g., "metals", "fuel")
        name: Display name (e.g., "Metals", "Fuel")
        description: Human-readable description
        display_group: Optional UI grouping hint (e.g., "planetary", "operational")
        has_quality: Whether planet deposits of this resource track quality
    """
    id: str
    name: str
    description: str = ""
    display_group: str = ""
    has_quality: bool = False


class ResourceCatalog:
    """Registry of all resource definitions. Loaded once from JSON.

    The catalog is the single source of truth for what resources exist
    in the game. Both planetary materials and operational consumables
    are defined here. A resource's behavior (extractable, consumable,
    etc.) is determined by what components and data files reference it,
    not by any category on the resource itself.

    Usage:
        # Load from the default data/resources.json
        catalog = ResourceCatalog.from_json()

        # Query resources
        catalog.get("metals")           # -> ResourceDefinition or None
        catalog.has("fuel")             # -> True
        catalog.all_ids()               # -> ["metals", "organics", ..., "fuel", ...]
        catalog.by_display_group("planetary")  # -> [ResourceDefinition, ...]

        # Build from in-memory data (useful for testing/modding)
        catalog = ResourceCatalog.from_data([{"id": "dilithium", "name": "Dilithium"}])
    """

    def __init__(self, definitions: Dict[str, ResourceDefinition]):
        """Initialize with a dict of id -> ResourceDefinition.

        Use the factory methods from_json() or from_data() instead of
        calling this directly.
        """
        self._definitions: Dict[str, ResourceDefinition] = dict(definitions)

    @classmethod
    def from_json(cls, file_path: str = "data/resources.json") -> 'ResourceCatalog':
        """Load a ResourceCatalog from a JSON file.

        Args:
            file_path: Path to the resources JSON file. Supports both
                       absolute paths and paths relative to the project root.

        Returns:
            A ResourceCatalog populated with definitions from the file.
            Returns an empty catalog if the file cannot be loaded.
        """
        resolved = _resolve_resource_path(file_path)
        if resolved is None:
            logger.warning(f"Resources file not found at {file_path}, returning empty catalog")
            return cls({})

        try:
            data = load_json_required(resolved)
            resource_list = data.get('resources', [])
            return cls.from_data(resource_list)
        except (FileNotFoundError, json.JSONDecodeError, PermissionError,
                OSError, TypeError, AttributeError) as e:
            logger.warning(f"Failed to load resources from {resolved}: {e}")
            return cls({})

    @classmethod
    def from_data(cls, resource_list: List[Dict[str, Any]]) -> 'ResourceCatalog':
        """Build a ResourceCatalog from a list of resource dictionaries.

        Each dict should have at minimum an 'id' and 'name' key.
        Missing optional fields get sensible defaults.

        Args:
            resource_list: List of resource definition dicts.

        Returns:
            A ResourceCatalog populated with the given definitions.
        """
        definitions: Dict[str, ResourceDefinition] = {}
        for entry in resource_list:
            res_id = entry.get('id')
            if not res_id:
                continue
            definitions[res_id] = ResourceDefinition(
                id=res_id,
                name=entry.get('name', res_id),
                description=entry.get('description', ''),
                display_group=entry.get('display_group', ''),
                has_quality=entry.get('has_quality', False),
            )
        return cls(definitions)

    def get(self, resource_id: str) -> Optional[ResourceDefinition]:
        """Get a resource definition by ID, or None if not found."""
        return self._definitions.get(resource_id)

    def has(self, resource_id: str) -> bool:
        """Check whether a resource ID exists in the catalog."""
        return resource_id in self._definitions

    def all_ids(self) -> List[str]:
        """Return a list of all resource IDs (order matches JSON)."""
        return list(self._definitions.keys())

    def all_definitions(self) -> List[ResourceDefinition]:
        """Return a list of all resource definitions."""
        return list(self._definitions.values())

    def by_display_group(self, group: str) -> List[ResourceDefinition]:
        """Return all resources belonging to a display group."""
        return [d for d in self._definitions.values() if d.display_group == group]


# =============================================================================
# Path Resolution
# =============================================================================

def _resolve_resource_path(file_path: str) -> Optional[str]:
    """
    Resolve resource file path using Paths.ROOT_DIR for project root.

    Args:
        file_path: Path to the resources JSON file (relative or absolute)

    Returns:
        Resolved absolute path if file exists, None otherwise
    """
    if os.path.exists(file_path):
        return file_path

    # Try absolute path using centralized Paths configuration
    abs_path = os.path.join(Paths.ROOT_DIR, file_path)

    if os.path.exists(abs_path):
        return abs_path

    return None
