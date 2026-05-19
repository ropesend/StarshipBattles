# PROJ-457: UI structural debt extractions (top 3 worst-offender UI files + game/core/exceptions.py domain split)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-457` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-457 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03a-continue-working (serial on `main` per user standing preference; no worktrees).

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 0. Re-measure LOC of all 12 F-C-027 files after PROJ-456 ships (rescope) | Complete | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. Extract one responsibility from `build_queue_screen.py` (958 → under 500) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Same recipe for `planet_list_window.py` (862 → under 500) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Same recipe for `test_lab/screen.py` (744 → under 500) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. F-C-028 — Split `game/core/exceptions.py` | Dropped (user decision 2026-05-19) | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Document remaining over-ceiling files as "next-touch" rule in decisions.md | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-05-19
**Active Phase:** Phase 3 (test_lab/screen.py extraction)
**Last Action:** Phase 2 complete: planet_list_window.py 862 → 453 LOC. Extracted (a) helpers + production UI builder into `planet_list_helpers.py` (~250 LOC): `_get_planetary_ids`, `_format_population`, `_render_effect_cell`, `build_effect_columns`, `PlanetListUiBuilder`; (b) event dispatch + selection coordination into `planet_list_event_router.py` (~270 LOC): `process_event`, `_set_all_filters`, `_set_all_effects`, `_toggle_filter`, `_navigate_to_selected`, `_on_planet_selected`, `_resolve_demographic_view`, `_detail_panel_geometry`. Window retains a thin `process_event` delegate (1-line body) + a `_super_process_event` hook the router uses to call the base class. Migrated tests for `_on_planet_selected` (3 sites) and `_detail_panel_geometry` (1 fixture) to use the router. Sharded 23375/23375 green.
**Next Action:** Phase 3 — extract one responsibility from `test_lab/screen.py` (744 → under 500).
**Blockers:** PROJ-456 must complete first (Group B serial order; hard gate per coordinator 2026-05-19) — Phase 0 explicitly re-measures the 12 over-ceiling files after PROJ-456's shim retirement.

## Overview
After PROJ-456 retires the bulk of UI back-compat shims, do the real structural extractions for the 3 worst-offender UI files still over the 500-LOC ceiling: `build_queue_screen.py` (846 at HEAD; was 961 in original scan), `planet_list_window.py` (746 at HEAD; was 862), `test_lab/screen.py` (614 at HEAD; was 744). All three top-3 are STILL OVER 500 even after intervening work — extraction scope holds. Same recipe per file: read the file, identify a cohesive responsibility (yard population / queue selection / drag handling / list filtering / test runner orchestration / etc.), extract into a sibling module, rewire callers, run tests. Plus split `game/core/exceptions.py` (**411 LOC at HEAD — ALREADY UNDER 500 ceiling**, 31 exception classes) by domain (`base / strategy / simulation / llm / image`) with the top-level `exceptions.py` becoming a re-export aggregator — re-export shim is allowed per the convention because the 250+ caller files justify it. **Phase 4's rationale shifted from "ceiling enforcement" (no longer applicable) to "architectural cleanup of 31 classes split by domain for clarity / import locality"; PENDING USER DECISION on whether Phase 4 stays in scope.**

## Goals
- Drop the top 3 worst-offender UI production files under the 500-LOC ceiling (`build_queue_screen.py` 846 → <500; `planet_list_window.py` 746 → <500; `test_lab/screen.py` 614 → <500; HEAD measurements 2026-05-19).
- (Pending user decision) Split `game/core/exceptions.py` (411 LOC at HEAD — already under 500) by domain with a re-export aggregator at the top-level; preserve all 250+ existing callers via the re-export shim. Rationale shifted from "ceiling enforcement" to "architectural cleanup of 31 classes split by domain for clarity".
- Document the remaining 9 over-ceiling UI files as a "next-touch" rule in `decisions.md` — when one of them is touched for an unrelated reason, the touching agent does an extract-by-responsibility pass before merging.
- Keep every phase independently shippable; same single-file recipe per phase.
- Land with full sharded suite green at the end of each phase.

## Scope

**In Scope:**
- F-C-027 (top 3 only; HEAD LOC re-measured 2026-05-19):
  - Phase 1: `game/ui/screens/build_queue_screen.py` (846 LOC at HEAD) — extract one cohesive responsibility into a sibling module.
  - Phase 2: `game/ui/screens/planet_list_window.py` (746 LOC at HEAD) — same recipe.
  - Phase 3: `game/ui/screens/test_lab/screen.py` (614 LOC at HEAD) — same recipe.
- F-C-028 (PENDING USER DECISION on whether Phase 4 stays in scope): `game/core/exceptions.py` (411 LOC at HEAD — under 500 ceiling already) → 31 classes split by domain with re-export aggregator; 5 new submodules (`exceptions_base.py`, `exceptions_strategy.py`, `exceptions_simulation.py`, `exceptions_llm.py`, `exceptions_image.py`).
- Phase 0 re-measurement of all 12 F-C-027 files after PROJ-456 ships (rescope if any drop naturally).
- Phase 5 — document the remaining 9 over-ceiling UI files as a "next-touch" rule in `decisions.md`.

**Out of Scope:**
- The other 9 F-C-027 over-ceiling files (`empire_build_queue_window.py`, `event_log_window.py`, `race_summary_panel.py`, `empire_panel_window.py`, `build_queue_controller.py`, `system_tree_panel.py`, `design_selector_window.py`, `strategy_detail_fmt.py`, `new_game_setup_screen.py`) — covered by the Phase 5 "next-touch" rule, not inline extracted.
- All PROJ-456 findings (UI shim retirement) — owned by PROJ-456.
- F-C-017 (UIWindow retrofit completion) — owned by PROJ-458.
- F-A-007 (`ship_instance.py` 839 LOC) — Codex r4: "F-A-007 should not be smuggled in as a side quest; if it still sits at 839 LOC after job 1, spin it as its own next-touch project." Out of PROJ-457 scope; owned by PROJ-455 (strategy data LOC extractions).
- All non-LOC-overflow findings.

## Findings Summary

| ID | Severity | Owner phase | File |
|----|----------|-------------|------|
| F-C-027 (top-3) | medium | Phases 1-3 | 3 UI files (build_queue_screen, planet_list_window, test_lab/screen) |
| F-C-027 (other 9) | medium | Phase 5 (next-touch rule) | 9 UI files documented in `decisions.md` |
| F-C-028 | low | Phase 4 | `game/core/exceptions.py` |

Full per-finding details: [findings/PROJ-457_findings.md](findings/PROJ-457_findings.md).

## Key Files

| Component | File Path |
|-----------|-----------|
| Worst-offender UI #1 | `game/ui/screens/build_queue_screen.py` (961 LOC at HEAD before PROJ-456 ships; re-measure at Phase 0) |
| Worst-offender UI #2 | `game/ui/screens/planet_list_window.py` (862 LOC at HEAD; re-measure at Phase 0) |
| Worst-offender UI #3 | `game/ui/screens/test_lab/screen.py` (744 LOC at HEAD; re-measure at Phase 0) |
| Exceptions module | `game/core/exceptions.py` (411 LOC at HEAD 2026-05-19; under 500 ceiling already; 31 exception classes across 5 domain clusters per phase_4 checklist enumeration) |
| F-C-027 "next-touch" 9 files | `empire_build_queue_window.py`, `event_log_window.py`, `race_summary_panel.py`, `empire_panel_window.py`, `build_queue_controller.py`, `system_tree_panel.py`, `design_selector_window.py`, `strategy_detail_fmt.py`, `new_game_setup_screen.py` |
| Re-export shim target | `game/core/exceptions.py` (becomes a re-export aggregator after Phase 4) |
| New exception submodules | `game/core/exceptions_base.py`, `exceptions_strategy.py`, `exceptions_simulation.py`, `exceptions_llm.py`, `exceptions_image.py` (Phase 4) |

Full enumeration in [manifest.md](manifest.md).

## Phase Breakdown

### Phase 0: Re-measure LOC of all 12 F-C-027 files after PROJ-456 ships (rescope)
**Status:** Not Started — gated on PROJ-456 completion.

After PROJ-456 ships (UI shim retirement sweep), the 9 owned shim clusters retire — `transfer_dialog.py` drops from 523 to under 500; `new_game_setup_screen.py` drops by ~50 LOC; `battle_setup/screen.py` was already under 500 at HEAD (189 LOC) but loses another ~113 LOC. Other files may also shrink incidentally. Re-measure all 12 F-C-027 files; rescope Phases 1-3 if any of the top-3 drop under 500 naturally.

Tasks: run a PowerShell line count over each of the 12 files; record results in `findings/post_proj_456_loc_remeasure.md`; if any of the top-3 (build_queue_screen, planet_list_window, test_lab/screen) drop under 500, replace that phase with the next-worst-offender from the remaining 9 (or close the phase if all 12 are under 500).

**PowerShell one-liner for batch LOC measurement (PS 5.1 compatible):**
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

**Checkpoint:** `findings/post_proj_456_loc_remeasure.md` committed; phase plan in `plan.md` Quick Status table updated if rescoped.

### Phase 1: Extract one responsibility from `build_queue_screen.py` (961 → under 500)
Read the file, identify a cohesive responsibility, extract into a sibling module. F-C-027 suggests "yard population, queue selection, drag handling" as candidate responsibilities. The screen already has a `build_queue_*` family split (per finding) so the pattern is established.

**Recipe** (mirrors PROJ-374-era extractions):
1. Pick the responsibility cluster (e.g. drag-and-drop event handling).
2. Identify the methods + state fields belonging to that cluster.
3. Create new module `game/ui/screens/build_queue_drag_*.py` (or similar — match existing naming).
4. Move the cluster; expose a narrow API.
5. Rewire `build_queue_screen.py` to call the new module.
6. Migrate any test reads to the new module's API.
7. Run sharded suite green.

**Checkpoint (PowerShell-safe):** `(Get-Content game/ui/screens/build_queue_screen.py | Measure-Object -Line).Lines` returns < 500.

### Phase 2: Same recipe for `planet_list_window.py` (862 → under 500)
Pick a cohesive responsibility. Candidates per the file's existing structure (verified 2026-05-19 read of lines 1-60): `_format_population` and other formatting helpers; filter/sort orchestration via `PlanetListFilterManager` (already extracted — see if more can join); or the sidebar build (`build_sidebar`).

Same 7-step recipe as Phase 1.

**Checkpoint (PowerShell-safe):** `(Get-Content game/ui/screens/planet_list_window.py | Measure-Object -Line).Lines` returns < 500.

### Phase 3: Same recipe for `test_lab/screen.py` (744 → under 500)
The file's docstring (verified 2026-05-19) says "Target: keep the class under 300 lines — delegate logic to ViewModel / Renderer / InputHandler / Controller. FleetBattleSetupScreen is the sibling exemplar." The existing decomposition (`viewmodel`, `renderer`, `input_handler`, `panel_manager`, `test_executor`, `data_extractor`) means further extraction has clear precedent. Candidate: scenario loading / test history coordination.

Same 7-step recipe as Phase 1.

**Checkpoint (PowerShell-safe):** `(Get-Content game/ui/screens/test_lab/screen.py | Measure-Object -Line).Lines` returns < 500.

### Phase 4: F-C-028 — Split `game/core/exceptions.py` by domain with re-export shim
Split 31 exception classes into 5 domain submodules; `exceptions.py` becomes a re-export aggregator (~60-80 LOC of explicit `from ... import X, Y, Z` lines + `__all__` declaration — explicit imports preferred over `import *` per convention).

**Domain split (verified 2026-05-19 by reading exceptions.py class headers):**
- `exceptions_base.py` (7 classes, ~110 LOC): `GameException`, `StateException`, `FrozenStateException`, `ValidationException`, `ResourceException`, `MissingResourceException`, `PersistenceException`.
- `exceptions_strategy.py` (5 classes, ~95 LOC): `StrategyException`, `SessionInitializationError`, `EnginePhaseError`, `TurnFailedError`, `BattleResolutionError`.
- `exceptions_simulation.py` (3 classes, ~30 LOC): `SimulationException`, `ComponentException`, `FormulaException`.
- `exceptions_llm.py` (8 classes, ~85 LOC): `LLMException`, `LLMConfigError`, `LLMNetworkError`, `LLMResponseError`, `LLMRateLimited`, `LLMTimeoutError`, `LLMCancelled`, `LLMUnexpectedError`.
- `exceptions_image.py` (8 classes, ~80 LOC): `ImageException`, `ImageConfigError`, `ImageNetworkError`, `ImageResponseError`, `ImageRateLimited`, `ImageTimeoutError`, `ImageCancelled`, `ImageUnexpectedError`.

**Re-export aggregator (new `exceptions.py`):**
```python
"""Exception hierarchy re-exports.

This module is a thin aggregator over the domain-split exception modules.
All 27+ exception classes are still importable from `game.core.exceptions`
for back-compat with the 250+ caller files in the repo.

Direct imports from the domain submodules are also supported.
"""
from game.core.exceptions_base import *  # noqa: F401, F403
from game.core.exceptions_strategy import *  # noqa: F401, F403
from game.core.exceptions_simulation import *  # noqa: F401, F403
from game.core.exceptions_llm import *  # noqa: F401, F403
from game.core.exceptions_image import *  # noqa: F401, F403
```

Each domain submodule declares its own `__all__`. The aggregator's `__all__` is the union.

**Checkpoint (PowerShell-safe):** `(Get-Content game/core/exceptions.py | Measure-Object -Line).Lines` returns < 80 (the re-export aggregator with explicit per-name imports per convention; aligns with phase_4_checklist target); each submodule LOC measured similarly is under 200 LOC; 250+ existing `from game.core.exceptions import ...` imports continue to work without change; sharded suite green.

### Phase 5: Document remaining over-ceiling files as "next-touch" rule in decisions.md
The other 9 F-C-027 files become a documented "next-touch" rule: when an agent touches any of them for an unrelated reason, they do an extract-by-responsibility pass before merging. This codifies Codex r4's "Keep the other 10 over-ceiling simulation files as 'next touch', not inline scope" principle for the UI side.

**Decisions.md row template:**
```
| 2026-05-XX | F-C-027 follow-up: 9 over-ceiling UI files become a "next-touch" rule | After top-3 extractions in Phases 1-3, the remaining 9 files (empire_build_queue_window 734, event_log_window 732, race_summary_panel 732, empire_panel_window 724, build_queue_controller 723, system_tree_panel 711, design_selector_window 708, strategy_detail_fmt 707, new_game_setup_screen 734) stay over 500 LOC. Per Codex r4, do not force-project them; instead, document a rule: when an agent touches any of them for an unrelated reason, they do a same-recipe extract pass before merging. The agent records the post-extraction LOC in their commit message. |
```

**Checkpoint:** decisions.md row appended; CLAUDE.md or AGENTS.md updated with a one-line cross-reference if the touching-agent guidance belongs there.

## Dependencies & Sibling Projects

**Group B serial order (coordinator-confirmed 2026-05-19): `PROJ-453 → PROJ-454 → PROJ-456 → PROJ-457`.** PROJ-457 is the LAST project Group B's run agent executes. Its Phase 0 re-measurement gate requires PROJ-456 (immediate predecessor) to be unambiguously Complete.

| Project | Status | Relationship |
|---------|--------|--------------|
| **PROJ-453** (engine + services polish) | Active — **Group B predecessor** | Already complete by the time PROJ-457 starts. No file overlap with `game/ui/` or `game/core/exceptions.py`. |
| **PROJ-454** (services + facade retirement) | Active — **Group B predecessor** | Already complete by the time PROJ-457 starts. No file overlap. |
| **PROJ-456** (UI shim retirement) | Active — **HARD Group B predecessor** | **MUST be Complete before PROJ-457 starts.** PROJ-456's shim retirement drops UI LOC for several of PROJ-457's target files (`battle_setup/screen.py`, `new_game_setup_screen.py`, etc.). PROJ-457 Phase 0 re-measures ALL F-C-027 files after PROJ-456 ships — some may drop under 500 naturally and require rescope (Phase 0 escalation gate). |
| PROJ-458 (UIWindow retrofit completion) | Active — **Group C** | Parallel-safe — PROJ-458 touches `settings_window.py`, `atmosphere_target_editor.py`, `gravity_target_editor.py`, `water_target_editor.py`, `radiation_shield_editor.py`; PROJ-457 doesn't touch any of those. |
| PROJ-459 (strategy data LOC extractions) | Active — **Group A** | Doc collision risk on `docs/01_ARCHITECTURE.md` + `docs/02_PATTERNS.md` — see the "Doc consolidation rule (cross-group)" section below. Production file sets are disjoint. |
| PROJ-460 (simulation clean-cut LOC extractions) | Active — **Group C** | Doc collision risk on `docs/01_ARCHITECTURE.md` + `docs/02_PATTERNS.md` — see the "Doc consolidation rule (cross-group)" section below. Production file sets are disjoint. |

**No worktrees** per user standing preference. Serial execution in `main` checkout.

## Related Documents

- [design.md](design.md) — design rationale for the same-recipe extraction pattern.
- [decisions.md](decisions.md) — full decisions log; the Phase 5 "next-touch" rule lands here.
- [findings/PROJ-457_findings.md](findings/PROJ-457_findings.md) — 2 owned findings (F-C-027 top-3, F-C-028).
- [manifest.md](manifest.md) — file-touch list grouped by phase.
- Codex r4 audit redesign: [`AgentCoordination/Scratchpad/Consult/20260519T004841Z_stages-1-2-audit-and-redesign/response.md`](../../../AgentCoordination/Scratchpad/Consult/20260519T004841Z_stages-1-2-audit-and-redesign/response.md) — Job 9 row.
- Original bucket scan (2026-05-18): [`Projects/archived_projects/PROJ-446/findings/bucket_c_ui_core_tests_scan.md`](../../archived_projects/PROJ-446/findings/bucket_c_ui_core_tests_scan.md).
- Pattern reference (re-export shim): `docs/02_PATTERNS.md` §36 — guidance for the Phase 4 `exceptions.py` re-export aggregator.
- Convention reference: `docs/03_CONVENTIONS.md` "File Size" — 500-LOC ceiling + "Preserve public API with a re-export shim only when many callers exist."

## Doc consolidation rule (cross-group)

PROJ-457 (this), PROJ-459 (Group A — strategy data LOC extractions), and PROJ-460 (Group C — simulation clean-cut LOC extractions) all update `docs/01_ARCHITECTURE.md` and `docs/02_PATTERNS.md`. To avoid 3-way merge conflicts:

- PROJ-457's plan.md and decisions.md describe doc changes **WITHOUT applying them inline**. The phase checklists must NOT `Edit` `docs/01_ARCHITECTURE.md` or `docs/02_PATTERNS.md` during normal phase execution.
- When PROJ-457 is complete (typically after the `exceptions.py` split entry plus the build_queue / planet_list / test_lab extractions), record the intended doc additions as a structured **"Pending doc consolidation"** block in `decisions.md`. The block should enumerate: target file (`docs/01_ARCHITECTURE.md` or `docs/02_PATTERNS.md`), section heading or anchor, exact text to insert/replace, and the originating phase + finding.
- Whichever of PROJ-457 / PROJ-459 / PROJ-460 finishes **LAST** is responsible for applying ALL three projects' pending doc additions as a single consolidated edit to `docs/01_ARCHITECTURE.md` + `docs/02_PATTERNS.md`. The last-finishing run agent reads the "Pending doc consolidation" blocks from each project's `decisions.md`, merges them, and ships a single PR covering all three projects' doc deltas.
- If PROJ-457 finishes last, its run agent owns the consolidated edit. Otherwise, PROJ-457's pending entries sit in decisions.md awaiting pickup by whichever of the other two finishes last.

## Verification

### Project Start (REQUIRED)
- [ ] PROJ-456 complete (all 14 owned findings resolved; sharded suite green).
- [ ] Read `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md` (§36 re-export shim), `docs/03_CONVENTIONS.md` (file-size convention).
- [ ] Run full test suite: `python Tools/test_sharded/test_sharded.py` — all tests pass (establishes baseline).

### After Each Phase
- [ ] Targeted tests for the touched cluster pass.
- [ ] Sharded suite green (no regression).
- [ ] LOC re-measured (PowerShell-safe): `(Get-Content <target file> | Measure-Object -Line).Lines` matches the phase exit criterion.
- [ ] `plan.md` Quick Status table updated for the closed phase.
- [ ] Current State `Last Updated` / `Active Phase` / `Last Action` / `Next Action` updated.

### Final Verification (after Phase 5) — PowerShell-safe
- [ ] `(Get-Content game/ui/screens/build_queue_screen.py | Measure-Object -Line).Lines` < 500.
- [ ] `(Get-Content game/ui/screens/planet_list_window.py | Measure-Object -Line).Lines` < 500.
- [ ] `(Get-Content game/ui/screens/test_lab/screen.py | Measure-Object -Line).Lines` < 500.
- [ ] `(Get-Content game/core/exceptions.py | Measure-Object -Line).Lines` < 80 (the re-export aggregator with explicit per-name imports; aligned with phase_4_checklist target).
- [ ] All 250+ existing `from game.core.exceptions import ...` imports work (sharded suite confirms).
- [ ] "Next-touch" rule documented in `decisions.md` and referenced from CLAUDE.md / AGENTS.md if appropriate.
- [ ] Sharded suite green: `python Tools/test_sharded/test_sharded.py`.
- [ ] Codex end-of-project consult landed; verified findings remediated.
- [ ] User applies the `verified` label.
