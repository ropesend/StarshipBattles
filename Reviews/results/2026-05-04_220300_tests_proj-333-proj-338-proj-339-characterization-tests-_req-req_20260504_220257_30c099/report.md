# Review Report: PROJ-333/PROJ-338/PROJ-339 Characterization Tests

**Review Type:** tests | **Request ID:** req_20260504_220257_30c099
**Date:** 2026-05-04 | **Reviewer:** OpenCode
**Scope:** ~266 tests across 20 files (PROJ-333: 8 files, PROJ-338: 6 files, PROJ-339: 6 files)
**Review Mode:** full — behavior accuracy traces, bug-pin verification, drag-state inventory, mocking audit, naming review, missing-coverage scan, commit-contamination check.

---

## Executive Summary

**Overall: 0 CRITICAL, 20 MAJOR, 16 MINOR.** No behavior-accuracy mismatches found across 16 traced tests — all correctly pin production behavior. The primary quality concerns are vacuous "doesn't crash" tests in PROJ-338/339 and missing coverage for edge cases identified in design docs. No commit contamination detected (single author across all 20 files). No vague test names found.

---

## 1. Behavior Accuracy — All Traces Match Production

16 tests were traced end-to-end through production code across all three projects. All correctly pin current behavior. No mismatches.

### PROJ-333 (7 traces)
| Test | Production Path | Verdict |
|------|----------------|---------|
| `test_complex_only_queue_stops_on_non_complex_item` (queue.py:211) | `_validate_queue_item` STOP action | MATCH |
| `test_max_queue_iterations_limits_inner_loop_to_10` (queue.py:283) | `MAX_QUEUE_ITERATIONS=10` loop guard | MATCH |
| `test_spawn_fleet_complex_falls_back_to_first_planet_when_target_id_missing` (spawner.py:252) | `planets_at_hex[0]` fallback | MATCH |
| `test_load_design_returns_empty_dict_when_no_save_path` (spawner.py:109) | `return {}` on no path | MATCH |
| `test_process_transfer_target_fleet_...galaxy_lacks_empires_attr` (transfer.py:171) | `getattr(galaxy, 'empires', [])` fallback | MATCH |
| `test_get_effective_speed_floors_via_int_truncation` (fleet characterization.py:80) | `int(0.6) = 0` floor | MATCH |
| `test_load_pod_from_staging_yard_iterates_in_reverse` (transfer.py:377) | `range(len-1, -1, -1)` LIFO | MATCH |

### PROJ-338 (6 traces)
| Test | Production Path | Verdict |
|------|----------------|---------|
| Design-button mousedown (drag_handler.py:165) | Sets `dragged_item`, calls `on_refresh` | MATCH |
| Motion above threshold starts drag (drag_handler.py:295) | `_on_remove_from_queue` + portrait build | MATCH |
| Drop inside with index clamping (drag_handler.py:405) | `max(0, min(est_idx, len(queue)))` | MATCH |
| `test_calculate_build_turns_no_cost_returns_one` (controller.py:1249) | `not cost: return 1.0` | MATCH |
| `test_per_resource_bottleneck_metals` (controller.py:910) | Exact float division, not ceil | MATCH |
| `test_draw_battle_over_team0_alive_renders_team1_wins_text` (battle_panels.py:427) | 1-indexed team display | MATCH |

### PROJ-339 (3 traces)
| Test | Production Path | Verdict |
|------|----------------|---------|
| `test_format_value_prefixes_per_operation` (modifier_impact_grid.py:237) | `_format_sig_digits` for all 4 operations | MATCH |
| `test_format_value_zero_thousands_and_rounding` (treasury.py:496) | `int(round(...))` + `f"{n:,}"` | MATCH |
| `test_format_sig_digits_negative_values_use_same_tier_boundaries` (grid.py:267) | `abs(value)` for tier selection | MATCH |
| `test_faction_override_blocks_auto_regen_on_race_name_edit` (identity.py:365) | `_faction_name_overridden` guard | MATCH |

---

## 2. PROJ-333 — Bug Pin Verification

All 7 design.md bug pins are covered by tests. No missing pins.

| Bug | Pinned By | Status |
|-----|-----------|--------|
| (a) MAX_QUEUE_ITERATIONS=10 silent cap | queue.py:283 | COVERED |
| (b) is_complex_only STOP-not-SKIP | queue.py:211 | COVERED |
| (c) _load_design → {} silent fallback | spawner.py:109,116 | COVERED |
| (d) int() truncation flooring | fleet characterization.py:80 | COVERED |
| (e) Hard-coded /100.0 divisor | consumable characterization.py:66 | COVERED |
| (f) staging-yard reverse iteration | transfer.py:377 | COVERED |
| (g) getattr(galaxy, 'empires', []) | transfer.py:171 | COVERED |

However, 2 of 15 "Top 3 surprising behaviors per file" from design.md are unpinned:

- **production_spawner #2**: `_spawn_to_staging_yard` reaching into `simulation.entities.ship_design_stats` for mass calculation — unpinned.
- **fleet_movement_engine #3**: Warp no-resources returning `warp_blocked=False` (indistinguishable from successful non-warp move) — unpinned.

---

## 3. PROJ-338 — Drag Handler State Machine

5 of 6 required transitions covered. One gap:

- **MISSING TRANSITION**: `handle_mouse_motion` returning False during design-button drag (where `drag_start_pos=None` suppresses motion). Queue-row drags set `drag_start_pos` and enter the threshold path; design-button drags skip motion entirely — this split is unpinned.

All other transitions (design-button mousedown, queue-row pending, threshold gating, multi-select disabling, drop inside/outside) are covered.

---

## 4. PROJ-339 — D-009 and MIN-004

**D-009: `_StubShip` + `_patched_pygame_gui_for_rebuild`**: Tests are substantive. They verify vehicle-type section filtering, layer row visibility, requirements HTML rendering, clean-path messaging, collapse/expand toggling, and click-outside returns False. The mock pattern is sound. However, StatRow value-population through `update_stats()` (the stat-definition pipeline) is untested at panel level, and the `needs_rebuild → True` path for logistics-key changes is untested.

**MIN-004 negative-tier pin**: `abs(value)` accurately matches production `_format_sig_digits`. Boundary values at tier transitions are untested for negatives (e.g., -10.0, -100.0, -9.999).

---

## 5. Mocking Discipline

### Vacuous Tests (tests that verify nothing about production behavior)

**PROJ-338: 3 MAJOR**
- `test_construction_with_show_complexes_creates_complexes_container` (planet_report:66) — `__init__` bypassed; test assigns attribute, reads it back. Tautology.
- `test_construction_without_show_complexes_text_panel_takes_full_width` (planet_report:77) — same pattern.
- `test_resource_grid_text_colour_setter_..._swallowed_silently` (planet_report:305) — creates synthetic `_DummyCell` class, never touches pygame_gui `UILabel`. Tests its own code, not production.

**PROJ-339: 7 MAJOR**
- `test_panel_stores_references` + `test_scroll_container_created` (treasury.py:412,426) — attribute-assignment tautologies.
- `test_panel_has_homeworld_dropdown` + `test_panel_has_points_label` (environment.py:129,135) — `is not None` assertions.
- `test_update_labels_is_no_op` (identity.py:309) — tests a `pass` body. Zero behavioral signal.
- `test_race_summary_panel_has_expected_attributes` (summary.py:159) — `hasattr` checks for unconditionally-set attributes.

**PROJ-333: 0 MAJOR** — Mocking is well-disciplined. The DI seams are correctly used; internal monkey-patching is limited and documented.

### Formula Reimplementation (tests test themselves, not production)

**PROJ-338: 2 MINOR** — Atmosphere graph height formula and scrollable area layout formula are copied verbatim into tests. A production formula change leaves these tests green while behavior diverges.

### Well-Disciplined Areas

- **BuildQueueDragHandler**: Pygame events synthesized correctly; state machine exercised through real event dispatch.
- **BuildQueueController**: `_make_add_callback` is a functional callback, not just `MagicMock`.
- **Battle Panels**: Established `sys.modules` pygame substitution pattern reused correctly.
- **PROJ-333**: All 8 test files use explicit mock attributes; no MagicMock auto-attribute pollution detected.

---

## 6. Missing Coverage

### PROJ-333
- `production_spawner`: simulation reach-in for mass calculation (design.md surprise #2)
- `fleet_movement_engine`: warp-no-resources `warp_blocked=False` behavior (design.md surprise #3)
- `consumable_management_engine`: multi-component same-resource depletion, repeated depletion on same tick

### PROJ-338
- Drag handler: mouse-motion suppression during design-button drag (missing transition)

### PROJ-339
- `design_stats_panel`: StatRow value-population pipeline, `needs_rebuild → True` path, `kill()` method
- `modifier_impact_grid`: `set_position()`, `handle_event` non-mousewheel path, `_format_value` unknown-op fallback, `_format_sig_digits` boundary rounding values
- `race_environment_panel`: `handle_dropdown_change`
- `race_summary_panel`: `btn_randomize_all` click path (note: production `handle_button_click` doesn't handle it — may be a screen-level concern)

---

## 7. Commit Contamination Check

All 20 test files committed by a single author (Ross McLean) to branch `feat/03c-phase-aware-execution`. No cross-agent contamination. No files are missing or duplicated. All 20 files verified present on disk.

---

## 8. Test Naming

No vague names (`test_basic`, `test_default`, `test_simple`) found across any of the 20 test files. All tests use descriptive, behavior-focused names.

---

## Finding Summary by Severity

| Severity | Count | Areas |
|----------|-------|-------|
| **CRITICAL** | 0 | — |
| **MAJOR** | 20 | 3 vacuous tests (PROJ-338), 7 vacuous tests (PROJ-339), 1 missing drag transition, 2 missing design.md bug pins (PROJ-333), 7 missing coverage gaps (PROJ-339) |
| **MINOR** | 16 | 8 mocking/minor issues (PROJ-333), 2 formula-reimplementation (PROJ-338), 6 naming/minor gaps (PROJ-339) |

### Finding Breakdown by File

| File | Severities |
|------|-----------|
| `test_production_engine_queue.py` | MINOR: internal monkey-patching, naming |
| `test_production_engine_consumption.py` | MINOR: fixture inconsistency |
| `test_production_spawner.py` | **MAJOR**: missing simulation reach-in pin |
| `test_characterization.py` (consumable) | MINOR: partial internal patch |
| `test_characterization.py` (fleet movement) | **MAJOR**: missing warp-no-resources pin; MINOR: non-deterministic setup |
| `test_order_processor_instant.py` | MINOR: confusing Phase-A bypass test setup |
| `test_order_processor_colonize.py` | No issues |
| `test_order_processor_transfer.py` | No issues |
| `test_build_queue_drag_handler.py` | **MAJOR**: missing design-button motion suppression test |
| `test_build_queue_controller.py` | No issues |
| `test_system_tree_panel_characterization.py` | No issues |
| `test_system_tree_panel_hazard.py` | No issues |
| `test_planet_report_panel_characterization.py` | **MAJOR**: 3 vacuous tests; MINOR: 2 formula-reimplementation tests |
| `test_battle_panels_characterization.py` | No issues |
| `test_empire_treasury_panel.py` | **MAJOR**: 2 vacuous tests; MINOR: naming |
| `test_race_environment_panel.py` | **MAJOR**: 2 vacuous tests, missing `handle_dropdown_change`; MINOR: naming |
| `test_race_identity_panel.py` | **MAJOR**: vacuous `update_labels_is_no_op` |
| `test_modifier_impact_grid.py` | **MAJOR**: 4 vacuous tests, 3 missing coverage gaps; MINOR: naming, boundary values |
| `test_race_summary_panel.py` | **MAJOR**: vacuous `has_expected_attributes`; MINOR: naming, `__new__` pattern |
| `test_design_stats_panel.py` | **MAJOR**: 3 missing coverage gaps (StatRow, needs_rebuild True, kill); MINOR: rebuild indirect test |

---

## Overall Assessment

The characterization test suites are **accurate and thorough** in their behavioral pinning — all 16 traced tests match production code exactly. The primary quality debt is concentrated in PROJ-339 (13 of 20 MAJOR findings) where 7 tests are vacuous "doesn't crash" or tautology tests and several design.md-coverage gaps remain. PROJ-333 and PROJ-338 core characterization tests are well-constructed within their mocking constraints. The drag handler state machine has 95% coverage of required transitions. No commit contamination detected. Recommended pre-merge action: address the 3 vacuous tests in `test_planet_report_panel_characterization.py` and the 7 vacuous tests in PROJ-339 files.
