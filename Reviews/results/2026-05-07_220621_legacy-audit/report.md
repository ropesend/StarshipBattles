# Legacy Code Audit — Final Report

**Date:** 2026-05-07  
**Review Directory:** `Reviews/results/2026-05-07_220621_legacy-audit`  
**Scope:** 749 production files across `game/` (~161K LOC est.)  
**Phase 1 Findings (deterministic):** 3 module aliases, 1 init re-export, 23 deprecation markers, 22 wrapper delegates, 3 name-pair drifts, 0 save migration, 1 superseded pattern  

---

## 1. Executive Summary

- **Total findings across all categories:** 77 (3 CRITICAL, 22 MAJOR, 39 MINOR, 13 INFO) — after verification deduplication and downgrades
- **Overall posture: DRIFT** — the codebase has accumulated legacy remnants but no active migration code disasters. Most issues are backward-compat wrappers and unplanned deprecation markers.
- **Count of one-PR-deletable items (CRITICAL with zero call sites):** 2 (LEG-01-003, LEG-01-004) — **166 LOC** of deprecated static methods that can be deleted immediately.
- **Rule 3 violations (CLAUDE.md):** 3 CRITICAL findings violate Rule 3 (compatibility shims / transitional re-exports). The `command_handlers.py` shim (LEG-01-005) is marked for deletion but still has 6+ production call sites.
- **Save-migration code:** Phase 1 detected 0. Agent review found 1 instance (LEG-03-008) mislabeled as a "deprecation marker"—it is save-format migration code.

---

## 2. Legacy Inventory by Category

| Category | Count | Critical | Major | Minor | Info |
|----------|-------|----------|-------|-------|------|
| Module aliases | 4 | 1 | 1 | 2 | 0 |
| `__init__.py` re-export shims | 1 | 0 | 0 | 1 | 0 |
| Deprecation markers | 23 | 0 | 0 | 15 | 8 |
| Wrapper delegates | 22 | 2 | 9 | 5 | 6 |
| Duplicate systems | 3 | 0 | 0 | 2 | 1 |
| Save migration code | 1 | 0 | 1 | 0 | 0 |
| Superseded pattern usage | 1 | 0 | 0 | 1 | 0 |
| TYPE_CHECKING-only re-exports | 0 | 0 | 0 | 0 | 0 |
| Partial Protocol implementers | 0 | 0 | 0 | 0 | 0 |
| Additional legacy indicators | 22 | 0 | 11 | 13 | -2 |

**Note:** "Additional legacy indicators" includes findings from agent-driven discovery (shim files, stale PROJ comments, test-only callers, test fallback paths, auto-create singletons). Counts above are pre-deduplication; raw agent reports total 79 findings, reduced to 77 after removing cross-shard duplicates and false positives.

---

## 3. Legacy Removal Scorecard

### Module Aliases (4 findings)
- **CRITICAL:** `command_handlers.py` — entire file is a transitional re-export shim (82 LOC). Docstring says "this shim is transitional." 6 production + 25 test call sites need migration.
- **MAJOR:** `formula_evaluator.py` — 3 aliases (`evaluate_math_formula`, etc.) retained for test imports. 118 test call sites, 0 production.
- **MINOR:** Empty `__init__.py` files (simulation/components/, strategy/data/) — package markers, negligible maintenance cost.

### Wrapper Delegates (22 findings)
- **CRITICAL (2):** `AbilityManager.*_static` methods (56 LOC) and `ModifierManager.*_static` methods (110 LOC) — zero production callers, immediate delete.
- **MAJOR (9):** `strategy_renderer.py` wrappers (3), `quickstart_builder.py` wrappers (2), `new_game_setup_screen.py` wrappers (2), `score_planet_for_race` (1), `ModifierLogic` class-level shim (1).
- **MINOR (5):** `get_asset_manager`, `Ship.to_dict/from_dict`, `planet_naming.to_roman`, `_get_sector_text` — documented Facade/Delegate pattern, low priority.

### Duplicate Systems (3 findings)
- **MINOR (2):** `_get_harvester_info` / `get_harvester_info` (1 call site each), `_iter_components` / `iter_components` (1 legacy call site).
- **INFO (1):** `ModifierLogicService` / `ModifierService` — overlapping method signatures across simulation/UI layers with behavioral divergence.

### Deprecation Markers (23 findings)
All MINOR or INFO. Most are legacy fallback branches guarded by comments. Highlights:
- `planet_order_validator.py` — 2 legacy fallback branches (check by `ability_name`)
- `build_queue_drag_handler.py` / `empire_build_queue_window.py` — test fallback paths
- `battle_setup/controller.py` — save-format migration code mislabeled as deprecation marker (reclassified as MAJOR save-migration finding)

---

## 4. Prioritized Removal Plan

Scored by `severity_weight × layer_weight × LOC_affected`.

| Rank | Finding ID | Category | Severity | Layer | LOC | Score | Action |
|------|------------|----------|----------|-------|-----|-------|--------|
| 1 | LEG-01-004 | Wrapper delegates | CRITICAL | simulation | 110 | 2200.0 | Delete `ModifierManager.*_static` methods (lines 221-330). Zero external callers. |
| 2 | LEG-01-005 | Module aliases | CRITICAL | strategy | 82 | 1640.0 | Migrate 6 production call sites to `from game.strategy.engine.handlers import ...`, then delete `command_handlers.py`. |
| 3 | LEG-01-003 | Wrapper delegates | CRITICAL | simulation | 56 | 1120.0 | Delete `AbilityManager.*_static` methods (lines 286-341). Update 3 test methods. |
| 4 | LEG-03-009 | Wrapper delegates | MAJOR | ui/screens | 55 | 275.0 | Migrate `ModifierLogic` consumers to `ModifierLogicService`. Delete deprecated class. |
| 5 | LEG-04-005 | Save migration | MAJOR | ui/screens | 44 | 220.0 | Remove legacy `side_0`/`side_1` save-format keys from `battle_setup_state.py:257-300`. |
| 6 | LEG-03-022 | Additional legacy | MAJOR | strategy | 15 | 150.0 | Migrate Galaxy backward-compat property forwarders to canonical paths. |
| 7 | LEG-03-008 | Save migration | MAJOR | ui/screens | 20 | 100.0 | Delete legacy toggle migration code in `battle_setup/controller.py:548-568`. |
| 8 | LEG-04-006 | Wrapper delegates | MAJOR | ui/screens | 20 | 100.0 | Migrate callers to `NewGameSetupController`, remove Screen-level static wrappers. |
| 9 | LEG-03-017 | Additional legacy | MAJOR | strategy | 10 | 100.0 | Remove backward-compat save-format handling in `ComponentActivationState.from_dict`. |
| 10 | LEG-04-001 | Module aliases | MAJOR | core | 6 | 90.0 | Migrate 118 test call sites to `FormulaEvaluator.*`, remove 3 module aliases. |
| 11 | LEG-01-007 | Wrapper delegates | MAJOR | strategy | 8 | 80.0 | Inline `Paths.get_starter_*_dir()` calls, delete `quickstart_builder.py` wrappers. |
| 12 | LEG-02-001 | Wrapper delegates | MAJOR | strategy | 5 | 50.0 | Migrate 6 call sites to `calculate_habitability`, remove `score_planet_for_race`. |
| 13 | LEG-01-006 | Wrapper delegates | MAJOR | ui/screens | 9 | 45.0 | Inline `_layer_load_*` calls into callers in `strategy_renderer.py`. |
| 14 | LEG-04-009 | Additional legacy | MAJOR | simulation | 2 | 20.0 | Document `ModifierManager`/`ModifierService` separation; consider renaming for clarity. |

---

## 5. Trend Comparison

First agent-driven run for the legacy audit — no trend data yet. Future runs will compare against this baseline of **3 CRITICAL, 22 MAJOR, 39 MINOR**.

Phase 1 deterministic-only counts (23 deprecation, 22 wrapper, 3 alias, 3 drift) are recorded as a separate baseline for the scanner's raw precision tracking.

---

## 6. Refinement Notes

No refinements yet. The Claude bridge skill `claude-proj-from-legacy-audit` writes proposals here when it converts this review into projects.

---

## 7. Appendices

- **Raw tool outputs:** `Reviews/results/2026-05-07_220621_legacy-audit/raw/`
- **Shard reports:**
  - `Reviews/results/2026-05-07_220621_legacy-audit/findings/legacy_review_01.md` (Shard 01 — 18 findings)
  - `Reviews/results/2026-05-07_220621_legacy-audit/findings/legacy_review_02.md` (Shard 02 — 17 findings)
  - `Reviews/results/2026-05-07_220621_legacy-audit/findings/legacy_review_03.md` (Shard 03 — 22 findings)
  - `Reviews/results/2026-05-07_220621_legacy-audit/findings/legacy_review_04.md` (Shard 04 — 19 findings)
- **Cross-system report:** `Reviews/results/2026-05-07_220621_legacy-audit/findings/legacy_duplicate_systems_cross.md`
- **Verification report:** `Reviews/results/2026-05-07_220621_legacy-audit/findings/verification.md`
- **Manifest:** `Reviews/results/2026-05-07_220621_legacy-audit/raw/manifest.json`
