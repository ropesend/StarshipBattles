"""Contract tests for ``OrderMetadataView`` (PROJ-424 Phase 2).

The view is the single live, lazy, cycle-safe read facade over
``command_registry``. These tests pin the five derivation properties
plus the two cycle-safety invariants:

- ``test_view_is_lazy_at_import_time`` — the view module's source
  must NOT contain a module-level import of
  ``game.strategy.engine.commands.registry``. Enforced via ``ast``
  inspection of the source file. AST-based pinning is robust against
  ``sys.modules`` contamination from ``game.strategy/__init__.py``'s
  eager imports (which pull the registry in regardless of what any
  individual module imports). The cycle stays broken only as long as
  the registry import is deferred inside ``_registry()``.
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

def _module_level_imports(source_path: Path) -> set[str]:
    """Return the set of fully-qualified module names imported at module
    level (i.e. NOT inside a function or class) by the file at
    ``source_path``."""
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in tree.body:  # only top-level statements
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module is not None:
                names.add(node.module)
    return names


def test_view_is_lazy_at_import_time() -> None:
    """``order_metadata_view`` must NOT import
    ``game.strategy.engine.commands.registry`` at module load.

    The cycle ``order_types -> registry -> handlers -> order_types``
    stays broken only as long as the registry import is deferred
    inside :meth:`OrderMetadataView._registry`. Hoisting that import
    to the module top will reintroduce the cycle.

    Verified by parsing the view's source file and inspecting its
    top-level imports via ``ast``. AST-based pinning is preferred over
    ``sys.modules`` inspection because ``game.strategy/__init__.py``
    eagerly imports the registry through ``TurnEngine``, which
    contaminates ``sys.modules`` regardless of what the view module
    itself imports.
    """
    import game.strategy.engine.commands.order_metadata_view as view_mod

    source_path = Path(view_mod.__file__)
    top_level = _module_level_imports(source_path)
    forbidden = "game.strategy.engine.commands.registry"
    assert forbidden not in top_level, (
        f"{forbidden!r} imported at module top in {source_path}. "
        f"Move it inside OrderMetadataView._registry() to preserve "
        f"the cycle break. Top-level imports observed: {sorted(top_level)}"
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
