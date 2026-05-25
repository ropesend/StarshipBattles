"""PROJ-496 Phase 1 T1.2 (origin PROJ-480 T5.14, originally PROJ-479 T3.21).

Architectural static guards for the strategy turn-engine layer. These were
previously embedded as introspection tests inside
``tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py``;
moving them here keeps the unit-test module focused on behavioral checks
and groups all architectural guards under ``tests/static_guards/``.

The two guards preserved here are:

* **Resolver-absent guard at the dispatch site.** PROJ-369 Phase 3 deleted
  the ``_NullBattleResolver`` placeholder. The absent-resolver case is now
  guarded at the dispatch site inside
  ``ConflictResolutionEngine._resolve_combat_at_hex`` (just before
  ``self._battle_resolver.resolve_battle(...)``). A pure-behavioral test
  is hard to write cleanly here because non-combat ticks legitimately do
  not raise — only the attempt to dispatch a battle does. We verify the
  guard's presence by inspecting the engine source for the explicit
  ``ValueError`` and the ``battle_resolver`` reference. This catches
  silent removal of the guard during a future refactor.

* **No import of PlanetModifierEffectEngine from turn_phase_registry.**
  PROJ-428 Phase 1 moved the construction site of
  :class:`PlanetModifierEffectEngine` off the registry module and onto a
  lazy property on :class:`TurnEngine` (accessed through a resolver
  lambda on the descriptor). The AST guard below ensures the registry
  module does not regress by re-importing the engine class.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path


def test_conflict_engine_resolver_guard_present_at_dispatch_site():
    """PROJ-369 Phase 3: ``_NullBattleResolver`` deleted. The
    absent-resolver case is now guarded at the dispatch site inside
    ``ConflictResolutionEngine._resolve_combat_at_hex`` (just before
    ``self._battle_resolver.resolve_battle(...)``).

    Non-combat ticks (no actual battle) do not raise — only the attempt
    to dispatch a battle does. We verify the guard is present by
    inspecting the engine source for the explicit ``ValueError`` and the
    ``battle_resolver`` reference.
    """
    from game.strategy.engine import conflict_resolution_engine

    src = inspect.getsource(
        conflict_resolution_engine.ConflictResolutionEngine._resolve_combat_at_hex
    )
    assert "self._battle_resolver is None" in src, (
        "PROJ-369 Phase 3 guard missing from _resolve_combat_at_hex: "
        "expected an explicit `self._battle_resolver is None` check "
        "before the resolver call site."
    )
    assert "ValueError" in src
    assert "battle_resolver" in src


def test_registry_module_does_not_import_planet_modifier_effect_engine():
    """PROJ-428 Phase 1: turn_phase_registry must not import the engine.

    The construction site lives on a lazy property on TurnEngine; the
    registry must access it through the resolver lambda on the
    descriptor, not via a module-level import.
    """
    from game.strategy.engine import turn_phase_registry as _reg

    src = Path(_reg.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    offenders: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if "planet_modifier_effect_engine" in module:
                offenders.append(f"from {module} import ...")
            for alias in node.names:
                if alias.name == "PlanetModifierEffectEngine":
                    offenders.append(f"from {module} import {alias.name}")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if "planet_modifier_effect_engine" in alias.name:
                    offenders.append(f"import {alias.name}")
    assert not offenders, (
        f"turn_phase_registry must not import PlanetModifierEffectEngine "
        f"(found: {offenders}). PROJ-428 Phase 1 moves construction to "
        f"TurnEngine.planet_modifier_effect_engine."
    )
