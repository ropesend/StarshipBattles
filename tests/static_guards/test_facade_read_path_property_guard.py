"""PROJ-477 Phase 1 — AST static-guard against facade READ-path PROPERTY reads.

Third companion to the write-path guard
(``tests/static_guards/test_facade_bypass_guard.py``), the read-path *session*
guard (``tests/static_guards/test_facade_read_path_session_guard.py``), and the
read-path *import* guard
(``tests/static_guards/test_facade_read_path_imports_guard.py``).

The two earlier read-path guards measure two syntactic surfaces under
``game/ui/``: the ``.session``/``._session``/``.facade_state.session`` chain and
runtime ``game.strategy.*`` imports. NEITHER measures the broad
``StrategyScreen`` pass-through *properties* ``scene.galaxy`` / ``scene.empires``
/ ``scene.systems`` (and their renderer re-exporters ``r.galaxy``/etc.), because
those reads go through a property, not a ``.session`` chain. So those three
remain an unmeasured raw-domain bus. PROJ-477 closes them; this guard measures
the property surface so net-new bypasses cannot grow during the migration, and
is ratcheted down to its end-state in Phase 6.

**Matched shapes (Load-context property reads only, on the SCOPED shapes that
reach the pass-through seam — design.md "Third static guard design"):**

1. ``<expr>.scene.{galaxy,empires,systems}``   (e.g. ``c.scene.galaxy``)
2. ``<expr>._screen.{galaxy,empires,systems}`` (e.g. ``self._screen.galaxy``)
3. ``r.{galaxy,empires,systems}``              (renderer re-exporter reads)
4. ``screen.{galaxy,empires,systems}``         (ONLY in ``strategy_screen_*`` /
   ``planet_list_helpers`` helper modules that take a ``screen`` handle)
5. ``self.galaxy`` ONLY in ``strategy_screen.py`` (the screen's own pathfinder
   helpers ``:529-537`` — legitimate composition-root self-reads)

**Explicitly NOT matched:** generic ``self.galaxy`` / ``self.empires`` /
``self.systems`` (false-positives on the constructor-injected LOCAL attrs in
``build_queue_screen.py``, ``build_queue_controller.py``, ``planet_list_window.py``,
``star_list_window.py``, ``planet_list_filters.py`` — these store a raw galaxy
local and read it as ``self.galaxy``; the SOURCE read ``c.scene.galaxy`` is what
migrates). ``ast.Store`` context is excluded so a store ``x.galaxy = scene.galaxy``
flags only the RHS read.

Every read currently present in ``game/ui`` is on the allowlist below, keyed by
**file + attribute-path + reason**. The guard's value is preventing *new*,
non-allowlisted property reads; existing ones are PROJ-477 migration targets and
are removed from the allowlist as those land (ratcheted to the end-state in
Phase 6).

A positive-control test pins the matcher so a future refactor cannot silently
narrow it (mirrors the session-guard positive controls).
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
UI_DIR = REPO_ROOT / "game" / "ui"

# The three broad raw-domain pass-through property names.
_PASSTHROUGH_NAMES: frozenset[str] = frozenset({"galaxy", "empires", "systems"})

# Receiver names that, when one of the three pass-through attributes is read off
# them, count as a guarded property read: ``<expr>.scene.galaxy`` (receiver
# attr ``scene``), ``<expr>._screen.galaxy`` (``_screen``), ``r.galaxy``
# (Name ``r``), ``screen.galaxy`` (Name ``screen``).
_SCENE_RECEIVER_ATTRS: frozenset[str] = frozenset({"scene", "_screen"})
_BARE_RECEIVER_NAMES: frozenset[str] = frozenset({"r", "screen"})

# Helper modules that legitimately take a ``screen`` handle and read
# ``screen.galaxy/empires/systems`` off it (vs. an unrelated local named
# ``screen``). Restricting the ``screen.X`` form to these modules avoids
# false-positives elsewhere.
_SCREEN_HANDLE_MODULES: frozenset[str] = frozenset({
    "strategy_screen_assets.py",
    "strategy_screen_selection.py",
    "planet_list_helpers.py",
})

# Allowlist of (relative_posix_path, attribute_path) pairs that are permitted
# property reads. ``attribute_path`` is the matched chain tail, e.g.
# ``scene.galaxy`` / ``_screen.galaxy`` / ``r.empires`` / ``screen.systems`` /
# ``self.galaxy``. Each entry is a PROJ-477 migration target (Phase noted), so
# the directory scan is GREEN at introduction and shrinks as migrations land.
_PROPERTY_READ_ALLOWLIST: frozenset[tuple[str, str]] = frozenset({
    # END-STATE (PROJ-477 Phase 6): the allowlist is EMPTY. The facade
    # read-path boundary is closed — no UI module reads the broad
    # ``scene.galaxy`` / ``scene.empires`` / ``scene.systems`` pass-through bus
    # (deleted), the renderer re-exporters (deleted), or any matched
    # ``r.*`` / ``_screen.*`` / ``screen.*`` / ``self.galaxy`` form.
    #
    # Render-hot + raw-window consumers read live galaxy/empires/systems through
    # the scene-owned ``StrategyWorldAccess`` (``scene.world`` / ``r.world``)
    # seam; cold callers use the facade queries. ``StrategyWorldAccess`` itself
    # and the screen's pathfinder helpers read the composition-root
    # ``_session`` (caught/allowlisted by the SESSION guard, not this one — the
    # receiver is ``_session``/a provider Call, not a guarded property shape).
    #
    # The historical migration log (Phases 4-6) is preserved below for context.

    # PROJ-477 Phase 6 Task 6.2 DELETED the three StrategyScreen pass-throughs
    # (``galaxy``/``empires``/``systems``); the screen's pathfinder helpers +
    # ``current_empire`` now read ``self._session`` directly (composition root).

    # PROJ-477 Phase 6 Task 6.1 DELETED the renderer re-exporter property
    # bodies (``strategy_renderer.py`` ``scene.galaxy``/``scene.systems``/
    # ``scene.empires``) — render modules read through ``r.world`` now.

    # --- Render-hot stack (Phase 5.3) ---
    # PROJ-477 Phase 5 Task 5.3 MIGRATED all strategy_render/* modules off the
    # ``r.galaxy``/``r.empires`` re-exporters onto ``r.world.iter_systems()`` /
    # ``iter_empires()`` / ``global_hex_*`` / ``system_by_name`` (live, no
    # per-frame DTOs). The renderer re-exporter property BODIES
    # (``strategy_renderer.py`` ``scene.galaxy``/etc., above) are now unused by
    # render code and are DELETED in Phase 6.

    # --- COLD: object->system / spatial / scan consumers (Phase 4) ---
    # PROJ-477 Phase 4 Task 4.1 MIGRATED: strategy_camera_nav (scene.systems →
    # scene.world.iter_systems/system_for_object), strategy_event_router
    # (scene.galaxy → scene.world.system_for_object).
    # PROJ-477 Phase 4 Task 4.2 MIGRATED: strategy_colonization +
    # strategy_superweapons (scene.systems/galaxy → scene.world.iter_systems /
    # system_at_map_hex / planets_at_exact_hex / zones_at_hex),
    # strategy_click_dispatcher (scene.empires → iter_empires; scene.galaxy
    # zone read → scene.world.zones_at_hex).
    # PROJ-477 Phase 4 Task 4.6 MIGRATED: strategy_fleet_ops (deleted the unused
    # ``empires`` wrapper property entirely).

    # --- COLD: list windows + build-queue chain (Phase 4) ---
    # PROJ-477 Phase 4 Task 4.3 MIGRATED: strategy_ui menu builders
    # (scene.galaxy → scene.world; fleet/planet_menu_items take a world handle).
    # PROJ-477 Phase 4 Task 4.4 MIGRATED: list_windows (scene.galaxy/empires →
    # scene.world; planet/star windows + their filters take a world handle).
    # PROJ-477 Phase 4 Task 4.5 MIGRATED: build_queue_windows (scene.galaxy →
    # scene.world) + strategy_build_queue_manager (_screen.galaxy → _screen.world;
    # build_queue_screen / build_queue_controller take a world handle and read
    # world.planets_at_exact_hex / planet_by_id / system_for_object).

    # --- COLD: assets / selection / state-manager (Phase 4) — ``screen.X`` ---
    # PROJ-477 Phase 4 Task 4.6 MIGRATED: strategy_screen_assets
    # (screen.empires/systems → scene.world.iter_empires/iter_systems),
    # strategy_screen_selection (screen.systems → scene.world.system_for_object
    # / iter_systems), strategy_game_state_manager (_screen.empires →
    # _screen.world.iter_empires).
    # PROJ-477 Phase 4 Task 4.4 MIGRATED: planet_list_helpers
    # (screen.galaxy → screen.world for the PlanetDataSource context handle).
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
    """Line numbers of statements inside any ``if TYPE_CHECKING:`` block."""
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


def _matched_property_read(node: ast.Attribute, module_name: str) -> str | None:
    """Return the matched attribute-path tail if ``node`` is a guarded
    pass-through property read, else None.

    Only ``ast.Load`` context reads are matched (a store ``x.galaxy = ...``
    has ``node.ctx`` of ``ast.Store`` and is skipped) and ``node.attr`` must be
    one of ``galaxy``/``empires``/``systems``.

    Forms recognised (``node`` is the OUTER attribute carrying the
    pass-through name):
      * ``<expr>.scene.{name}``   -> "scene.{name}"
      * ``<expr>._screen.{name}`` -> "_screen.{name}"
      * ``r.{name}``              -> "r.{name}"
      * ``screen.{name}``         -> "screen.{name}"  (only in helper modules)
      * ``self.galaxy``           -> "self.galaxy"     (ONLY in strategy_screen.py)

    Generic ``self.galaxy``/``self.empires``/``self.systems`` elsewhere is NOT
    matched (injected-local false-positives — design.md).
    """
    if node.attr not in _PASSTHROUGH_NAMES:
        return None
    if not isinstance(node.ctx, ast.Load):
        return None

    receiver = node.value

    # Forms 1 & 2: ``<expr>.scene.{name}`` / ``<expr>._screen.{name}`` — the
    # receiver is itself an attribute access whose final attr is scene/_screen.
    if isinstance(receiver, ast.Attribute) and receiver.attr in _SCENE_RECEIVER_ATTRS:
        return f"{receiver.attr}.{node.attr}"

    # Forms 3 & 4: bare-name receiver ``r.{name}`` / ``screen.{name}``.
    if isinstance(receiver, ast.Name):
        if receiver.id == "r":
            return f"r.{node.attr}"
        if receiver.id == "screen" and module_name in _SCREEN_HANDLE_MODULES:
            return f"screen.{node.attr}"
        # Form 5: ``self.galaxy`` ONLY in strategy_screen.py (pathfinder helpers).
        if (
            receiver.id == "self"
            and node.attr == "galaxy"
            and module_name == "strategy_screen.py"
        ):
            return "self.galaxy"

    return None


@pytest.mark.parametrize(
    "path",
    _ui_python_files(),
    ids=lambda p: str(p.relative_to(REPO_ROOT)).replace("\\", "/"),
)
def test_no_unallowlisted_property_reads_in_ui(path: Path) -> None:
    """No non-allowlisted ``scene/_screen/r/screen.{galaxy,empires,systems}``
    (or ``self.galaxy`` in ``strategy_screen.py``) reads anywhere in
    ``game/ui/``.

    UI code reads galaxy/empires/systems through the scene-owned
    ``StrategyWorldAccess`` (``scene.world``) seam or the cold facade queries.
    Existing reads are allowlisted-with-reason in ``_PROPERTY_READ_ALLOWLIST``
    (PROJ-477 migration targets). A net-new read fails here until it is migrated
    or explicitly allowlisted.
    """
    rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    module_name = path.name
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    tc_lines = _type_checking_linenos(tree)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute):
            continue
        if node.lineno in tc_lines:
            continue
        attr_path = _matched_property_read(node, module_name)
        if attr_path is None:
            continue
        if (rel, attr_path) in _PROPERTY_READ_ALLOWLIST:
            continue
        pytest.fail(
            f"PROJ-477 read-path property violation: {rel}:{node.lineno} "
            f"reads `...{attr_path}` directly off the StrategyScreen "
            f"pass-through bus. UI code must read galaxy/empires/systems "
            f"through the scene-owned `scene.world` (StrategyWorldAccess) seam "
            f"or a cold facade query. If this is an intentional transitional "
            f"surface, add `('{rel}', '{attr_path}')` to "
            f"_PROPERTY_READ_ALLOWLIST with a reason comment."
        )


def test_ui_directory_has_python_files() -> None:
    """Sanity: parametrize would silently produce zero tests if not."""
    files = _ui_python_files()
    assert files, f"No .py files found in {UI_DIR}"
    names = {f.name for f in files}
    assert "strategy_screen.py" in names
    assert "strategy_renderer.py" in names


def _violations_in_source(rel_module: str, src: str) -> list[tuple[int, str]]:
    """Helper mirroring the directory-scan body for synthetic-source probes."""
    tree = ast.parse(src, filename=rel_module)
    tc_lines = _type_checking_linenos(tree)
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute):
            continue
        if node.lineno in tc_lines:
            continue
        attr_path = _matched_property_read(node, rel_module)
        if attr_path is None:
            continue
        out.append((node.lineno, attr_path))
    return out


def test_property_read_matcher_recognises_scoped_forms() -> None:
    """Positive-control: the matcher recognises the scoped pass-through reads
    and rejects the injected-local / store / unrelated forms.

    POST-FLESH B4: most live property matches take the NESTED ``c.scene.galaxy``
    / ``self.scene.galaxy`` shape, so those are pinned explicitly. A future
    refactor that narrowed the matcher (e.g. only matched a bare ``scene.galaxy``
    Name receiver, missing the nested attribute receiver) would silently reopen
    the bypass.
    """
    # Nested ``c.scene.galaxy`` / ``self.scene.galaxy`` (the dominant live shape).
    assert _violations_in_source("x.py", "v = c.scene.galaxy\n") == [(1, "scene.galaxy")]
    assert _violations_in_source("x.py", "v = self.scene.galaxy\n") == [(1, "scene.galaxy")]
    assert _violations_in_source("x.py", "v = self.scene.empires\n") == [(1, "scene.empires")]
    assert _violations_in_source("x.py", "v = ui.scene.systems\n") == [(1, "scene.systems")]

    # ``r.empires`` (render re-exporter) and ``_screen.systems`` (build-queue mgr).
    assert _violations_in_source("x.py", "v = r.empires\n") == [(1, "r.empires")]
    assert _violations_in_source("x.py", "v = self._screen.systems\n") == [(1, "_screen.systems")]

    # ``screen.galaxy`` matches ONLY in a helper module that takes a screen handle.
    assert _violations_in_source("strategy_screen_assets.py", "v = screen.empires\n") == [
        (1, "screen.empires")
    ]
    assert _violations_in_source("unrelated_module.py", "v = screen.empires\n") == []

    # ``self.galaxy`` matches ONLY in strategy_screen.py (pathfinder helpers).
    assert _violations_in_source("strategy_screen.py", "v = self.galaxy\n") == [
        (1, "self.galaxy")
    ]

    # NEGATIVE: generic ``self.galaxy`` in a build-queue-style module (injected
    # local) does NOT match — design.md false-positive guard.
    assert _violations_in_source("build_queue_controller.py", "v = self.galaxy\n") == []
    assert _violations_in_source("planet_list_window.py", "v = self.galaxy\n") == []

    # NEGATIVE: a ``.galaxy =`` STORE flags only the RHS read, not the LHS store.
    assert _violations_in_source("x.py", "x.galaxy = c.scene.galaxy\n") == [
        (1, "scene.galaxy")
    ]

    # NEGATIVE: an unrelated ``.galaxy`` attribute (not on a guarded receiver).
    assert _violations_in_source("x.py", "v = obj.galaxy\n") == []
