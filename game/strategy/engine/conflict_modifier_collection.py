"""Modifier-collection helpers for ConflictResolutionEngine.

PROJ-382 Phase 5: extracted from ``conflict_resolution_engine.py`` to
bring the parent module under the 500 LOC ceiling.  Two functions
implement the environmental-effects + team-modifier collection
responsibility — they take an explicit ``engine`` reference because they
need ``engine._galaxy`` / ``engine._registries`` / ``engine._empires``.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine


logger = logging.getLogger(__name__)


def lookup_environmental_effects(
    engine: "ConflictResolutionEngine", location: Any,
) -> Optional[Any]:
    """PROJ-189: Query environmental effects at the combat location.

    PROJ-300: returns the new sector-effects list shape from the unified
    collector. The spec compiler accepts either the legacy
    EnvironmentalEffects object (effective during AreaEffectManager
    deprecation) or this new list. Phase 7 deletes the legacy path.
    """
    if engine._galaxy is None:
        return None
    get_system = getattr(engine._galaxy, 'get_system_at_location', None)
    if get_system is None:
        return None
    system = get_system(location)
    if system is None:
        return None
    from game.strategy.services.system_effects_collector import collect_sector_effects
    return collect_sector_effects(
        system, location, empire_id=None, registries=engine._registries,
    )


def collect_team_modifiers(
    engine: "ConflictResolutionEngine",
    fleets_by_empire: Dict[int, List["Fleet"]],
    empire_order: List[int],
    *,
    location: Any = None,
) -> Optional[Dict[int, Any]]:
    """Collect strategic combat modifiers for each team.

    PROJ-320 Phase 3: per-empire fleet lists; team_id is the position in
    ``empire_order``. Each team's modifier set is computed once using a
    representative fleet (the lowest-id one) — only the opponent's empire
    id matters for facility-scope queries.
    """
    if engine._galaxy is None:
        return None
    all_empires = getattr(engine, '_empires', [])
    modifiers: Dict[int, Any] = {}
    # Pre-pick one representative fleet per empire for the modifier
    # collector — sorted by fleet.id for determinism.
    representatives: Dict[int, "Fleet"] = {
        eid: sorted(fleets_by_empire[eid], key=lambda f: f.id)[0]
        for eid in empire_order
    }
    try:
        from game.strategy.services.combat_modifier_collector import (
            collect_combat_modifiers,
        )
        for team_id, eid in enumerate(empire_order):
            fleet = representatives[eid]
            opponent_empires = [other for other in empire_order if other != eid]
            if not opponent_empires:
                continue
            opponent_fleet = representatives[opponent_empires[0]]
            modifiers[team_id] = collect_combat_modifiers(
                fleet, opponent_fleet, engine._galaxy, all_empires,
                engine._registries,
            )
    except Exception as e:  # Intentional broad catch: external collector may raise any type from non-engine empire/system extensions; ERROR-log and proceed with degraded modifier stack so battle still resolves. Hex + empire context included to allow log-side debugging.
        # PROJ-381 Phase 2 (B-7): demote-to-warning was hiding a real
        # information loss; promote to error and include hex/empire
        # context so the log line is actionable.
        logger.error(
            "Failed to collect combat modifiers at hex=%s empires=%s: %s",
            location, empire_order, e,
        )
        return None
    return modifiers or None
