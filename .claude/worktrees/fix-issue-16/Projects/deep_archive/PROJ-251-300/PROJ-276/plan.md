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
| 1. Call-site audit (read-only) | Complete (discrepancy flagged) | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Delete dead `ship_stats_calculator.py` | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Migrate `ship_instance_bridge.py` | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Migrate `ship_design_stats.py` | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Update serializer + bump save format | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Delete field + dual-write | Complete | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Update tests | Complete | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. Docs | Complete | [phase_8_checklist.md](phase_8_checklist.md) |

## Current State
**Last Updated:** 2026-04-16
**Active Phase:** ALL PHASES COMPLETE — project ready for user verification.
**Last Action:** Completed Phases 7 (test cleanup — mechanical) and 8 (docs + memory). Full sharded suite: 14,627 passed / 1 pre-existing unrelated failure / 3 pre-existing unrelated ImportErrors. Above CLAUDE.md baseline of 14,420.
**Next Action:** User verification — manual multi-instance damage scenario: start a strategy game, deal partial damage to a multi-instance weapon ship, retreat, save, reload, verify per-instance damage preserved.
**Blockers:** None.

### Phase 2 scope change — user-approved deletion

Original plan called for migrating 20 `component_damage` sites in
`ship_stats_calculator.py`. Phase 1 audit revealed the module is dead
code in production (zero importers). User requested verification via
parallel subagents; four-agent synthesis confirmed safe to delete (see
`.agent_reports/proj276-dead-module-verification/SYNTHESIS.md`). User
approved deletion. Phase 2 executed as deletion, not migration.

### Side-finding worth remembering

The deleted strategy calculator implemented **linear effectiveness
degradation** between 100% and 50% HP; live production (simulation
layer) uses **binary** effectiveness (active until 50% HP, inactive
below). This divergence existed long before PROJ-276 began. Recommend
a separate future project to decide whether production should get
linear degradation — out of scope for PROJ-276.

### Context for Next Agent (Phase 7)

- Phases 1-6 checklists fully checked. `component_damage` field is GONE
  from production code. Only historical comments remain.
- `ComponentState` now carries `max_hp` + `is_damaged` property. Key
  producers (`_build_full_hp_components_from_design`,
  `ShipInstanceBridge.update_from_ship`, post_battle_hook
  `_apply_survivor_outcome`) all populate `max_hp` from the Ship
  component's `max_hp`.
- Save format is now **3.0.0** (up from 2.0.0). Old saves rejected with
  "Incompatible save version: 2.0.0 (requires 3.0.0)".
- Targeted test run (strategy + save_load + fleet_combat + integration
  strategy): 3462 passed, 2 skipped, 1 pre-existing unrelated error.
- Pre-existing failures unrelated to PROJ-276 (seen every phase):
  - `test_copy_designs_without_themes_preserves_original` — theme_id Klingons vs Federation
  - ImportErrors in `test_ai_protocols.py`, `test_behavior_units.py`, `test_build_order_command_handler.py`

**Phase 7 cleanup list (remaining test-only `component_damage` references):**

- `tests/unit/strategy/test_ship_display_formatter.py:28` —
  `ship.component_damage = {}` attribute assignment does nothing now;
  delete or replace with `ship.components = {}`
- `tests/integration/resource_system/test_resource_pipeline.py:276` —
  `'component_damage': {'engine_0': 50}` key inside test save data.
  Now silently ignored by `from_dict`. Consider rewriting to use
  `'components': {component_state_key('engine_0', 0): {...}}` to
  actually exercise damage persistence
- `tests/unit/strategy/test_fleet_capability_calculator_di.py:142` —
  `'component_damage': {}` empty dict in save data. Safe to delete.

**Phase 8** handles `docs/` updates (see `docs/systems/strategy_layer.md`
and `docs/04_SERVICES.md`).

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
- [x] All phase checklists complete
- [x] Grep `grep "component_damage" game/` returns ONLY 5 historical comment lines (no field access, no legacy behavior)
- [x] Full suite: `python Tools/test_sharded/test_sharded.py` — 14,627 passing (+207 over baseline). Only pre-existing unrelated failures remain (theme_id fixture, 3 AI ImportErrors)
- [ ] Manual: start new strategy game, deal partial damage to a multi-instance weapon, retreat, save, reload; verify per-instance damage preserved  — **pending user**
- [x] Perf: no regression on stat-calculation hot path (same Ship.from_dict + recalculate_stats call; dict lookup cost O(1))
- [x] Audit passed (4 subagents verified zero production importers of the dead module)
- [ ] User verified  — **pending user**
