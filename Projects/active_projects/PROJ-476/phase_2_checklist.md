# Phase 2: Add the `_TOOLING_EXEMPTIONS` category + move tooling residue out of `TAIL`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-476 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Turn the comment-only `TAIL` parking of the tooling imports into a
first-class, machine-checkable `_TOOLING_EXEMPTIONS` category in
`tests/static_guards/test_facade_read_path_imports_guard.py`, with a no-misfile
invariant and a positive control, using the authoritative triple set from
Phase 1. Strict TDD: failing tests first.

---

## Tasks

### Task 2.1: Failing no-misfile invariant test [Medium]
**File:** `tests/static_guards/test_facade_read_path_imports_guard.py`
**Symbol:** new `test_tooling_exemptions_are_disjoint_from_uisafe_and_tail`
**Tests:** `pytest tests/static_guards/test_facade_read_path_imports_guard.py -k disjoint`

- [x] Write the test FIRST. It asserts: (a) the `(module, member)` projection of
      `_TOOLING_EXEMPTIONS` is disjoint from `_UISAFE_SYMBOLS`; (b) the
      `(file, module, member)` set of `_TOOLING_EXEMPTIONS` is disjoint from the
      residual `TAIL`/`CLUSTER`/`FLEETCAP` triples. Each import classified once.
- [x] Run it — confirm it FAILS (`_TOOLING_EXEMPTIONS` does not yet exist →
      NameError / empty-set assertion failure). Record the failure.
- [x] Verify: failure is the expected "category not yet defined" state.

### Task 2.2: Failing positive-control test [Medium]
**File:** `tests/static_guards/test_facade_read_path_imports_guard.py`
**Symbol:** new `test_tooling_exemption_allows_exact_triple_not_folder`
**Tests:** `pytest tests/static_guards/test_facade_read_path_imports_guard.py -k tooling_exemption`

- [x] Write the test FIRST. Assert: a known tooling triple (e.g.
      `battle_setup_state.py` · `game.strategy.data.fleet` · `Fleet`) is ALLOWED
      via `_TOOLING_EXEMPTIONS`; AND a synthetic NON-exempt live import in a
      tooling-dir file (e.g. a fake `GameSession` import in a path NOT in
      `_TOOLING_EXEMPTIONS`) is STILL FLAGGED — proving the category is
      exact-triple scoped, not a folder waiver.
- [x] Run it — confirm it FAILS (category absent). Record the failure.
- [x] Verify: failure is expected.

### Task 2.3: Add `_TOOLING_EXEMPTIONS` + wire the matcher [Medium]
**File:** `tests/static_guards/test_facade_read_path_imports_guard.py`
**Symbol:** `_TOOLING_EXEMPTIONS`, `_violations_in_file`
**Tests:** `pytest tests/static_guards/test_facade_read_path_imports_guard.py`

- [x] Add `_TOOLING_EXEMPTIONS` (exact `(file, module, member)` + `category_tag`
      ∈ {`prebattle-editor`,`sandbox-harness`,`race-authoring`,`design-editor`} +
      reason) populated from the Phase 1 authoritative set.
- [x] Extend the matcher (`_violations_in_file` / its allowlist check) to treat a
      `(file, module, member)` present in `_TOOLING_EXEMPTIONS` as allowed,
      alongside the existing `_UISAFE_SYMBOLS` and transitional-allowlist checks.
- [x] Run 2.1 + 2.2 — confirm they now PASS.
- [x] Verify: the existing positive-control tests
      (`test_import_classifier_positive_controls`,
      `test_matcher_flags_live_domain_imports_when_not_allowlisted`) still pass.

### Task 2.4: Move the tooling residue triples out of `TAIL` [Medium]
**File:** `tests/static_guards/test_facade_read_path_imports_guard.py`
**Symbol:** `_IMPORT_ALLOWLIST` (`TAIL` block) → `_TOOLING_EXEMPTIONS`
**Tests:** `pytest tests/static_guards/test_facade_read_path_imports_guard.py`

- [x] Delete the Phase-1-authoritative tooling triples from the `TAIL` comment
      block (they now live in `_TOOLING_EXEMPTIONS`). Update the module docstring
      `TAIL` category note to point at the new category.
- [x] Prune any tooling triple whose live import no longer exists post-gate
      (e.g. the `race_setup/screen.py` `RaceRandomizer` test-seam if removed).
- [x] Run the full guard module — confirm GREEN (every tooling import still
      classified exactly once; the directory scan passes).
- [x] Verify: no tooling residue remains in the `TAIL` comment block.

**Notes (execution 2026-05-22):** TDD followed strictly. 2.1 + 2.2 written
first; both FAILED with `NameError: _TOOLING_EXEMPTIONS not defined` (recorded).
Then added `_TOOLING_EXEMPTIONS` (30 5-tuples) + `_TOOLING_EXEMPTION_TRIPLES`
projection + matcher wiring (both bare-`import` and `from...import` paths).
Moved all 30 tooling triples out of `_IMPORT_ALLOWLIST` TAIL (left a one-line
PROJ-476 breadcrumb at each removal site) and rewrote the module-docstring TAIL
note. `race_setup/screen.py:28` RaceRandomizer test-seam is STILL live (noqa
F401) → kept, not pruned. Full guard module: **349 passed** (directory scan +
no-misfile + both positive controls + all pre-existing PROJ-472/474/475 tests).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/static_guards/test_facade_read_path_imports_guard.py` GREEN
- [x] No-misfile + positive-control tests pass; no tooling residue in `TAIL`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
