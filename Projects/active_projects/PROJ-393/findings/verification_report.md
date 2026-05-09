# PROJ-393 — Verification Report

**Source audit:** `Reviews/results/2026-05-07_220621_legacy-audit/`
**Run date:** 2026-05-08
**Cluster:** Test-injection fallbacks + comment cleanups
**Batch summary:** 11 verified / 0 rejected / 3 uncertain (included) / 2 INFO (included) / 0 out-of-scope (within this bundle)

## Verified

| ID | File | Symbol | Recommendation | Severity |
|---|---|---|---|---|
| LEG-02-002 | `game/run_loop.py:205` | Legacy `handle_input` branch for RESEARCH_TREE/GALAXY_TEST | migrate scenes to `IScene.handle_event` then delete | MINOR |
| LEG-02-003 | `game/strategy/engine/planet_action_engine.py:366` | `'PlanetaryShield'` hardcoded fallback | delete | MINOR |
| LEG-02-004 | `game/strategy/engine/commands/__init__.py:102, ~286, ~297` | `fleet_id: int  # Kept for backward compat` field on 3 commands | migrate_callers_then_delete | MINOR |
| LEG-02-013 | `build_queue_helpers.py:8`, `strategy_ui.py:25` | module-level `ResourceCatalog.from_json()` | replace with lazy init | MINOR |
| LEG-03-002 | `game/simulation/combat/formation.py:357` | comment-only legacy snap reference | delete (comment only) | MINOR |
| LEG-03-003 | `game/strategy/combat/spec_compiler.py:462` | comment-only EnvironmentalEffects reference | delete (comment only) | MINOR |
| LEG-03-004 | `game/strategy/validation/planet_order_validator.py:66-75` | activate `ability_name` fallback | migrate_callers_then_delete | MINOR |
| LEG-03-005 | `game/strategy/validation/planet_order_validator.py:113-125` | deactivate `ability_name` fallback | migrate_callers_then_delete | MINOR |
| LEG-03-006 | `game/ui/panels/build_queue_drag_handler.py:210-212` | test-fallback branch when callback None | migrate_callers_then_delete | MINOR |
| LEG-03-007 | `game/ui/screens/empire_build_queue_window.py:428-429` | test-fallback branch when facade None | migrate_callers_then_delete | MINOR |
| LEG-04-004 | `game/strategy/engine/order_handlers/transfer_branches.py:107-108` | Legacy/Default first-species fallback | delete (after fleet-cargo-species TODO resolved) | MINOR |

## Rejected

None for this bundle.

## Uncertain (resolved)

| ID | Symbol | Question | User decision |
|---|---|---|---|
| LEG-02-006 | `format_planet_info()` `view is None` branch (15 LOC) | Some callers still pass None (uncolonized planets + pre-PROJ-289 tests). Include or exclude? | **Include** — audit callers, migrate, delete branch |
| LEG-03-023 | 6 Combat Lab instance vars on `BattleScreen` (NOQA, tracked for PROJ-270 Phase 10) | PROJ-270 is archived. Reclaim now or wait? | **Include** — PROJ-270 archived, reclaim now |
| LEG-03-024 | `_LEGACY_PATTERN = re.compile(r"Comp_(\d+)\.\w+$")` in `sprites.py` | Whether dead depends on asset scan. Include or exclude? | **Include** — task starts with asset scan, deletes if no matches |

## INFO (resolved)

| ID | Symbol | User decision |
|---|---|---|
| LEG-02-005 | Historical `# legacy` comment in `save_game_service.py:68` | **Include** — clean up alongside the rest |
| LEG-02-017 | Stale `# PROJ-258` docstring tag at `context.py:13` | **Include** — PROJ-372 is current; update or remove |

## Out of Scope

| ID | Reason |
|---|---|
| LEG-02-001 (`Game.running` flag) | UNCERTAIN-excluded by user — test-bypass backdoor still needed. Recorded in shared [bundling_decisions.md](bundling_decisions.md). |

## Implementation Notes

### Phase 1, Task 1.1 (LEG-02-017) — `PROJ-258` references in `game/context.py`
- Docstring tag at original line 13 (`PROJ-258: Initial implementation as wrapper around existing singletons.`) was the stale-state comment the user wanted cleaned up. **Deleted.**
- Two other `PROJ-258` references remain and are intentionally preserved:
  - Line ~41: docstring inside `get_default_planet_habitability_service` saying "modders may override … (PROJ-258 pattern)" — documents the architectural pattern name; not stale.
  - Line ~162: comment at the start of the `set_default_*` block in `create_production` describing why all module-level references are set in lockstep — current implementation context.
- The checklist's literal grep verification (`grep -rn "PROJ-258" game/context.py" returns zero hits`) is too aggressive. The intent was the stale docstring tag, which is gone.
