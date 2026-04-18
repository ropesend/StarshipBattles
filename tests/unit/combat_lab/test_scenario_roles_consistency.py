"""Consistency check: every literal role label referenced in
`combat_lab/scenarios/*.py` must be registered in
`combat_lab_role_registry` (loaded from `combat_lab/data/scenario_roles.json`).

Catches role-label typos at test time. Phase 3 of PROJ-278 — see
`Projects/active_projects/PROJ-278/phase_3_checklist.md` Task 3.4.

Limitations:
  - AST scan only detects LITERAL string keys: `ships_by_role["attacker"]`
    or `ships_by_role.get("target")`. Dynamic keys (variables, kwargs,
    f-strings) are NOT caught — those rely on author discipline.
  - One known dynamic-key site exists: `combat_lab/scenarios/templates.py`
    around line 1115 uses `role_attacker` / `role_target` variables. Those
    variables resolve to literal strings at scenario authoring time, but
    the AST scanner won't see them. They're documented in the audit.
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Set

import pytest

from combat_lab.scenario_role_registry import (
    get_default_combat_lab_role_registry,
    reset_default_combat_lab_role_registry,
)


SCENARIOS_DIR = Path(__file__).resolve().parents[3] / "combat_lab" / "scenarios"


@pytest.fixture(autouse=True)
def _reset_registry():
    reset_default_combat_lab_role_registry()
    yield
    reset_default_combat_lab_role_registry()


def _extract_referenced_role_names(scenarios_dir: Path) -> Set[str]:
    """Walk every `.py` file under `scenarios_dir`. Collect every literal
    string used as a key against `ships_by_role` or `initial_state` —
    e.g. `ships_by_role["attacker"]`, `ships_by_role.get("target")`.

    Skips dynamic keys (Name nodes, attribute accesses, f-strings).
    Returns the set of distinct literal role names.
    """
    referenced: Set[str] = set()
    target_receivers = {"ships_by_role", "initial_state"}

    for py_file in scenarios_dir.rglob("*.py"):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except (SyntaxError, OSError):
            continue

        for node in ast.walk(tree):
            # Pattern: ships_by_role["attacker"]
            if isinstance(node, ast.Subscript):
                receiver = _receiver_name(node.value)
                if receiver in target_receivers:
                    key = _literal_string(node.slice)
                    if key is not None:
                        referenced.add(key)

            # Pattern: ships_by_role.get("attacker") or .pop("attacker")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    receiver = _receiver_name(node.func.value)
                    if receiver in target_receivers:
                        if node.args:
                            key = _literal_string(node.args[0])
                            if key is not None:
                                referenced.add(key)

    return referenced


def _receiver_name(node: ast.AST) -> str:
    """Extract the receiver variable name from a Subscript or Attribute base."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _literal_string(node: ast.AST):
    """Return the literal string from an ast Constant or Index(Constant), else None."""
    # Python 3.9+: subscript slice is the expression directly
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


class TestScenarioRolesConsistency:
    """Every role label referenced by a literal string in scenario code
    must be registered in `combat_lab_role_registry`."""

    def test_every_referenced_role_is_registered(self):
        referenced = _extract_referenced_role_names(SCENARIOS_DIR)
        assert referenced, (
            "Scanner found no role references at all — "
            "scanner may be broken or scenarios directory is empty"
        )

        registry = get_default_combat_lab_role_registry()
        registered = {r.id for r in registry.all()}

        unregistered = referenced - registered
        assert not unregistered, (
            f"Role labels referenced in scenarios but missing from "
            f"combat_lab/data/scenario_roles.json: {sorted(unregistered)}. "
            f"Add them to the data file."
        )

    def test_scanner_finds_known_baseline_roles(self):
        """Sanity check: the scanner should at minimum find the core roles
        used by the canonical templates."""
        referenced = _extract_referenced_role_names(SCENARIOS_DIR)
        baseline = {"attacker", "target", "ship1", "ship2", "ship"}
        missing = baseline - referenced
        assert not missing, (
            f"Scanner missed baseline roles {missing} — "
            f"scanner logic may be broken"
        )
