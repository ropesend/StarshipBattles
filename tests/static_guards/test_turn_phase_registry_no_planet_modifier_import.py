"""Import-absence guard: ``turn_phase_registry`` must NOT import
``PlanetModifierEffectEngine``.

PROJ-428 Phase 1 moved planet-modifier engine construction from the
registry module to a lazy property on :class:`TurnEngine` (accessed
via a resolver lambda on the descriptor). Re-introducing the import
inside ``turn_phase_registry`` would silently resurrect the pre-
PROJ-428 wiring even if no obvious behavioral test fails.

PROJ-491 Task 1.5: extracted from
``tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py``
into the canonical static-guard suite to preserve architectural intent
while moving away from in-line AST scans from behavioral test files.
"""
from __future__ import annotations

import ast
from pathlib import Path


def test_registry_module_does_not_import_planet_modifier_effect_engine() -> None:
    """``turn_phase_registry`` must not import ``PlanetModifierEffectEngine``."""
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
