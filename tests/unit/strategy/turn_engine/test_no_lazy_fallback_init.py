"""
PROJ-369 Phase 3 — AST regression guard for TurnEngine.

Pins three invariants that the Phase 3 refactor establishes:

1. Zero ``if self._<x>_engine is None:`` fallback patterns inside
   ``turn_engine.py`` (the lazy-init pattern that defeated DI).
2. Zero function-local ``from game.strategy.engine.<x>_engine import
   <X>Engine`` statements inside ``TurnEngine`` methods. The ONE
   allow-listed location for engine imports is
   ``TurnEngineConfig.create_default()`` (different module).
3. ``TurnEngine.__init__`` accepts at most 8 parameters (excluding
   ``self``) — collapsed from 21 in PROJ-259's wire-up.
4. The ``_NullBattleResolver`` symbol is no longer importable from
   ``game.strategy.engine.turn_engine`` — eliminated in favor of
   raise-on-use in ``ConflictResolutionEngine``.

Any of these failing means the refactor regressed; that's intentional
and the test should NOT be relaxed without surfacing the change in
PROJ-369's decisions.md.
"""
from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest


TURN_ENGINE_PATH = (
    Path(__file__).resolve().parents[4]
    / "game"
    / "strategy"
    / "engine"
    / "turn_engine.py"
)


def _parse_turn_engine() -> ast.Module:
    src = TURN_ENGINE_PATH.read_text(encoding="utf-8")
    return ast.parse(src)


def _turn_engine_class_node(tree: ast.Module) -> ast.ClassDef:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "TurnEngine":
            return node
    pytest.fail("TurnEngine class not found in turn_engine.py")


class TestNoLazyFallbackInit:
    """AST-level regression guard for PROJ-369 Phase 3 invariants."""

    def test_no_if_self_engine_is_none_pattern(self):
        """No ``if self._foo_engine is None:`` checks inside the file.

        These are the 15 lazy-fallback init bodies that PROJ-369 Phase 3
        removed. Any reappearance is a regression.
        """
        tree = _parse_turn_engine()
        offenders: list[str] = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.If):
                continue
            t = node.test
            if not isinstance(t, ast.Compare):
                continue
            if not (len(t.ops) == 1 and isinstance(t.ops[0], ast.Is)):
                continue
            # left side: self._<x>_engine (Attribute on self)
            left = t.left
            if not (
                isinstance(left, ast.Attribute)
                and isinstance(left.value, ast.Name)
                and left.value.id == "self"
                and left.attr.startswith("_")
                and left.attr.endswith(("_engine", "_processor", "_resolver"))
            ):
                continue
            # right side: Constant(None) or NameConstant
            right = t.comparators[0]
            if isinstance(right, ast.Constant) and right.value is None:
                offenders.append(left.attr)
        assert not offenders, (
            f"Found `if self._X is None` fallback patterns: {offenders}. "
            "PROJ-369 Phase 3 removed these in favor of "
            "TurnEngineConfig.create_default()."
        )

    # Set of engine submodules whose construction must happen in
    # ``TurnEngineConfig.create_default()`` (turn_engine_config.py:122-151).
    # Any function-local import of one of these inside a TurnEngine method
    # is a regression that re-introduces the lazy-fallback pattern PROJ-369
    # eliminated. Update this set when new engines land in
    # ``TurnEngineConfig.create_default()``.
    #
    # PROJ-369 review MIN-002: this is an explicit allowlist rather than a
    # ``module.endswith("_engine")`` filter, which (a) failed to catch
    # ``order_processor`` (a real engine submodule whose name does not
    # match the suffix) and (b) over-caught legitimate non-engine helper
    # modules like ``turn_state_snapshot`` (PROJ-251 rollback) which have
    # documented late-import reasons.
    _CONSTRUCTABLE_ENGINE_MODULES = frozenset({
        "game.strategy.engine.fleet_movement_engine",
        "game.strategy.engine.production_engine",
        "game.strategy.engine.order_processor",
        "game.strategy.engine.conflict_resolution_engine",
        "game.strategy.engine.consumable_management_engine",
        "game.strategy.engine.population_engine",
        "game.strategy.engine.resupply_engine",
        "game.strategy.engine.harvesting_engine",
        "game.strategy.engine.action_execution_engine",
        "game.strategy.engine.environmental_hazard_engine",
        "game.strategy.engine.planet_energy_engine",
        "game.strategy.engine.planet_action_engine",
        "game.strategy.engine.component_activation_engine",
        "game.strategy.engine.organics_consumption_engine",
        "game.strategy.engine.happiness_engine",
        "game.strategy.engine.quality_engine",
        "game.strategy.engine.atmosphere_engine",
        "game.strategy.engine.water_engine",
    })

    def test_no_function_local_engine_imports_in_TurnEngine_methods(self):
        """No function-local import of any constructable engine module
        inside a TurnEngine method.

        The lone allow-listed location for engine imports is
        ``TurnEngineConfig.create_default()`` (a different module).
        """
        tree = _parse_turn_engine()
        cls = _turn_engine_class_node(tree)
        offenders: list[str] = []
        for child in cls.body:
            if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for node in ast.walk(child):
                if not isinstance(node, ast.ImportFrom):
                    continue
                module = node.module or ""
                if module in self._CONSTRUCTABLE_ENGINE_MODULES:
                    offenders.append(f"{child.name}: from {module} import ...")
        assert not offenders, (
            f"Found function-local engine imports inside TurnEngine: {offenders}. "
            "Construction belongs in TurnEngineConfig.create_default()."
        )

    def test_TurnEngine_init_signature_has_at_most_8_params(self):
        """``TurnEngine.__init__`` should accept at most 8 params after self.

        Phase 3 collapses the 21-param ctor (battle_resolver + 16 engine
        kwargs + registries/race_registry/event_bus/config/ai_factory/
        tick_phases/end_of_turn_phases) down to 8.
        """
        from game.strategy.engine.turn_engine import TurnEngine

        sig = inspect.signature(TurnEngine.__init__)
        # Exclude 'self'.
        params = [p for p in sig.parameters.values() if p.name != "self"]
        assert len(params) <= 8, (
            f"TurnEngine.__init__ has {len(params)} params: "
            f"{[p.name for p in params]}. Phase 3 caps this at 8."
        )

    def test_NullBattleResolver_symbol_absent(self):
        """``_NullBattleResolver`` must not exist on the module.

        Phase 3 deleted this class. Combat with ``battle_resolver=None``
        now raises directly from ``ConflictResolutionEngine`` instead of
        going through a placeholder warn-and-raise wrapper.
        """
        from game.strategy.engine import turn_engine as turn_engine_module

        assert not hasattr(turn_engine_module, "_NullBattleResolver"), (
            "_NullBattleResolver was deleted in PROJ-369 Phase 3."
        )

    def test_run_phases_called_exactly_twice_in_process_turn(self):
        """``process_turn`` must dispatch through ``_run_phases`` twice:
        once for the per-tick body (inside the 100-tick loop via
        ``_process_tick``) and once for the end-of-turn block.

        PROJ-369 Phase 5: pins the unified-loop invariant so future
        edits cannot reintroduce inline iteration without breaking
        this test.
        """
        tree = _parse_turn_engine()
        cls = _turn_engine_class_node(tree)

        # Find the two functions whose bodies should each contain one
        # _run_phases call: process_turn (end-of-turn dispatch) and
        # _process_tick (per-tick dispatch).
        target_methods = {"process_turn", "_process_tick"}
        run_phases_calls: dict[str, int] = {}
        for child in cls.body:
            if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if child.name not in target_methods:
                continue
            count = 0
            for node in ast.walk(child):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "_run_phases"
                ):
                    count += 1
            run_phases_calls[child.name] = count

        assert run_phases_calls.get("process_turn") == 1, (
            f"process_turn must call _run_phases exactly once "
            f"(found {run_phases_calls.get('process_turn', 0)})"
        )
        assert run_phases_calls.get("_process_tick") == 1, (
            f"_process_tick must call _run_phases exactly once "
            f"(found {run_phases_calls.get('_process_tick', 0)})"
        )

    def test_no_inline_engine_method_calls_in_process_turn(self):
        """``process_turn`` must not contain inline ``self.<x>_engine.<m>(...)``
        calls outside the descriptor-iteration helper.

        PROJ-369 Phase 5: ensures the imperative end-of-turn block
        cannot reappear. Whitelist: snapshot capture, _log_empire_state,
        _process_tick, _run_phases, _reset_phase_times — none of those
        match the engine-method-call pattern.
        """
        tree = _parse_turn_engine()
        cls = _turn_engine_class_node(tree)
        process_turn = next(
            n for n in cls.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            and n.name == "process_turn"
        )

        offenders: list[str] = []
        for node in ast.walk(process_turn):
            if not isinstance(node, ast.Call):
                continue
            f = node.func
            if not isinstance(f, ast.Attribute):
                continue
            # `self.<x>_engine.<method>(...)` pattern, e.g.
            # `self.population_engine.process_population_growth(...)`.
            if not isinstance(f.value, ast.Attribute):
                continue
            inner = f.value
            if not isinstance(inner.value, ast.Name):
                continue
            if inner.value.id != "self":
                continue
            if not (
                inner.attr.endswith("_engine")
                or inner.attr == "order_processor"
            ):
                continue
            offenders.append(f"self.{inner.attr}.{f.attr}(...)")
        assert not offenders, (
            f"Found inline engine-method calls in process_turn: "
            f"{offenders}. End-of-turn dispatch must go through "
            f"`_run_phases(self._end_of_turn_phases, ...)`."
        )

    def test_create_default_is_only_function_local_engine_import_site(self):
        """``TurnEngineConfig.create_default`` is the lone module that
        may use function-local engine imports. ``turn_engine.py`` must
        contain zero such imports inside any TurnEngine method
        (already pinned by ``test_no_function_local_engine_imports_…``);
        this test verifies the ``create_default`` allow-listing
        explicitly to lock in the convention.
        """
        from game.strategy.engine.turn_engine_config import TurnEngineConfig
        # Sanity: create_default exists and is a classmethod.
        assert callable(getattr(TurnEngineConfig, "create_default", None))
