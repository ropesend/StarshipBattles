"""
Tests that the strategy layer does not import from the AI layer.

PROJ-239 Task 1.2: AR-001 - The architecture requires Strategy to depend
only on Core and Simulation. AI imports are forbidden.
"""
import ast
import os


class TestNoAIImportInStrategy:
    """Verify no game.ai imports exist in game/strategy/."""

    def test_no_ai_imports_in_strategy_layer(self):
        """No file in game/strategy/ should import from game.ai at module level or locally."""
        strategy_dir = os.path.join("game", "strategy")
        violations = []

        for root, dirs, files in os.walk(strategy_dir):
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
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name.startswith("game.ai"):
                                violations.append(
                                    f"{filepath}:{node.lineno} - import {alias.name}"
                                )
                    elif isinstance(node, ast.ImportFrom):
                        if node.module and node.module.startswith("game.ai"):
                            names = ", ".join(a.name for a in node.names)
                            violations.append(
                                f"{filepath}:{node.lineno} - from {node.module} import {names}"
                            )

        assert violations == [], (
            f"Strategy layer must not import from AI layer. Violations:\n"
            + "\n".join(f"  {v}" for v in violations)
        )
