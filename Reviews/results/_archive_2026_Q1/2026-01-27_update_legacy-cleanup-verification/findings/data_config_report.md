# Data & Config Scout Report

## Summary
- Files Reviewed: 27
- Issues Found: 15
- Critical: 0, Major: 4, Minor: 8, Info: 3

---

## Findings

### MAJOR: Schema Format Inconsistency in Modifier Files
**ID:** NEW-DATA-001
**Location:** `data/modifiers.json`, `data/modifiers_v2.json`, `data/modifiers_v1_backup.json`
**Issue:** Three versions of modifiers exist with fundamentally different schema structures:
- modifiers.json: Uses nested "effects" array
- modifiers_v2.json: Similar but adds different defaults
- modifiers_v1_backup.json: Completely different structure
**Impact:** Systems expecting one schema will fail with another format; validation problems.
**Recommendation:** Consolidate to single schema; remove deprecated versions.
**Effort:** Medium

---

### MAJOR: Empty Component Presets File
**ID:** NEW-DATA-002
**Location:** `data/component_presets.json`
**Issue:** File contains only empty `"presets": {}` object. No presets are defined.
**Impact:** File is unused or incomplete; no component customization available.
**Recommendation:** Either populate with presets or remove file.
**Effort:** Simple

---

### MAJOR: Modifier Schema Mismatch with Component References
**ID:** NEW-DATA-003
**Location:** `data/components.json` and all modifier files
**Issue:** Components define modifiers array but no standardized way to reference modifiers by ID. No validation that referenced modifier IDs exist.
**Impact:** Components can't reliably declare applicable modifiers.
**Recommendation:** Add modifier ID validation; standardize reference pattern.
**Effort:** Medium

---

### MAJOR: Duplicate Modifier Definition
**ID:** NEW-DATA-004
**Location:** `data/modifiers_v2.json`
**Issue:** "efficient_engines" modifier is defined twice in the file.
**Impact:** Duplicate definitions could cause loading errors or unexpected behavior.
**Recommendation:** Remove duplicate definition.
**Effort:** Simple

---

### MINOR: Unprofessional Formation File Naming
**ID:** NEW-DATA-005
**Location:** `data/formations/fucked upformation.json`
**Issue:** Formation file uses profane language in filename.
**Impact:** Unprofessional; appears to be debug data committed to repo.
**Recommendation:** Rename to "irregular_formation.json" or remove.
**Effort:** Simple

---

### MINOR: Incomplete Resource Definition
**ID:** NEW-DATA-006
**Location:** `data/resources.json`
**Issue:** Resource definitions lack metadata: name, description, color, icon, base_storage, generation_rate.
**Impact:** Components reference resources but no metadata exists for display or validation.
**Recommendation:** Add complete resource metadata.
**Effort:** Simple

---

### MINOR: Inconsistent Vehicle Class Type References
**ID:** NEW-DATA-007
**Location:** `data/vehicleclasses.json` and `data/components.json`
**Issue:** Components reference vehicle types in `allowed_vehicle_types` but no validation that types match vehicleclasses definitions. Typo noted: "Superdreadnaugh" misspelled.
**Impact:** Typo would break instantiation silently.
**Recommendation:** Add type validation; fix spelling.
**Effort:** Simple

---

### MINOR: Tech Presets Only Contain Wildcard Unlocks
**ID:** NEW-DATA-008
**Location:** `data/tech_presets/` (3 files)
**Issue:** All three preset files use only wildcard unlocks `["*"]`. No actual tiered progression defined.
**Impact:** early_game.json and mid_game.json appear to be placeholders.
**Recommendation:** Define actual progression tiers or remove placeholders.
**Effort:** Medium

---

### MINOR: Builder Theme Color Scheme Inconsistency
**ID:** NEW-DATA-009
**Location:** `data/builder_theme.json`
**Issue:** Theme defines colors with inconsistent types: some integers, some strings. Font size as string "14" should be integer.
**Impact:** String vs integer inconsistency could cause parsing issues.
**Recommendation:** Standardize field types.
**Effort:** Simple

---

### MINOR: Range Mount Default Value Mismatch
**ID:** NEW-DATA-010
**Location:** `data/modifiers.json` vs `data/modifiers_v2.json`
**Issue:** "range_mount" modifier has different default values (0 vs 1).
**Impact:** Different behavior depending on which file is used.
**Recommendation:** Standardize defaults across versions.
**Effort:** Simple

---

### MINOR: Precision Mount Default Value Difference
**ID:** NEW-DATA-011
**Location:** `data/modifiers.json` vs `data/modifiers_v2.json`
**Issue:** "precision_mount" modifier has different defaults (0 vs 1).
**Impact:** Inconsistent defaults between versions.
**Recommendation:** Standardize defaults across versions.
**Effort:** Simple

---

### MINOR: Missing Tech Tree Cross-Reference Validation
**ID:** NEW-DATA-012
**Location:** `data/techtree.json`
**Issue:** Tech tree nodes define requirement references but no validation that:
- Referenced node_id values exist
- Level ranges match max_levels
- No circular dependencies
**Impact:** Could cause runtime errors if node references non-existent parent.
**Recommendation:** Add validation during loading.
**Effort:** Medium

---

### INFO: Undocumented Formation Schema
**ID:** NEW-DATA-013
**Location:** `data/formations/` directory (7 files)
**Issue:** Formation files contain only "arrows" array. Schema lacks documentation of coordinate system, constraints, or validation rules.
**Impact:** Developers can't understand expected format.
**Recommendation:** Add schema documentation or README.
**Effort:** Simple

---

### INFO: Outdated UI Preset File
**ID:** NEW-DATA-014
**Location:** `data/ui_presets.json`
**Issue:** File contains only test placeholder: `{"Test Preset": {"damage": 10}}`.
**Impact:** Test/placeholder data in production config.
**Recommendation:** Populate with real presets or remove.
**Effort:** Simple

---

### INFO: Component Preset Cross-Reference Gap
**ID:** NEW-DATA-015
**Location:** `data/component_presets.json` and `data/tech_presets/default.json`
**Issue:** Tech presets reference components with wildcard but no validation for specific component references.
**Impact:** Specific component references would not be validated.
**Recommendation:** Add cross-reference validation.
**Effort:** Simple

---

## Files Reviewed

### Component Data (4 files)
1. `data/components.json` - Main component definitions
2. `data/component_presets.json` - Empty file
3. `data/component_recipes.json` - Crafting recipes
4. `data/vehicleclasses.json` - Vehicle type definitions

### Modifier Data (3 files)
1. `data/modifiers.json` - Primary modifier definitions
2. `data/modifiers_v2.json` - Alternative version
3. `data/modifiers_v1_backup.json` - Already flagged (DC-03)

### Formation Data (7 files)
1-7. Various formation JSON files in `data/formations/`

### Tech Tree Data (4 files)
1. `data/techtree.json` - Tech tree definitions
2. `data/tech_presets/default.json`
3. `data/tech_presets/early_game.json`
4. `data/tech_presets/mid_game.json`

### AI/Combat Data (3 files)
1. `data/combat_strategies.json`
2. `data/targeting_policies.json`
3. `data/projectiles.json`

### Resource/UI Data (4 files)
1. `data/resources.json`
2. `data/builder_theme.json`
3. `data/ui_presets.json`
4. `data/battles/` (2 files)

### Theme Data (4 files)
1-4. Race theme JSON files

---

## Key Observations

1. **Multiple Schema Versions** (NEW-DATA-001): Three modifier versions coexisting creates maintenance burden and validation complexity.

2. **Placeholder Files** (NEW-DATA-002, NEW-DATA-008, NEW-DATA-014): Several files contain empty or placeholder data that should be completed or removed.

3. **Cross-Reference Gaps** (NEW-DATA-003, NEW-DATA-007, NEW-DATA-012): No validation for component/modifier/tech tree cross-references.

4. **Inconsistent Defaults** (NEW-DATA-010, NEW-DATA-011): Modifier files have different default values which could cause behavior differences.

---

**Report Generated:** 2026-01-27
**Scout:** Data & Config Scout
**Coverage:** 27/27 files (100%)
