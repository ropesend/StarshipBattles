"""
WorkshopDataLoader - Handles loading and reloading game data from a directory (renamed from BuilderDataLoader).

Extracted from DesignWorkshopGUI._reload_data() for better testability and reusability.
"""
import os
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Union

from game.core.logger import log_error, log_info, log_warning, log_debug
from game.core.registry import RegistryManager, get_vehicle_classes


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
    
    def __init__(self, directory: str, default_data_dir: Optional[str] = None):
        """
        Initialize the data loader.
        
        Args:
            directory: Primary directory to load data from
            default_data_dir: Fallback directory (defaults to cwd/data)
        """
        self.directory = directory
        self.default_data_dir = default_data_dir or os.path.join(os.getcwd(), "data")
    
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
        from game.ai.controller import StrategyManager

        RegistryManager.instance().clear()

        # Clear StrategyManager data
        StrategyManager.instance().clear()
    
    def load_all(self) -> LoadResult:
        """
        Load all game data and return structured result.
        
        Loads: modifiers, components, combat strategies, vehicle classes.
        
        Returns:
            LoadResult with success status, default class, and any errors/warnings
        """
        from game.simulation.components.component import load_components, load_modifiers
        from game.simulation.entities.ship import load_vehicle_classes
        from game.ai.controller import load_combat_strategies

        result = LoadResult()
        
        try:
            # 1. Clear registries first
            self.clear_registries()
            
            # 2. Load Modifiers
            mod_path, _ = self.find_file("modifiers.json")
            if mod_path:
                load_modifiers(mod_path)
                log_info(f"Loaded modifiers from {mod_path}")
            else:
                result.warnings.append("No modifiers.json found")
                log_warning("No modifiers.json found")
            
            # 3. Load Components
            comp_path, _ = self.find_file("components.json")
            if comp_path:
                load_components(comp_path)
                log_info(f"Loaded components from {comp_path}")
            else:
                result.warnings.append("No components.json found")
                log_warning("No components.json found")
            
            # 4. Load Combat Strategies
            self._load_strategies(result)
            
            # 5. Load Vehicle Classes & Layers
            self._load_vehicle_classes(result)
            
            # 6. Determine default class
            result.default_class = self._get_default_class()
            
        except Exception as e:
            log_error(f"Failed to load data: {e}")
            result.success = False
            result.errors.append(str(e))
        
        return result
    
    def _load_strategies(self, result: LoadResult) -> None:
        """Load combat strategies with test mode detection."""
        from game.ai.controller import StrategyManager, load_combat_strategies

        # Check if test files exist (with test_ prefix)
        test_strat = os.path.join(self.directory, "test_combat_strategies.json")

        if os.path.exists(test_strat):
            # Test data mode - use test_ prefixed files
            manager = StrategyManager.instance()
            manager.load_data(
                self.directory,
                targeting_file="test_targeting_policies.json",
                movement_file="test_movement_policies.json",
                strategy_file="test_combat_strategies.json"
            )
            manager._loaded = True
            log_info(f"Loaded strategies from test data in {self.directory}")
        else:
            # Production mode - try standard names
            strat_path, _ = self.find_file(["combatstrategies.json", "combat_strategies.json"])
            if strat_path:
                load_combat_strategies(strat_path)
                log_info(f"Loaded strategies from {strat_path}")
    
    def _load_vehicle_classes(self, result: LoadResult) -> None:
        """Load vehicle classes and layer definitions."""
        from game.simulation.entities.ship import load_vehicle_classes
        
        vclass_path, _ = self.find_file(["vehicleclasses.json", "classes.json"])
        vlayer_path, _ = self.find_file(["vehiclelayers.json", "layers.json"])
        
        if vclass_path:
            if vlayer_path:
                load_vehicle_classes(vclass_path, layers_filepath=vlayer_path)
                log_info(f"Loaded classes from {vclass_path} with layers from {vlayer_path}")
            else:
                load_vehicle_classes(vclass_path)
                log_info(f"Loaded classes from {vclass_path}")
        else:
            result.warnings.append("No vehicleclasses.json found")
            log_warning("No vehicleclasses.json found")
    
    def _get_default_class(self) -> str:
        """Determine the default ship class after loading."""
        default_class = "Escort"
        classes = get_vehicle_classes()
        
        if default_class not in classes and classes:
            # Pick first available class
            default_class = next(iter(classes.keys()))
        
        return default_class
