# PROJ-276: Eradicate Legacy component_damage Dual-Tracking

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-276` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-276 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Call-site audit (read-only) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Migrate `ship_stats_calculator.py` (TDD) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Migrate `ship_instance_bridge.py` | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Migrate `ship_design_stats.py` | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Update serializer + bump save format | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Delete field + dual-write | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Update tests | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. Docs | Not Started | [phase_8_checklist.md](phase_8_checklist.md) |

## Current State
**Last Updated:** 2026-04-16
**Active Phase:** Planning (ready to start Phase 1)
**Last Action:** Project created with full plan
**Next Action:** Begin Phase 1 — audit and classify all 47 production `component_damage` call sites
**Blockers:** None (independent of PROJ-273/274/275)
**Context for Next Agent:** User was unaware of this dual-tracking until the combat-system review. `ShipInstance.component_damage: Dict[str, int]` is legacy (single-instance granularity — one HP per `component_id`) and coexists with `ShipInstance.components: Dict[str, ComponentState]` (per-instance granularity — keyed `{component_id}#{instance_index}`). The post-battle hook silently lossy-flattens per-instance data back to the legacy dict. `ShipStatsCalculator` still reads the legacy version for stat math. 47 production call sites + 29 test occurrences. User's Clean-Sheet Rule + System Migration Policy mandate eradication, not bridging. Save format bumps; saves disposable per CLAUDE.md.

## Overview

Delete `ShipInstance.component_damage` field entirely. Migrate all 47 production call sites to `ShipInstance.components: Dict[str, ComponentState]`. Bump save-file format; do not write migration shims (saves are disposable per project policy).

## Goals

- `ShipInstance.component_damage` field deleted.
- All 47 production call sites migrated to per-instance `components` dict.
- `ShipStatsCalculator` reads per-instance HP (multi-instance ships now correctly represent partial damage).
- Save format bumped; no migration code.
- Post-battle hook writes only to `components`.

## Scope

**In:**
- `game/strategy/data/ship_instance.py` — delete `component_damage` field (L113).
- `game/strategy/services/ship_stats_calculator.py` — 20 migration sites (the big one).
- `game/strategy/data/ship_instance_bridge.py` — 6 sites.
- `game/strategy/data/ship_instance_serializer.py` — 3 sites; save format bump.
- `game/strategy/data/component_state.py` — 2 sites; verify API surface.
- `game/strategy/combat/post_battle_hook.py` — delete legacy rebuild (L155-162).
- `game/simulation/entities/ship_design_stats.py` — 4 sites.
- Test updates: 10 files, ~29 occurrences.
- Docs: `docs/systems/strategy_layer.md`, `docs/04_SERVICES.md`.

**Out:**
- Save migration (saves disposable per `CLAUDE.md`).
- Repair/regeneration mechanics (separate future project).

## Key Files

| Component | File Path |
|-----------|-----------|
| Ship instance DTO | `game/strategy/data/ship_instance.py` |
| Ship stats calculator | `game/strategy/services/ship_stats_calculator.py` |
| Ship instance bridge | `game/strategy/data/ship_instance_bridge.py` |
| Serializer | `game/strategy/data/ship_instance_serializer.py` |
| Component state | `game/strategy/data/component_state.py` |
| Post-battle hook | `game/strategy/combat/post_battle_hook.py` |
| Design stats | `game/simulation/entities/ship_design_stats.py` |
| Test fixture | `tests/fixtures/strategy_entities.py` |
| Docs | `docs/systems/strategy_layer.md`, `docs/04_SERVICES.md` |

## Related Documents
- [design.md](design.md)
- [decisions.md](decisions.md)
- [manifest.md](manifest.md)

## Verification
- [ ] All phase checklists complete
- [ ] Grep `grep -rn "component_damage" game/` returns ZERO production hits
- [ ] Full suite: `python Tools/test_sharded/test_sharded.py` — 14727+ passing, no regressions
- [ ] Manual: start new strategy game, deal partial damage to a multi-instance weapon, retreat, save, reload; verify per-instance damage preserved
- [ ] Perf: no regression on stat-calculation hot path
- [ ] Audit passed
- [ ] User verified
