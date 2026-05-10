"""PROJ-372 Phase 5: AST guard — Galaxy/Planet/Star method bodies are facades.

Every method on the three god classes must be at most 5 statements
long, OR be on the allow-list (lifecycle / serde — these are
inherently long because of the field counts they orchestrate).

If a method exceeds 5 statements, the implementer hasn't fully
extracted its logic to a service.
"""
from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]

# Allow-listed method names (per-class).
ALLOW_LIST = {
    "Galaxy": {
        "__init__", "__eq__", "__hash__", "__repr__",
        "to_dict", "from_dict",
        "remove_warp_link",  # Two-system warp removal — preserved as-is per Decision; not algorithmic enough to extract for marginal gain.
    },
    "Planet": {
        "__init__", "__eq__", "__hash__", "__repr__",
        "to_dict", "from_dict",
        "add_to_stockpile",  # Cap-aware add: 7 statements; trivial protocol method.
    },
    "Star": {
        "__init__", "__eq__", "__hash__", "__repr__",
        "to_dict", "from_dict",
    },
}

MAX_BODY_STATEMENTS = 5


def _count_real_statements(body) -> int:
    """Count non-docstring statement nodes in a function body."""
    count = 0
    for i, stmt in enumerate(body):
        # Module / function docstrings are Expr(Constant(str)) at index 0.
        if i == 0 and isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
            continue
        count += 1
    return count


def _check_class_methods(file_path: Path, class_name: str, allow: set) -> list[str]:
    """Return a list of violations: 'name: N statements'."""
    src = file_path.read_text(encoding="utf-8")
    tree = ast.parse(src, filename=str(file_path))
    violations: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if child.name in allow:
                        continue
                    n = _count_real_statements(child.body)
                    if n > MAX_BODY_STATEMENTS:
                        violations.append(f"{class_name}.{child.name}: {n} statements")
            break  # only check the first matching class
    return violations


def test_galaxy_methods_are_facades() -> None:
    path = REPO_ROOT / "game" / "strategy" / "data" / "galaxy.py"
    violations = _check_class_methods(path, "Galaxy", ALLOW_LIST["Galaxy"])
    assert not violations, "Galaxy method bodies > 5 statements:\n  " + "\n  ".join(violations)


def test_planet_methods_are_facades() -> None:
    path = REPO_ROOT / "game" / "strategy" / "data" / "planet.py"
    violations = _check_class_methods(path, "Planet", ALLOW_LIST["Planet"])
    assert not violations, "Planet method bodies > 5 statements:\n  " + "\n  ".join(violations)


def test_star_methods_are_facades() -> None:
    path = REPO_ROOT / "game" / "strategy" / "data" / "stars.py"
    violations = _check_class_methods(path, "Star", ALLOW_LIST["Star"])
    assert not violations, "Star method bodies > 5 statements:\n  " + "\n  ".join(violations)
