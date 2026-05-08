"""PROJ-382 Phase 1 Task 1.5 — AST static-guard against facade bypass.

Pattern #5 (Facade / Delegate) requires UI code to dispatch commands through
the strategy session facade, never directly through ``GameSession``.  After
PROJ-382 Phase 1 eliminated the dual-path dispatch sites in
``build_queue_screen.py`` and ``empire_build_queue_window.py``, this guard
prevents the bypass from silently re-growing.

Two violation classes are caught:

1. **Direct dispatch:** any ``<expr>.session.handle_command(<args>)`` call
   inside ``game/ui/``.  UI code may only call
   ``<expr>.facade.handle_command(...)``.

2. **Constructor leakage:** any keyword argument named ``session`` passed to
   ``BuildQueueScreen(...)`` or ``EmpireBuildQueueWindow(...)`` from anywhere
   outside the legitimate composition root in
   ``game/ui/screens/strategy_screen.py``.  These two screens take the facade
   only — passing the session keeps the bypass alive.

Reference: ``tests/unit/strategy/services/test_ability_sources_no_global_registry_access.py``
(PROJ-300/306 AST guard for ``get_default_registry_provider``) is the
canonical static-guard template.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
UI_DIR = REPO_ROOT / "game" / "ui"

# Constructors that must never receive a ``session=`` kwarg from outside the
# strategy_screen composition root.
GUARDED_CONSTRUCTORS = {"BuildQueueScreen", "EmpireBuildQueueWindow"}

# The composition root is allowed to retain session-aware DI as it is the
# legitimate place a UI screen is born.  Phase 1 still removed session=
# from those particular construction calls, but if the composition layer
# legitimately needs to pass session for a *different* screen later, it is
# expected to live here.  The guard exempts this single file.
COMPOSITION_ROOT_FILES: set[str] = set()


def _ui_python_files() -> list[Path]:
    """Every .py under game/ui/ except __pycache__."""
    files: list[Path] = []
    for path in UI_DIR.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        files.append(path)
    return sorted(files)


def _is_session_handle_command(node: ast.Call) -> bool:
    """Match ``<expr>.session.handle_command(...)`` calls."""
    func = node.func
    if not isinstance(func, ast.Attribute):
        return False
    if func.attr != "handle_command":
        return False
    inner = func.value
    if not isinstance(inner, ast.Attribute):
        return False
    return inner.attr == "session"


def _has_session_kwarg(node: ast.Call) -> bool:
    """Match a Call that passes ``session=...`` as keyword."""
    for kw in node.keywords:
        if kw.arg == "session":
            return True
    return False


def _called_constructor_name(node: ast.Call) -> str | None:
    """Return the simple constructor name being called, or None.

    Handles both ``BuildQueueScreen(...)`` and
    ``module.BuildQueueScreen(...)`` shapes.
    """
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


@pytest.mark.parametrize(
    "path",
    _ui_python_files(),
    ids=lambda p: str(p.relative_to(REPO_ROOT)).replace("\\", "/"),
)
def test_no_session_handle_command_in_ui(path: Path) -> None:
    """No ``<expr>.session.handle_command(...)`` calls anywhere in game/ui/.

    UI code dispatches commands via the StrategySessionFacade only.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _is_session_handle_command(node):
            rel = path.relative_to(REPO_ROOT)
            pytest.fail(
                f"PROJ-382 Pattern #5 violation: {rel}:{node.lineno} calls "
                f"`<expr>.session.handle_command(...)`. UI code must "
                f"dispatch commands through the facade: "
                f"`<expr>.facade.handle_command(...)`."
            )


@pytest.mark.parametrize(
    "path",
    _ui_python_files(),
    ids=lambda p: str(p.relative_to(REPO_ROOT)).replace("\\", "/"),
)
def test_no_session_kwarg_to_facade_only_constructors(path: Path) -> None:
    """``BuildQueueScreen`` / ``EmpireBuildQueueWindow`` take only ``facade=``.

    Passing ``session=`` to either constructor reintroduces the bypass
    surface that Phase 1 removed.
    """
    rel_str = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    if rel_str in COMPOSITION_ROOT_FILES:
        return

    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        ctor = _called_constructor_name(node)
        if ctor not in GUARDED_CONSTRUCTORS:
            continue
        if _has_session_kwarg(node):
            pytest.fail(
                f"PROJ-382 Pattern #5 violation: {rel_str}:{node.lineno} "
                f"constructs `{ctor}(... session=...)`. These screens take "
                f"only `facade=`. Pass facade and drop session."
            )


def test_ui_directory_has_python_files() -> None:
    """Sanity: parametrize would silently produce zero tests if not."""
    files = _ui_python_files()
    assert files, f"No .py files found in {UI_DIR}"
    names = {f.name for f in files}
    assert "build_queue_screen.py" in names
    assert "empire_build_queue_window.py" in names
    assert "strategy_screen.py" in names
