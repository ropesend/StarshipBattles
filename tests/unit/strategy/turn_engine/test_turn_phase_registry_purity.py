"""
PROJ-428 Phase 4 (TD-04) — Registry-purity AST guard.

Pins three invariants on ``game/strategy/engine/turn_phase_registry.py``:

1. Zero module-level ``FunctionDef`` / ``AsyncFunctionDef`` nodes — the
   module is descriptor data + dataclasses + constants only.
2. Zero gameplay engine imports. Specifically, no top-level
   ``import``/``from … import`` that references ``MinefieldResolver``,
   ``PlanetModifierEffectEngine``, or any module under
   ``game.strategy.engine.*_engine`` / ``minefield_resolver`` /
   ``planet_modifier_effect_engine``.
3. ``DEFAULT_TICK_PHASE_LIST`` and ``DEFAULT_END_OF_TURN_PHASE_LIST``
   keep the same phase keys in the same order.

Any of these failing means the registry has drifted back toward
behavior-bearing helpers; that is intentionally a hard failure.
"""
from __future__ import annotations

import ast
from pathlib import Path


REGISTRY_PATH = (
    Path(__file__).resolve().parents[4]
    / "game"
    / "strategy"
    / "engine"
    / "turn_phase_registry.py"
)


# Pinned golden orders. Any reorder/rename is a regression that should
# break this test loudly.
GOLDEN_TICK_PHASE_KEYS: tuple[str, ...] = (
    'harvesting',
    'resources',
    'fuel_gen',
    'planet_energy',
    'resupply',
    'production',
    'environmental',
    'instant_orders',
    'actions',
    'planet_actions',
    'activation_timers',
    'planet_modifier_effects',
    'movement_calc',
    'movement_apply',
    'combat',
)

GOLDEN_END_OF_TURN_PHASE_KEYS: tuple[str, ...] = (
    'organics_consumption',
    'happiness',
    'population_growth',
    'quality_improvement',
    'atmosphere',
    'water_modification',
)


# Forbidden gameplay-engine module substrings. Any top-level
# ``ImportFrom`` whose ``module`` matches a substring here is a
# violation. The list is intentionally aggressive — the registry must
# stay descriptor-only.
_FORBIDDEN_ENGINE_IMPORT_SUBSTRINGS: tuple[str, ...] = (
    "minefield_resolver",
    "planet_modifier_effect_engine",
    "production_engine",
    "harvesting_engine",
    "fleet_movement_engine",
    "conflict_resolution_engine",
    "consumable_management_engine",
    "resupply_engine",
    "action_execution_engine",
    "environmental_hazard_engine",
    "planet_energy_engine",
    "planet_action_engine",
    "component_activation_engine",
    "organics_consumption_engine",
    "happiness_engine",
    "quality_engine",
    "atmosphere_engine",
    "water_engine",
    "population_engine",
)

# Forbidden top-level imported names. ``MinefieldResolver`` /
# ``PlanetModifierEffectEngine`` must never be imported at module scope.
_FORBIDDEN_IMPORTED_NAMES: tuple[str, ...] = (
    "MinefieldResolver",
    "PlanetModifierEffectEngine",
)


def _parse_registry() -> ast.Module:
    src = REGISTRY_PATH.read_text(encoding="utf-8")
    return ast.parse(src)


def _collect_dynamic_import_target(call: ast.Call) -> str | None:
    """Return the string-literal argument of an ``importlib.import_module(...)``
    or ``__import__(...)`` call, or ``None`` if the call is not one of those
    forms or its first argument is not a string literal.

    Catches both:
      * ``importlib.import_module("a.b.c")`` -> ``Attribute(attr='import_module')``
      * ``__import__("a.b.c")``              -> ``Name(id='__import__')``
    """
    func = call.func
    is_target = False
    if isinstance(func, ast.Attribute) and func.attr == "import_module":
        is_target = True
    elif isinstance(func, ast.Name) and func.id == "__import__":
        is_target = True
    if not is_target or not call.args:
        return None
    first = call.args[0]
    if isinstance(first, ast.Constant) and isinstance(first.value, str):
        return first.value
    return None


def _iter_module_load_evaluated_statements(
    tree: ast.Module,
) -> list[ast.stmt]:
    """Yield every statement that is *evaluated at module load*.

    That is: the module-top statements plus the bodies of every top-level
    ``class`` (class bodies execute eagerly at module load). Function and
    method bodies are NOT included — those are deferred until the function
    is called.
    """
    stmts: list[ast.stmt] = list(tree.body)
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            stmts.extend(node.body)
    return stmts


def _find_forbidden_engine_imports(tree: ast.Module) -> list[str]:
    """Return human-readable descriptions of every forbidden gameplay-engine
    import or dynamic-import call that is evaluated at module load by
    ``tree``.

    Detects:

    1. Static module-top ``import`` / ``from ... import`` statements
       referencing a forbidden engine module substring or imported name.
    2. ``import`` / ``from ... import`` statements inside a top-level
       ``class`` body (class bodies execute at module load).
    3. Top-level ``importlib.import_module("...")`` and ``__import__("...")``
       calls (including inside top-level class bodies) whose string-literal
       argument names a forbidden engine module.

    Imports inside function or method bodies are NOT flagged — those are
    lazy by design and do not execute at module load.
    """
    offenders: list[str] = []

    def _check_static_import(node: ast.stmt) -> None:
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for forbidden in _FORBIDDEN_ENGINE_IMPORT_SUBSTRINGS:
                if forbidden in module:
                    offenders.append(
                        f"from {module} import "
                        f"{', '.join(a.name for a in node.names)}"
                    )
                    return
            for alias in node.names:
                if alias.name in _FORBIDDEN_IMPORTED_NAMES:
                    offenders.append(
                        f"from {module} import {alias.name}"
                    )
                    return
        elif isinstance(node, ast.Import):
            for alias in node.names:
                for forbidden in _FORBIDDEN_ENGINE_IMPORT_SUBSTRINGS:
                    if forbidden in alias.name:
                        offenders.append(f"import {alias.name}")
                        break

    def _check_dynamic_call_in_value(value: ast.expr) -> None:
        if not isinstance(value, ast.Call):
            return
        target = _collect_dynamic_import_target(value)
        if target is None:
            return
        for forbidden in _FORBIDDEN_ENGINE_IMPORT_SUBSTRINGS:
            if forbidden in target:
                offenders.append(
                    f"dynamic import of {target!r} at module load"
                )
                return

    for node in _iter_module_load_evaluated_statements(tree):
        _check_static_import(node)
        if isinstance(node, ast.Expr):
            _check_dynamic_call_in_value(node.value)
        elif isinstance(node, ast.Assign):
            _check_dynamic_call_in_value(node.value)
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            _check_dynamic_call_in_value(node.value)

    return offenders


class TestRegistryHasNoModuleLevelFunctions:
    """The registry module must contain zero module-level function
    definitions — pure descriptor data only."""

    def test_no_module_level_functiondef(self):
        tree = _parse_registry()
        offenders: list[str] = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                offenders.append(node.name)
        assert not offenders, (
            f"turn_phase_registry.py has module-level function defs: "
            f"{offenders}. PROJ-428 keeps this module descriptor-only; "
            f"move behavior onto TurnEngine or a named collaborator."
        )


class TestRegistryHasNoGameplayEngineImports:
    """The registry must not import any gameplay engine class or module
    at module load. Construction lives on TurnEngine or its
    collaborators.

    "At module load" includes both module-top statements AND the bodies
    of top-level class definitions (which execute eagerly when the
    module is first imported), plus dynamic
    ``importlib.import_module(...)`` / ``__import__(...)`` calls in
    either location. Function/method bodies are lazy and are NOT
    inspected.
    """

    def test_no_forbidden_engine_module_imports(self):
        tree = _parse_registry()
        offenders = _find_forbidden_engine_imports(tree)
        assert not offenders, (
            f"turn_phase_registry.py imports gameplay engine modules at "
            f"module load: {offenders}. Move construction to TurnEngine "
            f"or its collaborators."
        )


# ---------------------------------------------------------------------------
# Hardened-guard regression tests (PROJ-428 Phase 6).
#
# Each synthetic source string proves the guard catches a previously-
# possible bypass: class-body imports, top-level
# ``importlib.import_module(...)``, top-level ``__import__(...)``. The
# function-body case proves the guard correctly leaves lazy imports
# alone.
# ---------------------------------------------------------------------------


class TestGuardCatchesBypassVectors:
    """Synthetic-source regression tests for the hardened AST walker.

    These mirror the PROJ-424 Phase 7 hardening of the lazy-import guard
    at ``tests/unit/strategy/engine/commands/test_order_metadata_view.py``.
    Without this hardening, a contributor could bypass the registry-
    purity guard by hiding a forbidden import inside a class body or by
    routing it through ``importlib.import_module``.
    """

    def test_guard_detects_class_body_import_of_planet_modifier_engine(
        self,
    ) -> None:
        """A class-body import of a gameplay engine executes at module
        load and MUST be reported. Without this, a contributor could
        ``hide`` the forbidden import inside a top-level class body."""
        source = (
            "class _RegistryShim:\n"
            "    from game.strategy.engine.planet_modifier_effect_engine "
            "import PlanetModifierEffectEngine\n"
            "    pass\n"
        )
        tree = ast.parse(source)
        offenders = _find_forbidden_engine_imports(tree)
        assert offenders, (
            "Guard failed to catch class-body import of "
            "PlanetModifierEffectEngine."
        )

    def test_guard_detects_top_level_importlib_import_module_call(
        self,
    ) -> None:
        """A top-level ``importlib.import_module("...minefield_resolver")``
        call evaluates at module load and MUST be reported."""
        source = (
            "import importlib\n"
            "importlib.import_module("
            "\"game.strategy.engine.minefield_resolver\")\n"
        )
        tree = ast.parse(source)
        offenders = _find_forbidden_engine_imports(tree)
        assert offenders, (
            "Guard failed to catch top-level "
            "importlib.import_module(\"...minefield_resolver\") call."
        )

    def test_guard_detects_top_level_dunder_import_call(self) -> None:
        """A top-level ``__import__("...planet_modifier_effect_engine")``
        call evaluates at module load and MUST be reported."""
        source = (
            "__import__("
            "\"game.strategy.engine.planet_modifier_effect_engine\")\n"
        )
        tree = ast.parse(source)
        offenders = _find_forbidden_engine_imports(tree)
        assert offenders, (
            "Guard failed to catch top-level "
            "__import__(\"...planet_modifier_effect_engine\") call."
        )

    def test_guard_ignores_function_body_import(self) -> None:
        """An import inside a function body is deferred until the
        function is called — exactly the cycle-break contract
        ``TurnEngine`` lazy properties rely on. The guard MUST NOT
        flag it."""
        source = (
            "def _planet_modifier_engine():\n"
            "    from game.strategy.engine.planet_modifier_effect_engine "
            "import PlanetModifierEffectEngine\n"
            "    return PlanetModifierEffectEngine\n"
        )
        tree = ast.parse(source)
        offenders = _find_forbidden_engine_imports(tree)
        assert not offenders, (
            "Guard incorrectly flagged a function-body (lazy) import "
            f"of PlanetModifierEffectEngine; observed: {offenders}"
        )


class TestRegistryDescriptorListsAreGolden:
    """The two pinned descriptor lists must keep the same phase keys in
    the same order. Reordering is a regression."""

    def test_default_tick_phase_list_keys_match_golden(self):
        from game.strategy.engine.turn_phase_registry import (
            DEFAULT_TICK_PHASE_LIST,
        )

        actual = tuple(p.phase_key for p in DEFAULT_TICK_PHASE_LIST)
        assert actual == GOLDEN_TICK_PHASE_KEYS

    def test_default_end_of_turn_phase_list_keys_match_golden(self):
        from game.strategy.engine.turn_phase_registry import (
            DEFAULT_END_OF_TURN_PHASE_LIST,
        )

        actual = tuple(p.phase_key for p in DEFAULT_END_OF_TURN_PHASE_LIST)
        assert actual == GOLDEN_END_OF_TURN_PHASE_KEYS
