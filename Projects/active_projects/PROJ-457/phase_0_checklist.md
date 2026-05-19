# PROJ-457 Phase 0: Re-measure LOC of all 12 F-C-027 files after PROJ-456 ships (rescope)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-457 0`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** PROJ-456 complete (all 14 owned findings resolved; sharded suite green).
**Review Mode:** standard
**Objective:** Re-measure LOC of all 12 over-ceiling UI files identified by F-C-027 *after* PROJ-456 retires the bulk of UI back-compat shims. If any of the top-3 (build_queue_screen, planet_list_window, test_lab/screen) drop under 500 LOC naturally, rescope Phases 1-3 to pick up the next-worst-offender from the remaining 9 (or close the phase if the file is already compliant).

**Source-of-truth finding:** F-C-027 in [`findings/PROJ-457_findings.md`](findings/PROJ-457_findings.md).

**Rationale (per Codex r4):** "Job 9 depends on Job 8 (LOC drops after shim retirement; rescope before starting)." This phase is the gate.

---

## Tasks

### Task 0.1: Verify PROJ-456 is complete [Simple]

- [x] Check `Projects/active_projects/PROJ-456/plan.md` Quick Status table — all 5 phases marked `Complete`.
- [x] Check `Projects/projects_index.md` — PROJ-456 row marked `Complete` and `verified` (or at least `awaiting-confirmation`).
- [x] Run `python Tools/test_sharded/test_sharded.py` — sharded suite green at the post-PROJ-456 baseline.
- [x] If PROJ-456 has not yet completed, STOP: PROJ-457 cannot start until PROJ-456 is in.

### Task 0.2: Re-measure all 12 F-C-027 files [Simple]
**Files:** the 12 UI files listed in F-C-027.
**Tests:** none — read-only LOC measurement.

- [x] Run (PowerShell, PS 5.1 compatible — this repo's shell is Windows PowerShell):
  ```powershell
  $files = @(
      'game/ui/screens/build_queue_screen.py',
      'game/ui/screens/planet_list_window.py',
      'game/ui/screens/test_lab/screen.py',
      'game/ui/screens/new_game_setup_screen.py',
      'game/ui/screens/empire_build_queue_window.py',
      'game/ui/screens/event_log_window.py',
      'game/ui/panels/race_summary_panel.py',
      'game/ui/screens/empire_panel_window.py',
      'game/ui/panels/build_queue_controller.py',
      'game/ui/panels/system_tree_panel.py',
      'game/ui/screens/design_selector_window.py',
      'game/ui/screens/strategy_detail_fmt.py'
  )
  $files | ForEach-Object {
      $loc = (Get-Content $_ | Measure-Object -Line).Lines
      [PSCustomObject]@{ File = $_; LOC = $loc }
  } | Format-Table -AutoSize
  ```
  (`wc -l` is unreliable on this checkout — `wc.exe` and `grep.exe` from Git-for-Windows crash with `CreateFileMapping ... Win32 error 5` per the codex r5 audit 2026-05-19. Use the PowerShell-native pattern above.)
- [x] Record results in `findings/post_proj_456_loc_remeasure.md` with a table comparing pre-PROJ-456 (2026-05-19) LOC to post-PROJ-456 LOC and the delta.
- [x] Identify which files are now under 500 LOC (naturally compliant — no longer in F-C-027 scope) and which still over-run.

### Task 0.3: Rescope Phases 1-3 if needed [Simple]
**File:** `Projects/active_projects/PROJ-457/plan.md` Quick Status table.

- [x] **ESCALATION GATE**: If ANY of the top-3 target files (`build_queue_screen.py`, `planet_list_window.py`, `test_lab/screen.py`) is already under 500 LOC at this re-measurement, **STOP and surface to the user** before proceeding with that phase's extraction. The "ceiling enforcement" rationale is gone; force-splitting a file just because it was scoped is the exact anti-pattern Codex r4 warned against ("F-A-007 should not be smuggled in as a side quest"). Document the user's decision in `decisions.md`: (a) drop that phase entirely, (b) replace the target with a next-worst offender from the remaining 9, or (c) proceed with an explicit architectural-cleanup rationale documented in plan.md.
- [x] (For reference — same pattern as F-C-028 in Phase 4: that file is already 411 LOC at HEAD, under the 500 ceiling, and Phase 4 is PENDING USER DECISION. Apply the same escalation discipline here.)
- [x] If `build_queue_screen.py` < 500: STOP per the escalation gate above. If user approves replacement: pick the next-worst-offender from the remaining 9.
- [x] If `planet_list_window.py` < 500: STOP per the escalation gate above.
- [x] If `test_lab/screen.py` < 500: STOP per the escalation gate above.
- [x] If all 12 are now under 500 LOC: close PROJ-457 except for Phase 4 (exceptions split, which is independent and ALSO under the ceiling — pending user decision) and the Phase 5 "next-touch" rule documentation (which can also be skipped if no files remain over-ceiling).
- [x] Document the rescope rationale in `decisions.md` with a 2026-05-XX row.
- [x] Update `plan.md` Quick Status, Current State, and the per-phase target file references.

### Task 0.4: Identify candidate extraction responsibilities for top-3 (preparation for Phases 1-3) [Medium]
**Files:** read-only audit of the top-3 (post-rescope) target files.

- [x] For each of the (possibly rescoped) Phase 1 / 2 / 3 targets, do a read-only audit: identify 2-3 candidate cohesive responsibilities that could be extracted to a sibling module. Record candidates in `decisions.md` along with the expected post-extraction LOC for each candidate.
- [x] The actual choice is made at Phase 1 / 2 / 3 start; this audit just gives the executing agent a head start.

---

## Phase Completion Checklist

When all 4 tasks are checked off:
- [x] `findings/post_proj_456_loc_remeasure.md` committed with 12-file LOC table + deltas.
- [x] `plan.md` Quick Status table updated if any rescope happened.
- [x] `decisions.md` carries 1-2 rows documenting the rescope rationale + candidate-extraction audit.
- [x] Run `python Projects/scripts/validate_phase.py PROJ-457 0` — PASSED.
- [x] Update status at top of this file to `Complete`.
- [x] Update plan.md phase table row to `Complete`.
- [x] Update plan.md Current State to point to Phase 1.
- [x] Commit message: `PROJ-457 Phase 0: re-measure 12 F-C-027 files post-PROJ-456 (rescope decisions documented)`.
- [x] No new entries in `AgentCoordination/discovered_issues/log.jsonl` unless they are genuine out-of-scope discoveries.
