# Phase 5: Minor sweep (m1, m4-m13, plus typo fixes)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-292 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Sweep the 11 Minor findings from the dual audit. Each task below is independent and can be skipped if the user de-prioritizes — phase completion only requires the explicitly-checked items.

---

## Tasks

### Task 5.1: m17 — Fix `projects_index.md` line-1 typo [Simple]
**File:** [Projects/projects_index.md](Projects/projects_index.md)
**Tests:** None (trivial)

- [ ] Open the file. Line 1 reads `w# Projects Index` (stray `w`). Change to `# Projects Index`.

**Notes:** Pre-existing typo. Trivial fix.

### Task 5.2: m1 — Document the asymmetric `update_planet` semantics [Simple]
**File:** [game/ui/panels/planet_report_panel.py](game/ui/panels/planet_report_panel.py)
**Tests:** None (doc-only)

- [ ] Open `update_planet`. Add to its docstring:
  ```
  Note on kwarg-fallback semantics: `view` is overwritten unconditionally
  on every call (PROJ-289 policy). `empire` and `race_registry` use
  None-sentinel fallback (PROJ-290 policy) — passing None preserves the
  previous values from construction time. This asymmetry is intentional:
  `view` changes per-planet, while empire/registry change per-session.
  Callers that switch planets without changing empire pass only `view`.
  ```
- [ ] Verify by re-reading.

**Notes:** Doc-only. No behaviour change.

### Task 5.3: m4 — Wrap `total_upkeep` with MappingProxyType [Medium]
**File:** [game/strategy/facade/dto/colony_demographic_view.py](game/strategy/facade/dto/colony_demographic_view.py)
**Tests:** `pytest tests/unit/strategy/facade/test_colony_demographic_view.py -v`

- [ ] Add `from types import MappingProxyType` to the top of the file.
- [ ] Add a `__post_init__` method to `ColonyDemographicView`:
  ```python
  def __post_init__(self):
      # m4: enforce read-only contract on total_upkeep
      object.__setattr__(self, 'total_upkeep', MappingProxyType(dict(self.total_upkeep)))
  ```
  (Frozen dataclasses require `object.__setattr__` to bypass the frozen guard during __post_init__.)
- [ ] Add a test: `test_total_upkeep_is_immutable` — assert `view.total_upkeep['x'] = 1` raises TypeError.
- [ ] Run the file's tests — green.

**Notes:**

### Task 5.4: m5 — Enforce species largest-first sort in DTO `__post_init__` [Medium]
**File:** [game/strategy/facade/dto/colony_demographic_view.py](game/strategy/facade/dto/colony_demographic_view.py)
**Tests:** `pytest tests/unit/strategy/facade/test_colony_demographic_view.py -v`

- [ ] In the same `__post_init__` from Task 5.3, add:
  ```python
  # m5: enforce largest-first ordering invariant in the DTO itself
  sorted_species = tuple(sorted(self.species, key=lambda s: s.count, reverse=True))
  object.__setattr__(self, 'species', sorted_species)
  ```
- [ ] Add test: `test_species_sorted_in_dto_constructor` — construct DTO with species in arbitrary order, assert post-construction order is largest-first.
- [ ] Run tests — green.

**Notes:**

### Task 5.5: m6 — Add warning when economy_config falls back [Simple]
**File:** [game/strategy/facade/strategy_session_facade.py](game/strategy/facade/strategy_session_facade.py)
**Tests:** `pytest tests/unit/strategy/facade/ -v`

- [ ] Find `_resolve_economy_config`. Add `logger.warning("session has no economy_config; falling back to get_default_economy_config()")` immediately before the fallback return.
- [ ] If a logger isn't already imported, add `import logging; logger = logging.getLogger(__name__)`.
- [ ] Run tests — green (the warning may surface in test logs but shouldn't fail anything).

**Notes:**

### Task 5.6: m7 — Document tie-break in uncolonized habitability [Simple]
**File:** [game/ui/screens/strategy_detail_fmt.py](game/ui/screens/strategy_detail_fmt.py)
**Tests:** None (doc-only)

- [ ] Find `format_uncolonized_habitability_for_empire`. Add to docstring:
  ```
  Tie-break note: equal habitability scores are sorted alphabetically by
  display name (Python's stable sort + alphabetical input ordering). If
  insertion-order is preferred (matches colonization order), pass the
  empire.resident_species() result without the alphabetical pre-sort.
  ```
- [ ] No behaviour change.

**Notes:**

### Task 5.7: m8 — Verify integration tests run on sharded runner [Simple]
**File:** [Tools/test_sharded/test_sharded.py](Tools/test_sharded/test_sharded.py)
**Tests:** Visual inspection + `python Tools/test_sharded/test_sharded.py` to confirm

- [ ] Read the sharded runner. Look for `tests/integration/` references.
- [ ] If absent, add it to the test discovery path. If present, document confirmation in your task notes.
- [ ] Run the sharded suite — confirm the integration tests are picked up.

**Notes:**

### Task 5.8: m9 — UI assembly test for `_build_projection_grid` [Medium]
**File:** [tests/unit/ui/panels/test_planet_report_panel.py](tests/unit/ui/panels/test_planet_report_panel.py)
**Tests:** `pytest tests/unit/ui/panels/test_planet_report_panel.py::TestProjectionGridAssembly -v`

- [ ] Add a new test class `TestProjectionGridAssembly`.
- [ ] Test 1: `test_correct_label_count_for_n_resources`. Mock `UILabel`. Call `_build_projection_grid` with a view containing 3 resources. Assert `UILabel` was called `1 + (1+5)*3 + 1` times (or whatever the actual count formula is — count: header label + per-row (resource_label + 5 cells) + optional stockpile summary). Check the actual implementation for the exact count.
- [ ] Test 2: `test_no_overlapping_label_rects`. Same mock. Capture all `relative_rect=Rect(...)` arguments. Assert no two rects overlap (same x, y, w, h or any overlap).
- [ ] Run tests — green.

**Notes:** Closes my-review M9 finding.

### Task 5.9: m10 — Write the deferred-manual-smoke checklist for the user [Simple]
**File:** `Projects/active_projects/PROJ-292/MANUAL_SMOKE_CHECKLIST.md` (NEW)
**Tests:** None (doc-only)

- [ ] Create the file. Aggregate the deferred manual smokes from PROJ-283 Phase 5 Task 5.7, PROJ-284 Verification, PROJ-289 Phase 3 Task 3.3, PROJ-290 manual checks, PROJ-291 Phase 4 Task 4.5, and PROJ-292 Phase 6 Task 6.4 (forward-link). Format as a single durable checklist the user can run in one sitting before signing off PROJ-283..292.

**Notes:**

### Task 5.10: m12 — Verify shim retired post-PROJ-291 [Simple]
**Tests:** `grep -rn "population_food_resource" game/`

- [ ] Run the grep. Expected: zero (or only the property definition itself if PROJ-291 left it for label-resolution callers).
- [ ] If the grep returns hits in production code, document them in decisions.md as accepted vs. follow-up.

**Notes:** PROJ-291 Phase 3 Task 3.5 should have cleared this. Phase 5 verifies.

### Task 5.11: m13 — Re-grep doc claim about `format_signed_float` formatting [Simple]
**File:** [docs/systems/strategy_layer.md](docs/systems/strategy_layer.md)
**Tests:** None (doc-only)

- [ ] Open the doc. Find the claim "format_signed_float(rate * 100, 1) + '% / turn'" or similar.
- [ ] Run `grep -rn "format_signed_float" game/ui/screens/strategy_detail_fmt.py`. Compare actual call shape to the doc's claim.
- [ ] If the doc is stale, update it to match the actual code.

**Notes:**

### Task 5.12: Targeted regression suite [Simple]
**Tests:** `pytest tests/unit/ui/ tests/unit/strategy/facade/ -q`

- [ ] Both suites green.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done (or explicitly skipped per user de-prioritization):
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
