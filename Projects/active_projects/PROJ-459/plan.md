# PROJ-459: Strategy data LOC extractions (fleet_serde + planet_gen split + ship_instance re-measure)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-459` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-459 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03a-continue-working (serial on main; user's standing preference — no worktrees)

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 0. Re-measure target files after PROJ-449 + PROJ-451 ship | Complete | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. F-A-008 — extract `Fleet.to_dict` / `Fleet.from_dict` into `fleet_serde.py` | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. F-A-009 — split `planet_gen.py` by sub-concern (or document deferral) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. F-A-007 measurement decision — `ship_instance.py` close-or-spinout | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-19
**Active Phase:** Phase 1 (ready)
**Last Action:** Phase 0 re-measurement complete. PROJ-449 merged at SHA `ebb5c0e7f`; PROJ-451 merged at `893482c04`; PROJ-454 merged at `ab2da0669` (Group B). LOC table: fleet.py 686→693 (+7 from PROJ-451 Task 2.0); planet_gen.py 610→610 (unchanged); ship_instance.py 839→789 (−50 from PROJ-449). Phase 3 provisional verdict: **SPINOUT to PROJ-461** (789 LOC > 500). Phase 1 extraction targets stable at fleet.py:527-664. Phase 2 split candidates identified: moon-generation cluster (~90 LOC) and surface-type-resource cluster (~170 LOC). Findings written to `findings/phase_0_remeasurement.md`.
**Next Action:** Execute Phase 1 — extract `Fleet.to_dict` / `Fleet.from_dict` / `Fleet.resolve_order_references` into `game/strategy/data/fleet_serde.py` modeled on `planet_serde.py`.
**Blockers:** None.

## Overview
Three clean LOC extractions in the strategy-data layer, plus a measurement-only decision on `ship_instance.py`:

1. `game/strategy/data/fleet.py` is currently 686 LOC. `Fleet.to_dict` / `Fleet.from_dict` (~140 LOC at fleet.py:520-655) extracts cleanly into `fleet_serde.py`, modeled directly on the existing `game/strategy/data/planet_serde.py` template from PROJ-372. Target: drop fleet.py to ~545 LOC, just over the 500 ceiling but tractable next-touch.
2. `game/strategy/data/planet_gen.py` is 610 LOC. Procedural body-generation logic with potentially-extractable sub-concerns (atmosphere / surface conditions / orbital arrangement). If a clean axis emerges from the read, split. If not, document the structural reason and defer — do not force a bad cut.
3. `game/strategy/data/ship_instance.py` is currently 839 LOC. The retained shims (kwarg wrapper, @property cluster, the legacy_kwargs translator, plus the 5 high-value TD-06 shims) account for ~360 LOC of the overage. After PROJ-449 retires the wrapper + property shims, re-measure: if under 500, close F-A-007. If over, spin out as its own next-touch project. **Do not attempt the split inside this project.**

Per Codex r4 framing: "F-A-007 should not be smuggled in as a side quest; if it still sits at 839 LOC after job 1, spin it as its own next-touch project."

## Goals
- Close F-A-008 (fleet.py extraction). Land the extraction as a 1-to-1 mirror of `planet_serde.py`'s shape.
- Close F-A-009 (planet_gen.py split), OR document the structural reason for deferring it with a concrete "next-touch" criterion in `decisions.md`.
- Reach an explicit verdict on F-A-007 (ship_instance.py): either close (LOC met) or hand off as a new project (LOC still violated).
- Zero behavior change. Every phase ends with sharded suite green.
- Save-file compatibility unchanged. The extracted `to_dict` / `from_dict` produces byte-for-byte identical output.

## Scope
**In:**
- Phase 1: extract `Fleet.to_dict` + `Fleet.from_dict` + `resolve_order_references` (already delegating to `OrderSerializer`) into `game/strategy/data/fleet_serde.py`. Replace the body of the methods on `Fleet` with 1-line facades calling into the new module.
- Phase 2: split `planet_gen.py` into sub-modules along whichever axis (atmosphere / surface / orbits) the read surfaces as the cleanest cut. If no clean axis exists, document and defer.
- Phase 3: re-measure `ship_instance.py` LOC after PROJ-449 ships. Decide and document.
- Targeted save-load tests as the regression gate (`tests/integration/save_load/`).

**Out:**
- `ship_instance.py` extraction work in this project (explicit Codex r4 directive; spun out if needed).
- Any non-LOC residue in fleet.py, planet_gen.py, or ship_instance.py (e.g., DI-006 fleet rounding, F-A-013 fleet slice snapshot). Those belong to other projects.
- Behavior changes. No save-format changes. No public-API changes.
- Touching the other ~10 strategy-data files (planet.py, empire.py, galaxy.py, etc.) under or near the ceiling. This project is strictly the three named files.

## Dependencies
**Phase-scoped predecessors:**
- **PROJ-451** (Production resource-consumption semantics) — required for **Phase 1** and beyond. Closes the engine-side half of DI-006 / DI-007 and may touch `Fleet.has_cargo_resources` / `consume_cargo_resource` / `production_*` methods (fleet.py:245-315), which sit immediately adjacent to the serialization surface being extracted in Phase 1. Re-measure post-PROJ-451 to confirm the extraction target still cleanly delineates from production-engine concerns.
- **PROJ-449** (Strategy entity wrapper retirement) — required for **Phase 3 only** (ship_instance.py LOC re-measure). PROJ-449 retires the `Planet` / `ShipInstance` legacy-kwarg wrapper + @property shim cluster (F-A-002..F-A-005 + F-C-020). It is the primary driver of the ship_instance.py LOC delta. Phases 1 and 2 can begin once PROJ-451 has landed even if PROJ-449 is still in flight, because they touch `fleet.py` and `planet_gen.py` — neither of which is materially changed by PROJ-449's wrapper deletion. Phase 0 confirms PROJ-451 status as a hard gate, and confirms PROJ-449 status as advisory for Phases 1-2 and hard for Phase 3.

Both deps are Codex r4 jobs 1 and 3. Per Codex: "Sequential. Depends on: `1` and `3`." Per audit feedback (Bucket D, response.md): the PROJ-449 gate is strongly justified for Phase 3 and only weakly justified for Phase 1/2, so the gate is scoped per phase here.

**No worktrees** per user standing preference. Serial execution in main checkout.

## Findings Summary
Source: `Projects/archived_projects/PROJ-444/findings/bucket_a_data_facade_scan.md`. Per-finding entries with current-state verification live in [findings/PROJ-459_findings.md](findings/PROJ-459_findings.md).

| Finding | Severity | File:line | Status | Closure phase |
|---------|----------|-----------|--------|---------------|
| F-A-007 | medium | `game/strategy/data/ship_instance.py:1` (839 LOC) | open (measurement-decision; **not** extracted here) | Phase 3 — close if `<500` after PROJ-449, otherwise spin out as PROJ-461 |
| F-A-008 | low | `game/strategy/data/fleet.py:1` (686 LOC); to_dict :520, from_dict :558, resolve_order_references :657 | open | Phase 1 — extract `fleet_serde.py` mirroring `planet_serde.py` |
| F-A-009 | low | `game/strategy/data/planet_gen.py:1` (610 LOC) | open | Phase 2 — split or document deferral with concrete next-touch criterion |

## Dependencies & Sibling Projects

| This project depends on | What | Why | Phase(s) gated |
|-------------------------|------|-----|----------------|
| PROJ-451 (Production resource-consumption semantics) | Engine-side resource-consumption contract closing DI-006 / DI-007 | `Fleet.has_cargo_resources` / `consume_cargo_resource` / `production_*` (fleet.py:245-315) sit immediately adjacent to the extracted serde surface. Confirms the extraction line still cleanly delineates. | Phase 1, 2, 3 |
| PROJ-449 (Strategy entity wrapper retirement) | `_planet_init_with_legacy_kwargs` + `_ship_instance_init_with_legacy_kwargs` + property/setter clusters retired | Primary driver of `ship_instance.py` LOC delta. Without PROJ-449, Phase 3's verdict is fixed at "spin out" regardless. | Phase 3 only (Phases 1-2 can proceed before this lands) |

| Sibling / downstream projects | Their dependency on PROJ-459 | When unblocked |
|-------------------------------|-------------------------------|----------------|
| PROJ-461 (`ship_instance.py` LOC reduction — conditional, scaffolded by Phase 3 if needed) | depends on **PROJ-459 Phase 3 verdict** | After Phase 3's measurement decides "spin out" |
| PROJ-450 (typed staging-yard substrate) | independent at the project level (different file surfaces) | Runs AFTER PROJ-459 in Group A serial order (collision-resolution reorder) |

Per Codex r4 redesign DAG: PROJ-459 is Job 11, downstream of Job 1 (PROJ-449) and Job 3 (PROJ-451). No other Stage-3 project depends on PROJ-459 directly; F-A-007 spinout is the only conditional downstream.

### Group A serial order (2026-05-19 collision resolution)

Group A executes its 4 projects in this serial order: **PROJ-449 → PROJ-451 → PROJ-459 → PROJ-450**.

This project (PROJ-459) is third. It runs after PROJ-449 + PROJ-451 close (both hard prerequisites) and before PROJ-450 (which carries a sync gate for Group B coordination).

### Doc consolidation rule (cross-group, three-project)

PROJ-457 (Group B), PROJ-459 (this), and PROJ-460 (Group C) all update `docs/01_ARCHITECTURE.md` and `docs/02_PATTERNS.md`. Three-way concurrent doc edits would produce nasty merge conflicts.

**Convention:**
- PROJ-459's plan.md and decisions.md describe doc changes WITHOUT applying them inline during execution.
- When PROJ-459 is complete, record the intended doc additions (`fleet_serde.py` row for the package-map table in `01_ARCHITECTURE.md`; if `planet_gen.py` split happens, the relevant pattern entry in `02_PATTERNS.md`) as a structured "Pending doc consolidation" block in `decisions.md`.
- Whichever of PROJ-457 / PROJ-459 / PROJ-460 **finishes last** is responsible for applying ALL three projects' pending doc additions as a single consolidated edit to `docs/01_ARCHITECTURE.md` + `docs/02_PATTERNS.md`. Read the other two projects' decisions.md "Pending doc consolidation" blocks; merge into one PR-shaped edit.

## Key Files
| Component | File Path | Current LOC (2026-05-19) |
|-----------|-----------|--------------------------|
| Fleet entity | `game/strategy/data/fleet.py` | 686 |
| Fleet serde (new) | `game/strategy/data/fleet_serde.py` | 0 (to be created) |
| Planet generator | `game/strategy/data/planet_gen.py` | 610 |
| Ship instance | `game/strategy/data/ship_instance.py` | 839 (will drop after PROJ-449) |
| Planet serde (template) | `game/strategy/data/planet_serde.py` | 219 (read-only reference) |

Full enumeration in [manifest.md](manifest.md). Consolidated findings live at [findings/PROJ-459_findings.md](findings/PROJ-459_findings.md).

## Related Documents
- [design.md](design.md) — Architecture analysis and design rationale
- [decisions.md](decisions.md) — Full decisions log
- [findings/PROJ-459_findings.md](findings/PROJ-459_findings.md) — F-A-007, F-A-008, F-A-009 carried verbatim from archived PROJ-444 with current status
- Codex r4 redesign source: `AgentCoordination/Scratchpad/Consult/20260519T004841Z_stages-1-2-audit-and-redesign/response.md` (Job 11)

## Phases

### Phase 0: Re-measure target files after PROJ-449 + PROJ-451 ship [Simple]
**Mandatory.** Without re-measurement, scope may be wrong. PROJ-449 (wrapper retirement) and PROJ-451 (production semantics) both touch surfaces that affect fleet.py and ship_instance.py LOC and structure. Phase 0 is the gate that confirms whether each remaining phase is still scoped correctly.

- Verify PROJ-449 status: Complete and merged into main.
- Verify PROJ-451 status: Complete and merged into main.
- Re-measure `fleet.py`, `planet_gen.py`, `ship_instance.py` LOC.
- Re-grep for the extraction targets to confirm `Fleet.to_dict` / `Fleet.from_dict` / `resolve_order_references` still live at expected locations.
- Read `ship_instance.py` end-to-end to confirm which shims actually deleted in PROJ-449 vs. survive.
- Decide: is Phase 1 still ~140 LOC of extraction? Is Phase 3 a close (under 500), spinout (still over), or still uncertain?
- Document the re-measurement table in `findings/phase_0_remeasurement.md`.

**Checkpoint:** `findings/phase_0_remeasurement.md` committed with: PROJ-449 + PROJ-451 status, current LOC table for all three files, extraction-target-location confirmation, Phase 3 verdict pending or final.

### Phase 1: F-A-008 — extract `Fleet.to_dict` / `Fleet.from_dict` into `fleet_serde.py` [Medium]
**Closes F-A-008.** Direct mirror of PROJ-372's planet_serde extraction.

**Characterization-first refactor.** This is a pure no-behavior-change extraction; the standard RED-then-GREEN cycle does not apply because no new behavior is introduced. Per CLAUDE.md's allowance for pure-refactor work, the discipline is characterization-first: write a comprehensive `Fleet` → dict → `Fleet` round-trip test, confirm it passes against current code (captures the current behavior verbatim), THEN extract. The post-extraction test run is the regression gate — any drift between pre- and post-extraction dict output is a real failure.

A new file `tests/integration/save_load/test_fleet_serde_roundtrip.py` will be **created** in Phase 1 (it does not exist at HEAD). Existing fleet-serialization coverage at `tests/unit/strategy/fleet/test_serialization.py` and `tests/integration/save_load/test_roundtrip_fleet.py` serves as adjacent regression coverage but does not duplicate the byte-identical capture-then-replay check the new test owns.

- Create `tests/integration/save_load/test_fleet_serde_roundtrip.py` with the byte-identical capture-then-replay assertion (frozen dict captured pre-extraction, replayed post-extraction).
- Create `game/strategy/data/fleet_serde.py` with `fleet_to_dict(fleet)` and `fleet_from_dict_kwargs(data, registries)` modeled on `planet_serde.py`. The helper returns ONLY the kwargs that `Fleet.__init__` accepts (`fleet_id`, `owner_id`, `location`, `speed`, `component_registry`, `display_name`). `Fleet.__init__` initializes `self.ships`, `self._task_forces`, `self.fleet_policy`, `self.orders`, `self.path` internally; the helper does NOT return a `ships` list. Per-ship deserialization and the post-construction hydration of ships / task_forces / fleet_policy / orders happens in `Fleet.from_dict` AFTER `Fleet(**fleet_from_dict_kwargs(data, registries))` returns. The `registries` argument threads through `fleet_from_dict_kwargs` only insofar as it is needed for validation; the actual `ShipInstance.from_dict(ship_data, registries=registries)` calls run inside `Fleet.from_dict` (or a sibling helper exported from fleet_serde, such as `_deserialize_fleet_ships(ship_data_list, registries)` — decide in-phase and record in `decisions.md`).
- Replace `Fleet.to_dict` body with a 1-line call to `fleet_to_dict(self)`.
- Replace `Fleet.from_dict` body with the split-call shape described above: `Fleet(**fleet_from_dict_kwargs(data, registries))`, then ship hydration, then post-construction reattach (TaskForce / fleet_policy / task_forces / order resolution). Match exactly what's currently in the method.
- Update `Fleet.resolve_order_references` if it needs to move into serde or stay as a Fleet method (depends on what's idiomatic for the planet_serde precedent; verify in Phase 0).
- Verify byte-for-byte save-format identity: a checkpoint Fleet's `to_dict()` produces an identical dict before and after extraction.
- Run sharded suite to verify no regressions.

**Targeted gate:**
```powershell
pytest tests/integration/save_load/ tests/unit/strategy/fleet/test_serialization.py tests/integration/save_load/test_fleet_serde_roundtrip.py -q -n 4
python Tools/test_sharded/test_sharded.py
```

**Checkpoint:** fleet.py drops to ~545 LOC (still slightly over but tractable). fleet_serde.py created at ~150 LOC. Save-format byte-identical. Sharded suite green.

### Phase 2: F-A-009 — split `planet_gen.py` by sub-concern (or document deferral) [Medium]
**Closes F-A-009 OR documents a concrete deferral with criteria.**

Read `planet_gen.py` end-to-end and surface the cleanest split axis. Candidates per F-A-009: atmosphere generation / surface conditions / orbital arrangement. The file is one class (`PlanetGenerator`) with ~13 private methods; surface-flag generation (`_generate_surface_flags`), planet-type determination (`_determine_type`), and resource generation (`_generate_resources`) are obvious slice candidates.

- Read the file in full. Identify the natural axes.
- If a clean axis emerges (e.g., "all atmosphere/surface methods extract to `planet_gen_surface.py`"; the orbital-slots methods stay with `PlanetGenerator`):
  - Create the sibling module(s).
  - Move the methods. If they remain bound to `PlanetGenerator`'s `self` (use `self._image_registry`, mutate shared state), turn them into module-level helpers taking the registry / state as explicit args.
  - Update `PlanetGenerator` to call into the new module(s).
  - Save-format and behavior unchanged (this is generation-time logic, not serialization, but the generated output must be deterministic-given-seed).
- If no clean axis exists (e.g., the methods share state too tightly, or each "subconcern" is <50 LOC and not worth a file):
  - Document the structural reason in `decisions.md` with a concrete next-touch criterion (e.g., "split when atmosphere generation grows past 200 LOC", or "split when a non-orbital generator emerges that doesn't fit into `_create_single_planet`").
  - Mark F-A-009 as "deferred with rationale" in `findings/PROJ-459_findings.md`.

**Targeted gate:**
```powershell
pytest tests/unit/strategy/data/test_planet_gen.py tests/unit/strategy/generation/ -q -n 4
python Tools/test_sharded/test_sharded.py
```

**Checkpoint:** Either (a) planet_gen.py drops below 500 with sibling module(s) created, sharded green, or (b) `decisions.md` carries the deferral entry and `findings/PROJ-459_findings.md` updates F-A-009's status to "deferred with concrete next-touch criterion." Either outcome is acceptable; forcing a bad cut is not.

### Phase 3: F-A-007 measurement decision — `ship_instance.py` close-or-spinout [Simple]
**Measurement and decision only.** Do NOT attempt the split here. Per Codex r4: "if it still sits at 839 LOC after job 1, spin it as its own next-touch project."

- Re-measure ship_instance.py LOC post-PROJ-449 (already done in Phase 0; reconfirm here as a separate explicit gate).
- Read the file to confirm what's left after the wrapper / @property retirement. Specifically, check the 5 high-value TD-06 shims (`create`, `to_dict`, `clone`, `to_ship`, `update_from_ship`) and the inline `design_data` carry-along.
- Verdict:
  - **If LOC < 500:** document in `decisions.md` as "ceiling met after PROJ-449; F-A-007 closed". Update `findings/PROJ-459_findings.md` to "closed via PROJ-449 + re-measurement".
  - **If LOC >= 500:** document the structural residue (which shims remain, which can't be retired without a 910-caller sweep). Spin out a fresh "PROJ-461 ship_instance.py LOC reduction" project in `Projects/active_projects/`. Update `findings/PROJ-459_findings.md` to "spun out as PROJ-461; this project carries F-A-007 only as a measurement-decision".

**Targeted gate:** none (no code changes). Sharded suite green from Phase 1/2 is sufficient.

**Checkpoint:** verdict recorded in `decisions.md` and `findings/PROJ-459_findings.md`. If spinout: PROJ-461 charter exists at `Projects/active_projects/PROJ-461/`.

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Read `docs/` foundation docs (`01_ARCHITECTURE.md`, `02_PATTERNS.md`, `03_CONVENTIONS.md`)
- [ ] Confirm PROJ-449 + PROJ-451 are merged into main
- [ ] Run full test suite: `python Tools/test_sharded/test_sharded.py` — all green (establishes baseline)

### After Each Phase
- [ ] Run targeted gate listed in the phase
- [ ] Run sharded suite — no regression vs baseline
- [ ] Save-load round-trip verified byte-identical (Phase 1 specifically)
- [ ] Update `plan.md` Current State

### Final Verification
- [ ] All 3 production phases checked off (Phase 3 is a decision, not code)
- [ ] Fleet save-format byte-identical pre/post extraction (manual or scripted comparison)
- [ ] `findings/PROJ-459_findings.md` updated with final status per finding
- [ ] Sharded suite green
- [ ] Docs updated if architecture/patterns changed (likely a 1-line update in `docs/02_PATTERNS.md` referencing `fleet_serde.py` as a second instance of the planet_serde pattern)
- [ ] User verified

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] Phase 0 re-measurement done; scope confirmed
- [ ] Phase 1 fleet_serde extraction landed (F-A-008 closed)
- [ ] Phase 2 planet_gen split landed OR deferral documented with criterion (F-A-009 closed or deferred)
- [ ] Phase 3 ship_instance verdict recorded (F-A-007 closed-via-PROJ-449 or spun out as PROJ-461)
- [ ] All tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified
