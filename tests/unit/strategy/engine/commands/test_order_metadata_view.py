"""Contract tests for ``OrderMetadataView`` (PROJ-424 Phase 2).

The view is the single live, lazy, cycle-safe read facade over
``command_registry``. These tests pin the five derivation properties
plus the two cycle-safety invariants:

- ``test_view_is_lazy_at_import_time`` — the view module's source
  must NOT evaluate an import of
  ``game.strategy.engine.commands.registry`` at module load by ANY
  mechanism: top-level ``import`` / ``from`` statements, class-body
  imports (class bodies execute at module load), or dynamic
  ``importlib.import_module(...)`` / ``__import__(...)`` calls at
  module scope. Enforced via ``ast`` inspection of the source file
  by :func:`_module_load_evaluated_imports`. AST-based pinning is
  robust against ``sys.modules`` contamination from
  ``game.strategy/__init__.py``'s eager imports (which pull the
  registry in regardless of what any individual module imports). The
  cycle stays broken only as long as the registry import is deferred
  inside ``_registry()`` (or some other function body that is not
  called at module load).
- ``test_view_reflects_replace_overlay`` — registering an overlay
  spec via ``replace=True`` is immediately visible through the view
  (no cached snapshot).

The pattern verified here is mirrored by PROJ-429 (TD-07 ability
metadata convergence).
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from game.strategy.data.order_types import OrderType
from game.strategy.engine.commands.order_metadata_view import (
    OrderMetadataView,
    order_metadata,
)
from game.strategy.engine.commands.registry import (
    CommandSpec,
    command_registry,
    reset_command_registry,
    seed_default_commands,
)


@pytest.fixture(autouse=True)
def _seeded_registry():
    """Each test runs against the freshly-seeded default registry."""
    if len(command_registry) == 0:
        seed_default_commands(command_registry)
    yield
    # Restore the canonical seed in case a test mutated the registry.
    reset_command_registry()


# ---------------------------------------------------------------------------
# Derivation parity — view properties == registry methods.
# ---------------------------------------------------------------------------

def test_view_movement_matches_registry() -> None:
    assert order_metadata.movement_order_types == command_registry.movement_order_types()


def test_view_action_matches_registry() -> None:
    assert order_metadata.action_order_types == command_registry.action_order_types()


def test_view_planet_action_matches_registry() -> None:
    assert (
        order_metadata.planet_action_order_types
        == command_registry.planet_action_order_types()
    )


def test_view_planet_fms_matches_registry() -> None:
    assert (
        order_metadata.planet_fms_action_order_types
        == command_registry.planet_fms_action_order_types()
    )


def test_view_order_to_ability_matches_registry() -> None:
    assert (
        order_metadata.order_to_ability_map
        == command_registry.order_to_ability_map()
    )


# ---------------------------------------------------------------------------
# Cycle-safety: importing the view module does NOT import the registry.
# ---------------------------------------------------------------------------

def _module_load_evaluated_imports(source: str) -> set[str]:
    """Return the set of fully-qualified module names that are
    imported, dynamically imported, or otherwise *evaluated* at module
    load time by ``source``.

    "Module-load-evaluated" means any of:

    * A top-level ``import`` or ``from ... import`` statement.
    * An ``import`` / ``from ... import`` statement that appears in the
      body of a top-level ``class`` (class bodies execute at module
      load).
    * A top-level (or top-level class-body) call to
      ``importlib.import_module("dotted.path")`` or
      ``__import__("dotted.path")`` with a string-literal argument.

    Imports inside function or method bodies are NOT collected —
    function bodies are deferred until the function is called, which
    is the contract :class:`OrderMetadataView` relies on for cycle
    safety. Top-level calls to those functions would still be caught
    by the static + dynamic detection above (a function defined here
    but only referenced, not invoked, at module scope is harmless).
    """
    tree = ast.parse(source)
    names: set[str] = set()

    def _collect_dynamic_from_call(call: ast.Call) -> None:
        # importlib.import_module("a.b.c") -> Attribute(attr='import_module')
        # __import__("a.b.c")              -> Name(id='__import__')
        target_module: str | None = None
        func = call.func
        if isinstance(func, ast.Attribute) and func.attr == "import_module":
            target_module = "import_module"
        elif isinstance(func, ast.Name) and func.id == "__import__":
            target_module = "__import__"
        if target_module is None:
            return
        if not call.args:
            return
        first = call.args[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            names.add(first.value)

    def _scan_statement_list(stmts: list[ast.stmt]) -> None:
        for node in stmts:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    names.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module is not None:
                    names.add(node.module)
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                _collect_dynamic_from_call(node.value)
            elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                _collect_dynamic_from_call(node.value)
            elif isinstance(node, ast.AnnAssign) and isinstance(node.value, ast.Call):
                _collect_dynamic_from_call(node.value)

    # Module-top statements.
    _scan_statement_list(tree.body)
    # Top-level class bodies also execute at module load.
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            _scan_statement_list(node.body)

    return names


def _module_level_imports(source_path: Path) -> set[str]:
    """Backward-compatible file wrapper around
    :func:`_module_load_evaluated_imports`."""
    return _module_load_evaluated_imports(
        source_path.read_text(encoding="utf-8")
    )


# ---------------------------------------------------------------------------
# Hardened guard regressions: each synthetic source string proves the
# guard catches a previously-possible bypass.
# ---------------------------------------------------------------------------

_FORBIDDEN_REGISTRY_PATH = "game.strategy.engine.commands.registry"


def test_guard_detects_class_body_import_of_registry() -> None:
    """A class-body import of the registry executes at module load and
    MUST be reported. Without this, a contributor could "hide" the
    forbidden import inside a top-level class definition."""
    source = (
        "class _ViewImpl:\n"
        "    from game.strategy.engine.commands.registry import command_registry\n"
        "    pass\n"
    )
    found = _module_load_evaluated_imports(source)
    assert _FORBIDDEN_REGISTRY_PATH in found, (
        "Guard failed to catch class-body import of "
        f"{_FORBIDDEN_REGISTRY_PATH!r}; observed: {sorted(found)}"
    )


def test_guard_detects_top_level_importlib_import_module_call() -> None:
    """A top-level ``importlib.import_module(...)`` call evaluates at
    module load and MUST be reported when its string argument names
    the registry module."""
    source = (
        "import importlib\n"
        "importlib.import_module(\"game.strategy.engine.commands.registry\")\n"
    )
    found = _module_load_evaluated_imports(source)
    assert _FORBIDDEN_REGISTRY_PATH in found, (
        "Guard failed to catch top-level importlib.import_module call "
        f"targeting {_FORBIDDEN_REGISTRY_PATH!r}; observed: {sorted(found)}"
    )


def test_guard_detects_top_level_dunder_import_call() -> None:
    """A top-level ``__import__(...)`` call evaluates at module load
    and MUST be reported when its string argument names the registry
    module."""
    source = (
        "__import__(\"game.strategy.engine.commands.registry\")\n"
    )
    found = _module_load_evaluated_imports(source)
    assert _FORBIDDEN_REGISTRY_PATH in found, (
        "Guard failed to catch top-level __import__ call "
        f"targeting {_FORBIDDEN_REGISTRY_PATH!r}; observed: {sorted(found)}"
    )


def test_guard_ignores_function_body_import() -> None:
    """An import inside a function body is deferred until the function
    is called — exactly the cycle-break contract the view relies on.
    The guard MUST NOT flag it."""
    source = (
        "def _registry():\n"
        "    from game.strategy.engine.commands.registry import command_registry\n"
        "    return command_registry\n"
    )
    found = _module_load_evaluated_imports(source)
    assert _FORBIDDEN_REGISTRY_PATH not in found, (
        "Guard incorrectly flagged a function-body (lazy) import of "
        f"{_FORBIDDEN_REGISTRY_PATH!r}; observed: {sorted(found)}"
    )


def test_view_is_lazy_at_import_time() -> None:
    """``order_metadata_view`` must NOT evaluate an import of
    ``game.strategy.engine.commands.registry`` at module load — by
    any mechanism.

    The cycle ``order_types -> registry -> handlers -> order_types``
    stays broken only as long as the registry import is deferred
    inside :meth:`OrderMetadataView._registry`. Hoisting that import
    to the module top, slipping it into a top-level class body, or
    smuggling it in via ``importlib.import_module(...)`` /
    ``__import__(...)`` at module scope would all reintroduce the
    cycle. The helper :func:`_module_load_evaluated_imports` covers
    all of those vectors; see its dedicated regression tests above.

    Verified by parsing the view's source file via ``ast``. AST-based
    pinning is preferred over ``sys.modules`` inspection because
    ``game.strategy/__init__.py`` eagerly imports the registry
    through ``TurnEngine``, which contaminates ``sys.modules``
    regardless of what the view module itself imports.
    """
    import game.strategy.engine.commands.order_metadata_view as view_mod

    source_path = Path(view_mod.__file__)
    module_load_imports = _module_level_imports(source_path)
    forbidden = "game.strategy.engine.commands.registry"
    assert forbidden not in module_load_imports, (
        f"{forbidden!r} is module-load-evaluated in {source_path}. "
        f"Move it inside OrderMetadataView._registry() (or another "
        f"function body) to preserve the cycle break. "
        f"Module-load-evaluated imports observed: "
        f"{sorted(module_load_imports)}"
    )


def test_view_reflects_replace_overlay() -> None:
    """A ``replace=True`` overlay must be visible through the view
    immediately. No caching, no snapshot.

    Picks an OrderType that already carries an ``action_ability_name``
    (COLONIZE -> ColonizePlanet) and re-registers its spec with a
    different ability name; the view's ``order_to_ability_map`` must
    reflect the change without any explicit invalidation call.
    """
    before = order_metadata.order_to_ability_map
    assert before[OrderType.COLONIZE] == "ColonizePlanet"

    original_spec = command_registry.get("IssueColonizeCommand")
    assert original_spec is not None

    overlay = CommandSpec(
        command_class=original_spec.command_class,
        order_type=original_spec.order_type,
        handler_class=original_spec.handler_class,
        category=original_spec.category,
        subcategories=original_spec.subcategories,
        action_ability_name="OverlayColonizeAbility",
        execution_model=original_spec.execution_model,
        facade_helper_name=original_spec.facade_helper_name,
        serializer_codec=original_spec.serializer_codec,
    )
    command_registry.register(overlay, replace=True)

    after = order_metadata.order_to_ability_map
    assert after[OrderType.COLONIZE] == "OverlayColonizeAbility", (
        "OrderMetadataView did not pick up the replace=True overlay — "
        "view must be live, not a cached snapshot."
    )


# ---------------------------------------------------------------------------
# Singleton + type sanity.
# ---------------------------------------------------------------------------

def test_order_metadata_is_singleton_instance_of_view() -> None:
    assert isinstance(order_metadata, OrderMetadataView)
