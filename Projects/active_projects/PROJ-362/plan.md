# PROJ-362: Strategic effects metadata registry + _aggregate decomposition

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-362`
> - Open the phase checklist file for your current phase
> - Check off tasks as completed
> - Update Current State before stopping

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-362 [phase]`
> - Update Current State with handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Characterization tests (TDD baseline) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. EffectAbilityMetadata registry | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Decompose `_aggregate` | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Retire `_legacy_provider_fields` (deferred) | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** Planning (awaiting user approval)
**Last Action:** Plan drafted from review finding #2 (P1 hotspot — CC 47, 193 lines, hardcoded ability metadata). Renumbered from PROJ-352 to PROJ-362.
**Next Action:** User approval, then begin Phase 1 in Continue Project session.
**Blockers:** None

## Overview
`game/strategy/services/system_effects_collector._aggregate` is a 193-line CC-47 function that owns: source iteration, error tolerance, ownership filtering, scope validation, activation lookup, provider DTO construction, legacy compatibility, mixed-kind validation, and final aggregation. The supported ability set is hardcoded in `SYSTEM_EFFECT_ABILITIES`, `_RATE_ABILITIES`, `_OWNER_AWARE_SCOPES`, and special-case branches in `make_group_key` / `make_display_name`. Adding a new strategic effect requires editing the collector.

## Goals
- Introduce `EffectAbilityMetadata` registry that drives display name, kind, grouping, scope rules, and value extraction.
- Decompose `_aggregate` into `collect_providers`, `aggregate_status`, `aggregate_value`, `format_rows` — each a tightly-scoped function.
- Eliminate hardcoded ability-name special cases from the collector. New effects added by registering metadata.
- Plan `_legacy_provider_fields` retirement after UI consumer audit (Phase 4, deferred).

## Scope
**In:**
- `game/strategy/services/system_effects_collector.py`
- New `game/strategy/services/effect_ability_metadata.py` registry module
- `tests/unit/strategy/services/test_system_effects_collector*.py` (characterization additions)
- `tests/unit/strategy/services/test_effect_ability_metadata.py` (new)

**Out:**
- `game/strategy/services/combat_modifier_collector.py` — parallel consumer of similar data, but uses `find_abilities_in_scope` and a different aggregation model. Out of scope per finding (PROJ-272 boundary).
- UI panel changes — they continue consuming the same return shape from `collect_system_effects` / `collect_sector_effects`.
- `_legacy_provider_fields` actual deletion (Phase 4 deferred until UI consumer migration plan exists)

## Key Files
| Component | File Path |
|-----------|-----------|
| Collector | `game/strategy/services/system_effects_collector.py` (lines 62-90 hardcoded tables, 281-430+ `_aggregate`) |
| New metadata registry | `game/strategy/services/effect_ability_metadata.py` (new) |
| Combat modifier (parallel, not modified) | `game/strategy/services/combat_modifier_collector.py` |
| IAbilitySource framework | `game/strategy/protocols/ability_source.py` |
| Existing tests | `tests/unit/strategy/services/test_system_effects_collector.py` |
| New characterization tests | `tests/unit/strategy/services/test_system_effects_collector_aggregate_characterization.py` (new) |
| New registry tests | `tests/unit/strategy/services/test_effect_ability_metadata.py` (new) |

## Related Documents
- [design.md](design.md) - Architecture and decomposition design
- [decisions.md](decisions.md) - Full decisions log
- [findings/01_architecture.md](findings/01_architecture.md) - Hardcoded special cases inventory; proposed metadata shape
- [findings/02_dependencies.md](findings/02_dependencies.md) - Public callers; legacy field consumers
- [findings/03_test_impact.md](findings/03_test_impact.md) - Coverage gaps; required characterization tests

## Verification
- [ ] All phase checklists complete
- [ ] `pytest tests/unit/strategy/services/test_system_effects_collector*.py tests/unit/strategy/services/test_effect_ability_metadata.py -v` — all pass
- [ ] `pytest tests/unit/strategy/ tests/integration/strategy/ --testmon` — no regressions
- [ ] UI smoke test: open System Tree panel and Planet List; effect rows render identically
- [ ] Audit passed
- [ ] User verified
