# Review Report: Dead Code Cleanup Audit

## Metadata
- **Date:** 2026-02-23
- **Type:** Focused Question Review — Dead Code, Orphaned Files, Unused Artifacts
- **Description:** Comprehensive audit to catalog all dead code for conversion to cleanup project
- **Agents Used:** 6

## Executive Summary
- **Total Actionable Findings:** 25
- **Critical (delete immediately):** 3 (Categories A, B, F)
- **Major (delete with verification):** 4 (Categories D, E, formation_editor duplicate)
- **Minor (cleanup):** 12 (unused imports, misplaced files, empty dirs)
- **Info (keep as-is):** 6 (test_framework, BattlePanel, tkinter_utils, Debugging/)
- **Total Dead LOC:** ~4,288 lines of Python + 1,593 .pyc files (22.8MB)
- **Total Dead Files:** 54 Python files + 176 __pycache__ directories
- **Overall Risk:** VERY LOW — no runtime dependencies on dead code
- **Estimated Cleanup Effort:** ~75 minutes (4 phases)

## Key Outcome: Revised Assessments from Prior Review

Several items from the prior dead code report (DC-001 through DC-027) were **reclassified** after deep investigation:

| Item | Prior Assessment | Revised Assessment | Reason |
|------|-----------------|-------------------|--------|
| test_framework/ (DC-003) | "Orphaned, complex delete" | **KEEP — Active** | Combat Lab UI depends on it; unique functionality |
| Debugging/ (DC-005) | "Delete or archive" | **KEEP — Active** | Active bug tracking workflow |
| BattlePanel (DC-011) | "NotImplementedError stub" | **KEEP — Correct pattern** | Active abstract base with 3 subclasses |
| tkinter_utils.py (DC-008) | "Questionable dependency" | **KEEP — Well placed** | Intentional consolidation (DUP-UI2-001) |

---

## Priority Findings (Top 10)

### 1. CRITICAL: __pycache__ Tracked in Git (22.8MB)
**ID:** DEAD-003 | **Agent:** Trivial Delete Verifier
**Location:** 176 directories, 1,593 .pyc files across entire repo
**Action:** `git rm -r --cached **/__pycache__` — .gitignore already excludes them
**Effort:** Trivial | **Risk:** Zero

### 2. CRITICAL: Legacy Migration Scripts (904 LOC)
**ID:** DEAD-001 | **Agent:** Trivial Delete Verifier
**Location:** `docs/_legacy_docs/Tools/` (10 files)
**Action:** Delete entire directory
**Effort:** Trivial | **Risk:** Zero — zero imports confirmed

### 3. CRITICAL: Duplicate formatimg.py Files (405 LOC)
**ID:** DEAD-002 | **Agent:** Trivial Delete Verifier
**Location:** 5 identical files in `assets/ShipThemes/`
**Action:** Delete all 5 files
**Effort:** Trivial | **Risk:** Zero — zero imports confirmed

### 4. MAJOR: Tools/ Dead Files (1,671 LOC)
**ID:** DEAD-010 | **Agent:** Tools & Scripts Auditor
**Location:** `Tools/` (8 files: component_manager.py, component_graphic_picker.py, process_planet_images.py, resize_components.py, verify_accuracy_formula.py, verify_cache.py, verify_resources.py, cleanup_pygame.py)
**Action:** Delete all 8 files + __init__.py
**Effort:** Trivial | **Risk:** Zero — zero imports confirmed

### 5. MAJOR: scripts/ Dead One-Time Scripts (967 LOC)
**ID:** DEAD-011 | **Agent:** Tools & Scripts Auditor
**Location:** `scripts/` (13 files: apply_resource_costs.py, check_legacy_data.py, find_alias_usages.py, generate_placeholders.py, manage_batches.py, reorg_tests.py, reproduce_cycling.py, repro_energy_stats.py, repro_shield.py, verify_determinism_current.py, verify_planet_names.py, verify_star_scale.py, verify_themes.py)
**Action:** Delete all 13 files
**Effort:** Trivial | **Risk:** Zero — zero imports confirmed

### 6. MAJOR: planet_qc/ Subdirectories (327 LOC)
**ID:** DEAD-012 | **Agent:** Tools & Scripts Auditor
**Location:** `scripts/planet_qc/` (3 files) + `scripts/planet_qc_v2/` (1 file)
**Action:** Delete both subdirectories
**Effort:** Trivial | **Risk:** Zero

### 7. MAJOR: Duplicate formation_editor.py
**ID:** MISPLACED-001 | **Agent:** Misplaced File Auditor
**Location:** `Tools/formation_editor.py` (1,055 LOC) — duplicate of `game/ui/screens/formation_editor.py` (941 LOC)
**Action:** Delete Tools/ version, update game/app.py import, update pytest.ini
**Effort:** Simple | **Risk:** Low — requires import updates

### 8. MINOR: 14 Unused Imports Across 10 Files
**ID:** UNUSED-001 through UNUSED-014 | **Agent:** Unused Import Scanner
**Location:** 10 files in game/ (app.py, battle_controller.py, component.py, battle_engine.py, battle_screen.py, ship.py, registry_loader.py, quickstart_builder.py, empire_panel_window.py, race_setup_screen.py, strategy_panel_manager.py, test_lab/screen.py)
**Action:** Remove 14 unused standard library imports
**Effort:** Trivial | **Risk:** Zero

### 9. MINOR: Misnamed tests/refactor/ Directory
**ID:** MISPLACED-002 | **Agent:** Misplaced File Auditor
**Location:** `tests/refactor/` — regression guard tests, not active refactoring
**Action:** Rename/merge into `tests/regression/`
**Effort:** Trivial | **Risk:** Zero

### 10. MINOR: Empty Directories
**ID:** MISPLACED-003, MISPLACED-004 | **Agent:** Misplaced File Auditor
**Location:** `game/ui/hud/`, `game/simulation/entities/mixins/`
**Action:** Delete empty directories
**Effort:** Trivial | **Risk:** Zero

---

## Confirmed KEEP Items (Not Dead Code)

### test_framework/ — Active Combat Lab Infrastructure
**ID:** TF-001 | **Agent:** test_framework Analyzer
- 17 files, ~2,100 LOC — provides TestRegistry, TestRunner, TestHistory, BattleStateCapture, 6 service classes
- Exclusively used by Combat Lab UI (4 consumer files in game/)
- NOT used by pytest test suite — clean separation
- Unique functionality with no equivalent in simulation_tests
- **Verdict:** KEEP — low maintenance cost, high functional value

### Debugging/ — Active Bug Tracking Workflow
**ID:** LIVE-004 | **Agent:** Trivial Delete Verifier
- 2 files, ~439 LOC — Tkinter-based bug confirmation + auto-archival
- Interdependent pair used for local bug tracking workflow
- **Verdict:** KEEP

### scripts/ Active Tools — 10 Files Worth Keeping (reorganized 2026-03-14)
**ID:** KEEP-001 | **Agent:** Tools & Scripts Auditor
- scripts/: test_sharded.py, test.ps1, loc.py, analyze_dependency_graph.py, find_orphaned_tests.py
- scripts/strategy/: galaxy_screenshot.py, visual_test_galaxy.py, diagnose_blueprints.py
- assets/tools/: process_flags.py, process_planet_spheres.py, nebula_to_alpha.py, ship_background_remover.py
- **Verdict:** KEEP — active development tools and asset processing (reorganized by system)

---

## Configuration Updates Required

| File | Change | When |
|------|--------|------|
| pytest.ini line 5 | `pythonpath = . Tools` → `pythonpath = .` | After Tools/ deletion |
| pytest.ini line 3 | Remove `--ignore=Tools` | After Tools/ deletion |
| game/app.py line 22 | Update formation_editor import path | After MISPLACED-001 |
| tests/unit/builder/test_formation_editor_logic.py | Update import + relocate file | After MISPLACED-001 |

---

## Proposed Project Phases

### Phase 1: Zero-Risk Deletes (~10 minutes)
- [ ] Delete `docs/_legacy_docs/Tools/` (10 files, 904 LOC)
- [ ] Delete 5 `formatimg.py` files from `assets/ShipThemes/`
- [ ] Run `git rm -r --cached **/__pycache__` (176 dirs, 22.8MB)
- [ ] Verify: run `pytest tests/ -n 12`

### Phase 2: Script & Tool Cleanup (~20 minutes)
- [ ] Delete 8 dead files from `Tools/` (1,671 LOC)
- [ ] Delete `Tools/__init__.py`
- [ ] Delete 13 dead scripts from `scripts/` (967 LOC)
- [ ] Delete `scripts/planet_qc/` and `scripts/planet_qc_v2/` directories (327 LOC)
- [ ] Verify: run `pytest tests/ -n 12`

### Phase 3: Formation Editor Migration (~30 minutes)
- [ ] Verify `game/ui/screens/formation_editor.py` has FormationEditorScreen
- [ ] Update `game/app.py` import to use `game.ui.screens.formation_editor`
- [ ] Delete `Tools/formation_editor.py` (1,055 LOC)
- [ ] Move `tests/unit/builder/test_formation_editor_logic.py` → `tests/unit/ui/screens/`
- [ ] Update test imports
- [ ] Update `pytest.ini`: remove `Tools` from pythonpath, remove `--ignore=Tools`
- [ ] Delete `Tools/` directory entirely (should now be empty)
- [ ] Verify: run `pytest tests/ -n 12`

### Phase 4: Polish (~15 minutes)
- [ ] Remove 14 unused imports across 10 files
- [ ] Move `tests/refactor/` contents into `tests/regression/`
- [ ] Delete empty `game/ui/hud/` directory
- [ ] Delete empty `game/simulation/entities/mixins/` directory
- [ ] Verify: run `pytest tests/ -n 12`

---

## Agent Reports

- [Trivial Delete Verifier Report](findings/trivial_delete_verifier_report.md)
- [test_framework Analyzer Report](findings/test_framework_analyzer_report.md)
- [Tools & Scripts Auditor Report](findings/tools_scripts_auditor_report.md)
- [Unused Import Scanner Report](findings/unused_import_scanner_report.md)
- [Misplaced File Auditor Report](findings/misplaced_file_auditor_report.md)
- [Size & Impact Estimator Report](findings/size_impact_estimator_report.md)

---

## Appendix: Statistics

| Metric | Value |
|--------|-------|
| Total Actionable Findings | 25 |
| Critical | 3 |
| Major | 4 |
| Minor | 12 |
| Info (Keep) | 6 |
| Dead Python LOC | 4,288 |
| Dead Python Files | 54 |
| __pycache__ Dirs | 176 |
| .pyc Files | 1,593 |
| __pycache__ Size | ~22.8 MB |
| Config Updates Needed | 4 |
| Agents Used | 6 |

---
*Report compiled: 2026-02-23*
