# Phase 2: Script & Tool Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-169 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete confirmed dead files from Tools/ and scripts/ directories (excluding formation_editor.py — handled in Phase 3)

---

## Tasks

### Task 2.1: Delete Dead Tools/ Files [Simple]
**File:** `Tools/` (8 files + __init__.py, ~1,671 LOC)
**Tests:** `pytest tests/ -n 12`

- [ ] Verify zero imports for each file (search for filename without extension in codebase)
- [ ] Delete `Tools/component_manager.py` (825 lines)
- [ ] Delete `Tools/component_graphic_picker.py` (423 lines)
- [ ] Delete `Tools/process_planet_images.py` (86 lines)
- [ ] Delete `Tools/resize_components.py` (78 lines)
- [ ] Delete `Tools/verify_accuracy_formula.py` (47 lines)
- [ ] Delete `Tools/verify_cache.py` (41 lines)
- [ ] Delete `Tools/verify_resources.py` (138 lines)
- [ ] Delete `Tools/cleanup_pygame.py` (33 lines)
- [ ] Delete `Tools/__init__.py` (empty file)
- [ ] Do NOT delete `Tools/formation_editor.py` yet (Phase 3)
- [ ] Do NOT delete `Tools/README.md` if it exists (may contain useful history)

**Notes:**

---

### Task 2.2: Delete Dead scripts/ Files [Simple]
**File:** `scripts/` (13 files, ~967 LOC)
**Tests:** No test run needed (standalone scripts, not imported)

- [ ] Delete one-time migration scripts:
  - `scripts/apply_resource_costs.py` (121 lines)
  - `scripts/check_legacy_data.py` (37 lines)
  - `scripts/find_alias_usages.py` (50 lines)
  - `scripts/generate_placeholders.py` (61 lines)
  - `scripts/reorg_tests.py` (56 lines)
- [ ] Delete bug reproduction scripts:
  - `scripts/reproduce_cycling.py` (133 lines)
  - `scripts/repro_energy_stats.py` (68 lines)
  - `scripts/repro_shield.py` (53 lines)
- [ ] Delete superseded verification scripts:
  - `scripts/verify_determinism_current.py` (116 lines)
  - `scripts/verify_planet_names.py` (28 lines)
  - `scripts/verify_star_scale.py` (48 lines)
  - `scripts/verify_themes.py` (43 lines)
- [ ] Delete batch management script:
  - `scripts/manage_batches.py` (72 lines)

**Notes:**

---

### Task 2.3: Delete planet_qc/ Subdirectories [Simple]
**File:** `scripts/planet_qc/` (3 files, 262 LOC) + `scripts/planet_qc_v2/` (1 file, 65 LOC)
**Tests:** No test run needed

- [ ] Delete entire `scripts/planet_qc/` directory:
  - `scripts/planet_qc/main.py` (112 lines)
  - `scripts/planet_qc/maintenance_sync.py` (64 lines)
  - `scripts/planet_qc/rename_planets.py` (86 lines)
- [ ] Delete entire `scripts/planet_qc_v2/` directory:
  - `scripts/planet_qc_v2/server.py` (65 lines)

**Notes:**

---

### Task 2.4: Phase 2 Verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] All tests pass
- [ ] Commit Phase 2 changes

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
