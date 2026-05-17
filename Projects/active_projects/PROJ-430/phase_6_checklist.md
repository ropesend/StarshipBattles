# Phase 6: Documentation sync

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-430 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_5
**Review Mode:** lightweight
**Files (planned):**
- `docs/systems/strategy_layer.md`
- `Projects/active_projects/PROJ-309/findings/strategy_session_facade_decomposition.md`
- `docs/03_CONVENTIONS.md` (conditional)

**Objective:** Bring documentation in line with the post-TD-08 architecture. Update the strategy-layer doc's facade-boundary section, append the new target shape to the PROJ-309 findings file (do not overwrite history), and optionally tighten the conventions doc.

---

## Tasks

### Task 6.1: Update `docs/systems/strategy_layer.md` facade-boundary section [Simple]
**File:** `docs/systems/strategy_layer.md`
**Tests:** none — docs

- [ ] Locate the facade-boundary section (whatever heading currently describes `StrategySessionFacade`'s public surface).
- [ ] Replace the description of "68 flat methods plus writable cache forwarders" with the post-TD-08 shape:
  - 2 top-level callables: `handle_command(cmd)`, `process_turn(progress_callback=None)`.
  - 10 public attributes: `facade_state` + 9 grouped accessors (`commands`, `fleets`, `systems`, `planets`, `empires`, `events`, `session_meta`, `economy`, `validation`).
  - Architectural invariant: new facade methods land inside the appropriate group; the top-level surface is closed.
  - Test-seeding contract: tests that need to inject planet/race state use `FacadeSessionState.seed_*` helpers, not direct field writes.
- [ ] Skip `docs/_ignore/` entirely per AGENTS.md.

**Notes:** [Filled during implementation. If the existing doc section is already structured well, edit in place; if it's stale or overloaded, prefer a clean rewrite of that section only.]

### Task 6.2: Append the post-TD-08 target shape to PROJ-309 findings [Simple]
**File:** `Projects/active_projects/PROJ-309/findings/strategy_session_facade_decomposition.md`
**Tests:** none — docs

- [ ] **Do not overwrite** the historical content. Append a new section at the end of the file:
  - Heading: `## TD-08 (PROJ-430) target surface (2026-05-16)` (or current date when appending).
  - Body: link to this project (`[PROJ-430](../../../../Projects/active_projects/PROJ-430/plan.md)`), summarize the target shape (2 top-level callables + 10 grouped attrs), and state that this is now the source of truth for facade-boundary decisions in future projects.
- [ ] Verify by re-reading the file that the historical PROJ-309 decomposition record is intact.

**Notes:** [Filled during implementation. Per CLAUDE.md's versioned-specs preference: never overwrite historical content; revisions get a new section or bumped version.]

### Task 6.3: Conditionally update `docs/03_CONVENTIONS.md` [Simple]
**File:** `docs/03_CONVENTIONS.md`
**Tests:** none — docs

- [ ] Read the relevant section (facade conventions, public surface conventions, or whatever the closest heading is).
- [ ] If existing language already captures "prefer grouped feature-domain facades over flat ones," no edit is required. Skip and record the decision in `decisions.md`.
- [ ] If the conventions doc does not capture the pattern, add a single bullet under the appropriate heading. Example wording: "Prefer grouped feature-domain accessors over flat methods on large facade classes. New methods on a multi-domain facade land inside the appropriate group, not at the top level. Example: `StrategySessionFacade` (post-TD-08)."
- [ ] Do **not** add more than one bullet. Per the TD-08 plan: "only if a new grouped-facade rule is added."

**Notes:** [Filled during implementation]

### Task 6.4: Final verification [Simple]
**Files:** none (verification)
**Tests:** none — docs phase

- [ ] Re-grep for stale references to the old facade surface across `docs/`:
  ```
  rg -n "dispatch_|_planet_index|_resolve_economy_config|68 (public )?methods" docs/
  ```
  Skip `docs/_ignore/`. Any remaining hit outside `docs/_ignore/` is a stale reference; update it.
- [ ] Final sanity grep across the project (production + tests + docs):
  ```
  rg -n "facade\._(planet_index|all_stars_cache|fleets_by_hex_cache|race_registry)" .
  ```
  Expected: zero hits outside the `seed_*` helper file and the underlying `FacadeSessionState` field declarations.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `docs/systems/strategy_layer.md` reflects the grouped surface and `seed_*` seeding contract
- [ ] PROJ-309 findings file has a new appended section recording the post-TD-08 target shape; historical content intact
- [ ] `docs/03_CONVENTIONS.md` either has the new bullet or the decision to skip is recorded in `decisions.md`
- [ ] No stale references to the old facade surface remain in docs (per the final grep)
- [ ] `python Projects/scripts/validate_phase.py PROJ-430 6` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "All phases complete — awaiting user verification"
