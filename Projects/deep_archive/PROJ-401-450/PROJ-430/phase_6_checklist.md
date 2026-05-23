# Phase 6: Documentation sync

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-430 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
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

- [x] Locate the facade-boundary section (whatever heading currently describes `StrategySessionFacade`'s public surface).
- [x] Replace the description of "68 flat methods plus writable cache forwarders" with the post-TD-08 shape:
  - 2 top-level callables: `handle_command(cmd)`, `process_turn(progress_callback=None)`.
  - 10 public attributes: `facade_state` + 9 grouped accessors (`commands`, `fleets`, `systems`, `planets`, `empires`, `events`, `session_meta`, `economy`, `validation`).
  - Architectural invariant: new facade methods land inside the appropriate group; the top-level surface is closed.
  - Test-seeding contract: tests that need to inject planet/race state use `FacadeSessionState.seed_*` helpers, not direct field writes.
- [x] Skip `docs/_ignore/` entirely per AGENTS.md.

**Notes:** §1 of `docs/systems/strategy_layer.md` rewritten end-to-end around the post-TD-08 grouped surface. New subsections: "Top-level surface" table (2 callables + 10 attrs), "Grouped namespaces" verb table (9 groups), "Architectural invariant (TD-08)", "Test-seeding seam (TD-08 Phase 4)". The CQRS pattern section in `docs/02_PATTERNS.md` and the `dispatch_issue_lay_mines` reference in `docs/systems/minefields.md` also updated to point at `facade.commands.<verb>`.

### Task 6.2: Append the post-TD-08 target shape to PROJ-309 findings [Simple]
**File:** `Projects/active_projects/PROJ-309/findings/strategy_session_facade_decomposition.md`
**Tests:** none — docs

- [x] **Do not overwrite** the historical content. Append a new section at the end of the file:
  - Heading: `## TD-08 (PROJ-430) target surface (2026-05-17)`.
  - Body: links to PROJ-430 plan + TD-08 source plan + `docs/systems/strategy_layer.md` §1, summarizes the target shape (2 top-level callables + 10 grouped attrs), states the architectural invariant as the source of truth for future facade work.
- [x] Verify by re-reading the file that the historical PROJ-309 decomposition record is intact.

**Notes:** File lives at `Projects/deep_archive/PROJ-301-350/PROJ-309/findings/strategy_session_facade_decomposition.md` (PROJ-309 was archived). Section appended at end of file; original 278 lines of historical PROJ-309 decomposition record untouched. Cross-links use repo-relative paths.

### Task 6.3: Conditionally update `docs/03_CONVENTIONS.md` [Simple]
**File:** `docs/03_CONVENTIONS.md`
**Tests:** none — docs

- [x] Read the relevant section (facade conventions, public surface conventions, or whatever the closest heading is).
- [x] If existing language already captures "prefer grouped feature-domain facades over flat ones," no edit is required. Skip and record the decision in `decisions.md`.
- [x] If the conventions doc does not capture the pattern, add a single bullet under the appropriate heading. Example wording: "Prefer grouped feature-domain accessors over flat methods on large facade classes. New methods on a multi-domain facade land inside the appropriate group, not at the top level. Example: `StrategySessionFacade` (post-TD-08)."
- [x] Do **not** add more than one bullet. Per the TD-08 plan: "only if a new grouped-facade rule is added."

**Notes:** Added a single bullet under the "Preferences" list in `docs/03_CONVENTIONS.md`, mirroring the existing "X over Y" style of the surrounding bullets and naming `StrategySessionFacade` (post-TD-08) as the canonical example with the 2+9 shape spelled out.

### Task 6.4: Final verification [Simple]
**Files:** none (verification)
**Tests:** none — docs phase

- [x] Re-grep for stale references to the old facade surface across `docs/`:
  ```
  rg -n "dispatch_|_planet_index|_resolve_economy_config|68 (public )?methods" docs/
  ```
  Skip `docs/_ignore/`. Any remaining hit outside `docs/_ignore/` is a stale reference; update it.
- [x] Final sanity grep across the project (production + tests + docs):
  ```
  rg -n "facade\._(planet_index|all_stars_cache|fleets_by_hex_cache|race_registry)" .
  ```
  Expected: zero hits outside the `seed_*` helper file and the underlying `FacadeSessionState` field declarations.

**Notes:** First grep: 8 hits, all intentional explanatory references (describing how `dispatch_*` was replaced, the seed-helper pattern, the CommandDispatchSlice internal helper, or unrelated `_dispatch_toggle_pause_command` on `BuildQueueScreen`). No stale references. Second grep: zero production-code or test-driver hits — all matches are inside `_facade_state.py` docstrings (where the seed helpers live), test docstring comments, project/PROJ-309 history docs, the TD-08 source plan, or `docs/systems/strategy_layer.md` lines 66-67 where the migration is explained.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `docs/systems/strategy_layer.md` reflects the grouped surface and `seed_*` seeding contract
- [x] PROJ-309 findings file has a new appended section recording the post-TD-08 target shape; historical content intact
- [x] `docs/03_CONVENTIONS.md` either has the new bullet or the decision to skip is recorded in `decisions.md`
- [x] No stale references to the old facade surface remain in docs (per the final grep)
- [x] `python Projects/scripts/validate_phase.py PROJ-430 6` passes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "All phases complete — awaiting user verification"
