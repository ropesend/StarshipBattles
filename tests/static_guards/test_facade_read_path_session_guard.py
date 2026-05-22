"""PROJ-472 Phase 1A — AST static-guard against facade READ-path session reads.

Companion to the write-path guard
(``tests/static_guards/test_facade_bypass_guard.py``) and the read-path
*import* guard
(``tests/static_guards/test_facade_read_path_imports_guard.py``).

Pattern #5's read-path policy (option b, ``docs/02_PATTERNS.md``) requires UI
code to read session-owned state through the ``StrategySessionFacade`` rather
than reaching into the live ``GameSession`` via ``.session`` chains. This guard
catches the three syntactic forms of that bypass anywhere under ``game/ui/``:

1. ``<expr>.session.<attr>``         (e.g. ``c.scene.session.empires``)
2. ``<expr>._session.<attr>``        (the PROJ-382-privatized form)
3. ``<expr>.facade_state.session.<attr>``
   (e.g. ``self._screen.facade.facade_state.session.services`` —
   ``strategy_build_queue_manager.py``). Without this third form the guard
   misses live bypasses that route through ``FacadeSessionState.session``.

Every read currently present in ``game/ui`` is on the allowlist below, keyed by
**file + attribute-path + reason** (NOT by bare attribute name). The guard's
value is preventing *new*, non-allowlisted session reads; existing ones are
documented transitional surfaces (StrategyScreen composition-root pass-throughs,
mutator write seams) or are scheduled for migration in PROJ-472 Phase 1C / 475
and are removed from the allowlist as those land.

A positive-control test pins the matcher so a future refactor cannot silently
narrow it (mirrors ``test_facade_bypass_guard.py`` positive controls).
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
UI_DIR = REPO_ROOT / "game" / "ui"

# Inner-attribute names that, when the *next* attribute is read off them, count
# as a session read: ``<expr>.session.<attr>`` / ``<expr>._session.<attr>``.
_SESSION_ATTR_NAMES: frozenset[str] = frozenset({"session", "_session"})

# Allowlist of (relative_posix_path, attribute_path) pairs that are permitted
# session reads. ``attribute_path`` is the matched chain tail, e.g.
# ``_session.galaxy`` or ``facade_state.session.services``. Each entry is a
# documented transitional surface or a PROJ-472 1C / PROJ-475 migration target.
#
# Category A — StrategyScreen composition-root pass-through properties
#   (transitional; deprecation is PROJ-475). The screen owns the only legitimate
#   ``_session`` handle; these property bodies expose narrow reads to children.
# Category B — mutator / state-manager WRITE seams (deferred to PROJ-475).
# Category C — live session readers deferred to PROJ-475 (allowlisted-with-reason).
# Category D — PROJ-472 Phase 1C migration targets (TEMPORARY; removed as 1C lands).
_SESSION_READ_ALLOWLIST: frozenset[tuple[str, str]] = frozenset({
    # --- Category A: StrategyScreen pass-through properties (transitional) ---
    ("game/ui/screens/strategy_screen.py", "_session.galaxy"),
    ("game/ui/screens/strategy_screen.py", "_session.empires"),
    ("game/ui/screens/strategy_screen.py", "_session.systems"),
    ("game/ui/screens/strategy_screen.py", "_session.active_empire"),
    ("game/ui/screens/strategy_screen.py", "_session.enemy_empire"),
    ("game/ui/screens/strategy_screen.py", "_session.human_player_ids"),
    # --- Category B: mutator / state-manager write seams (PROJ-475) ---
    ("game/ui/screens/strategy_game_state_manager.py", "session.active_empire"),
    ("game/ui/screens/strategy_screen_order_editing.py", "session.fleet_mutator"),
    # --- Category C: live session readers deferred to PROJ-475 ---
    ("game/ui/screens/strategy_event_router.py", "session.get_empire"),
    ("game/ui/screens/strategy_screen_order_editing.py", "session.active_empire"),
    ("game/ui/screens/strategy_screen_selection.py", "session.active_empire"),
    ("game/ui/screens/strategy_windows/empire_panel_ctrl.py", "session.registries"),
    # --- Category D: PROJ-472 Phase 1C migration targets (TEMPORARY) ---
    ("game/ui/screens/strategy_detail_formatter.py", "session.registries"),  # PROJ-472 1C will migrate
    ("game/ui/screens/strategy_detail_formatter.py", "session.turn_engine"),  # PROJ-472 1C will migrate
    ("game/ui/screens/strategy_windows/list_windows.py", "session.empires"),  # PROJ-472 1C will migrate
    ("game/ui/screens/strategy_windows/list_windows.py", "session.registries"),  # PROJ-472 1C will migrate
    ("game/ui/screens/strategy_render/hex_outlines.py", "session.active_empire"),  # PROJ-472 1C will migrate
    ("game/ui/screens/strategy_render/fleets.py", "session.get_fleet_path_projection"),  # PROJ-472 1C will migrate
    ("game/ui/screens/strategy_build_queue_manager.py", "facade_state.session"),  # PROJ-472 1C will migrate
})


def _ui_python_files() -> list[Path]:
    """Every .py under game/ui/ except __pycache__."""
    files: list[Path] = []
    for path in UI_DIR.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        files.append(path)
    return sorted(files)


def _type_checking_linenos(tree: ast.AST) -> set[int]:
    """Line numbers of statements inside any ``if TYPE_CHECKING:`` block.

    Session reads are runtime constructs (not type annotations), so this is
    mostly defensive symmetry with the import guard, but it keeps the two
    guards consistent if a ``TYPE_CHECKING`` block ever contains an example
    expression.
    """
    out: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        name = test.id if isinstance(test, ast.Name) else (
            test.attr if isinstance(test, ast.Attribute) else None
        )
        if name != "TYPE_CHECKING":
            continue
        for child in node.body:
            for sub in ast.walk(child):
                lineno = getattr(sub, "lineno", None)
                if lineno is not None:
                    out.add(lineno)
    return out


def _matched_session_read(node: ast.Attribute) -> str | None:
    """Return the matched attribute-path tail if ``node`` is a guarded session
    read, else None.

    Forms recognised:
      * ``<expr>.session.<attr>``       -> "session.<attr>"   (node is the OUTER attr)
      * ``<expr>._session.<attr>``      -> "_session.<attr>"  (node is the OUTER attr)
      * ``<expr>.facade_state.session`` -> "facade_state.session" (node IS the
        ``.session`` access that extracts the live session out of
        ``FacadeSessionState`` — e.g. ``...facade.facade_state.session`` in
        ``strategy_build_queue_manager.py``; the subsequent ``.services`` read
        happens off the resulting local, so we anchor on the extraction itself).
    """
    # Form 3: extracting the session out of facade_state.
    # ``node`` itself is the ``.session`` attribute whose value is ``facade_state``.
    if node.attr == "session":
        parent = node.value
        if isinstance(parent, ast.Attribute) and parent.attr == "facade_state":
            return "facade_state.session"
    inner = node.value
    if not isinstance(inner, ast.Attribute):
        return None
    # Forms 1 & 2: <expr>.session.<attr> / <expr>._session.<attr>
    if inner.attr in _SESSION_ATTR_NAMES:
        return f"{inner.attr}.{node.attr}"
    return None


@pytest.mark.parametrize(
    "path",
    _ui_python_files(),
    ids=lambda p: str(p.relative_to(REPO_ROOT)).replace("\\", "/"),
)
def test_no_unallowlisted_session_reads_in_ui(path: Path) -> None:
    """No non-allowlisted ``.session`` / ``._session`` / ``.facade_state.session``
    reads anywhere in ``game/ui/``.

    UI code reads session-owned state through the facade. Existing reads are
    allowlisted-with-reason in ``_SESSION_READ_ALLOWLIST`` (transitional
    pass-throughs, write seams, or PROJ-472 1C / PROJ-475 migration targets).
    A net-new read fails here until it is migrated or explicitly allowlisted.
    """
    rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    tc_lines = _type_checking_linenos(tree)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute):
            continue
        if node.lineno in tc_lines:
            continue
        attr_path = _matched_session_read(node)
        if attr_path is None:
            continue
        if (rel, attr_path) in _SESSION_READ_ALLOWLIST:
            continue
        pytest.fail(
            f"PROJ-472 Pattern #5 read-path violation: {rel}:{node.lineno} "
            f"reads `...{attr_path}` directly off the session. UI code must "
            f"read session-owned state through the StrategySessionFacade. If "
            f"this is an intentional transitional surface, add "
            f"`('{rel}', '{attr_path}')` to _SESSION_READ_ALLOWLIST with a "
            f"reason comment."
        )


def test_ui_directory_has_python_files() -> None:
    """Sanity: parametrize would silently produce zero tests if not."""
    files = _ui_python_files()
    assert files, f"No .py files found in {UI_DIR}"
    names = {f.name for f in files}
    assert "strategy_screen.py" in names
    assert "strategy_build_queue_manager.py" in names


def test_session_read_matcher_recognises_all_three_forms() -> None:
    """Positive-control: ``_matched_session_read`` recognises the public,
    private, and ``facade_state.session`` forms, and rejects facade reads.

    Without this, a future refactor could narrow the matcher (e.g. drop the
    ``facade_state.session`` chain or the ``_session`` form) and the
    directory scan would still pass, silently reopening the bypass.
    """
    public = ast.parse("c.scene.session.empires").body[0].value
    private = ast.parse("self._session.registries").body[0].value
    facade_state = ast.parse(
        "self.facade.facade_state.session"
    ).body[0].value
    facade_ok = ast.parse("self.facade.empires.all()").body[0].value.func
    handle_cmd = ast.parse("self.facade.handle_command(cmd)").body[0].value.func

    assert isinstance(public, ast.Attribute)
    assert isinstance(private, ast.Attribute)
    assert isinstance(facade_state, ast.Attribute)
    assert isinstance(facade_ok, ast.Attribute)
    assert isinstance(handle_cmd, ast.Attribute)

    assert _matched_session_read(public) == "session.empires", (
        "Guard must match the public `.session.<attr>` form."
    )
    assert _matched_session_read(private) == "_session.registries", (
        "Guard must match the private `._session.<attr>` form (PROJ-382)."
    )
    assert _matched_session_read(facade_state) == "facade_state.session", (
        "Guard must match the `.facade_state.session` extraction — "
        "otherwise it misses FacadeSessionState bypasses."
    )
    assert _matched_session_read(facade_ok) is None, (
        "Guard must NOT match facade namespace reads like `facade.empires`."
    )
    assert _matched_session_read(handle_cmd) is None, (
        "Guard must NOT match `facade.handle_command` (the write path)."
    )


def test_facade_state_session_form_is_actually_present_in_ui() -> None:
    """Negative-control safety: confirm the ``facade_state.session`` form the
    guard's third clause targets is a real, currently-allowlisted bypass.

    Pins the allowlist entry for ``strategy_build_queue_manager.py`` to the
    live code so removing it during 1C forces a deliberate allowlist edit.
    """
    target = UI_DIR / "screens" / "strategy_build_queue_manager.py"
    tree = ast.parse(target.read_text(encoding="utf-8"), filename=str(target))
    found = any(
        isinstance(node, ast.Attribute)
        and _matched_session_read(node) == "facade_state.session"
        for node in ast.walk(tree)
    )
    assert found, (
        "Expected the `facade_state.session` extraction in "
        "strategy_build_queue_manager.py. If 1C migrated it, remove this pin "
        "and the matching _SESSION_READ_ALLOWLIST entry."
    )
