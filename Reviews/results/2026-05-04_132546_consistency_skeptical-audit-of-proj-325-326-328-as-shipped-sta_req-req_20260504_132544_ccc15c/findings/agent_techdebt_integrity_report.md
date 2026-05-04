# Agent: Tech Debt & Integrity Report
# Scope: Focus Areas 7 (remaining), 8 (remaining), 9
# Date: 2026-05-04
# Verdict: PARTIAL PASS (3 findings)

---

## Focus Area 7: Test Outcome Integrity

### 7.1 — Test Suite Results

```
2309 passed, 1 skipped in 29.58s
```

**Skip identified:** `tests/unit/ui/screens/test_strategy_window_manager_public_api.py:269` — `got empty parameter set for (slot)`

Root cause: the test parametrizes over `sorted(EXPECTED_WINDOW_SLOTS - {"settings_window"} - PROJ_313_MIGRATED_SLOTS)`. When the difference set is empty (all remaining slots are either settings_window or already migrated to PROJ-313's `wm.iter_live_modals()` tracking), pytest correctly skips. **Not a regression.** This is the intended steady-state behavior once all window slots have been migrated.

No unexpected failures. No flaky tests in this slice.

### 7.2 — Git Branch & Commit Integrity

Current branch: `feat/03c-phase-aware-execution` — matches the required branch documented in PROJ-328 plan.md.

The 20 most recent commits touching the specified files are all on this branch. The commit sequence confirms the expected delivery order:
- PROJ-324 foundation (`9ae5c4959`, `849ef56d6`)
- PROJ-325 PoC (`92a7490b6` — RaceSetupScreen two-stage)
- PROJ-326 linter + audit (`fcae158e9`, `849ef56d6`)
- PROJ-328 Phase A (`fd388946d` → `7859d652c` → `00874c571` → `495fa0f39`)
- PROJ-328 Phase B (`e916a213f`)
- PROJ-328 Phase C (`909bfbecf`)
- PROJ-327 Phase 4 (`078be72b8`)

✅ No unexpected commits, no merge noise, clean linear history on the expected branch.

---

## Focus Area 8: Cross-Reference Integrity

### 8.1 — PROJ-325 design.md Path Verification

| Path in design.md | Resolves? | Notes |
|---|---|---|
| `Reviews/results/2026-05-04_020005_.../report.md` | ✅ Yes | Found: `2026-05-04_020005_consistency_proj-323-p2-.../report.md` (line 10) |
| `Reviews/results/2026-05-04_015938_.../report.md` | ✅ Yes | Found: `2026-05-04_015938_consistency_proj-322-p1-.../report.md` (line 11) |
| `AgentCoordination/Scratchpad/plans/proj_321_322_323_continuation_plan.md` | ❌ **BROKEN** | Glob returned zero files matching `AgentCoordination/Scratchpad/plans/proj_32*_continuation_plan.md`. File does not exist. |
| `findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md` | ✅ Yes | Resolves relative to PROJ-325 dir. Found at expected location. |

**FND-CC-REF-001 (LOW):** `proj_321_322_323_continuation_plan.md` is referenced by both `PROJ-325/design.md:12` and `PROJ-326/design.md:12` but does not exist at the cited path. The continuation plan was likely written but never committed, or was written to an ad-hoc path and the reference was never updated. Impact: low — the file is reference-only for design context, not a build dependency. But stale cross-references erode doc trustworthiness over time.

### 8.2 — PROJ-328 plan.md Path Verification

| Path in plan.md | Resolves? | Notes |
|---|---|---|
| `../PROJ-325/findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md` | ✅ Yes | Resolves to `PROJ-325/findings/consensus_discussion/...` relative to PROJ-328 dir (line 115) |
| `game/ui/screens/battle_setup/screen.py` | ✅ Yes | File exists (line 122/128) |
| PROJ-322 checklist files | ✅ Yes | All 6 `phase_N_checklist.md` files exist under `PROJ-322/` |

### 8.3 — docs/known-issues.md UIWindow Blocker Status

**✅ Resolved.** The UIWindow super-init chain blocker section header reads:

> `### **[RESOLVED in PROJ-324 + PROJ-325 PoC + PROJ-328]** UIWindow super-init chain blocker (historical)`

A detailed "Resolution (2026-05-04)" subsection follows (lines 31-40), tracing the resolution across all three projects, listing concrete commits, and noting the canonical pattern is now documented at `docs/02_PATTERNS.md` §33.

---

## Focus Area 9: Tech Debt Opportunity

### 9.1 — DesignWorkshopScreen Deferral

| PROJ | DesignWorkshopScreen mentioned? | Deferral rationale documented? |
|---|---|---|
| PROJ-325 (design.md / plan.md) | No | N/A |
| PROJ-326 (design.md / plan.md) | No | N/A |
| PROJ-328 (design.md / plan.md) | No | N/A |

**DesignWorkshopScreen was NOT addressed or deferred in PROJ-325, 326, or 328.** It is entirely absent from all three projects' planning documents.

Context: `DesignWorkshopScreen` (`game/ui/screens/workshop_screen.py:50`) is a **plain class** — it does NOT extend `pygame_gui.elements.UIWindow` or `StrategyModalWindow`. PROJ-324 plan.md (lines 44-51) correctly notes this: "DesignWorkshopScreen: not a UIWindow, but `__init__` builds a real `pygame_gui.UIManager` + theme files." PROJ-322 phase_3_checklist.md had a deferred task targeting it that was subsequently dropped because the test file was deleted upstream by PROJ-321.

**FND-CC-REF-002 (LOW):** While DesignWorkshopScreen was legitimately out of scope (it's not a UIWindow subclass, so the two-stage construction pattern doesn't apply), no project in this wave explicitly documented the decision. Future agents reading the PROJ-322/324/325/328 chain may wonder why the workshop screen was skipped. A one-line note in `docs/known-issues.md` or PROJ-324 plan.md would close this gap.

### 9.2 — Remaining Un-refactored UIWindow Subclasses

**Only 6 of 17+ UIWindow subclasses were refactored** in the PROJ-325/328 wave. The refactored classes are:
- `RaceSetupScreen` (PROJ-325 Phase 3 PoC)
- `BuildQueueListWindow` (PROJ-328 Phase A)
- `OrdersWindow` (PROJ-328 Phase A)
- `FleetReportWindow` (PROJ-328 Phase A)
- `NewGameSetupScreen` (PROJ-328 Phase B)
- `TransferDialog` (PROJ-328 Phase C)

**Remaining `StrategyModalWindow` subclasses NOT refactored** (verified by grep):

| Class | File | Notes |
|---|---|---|
| `CargoQuickDialog` | `cargo_quick_dialog.py:25` | StrategyModalWindow |
| `EmpireBuildQueueWindow` | `empire_build_queue_window.py:63` | StrategyModalWindow |
| `EmpirePanelWindow` | `empire_panel_window.py:44` | StrategyModalWindow |
| `EventLogWindow` | `event_log_window.py:63` | StrategyModalWindow |
| `FleetSelectionWindow` | `fleet_selection_window.py:38` | StrategyModalWindow |
| `FoodAllocationEditor` | `food_allocation_editor.py:158` | StrategyModalWindow |
| `PlanetAbilitiesWindow` | `planet_abilities_window.py:53` | StrategyModalWindow |
| `PlanetListWindow` | `planet_list_window.py:111` | StrategyModalWindow |
| `PlanetSelectionWindow` | `planet_selection_window.py:25` | StrategyModalWindow |
| `PlanetTargetEditor` | `planet_target_editor_base.py:29` | StrategyModalWindow |
| `StarListWindow` | `star_list_window.py:39` | StrategyModalWindow |
| `SystemSelectionWindow` | `system_selection_window.py:20` | StrategyModalWindow |
| `MoveChoiceWindow` | `move_choice_dialog.py:26` | StrategyModalWindow |

**Direct `UIWindow` subclasses NOT refactored:**

| Class | File | Notes |
|---|---|---|
| `DesignSelectorWindow` | `design_selector_window.py:31` | Direct UIWindow |
| `SettingsWindow` | `settings_window.py:14` | Direct UIWindow |

**FND-CC-REF-003 (MEDIUM):** 13 `StrategyModalWindow` subclasses + 2 direct `UIWindow` subclasses remain on the legacy `__new__` bypass pattern. PROJ-328 plan.md "Out" scope only calls out `BuildQueueScreen` and `WorkshopScreen` as deferred — neither of which are UIWindow subclasses. The 13 remaining StrategyModalWindow subclasses are **silently absent** from the document. They were not explicitly deferred, not included in scope, and not mentioned in any checklist. This is a documentation gap — future agents encountering these classes won't know whether they were overlooked or intentionally left unchanged.

### 9.3 — PROJ-328 "Out" Scope Documentation

PROJ-328 plan.md lines 48-56 document "Out" scope items:
- ✅ `RaceSetupScreen` — owned by PROJ-325 (correct)
- ✅ `BuildQueueScreen` — already uses PanelFactory/Renderer/Controller (correct; it's a StrategyScene, not a UIWindow)
- ✅ `WorkshopScreen` — separate project later (correct; it's not a UIWindow)
- ✅ `make_ui_widget` / `bypass_init` — already landed by PROJ-324
- ✅ `LLMBackgroundCall` — already landed by PROJ-324
- ✅ Test runtime reduction — owned by PROJ-327
- ✅ Linter — owned by PROJ-326
- ✅ PROJ-323 cleanups — owned by PROJ-325

However, the 13 remaining `StrategyModalWindow` subclasses are NOT listed in "Out" scope. They are completely absent from the plan. See FND-CC-REF-003 above.

---

## Summary

| Finding | Severity | Area | Description |
|---|---|---|---|
| FND-CC-REF-001 | LOW | 8.1 | `proj_321_322_323_continuation_plan.md` referenced by PROJ-325 + PROJ-326 design.md but does not exist |
| FND-CC-REF-002 | LOW | 9.1 | DesignWorkshopScreen not a UIWindow (correct exclusion) but deferral undocumented |
| FND-CC-REF-003 | MEDIUM | 9.2 | 15 un-refactored UIWindow subclasses silently absent from PROJ-328 plan; no explicit deferral |

**Test integrity:** Clean. 2309 pass, 1 skip (expected parametric exhaust), on the correct branch.

**Cross-reference integrity:** 1 broken path (continuation plan missing), 4 resolved paths, known-issues.md correctly marked Resolved.

**Tech debt:** The refactor wave correctly excluded non-UIWindow classes (DesignWorkshopScreen, BuildQueueScreen, WorkshopScreen) but failed to document the non-refactored StrategyModalWindow subclasses. 15 UIWindow-inheriting classes remain on the legacy pattern with no tracking.
