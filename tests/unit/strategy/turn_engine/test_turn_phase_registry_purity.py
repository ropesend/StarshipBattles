"""
PROJ-428 Phase 4 (TD-04) — Registry-purity AST guard.

Pins three invariants on ``game/strategy/engine/turn_phase_registry.py``:

1. Zero module-level ``FunctionDef`` / ``AsyncFunctionDef`` nodes — the
   module is descriptor data + dataclasses + constants only.
2. Zero gameplay engine imports. Specifically, no top-level
   ``import``/``from … import`` that references ``MinefieldResolver``,
   ``PlanetModifierEffectEngine``, or any module under
   ``game.strategy.engine.*_engine`` / ``minefield_resolver`` /
   ``planet_modifier_effect_engine``.
3. ``DEFAULT_TICK_PHASE_LIST`` and ``DEFAULT_END_OF_TURN_PHASE_LIST``
   keep the same phase keys in the same order.

Any of these failing means the registry has drifted back toward
behavior-bearing helpers; that is intentionally a hard failure.
"""
from __future__ import annotations

import ast
from pathlib import Path


REGISTRY_PATH = (
    Path(__file__).resolve().parents[4]
    / "game"
    / "strategy"
    / "engine"
    / "turn_phase_registry.py"
)


# Pinned golden orders. Any reorder/rename is a regression that should
# break this test loudly.
GOLDEN_TICK_PHASE_KEYS: tuple[str, ...] = (
    'harvesting',
    'resources',
    'fuel_gen',
    'planet_energy',
    'resupply',
    'production',
    'environmental',
    'instant_orders',
    'actions',
    'planet_actions',
    'activation_timers',
    'planet_modifier_effects',
    'movement_calc',
    'movement_apply',
    'combat',
)

GOLDEN_END_OF_TURN_PHASE_KEYS: tuple[str, ...] = (
    'organics_consumption',
    'happiness',
    'population_growth',
    'quality_improvement',
    'atmosphere',
    'water_modification',
)


# Forbidden gameplay-engine module substrings. Any top-level
# ``ImportFrom`` whose ``module`` matches a substring here is a
# violation. The list is intentionally aggressive — the registry must
# stay descriptor-only.
_FORBIDDEN_ENGINE_IMPORT_SUBSTRINGS: tuple[str, ...] = (
    "minefield_resolver",
    "planet_modifier_effect_engine",
    "production_engine",
    "harvesting_engine",
    "fleet_movement_engine",
    "conflict_resolution_engine",
    "consumable_management_engine",
    "resupply_engine",
    "action_execution_engine",
    "environmental_hazard_engine",
    "planet_energy_engine",
    "planet_action_engine",
    "component_activation_engine",
    "organics_consumption_engine",
    "happiness_engine",
    "quality_engine",
    "atmosphere_engine",
    "water_engine",
    "population_engine",
)

# Forbidden top-level imported names. ``MinefieldResolver`` /
# ``PlanetModifierEffectEngine`` must never be imported at module scope.
_FORBIDDEN_IMPORTED_NAMES: tuple[str, ...] = (
    "MinefieldResolver",
    "PlanetModifierEffectEngine",
)


def _parse_registry() -> ast.Module:
    src = REGISTRY_PATH.read_text(encoding="utf-8")
    return ast.parse(src)


class TestRegistryHasNoModuleLevelFunctions:
    """The registry module must contain zero module-level function
    definitions — pure descriptor data only."""

    def test_no_module_level_functiondef(self):
        tree = _parse_registry()
        offenders: list[str] = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                offenders.append(node.name)
        assert not offenders, (
            f"turn_phase_registry.py has module-level function defs: "
            f"{offenders}. PROJ-428 keeps this module descriptor-only; "
            f"move behavior onto TurnEngine or a named collaborator."
        )


class TestRegistryHasNoGameplayEngineImports:
    """The registry must not import any gameplay engine class or module
    at module scope. Construction lives on TurnEngine or its
    collaborators."""

    def test_no_forbidden_engine_module_imports(self):
        tree = _parse_registry()
        offenders: list[str] = []
        for node in tree.body:
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for forbidden in _FORBIDDEN_ENGINE_IMPORT_SUBSTRINGS:
                    if forbidden in module:
                        offenders.append(
                            f"from {module} import "
                            f"{', '.join(a.name for a in node.names)}"
                        )
                        break
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    for forbidden in _FORBIDDEN_ENGINE_IMPORT_SUBSTRINGS:
                        if forbidden in alias.name:
                            offenders.append(f"import {alias.name}")
                            break
        assert not offenders, (
            f"turn_phase_registry.py imports gameplay engine modules at "
            f"module scope: {offenders}. Move construction to TurnEngine "
            f"or its collaborators."
        )

    def test_no_forbidden_imported_names(self):
        tree = _parse_registry()
        offenders: list[str] = []
        for node in tree.body:
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name in _FORBIDDEN_IMPORTED_NAMES:
                        offenders.append(
                            f"from {node.module} import {alias.name}"
                        )
        assert not offenders, (
            f"turn_phase_registry.py imports forbidden gameplay engine "
            f"names: {offenders}."
        )


class TestRegistryDescriptorListsAreGolden:
    """The two pinned descriptor lists must keep the same phase keys in
    the same order. Reordering is a regression."""

    def test_default_tick_phase_list_keys_match_golden(self):
        from game.strategy.engine.turn_phase_registry import (
            DEFAULT_TICK_PHASE_LIST,
        )

        actual = tuple(p.phase_key for p in DEFAULT_TICK_PHASE_LIST)
        assert actual == GOLDEN_TICK_PHASE_KEYS

    def test_default_end_of_turn_phase_list_keys_match_golden(self):
        from game.strategy.engine.turn_phase_registry import (
            DEFAULT_END_OF_TURN_PHASE_LIST,
        )

        actual = tuple(p.phase_key for p in DEFAULT_END_OF_TURN_PHASE_LIST)
        assert actual == GOLDEN_END_OF_TURN_PHASE_KEYS
