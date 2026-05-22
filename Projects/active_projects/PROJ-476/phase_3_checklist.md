# Phase 3: Document the tooling-exemption policy + final reconcile + full-suite verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-476 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Record the tooling-exemption policy in Pattern #5, confirm the
guard and doc agree, and verify the full suite. End state: every tooling-screen
`game.strategy.*` import is classified exactly once (UISAFE | tooling-exemption |
live-defer); the transitional `TAIL` parking for these files is cleared.

---

## Tasks

### Task 3.1: Document the tooling-exemption category in Pattern #5 [Simple]
**File:** `docs/02_PATTERNS.md` (Pattern #5)
**Tests:** doc edit; parity covered by guard tests

- [ ] Add a paragraph defining the tooling-exemption category: it covers
      detached pre-session editors, standalone sandbox harnesses, pre-session
      authoring services, and design-editor metadata/catalog loaders that do NOT
      read a live `GameSession`; it is exact-`(file, module, member)` scoped with
      a `category_tag` + reason; it is NOT a folder/subpackage waiver and NOT the
      UI-safe symbol surface (those are immutable pure symbols).
- [ ] Name the four tags (`prebattle-editor`, `sandbox-harness`,
      `race-authoring`, `design-editor`) and point at `_TOOLING_EXEMPTIONS`.
- [ ] State the boundary: live-session/service readers stay facade-routed
      (PROJ-475/477); pure value/enum symbols are UI-safe (PROJ-474).
- [ ] Verify: doc and `_TOOLING_EXEMPTIONS` agree (no symbol both UI-safe and
      tooling-exempt; consistent with the no-misfile test).

### Task 3.2: Doc/guard tag-parity test (concrete, not optional) [Simple]
**Files:** `docs/02_PATTERNS.md`, `tests/static_guards/test_facade_read_path_imports_guard.py`
**Symbol:** new `test_tooling_exemption_tags_match_pattern5`
**Tests:** `pytest tests/static_guards/test_facade_read_path_imports_guard.py -k tooling_exemption_tags`

- [ ] Embed the four category tags in Pattern #5 as a parseable fenced token
      list (one tag per line — NOT prose), mirroring PROJ-474's
      `_UISAFE_SYMBOLS` ↔ Pattern #5 token-list parity approach.
- [ ] Write `test_tooling_exemption_tags_match_pattern5` FIRST: assert the set of
      tags used in `_TOOLING_EXEMPTIONS` equals the parsed Pattern #5 tag token
      list. Confirm it FAILS before the doc fenced block exists.
- [ ] Add the fenced block; confirm the test PASSES. (Per post-flesh review
      Finding 6 — keep wording from drifting while the guard stays green.)
- [ ] Verify: guard module GREEN; doc tags == guard tags.

### Task 3.3: Full static-guard + affected-screen verification [Medium]
**Tests:** `pytest tests/static_guards/ ` then `python Tools/test_sharded/test_sharded.py`

- [ ] Run the full static-guard suite — GREEN (both read-path guards;
      session-read guard unchanged).
- [ ] Run the sharded suite (or at minimum the tooling-screen test modules:
      battle_setup, galaxy_test, race_setup, builder, design_selector) — GREEN.
      No `game/ui/` production code changed, so behavior must be identical.
- [ ] Verify: no net-new `TAIL` entries for tooling files; `git diff` touches
      only the guard file + Pattern #5.

### Task 3.4: End-of-project audit [Medium]
**Tests:** n/a (review)

- [ ] Re-read plan.md Verification checklist; tick each item.
- [ ] Confirm honest-scope claim holds: PROJ-476 codified exemptions only; it did
      NOT migrate any tooling screen or add a DTO surface (there were no live
      reads to migrate).
- [ ] Set `status:awaiting-confirmation`; the user applies `verified` + closes.

**Notes:** [Filled during execution.]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `python Tools/test_sharded/test_sharded.py` GREEN (or scoped equivalent)
- [ ] Pattern #5 documents the tooling-exemption category; guard/doc consistent
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State + Verification
