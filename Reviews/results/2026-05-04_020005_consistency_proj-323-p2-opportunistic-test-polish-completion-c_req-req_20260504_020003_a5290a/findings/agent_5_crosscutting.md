# Agent 5 Report: Cross-Cutting Consistency

## 1. Count Accuracy

The plan claims "149/149 tasks" complete. However the phase table in `plan.md` uses **item counts** (CAT findings), not task counts:

| Phase | Tasks (Task N.M) | Items (CAT findings) | Plan Table Says | Checked [x] Tasks | Match? |
|-------|-------------------|----------------------|-----------------|-------------------|--------|
| Phase 1 | 32 | 32 | 32 items | 32/32 | YES |
| Phase 2 | 30 | 32 (2 multi-item tasks) | 32 items | 30/30 | **NO** (table says 32 "items" but only 30 tasks) |
| Phase 3 | 46 | 53 (7 multi-item tasks) | 53 items | 46/46 | **NO** (table says 53 "items" but only 46 tasks) |
| Phase 4 | 15 | 15 | 15 items | 15/15 | YES |
| Phase 5 | 26 | 27 (1 multi-item task) | 27 items | 26/26 | **NO** (table says 27 "items" but only 26 tasks) |
| **Total** | **149** | **159** | **159** | **149/149** | **TERMINOLOGY MISMATCH** |

**Raw [x] checkbox counts** (includes sub-items and Phase Completion checkboxes):

| Phase | Total [x] |
|-------|-----------|
| Phase 1 | 68 |
| Phase 2 | 67 |
| Phase 3 | 104 |
| Phase 4 | 34 |
| Phase 5 | 57 |
| **Total** | **330** |

**Verdict:** The plan header table uses the word "items" but lists the CAT-finding counts (159 total). The Current State uses the word "tasks" and lists the Task N.M count (149 total). Both internal counts are internally correct, but the terminology is inconsistent — the table says 32+32+53+15+27=159 "items" while Current State says 149/149 "tasks". A naive reader comparing both sees a 10-item discrepancy. The task-level checkbox count (149/149) is accurate.

## 2. Obsoletion Consistency

**41 items** claimed obsolete because upstream PROJ-321 deleted target files. Verified all 40 unique files across all 5 phases — **all 40 files confirmed deleted** from disk:

| Phase | Files Verified Deleted | Result |
|-------|----------------------|--------|
| Phase 1 | test_cycle_detection.py, test_projectile_manager.py, test_system_tree_panel.py | All deleted |
| Phase 2 | test_three_empire_battle.py, test_flat_shield_bonus.py, test_caption_schemas_validate.py, test_planet_specific_colonization.py, test_colony_demographic_view.py, test_build_queue_screen.py | All deleted |
| Phase 3 | test_testruncard_propulsion.py, test_ship_consumable_manager.py, test_battle_state_serialization.py, test_battle_state_validation.py, test_fleet_validation.py, test_loading.py, test_ship_serialization.py, test_commands.py, test_engine_validation.py, test_fleet_consumable_aggregator.py, test_planet_command_handlers.py, test_resource_transfer.py, test_strategy_menu_panel.py, test_battle_panels_extended.py, test_draw_helpers.py, test_resource_constants.py, test_colonization_facade.py, test_color_helpers.py | All deleted |
| Phase 4 | test_portrait_load_success.py, test_formation_files_have_professional_names.py, test_battle_state_validation.py, test_event_validation.py, test_race_loader.py, test_strategy_menu_panel.py, test_unified_entry_guard.py | All deleted |
| Phase 5 | test_mass_validation.py, test_persistence.py, test_full_roundtrip.py, test_happiness_engine.py, test_save_game_service.py, test_warp_logic_rework.py, test_build_queue_portraits.py | All deleted |

**False-positive [x] checkboxes found on deleted files:**

| Task | Item | Status Claimed | Actual | Problem |
|------|------|---------------|--------|---------|
| 3.3 | `[S11-CAT10-005]` Pod-filtering tests | `[x]` — "Parametrize." | File deleted | Should be marked `_(skipped — upstream project already deleted target file)_` like its sibling S11-CAT10-004 |
| 3.6 | `[S11-CAT10-007]` get_component_status_display tests | `[x]` — "Parametrize." | File deleted | Should be marked `_(skipped — upstream project already deleted target file)_` like its sibling S11-CAT10-006 |

Both tasks have one finding correctly marked skipped but the sibling finding checked as if work was done. The target files (`test_colonization_facade.py`, `test_color_helpers.py`) don't exist on disk. The claimed LOC deltas of ~201 and ~113 respectively cannot represent actual work. These are the only two false positives found across all 159 items.

All other "skipped" notations are consistent: the `_(skipped — upstream project already deleted target file)_` string appears on both the main item checkbox and the verify checkbox line.

## 3. LOC Delta Plausibility

**Claimed totals from decisions.md:**
- Pass 1: 27 substantive items → -838 LOC (\~31 LOC/item)
- Pass 2: 43 items (32 substantive + 10 leave-as-is + 1 deferral) → -580 LOC (\~18 LOC/substantive-item)
- Combined: **~-1,418 LOC**

**Problem:** The per-task LOC numbers in the checklist verify lines are **pre-work estimates from the source review**, NOT actual measured deltas. Many tasks marked "no-op" or "skipped" still carry their original estimate in the verify line (e.g., Task 2.19 claims "LOC delta ≈ 336 (no-op)"). The verify-line LOC deltas sum to far more than -1,418 because (a) they overlap between phases for the same file, and (b) they include skipped/no-op items.

**Overlap examples (same file, multiple phases):**
- `test_fleet_report_filters.py`: Phase 3 (≈370 LOC) + Phase 5 (≈117 LOC) = ≈487 LOC claimed
- `test_fleet_data_source.py`: Phase 1 (≈80 LOC) + Phase 3 (≈93 LOC) = ≈173 LOC claimed
- `test_fleet_speed_calculator.py`: Phase 1 (≈50 LOC) + Phase 3 (≈103 LOC) = ≈153 LOC claimed
- `test_engine_event_emission.py`: Phase 1 (≈28 LOC no-op) + Phase 2 (≈59 LOC) = ≈87 LOC claimed
- `test_callbacks.py` / `test_initialization.py`: Phase 1 work + Phase 2 cross-reference (Phase 2 Tasks 2.8/2.9 explicitly note "addressed in Phase 1")

Naively summing all verify-line LOC deltas across the 5 phases produces **~7,700+ LOC**, which is ~5.4x the claimed actual of -1,418. This is because the verify-line numbers are (a) estimates, (b) count potential without subtracting no-op/skipped, and (c) double-count across phases.

**Plausibility of -1,418:** For 59 substantive items (27 + 32), averaging ~24 LOC/item, the -1,418 figure is **plausible** given the nature of P2 test polish (mock consolidation, parametrization, import hoisting). However, **cannot be independently verified** without a `git diff --stat` against the pre-PROJ-323 baseline.

## 4. Cross-Phase Contradictions

**None found.** Specific cross-phase interactions examined:

| Interaction | Phase 1 | Phase 2 | Assessment |
|-------------|---------|---------|------------|
| `test_callbacks.py` mock dedupe | Task 1.4: CAT-9 simplification, extracted `_patched_research_scene()` helper | Task 2.8: CAT-8 nested patches → notes "addressed by PROJ-323 Phase 1 Task 1.4" | Phase 2 correctly defers to Phase 1 work. No contradiction. |
| `test_initialization.py` mock dedupe | Task 1.6: CAT-9 simplification, extracted `_patched_research_scene()` helper | Task 2.9: CAT-8 nested patches → notes "addressed by PROJ-323 Phase 1 Task 1.6" | Phase 2 correctly defers to Phase 1 work. No contradiction. |

Files appearing in multiple phases (e.g., `test_fleet_data_source.py` in Phases 1+3, `test_fleet_speed_calculator.py` in Phases 1+3) address **different CAT categories** on the same file. Phase 1 addresses CAT-9 (simplifications), Phase 3 addresses CAT-10 (parametrization). These are orthogonal concerns — no contradiction.

No instance found where Phase N claims to have restructured something that Phase M claims to have parametrized in a contradictory way.

## 5. Pass 1/Pass 2 Coherence

**Decisions log claims:**
- Pass 1: 27 substantive items (-838 LOC), 41 obsolete-skipped, 43 deferred to Pass 2
- Pass 2: 43 items (-580 LOC) = 23 substantive Phase 3 + 9 substantive Phase 5 + 10 leave-as-is + 1 documented-rationale deferral (Task 3.34)

**Reconciliation with checklist annotations:** Phase 3 tasks annotated "_(pass 2: ...)_" on 24 tasks (3.1-3.5, 3.7-3.9, 3.12-3.14, 3.16, 3.19-3.22, 3.24, 3.29-3.31, 3.33, 3.38, 3.43-3.44). Phase 5 tasks annotated "_(pass 2: ...)_" on 19 tasks (5.1-5.12, 5.15, 5.17-5.19, 5.23-5.24, 5.26). Total annotated: 43, matching the decisions log.

**Per-task pass annotation patterns are consistent:**
- "pass 2: N passed, ≈X LOC saved" — substantive work done
- "pass 2 leave-as-is: N passed" — reviewed, no change
- "pass 2 obsolete: ..." — file no longer exists
- "pass 2 deferred — see task notes above" — rationale documented (Task 3.10, 3.34)

**One counting subtlety:** Task 3.10 (`test_defense_marker_bindings.py`) is marked `[x]` but annotated "deferred" — the item is **checked as complete** despite no work done. Its LOC delta of ≈43 is stated but unrealized. This is arguably a "leave-as-is" mislabeled as "deferred." Not a contradiction, but a classification inconsistency.

**Assessment: COHERENT.** The Pass 1/Pass 2 decomposition in decisions.md matches the per-task annotations in the checklists. The 43 Pass 2 items break down correctly as 24 Phase 3 + 19 Phase 5.

## 6. Manifest Accuracy

**manifest.md was generated during project initialization and was never updated after upstream PROJ-321 deletions.** It lists 147 file entries. Of these, approximately **42 entries (~29%) reference files that no longer exist on disk** because PROJ-321 deleted them.

These 42 manifest entries correspond exactly to the files flagged as "skipped — upstream project already deleted target file" across the 5 phase checklists. No manifest entry references a non-existent file that ISN'T accounted for by an upstream deletion — the stale entries are all for known-obsolete files.

**However**, two manifest entries reference files that are partially worked-on but fully deleted (the false positives from Section 2):
- `tests/unit/strategy/test_colonization_facade.py` — manifest line 90, says "2 item(s): CAT-10(2)" — but file is deleted (Task 3.3 has 1 skipped + 1 false-positive [x])
- `tests/unit/ui/utils/test_color_helpers.py` — manifest line 143, says "2 item(s): CAT-10(2)" — but file is deleted (Task 3.6 has 1 skipped + 1 false-positive [x])

The manifest's item counts for these files (2 items each) are now misleading since no work could have been done.

**Manifest completeness:** All files in the 5 phase checklists that are NOT claimed obsolete DO exist on disk (spot-checked 9 Key Files from plan.md plus random sampling — all present).

## 7. Findings Summary

| ID | Severity | Description |
|----|----------|-------------|
| FND-CC-001 | **HIGH** | Tasks 3.3 (S11-CAT10-005) and 3.6 (S11-CAT10-007) are checked `[x]` as if work was completed, but their target files (`test_colonization_facade.py`, `test_color_helpers.py`) were deleted by PROJ-321. These are false-positive checkmarks. Combined claimed LOC delta of ~314 is fictitious. Both should be marked `_(skipped — upstream project already deleted target file)_`. |
| FND-CC-002 | MEDIUM | Plan header table says 32+32+53+15+27 = 159 "items" but Current State says 149/149 "tasks." The table uses item (CAT-finding) counts while Current State uses task (Task N.M) counts. Phase 2 has 30 tasks for 32 items, Phase 3 has 46 tasks for 53 items. This source-of-truth confusion creates an apparent 10-item discrepancy. |
| FND-CC-003 | MEDIUM | Per-task LOC delta numbers in verify lines are pre-work estimates from the source review, not actual measured savings. Many are carried forward on "no-op" and "skipped" items (e.g., Task 2.19: "LOC delta ≈ 336 (no-op)"). Naive sum across all phases exceeds ~7,700 LOC vs. the -1,418 claimed actual. The verify lines should either show actual deltas or be marked "(estimated)" / "(no-op — 0 LOC)" clearly. |
| FND-CC-004 | LOW | manifest.md was never updated after PROJ-321 deletions. ~42 of 147 entries (~29%) reference deleted files. This is acknowledged in design.md but the manifest itself carries no staleness warning. |
| FND-CC-005 | LOW | Task 3.10 is marked `[x]` (complete) but the annotated action is "deferred" — it was neither done nor left-as-is with documentation. Its LOC delta of ≈43 contributes to the claimed total without any actual work. Classification is "deferred" which is inconsistent with a `[x]` checkbox. |
| FND-CC-006 | LOW | Phase 2 Tasks 2.8 and 2.9 carry LOC deltas of ≈307 and ≈250 in their verify lines but both note "addressed in Phase 1 Tasks 1.4/1.6." These deltas double-count work done in Phase 1. The verify lines should be ~0 or cross-reference the Phase 1 task. |
| FND-CC-007 | INFO | All 40 unique obsolete-claimed files verified deleted from disk. Obsoletion notations are consistently formatted as `_(skipped — upstream project already deleted target file)_` across all 5 phases (with the two exceptions in FND-CC-001). |
| FND-CC-008 | INFO | The decisions log's Pass 1/Pass 2 decomposition (27 + 43 = 70 non-obsolete items handled across both passes) plus the 41 obsolete-skipped items accounts for 111 of 159 total items. The remaining 48 items are the "no-op"/"leave-as-is" items from Phases 1, 2, and 4 (e.g., Tasks 1.10, 1.13, 1.14, 1.16, 1.18, 2.5, 2.6, 2.11, 2.12, 2.13, 2.15, 2.19, 2.22, 2.24, 2.27, 2.28, 2.30, 4.2, 4.3, 4.8, 4.9, 4.10, 4.12, 4.13, 4.14). Coherent. |
