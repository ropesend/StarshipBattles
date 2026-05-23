# PROJ-456 Phase 5: Big-three shim clusters (StrategyRenderer + NewGameSetupScreen + BattleSetupScreen)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-456 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** None (write scopes disjoint from Phases 1-4 and from each other; renderer / new_game / battle_setup are in 3 sibling packages).
**Review Mode:** standard
**Objective:** Retire the three highest-volume shim clusters in PROJ-456. Each sub-task is independently shippable.

**Source-of-truth findings:** F-C-004, F-C-008, F-C-009 in [`findings/PROJ-456_findings.md`](findings/PROJ-456_findings.md).

**Codex r4 risk flag:** "Job 8 is still the biggest review burden in the new plan. If the diff starts looking like 'every UI screen changed', cut it into two PRs by feature family." → Phase 5 can be split into 5a (F-C-004 — small, no test reads), 5b (F-C-008 — NewGameSetupScreen), 5c (F-C-009 — BattleSetupScreen panels). Operator's choice.

---

## Tasks

### Task 5.1: F-C-004 — StrategyRenderer 6 cache-attr shims [Simple]
**File:** `game/ui/screens/strategy_renderer.py:107-130`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer.py -q`

- [x] Read the property block at strategy_renderer.py:107-130 — 6 read-only `@property` shims delegating to `self._background.<attr>` and `self._hex_outlines.<attr>`.
- [x] **Verify** (PowerShell-safe; already done at 2026-05-19, re-check at phase start): `rg -n "_bg_image|_bg_scaled|_bg_brightness|_hex_outline_cache" tests` returns 0 hits. No test reads of these names.
- [x] **GREEN**: Delete the property block at lines 107-130 (~24 lines including the `# -- Back-compat shims for tests that read these as instance attributes --` header comment).
- [x] Audit production-side reads (PowerShell-safe): `rg -n "renderer\._bg_image|renderer\._bg_scaled|renderer\._bg_brightness|renderer\._hex_outline_cache" game` — should return 0 hits. If any do exist, migrate them to `renderer._background.<attr>` / `renderer._hex_outlines.<attr>`.
- [x] Run targeted tests; sharded suite green.

**Notes:** No test reads means the migration is purely production-side. The class comment at line 107 (`# -- Back-compat shims for tests that read these as instance attributes --`) acknowledges these were kept for tests that no longer reference them.

---

### Task 5.2: F-C-008 — NewGameSetupScreen 6 VM property shims [Medium]
**Files:**
- `game/ui/screens/new_game_setup_screen.py:272-321` (target)
- `tests/unit/ui/test_new_game_setup.py` (1 ref)
- `tests/unit/ui/screens/test_new_game_setup_extended.py` (29 refs)
- `tests/fixtures/new_game_setup_ui_builder.py` (4 refs)

**Tests:** `pytest tests/unit/ui/test_new_game_setup.py tests/unit/ui/screens/test_new_game_setup_extended.py -q`

- [x] Read property block at new_game_setup_screen.py:272-321 — 6 read/write property shims:
  - `player_count` ↔ `_view_model.player_count`
  - `galaxy_type` ↔ `_view_model.galaxy_type`
  - `system_count` ↔ `_view_model.system_count`
  - `player_races` ↔ `_view_model.player_races`
  - `active_race_modal` ↔ `_view_model.active_race_modal`
  - `race_modal_player_index` ↔ `_view_model.race_modal_player_index`
- [x] **RED**: For each of the 3 test/fixture files, replace `screen.<name>` with `screen._view_model.<name>` (read & write). 34 refs total + 1 self-reference in the screen file (inside the property block being deleted).
- [x] **RED — Fixture migration**: `tests/fixtures/new_game_setup_ui_builder.py` likely sets these as part of bypass-init builder behavior. The 4 refs should migrate to `screen._view_model.<name> = ...`. Verify the builder still constructs `_view_model` first; if not, the fixture may need adjustment.
- [x] Run each test file individually after migration.
- [x] **GREEN**: Delete property block at new_game_setup_screen.py:272-321 (~50 lines including the comment header at 272-273).
- [x] **Verify (PowerShell-safe)**: `rg -n "screen\.(player_count|galaxy_type|system_count|player_races|active_race_modal|race_modal_player_index)" game tests` returns 0 hits in non-VM context.
- [x] Run targeted tests; sharded suite green.

**Notes:** F-C-008 framing of "the screen is 734 LOC (over the 500-LOC ceiling)" — retiring this cluster shrinks the file by ~50 LOC but does NOT drop it under 500. The file-level LOC overflow is owned by PROJ-457 territory, not this finding. Document the post-retirement LOC count in `decisions.md`.

---

### Task 5.3: F-C-009 — BattleSetupScreen 11 VM + controller property shims [Medium]
**Files:**
- `game/ui/screens/battle_setup/screen.py:93-205` (target)
- `game/ui/screens/battle_setup/panels/left_panel.py` (11 refs)
- `game/ui/screens/battle_setup/panels/center_panel.py` (14 refs)
- `game/ui/screens/battle_setup/panels/right_panel.py` (1 ref)
- `tests/unit/ui/screens/test_battle_setup_state.py` (7 refs)

**Tests:** `pytest tests/unit/ui/screens/test_battle_setup_state.py tests/unit/ui/screens/battle_setup/ -q`

- [x] Read property block at battle_setup/screen.py:93-205 — 11 property shims:
  - **VM-side (7)**: `active_side`, `active_fleet_index`, `selected_tf_index`, `selected_sq_index`, `selected_ship_index`, `available_designs` — these route to `self.view_model.<name>`.
  - **Controller-side (4)**: `tick_limit`, `end_all_destroyed`, `end_all_derelict`, `end_mass_ratio`, `mass_ratio_threshold` — these route to `self.controller.<name>`.

  Note: F-C-009 says "~11 read/write property shims" — count is 11 (6 VM + 5 controller; the finding's "7 + 4 = 11" framing maps to 6 VM + 5 controller depending on whether `available_designs` is counted as the 7th VM shim or part of the controller cluster).

- [x] **RED — Production panel migration**:
  - `panels/left_panel.py` (11 refs) — for each `screen.<name>`, replace with `screen.view_model.<name>` or `screen.controller.<name>` per the cluster.
  - `panels/center_panel.py` (14 refs) — same.
  - `panels/right_panel.py` (1 ref) — same.
- [x] **RED — Test migration**:
  - `tests/unit/ui/screens/test_battle_setup_state.py` (7 refs) — same.
- [x] Run targeted tests after each file migration.
- [x] **GREEN**: Delete property block at battle_setup/screen.py:93-205 (~113 lines including comment headers at 93-95 and 145-146).
- [x] **Verify (PowerShell-safe)**: For each shim name, `rg -n "screen\.<name>" game/ui/screens/battle_setup tests` returns 0 hits in non-VM/non-controller context.
- [x] **Re-measure LOC (PowerShell-safe)**: `(Get-Content game/ui/screens/battle_setup/screen.py | Measure-Object -Line).Lines`. The file was 189 LOC at HEAD before this phase (per the 2026-05-19 re-measurement); after deleting ~113 lines of property block, expect ~75-85 LOC. Document in `decisions.md`.
- [x] Run targeted tests; sharded suite green.

**Notes:** The 2026-05-18 bucket scan said this file was 559 LOC and that the shims pushed it over the 500-LOC ceiling. The 2026-05-19 re-verification found 189 LOC — the file already had its main responsibilities extracted into the panels package (left/center/right). The remaining 11 shims still merit removal for the dual-path foot-gun reason (writes through `screen.<name>` and `screen.view_model.<name>` both succeed, masking which path is canonical), but the "drops the file under the LOC ceiling" framing in F-C-009 no longer applies.

---

## Phase Completion Checklist

When all 3 tasks are checked off:
- [x] F-C-004, F-C-008, F-C-009 flipped to `Status: resolved` in `findings/PROJ-456_findings.md`.
- [x] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green.
- [x] Run `python Projects/scripts/validate_phase.py PROJ-456 5` — PASSED.
- [x] Update status at top of this file to `Complete`.
- [x] Update plan.md phase table row to `Complete` (and mark PROJ-456 as Project Complete in `plan.md` Current State).
- [x] Update `Projects/projects_index.md` PROJ-456 row to `Complete`.
- [x] Commit message: `PROJ-456 Phase 5: retire big-three UI shim clusters (F-C-004 strategy_renderer, F-C-008 new_game_setup, F-C-009 battle_setup); PROJ-456 complete`.
- [x] No new entries in `AgentCoordination/discovered_issues/log.jsonl` unless they are genuine out-of-scope discoveries.

## Project Completion Checklist (last phase)

When all 14 owned findings (F-C-001..F-C-012, F-C-029, DI-2026-05-18-002) are resolved:
- [x] All 5 phase checklists complete.
- [x] Final sharded-suite green run on file with the expected new baseline.
- [x] `transfer_dialog.py` LOC < 500.
- [x] All 14 owned-finding entries in `findings/PROJ-456_findings.md` carry `Status: resolved` with closure dates.
- [x] Codex end-of-project consult invoked + remediation landed if it surfaced any MUST-FIX-NOW items.
- [x] User applies the `verified` label and closes the project per the CLAUDE.md authority constraint.
