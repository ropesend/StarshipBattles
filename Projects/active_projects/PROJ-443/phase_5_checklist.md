# Phase 5: PROJ-436 deferred-item bundle

**Status:** Not Started
**Depends on:** phase_4
**Review Mode:** standard
**Files (planned):** see `phase_state.json` phase_5.planned_files

**Objective:** Clean up the four small follow-up items deferred by PROJ-436's Codex consults. Each is its own commit; order can be flexible.

---

## Sub-tasks

### 5a — Phase 3 finding (d) dataclass-introspection drift on `ShipInstance`

**Background:** PROJ-436 Phase 3f renamed `consumable_levels` and `cargo_contents` to `_consumable_levels` and `_cargo_contents` dataclass fields plus `@property` accessors. `dataclasses.fields(ShipInstance)` and `inspect.signature(ShipInstance.__init__)` now expose the private names. Cosmetic — no production caller affected.

- [ ] Read `game/strategy/data/ship_instance.py` post-Phase-3f shape and PROJ-436 Phase 3 closeout commit (`c3a39858c`).
- [ ] Decide: clean up via a more clever dataclass pattern, OR document as accepted in `decisions.md`.
- [ ] Commit.

### 5b — Phase 3 finding (e) legacy-kwarg constructor wrapper

**Background:** PROJ-436 Phase 3f added a module-level wrapper translating `ShipInstance(consumable_levels=...)` / `ShipInstance(cargo_contents=...)` kwargs into the private-field names. Functional but a code smell. ~24 sites in ~7 test files.

- [ ] `grep -rn "ShipInstance(.*consumable_levels=\|cargo_contents=" tests/` to enumerate sites.
- [ ] Migrate each test fixture: construct `ShipInstance(...)` without the legacy kwargs, then call `ship._resource_mgr.replace_levels(...)` / `ship._cargo_mgr.replace_cargo(...)` (or whichever Phase 3b method matches) to set the initial state.
- [ ] Delete the wrapper in `ship_instance.py`.
- [ ] Sharded gate.
- [ ] Commit.

### 5c — Phase 6 production_engine test-mock residue

**Background:** PROJ-436 Phase 6 audit found 6 inert `MagicMock(add_resources=..., consume_resources=..., resource_pool=...)` attribute attachments for Empire methods that were deleted in Phase 5. Production never invokes them.

- [ ] `grep -rn "add_resources\|consume_resources\|_fleet_resource_pool" tests/unit/strategy/engine/test_production_engine_*.py tests/unit/strategy/engine/test_harvesting_engine.py` to find the sites.
- [ ] Delete the attribute attachments. Some test files may need a mock-setup refactor; minimize churn.
- [ ] Commit.

### 5d — Phase 5 D2 large-empire profiling (conditional)

**Background:** Phase 5's `Empire.resource_pool` pure-aggregation query was net-zero cost in the analytical case (the deleted summand was always an empty dict). No production stress test has shown a hot path.

- [ ] If a real perf signal has emerged since PROJ-436 close, profile on a 100+ colony fixture; record at `findings/d2_profiling.md`.
- [ ] If still no signal, document in `decisions.md` as "no signal observed; deferred indefinitely."
- [ ] Commit.

---

## Phase Completion Checklist
- [ ] All four sub-items resolved or documented as accepted-tradeoff
- [ ] Sharded suite green
- [ ] `plan.md` + `phase_state.json` updated
- [ ] Phase 6 unblocked
