# PROJ-449: Strategy entity wrapper retirement (Planet + ShipInstance legacy-kwarg + property shim cluster)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-449` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-449 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03a-continue-working (serial on `main`, no worktrees — per standing user preference)

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 0. Pre-flight audit (rg counts, PROJ-443 Phase 5b carry-over verification) | Complete | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. Migrate `tests/fixtures/strategy_entities.py` (4 sites; +3-line scope creep in `test_roundtrip_ships.py`) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Sweep direct call sites in tests + rewrite `planet_from_dict_kwargs` | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Delete `_planet_init_with_legacy_kwargs` + 3 Planet @property/@setter pairs | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Delete `_ship_instance_init_with_legacy_kwargs` + 2 ShipInstance @property/@setter pairs | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Drop `IShipInstance.cargo_contents` caveat + tighten `IFacility.consumable_levels` | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Profile `Empire.resource_pool`; add cached aggregation only if hot | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-05-18
**Active Phase:** Phase 2 (ready to start)
**Last Action:** Phase 1 complete. `tests/fixtures/strategy_entities.py` lines 318, 320, 425 migrated to private kwargs (line 140 stays public per F-A-012 deferral). Scope crept by 3 lines into `test_roundtrip_ships.py:46/56/62` because the wrapper raises TypeError on duplicate public+private kwargs; decisions.md captures the rationale. Sharded suite 23368/23368 GREEN.
**Next Action:** Execute Phase 2 — sweep all direct call sites in tests + rewrite `planet_from_dict_kwargs`. Phase 2 sweep set shrinks by 1 file (the 3 Phase-1 absorbed lines).
**Blockers:** None.
**Context for Next Agent:** Audit landed clean PROCEED on both axes. Phase 1 should be a small, focused commit; sharded suite must stay green at 23368 tests after Phase 1.

## Checkpoint Log

### 2026-05-18 — project-449-start + phase-0-complete
- **Done so far**: Group A session-start (branched `group-a` from `main`; pre-flight §14 verified; baseline sharded 23368/23368 green). PROJ-449 Phase 0 audit complete.
- **Key decisions**: F-A-012 deferral keeps PlanetaryFacility `consumable_levels=` kwarg out of scope. MagicMock factories (`make_cargo_mock_ship`, `_make_cargo_ship`, etc.) excluded — they never reach real `ShipInstance.__init__`. Attribute-setter sites (e.g., `create_mock_ship_instance` in `turn_engine/conftest.py:58`) are in scope because Phase 4 deletes the @setter property shim.
- **Open threads**: None.
- **Next action**: Phase 1 — `tests/fixtures/strategy_entities.py` lines 318/320/425 → private kwargs.
- **Cross-group state observed**: No `group-b` or `group-c` branches present on origin at branch creation; Group A is first to start.

## Overview
Retire the two legacy-kwarg constructor wrappers (`_planet_init_with_legacy_kwargs` and `_ship_instance_init_with_legacy_kwargs`) and the five matching `@property`/`@setter` clusters they exist to support. Migrate `tests/fixtures/strategy_entities.py` (the largest fixture site), `planet_serde.py:160-162` (the load-bearing serializer site), and sweep every direct call site in tests. Complete F-C-014 by dropping the "not read-only in absolute terms" caveat from `IShipInstance.cargo_contents` once the concrete-class setters are gone. Profile `Empire.resource_pool` against a late-game save and add cached aggregation only if a real perf signal emerges.

## Goals
- Delete `_planet_init_with_legacy_kwargs` (`game/strategy/data/planet.py:398-420`) and the three Planet `@property`/`@setter` pairs that share its rationale (`stockpile`, `max_stockpile`, `staging_yard` at `planet.py:224-262`).
- Delete `_ship_instance_init_with_legacy_kwargs` (`game/strategy/data/ship_instance.py:809-833`) and the two ShipInstance `@property`/`@setter` pairs (`consumable_levels`, `cargo_contents` at `ship_instance.py:237-262`).
- Migrate `tests/fixtures/strategy_entities.py` (4 known sites: facility `consumable_levels=` line 140, ship `consumable_levels=` line 318 + `cargo_contents=` line 320, planet `stockpile=` line 425) and every test that constructs `ShipInstance(...)` / `PlanetaryFacility(...)` / `Planet(...)` with the legacy kwarg spellings.
- Rewrite `planet_serde.planet_from_dict_kwargs` (`game/strategy/data/planet_serde.py:130-162`) to emit the post-rename private kwargs (`_stockpile=`, `_max_stockpile=`, `_staging_yard=`).
- Drop the F-C-014 caveat in `IShipInstance.cargo_contents` (`game/core/protocols/strategy_domain.py:208-233`) and the parallel F-C-013 caveat in `IFacility.consumable_levels` (`game/core/protocols/strategy_domain.py:146-166`).
- Profile `Empire.resource_pool` (`game/strategy/data/empire.py:228-249`) under late-game save; add the cached aggregation pattern from PROJ-293 only if profiling shows the walk is a hotspot.
- Maintain green sharded suite at each phase transition.

## Scope

**In Scope:**
- `game/strategy/data/planet.py` — wrapper + 3 property/setter pairs (`224-262`, `398-420`).
- `game/strategy/data/ship_instance.py` — wrapper + 2 property/setter pairs (`237-262`, `809-833`).
- `game/strategy/data/planet_serde.py` — `planet_from_dict_kwargs` rewrite (`130-162`).
- `game/core/protocols/strategy_domain.py` — drop F-C-014 caveat on `IShipInstance.cargo_contents` (`208-233`) and tighten F-C-013 framing on `IFacility.consumable_levels` (`146-166`).
- `game/strategy/data/empire.py` — optional caching for `resource_pool` (`228-249`) gated on profiling.
- `tests/fixtures/strategy_entities.py` — 4 known call sites (verify count in Phase 0).
- All direct call sites surfaced by Phase 0 audit (estimated 18+ files for `consumable_levels=` / `cargo_contents=`, plus the Planet kwarg sites under `stockpile=` / `max_stockpile=` / `staging_yard=` if any).
- Sharded suite green at every phase boundary.

**Out of Scope:**
- `Planet._staging_yard` substrate widening (`List[Dict[str, Any]]` → `List[CarriedVehicle | DropPod]`) — that is **PROJ-450**, which depends on this project's Phase 3.
- `ProductionEngine._apply_resource_consumption` bool-return handling and the RESOURCE_SHORTAGE UX gap — that is **PROJ-451**.
- Catalog-driven resource surfaces (DI-2026-05-18-003/004/005) — Codex r4 job 4.
- `ship_instance.py` 500-LOC ceiling violation (F-A-007, currently 839 LOC) — Codex r4 explicit follow-up; "if it still sits at 839 LOC after job 1, spin it as its own next-touch project".
- Any UI shim retirement (Codex r4 jobs 8/9/10).
- **F-A-012 facility constructor-kwarg rename.** `PlanetaryFacility.consumable_levels` is still a public dataclass field (F-A-012's generic consumable API landed in May 2026 but the constructor kwarg was not renamed). Renaming to `_consumable_levels` would be a separate sweep across every `PlanetaryFacility(...)` test site plus a serde-key reconciliation. If a future project takes this on, it should split as its own work item — PROJ-449 only retires the Planet + ShipInstance wrappers and the matching property clusters.

## Findings Summary
Source: `Projects/archived_projects/PROJ-444/findings/bucket_a_data_facade_scan.md` and `Projects/archived_projects/PROJ-446/findings/bucket_c_ui_core_tests_scan.md`. Per-finding entries with current-state verification land in [findings/PROJ-449_findings.md](findings/PROJ-449_findings.md).

| Finding | Severity | File:line | Status |
|---------|----------|-----------|--------|
| F-A-002 | medium | `planet.py:398-420` + `planet_serde.py:160-162` | open |
| F-A-003 | low | `ship_instance.py:787-833` | open (was deferred by PROJ-443 Phase 5b) |
| F-A-004 | low | `planet.py:224-262` | open |
| F-A-005 | low | `ship_instance.py:237-262` | open |
| F-A-011 | low | `empire.py:228-249` | open (deferred D2; profile-gated) |
| F-C-014 | medium | `strategy_domain.py:208-233` | partially-resolved (annotation narrowed PROJ-446 Phase 2; concrete setter still exists) |
| F-C-020 | low | `tests/fixtures/strategy_entities.py:140,318,320` | open (Codex r3 flagged 4th site at line 425) |

## Key Files
| Component | File Path |
|-----------|-----------|
| Planet kwarg wrapper | `game/strategy/data/planet.py:398-420` |
| Planet property shims | `game/strategy/data/planet.py:224-262` |
| Planet serde reconstruction | `game/strategy/data/planet_serde.py:130-162` |
| ShipInstance kwarg wrapper | `game/strategy/data/ship_instance.py:809-833` |
| ShipInstance property shims | `game/strategy/data/ship_instance.py:237-262` |
| IShipInstance cargo_contents protocol | `game/core/protocols/strategy_domain.py:208-233` |
| IFacility consumable_levels protocol | `game/core/protocols/strategy_domain.py:146-166` |
| Empire.resource_pool | `game/strategy/data/empire.py:228-249` |
| Test fixture (largest single migration site) | `tests/fixtures/strategy_entities.py:140, 318, 320, 425` |

Full enumeration per phase in [manifest.md](manifest.md).

## Phase Breakdown

### Phase 0: Pre-flight audit — gate on call-site count
Run a fresh `rg` audit for every legacy-kwarg spelling and the legacy property-name write paths. Pin the actual file counts in `findings/phase_0_audit.md`. Confirm or revise the Phase-1/Phase-2 file lists. Verify PROJ-443 Phase 5b's audit-of-record finding (18 files for the ShipInstance side) is still accurate. **Gate:** if the audit reveals dramatically more sites than expected (e.g. >40 files), pause and surface to user before continuing — the wrapper retention rationale in PROJ-443 Phase 5b decisions.md was sized for ~18 files. **No code changes.**

### Phase 1: Migrate `tests/fixtures/strategy_entities.py`
Translate the 3 ShipInstance / Planet legacy-kwarg fixture sites to private-kwarg spellings. **Note (2026-05-19 codex audit, see decisions.md row):** `PlanetaryFacility.consumable_levels` is still a public dataclass field — F-A-012's generic consumable API landed but the constructor kwarg was NOT renamed (`game/strategy/data/planetary_facility.py:32`, deprecated fuel wrappers at `:203-217`). The Phase-1 facility-site (line 140) keeps the public `consumable_levels=` kwarg; only ShipInstance + Planet sites move to private kwargs:
- `create_test_facility` (line 140): keep `consumable_levels={"fuel": 50.0, "energy": 100.0}` as-is (PlanetaryFacility constructor kwarg unchanged — see scope note below).
- `create_test_ship_instance` (lines 318, 320): `consumable_levels={...}` → `_consumable_levels={...}`, `cargo_contents={"minerals": 10}` → `_cargo_contents={"minerals": 10}`.
- `create_test_empire` (line 425): `stockpile=dict(seed_pool)` → `_stockpile=dict(seed_pool)`.

Phase-1 standalone changes only — wrappers stay in place so this phase is independently green. Sharded suite must remain green.

### Phase 2: Sweep direct call sites in tests + rewrite `planet_from_dict_kwargs`
Migrate all direct call sites discovered by Phase 0. For each test file (Phase 0 audit gives the canonical list), translate the legacy kwarg names to private spellings, OR use the manager API where the test intent is "establish initial state" rather than "exercise the constructor". Rewrite `planet_from_dict_kwargs` (`planet_serde.py:130-162`) to emit `_stockpile=`, `_max_stockpile=`, `_staging_yard=` and drop the legacy `data.get("resources", {})` fallback at line 156 (F-A-025 cleanup, free-rider). Sharded suite green at end of phase. Wrappers still live; their bodies are now unreached by tests.

### Phase 3: Delete `_planet_init_with_legacy_kwargs` + 3 Planet property/setter pairs
RED: delete the wrapper assignment at `planet.py:420` and the 3 `@property`/`@setter` blocks at `planet.py:224-262`. Sharded suite confirms zero callers remain (Phase 2 already migrated them). Update `planet_serde.planet_to_dict` (`planet_serde.py:53-55`) to read directly from `_stockpile` / `_max_stockpile` / `_staging_yard` instead of routing through the now-deleted properties. **Closes F-A-002 + F-A-004.** This phase frees the `planet.py` surface so **PROJ-450 Phase 1** can begin clean substrate work.

### Phase 4: Delete `_ship_instance_init_with_legacy_kwargs` + 2 ShipInstance property/setter pairs
RED: delete the wrapper assignment at `ship_instance.py:833` and the 2 `@property`/`@setter` blocks at `ship_instance.py:237-262`. Sharded suite confirms zero callers remain. **Closes F-A-003 + F-A-005.** Watch the `ship_instance.py` LOC — current 839 drops by ~25 LOC for the wrapper + ~25 LOC for the properties, landing around 789. Still over the 500-LOC ceiling. Note in decisions.md that the Codex r4 follow-up (job 11 trigger condition) applies: if LOC sits above 750, the file split is a next-touch project, not a side-quest here.

### Phase 5: Drop `IShipInstance.cargo_contents` caveat + tighten `IFacility.consumable_levels`
Rewrite the docstring for `IShipInstance.cargo_contents` (`strategy_domain.py:208-233`) to drop the "**not** read-only in absolute terms" caveat — Phase 4 deleted the concrete-class setter, so `Mapping[str, int]` is now read-only end-to-end. Update `IFacility.consumable_levels` (`strategy_domain.py:146-166`) docstring to reflect F-C-013's "kept-as-dict by deliberate design" status without referring to the wrapper that no longer exists. **Completes F-C-014.**

### Phase 6: Profile `Empire.resource_pool`; add cached aggregation only if hot
Run a profiling pass under a late-game fixture save (the largest available). If `Empire.resource_pool` shows >5% of frame time in UI-driven flows, add the cached-with-explicit-invalidation pattern from PROJ-293: invalidate cache on `Planet.add_to_stockpile` / `consume_from_stockpile` / `IPlanetMutator.set_stockpile_amount` and on `Empire.add_colony` / `remove_colony`. If profiling shows no signal, document "no perf signal observed; deferred indefinitely" in decisions.md and close the finding without code change. **Closes F-A-011 either way.**

## Related Documents
- [design.md](design.md) — design rationale (wrapper-deletion sequencing).
- [decisions.md](decisions.md) — decisions log.
- [findings/PROJ-449_findings.md](findings/PROJ-449_findings.md) — consolidated findings with current-state verification.
- [manifest.md](manifest.md) — file manifest grouped by phase + production/test/doc type.
- Codex r4 redesign: `AgentCoordination/Scratchpad/Consult/20260519T004841Z_stages-1-2-audit-and-redesign/response.md` (job 1 row).
- Archived bucket scan: `Projects/archived_projects/PROJ-444/findings/bucket_a_data_facade_scan.md` (F-A-002/003/004/005/011 source).
- Archived bucket scan: `Projects/archived_projects/PROJ-446/findings/bucket_c_ui_core_tests_scan.md` (F-C-014/020 source).
- PROJ-443 carry-over rationale: `Projects/active_projects/PROJ-443/phase_5_checklist.md` + decisions.md "Phase 5b: wrapper retained" row 2026-05-17.

## Dependencies & Sibling Projects

| This project depends on | What | Why |
|-------------------------|------|-----|
| (none) | none | Phase 0 / 1 / 2 are independent of other Stage-3 work |

| Sibling projects | Their dependency on PROJ-449 | When unblocked |
|------------------|------------------------------|----------------|
| PROJ-450 (typed staging-yard substrate) | depends on **PROJ-449 Phase 3** | After Planet wrapper + property deletion lands, `planet.py` is clean for substrate work |
| PROJ-451 (production resource-consumption) | independent | Can run in parallel |
| PROJ-459 (strategy data LOC extractions) | depends on **PROJ-449 completion (Phase 3 drives ship_instance.py LOC delta)** + **PROJ-451 completion (production-resource adjacency)** | Per Codex r4: PROJ-459 is downstream of both. PROJ-449 Phase 3 hard-gates PROJ-459 Phase 3 only; Phases 1-2 of PROJ-459 only need PROJ-451. |

### Group A serial order (2026-05-19 collision resolution)

Group A executes its 4 projects in this serial order: **PROJ-449 → PROJ-451 → PROJ-459 → PROJ-450**.

PROJ-450 was reordered from third-place to last-place because it has hard test-file collisions with PROJ-454 (Group B, `test_order_processor_transfer.py`) and PROJ-456 (Group B, `test_transfer_dialog_characterization.py`). Running PROJ-450 after upstream Group B work lands lets us rebase once cleanly rather than twice noisily. PROJ-450's Phase 0 carries an explicit sync gate that waits for both Group B projects to mark `Status: Complete` before Phase 1 begins.

## Verification
- [ ] Phase 0 pre-flight audit: count pinned in `findings/phase_0_audit.md`
- [ ] Phase 1: `tests/fixtures/strategy_entities.py` migrated; sharded suite green
- [ ] Phase 2: all direct call sites swept; `planet_from_dict_kwargs` rewritten; sharded suite green
- [ ] Phase 3: `_planet_init_with_legacy_kwargs` + 3 property/setter pairs deleted; sharded suite green
- [ ] Phase 4: `_ship_instance_init_with_legacy_kwargs` + 2 property/setter pairs deleted; sharded suite green
- [ ] Phase 5: `IShipInstance.cargo_contents` caveat dropped; `IFacility.consumable_levels` docstring updated
- [ ] Phase 6: `Empire.resource_pool` profiled (cache added IF hot, otherwise documented)
- [ ] Full sharded suite green at the new (lower) test count after wrapper deletion
- [ ] Audit passed (end-of-project Codex consult per standing workflow)
- [ ] User verified
