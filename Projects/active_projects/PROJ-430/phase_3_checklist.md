# Phase 3: Migrate UI callers to the grouped surface

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-430 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_2
**Review Mode:** standard
**Files (planned):** ~25 UI files under `game/ui/` (re-enumerated freshly via `rg`, not trusted from a stale list)

**Objective:** Mechanical rename across the 25 UI files. `facade.dispatch_issue_move(...)` -> `facade.commands.issue_move(...)`; `facade.get_fleet(id)` -> `facade.fleets.get(id)`; etc. No UI behavior change. One commit per UI screen group. The legacy flat surface remains in place — this phase only moves callers off it.

---

## Tasks

### Task 3.1: Re-enumerate UI callers (do not trust the Phase 1 list) [Simple]
**Files:** none (discovery)
**Tests:** none

- [ ] Re-run the UI caller grep against the current tree:
  ```
  rg -n "facade\.(dispatch_|get_|can_|get_turn_number|get_save_path|get_human_player_ids|get_race_registry|get_colony_demographic_view)" game/ui | sort -u
  ```
- [ ] Compare against `findings/phase_1_ui_caller_inventory.md`. If the list has drifted (Phase 1 ran some time ago, or other strategy tech-debt projects landed in parallel), record the new list in `findings/phase_3_ui_caller_list.md`.
- [ ] Group the files by UI screen (e.g. "build queue screens", "fleet command screens", "planet report screens") so one commit per group is achievable.
- [ ] Per the TD-08 plan's weak-LLM guardrail: do **not** invent new per-file API shapes. The rename table in [manifest.md](manifest.md) is exhaustive. If a UI file calls a facade method not in the rename table, stop and reconcile with Phase 2's namespace design before continuing.

**Notes:** [Filled during implementation]

### Task 3.2: Mechanical rewrite — UI screen group 1 [Simple per file]
**Files:** first group of UI files from Task 3.1
**Tests:** `pytest tests/unit/ui tests/integration -x` after the commit

- [ ] For each file in the group, apply the rename table from [manifest.md](manifest.md):
  - `facade.dispatch_<verb>(...)` -> `facade.commands.<verb>(...)`
  - `facade.get_fleet(...)` -> `facade.fleets.get(...)`
  - `facade.get_fleets_at_hex(...)` -> `facade.fleets.at_hex(...)`
  - `facade.get_fleet_path_preview(...)` -> `facade.fleets.path_preview(...)`
  - `facade.get_fleet_path_projection(...)` -> `facade.fleets.path_projection(...)`
  - `facade.get_fleet_remaining_pods(...)` -> `facade.fleets.remaining_pods(...)`
  - `facade.get_planet(...)` -> `facade.planets.get(...)`
  - `facade.get_star(...)` etc. -> `facade.systems.<verb>(...)`
  - `facade.get_empire(...)` etc. -> `facade.empires.<verb>(...)`
  - `facade.get_event(...)` etc. -> `facade.events.<verb>(...)`
  - `facade.get_turn_number()` / `.get_save_path()` / `.get_human_player_ids()` -> `facade.session_meta.<final form>`
  - `facade.get_race_registry()` -> `facade.economy.race_registry`
  - `facade.get_colony_demographic_view(...)` -> `facade.economy.colony_demographic_view(...)`
  - `facade.can_colonize(...)` -> `facade.validation.can_colonize(...)`
  - `facade.can_move_to(...)` -> `facade.validation.can_move_to(...)`
- [ ] Run `pytest tests/unit/ui tests/integration -x`. Investigate any failure before continuing to the next group.
- [ ] Commit: `refactor: migrate <UI screen group> to facade grouped surface (TD-08 phase 3)`

**Notes:** [Filled during implementation. Per the TD-08 plan: "Use one commit per UI screen group to keep diffs reviewable."]

### Task 3.3: Mechanical rewrite — UI screen group 2 [Simple per file]
**Files:** second group of UI files from Task 3.1
**Tests:** `pytest tests/unit/ui tests/integration -x` after the commit

- [ ] Same procedure as Task 3.2 for the next group.
- [ ] Commit per group.

**Notes:** [Filled during implementation. Repeat the task pattern (3.4, 3.5, ...) for as many groups as Task 3.1 produces. Typical TD-08 grouping: ~5-7 groups across the 25 files.]

### Task 3.4: Mechanical rewrite — remaining UI screen groups [Simple per group]
**Files:** remaining UI files from Task 3.1
**Tests:** `pytest tests/unit/ui tests/integration -x` after each commit

- [ ] Continue group-by-group until every file in `findings/phase_3_ui_caller_list.md` is migrated.
- [ ] After the final group, re-run the original grep to confirm zero hits:
  ```
  rg -n "facade\.(dispatch_|get_|can_|get_turn_number|get_save_path|get_human_player_ids|get_race_registry|get_colony_demographic_view)" game/ui
  ```
  Expected: zero matches. Any remaining match is a missed file; migrate it before completing the phase.

**Notes:** [Filled during implementation]

### Task 3.5: Sweep non-UI production callers [Simple]
**Files:** none initially (discovery)
**Tests:** focused strategy suite

- [ ] Grep across all of `game/` (not just `game/ui/`) for legacy facade usage:
  ```
  rg -n "facade\.(dispatch_|get_fleet|get_planet|get_star|get_empire|get_event|get_turn_number|get_save_path|get_human_player_ids|get_race_registry|get_colony_demographic_view|can_colonize|can_move_to)" game/
  ```
- [ ] Any non-UI production hits (AI controllers, save-game writers, etc.) get migrated the same way. Record any such files in `findings/phase_3_non_ui_callers.md` and migrate.
- [ ] Run `pytest tests/unit/strategy tests/integration/strategy -q` after these edits.

**Notes:** [Filled during implementation. The TD-08 plan focuses on UI because that was the verified consumer; if other callers turn up, the same rename rules apply.]

### Task 3.6: Confirm focused suites green before exiting the phase [Simple]
**Files:** none (verification)
**Tests:** focused strategy + UI + integration suites

- [ ] Run:
  ```
  pytest tests/unit/strategy/facade tests/unit/ui tests/integration -q
  ```
- [ ] Expected: green except for the Phase 1 contract assertions that flip in Phase 5 (`test_no_legacy_flat_methods`, `test_legacy_cache_attrs_removed`). Those stay red by design.
- [ ] Do **not** run the full sharded suite here — that's Phase 5's job. Focused suites are sufficient to clear Phase 3.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Every UI caller in `findings/phase_3_ui_caller_list.md` migrated to the grouped surface
- [ ] Final grep returns zero hits for legacy facade usage in `game/ui/`
- [ ] Non-UI production callers also migrated (per Task 3.5)
- [ ] Focused facade + UI + integration suites green except the two Phase-1-anchored assertions that go green in Phase 5
- [ ] `python Projects/scripts/validate_phase.py PROJ-430 3` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
