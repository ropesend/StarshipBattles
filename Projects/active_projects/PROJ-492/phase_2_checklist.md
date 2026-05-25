# Phase 2: HLP-004 _make_fleet 37-file sweep (exact word-boundary match)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-492 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate 37 local `_make_fleet` / `make_fleet` / `_make_mock_fleet` (EXACT word boundary) definitions to consume the canonical `_make_mock_fleet` helper at `tests/conftest.py`. Triage signature variation; rename rather than force-merge for semantically-different fleet helpers.

**Scope clarification per audit Finding 3:** files defining sibling helpers like `_make_fleet_pair`, `_make_fleet_at`, `_make_fleet_with_ship`, `_make_fleet_mock`, `_make_fleet_controller_with_galaxy` are OUT OF SCOPE — they're different families. See manifest.md "Excluded from Phase 2" table.

**Mechanical pattern:** for each file, classify as A/B/C/D per design.md, then:
- A: delete local, import canonical
- B: delete local, import canonical (canonical superset works)
- C: rewrite call sites to canonical signature, delete local, import canonical
- D: rename local to `_make_<purpose>_fleet`, document intent; do NOT force-merge

---

## Tasks

### Task 2.1: Audit canonical _make_mock_fleet signature
**File:** `tests/conftest.py`
**Tests:** none — read-only

- [x] Record the canonical signature in this checklist:
  ```
  def _make_mock_fleet(<params>) -> <return type>:
  ```
- [x] Note all optional kwargs and their defaults.

### Task 2.2: Triage pass — classify all 37 files (exact match only)
**Output:** `findings/triage_results.md` (new)

- [x] For each file in manifest.md Phase 2 list (37 files, exact match), open it, compare local signature to canonical, classify as A/B/C/D.
- [x] For each file in manifest.md "Excluded from Phase 2" table, verify the helper is truly sibling (different name suffix or different shape). If a file is actually exact-match `_make_fleet`/`make_fleet`/`_make_mock_fleet`, move to the included list.
- [x] Record results in `findings/triage_results.md` with the format:
  ```
  ### tests/path/to/file.py — Category X
  Local signature: `def _make_fleet(...)`
  Diff vs canonical: <text>
  Action: <delete-and-import | rewrite-call-sites | rename-to-_make_X_fleet>
  ```

### Task 2.3: Category A migrations (identical signature)
**Tests:** `pytest <affected files>` after each batch

- [x] Migrate each Category A file: delete local, add canonical import, verify.
- [x] Work in batches of ~5 files; run tests after each batch.

### Task 2.4: Category B migrations (canonical-superset signature)
**Tests:** `pytest <affected files>` after each batch

- [x] Same as Task 2.3 — local omitted optional kwargs are filled by canonical defaults.

### Task 2.5: Category C migrations (divergent signature, rewrite call sites)
**Tests:** `pytest <affected files>` after each batch

- [x] For each Category C file, rewrite call sites in tests to use canonical kwarg names/defaults, then delete local.
- [x] Verify after each file (don't batch — higher regression risk).

### Task 2.6: Category D — rename for clarity
**Tests:** `pytest <affected files>` after each batch

- [x] For each Category D file, rename `_make_fleet` → `_make_<purpose>_fleet` (e.g. `_make_cargo_fleet`, `_make_order_fleet`).
- [x] Add docstring explaining why this isn't the canonical.
- [x] Update call sites within the file.
- [x] Verify: tests pass.

### Task 2.7: Final sweep
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] `grep -rl "def _make_fleet\b\|def make_fleet\b\|def _make_mock_fleet\b" tests/` should return only `tests/conftest.py` (canonical) — Category D renames removed the exact-match collision.
- [x] Full test suite passes.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] LOC reclaimed recorded in plan.md (expect ~250-350 LOC across 37 files)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3

_Source: PROJ-479 Phase 6 Task 6.4. See [findings/source_review.md](findings/source_review.md)._
