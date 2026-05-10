"""AST regression: no ``COMMAND_SPECS = (...)`` tuple literal in ``game/``.

PROJ-371 Phase 2 deleted ``game/strategy/engine/commands/specs.py``. The
:class:`CommandRegistry` is the single source of truth. Reintroducing a
module-level tuple of ``CommandSpec`` rows would silently bring back the
pre-PROJ-371 architecture.

The walker scans every ``*.py`` file under ``game/`` and flags any
top-level ``ast.Assign`` whose RHS is an ``ast.Tuple`` with one or more
``ast.Call(func=ast.Name(id='CommandSpec'))`` elements. Allowed in
``tests/`` (e.g. ``test_command_specs_contract.py`` rebuilds a local
view from the registry).

Test design notes:
- The walker also has a self-test that feeds it synthetic AST shapes,
  proving the test isn't vacuous (would catch a regression).
"""
from __future__ import annotations

import ast
from pathlib import Path

GAME_ROOT = Path(__file__).resolve().parents[4] / "game"
ALLOWED_RELATIVE_PATHS: frozenset[str] = frozenset()  # currently none


def _file_has_command_spec_tuple_literal(tree: ast.Module) -> bool:
    """True iff ``tree`` contains a top-level Assign whose RHS is a Tuple
    with at least one ``CommandSpec(...)`` Call element.
    """
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        rhs = node.value
        if not isinstance(rhs, ast.Tuple):
            continue
        for elt in rhs.elts:
            if (
                isinstance(elt, ast.Call)
                and isinstance(elt.func, ast.Name)
                and elt.func.id == "CommandSpec"
            ):
                return True
    return False


def test_no_command_specs_tuple_literal_in_game() -> None:
    """No production module under ``game/`` may declare ``COMMAND_SPECS = (...)``."""
    assert GAME_ROOT.is_dir(), f"GAME_ROOT does not exist: {GAME_ROOT}"
    offending: list[str] = []
    for path in GAME_ROOT.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        rel = str(path.relative_to(GAME_ROOT)).replace("\\", "/")
        if rel in ALLOWED_RELATIVE_PATHS:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            # Malformed source files are someone else's problem — skip.
            continue
        if _file_has_command_spec_tuple_literal(tree):
            offending.append(rel)
    assert offending == [], (
        "PROJ-371 regression: the following files declare a module-level "
        "tuple of CommandSpec(...) rows. Adding a 36th command must use "
        "the @command_spec(...) decorator + per-module register(registry) "
        "function, not a tuple literal. Offending files:\n  - "
        + "\n  - ".join(offending)
    )


# ---------------------------------------------------------------------------
# Walker self-tests — prove the walker actually flags regressions.
# ---------------------------------------------------------------------------

def test_walker_flags_synthetic_command_spec_tuple() -> None:
    """Synthetic positive: a CommandSpec(...) tuple literal IS flagged."""
    src = (
        "COMMAND_SPECS = (\n"
        "    CommandSpec(command_class=Foo, order_type=None,\n"
        "                handler_class=FooHandler, category='action'),\n"
        ")\n"
    )
    tree = ast.parse(src)
    assert _file_has_command_spec_tuple_literal(tree) is True


def test_walker_does_not_flag_unrelated_tuple() -> None:
    """Synthetic negative: a non-CommandSpec tuple literal is NOT flagged."""
    src = "FOO_LIST = (Foo(), Bar(),)\n"
    tree = ast.parse(src)
    assert _file_has_command_spec_tuple_literal(tree) is False


def test_walker_does_not_flag_command_spec_in_other_context() -> None:
    """A function-call to ``CommandSpec(...)`` outside a tuple literal is NOT flagged.

    The registry's ``register(spec)`` calls take ``CommandSpec(...)`` as
    arguments — those must not be flagged.
    """
    src = (
        "def register(registry):\n"
        "    registry.register(CommandSpec(handler_class=H, **kwargs))\n"
    )
    tree = ast.parse(src)
    assert _file_has_command_spec_tuple_literal(tree) is False
