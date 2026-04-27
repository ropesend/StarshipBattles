"""Component and Modifier data loading — extracted from component.py.

Provides pure-function loaders (load_components_data, load_modifiers_data)
and registry-populating wrappers (load_components, load_modifiers).

Also provides ComponentCacheManager (singleton) for caching loaded data,
and factory functions (create_component, get_all_components).
"""
from __future__ import annotations

import copy
import json
import logging
import os
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.simulation.components.component import Component

from game.core.json_utils import load_json_required
from game.core.paths import Paths
from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode
from game.simulation.components.component_constants import Modifier

if TYPE_CHECKING:
    from game.core.registry import GameRegistries

logger = logging.getLogger(__name__)


# =============================================================================
# Cache Manager
# =============================================================================

# Module-level reference (PROJ-258)
_default_cache_manager: 'Optional[ComponentCacheManager]' = None


def get_default_cache_manager() -> 'ComponentCacheManager':
    """Get the module-level ComponentCacheManager reference.

    Auto-creates on first access if not yet set.

    Returns:
        The module-level ComponentCacheManager instance.
    """
    global _default_cache_manager
    if _default_cache_manager is None:
        _default_cache_manager = ComponentCacheManager()
    return _default_cache_manager


class ComponentCacheManager:
    """Manager for component and modifier caches.

    PROJ-258: Migrated from SingletonMeta to DI via ApplicationContext.
    """

    def __init__(self):
        self.component_cache = None
        self.modifier_cache = None
        self.last_component_file = None
        self.last_modifier_file = None


def reset_component_caches() -> None:
    """Reset all caches for test isolation."""
    global _default_cache_manager
    _default_cache_manager = ComponentCacheManager()


# =============================================================================
# Component Loading
# =============================================================================

def load_components_data(
    file_path: str = None,
    *,
    registries: 'GameRegistries'
) -> dict:
    """Pure function to load components from JSON file.

    PROJ-211: registries is now required (no fallback).

    Args:
        file_path: Path to the components JSON file
        registries: GameRegistries for DI. Required.

    Returns:
        Dict[str, Component]: Component objects keyed by their ID
    """
    from game.simulation.components.component import Component

    if file_path is None:
        file_path = Paths.COMPONENTS_FILE
    if not os.path.exists(file_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        abs_path = os.path.join(base_dir, file_path)
        if os.path.exists(abs_path):
            file_path = abs_path
        else:
            logger.error(f"components file not found at {abs_path}")
            return {}

    try:
        data = load_json_required(file_path)

        result = {}
        errors = []
        for comp_def in data['components']:
            comp_id = comp_def.get('id', 'unknown')
            try:
                obj = Component(comp_def, registries=registries)
                result[comp_id] = obj
            except (KeyError, TypeError, ValueError, ValidationException) as e:
                logger.error(f"Component '{comp_id}': invalid data - {e}")
                errors.append(comp_id)
            except (AttributeError, ImportError) as e:
                logger.error(f"Component '{comp_id}': unexpected error - {type(e).__name__}: {e}")
                errors.append(comp_id)

        if errors:
            logger.warning(f"Loaded {len(result)} components, {len(errors)} failed: {errors[:5]}{'...' if len(errors) > 5 else ''}")

        return result

    except KeyError as e:
        logger.error(f"Missing required key in components JSON: {e}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in components file: {e}")
        return {}
    except (FileNotFoundError, OSError, KeyError, TypeError, ValueError) as e:
        logger.error(f"loading/parsing components json: {type(e).__name__}: {e}")
        return {}


def load_components(file_path: Optional[str] = None, *, registry_provider=None) -> None:
    """Load components from JSON and populate the global registry.

    PROJ-211: registry_provider is now required (no fallback).

    Args:
        file_path: Path to the components JSON file.
        registry_provider: IRegistryProvider for DI. Required.
    """
    from game.core.registry import GameRegistries

    if registry_provider is None:
        raise ValueError("registry_provider is required (PROJ-211: no fallback)")

    if file_path is None:
        file_path = Paths.COMPONENTS_FILE

    cache_mgr = get_default_cache_manager()
    comps = registry_provider.get_components()

    if cache_mgr.component_cache is not None and cache_mgr.last_component_file == file_path:
        for c_id, comp in cache_mgr.component_cache.items():
            comps[c_id] = comp.clone()
        return

    registries = GameRegistries(
        components=comps,
        modifiers=registry_provider.get_modifiers(),
        vehicle_classes=registry_provider.get_vehicle_classes(),
        resources={},
        resource_catalog=registry_provider.get_resource_catalog(),
    )
    result = load_components_data(file_path, registries=registries)
    if not result:
        return

    cache_mgr.component_cache = result
    cache_mgr.last_component_file = file_path

    for c_id, comp in cache_mgr.component_cache.items():
        comps[c_id] = comp.clone()


# =============================================================================
# Modifier Loading
# =============================================================================

def load_modifiers_data(file_path: str = None) -> dict:
    """Pure function to load modifiers from JSON file.

    Args:
        file_path: Path to the modifiers JSON file

    Returns:
        Dict[str, Modifier]: Modifier objects keyed by their ID
    """
    from game.simulation.components.modifier_schema import validate_modifier_v2

    if file_path is None:
        file_path = Paths.MODIFIERS_FILE
    if not os.path.exists(file_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        abs_path = os.path.join(base_dir, file_path)
        if os.path.exists(abs_path):
            file_path = abs_path
        else:
            logger.error(f"modifiers file not found at {abs_path}")
            return {}

    try:
        data = load_json_required(file_path)

        result = {}
        errors = []
        for mod_def in data['modifiers']:
            mod_id = mod_def.get('id', 'unknown')
            if not validate_modifier_v2(mod_def):
                logger.warning(f"Modifier '{mod_id}' failed schema validation, loading anyway")
            try:
                mod = Modifier(mod_def)
                result[mod.id] = copy.deepcopy(mod)
            except (KeyError, TypeError, ValueError) as e:
                logger.error(f"Modifier '{mod_id}': invalid data - {e}")
                errors.append(mod_id)

        if errors:
            logger.warning(f"Loaded {len(result)} modifiers, {len(errors)} failed: {errors[:5]}{'...' if len(errors) > 5 else ''}")

        return result

    except KeyError as e:
        logger.error(f"Missing required key in modifiers JSON: {e}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in modifiers file: {e}")
        return {}
    except (FileNotFoundError, OSError, KeyError, TypeError, ValueError) as e:
        logger.error(f"loading modifiers: {type(e).__name__}: {e}")
        return {}


def load_modifiers(file_path: Optional[str] = None, *, registry_provider=None) -> None:
    """Load modifiers from JSON and populate the global registry.

    PROJ-211: registry_provider is now required (no fallback).

    Args:
        file_path: Path to the modifiers JSON file.
        registry_provider: IRegistryProvider for DI. Required.
    """
    if registry_provider is None:
        raise ValueError("registry_provider is required (PROJ-211: no fallback)")

    if file_path is None:
        file_path = Paths.MODIFIERS_FILE

    cache_mgr = get_default_cache_manager()
    mods = registry_provider.get_modifiers()

    if cache_mgr.modifier_cache is not None and cache_mgr.last_modifier_file == file_path:
        for m_id, mod in cache_mgr.modifier_cache.items():
            mods[m_id] = copy.deepcopy(mod)
        return

    result = load_modifiers_data(file_path)
    if not result:
        return

    cache_mgr.modifier_cache = result
    cache_mgr.last_modifier_file = file_path

    for m_id, mod in cache_mgr.modifier_cache.items():
        mods[m_id] = copy.deepcopy(mod)


# =============================================================================
# Factory Functions
# =============================================================================

def create_component(component_id: str, *, registries: 'GameRegistries') -> Optional["Component"]:
    """Create a clone of a component from the registry by ID.

    PROJ-50: Strict DI - registries is required.

    Args:
        component_id: The ID of the component to create
        registries: GameRegistries for DI (required).

    Returns:
        Component clone or None if not found
    """
    if registries is None:
        raise ValidationException(
            "registries is required for create_component",
            code=ErrorCode.MISSING_DEPENDENCY.value,
            context={"function": "create_component", "parameter": "registries"}
        )
    comps = registries.components

    if component_id in comps:
        clone = comps[component_id].clone()
        clone._registries = registries
        return clone
    logger.error(f"Component ID {component_id} not found in registry.")
    return None


def get_all_components(*, registries: 'GameRegistries') -> List["Component"]:
    """Get a list of all components in the registry.

    PROJ-50: Strict DI - registries is required.

    Args:
        registries: GameRegistries for DI (required).

    Returns:
        List of all Component instances in the registry.
    """
    if registries is None:
        raise ValidationException(
            "registries is required for get_all_components",
            code=ErrorCode.MISSING_DEPENDENCY.value,
            context={"function": "get_all_components", "parameter": "registries"}
        )
    return list(registries.components.values())
