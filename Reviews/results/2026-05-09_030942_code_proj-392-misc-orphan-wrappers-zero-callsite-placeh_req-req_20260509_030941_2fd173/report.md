# Review Report: PROJ-392 — Misc Orphan Wrappers + Zero-Callsite Placeholders

**Request ID:** req_20260509_030941_2fd173
**Review Type:** code (normal)
**Completed:** 2026-05-09T03:20:00Z
**Reviewer:** OpenCode (3-agent swarm: semantic migrations, rename/indirection, registry/rule3)

**Scope:** 12 legacy-item cleanup across ~12 production files + ~13 test files. 4 commits on `feat/03c-phase-aware-execution`.

**Reference:** `Projects/active_projects/PROJ-392/findings/verification_report.md`, `Reviews/results/2026-05-07_220621_legacy-audit/`

---

## Headline Answers

1. **Are all 12 symbols GONE?** — 11 of 12 cleanly removed. One internal caller (`new_game_setup_screen.py:348`) still references a deleted static method. **CRITICAL.**

2. **Is the dispatch-registry-KEY retention legitimate config-vs-shim?** — YES. The `'get_crew_required'` key in `GETTERS` dict is a configuration identifier resolved through the standard Registry pattern (Pattern 4). JSON data files reference it as a data value. It is NOT a code shim. **No Rule 3 violation.**

3. **Did the audit-underestimate corrections preserve semantics?** — 6 of 7 corrections fully preserved semantics. One (`LEG-04-006`) missed updating the internal production caller at `new_game_setup_screen.py:348`. **One runtime crash risk.**

---

## Findings

### CRITICAL

**CRIT-001: `new_game_setup_screen.py:348` — deleted static method still called**
- **File:** `game/ui/screens/new_game_setup_screen.py:348`
- **Severity:** CRITICAL
- **Description:** `self.generate_default_save_name()` is called inside `_create_ui()` but the `generate_default_save_name` static method was deleted from `NewGameSetupScreen` in PROJ-392. The method now only exists as `NewGameSetupController.generate_default_save_name()`. The screen class does not inherit from the controller and has no `__getattr__` forwarding. This will raise `AttributeError` when `NewGameSetupScreen` is constructed in production.
- **Missed by tests because:** Test fixtures use `MockNewGameSetupUiBuilder` which bypasses the real `_create_ui()` path. No integration test exercises the production UI construction path.
- **Fix:** Change line 348 to:
  ```python
  self.save_name_input.set_text(NewGameSetupController.generate_default_save_name())
  ```
  Add import if not already present: `from game.ui.screens.new_game_setup_controller import NewGameSetupController`
- **Fingerprint:** `sha256:ec0a5b3f7d2e4c6a8b1f3d5e7a9c2b4d`

### INFO

**INFO-001: Production init path untested for NewGameSetupScreen**
- **File:** `tests/unit/ui/test_new_game_setup.py`, `tests/unit/ui/screens/test_new_game_setup_controller.py`
- **Severity:** INFO
- **Description:** The `NewGameSetupScreen._create_ui()` method (which calls `self.generate_default_save_name()`) is never exercised by the test suite. All tests use `MockNewGameSetupUiBuilder` that bypasses real UI construction. This coverage gap allowed CRIT-001 to go undetected.

---

## Instruction Verification Summary

### Instruction 1: Final grep for 12 deleted/renamed symbols

| # | Symbol | Status | Evidence |
|---|--------|--------|----------|
| 1 | `_priority_sort_key` (LEG-01-001) | ✓ CLEAN | Only in comment at `command.py:14` |
| 2 | `name_input` placeholder (LEG-02-007) | ✓ CLEAN | Zero refs in production or test fixtures |
| 3 | `expanded_ships` alias (LEG-03-025) | ✓ CLEAN | Zero refs on `ShipStatsPanel`; `BattleUI.expanded_ships` is unrelated |
| 4 | `_load_*_image` wrappers (LEG-01-006) | ✓ CLEAN | Zero definitions on `StrategyRenderer` |
| 5 | `get_quickstart_*_dir` wrappers (LEG-01-007) | ✓ CLEAN | Zero definitions in production |
| 6 | `find_path_deep_space` static (LEG-01-009) | ✓ CLEAN | Static method deleted from `galaxy_pathfinding_service.py`; standalone `pathfinding.py:40` is real implementation |
| 7 | `priority_sort_key` wrapper (LEG-01-010) | ✓ CLEAN | Zero function definitions |
| 8 | `_menu_scene` private form (LEG-02-015) | ✓ CLEAN | Zero `Game._menu_scene` references; `ScreenRouter._menu_scene` is different class |
| 9 | `get_asset_manager` alias (LEG-03-010) | ✓ CLEAN | Zero references; all callers use `get_default_asset_manager` |
| 10 | `_get_sector_text` instance method (LEG-03-014) | ✓ CLEAN | Zero references; callers use module-level `get_sector_text` |
| 11 | `get_crew_required` function (LEG-03-016) | ✓ CLEAN | Zero function definitions; dispatch KEY retained |
| 12 | `validate_save_name`/`generate_default_save_name` statics (LEG-04-006) | ⚠ PARTIAL | Static methods deleted but `self.generate_default_save_name()` at line 348 still calls deleted method |

### Instruction 2: Dispatch-registry-key retention

**PASS — Legitimate configuration, NOT a Rule 3 violation.**

- `data/stats_layout.json:284` and `data/stats_sections.json:274` reference `"getter": "get_crew_required"` — data configuration values resolved through `GETTERS` dict → `GETTERS.get()` → `get_total_crew_requirement` function.
- The GETTERS dict at `stat_getters.py:396` maps the string key `'get_crew_required'` to the renamed function `get_total_crew_requirement`.
- The dispatch chain: JSON `"getter"` → `stats_config.py:64` string lookup → GETTERS dict → function → invocation. This is the standard Registry pattern (Pattern 4).
- The string `"get_crew_required"` is a configuration identifier, comparable to a database column name — not a code shim.

### Instruction 3: Audit-vs-actual call-site corrections

Detailed results in `findings/agent_semantic_migrations_report.md`. Summary:

| # | Correction | Status | Details |
|---|-----------|--------|---------|
| 1 | LEG-03-025 `expanded_ships` (0→14 readers) | ✓ PASS | 14 test refs migrated to `_expanded_ids` |
| 2 | LEG-02-007 `name_input` (2 test fixtures) | ✓ PASS | Fixture and test fixture cleaned |
| 3 | LEG-01-007 quickstart dirs (4 patches) | ✓ PASS | 4 mock.patch targets retargeted |
| 4 | LEG-01-009 find_path_deep_space (4th caller) | ✓ PASS | `find_hybrid_path` substitution correct |
| 5 | LEG-04-006 new_game_setup (9+2 callers) | ⚠ PARTIAL | 9 test callers + 2 patches migrated correctly, but internal production caller at line 348 missed |
| 6 | LEG-01-006 strategy_renderer images | ✓ PASS | 3 zero-caller wrappers deleted |
| 7 | LEG-03-014 `_get_sector_text` | ✓ PASS | Zero-caller wrapper deleted |

### Instruction 4: `_menu_scene` → `menu_scene` rename

**PASS — Complete.** Detailed results in `findings/agent_rename_indirection_report.md`.

- Zero `Game._menu_scene` references remain.
- Property at `app.py:232-235` uses `_route_get('_menu_scene')` / `_route_set('_menu_scene', value)` — the `'_menu_scene'` is a routing key string, not a Python attribute reference. External API is `game.menu_scene` (public).
- All test callers use `game.menu_scene` (public form).
- `ScreenRouter._menu_scene` is the router's own attribute — unrelated to `Game`.
- PROJ-381 `Game.running` area has no `_menu_scene` references.

### Instruction 5: `get_asset_manager` → `get_default_asset_manager` migration

**PASS — Complete.** Zero `get_asset_manager` references remain. All 14 callers in production use `get_default_asset_manager()` from `game/assets/asset_manager.py`.

### Instruction 6: `_get_total_crew_requirement` rename

**PASS — Complete.** Zero `_get_total_crew_requirement` references. All callers use `get_total_crew_requirement` (public). The dispatch registry at `stat_getters.py:396` maps the key to the new public name.

### Instruction 7: `new_game_setup_screen` wrapper deletion + controller indirection

**PARTIAL — Static wrappers deleted but one internal caller missed.** See CRIT-001. The controller indirection at `controller.py:162` was correctly simplified to call `NewGameSetupController.validate_save_name(...)` directly. All tests migrated correctly. But the production screen's `_create_ui()` at line 348 was not updated.

### Instruction 8: Rule 3 compliance

**PASS — No replacement shim anywhere in PROJ-392 changes.**

Comprehensive sweep (see `findings/agent_registry_rule3_report.md`):
- Zero `@deprecated` markers
- Zero wrapper-shim function definitions remain
- `find_path_deep_space` in `pathfinding.py:40` is a real implementation calling `hex_linedraw` — not a compat shim
- Dispatch-registry-key retention is configuration, not a shim

---

## Limitations

- Agent review covered production and test `.py` files only; JSON data files checked for dispatch keys.
- The CRITICAL finding at `new_game_setup_screen.py:348` was independently confirmed by two agents.
- No manual replay of the full UI construction path — the bug is inferred from static analysis of the dead method call.

---

## Required Remediation

1. **CRIT-001** (fix before deployment): Update `game/ui/screens/new_game_setup_screen.py:348`
   ```python
   # Before (broken):
   self.save_name_input.set_text(self.generate_default_save_name())
   # After:
   self.save_name_input.set_text(NewGameSetupController.generate_default_save_name())
   ```

2. **INFO-001** (follow-up): Add an integration test that exercises `NewGameSetupScreen._create_ui()` to catch init-path regressions.
