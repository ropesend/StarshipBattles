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
# Category C — live session READERS deferred to PROJ-475 (allowlisted-with-reason).
#
# PROJ-472 Phase 1C (2026-05-21) MIGRATED and REMOVED the former Category D
# TEMPORARY entries: strategy_detail_formatter (registries / turn_engine →
# scene.registries + facade.validation.can_colonize), list_windows
# (empires/registries → scene pass-throughs), hex_outlines (active_empire/turn →
# scene.active_empire_id / scene.turn_number), strategy_render/fleets
# (path projection → facade.fleets.path_projection), and
# strategy_build_queue_manager (facade_state.session.services /
# facade_state.session._get_fleet_by_id → facade_state.get_design_catalog_for_empire /
# get_fleet_by_id). The guard now ENFORCES the boundary for those files.
# The remaining allowlist is honestly NOT the full read path: pass-throughs +
# the explicitly-deferred PROJ-475 readers + mutator write seams persist.
_SESSION_READ_ALLOWLIST: frozenset[tuple[str, str]] = frozenset({
    # --- Category A: StrategyScreen composition-root self-reads (transitional) ---
    # ``galaxy``/``empires``/``systems`` are the broad raw-domain pass-through
    # properties, DEFERRED to PROJ-477 (render/read-model boundary).
    ("game/ui/screens/strategy_screen.py", "_session.galaxy"),
    ("game/ui/screens/strategy_screen.py", "_session.empires"),
    ("game/ui/screens/strategy_screen.py", "_session.systems"),
    # PROJ-475 Phase 3 RETIRED the public ``enemy_empire``/``human_player_ids``/
    # ``active_empire`` READ pass-throughs (consumers migrated to the facade).
    # ``_session.active_empire`` STAYS allowlisted: it now backs the screen's
    # own ``active_empire_id``/``current_empire`` helpers (the screen IS the
    # composition-root boundary and owns the only legitimate ``_session``).
    ("game/ui/screens/strategy_screen.py", "_session.active_empire"),
    # ``current_empire`` (the screen's own viewing-empire helper) reads
    # ``_session.human_player_ids`` directly — a Category-A composition-root
    # self-read, distinct from the retired public ``human_player_ids``
    # pass-through whose external consumers moved to the facade in Phase 3.
    ("game/ui/screens/strategy_screen.py", "_session.human_player_ids"),
    # The ``session`` property body returns the private handle wholesale;
    # this IS the documented composition-root pass-through. Its GETTER
    # retirement is DEFERRED to PROJ-477 (live consumers: system_tree_panel
    # dynamic resolve + Category B mutator write seams). The setter stays.
    ("game/ui/screens/strategy_screen.py", "_session.__extract__"),
    # --- Category B: mutator / state-manager write seams (PROJ-475) ---
    ("game/ui/screens/strategy_game_state_manager.py", "session.active_empire"),
    ("game/ui/screens/strategy_screen_order_editing.py", "session.fleet_mutator"),
    # --- Category C: live session readers deferred to PROJ-475 ---
    # PROJ-475 Phase 2 MIGRATED + REMOVED the former Category C readers:
    #   strategy_event_router (session.get_empire → facade.empires.race_config),
    #   strategy_screen_selection / strategy_screen_order_editing
    #     (session.active_empire READ → screen.active_empire_id),
    #   empire_panel_ctrl (session.registries → scene.registries).
    # The guard now ENFORCES the boundary for those reads. The
    # order_editing mutator WRITE seam (session.fleet_mutator, Category B
    # above) STAYS — out of PROJ-475 scope.
    # --- Category E: bare-session ESCAPE seams surfaced by the PROJ-472 1D
    #     hardened matcher (Codex finding 2). The live session object is
    #     handed wholesale to a save service or aliased into a local. All are
    #     pre-existing deferred-tail reads (NOT migrated by PROJ-472); they
    #     stay allowlisted-with-reason and are recorded as deferred to
    #     PROJ-475 (save seams) / PROJ-476 (transfer tooling tail). ---
    # PROJ-475 Phase 2 Task 2.4 MIGRATED + REMOVED the save-seam Category E
    # entries: strategy_game_state_manager (auto-save) and
    # strategy_screen_lifecycle (manual save + on_design_click workshop ctx)
    # now route through facade.session_meta.save_current_game() / a scalar
    # save_path handoff. Task 2.5 MIGRATED + REMOVED the transfer_controller
    # entry (discover_pod_designs now uses
    # facade.facade_state.get_design_catalog_for_empire(viewing_empire_id)).
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


def _parent_map(tree: ast.AST) -> dict[int, ast.AST]:
    """Map ``id(child_node) -> parent_node`` for every AST node.

    Used so :func:`_matched_session_read` can tell whether a ``.session``
    extraction is consumed by an immediate attribute read (a chained
    ``.session.<attr>`` read) or is bare/aliased (assigned to a local,
    passed as an argument, returned, …). The bare form is the bypass the
    direct-chain matcher used to miss (Codex finding 2).
    """
    parents: dict[int, ast.AST] = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[id(child)] = parent
    return parents


def _matched_session_read(
    node: ast.Attribute, parents: dict[int, ast.AST] | None = None
) -> str | None:
    """Return the matched attribute-path tail if ``node`` is a guarded session
    read, else None.

    Forms recognised:
      * ``<expr>.session.<attr>``       -> "session.<attr>"   (node is the OUTER attr)
      * ``<expr>._session.<attr>``      -> "_session.<attr>"  (node is the OUTER attr)
      * ``<expr>.facade_state.session`` -> "facade_state.session" (node IS the
        ``.session`` access that extracts the live session out of
        ``FacadeSessionState``; the subsequent read happens off the resulting
        local, so we anchor on the extraction itself).
      * bare/aliased ``<expr>.session`` / ``<expr>._session`` extraction
        -> "session.__extract__" / "_session.__extract__" (PROJ-472 1D,
        Codex finding 2). When the ``.session`` extraction is NOT immediately
        consumed by an attribute read (i.e. it is assigned to a local, passed
        as an argument, or returned), the live session object escapes wholesale
        — a strictly worse leak than a single scalar read — and must be
        flagged. ``parents`` lets us distinguish this from the chained form so
        a chained read is reported once, per-attribute (not double-counted).

    ``parents`` is the :func:`_parent_map` for the tree. When omitted (the
    synthetic positive-control probes that test a single expression in
    isolation), an extraction with no parent attribute access is treated as
    bare.
    """
    # Forms 1 & 2: <expr>.session.<attr> / <expr>._session.<attr>
    # (anchored on the OUTER attribute; reported per-attribute).
    inner = node.value
    if isinstance(inner, ast.Attribute) and inner.attr in _SESSION_ATTR_NAMES:
        return f"{inner.attr}.{node.attr}"

    # ``node`` is itself a ``.session`` / ``._session`` extraction.
    if node.attr in _SESSION_ATTR_NAMES or node.attr == "session":
        # Form 3: extracting the session out of facade_state.
        parent_attr = node.value
        if (
            node.attr == "session"
            and isinstance(parent_attr, ast.Attribute)
            and parent_attr.attr == "facade_state"
        ):
            return "facade_state.session"

        if node.attr not in _SESSION_ATTR_NAMES:
            return None

        # Bare/aliased extraction: flag UNLESS this extraction is the
        # ``.value`` of an outer attribute access (the chained
        # ``.session.<attr>`` form, already reported by Forms 1 & 2 above on
        # the OUTER node).
        if parents is not None:
            consumer = parents.get(id(node))
            if isinstance(consumer, ast.Attribute) and consumer.value is node:
                return None
        return f"{node.attr}.__extract__"

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
    parents = _parent_map(tree)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute):
            continue
        if node.lineno in tc_lines:
            continue
        attr_path = _matched_session_read(node, parents)
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


def _violations_in_source(rel: str, src: str) -> list[tuple[int, str]]:
    """Helper mirroring the directory-scan body for synthetic-source probes."""
    tree = ast.parse(src, filename="synthetic.py")
    tc_lines = _type_checking_linenos(tree)
    parents = _parent_map(tree)
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute):
            continue
        if node.lineno in tc_lines:
            continue
        attr_path = _matched_session_read(node, parents)
        if attr_path is None:
            continue
        out.append((node.lineno, attr_path))
    return out


def test_session_guard_catches_aliased_extraction() -> None:
    """PROJ-472 1D (Codex finding 2): a net-new bypass that aliases the
    session out (``sess = obj.session``) and reads off the alias, or passes
    the bare session object as an argument, must be flagged.

    Before 1D the matcher only anchored on the direct ``obj.session.<attr>``
    chain, so ``sess = screen.session; sess.active_empire`` and
    ``save_game(screen.session)`` slipped through unflagged — the live
    counterexamples Codex found (``transfer_controller.py``,
    ``strategy_game_state_manager.py``). The guard now flags the bare
    ``.session`` / ``._session`` extraction itself.
    """
    aliased = _violations_in_source(
        "synthetic.py", "sess = screen.session\nv = sess.active_empire\n"
    )
    assert any(p == "session.__extract__" for _, p in aliased), (
        "Aliasing the session out must be flagged at the extraction site."
    )

    bare_arg = _violations_in_source(
        "synthetic.py", "save_game(screen.session)\n"
    )
    assert any(p == "session.__extract__" for _, p in bare_arg), (
        "Passing the bare session object as an argument must be flagged."
    )

    private = _violations_in_source(
        "synthetic.py", "s = self._session\nv = s.galaxy\n"
    )
    assert any(p == "_session.__extract__" for _, p in private), (
        "Aliasing the private `_session` out must be flagged too."
    )


def test_session_guard_chained_read_reports_per_attribute_not_extract() -> None:
    """A direct chained read still reports the per-attribute key
    (``session.<attr>``), NOT the coarse ``__extract__`` key — so existing
    per-attribute allowlist granularity is preserved and a chained read does
    not double-count.
    """
    hits = _violations_in_source(
        "synthetic.py", "v = screen.session.registries\n"
    )
    assert ("session.registries") in {p for _, p in hits}
    assert "session.__extract__" not in {p for _, p in hits}, (
        "A chained `.session.<attr>` read must be reported once, per-attribute."
    )


def test_facade_state_session_attribute_is_privatized() -> None:
    """PROJ-475 Phase 4: ``FacadeSessionState.session`` is privatized to
    ``_session`` so the live session is NOT publicly reachable via
    ``facade.facade_state.session`` from UI code.

    The AST scan above catches the syntactic ``<expr>.facade_state.session``
    chain, but a string-based ``getattr(facade_state, "session", ...)`` would
    slip past it (this is exactly the live counterexample PROJ-475 Phase 4
    found in ``workshop_ship_io.py`` and migrated to
    ``get_design_catalog_for_empire``). This runtime pin makes the closure
    explicit: the public ``session`` attribute must be gone while the
    engine-internal ``_session`` still holds the live session.
    """
    from unittest.mock import MagicMock

    from game.strategy.facade.slices._facade_state import FacadeSessionState

    session = MagicMock()
    state = FacadeSessionState(session)
    assert not hasattr(state, "session"), (
        "PROJ-475 Phase 4: FacadeSessionState.session must be privatized to "
        "_session; the live session must not be publicly reachable via "
        "facade.facade_state.session (incl. getattr-by-name)."
    )
    assert state._session is session, (
        "The engine-internal _session must still hold the live session so the "
        "facade's own slices keep functioning."
    )


def test_facade_state_session_form_no_longer_present_in_build_queue_manager() -> None:
    """PROJ-472 1C migrated ``strategy_build_queue_manager.py`` off the
    ``facade_state.session`` bypass.

    Replaces the former negative-control pin (which asserted the bypass was
    *present* and allowlisted). The migration routed both the design-catalog
    read and the live-fleet lookup through facade-state accessors
    (``get_design_catalog_for_empire`` / ``get_fleet_by_id``), so the
    ``facade_state.session`` extraction must NOT reappear here. The matcher's
    third-form coverage is still pinned synthetically by
    ``test_session_read_matcher_recognises_all_three_forms``.
    """
    target = UI_DIR / "screens" / "strategy_build_queue_manager.py"
    tree = ast.parse(target.read_text(encoding="utf-8"), filename=str(target))
    found = any(
        isinstance(node, ast.Attribute)
        and _matched_session_read(node) == "facade_state.session"
        for node in ast.walk(tree)
    )
    assert not found, (
        "PROJ-472 1C migrated strategy_build_queue_manager.py off "
        "`facade_state.session`; the bypass must not reappear. Route new "
        "session reads through a facade-state accessor."
    )
