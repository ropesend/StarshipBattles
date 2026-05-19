# PROJ-454: Engine + Services Obsolete-Surface Retirement

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-454` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-454 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** legacy serial-on-main (matches PROJ-443/444 standing preference; no worktrees).

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. F-B-004 — Retire `effect_ability_metadata.py` (131 LOC, 2 callers) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. F-B-005 — Retire `component_inspector.py` (~68 caller sites — 52 imports + 16 patch targets — across ~31 files; sized up from `~45` after codex audit 2026-05-19) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. F-B-017 — Unwind `OrderProcessor.process_*` facade reshape; delete legacy typed result dataclasses (68 sites / 12 files; sized up from `~15 / 7` after codex audit 2026-05-19) | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. F-B-018 — Remove "legacy field" framing on `OrderExecutionResult` (fields become live unified surface post-Phase-3 facade unwind; delete specific fields ONLY if Phase 4 audit shows they're dead) | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-05-17
**Active Phase:** All phases complete; awaiting end-of-project codex audit
**Last Action:** Phase 4 complete. Refreshed `OrderExecutionResult` docstring + dropped the 5 inline `# X legacy field` comments. Per Codex r4 redesign, kept all 5 fields flat (every field has live producers + consumers post-Phase-3; per-handler subclasses would complicate caller ergonomics). Also refreshed one stale docstring reference in `handlers/base.py:423`. Sharded first run had 2 errors (no detail captured); per protocol §13 the retry ran clean (23363/23363) — flagging as a flake. Phase 4 is documentation/comment-only edits; no behaviour changes that could have caused real regressions.
**Next Action:** Dispatch PROJ-454 end-of-project codex audit per protocol §10.
**Blockers:** None.

## Checkpoint Log

### 2026-05-17 — phase-2-complete-checkpoint
- **Done so far**: PROJ-453 fully closed (Phases 1+2, merged at `82b751fe0`). PROJ-454 Phases 1 + 2 closed. Phase 1: deleted `effect_ability_metadata.py` shim and rewrote 2 callers to use `get_ability_metadata(name).effect` (the planning doc's "drop-in import swap" claim was wrong — canonical API has different verb name + nested shape). Phase 2: ~68-site sweep retiring `component_inspector.py`; routine work but large. Net: -2 shim modules (~200 LOC) + 4 test files renamed/deleted.
- **Key decisions**: (1) Phase 1 deviation documented in decisions.md (no compat shim in the canonical module). (2) Task 2.9 — deleted drift-gate test rather than refactor as re-emergence guard. Both decisions enforced CLAUDE.md Rule 4 (no compat shims) more strictly than the original plan anticipated.
- **Open threads**: Phase 3 (F-B-017 facade unwind) and Phase 4 (legacy-field reframing) still pending.
- **Next action**: PROJ-454 Phase 3 Task 3.1 — call-site inventory for `OrderProcessor.process_join_fleet` / `process_colonize` / `process_transfer` (68 sites / 12 files).
- **Cross-group state observed**: `origin/main` = `82b751fe0` (post-PROJ-453 merge). `origin/group-a` advanced to `d531b430a`; `origin/group-c` exists. No `_doc_consolidation/` files on origin/main yet.

### 2026-05-17 — project-454-start
- **Done so far**: PROJ-453 closed and merged (`82b751fe0`). Group B serial gate cleared for PROJ-454.
- **Key decisions**: Following Phase 1 → 2 → 3 → 4 ordering strictly (Phase 1 deletes a 131-LOC shim, Phase 2 is the 68-site `component_inspector` sweep, Phase 3 is the 68-site facade unwind, Phase 4 reframes `OrderExecutionResult` legacy fields).
- **Open threads**: None.
- **Next action**: Phase 1 Task 1.1.
- **Cross-group state observed**: origin/main = `82b751fe0`. Group A pushed updates (`d531b430a` on group-a); Group C published `origin/group-c`.

## Overview

Two service-layer re-export shims + one engine-layer facade reshape retire in this project:

1. **F-B-004 — `effect_ability_metadata.py`** (131 LOC). Module is a thin shim over `ability_metadata.py` per PROJ-429's intentional deferral; 3 caller sites today (2 production + 1 test). The deferral was always "until all downstream callers are ready"; that's now true. Migrate the 3 callers, delete the module.
2. **F-B-005 — `component_inspector.py`** (67 LOC). Re-exports 16 symbols from `component_abilities.py` + `component_layers.py` per PROJ-433's intentional file-split deferral. **~68 caller sites across ~31 distinct files** (codex audit 2026-05-19 corrected from the original `~45` estimate): 52 `from game.strategy.services.component_inspector import ...` statements and 16 `patch('game.strategy.services.component_inspector.X', ...)` test sites. The largest mechanical sweep in this project — each caller's import line gets re-pointed; **no behaviour changes**. The 16 `patch(...)` targets need careful migration to patch the canonical module path instead.
3. **F-B-017 — OrderProcessor facade reshape**. `OrderProcessor.process_join_fleet` / `process_colonize` / `process_transfer` still wrap `OrderExecutionResult` into the legacy typed result dataclasses (`JoinFleetResult` / `ColonizeResult` / `TransferResult`). The handlers themselves already match the unified Protocol per PROJ-438 Phase 6; only the facade-side compensation survives. Migrate **68 caller sites across 12 test files** (count corrected by codex audit 2026-05-19 from the original `~15 sites / 7 files`) to read `OrderExecutionResult` directly; delete the three legacy facade methods + the three legacy result dataclasses.
4. **F-B-018 — `OrderExecutionResult` legacy fields**. With F-B-017 done, the 5 per-handler "legacy fields" on `OrderExecutionResult` (`merged`, `cancelled`, `colonized`, `planet_name`, `amount_transferred`) become the live fields. Phase 4 removes the "legacy field" framing and decides whether any are now truly dead.

Together these close ≈300 LOC of intentional deferral-shim from PROJ-429 / PROJ-433 / PROJ-368.

## Goals

- Delete `game/strategy/services/effect_ability_metadata.py` and its single test file.
- Delete `game/strategy/services/component_inspector.py` and the static-guard test file.
- Migrate every live caller of the two retired modules to the canonical `ability_metadata.py` / `component_abilities.py` / `component_layers.py` import paths.
- Delete `OrderProcessor.process_join_fleet` / `process_colonize` / `process_transfer` plus the three legacy result dataclasses `JoinFleetResult` / `ColonizeResult` / `TransferResult`.
- Migrate every live caller to read `OrderExecutionResult` directly via `execute_action_order(...)` or via the handler registry.
- Drop the 5 legacy compensation fields from `OrderExecutionResult` where dead post-F-B-017; otherwise document the unified-result design decision.
- Surface no new entries in `discovered_issues/log.jsonl` from this project's work.

## Scope

**In (this project owns these files):**

**Phase 1 — F-B-004:**
- `game/strategy/services/effect_ability_metadata.py` (delete)
- `game/strategy/services/effect_ability_display.py` (1 import migrated)
- `game/strategy/services/system_effects_collector.py` (1 import migrated)
- `tests/unit/strategy/services/test_effect_ability_metadata.py` (delete or rewrite against `ability_metadata.py`)

**Phase 2 — F-B-005:**
- `game/strategy/services/component_inspector.py` (delete)
- ~30 production caller files across `game/strategy/data/`, `game/strategy/engine/`, `game/strategy/services/ability_sources/`, `game/strategy/validation/`, `game/ui/screens/`
- ~15 test caller files including patch-target rewrites
- `tests/unit/strategy/services/test_component_inspector_surface.py` (static drift gate — adapt to new surface modules or delete)

**Phase 3 — F-B-017:**
- `game/strategy/engine/order_processor.py` (delete `JoinFleetResult` / `ColonizeResult` / `TransferResult` dataclasses + the three `process_*` methods)
- ~15 caller files (mostly tests in `tests/integration/colonization/`, `tests/integration/strategy/`, `tests/unit/strategy/engine/`)

**Phase 4 — F-B-018:**
- `game/strategy/engine/order_handlers/base.py` (refresh / shrink the 5 legacy-field block on `OrderExecutionResult`)

**Out (PROJ-452 owns):** catalog-driven resource surface work.

**Out (PROJ-453 owns):** annotation polish and stale docstrings in the same engine/services file set. Phase 1/2 of PROJ-454 may incidentally touch the same files PROJ-453 touches; coordinate via the manifest cross-bucket section.

**Out (PROJ-455 owns):** planet-FMS engine-mediated behavioural coverage.

**Out of scope entirely:**
- Refactoring UI behaviour in `game/ui/` while migrating `component_inspector` imports. The Phase 2 contract is "edit only the import statement; do NOT refactor UI behaviour" — even when the surrounding UI code is obviously stale, it's not in this project's territory.
- Any work on `OrderProcessor.process_instant_orders` or `OrderProcessor.execute_action_order`. Those are the canonical-direction methods that handlers already implement against the unified protocol; only the three legacy `process_*` shims retire.
- Any change to `SuperweaponResult` (mentioned in `OrderExecutionResult`'s docstring at base.py:43-44). Superweapon dispatch is on a separate facade per `SuperweaponOrderProcessor`; out of scope.

## Findings Summary

Full report: [findings/PROJ-454_findings.md](findings/PROJ-454_findings.md) (4 entries: F-B-004, F-B-005, F-B-017, F-B-018 verbatim from bucket B scan + verified against current code 2026-05-19).

| Finding | Severity | Effort | Caller Count |
|---------|----------|--------|--------------|
| F-B-004 (effect_ability_metadata retirement) | low | small | 3 (2 production + 1 test) |
| F-B-005 (component_inspector retirement) | low | medium-large | **~68 sites** (52 `from ... import` + 16 `patch(...)` targets) across ~31 distinct files (engine, UI, validators, tests) — codex audit 2026-05-19 corrected from the original `~45 sites` estimate |
| F-B-017 (OrderProcessor facade reshape) | medium | medium-large | 68 call sites across 12 test files (codex audit 2026-05-19 corrected from `~15 sites / 7 files`) |
| F-B-018 (OrderExecutionResult legacy fields) | low | tiny (post F-B-017) | 0 (after F-B-017 deletes the reshape callers) |

## Key Files

| Component | File Path | Phase |
|-----------|-----------|-------|
| effect_ability_metadata shim | `game/strategy/services/effect_ability_metadata.py` | 1 (delete) |
| effect_ability_metadata canonical home | `game/strategy/services/ability_metadata.py` | 1 (target of migrated imports) |
| effect_ability_metadata callers | `effect_ability_display.py`, `system_effects_collector.py:42`, `tests/unit/strategy/services/test_effect_ability_metadata.py` | 1 |
| component_inspector shim | `game/strategy/services/component_inspector.py` | 2 (delete) |
| component_inspector canonical homes | `game/strategy/services/component_abilities.py` (Surface A), `game/strategy/services/component_layers.py` (Surface B) | 2 (target of migrated imports) |
| component_inspector callers — production | See findings/PROJ-454_findings.md "F-B-005 caller list (production)" | 2 |
| component_inspector callers — tests | See findings/PROJ-454_findings.md "F-B-005 caller list (tests)" | 2 |
| OrderProcessor facade | `game/strategy/engine/order_processor.py:39-143` | 3 (delete legacy methods + dataclasses) |
| OrderProcessor callers | See findings/PROJ-454_findings.md "F-B-017 caller list" | 3 |
| OrderExecutionResult | `game/strategy/engine/order_handlers/base.py:36-56` | 4 (refresh legacy-field framing) |

Full enumeration in [manifest.md](manifest.md).

## Phase Breakdown

### Phase 1 — F-B-004: retire `effect_ability_metadata.py` (3 caller sites) [Small]

Mechanical migration. The shim re-exports `EFFECT_ABILITY_METADATA` (tuple), `find_metadata`, `is_known_effect_ability`, `all_owner_aware_scopes`, and the `EffectAbilityMetadata` dataclass. Every symbol has an equivalent in `ability_metadata.py`. Migrate the 3 callers to import from there; delete the shim.

The test file `tests/unit/strategy/services/test_effect_ability_metadata.py` is the trickiest single decision: delete it outright (the canonical module has its own tests) or rewrite against `ability_metadata.py` (potentially adding tests `ability_metadata.py` doesn't already have). Phase 1 Task 1.3 walks through the decision.

### Phase 2 — F-B-005: retire `component_inspector.py` (~68 caller sites across ~31 files) [Large]

**The largest mechanical sweep in this project.** The shim re-exports 16 symbols, split across two destination modules:

- `component_abilities.py` (Surface A) — `get_component_abilities`, `extract_abilities_from_component`, `get_component_type`, `get_component_threshold`, `iterate_design_components`, `iter_facility_ability_entries`, `ship_has_ability`, `find_ship_with_ability`, `count_ability`, `list_ship_abilities`, `get_ability_list`, `has_warp_capability` (12 symbols)
- `component_layers.py` (Surface B) — `iter_components_by_layer`, `damaged_components_by_layer`, `count_damaged_components`, `lookup_design_max_hp` (4 symbols)

**Critical caller-list scaffolding (per the project brief):**

```bash
# Discover all live callers (production + tests):
git grep -nE "from game\.strategy\.services\.component_inspector import|game\.strategy\.services\.component_inspector\." game/ tests/

# Discover patch-target sites (need the canonical module path after migration):
git grep -n "game.strategy.services.component_inspector\." tests/
```

The 2026-05-19 codex re-audit yielded ~68 total references across ~31 distinct files:
- 52 `from ... import` sites across ~28 files (production + tests)
- 16 `patch('game.strategy.services.component_inspector.X', ...)` sites across 4 test files (the bulk in `test_fleet_report_filters.py`, which has 11 `component_inspector.` references = 6 inline imports + 5 `patch(...)` calls — confirmed 2026-05-19)
- File breakdown still ~30 production files + ~7 test files; the test-side patch-target migration is the larger half by site count

**Some callers will be in `game/ui/`** (e.g., `fleet_data_source.py`, `fleet_report_filters.py`, `planet_abilities_controller.py`, `strategy_detail_fmt.py`, `strategy_detail_formatter.py`, `strategy_fleet_command_router.py`). **Edit only the import statement; do NOT refactor UI behaviour** — UI shim retirement is a separate Codex r4 redesign job (#8) outside PROJ-454's scope.

For each caller, the recipe is:
1. Identify which of the 16 symbols are imported.
2. Per symbol, look up which destination module owns it (the `component_inspector.py` re-export at lines 28-47 is the canonical map).
3. Replace the import path on the line. If both Surface A and Surface B symbols are imported in the same statement, split into two imports.
4. For test files using `patch('game.strategy.services.component_inspector.X', ...)`, repoint to the canonical module path: `patch('game.strategy.services.component_abilities.X', ...)` or `patch('game.strategy.services.component_layers.X', ...)`.

Once all 68 sites migrate, delete `component_inspector.py` AND the static-guard test `tests/unit/strategy/services/test_component_inspector_surface.py` (the latter exists specifically to gate the shim; with the shim retired it becomes a drift-against-deleted-code test). **Before deleting the static-guard test, run `rg -n "test_component_inspector_surface\." game/ tests/` to confirm no other code imports symbols FROM that test module — if it exports any helper used elsewhere, deletion breaks them.**

### Phase 3 — F-B-017: unwind `OrderProcessor.process_*` facade reshape [Medium-Large]

Three steps:

1. **Audit callers** of `process_join_fleet` / `process_colonize` / `process_transfer`. The 2026-05-19 codex re-audit corrected the call-site count: **68 sites across 12 test files** (the original audit cited `~15 sites / 7 files`, an undercount of more than 4×). Sites span `tests/integration/colonization/`, `tests/integration/strategy/`, `tests/unit/strategy/`, and `tests/unit/strategy/engine/`. Each call receives one of the three legacy result dataclasses (`JoinFleetResult` / `ColonizeResult` / `TransferResult`). The full inventory lives at the top of `phase_3_checklist.md` and Tasks 3.3 through 3.8f cover every file.
2. **Migrate callers** to read `OrderExecutionResult` directly via either:
   - `processor.get_handler(OrderType.JOIN_FLEET).execute_action_order(fleet, empire, galaxy, ...)` — returns `OrderExecutionResult`.
   - Or, for the integration tests where ergonomics matter, expose a public test-helper if needed (decision deferred to Phase 3 itself).
   
   After migration, each call site reads `result.merged` / `result.cancelled` / `result.colonized` / `result.planet_name` / `result.success` / `result.amount_transferred` / `result.message` from the `OrderExecutionResult` directly. These attributes already exist on `OrderExecutionResult` (the legacy fields at `base.py:46-55`).
3. **Delete** the three legacy result dataclasses + the three `process_*` methods + the corresponding imports in `tests/unit/strategy/engine/test_colonize_population.py:22` and `tests/unit/strategy/engine/test_transfer_order.py:15`.

### Phase 4 — F-B-018: drop / refresh 5 legacy fields from `OrderExecutionResult` [Tiny]

After Phase 3 deletes the facade reshape and all callers read `OrderExecutionResult` directly, the 5 "legacy fields" on `OrderExecutionResult` (`merged`, `cancelled`, `colonized`, `planet_name`, `amount_transferred`) **become the live fields**, not legacy. Phase 4's actual job is therefore not "delete fields" but **"remove the legacy-field framing"**:

- Drop the inline comments at `base.py:51-55` that label them "legacy field"
- Decide whether to leave them as flat fields on the unified result (current shape) or extract per-handler payload subclasses (future work). Recommendation per Codex r4 redesign: **leave flat**. The 5-field overhead on the unified result is a small price for caller simplicity, and the per-handler payload-subclass refactor is a separate design call.

If after Phase 3 some handler outputs are genuinely unused (e.g., `amount_transferred` only set by `TransferHandler` and only read by transfer tests), Phase 4 may shrink the dataclass; otherwise it's a documentation-only refresh.

Phase 4's deliverable is documented in `decisions.md` regardless of the field-shrink outcome.

## Related Documents

- [design.md](design.md) — architecture rationale + parallelism contract with PROJ-453
- [decisions.md](decisions.md) — decisions log
- [findings/PROJ-454_findings.md](findings/PROJ-454_findings.md) — full finding text (verbatim from bucket B scan) + caller-list scaffolding
- [`Projects/archived_projects/PROJ-445/findings/bucket_b_engine_services_scan.md`](../../archived_projects/PROJ-445/findings/bucket_b_engine_services_scan.md) — source scan
- [`AgentCoordination/Scratchpad/Consult/20260519T004841Z_stages-1-2-audit-and-redesign/response.md`](../../../AgentCoordination/Scratchpad/Consult/20260519T004841Z_stages-1-2-audit-and-redesign/response.md) — Codex r4 redesign that produced this project (job #6)

## Dependencies & Sibling Projects

**Group B serial order (coordinator-confirmed 2026-05-19): `PROJ-453 → PROJ-454 → PROJ-456 → PROJ-457`.** PROJ-454 is the second project Group B's run agent executes. PROJ-453 must complete before PROJ-454 starts.

| Project | Status | Relationship |
|---------|--------|--------------|
| **PROJ-453** (engine + services surface polish) | Active — **Group B predecessor** | **HARD predecessor in Group B serial order.** Per the coordinator's resolution of the soft `order_processor.py` collision: PROJ-453 lands its `__init__` annotation first, then PROJ-454 deletes the `process_*` facade methods. The sites are line-disjoint within `order_processor.py` so the diff is clean. Codex r4 redesign: "PROJ-454 depends on PROJ-453 (preferred — polish should land first to reduce noise during the retirement sweeps)." |
| **PROJ-456** (UI shim retirement) | Active — **Group B successor** | Runs AFTER PROJ-454 in Group B serial order. No file overlap with PROJ-454's scope. |
| **PROJ-457** (UI structural debt extractions) | Active — **Group B successor** | Runs LAST in Group B serial order, after PROJ-456. No file overlap with PROJ-454. |
| PROJ-452 (catalog-driven resource surfaces) | Active — **Group C** | Disjoint file set; runs in parallel from another agent's series. |
| PROJ-449 (strategy entity wrapper retirement) | Active — **Group A** | `game/strategy/data/ship_instance.py` is shared (PROJ-454 touches lines 635/654/663 for component_inspector imports; PROJ-449 deletes legacy-surface @property blocks at 237-262 + 786-833). Sites are line-disjoint; whichever runs second rebases easily. |
| PROJ-450 (typed staging-yard substrate) | Active — **Group A** | `tests/unit/strategy/engine/test_order_processor_transfer.py` is shared (PROJ-454 Phase 3 migrates 10 `process_transfer(...)` call sites; PROJ-450 Phase 4 owns the same 10 sites in a different concern). Codex Group 2 audit identified this as a collision; coordinator resolution 2026-05-19: **Group A re-ordered its serial so PROJ-450 runs LAST**, which means PROJ-454 lands first and PROJ-450 rebases. |
| PROJ-455 (Planet-FMS engine-mediated behavioural coverage) | Active — **Group A/C** | Read-only dependency on `OrderProcessor` (PROJ-455 invokes `OrderProcessor.get_handler` only; PROJ-454 does not touch `get_handler`). No conflict. |

Phase ordering within PROJ-454 is strict: Phase 1 → Phase 2 → Phase 3 → Phase 4 (each phase's tests verify the previous phase's deletion landed cleanly).

## Verification

- [ ] All four phase checklists complete
- [ ] `game/strategy/services/effect_ability_metadata.py` deleted
- [ ] `game/strategy/services/component_inspector.py` deleted
- [ ] `OrderProcessor.process_join_fleet` / `process_colonize` / `process_transfer` deleted
- [ ] `JoinFleetResult` / `ColonizeResult` / `TransferResult` dataclasses deleted
- [ ] `git grep -n "effect_ability_metadata" game/ tests/` returns zero matches (excluding docs/comments and archived projects)
- [ ] `git grep -n "component_inspector" game/ tests/` returns zero matches (same exclusion)
- [ ] `git grep -nE "process_join_fleet|process_colonize|process_transfer\b" game/ tests/` returns zero matches
- [ ] `git grep -nE "JoinFleetResult|ColonizeResult|TransferResult" game/ tests/` returns zero matches
- [ ] Full sharded suite green (`python Tools/test_sharded/test_sharded.py`)
- [ ] No new entries in `AgentCoordination/discovered_issues/log.jsonl` from this project's work
- [ ] Audit passed (Codex end-of-project consult per the standing workflow)
- [ ] User verified
