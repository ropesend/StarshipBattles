# Phase 3: Test seam strengthen (R7) [optional]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-317 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Retire `_proj315_color` / `_proj315_strike` private
test attributes; replace with assertions that read pygame_gui's
rendered output. Prevents future "test passes but visual feature
doesn't ship" regressions like R2.

**This phase is optional.** Phases 1+2 deliver all correctness fixes.
Phase 3 is a test-strength upgrade and can ship later if pygame_gui's
text-element introspection API proves brittle.

---

## Tasks

### Task 3.1: Audit current `_proj315_*` test reads [Simple]
**File:** `tests/unit/ui/panels/test_ship_detail_panel.py`
**Tests:** N/A (audit only).

- [ ] Grep for `_proj315_color` and `_proj315_strike` references in
  `tests/`. Tally the count and list every assertion. Expected: ~10–15
  references across the `TestComponentStatusSection` class.
- [ ] For each reference, classify: (a) "asserts a specific colour
  tier was chosen" (replaced by R2-style rendered-output read), (b)
  "asserts strike was applied" (replaced by an assertion about the
  strike-overlay UIImage existence), (c) "asserts colour absence /
  default" (replaced by reading the rendered styling tree). Document
  the breakdown in **Notes** below.

**Notes:**

---

### Task 3.2: Choose the rendered-output assertion strategy [Medium]
**File:** N/A (decision documented in `decisions.md`).
**Tests:** N/A.

- [ ] Spike each strategy in priority order (see `design.md` §R7):
  1. Read pygame_gui's text-element internals
     (`label.text_box_layout` or equivalent).
  2. Pixel-sample at a known character cell.
  3. Hybrid intent + minimal pixel-sample.
- [ ] Pick the deepest-stable approach. Append a decisions.md row
  documenting the choice and why.
- [ ] Write one prototype test using the chosen approach. Confirm it
  passes against the post-Phase-1 colour-aware code AND fails when
  the colour is reverted to default. (Run the failure case in a
  scratch branch, do NOT commit the regression.)

**Notes:**

---

### Task 3.3: Migrate every `_proj315_*` assertion [Medium]
**File:** `tests/unit/ui/panels/test_ship_detail_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_ship_detail_panel.py`

- [ ] Replace each tagged assertion identified in Task 3.1 with the
  rendered-output assertion chosen in Task 3.2.
- [ ] Delete the `_proj315_color = color` and
  `_proj315_strike = strike` assignments in `_build_instance_row`
  (`ship_detail_panel.py` ~line 589–590) once no test reads them.
- [ ] Verify: targeted test suite green; no test references
  `_proj315_*` anywhere in `tests/`.

**Notes:**

---

### Task 3.4: Validate against full sharded suite [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run the full sharded suite. Expected: same total as end of
  Phase 2 (the test count is unchanged; assertions move from private
  attrs to rendered output).
- [ ] If pixel-sampling tests prove flaky across shards, reduce
  sampling tolerance or fall back to text-element introspection.

**Notes:**

---

### Task 3.5: Update PROJ-315 `decisions.md` row 31 [Simple]
**File:** `Projects/active_projects/PROJ-315/decisions.md`
**Tests:** None.

- [ ] PROJ-315 `decisions.md` row 31 documents the
  `_proj315_color` / `_proj315_strike` test-only seam. Append a brief
  note: "Retired in PROJ-317 Phase 3 — test seam was honest at plan
  time but let R2 ship undetected (see PROJ-317 audit log). New
  tests assert against rendered output."
- [ ] Update PROJ-317 `plan.md` Audit Log row 1 with the resolution
  note.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked.
- [ ] Update status at top of this file to `Complete`.
- [ ] Update plan.md phase table row to `Complete`.
- [ ] Update plan.md Current State to "Project Complete".
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-317 3`.

## If this phase is deferred
- [ ] Update plan.md phase table row to `Deferred`.
- [ ] Add a row to PROJ-317 `decisions.md` documenting the deferral
  (with reason — e.g., "pygame_gui text-element API too brittle for
  reliable assertion in this version; revisit when upgrading
  pygame_gui").
- [ ] Update plan.md Current State to "Project Complete (Phase 3
  deferred)".
