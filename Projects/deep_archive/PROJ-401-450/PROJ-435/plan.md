# PROJ-435: Migrate UI _ACTIVATABLE_ABILITIES to AbilityMetadataRegistry

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-435` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Audit gap + propose registry shape | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Implement migration | Complete | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-05-17
**Active Phase:** All phases complete; awaiting user verification.
**Last Action:** Phase 2 — registered `GravityModifier` and `RadiationShield` in `AbilityMetadataRegistry` (ENERGY_DRAINING + EnergyFacet); replaced `_ACTIVATABLE_ABILITIES` literal with `_ACTIVATABLE_ABILITY_LABELS` (label-only) + `_activatable_ability_iteration_order()` registry-driven helper; replaced inline `modifier_abilities` literal with `_MODIFIER_ABILITY_LABELS` + `_modifier_ability_iteration_order()` filtering `COMBAT_MODIFIER ∪ BUILD_RATE_BOOSTER ∪ RESOURCE_BOOSTER` by UI label presence. Full sharded suite green (21129/21129).
**Next Action:** User verification.
**Blockers:** None

## Phase 2 plan
1. Failing test in `tests/unit/ui/screens/builder/test_stat_rows_dynamic.py` that:
   - Asserts `_ACTIVATABLE_ABILITIES` and the inline `modifier_abilities` literal are gone (negative regression guard via `getattr(stat_rows_dynamic, '_ACTIVATABLE_ABILITIES', None) is None`).
   - Asserts that `get_planetary_defense_rows` picks up `GravityModifier` and `RadiationShield` (positive regression on the two newly registered abilities).
2. Add new test in `tests/unit/strategy/services/test_ability_metadata_registry.py` (or extend existing) asserting `GravityModifier` and `RadiationShield` are registered with the `ENERGY_DRAINING` kind tag and have an `EnergyFacet` with `drains_energy=True`.
3. Implementation:
   - Register the two abilities in `game/strategy/services/ability_metadata.py`.
   - Rewrite `_ACTIVATABLE_ABILITIES` in `stat_rows_dynamic.py` as a UI-side label dict that iterates `abilities_with_kind_tag(StrategicKind.ENERGY_DRAINING)` (renamed to make the label-only intent explicit).
   - Rewrite `modifier_abilities` to iterate registry tags and filter by UI label presence.
4. File diff estimate: ~50 lines (registry: +12, UI: ±30, tests: +20).

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
