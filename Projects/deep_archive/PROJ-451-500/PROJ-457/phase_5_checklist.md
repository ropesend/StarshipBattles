# PROJ-457 Phase 5: Document remaining over-ceiling files as "next-touch" rule in decisions.md

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-457 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** Phases 1-3 complete (the top-3 worst offenders extracted; remaining 9 files are now F-C-027's deferred long-tail).
**Review Mode:** standard
**Objective:** Codify the remaining over-ceiling UI files as a "next-touch" rule in `decisions.md`. When an agent touches one of them for an unrelated reason, they do a same-recipe extract pass before merging. This phase is documentation-only — no code changes.

**Source-of-truth finding:** F-C-027 entry in [`findings/PROJ-457_findings.md`](findings/PROJ-457_findings.md) — "PROJ-457 disposition" section.

**Codex r4 framing:** "Keep the other 10 over-ceiling simulation files as 'next touch', not inline scope." Same principle applies to the UI side; PROJ-457 explicitly carries 9 files over to a documented rule rather than force-projecting them.

---

## Tasks

### Task 5.1: Re-measure the 9 remaining files [Simple]
**Files:** the 9 over-ceiling UI files not touched by Phases 1-3.

- [x] Run (PowerShell, PS 5.1 compatible — `wc.exe` from Git-for-Windows crashes on this checkout per the codex r5 audit; see also `phase_0_checklist.md` Task 0.2 for the same pattern):
  ```powershell
  $files = @(
      'game/ui/screens/empire_build_queue_window.py',
      'game/ui/screens/event_log_window.py',
      'game/ui/panels/race_summary_panel.py',
      'game/ui/screens/empire_panel_window.py',
      'game/ui/panels/build_queue_controller.py',
      'game/ui/panels/system_tree_panel.py',
      'game/ui/screens/design_selector_window.py',
      'game/ui/screens/strategy_detail_fmt.py',
      'game/ui/screens/new_game_setup_screen.py'
  )
  $files | ForEach-Object {
      $loc = (Get-Content $_ | Measure-Object -Line).Lines
      [PSCustomObject]@{ File = $_; LOC = $loc }
  } | Format-Table -AutoSize
  ```
- [x] Cross-check against the 2026-05-19 reference values. After PROJ-456 ships and Phases 1-3 land, some of these may also have shrunk incidentally (e.g. `event_log_window.py` had the F-C-012 empire_name fix in PROJ-456 Phase 1 — small change).
- [x] If any are now under 500 LOC, drop them from the "next-touch" list. Document the drop in `decisions.md`.

### Task 5.2: Append the "next-touch" rule to decisions.md [Simple]
**File:** `Projects/active_projects/PROJ-457/decisions.md`

- [x] Append the decision row using this template (adjust LOC values to the Task 5.1 re-measurement):
  ```
  | 2026-05-XX | F-C-027 follow-up: <N> over-ceiling UI files become a "next-touch" rule | After Phases 1-3 extracted the top 3 worst offenders, <N> UI files remain over 500 LOC: empire_build_queue_window <LOC>, event_log_window <LOC>, race_summary_panel <LOC>, empire_panel_window <LOC>, build_queue_controller <LOC>, system_tree_panel <LOC>, design_selector_window <LOC>, strategy_detail_fmt <LOC>, new_game_setup_screen <LOC>. Per Codex r4, do not force-project these; instead, document a "next-touch" rule: when an agent touches any of them for an unrelated reason, they do a same-recipe extract pass (read the file, pick a cohesive responsibility, extract to a sibling module, rewire callers, run targeted tests) before merging. The agent records the post-extraction LOC in their commit message. |
  ```
- [x] Include the actual LOC values from Task 5.1.

### Task 5.3: Decide whether CLAUDE.md / AGENTS.md need the cross-reference [Simple]
**Files:** `CLAUDE.md`, `AGENTS.md`.

- [x] Read the "Key Conventions" section of `CLAUDE.md` and the "Critical Conventions" section of `AGENTS.md`. Both list the 500-LOC ceiling rule.
- [x] **Decision**: option (a) add a one-line cross-reference in both docs naming the `decisions.md` entry; option (b) leave the docs alone and rely on agents to discover the rule when they touch a flagged file.
- [x] **Recommendation**: (a) if the rule is repo-wide (apply to all files, not just F-C-027 ones), but (b) if the rule is bounded to the 9 named files. Given Codex r4's framing ("next touch"), this is a file-specific rule — (b) is the cleaner choice.
- [x] Record the decision in `decisions.md`. If (a), edit both docs and bump their "Last verified" dates.

### Task 5.4: Update `findings/PROJ-457_findings.md` final status [Simple]
**File:** `Projects/active_projects/PROJ-457/findings/PROJ-457_findings.md`

- [x] Update F-C-027 status:
  - **Top 3 files** (build_queue_screen, planet_list_window, test_lab/screen): `Status: resolved` with post-extraction LOC value.
  - **Remaining 9 files**: `Status: deferred to next-touch rule` with the `decisions.md` entry date reference.
- [x] If Task 5.1 found any of the 9 were already under 500, mark those as `Status: resolved (naturally; no extraction required)`.

### Task 5.5: PROJ-457 project-completion verification [Simple]

- [x] All 2 owned findings (F-C-027, F-C-028) closed in `findings/PROJ-457_findings.md`.
- [x] All 5 phases (0-5) marked `Complete` in `plan.md` Quick Status table.
- [x] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green.
- [x] Update `Projects/projects_index.md` PROJ-457 row to `Complete`.

---

## Phase Completion Checklist

When all 5 tasks are checked off:
- [x] F-C-027 / F-C-028 final disposition recorded in `findings/PROJ-457_findings.md`.
- [x] `decisions.md` carries the "next-touch" rule decision row.
- [x] `CLAUDE.md` / `AGENTS.md` updated if Task 5.3 chose option (a).
- [x] Run `python Projects/scripts/validate_phase.py PROJ-457 5` — PASSED.
- [x] Update status at top of this file to `Complete`.
- [x] Update plan.md phase table row to `Complete` (and mark PROJ-457 as Project Complete in `plan.md` Current State).
- [x] Update `Projects/projects_index.md` PROJ-457 row to `Complete`.
- [x] Commit message: `PROJ-457 Phase 5: document 9 remaining over-ceiling UI files as next-touch rule; PROJ-457 complete`.
- [x] No new entries in `AgentCoordination/discovered_issues/log.jsonl` unless they are genuine out-of-scope discoveries.

## Project Completion Checklist (last phase)

When all 2 owned findings (F-C-027, F-C-028) and all 5 phase checklists are complete:
- [x] All 6 phase checklists (0-5) complete.
- [x] Final sharded-suite green run.
- [x] (PowerShell-safe) `(Get-Content game/ui/screens/build_queue_screen.py | Measure-Object -Line).Lines` < 500.
- [x] (PowerShell-safe) `(Get-Content game/ui/screens/planet_list_window.py | Measure-Object -Line).Lines` < 500.
- [x] (PowerShell-safe) `(Get-Content game/ui/screens/test_lab/screen.py | Measure-Object -Line).Lines` < 500.
- [x] (PowerShell-safe) `(Get-Content game/core/exceptions.py | Measure-Object -Line).Lines` < 80.
- [x] 5 new exceptions submodules each under 200 LOC.
- [x] All 250+ existing `from game.core.exceptions import ...` callers still working.
- [x] "Next-touch" rule documented and referenced if appropriate.
- [x] Codex end-of-project consult invoked + remediation landed if it surfaced any MUST-FIX-NOW items.
- [x] User applies the `verified` label and closes the project.
