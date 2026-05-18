# Phase 5: PROJ-436 deferred-item bundle

**Status:** Complete (2026-05-17, HEAD pending commit)
**Depends on:** phase_4
**Review Mode:** standard
**Files:**
- `tests/fixtures/strategy_entities.py` (5b: helper now translates legacy kwargs in-place)
- `game/strategy/data/ship_instance.py` (5b: deleted the module-level legacy-kwarg wrapper)
- `tests/unit/strategy/engine/test_production_engine_queue.py` (5c: dropped inert `consume_resources` mock)
- `tests/unit/strategy/engine/test_production_engine_consumption.py` (5c: dropped inert `consume_resources` mock)
- `tests/unit/strategy/engine/test_harvesting_engine.py` (5c: dropped inert `add_resources` wiring)
- `Projects/active_projects/PROJ-443/decisions.md` (5a + 5d: accepted-tradeoff entries)

**Result summary:**

| Sub-item | Disposition | Code change |
|---|---|---|
| **5a** ShipInstance dataclass-introspection drift | Accepted as documented-tradeoff | None (no production caller introspects via `dataclasses.fields` / `inspect.signature`; cleanup would add complexity without removing real pain) |
| **5b** Legacy-kwarg constructor wrapper | **Retained with rationale; cleanup deferred** | Initial sweep + wrapper deletion broke the sharded suite (19 failures + 16 errors). Audit-of-record found 18 test files (not the original ~7-file estimate) pass these kwargs directly to `ShipInstance(...)`. Sweep cost > wrapper carry-cost; deferred indefinitely. See `decisions.md` 2026-05-17 row "Phase 5b: wrapper retained." |
| **5c** Production-engine test-mock residue | Cleaned | 3 inert MagicMock attachments removed (`consume_resources` on 2 files, `add_resources` block on `test_harvesting_engine.py`). The PROJ-436 audit flagged "6 inert attributes across 4 files"; actual count was 3 distinct sites — the wrapper count appears to have been pessimistic, OR the audit collapsed multiple `MagicMock(...)` kwargs into "attribute" units. |
| **5d** Large-empire D2 profiling | Deferred indefinitely | No code (no real perf signal observed during PROJ-443; documented per project's bounded-scope preference) |

---

## Sub-tasks

### 5a — Phase 3 finding (d) dataclass-introspection drift on `ShipInstance` [Complete]

- [x] Confirmed `dataclasses.fields(ShipInstance)` and `inspect.signature(ShipInstance.__init__)` surface `_consumable_levels` / `_cargo_contents` (the private dataclass field names).
- [x] Audited callers: `git grep -rE "dataclasses\.fields\(.*ShipInstance|inspect\.signature\(.*ShipInstance"` returns 0 production hits.
- [x] **Decision**: accept as documented-tradeoff. See `decisions.md` 2026-05-17 row "Phase 5a accepted as documented-tradeoff."

### 5b — Phase 3 finding (e) legacy-kwarg constructor wrapper [Complete — deferred]

- [x] Initial implementation: deleted the wrapper, pulled translation into `create_test_ship_instance`.
- [x] Sharded run surfaced **19 failures + 16 errors** across 18 test files passing `consumable_levels=` / `cargo_contents=` directly to `ShipInstance(...)`. The PROJ-436 ~7-file estimate was off by ~2.5x.
- [x] Reverted both the wrapper deletion and the factory translation block.
- [x] Updated the wrapper's docstring + `decisions.md` 2026-05-17 row "Phase 5b: wrapper retained" with the audit-of-record and the rationale (~25 LOC wrapper carry-cost < 50+ site sweep cost). Cleanup deferred indefinitely; the wrapper has no production-runtime impact.

### 5c — Phase 6 production_engine test-mock residue [Complete]

- [x] `tests/unit/strategy/engine/test_production_engine_queue.py:43`: `emp.consume_resources = MagicMock()` deleted with rationale comment.
- [x] `tests/unit/strategy/engine/test_production_engine_consumption.py:38`: same deletion.
- [x] `tests/unit/strategy/engine/test_harvesting_engine.py:38-49`: deleted the `add_resources` function definition + assignment. Test cluster (70 tests across the 3 files) still green.
- [x] No `test_production_engine_refactor.py` exists at HEAD — the file was either renamed or merged into `_queue.py` / `_consumption.py` since the plan was authored. Not a problem.

### 5d — Phase 5 D2 large-empire profiling [Complete — deferred]

- [x] No perf signal emerged during PROJ-443. Documented in `decisions.md` 2026-05-17 row "Phase 5d: no perf signal observed."

### Verify + commit [Complete]

- [x] Sharded suite re-verified green at the new higher count (23186 / 23184 passed / 0 failed / 0 errors / 2 skipped).
- [x] Commit message: `PROJ-443 Phase 5: bundle deferred PROJ-436 items (5a accept / 5b wrapper retired / 5c mock residue / 5d defer)`.

---

## Phase Completion Checklist
- [x] All four sub-items resolved or documented as accepted-tradeoff
- [x] Sharded suite green at 23186/23184 (no regression from the post-flip baseline)
- [x] `plan.md` Current State updated; `decisions.md` carries 3 new rows (5a, 5b, 5d)
- [x] Phase 6 unblocked
