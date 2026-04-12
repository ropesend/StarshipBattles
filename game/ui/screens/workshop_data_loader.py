"""
WorkshopDataLoader - Handles loading and reloading game data from a directory (renamed from BuilderDataLoader).

Extracted from DesignWorkshopScreen._reload_data() for better testability and reusability.

PROJ-38: Added registries parameter for dependency injection support.
"""
from json import JSONDecodeError
import os
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Union, TYPE_CHECKING

import logging

logger = logging.getLogger(__name__)
# PROJ-211: Re-added get_default_registry_provider for load_* functions
from game.core.paths import Paths
from game.core.registry import clear_registry, get_default_registry_provider

if TYPE_CHECKING:
    from game.core.registry import GameRegistries


@dataclass
class LoadResult:
    """Structured result from data loading operation."""
    success: bool = True
    default_class: str = "Escort"
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class WorkshopDataLoader:
    """
    Handles loading and reloading game data from a directory (renamed from BuilderDataLoader).
    
    Encapsulates file discovery with priority:
    1. Direct match in target directory
    2. test_ prefixed file in target directory
    3. Fallback to default data directory
    """
    
    def __init__(self, directory: str, default_data_dir: Optional[str] = None,
                 *, registries: 'GameRegistries'):
        """
        Initialize the data loader.

        PROJ-38: Added registries parameter for DI support.
        PROJ-50: Made registries mandatory, removed fallback.

        Args:
            directory: Primary directory to load data from
            default_data_dir: Fallback directory (defaults to cwd/data)
            registries: GameRegistries instance (required for _get_default_class)
        """
        self.directory = directory
        self.default_data_dir = default_data_dir or Paths.DATA_DIR
        self._registries = registries
    
    def find_file(self, base_names: Union[str, List[str]], 
                  allow_default: bool = True) -> Tuple[Optional[str], bool]:
        """
        Locate a data file with fallback logic.
        
        Searches in order:
        1. Direct filename in self.directory
        2. test_ prefixed filename in self.directory
        3. Direct filename in default_data_dir (if allow_default)
        
        Args:
            base_names: Filename or list of alternative filenames to search
            allow_default: Whether to fall back to default directory
            
        Returns:
            Tuple of (path or None, is_fallback_to_default)
        """
        if isinstance(base_names, str):
            base_names = [base_names]
        
        # 1. Check target directory (direct match)
        for name in base_names:
            path = os.path.join(self.directory, name)
            if os.path.exists(path):
                return path, False
            
            # 2. Check target directory (test_ prefix)
            test_path = os.path.join(self.directory, "test_" + name)
            if os.path.exists(test_path):
                return test_path, False
        
        # 3. Fallback to default directory
        if allow_default:
            for name in base_names:
                path = os.path.join(self.default_data_dir, name)
                if os.path.exists(path):
                    return path, True
        
        return None, False
    
    def clear_registries(self) -> None:
        """Clear all game data registries before loading new data."""
        from game.ai.policy_manager import get_default_policy_manager

        clear_registry()

        # Clear PolicyManager data
        get_default_policy_manager().clear()
    
    def load_all(self) -> LoadResult:
        """
        Load all game data and return structured result.

        Loads: modifiers, components, combat strategies, vehicle classes.

        Returns:
            LoadResult with success status, default class, and any errors/warnings
        """
        from game.simulation.components.component import load_components, load_modifiers
        from game.simulation.entities.ship_loader import load_vehicle_classes

        result = LoadResult()

        try:
            # 1. Clear registries first
            self.clear_registries()

            # PROJ-211: Pass registry_provider explicitly (no fallback)
            provider = get_default_registry_provider()

            # 2. Load Modifiers
            mod_path, _ = self.find_file("modifiers.json")
            if mod_path:
                load_modifiers(mod_path, registry_provider=provider)
                logger.info(f"Loaded modifiers from {mod_path}")
            else:
                result.warnings.append("No modifiers.json found")
                logger.warning("No modifiers.json found")

            # 3. Load Components
            comp_path, _ = self.find_file("components.json")
            if comp_path:
                load_components(comp_path, registry_provider=provider)
                logger.info(f"Loaded components from {comp_path}")
            else:
                result.warnings.append("No components.json found")
                logger.warning("No components.json found")
            
            # 4. Load Combat Strategies
            self._load_policies(result)
            
            # 5. Load Vehicle Classes & Layers
            self._load_vehicle_classes(result)
            
            # 6. Determine default class
            result.default_class = self._get_default_class()
            
        except (FileNotFoundError, OSError) as e:
            logger.error(f"Data file error: {e}")
            result.success = False
            result.errors.append(str(e))
        except (JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"Data format error: {e}")
            result.success = False
            result.errors.append(str(e))
        except ValueError as e:
            logger.error(f"Data validation error: {e}")
            result.success = False
            result.errors.append(str(e))
        
        return result
    
    def _load_policies(self, result: LoadResult) -> None:
        """Load targeting and movement policies.

        Uses PolicyManager.load_data() to load from data files.
        """
        from game.ai.policy_manager import get_default_policy_manager

        manager = get_default_policy_manager()
        manager.clear()

        # Check for test data files
        test_targeting = os.path.join(self.directory, "test_targeting_policies.json")
        if os.path.exists(test_targeting):
            manager.load_data(
                base_path=self.directory,
                targeting_file="test_targeting_policies.json",
                movement_file="test_movement_policies.json",
            )
            logger.info(f"Loaded policies from test data in {self.directory}")
        else:
            # Production mode
            manager.load_data(base_path=self.directory)
            logger.info(f"Loaded policies from {self.directory}")
    
    def _load_vehicle_classes(self, result: LoadResult) -> None:
        """Load vehicle classes and layer definitions."""
        from game.simulation.entities.ship_loader import load_vehicle_classes

        vclass_path, _ = self.find_file(["vehicleclasses.json", "classes.json"])
        vlayer_path, _ = self.find_file(["vehiclelayers.json", "layers.json"])

        # PROJ-211: Pass registry_provider explicitly (no fallback)
        provider = get_default_registry_provider()

        if vclass_path:
            if vlayer_path:
                load_vehicle_classes(vclass_path, layers_file_path=vlayer_path, registry_provider=provider)
                logger.info(f"Loaded classes from {vclass_path} with layers from {vlayer_path}")
            else:
                load_vehicle_classes(vclass_path, registry_provider=provider)
                logger.info(f"Loaded classes from {vclass_path}")
        else:
            result.warnings.append("No vehicleclasses.json found")
            logger.warning("No vehicleclasses.json found")
    
    def _get_default_class(self) -> str:
        """Determine the default ship class after loading.

        PROJ-50: Uses injected registries (required).
        """
        default_class = "Escort"
        classes = self._registries.vehicle_classes

        if default_class not in classes and classes:
            # Pick first available class
            default_class = next(iter(classes.keys()))

        return default_class
