"""
TestRegistry - Scenario Discovery and Management

This module provides automatic discovery of TestScenario subclasses for both
pytest and Combat Lab. It scans the simulation_tests/scenarios/ directory and
registers all test scenarios with their metadata.

Key Features:
    - Automatic discovery of test scenarios
    - Filtering by category, ID, or tags
    - Metadata extraction for UI display
    - Singleton pattern ensures one registry instance

Architecture:
    The registry bridges pytest and Combat Lab by providing a unified way to
    discover and access test scenarios. Both environments use the same registry
    to find tests.

Usage (pytest):
    ```python
    from test_framework.registry import TestRegistry

    registry = TestRegistry()
    scenarios = registry.get_by_category("Weapons")
    for test_id, info in scenarios.items():
        scenario_cls = info['class']
        scenario = scenario_cls()
        # Run test...
    ```

Usage (Combat Lab):
    ```python
    registry = TestRegistry()
    categories = registry.get_categories()
    # Display categories in UI
    # User selects category
    scenarios = registry.get_by_category(selected_category)
    # Display scenarios in UI
    # User selects scenario
    scenario_info = registry.get_by_id(selected_test_id)
    scenario = scenario_info['class']()
    # Run in visual mode
    ```
"""

import os
import sys
import importlib
import importlib.util
from typing import Dict, List, Type, Any, Optional
from pathlib import Path


class TestRegistry:
    """
    Singleton registry for discovering and managing test scenarios.

    The registry automatically discovers TestScenario subclasses in the
    simulation_tests/scenarios/ directory and provides methods for filtering
    and retrieving them.

    Attributes:
        scenarios: Dict mapping test_id to scenario information
                  Format: {test_id: {'class': ScenarioClass,
                                     'metadata': TestMetadata,
                                     'module': module_name,
                                     'file': file_path}}
    """

    _instance = None

    def __new__(cls):
        """Singleton pattern - only one registry instance."""
        if cls._instance is None:
            cls._instance = super(TestRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize registry and discover scenarios."""
        if self._initialized:
            return

        self.scenarios: Dict[str, Dict[str, Any]] = {}
        self._discover_scenarios()
        self._initialized = True

    def _get_scenarios_dir(self) -> str:
        """
        Get absolute path to simulation_tests/scenarios/ directory.

        Returns:
            Absolute path to scenarios directory
        """
        # This file is in test_framework/registry.py
        test_framework_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(test_framework_dir)
        return os.path.join(project_root, 'simulation_tests', 'scenarios')

    def _discover_scenarios(self):
        """
        Discover all TestScenario subclasses in simulation_tests/scenarios/.

        This method:
        1. Scans all .py files in scenarios directory (except __init__.py and base.py)
        2. Imports each module
        3. Finds TestScenario subclasses
        4. Extracts metadata and registers them

        The registry is populated with scenario information for both pytest
        and Combat Lab to use.
        """
        scenarios_dir = self._get_scenarios_dir()

        if not os.path.exists(scenarios_dir):
            print(f"Warning: Scenarios directory not found: {scenarios_dir}")
            return

        # Import TestScenario base class for type checking
        try:
            from simulation_tests.scenarios.base import TestScenario
        except ImportError as e:
            print(f"Error: Could not import TestScenario base class: {e}")
            return

        # Ensure project root is in path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        # Scan all Python files in scenarios directory
        scenario_files = Path(scenarios_dir).glob('*.py')

        for file_path in scenario_files:
            filename = file_path.name

            # Skip special files
            if filename.startswith('_') or filename == 'base.py':
                continue

            try:
                # Import module dynamically
                module_name = f"simulation_tests.scenarios.{file_path.stem}"
                spec = importlib.util.spec_from_file_location(module_name, file_path)

                if spec is None or spec.loader is None:
                    print(f"Warning: Could not load spec for {file_path}")
                    continue

                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

                # Find TestScenario subclasses in module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)

                    # Check if it's a class and subclass of TestScenario
                    if (isinstance(attr, type) and
                        issubclass(attr, TestScenario) and
                        attr is not TestScenario):

                        # Check if it has metadata
                        if not hasattr(attr, 'metadata') or attr.metadata is None:
                            print(f"Warning: {attr_name} in {filename} has no metadata")
                            continue

                        metadata = attr.metadata
                        test_id = metadata.test_id

                        # Register scenario
                        self.scenarios[test_id] = {
                            'class': attr,
                            'metadata': metadata,
                            'module': module_name,
                            'file': str(file_path)
                        }

                        print(f"Registered scenario: {test_id} - {metadata.name}")

            except Exception as e:
                print(f"Error loading scenario from {filename}: {e}")
                import traceback
                traceback.print_exc()

        print(f"TestRegistry: Discovered {len(self.scenarios)} scenarios")

    def get_all_scenarios(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered scenarios.

        Returns:
            Dictionary mapping test_id to scenario information
            Format: {test_id: {'class': ScenarioClass,
                              'metadata': TestMetadata,
                              'module': module_name,
                              'file': file_path}}

        Example:
            registry = TestRegistry()
            all_scenarios = registry.get_all_scenarios()
            for test_id, info in all_scenarios.items():
                print(f"{test_id}: {info['metadata'].name}")
        """
        return self.scenarios.copy()

    def get_by_id(self, test_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific scenario by test ID.

        Args:
            test_id: Test ID (e.g., "BEAM-001")

        Returns:
            Scenario information dict, or None if not found

        Example:
            registry = TestRegistry()
            scenario_info = registry.get_by_id("BEAM-001")
            if scenario_info:
                scenario = scenario_info['class']()
                print(scenario.metadata.summary)
        """
        return self.scenarios.get(test_id)

    def get_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all scenarios in a specific category.

        Args:
            category: Category name (e.g., "Weapons", "Propulsion")

        Returns:
            Dictionary of scenarios in that category

        Example:
            registry = TestRegistry()
            weapon_tests = registry.get_by_category("Weapons")
            for test_id, info in weapon_tests.items():
                print(f"  {test_id}: {info['metadata'].name}")
        """
        return {
            test_id: info
            for test_id, info in self.scenarios.items()
            if info['metadata'].category == category
        }

    def get_by_subcategory(self, category: str, subcategory: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all scenarios in a specific category and subcategory.

        Args:
            category: Category name (e.g., "Weapons")
            subcategory: Subcategory name (e.g., "Beam Accuracy")

        Returns:
            Dictionary of scenarios matching both filters

        Example:
            registry = TestRegistry()
            beam_tests = registry.get_by_subcategory("Weapons", "Beam Accuracy")
        """
        return {
            test_id: info
            for test_id, info in self.scenarios.items()
            if (info['metadata'].category == category and
                info['metadata'].subcategory == subcategory)
        }

    def get_by_tag(self, tag: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all scenarios with a specific tag.

        Args:
            tag: Tag to filter by (e.g., "accuracy", "edge_case")

        Returns:
            Dictionary of scenarios with that tag

        Example:
            registry = TestRegistry()
            accuracy_tests = registry.get_by_tag("accuracy")
        """
        return {
            test_id: info
            for test_id, info in self.scenarios.items()
            if tag in info['metadata'].tags
        }

    def get_categories(self) -> List[str]:
        """
        Get list of all unique categories.

        Returns:
            Sorted list of category names

        Example:
            registry = TestRegistry()
            categories = registry.get_categories()
            # ['Abilities', 'Propulsion', 'Resources', 'Weapons']
        """
        categories = set(
            info['metadata'].category
            for info in self.scenarios.values()
        )
        return sorted(categories)

    def get_subcategories(self, category: str) -> List[str]:
        """
        Get list of subcategories within a category.

        Args:
            category: Category to get subcategories for

        Returns:
            Sorted list of subcategory names

        Example:
            registry = TestRegistry()
            subcats = registry.get_subcategories("Weapons")
            # ['Beam Accuracy', 'Projectile Damage', 'Seeker Tracking']
        """
        subcategories = set(
            info['metadata'].subcategory
            for info in self.scenarios.values()
            if info['metadata'].category == category
        )
        return sorted(subcategories)

    def get_all_tags(self) -> List[str]:
        """
        Get list of all unique tags across all scenarios.

        Returns:
            Sorted list of tag names

        Example:
            registry = TestRegistry()
            tags = registry.get_all_tags()
            # ['accuracy', 'damage', 'edge_case', 'range']
        """
        tags = set()
        for info in self.scenarios.values():
            tags.update(info['metadata'].tags)
        return sorted(tags)

    def search(self, query: str) -> Dict[str, Dict[str, Any]]:
        """
        Search scenarios by name, summary, or test ID.

        Args:
            query: Search string (case-insensitive)

        Returns:
            Dictionary of matching scenarios

        Example:
            registry = TestRegistry()
            results = registry.search("beam accuracy")
            # Returns all scenarios with "beam accuracy" in name/summary
        """
        query_lower = query.lower()
        return {
            test_id: info
            for test_id, info in self.scenarios.items()
            if (query_lower in info['metadata'].name.lower() or
                query_lower in info['metadata'].summary.lower() or
                query_lower in test_id.lower())
        }

    def clear(self):
        """
        Clear the registry (useful for testing).

        This forces a re-discovery on next access.
        """
        self.scenarios.clear()
        self._initialized = False

    def refresh(self):
        """
        Refresh the registry by re-discovering scenarios.

        This is useful if scenario files have been added or modified.
        """
        self.clear()
        self._discover_scenarios()
        self._initialized = True

    def print_summary(self):
        """
        Print a summary of registered scenarios organized by category.

        Useful for debugging and verification.
        """
        print("\n" + "=" * 80)
        print("TEST REGISTRY SUMMARY")
        print("=" * 80)

        categories = self.get_categories()

        if not categories:
            print("No scenarios registered.")
            return

        for category in categories:
            print(f"\n{category}")
            print("-" * 80)

            category_scenarios = self.get_by_category(category)
            subcats = {}

            # Group by subcategory
            for test_id, info in category_scenarios.items():
                subcat = info['metadata'].subcategory
                if subcat not in subcats:
                    subcats[subcat] = []
                subcats[subcat].append((test_id, info))

            # Print by subcategory
            for subcat in sorted(subcats.keys()):
                print(f"\n  {subcat}:")
                for test_id, info in sorted(subcats[subcat], key=lambda x: x[0]):
                    metadata = info['metadata']
                    print(f"    {test_id}: {metadata.name}")
                    print(f"        {metadata.summary}")

        print("\n" + "=" * 80)
        print(f"Total scenarios: {len(self.scenarios)}")
        print("=" * 80 + "\n")


# Convenience function for getting singleton instance
def get_registry() -> TestRegistry:
    """
    Get the singleton TestRegistry instance.

    Returns:
        TestRegistry instance

    Example:
        from test_framework.registry import get_registry

        registry = get_registry()
        scenarios = registry.get_all_scenarios()
    """
    return TestRegistry()


if __name__ == "__main__":
    # Test the registry
    registry = TestRegistry()
    registry.print_summary()
