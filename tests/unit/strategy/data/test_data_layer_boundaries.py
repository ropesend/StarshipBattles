"""
Tests that the strategy data/ subpackage does not import from engine/.

PROJ-239 Task 2.1: AR-003 - The data/ subpackage should not depend on engine/.
"""
import ast
import os


class TestDataLayerDoesNotImportEngine:
    """Verify data/ files don't import from engine/."""

    def test_no_engine_imports_in_data_subpackage(self):
        """No file in game/strategy/data/ should import from game.strategy.engine."""
        data_dir = os.path.join("game", "strategy", "data")
        violations = []

        for root, dirs, files in os.walk(data_dir):
            for fname in files:
                if not fname.endswith(".py"):
                    continue
                filepath = os.path.join(root, fname)
                with open(filepath, "r", encoding="utf-8") as f:
                    source = f.read()

                try:
                    tree = ast.parse(source, filename=filepath)
                except SyntaxError:
                    continue

                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module and node.module.startswith("game.strategy.engine"):
                            names = ", ".join(a.name for a in node.names)
                            violations.append(
                                f"{filepath}:{node.lineno} - from {node.module} import {names}"
                            )

        assert violations == [], (
            f"data/ subpackage must not import from engine/. Violations:\n"
            + "\n".join(f"  {v}" for v in violations)
        )


class TestNoSingletonAccessInData:
    """Verify data/ files don't access RegistryManager.instance() directly."""

    def test_no_registry_singleton_in_data(self):
        """No file in game/strategy/data/ should call RegistryManager.instance()."""
        data_dir = os.path.join("game", "strategy", "data")
        violations = []

        for root, dirs, files in os.walk(data_dir):
            for fname in files:
                if not fname.endswith(".py"):
                    continue
                filepath = os.path.join(root, fname)
                with open(filepath, "r", encoding="utf-8") as f:
                    source = f.read()

                if "RegistryManager.instance()" in source:
                    violations.append(filepath)

        assert violations == [], (
            f"data/ should use DI, not RegistryManager.instance(). Violations:\n"
            + "\n".join(f"  {v}" for v in violations)
        )
