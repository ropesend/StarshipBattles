# Tools/ and scripts/ Auditor Report

## Summary
- Total files audited: 38
- Tools/ files: 10 (2,726 LOC)
- scripts/ files: 28 (3,106 LOC + 327 in subdirectories)
- Files to DELETE: 26 (~4,759 LOC)
- Files to KEEP: 11 (~1,400 LOC)
- Files to RELOCATE: 1 (formation_editor.py — see Misplaced File Auditor)

---

## Summary Table

| File | Category | Status | Action | Risk | LOC |
|------|----------|--------|--------|------|-----|
| Tools/formation_editor.py | D | Active Tool | Relocate/Merge | Low | 1055 |
| Tools/component_manager.py | D | Dead Code | Delete | Zero | 825 |
| Tools/component_graphic_picker.py | D | Dead Code | Delete | Zero | 423 |
| Tools/process_planet_images.py | D | One-Time Script | Delete | Zero | 86 |
| Tools/resize_components.py | D | One-Time Script | Delete | Zero | 78 |
| Tools/verify_accuracy_formula.py | D | One-Time Script | Delete | Zero | 47 |
| Tools/verify_cache.py | D | Dev Utility | Delete | Zero | 41 |
| Tools/verify_resources.py | D | One-Time Script | Delete | Zero | 138 |
| Tools/cleanup_pygame.py | D | One-Time Script | Delete | Zero | 33 |
| Tools/__init__.py | D | Empty | Delete | Zero | 0 |
| scripts/test_sharded.py | E | Active Dev Tool | Keep | Zero | 413 |
| scripts/loc.py | E | Active Dev Tool | Keep | Zero | 114 |
| scripts/galaxy_screenshot.py | E | Dev Utility | Keep | Zero | 366 |
| scripts/visual_test_galaxy.py | E | Verification | Keep | Zero | 323 |
| scripts/diagnose_blueprints.py | E | Verification | Keep | Zero | 293 |
| scripts/analyze_dependency_graph.py | E | Verification | Keep | Zero | 182 |
| scripts/find_orphaned_tests.py | E | Verification | Keep | Zero | 67 |
| scripts/process_flags.py | E | Asset Processing | Keep | Zero | 174 |
| scripts/process_planet_spheres.py | E | Asset Processing | Keep | Zero | 99 |
| scripts/process_planet_spheres_opt.py | E | Asset Processing | Keep | Zero | 109 |
| scripts/nebula_to_alpha.py | E | Asset Processing | Keep | Zero | 80 |
| scripts/apply_resource_costs.py | E | One-Time Script | Delete | Zero | 121 |
| scripts/check_legacy_data.py | E | One-Time Script | Delete | Zero | 37 |
| scripts/find_alias_usages.py | E | One-Time Script | Delete | Zero | 50 |
| scripts/generate_placeholders.py | E | One-Time Script | Delete | Zero | 61 |
| scripts/manage_batches.py | E | One-Time Script | Delete | Zero | 72 |
| scripts/reorg_tests.py | E | One-Time Script | Delete | Zero | 56 |
| scripts/reproduce_cycling.py | E | Bug Repro | Delete | Zero | 133 |
| scripts/repro_energy_stats.py | E | Bug Repro | Delete | Zero | 68 |
| scripts/repro_shield.py | E | Bug Repro | Delete | Zero | 53 |
| scripts/verify_determinism_current.py | E | One-Time Utility | Delete | Zero | 116 |
| scripts/verify_planet_names.py | E | One-Time Utility | Delete | Zero | 28 |
| scripts/verify_star_scale.py | E | One-Time Utility | Delete | Zero | 48 |
| scripts/verify_themes.py | E | One-Time Utility | Delete | Zero | 43 |
| scripts/planet_qc/main.py | E | One-Time Script | Delete | Zero | 112 |
| scripts/planet_qc/maintenance_sync.py | E | One-Time Script | Delete | Zero | 64 |
| scripts/planet_qc/rename_planets.py | E | One-Time Script | Delete | Zero | 86 |
| scripts/planet_qc_v2/server.py | E | One-Time Script | Delete | Zero | 65 |

---

## Findings

### Major: Tools/ Directory — 8 Dead Files (1,671 LOC)

**ID:** DEAD-010
**File(s):** Tools/ (8 files excluding formation_editor.py and __init__.py)
**Category:** D
**Status:** Confirmed Dead
**Dependencies:** None — zero imports from game/ or tests/ for any of these files
**Risk Level:** Zero
**Action:** Delete all 8 files
**Effort:** Trivial
**Blocked By:** Nothing

**Details per file:**
- **component_manager.py** (825 lines) — Pygame-based UI for managing component tags/images. Hardcoded asset paths. Last modified 2026-01-17. No imports found.
- **component_graphic_picker.py** (423 lines) — Pygame-based UI for selecting component graphics. Last modified 2026-01-03. No imports found.
- **process_planet_images.py** (86 lines) — One-time image conversion script. Hardcoded paths.
- **resize_components.py** (78 lines) — One-time image resizing. Hardcoded sizes.
- **verify_accuracy_formula.py** (47 lines) — Manual formula verification. Logic now in unit tests.
- **verify_cache.py** (41 lines) — Registry cache verification. Now in unit tests.
- **verify_resources.py** (138 lines) — Resource system verification. Refactor complete.
- **cleanup_pygame.py** (33 lines) — Removed pygame.quit() from tests. Already executed.

---

### Major: scripts/ One-Time Scripts — 13 Dead Files (967 LOC)

**ID:** DEAD-011
**File(s):** 13 scripts in scripts/ directory
**Category:** E
**Status:** Confirmed Dead — all are completed one-time scripts or bug reproductions
**Dependencies:** None — zero imports from game/ or tests/
**Risk Level:** Zero
**Action:** Delete all 13 files
**Effort:** Trivial

**Files:**
- apply_resource_costs.py (121), check_legacy_data.py (37), find_alias_usages.py (50)
- generate_placeholders.py (61), manage_batches.py (72), reorg_tests.py (56)
- reproduce_cycling.py (133), repro_energy_stats.py (68), repro_shield.py (53)
- verify_determinism_current.py (116), verify_planet_names.py (28)
- verify_star_scale.py (48), verify_themes.py (43)

---

### Major: planet_qc/ and planet_qc_v2/ Subdirectories — 4 Dead Files (327 LOC)

**ID:** DEAD-012
**File(s):** scripts/planet_qc/ (3 files) + scripts/planet_qc_v2/ (1 file)
**Category:** E
**Status:** Confirmed Dead — batch processing utilities with hardcoded paths, no longer active
**Dependencies:** None
**Risk Level:** Zero
**Action:** Delete both subdirectories entirely
**Effort:** Trivial

---

### Info: Tools/formation_editor.py — Active but Misplaced

**ID:** DEAD-013
**File(s):** Tools/formation_editor.py (1,055 lines)
**Category:** D
**Status:** Active Tool — IMPORTED by game/app.py:22
**Dependencies:** game/app.py, tests/unit/builder/test_formation_editor_logic.py, pytest.ini pythonpath
**Risk Level:** Low
**Action:** See Misplaced File Auditor report (MISPLACED-001) — may be duplicate of game/ui/screens/formation_editor.py
**Effort:** Simple (update imports after relocation)

---

### Info: Retained Scripts (11 files, ~2,220 LOC)

**ID:** KEEP-001
**Status:** Active — development tools, verification utilities, and asset processing scripts
**Files kept:**
- test_sharded.py (413) — Active test infrastructure
- loc.py (114) — Lines of code counter
- galaxy_screenshot.py (366) — Galaxy visualization
- visual_test_galaxy.py (323) — Interactive galaxy testing
- diagnose_blueprints.py (293) — Blueprint verification
- analyze_dependency_graph.py (182) — Dependency analysis
- find_orphaned_tests.py (67) — Test hygiene
- process_flags.py (174) — Flag image processing pipeline
- process_planet_spheres.py (99) — Planet image processing
- process_planet_spheres_opt.py (109) — Optimized planet processing
- nebula_to_alpha.py (80) — Nebula image processing

---

## Proposed Final Organization

### Tools/ Directory: DELETE ENTIRELY
- formation_editor.py → Resolve via MISPLACED-001 (duplicate exists in game/ui/screens/)
- All other files → DELETE (zero dependencies confirmed)
- Update pytest.ini to remove Tools from pythonpath
- Result: Tools/ directory no longer exists

### scripts/ Directory: CURATE
**Keep (11 files):**
- Development tools: test_sharded.py, loc.py
- Visualization: galaxy_screenshot.py, visual_test_galaxy.py
- Verification: diagnose_blueprints.py, analyze_dependency_graph.py, find_orphaned_tests.py
- Asset processing: process_flags.py, process_planet_spheres.py, process_planet_spheres_opt.py, nebula_to_alpha.py

**Delete (17 files + 2 subdirectories):**
- All one-time migration/fix scripts
- All bug reproduction scripts
- All verification scripts superseded by unit tests
- planet_qc/ and planet_qc_v2/ subdirectories

---

## Top 5 Priority Issues

1. **DEAD-010** — Tools/ directory has 8 dead files (1,671 LOC) with zero dependencies
2. **DEAD-011** — scripts/ has 13 dead one-time scripts (967 LOC)
3. **DEAD-012** — planet_qc/ subdirectories are dead (327 LOC)
4. **DEAD-013** — formation_editor.py is misplaced (see MISPLACED-001)
5. **KEEP-001** — 11 scripts worth keeping provide ongoing development value
