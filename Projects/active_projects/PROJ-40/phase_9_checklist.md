# Phase 9: Data & Config Cleanup

**Status:** Not Started
**Estimated Effort:** 4-5 hours
**Priority:** Medium

## Overview
Address issues in `data/` JSON files: schema inconsistencies, placeholders, and cross-reference gaps.

---

## Tasks

### 9.1 Consolidate Modifier Schema Versions (NEW-DATA-001)
**Location:** `data/modifiers.json`, `data/modifiers_v2.json`, `data/modifiers_v1_backup.json`
**Effort:** Medium

- [ ] Audit all three modifier files
- [ ] Determine canonical schema format
- [ ] Migrate all modifiers to single format
- [ ] Remove deprecated versions (keep backup in git history)
- [ ] Update all code references to use single file
- [ ] Run: `pytest tests/ -v -k modifier`

---

### 9.2 Populate or Remove Component Presets (NEW-DATA-002)
**Location:** `data/component_presets.json`
**Effort:** Simple

- [ ] Review if component presets are needed
- [ ] If yes: populate with actual presets
- [ ] If no: delete empty file
- [ ] Update any code that references this file
- [ ] Run: `pytest tests/ -v`

---

### 9.3 Add Modifier ID Validation (NEW-DATA-003)
**Location:** `data/components.json` and modifier files
**Effort:** Medium

- [ ] Create validation script or test
- [ ] Check that component modifier references exist
- [ ] Add to data loading validation
- [ ] Run: `pytest tests/unit/data/ -v` or create tests

---

### 9.4 Remove Duplicate Modifier Definition (NEW-DATA-004)
**Location:** `data/modifiers_v2.json`
**Effort:** Simple

- [ ] Find duplicate "efficient_engines" definition
- [ ] Remove one instance
- [ ] Verify file still loads correctly
- [ ] Run: `pytest tests/ -v -k modifier`

---

### 9.5 Rename Unprofessional Formation File (NEW-DATA-005)
**Location:** `data/formations/fucked upformation.json`
**Effort:** Simple

- [ ] Rename to `irregular_formation.json` or similar
- [ ] Update any code references
- [ ] Commit with clear message
- [ ] Run: `pytest tests/ -v -k formation`

---

### 9.6 Add Resource Metadata (NEW-DATA-006)
**Location:** `data/resources.json`
**Effort:** Simple

- [ ] Add name, description fields to each resource
- [ ] Add color, icon references
- [ ] Add base_storage, generation_rate if applicable
- [ ] Run: `pytest tests/ -v -k resource`

---

### 9.7 Fix Vehicle Class Typo (NEW-DATA-007)
**Location:** `data/vehicleclasses.json` and `data/components.json`
**Effort:** Simple

- [ ] Fix "Superdreadnaugh" → "Superdreadnought" spelling
- [ ] Add validation for allowed_vehicle_types references
- [ ] Run: `pytest tests/ -v`

---

### 9.8 Implement Tech Presets Progression (NEW-DATA-008)
**Location:** `data/tech_presets/` (3 files)
**Effort:** Medium

- [ ] Review if wildcard unlocks are intentional
- [ ] If not: define actual progression tiers
  - early_game.json: basic techs only
  - mid_game.json: intermediate techs
  - default.json: all techs
- [ ] Or remove placeholder files
- [ ] Run: `pytest tests/ -v`

---

### 9.9 Fix Builder Theme Type Consistency (NEW-DATA-009)
**Location:** `data/builder_theme.json`
**Effort:** Simple

- [ ] Convert string "14" to integer 14 for font_size
- [ ] Standardize color formats (all integers or all strings)
- [ ] Run: `pytest tests/unit/ui/ -v`

---

### 9.10 Standardize Modifier Defaults (NEW-DATA-010, NEW-DATA-011)
**Location:** `data/modifiers.json` vs `data/modifiers_v2.json`
**Effort:** Simple (combined with 9.1)

- [ ] Standardize "range_mount" default value
- [ ] Standardize "precision_mount" default value
- [ ] Document intended defaults
- [ ] Run: `pytest tests/ -v -k modifier`

---

### 9.11 Add Tech Tree Validation (NEW-DATA-012)
**Location:** `data/techtree.json`
**Effort:** Medium

- [ ] Add validation for node_id references
- [ ] Validate level ranges match max_levels
- [ ] Check for circular dependencies
- [ ] Add to data loading or create test
- [ ] Run: `pytest tests/ -v`

---

### 9.12 Add Formation Schema Documentation (NEW-DATA-013)
**Location:** `data/formations/`
**Effort:** Simple

- [ ] Create `data/formations/README.md`
- [ ] Document "arrows" array format
- [ ] Document coordinate system
- [ ] Document constraints and validation rules

---

### 9.13 Clean UI Presets File (NEW-DATA-014)
**Location:** `data/ui_presets.json`
**Effort:** Simple

- [ ] Review if UI presets are needed
- [ ] If yes: populate with real presets
- [ ] If no: delete placeholder file
- [ ] Update any code references

---

## Verification

- [ ] Run all tests: `pytest`
- [ ] Load game and verify data loads without errors
- [ ] Verify no JSON parsing errors in logs

---

## Notes
- Task 9.1 (modifier consolidation) is the most impactful
- Several tasks can be combined (9.1 + 9.4 + 9.10)
- Consider creating data validation tests as part of this phase
