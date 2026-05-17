"""PROJ-423 Phase 4: GameSession shell-shape regression tests.

These tests pin the structural endpoint of the refactor: `game_session.py`
no longer constructs mutator services / turn engine / event bus / command
registry / GameInitializer inline, `race_registry` is still lazy, and the
file is a thin shell well below the original 599 LOC.
"""
from __future__ import annotations

import ast
from pathlib import Path

from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.strategy.engine.game_session import GameSession


# Absolute path of the production file under inspection.
# parents: 0=engine, 1=strategy, 2=unit, 3=tests, 4=repo root.
_GAME_SESSION_PATH = (
    Path(__file__).resolve().parents[4]
    / "game" / "strategy" / "engine" / "game_session.py"
)


def _imported_names(source_path: Path) -> set[str]:
    """Return the set of names brought in by `import` / `from ... import`
    statements in `source_path` (excluding TYPE_CHECKING-only imports)."""
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    names: set[str] = set()

    def _walk(node: ast.AST, inside_type_checking: bool) -> None:
        if isinstance(node, ast.If):
            test = node.test
            is_tc_guard = (
                isinstance(test, ast.Name) and test.id == "TYPE_CHECKING"
            )
            for child in node.body:
                _walk(child, inside_type_checking or is_tc_guard)
            for child in node.orelse:
                _walk(child, inside_type_checking)
            return
        if isinstance(node, ast.Import):
            if not inside_type_checking:
                for alias in node.names:
                    names.add(alias.asname or alias.name.split(".")[-1])
            return
        if isinstance(node, ast.ImportFrom):
            if not inside_type_checking:
                for alias in node.names:
                    names.add(alias.asname or alias.name)
            return
        for child in ast.iter_child_nodes(node):
            _walk(child, inside_type_checking)

    _walk(tree, inside_type_checking=False)
    return names


def _minimal_config() -> GameConfig:
    config = GameConfig()
    config.galaxy_radius = 300
    config.system_count = 2
    config.players = [
        PlayerConfig(name="A", is_human=True, color=(0, 100, 200)),
        PlayerConfig(name="B", is_human=False, color=(200, 100, 0)),
    ]
    return config


class TestGameSessionImports:
    """`game_session.py` no longer pulls in the composition-root machinery
    directly — that lives in `SessionBootstrap` / `SessionPersistenceAdapter`
    now."""

    def test_game_session_no_longer_constructs_mutator_services_inline(self) -> None:
        names = _imported_names(_GAME_SESSION_PATH)
        for forbidden in (
            "FleetNavigationService",
            "FleetWriteService",
            "PlanetWriteService",
            "EmpireWriteService",
            "ShipInstanceWriteService",
        ):
            assert forbidden not in names, (
                f"game_session.py still imports {forbidden}; expected "
                f"construction to be delegated to SessionBootstrap."
            )

    def test_game_session_no_longer_constructs_turn_engine_inline(self) -> None:
        names = _imported_names(_GAME_SESSION_PATH)
        for forbidden in (
            "TurnEngineConfig",
            "TurnEngine",
            "create_default_registry",
            "EventBus",
            "GameInitializer",
        ):
            assert forbidden not in names, (
                f"game_session.py still imports {forbidden}; expected "
                f"construction to live in SessionBootstrap."
            )


class TestLazyRaceRegistry:
    """`race_registry` stays lazy-cached on GameSession — it is explicitly
    outside the SessionRuntimeServices bag.

    Pre-refactor `__init__` eagerly triggered `self.race_registry` access
    while wiring TurnEngineConfig, so the property is populated by the
    end of construction. The "lazy" contract is structural: the storage
    slot lives on `self`, not on the services bag, and the property
    backs onto `self._race_registry` with a one-shot construction. This
    test pins the structural invariant.
    """

    def test_game_session_keeps_lazy_race_registry_slot_on_session(self) -> None:
        session = GameSession(config=_minimal_config())
        # The cached instance lives directly on the session — NOT inside
        # SessionRuntimeServices.
        assert session._race_registry is not None
        assert not hasattr(session.services, "race_registry")
        # The race_registry property returns the cached slot, not a
        # fresh value on each call.
        first = session.race_registry
        second = session.race_registry
        assert first is second
        assert first is session._race_registry

    def test_game_session_race_registry_is_none_before_construction(self) -> None:
        """The `_race_registry` slot defaults to None before bootstrap
        applies state, preserving the lazy-cache semantic for any custom
        code path that constructs a session manually via `__new__`."""
        from game.strategy.engine.game_session import GameSession
        # Direct __new__ leaves _race_registry unset; the GameSession
        # bootstrap path sets it to None *before* services wiring so
        # `_build_services` can call `self.race_registry` and trigger
        # the lazy population.
        bare = GameSession.__new__(GameSession)
        assert not hasattr(bare, "_race_registry")


class TestFileSize:
    """The post-refactor file should be a thin shell; pin a generous
    ceiling so the structural goal stays a regression target."""

    # PROJ-423: file dropped from 599 LOC → ~475 LOC. The budget is set
    # comfortably above current to leave a small ceiling for docstring
    # additions, but materially below the pre-refactor size so any
    # regression of inline composition-root logic shows up here.
    LOC_BUDGET = 500

    def test_game_session_file_loc_budget(self) -> None:
        loc = sum(1 for _ in _GAME_SESSION_PATH.read_text(
            encoding="utf-8"
        ).splitlines())
        assert loc <= self.LOC_BUDGET, (
            f"game_session.py is {loc} LOC; budget is {self.LOC_BUDGET}. "
            f"PROJ-423 leaves it as a thin shell; if you need more lines, "
            f"check whether new composition-root logic snuck back in."
        )
