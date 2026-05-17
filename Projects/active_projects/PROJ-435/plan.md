# PROJ-435: Migrate UI _ACTIVATABLE_ABILITIES to AbilityMetadataRegistry

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-435` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Audit gap + propose registry shape | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Implement migration | Not Started | (TBD) |

## Current State
**Last Updated:** 2026-05-17
**Active Phase:** Planning
**Last Action:** Scaffold created by PROJ-429 Phase 8 as a spin-off from Codex consult finding 4.
**Next Action:** Phase 1 — audit the gap and decide whether to extend
`AbilityMetadataRegistry` with UI-facing labels or to introduce a thin
UI-layer label map keyed on `StrategicKind.ENERGY_DRAINING` + named
non-registered abilities.
**Blockers:** None

## Overview
`game/ui/screens/builder/stat_rows_dynamic.py:381-463` defines two hardcoded
dicts (`_ACTIVATABLE_ABILITIES` and `modifier_abilities`) mapping ability
names to UI display labels. The names overlap partially with
`AbilityMetadataRegistry` kind tags (ENERGY_DRAINING, COMBAT_MODIFIER,
RESOURCE_BOOSTER, BUILD_RATE_BOOSTER) but the UI also carries
display-label strings and includes two abilities that are NOT in the
registry (`GravityModifier`, `RadiationShield`).

## Goals
- Eliminate the hardcoded ability-name literals in `stat_rows_dynamic.py`
  in favour of registry-driven iteration.
- Decide and document the canonical home for UI-facing display labels
  (registry vs UI-layer label map).
- Either register `GravityModifier` and `RadiationShield` in
  `AbilityMetadataRegistry` (with appropriate kind tags) OR keep them as
  documented UI-only exceptions.

## Scope
**In:**
- `game/ui/screens/builder/stat_rows_dynamic.py` — `_ACTIVATABLE_ABILITIES`
  and `modifier_abilities` maps.
- Any registry extension required to support UI labels cleanly.

**Out:**
- Other UI-layer hardcoded ability lists (separate audit).
- Behaviour changes to which abilities are shown.

## Key Files
| Component | File Path |
|-----------|-----------|
| UI dynamic rows | `game/ui/screens/builder/stat_rows_dynamic.py` |
| Ability metadata registry | `game/strategy/services/ability_metadata.py` |
| Reference migration | `game/strategy/engine/planet_energy_engine.py` (Phase 3 pattern) |

## Spawning Context
This project was spun off from PROJ-429 Phase 8 (Codex consult follow-up
finding 4) because the migration is not a mechanical name-set swap:

1. The UI maps mix registered and unregistered ability names.
2. The UI maps carry display-label strings that have no current home in
   the registry.
3. The grouping (`_ACTIVATABLE_ABILITIES` = 6 names) doesn't match any
   single kind tag (`ENERGY_DRAINING` = 4 names).

See `Projects/active_projects/PROJ-429/decisions.md` row "Codex consult
follow-ups (Phase 8)" for the original gap analysis.

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
