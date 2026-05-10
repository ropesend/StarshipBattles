# Phase 4: Final verification + tooling

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-309 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Verify end-to-end. Optionally land a small tooling helper to keep the convention enforced.

**Prerequisites:** Phase 3 complete — all 10 files decomposed.

---

## Tasks

### Task 4.1: Top-10 sweep [Simple]
**File:** None — verification.
**Tests:** Manual.

- [x] `find game -name "*.py" -type f -exec wc -l {} + | sort -rn | head -20` — confirm none of the new top-20 files exceed 500 lines
- [x] If any do, document why (could be legitimate — e.g., a file just added by a different project) — but flag for follow-up

**Notes:** All 10 PROJ-309 targets decomposed; every resulting module <500 LOC (max: `screen_router.py` at 496). Top-10 final state — `race_setup_screen.py` 31 (shim), `strategy_renderer.py` 307, `test_lab/renderer.py` DELETED, `core/protocols.py` DELETED, `command_handlers.py` 82 (shim), `test_run_details.py` 12 (shim), `strategy_session_facade.py` 476, `workshop_viewmodel.py` 462, `app.py` 444, `strategy_window_manager.py` 334.

**Top-25 sweep findings (files NOT touched by PROJ-309):** 22 files in `game/` are still >500 LOC. These were OUT OF SCOPE for PROJ-309 (which targeted only the top-10). The 500-LOC convention now in place will pull them down organically as they are touched. Top of the residual list: `battle_state.py` 805, `battle_controller.py` 805, `transfer_dialog.py` 783, `order_processor.py` 779, `superweapon_order_processor.py` 771, `planetary.py` 762, `stars.py` 761, `battle_engine.py` 758, `turn_engine.py` 741, `test_lab/screen.py` 738. None of these were PROJ-309 targets; flagged for future organic decomposition under the new convention.

---

### Task 4.2: Full sharded suite [Simple]
**File:** None.
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Run the full sharded suite
- [x] Confirm 15389+ passing (no regressions introduced by decompositions)

**Notes:** Final sharded run after 3.9: **15582 / 15582 passed, 0 failed, 0 errors** (54.9s wall time). PROJ-309 added contract tests across the project: `test_protocols_public_api.py` (46), `test_command_handlers_public_api.py` (23), `test_workshop_viewmodel_public_api.py` (11), `test_strategy_session_facade_public_api.py` (5), `test_renderer_public_api.py` (4), `test_test_run_details_public_api.py` (12), `test_strategy_renderer_public_api.py` (7), `test_strategy_window_manager_public_api.py` (25), `test_race_setup_screen_public_api.py` (3), `test_app_public_api.py` (32), `test_app_bootstrap_invariants.py` (6) = 174 new contract tests. Baseline grew from 15405 → 15582.

Test patch-target migrations applied during 3.5 and 3.10 in 7 files total (find_hybrid_path → handlers.base.find_hybrid_path × 5 files; window-manager class patches × 2 files + 4 fixture additions of `wm.planet_abilities_window = None`).

---

### Task 4.3: Manual smoke (everything touched) [Medium]
**File:** Game runtime.
**Tests:** Manual.

- [ ] Launch the game
- [ ] Race setup screen (3.1)
- [ ] Strategy screen — every render layer (3.2, 3.10)
- [ ] Issue commands — every handler kind (3.5)
- [ ] Workshop screen (3.8)
- [ ] Combat Lab — open, run a scenario, view details (3.3, 3.6)
- [ ] Sub-windows on strategy screen (3.10)
- [ ] Confirm no console errors / import errors / silent UI breakage

**Notes:**

---

### Task 4.4: (Optional) Add `Tools/check_file_size.py` [Simple]
**File:** `Tools/check_file_size.py` (NEW)
**Tests:** Manual.

- [x] Decide whether to add the tooling now or capture as follow-up. If now:
  - [x] Write a small script: walks `game/`, fails (exit 1) if any production file >500 lines
  - [ ] Add it to a recommended pre-push hook or CI step (deferred — capture as follow-up; running it would fail today on the 52 OUT-OF-SCOPE files)
- [x] Smoke: `python Tools/check_file_size.py` — currently reports 52 violations (all OUT OF SCOPE for PROJ-309)

**Notes:** Tool landed at `Tools/check_file_size.py`. Walks `game/`, prints violations sorted by LOC desc, exits 1 if any file >500 LOC. Excludes `__pycache__`. Test/lab/sim-test files are not under `game/` so naturally skipped. Configurable via `--max N`.

PROJ-309's 10 targets all pass. The tool currently reports 52 violations — every one is a residual file PRE-EXISTING and OUT OF SCOPE for PROJ-309. The convention is now enforceable; future sub-projects can adopt the tool in CI once they decompose the residual 52.

Did NOT wire to a pre-push hook / CI gate — that would block all current development on the 52 unrelated files. The honest path: convention documented + tool available + organic decomposition as files are touched. A future PROJ-3xx can take the next-tier files (battle_state.py 805, battle_controller.py 805, etc.) and gradually flip the gate green.

---

### Task 4.5: Update MEMORY.md [Simple]
**File:** `C:\Users\rossr\.claude\projects\c--Dev-Starship-Battles\memory\MEMORY.md`
**Tests:** None.

- [ ] After user verification, add an entry under "Recently Archived":
  - `- **PROJ-309** — Top-10 File Decomposition + 500-LOC Convention (2026-MM-DD). All 4 phases complete. Decomposed 10 files (totalling ~10,000 lines) into modules each <500 LOC. CLAUDE.md "Code Quality" + docs/03_CONVENTIONS.md updated with the rule. [Optional: Tools/check_file_size.py landed.] Sharded suite: [N]/[N] passing.`

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] No production file in `game/` exceeds 500 lines (or any exceptions are documented)
- [ ] Full sharded suite passing
- [ ] Manual smoke passes
- [ ] User verified
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete — pending archive"
