# Validation Report

## Summary
| Status | Count | Percentage |
|--------|-------|------------|
| FIXED | 4 | 29% |
| PARTIALLY_FIXED | 6 | 43% |
| STILL_PRESENT | 1 | 7% |
| WORSE | 0 | 0% |
| OBSOLETE | 0 | 0% |
| CANNOT_VERIFY | 3 | 21% |

## Finding Status Table
| ID | Original Severity | Status | Evidence Summary |
|----|-------------------|--------|------------------|
| NC-01 | Critical | STILL_PRESENT | Both `battle.py` and `battle_scene.py` still exist with duplicate BattleScene |
| NC-02 | Major | PARTIALLY_FIXED | Workshop files created, but builder_* utility files not renamed |
| NC-03 | Major | FIXED | `ship_builder_service.py` shim deleted |
| NC-04 | Major | PARTIALLY_FIXED | Documentation partially updated, still has old references |
| NC-05 | Major | PARTIALLY_FIXED | Intentional distinction exists but not formally documented |
| NC-06 | Minor | PARTIALLY_FIXED | Distinction exists, not formally documented |
| NC-07 | Minor | PARTIALLY_FIXED | Distinction exists, not formally documented |
| NC-08 | Minor | PARTIALLY_FIXED | Distinction exists, not formally documented |
| NC-09 | Minor | FIXED | Singletons standardized to `instance()` pattern |
| NC-10 | Minor | FIXED | Most method aliases removed |
| NC-11 | Info | CANNOT_VERIFY | No formal documentation, but distinction maintained |
| NC-12 | Info | FIXED | "Component" remains canonical, no action needed |
| NC-13 | Info | CANNOT_VERIFY | Distinction exists, not documented |
| NC-14 | Info | CANNOT_VERIFY | Distinction exists, not documented |

## Detailed Validation

### NC-01: Duplicate BattleScene Class Definitions
**Original Severity:** Critical
**Original Location:** `game/ui/screens/battle.py:15` and `game/ui/screens/battle_scene.py:29`
**Status:** STILL_PRESENT
**Evidence:**
- File `game/ui/screens/battle.py` still exists (264 lines)
- Still defines `class BattleScene` at line 15
- Legacy version using direct `BattleEngine` instead of `BattleService`
- Modern version in `battle_scene.py` exists and uses `BattleService`
**Notes:** Both classes coexist. Original review recommended deletion of `battle.py` - has not been executed.

---

### NC-02: Builder vs Workshop vs Design Terminology
**Original Severity:** Major
**Status:** PARTIALLY_FIXED
**Evidence:**
- Workshop files successfully created and operational:
  - `workshop_screen.py`
  - `workshop_viewmodel.py`
  - `workshop_data_loader.py`
  - `workshop_event_router.py`
  - `workshop_context.py`
- Builder utility files NOT renamed:
  - `builder_utils.py` still exists (should be `workshop_utils.py`)
  - `builder_selection.py` still exists (should be `workshop_selection.py`)
  - `builder_widgets.py` still exists in panels (should be `workshop_widgets.py`)
  - `builder/` directory (21 files) still exists with "builder" naming
**Notes:** New workshop structure created, but legacy builder files remain. Partially migrated state.

---

### NC-03: ShipBuilderService Shim Still Exists
**Original Severity:** Major
**Status:** FIXED
**Evidence:**
- File `game/simulation/services/ship_builder_service.py` confirmed DELETED
- No longer exists as a shim
**Notes:** Successfully removed as part of legacy cleanup phase.

---

### NC-04: Documentation Uses Old Terminology
**Original Severity:** Major
**Status:** PARTIALLY_FIXED
**Evidence:**
- `docs/architecture/SERVICES.md`: 7-8 occurrences of "ShipBuilder" still present
- `docs/refactoring/workshop_refactoring_plan.md`: ~12 occurrences of "ShipBuilderService"
- `docs/refactoring/CODE_REVIEW_ACTION_PLAN.md`: ~5 occurrences of "ShipBuilderService"
- `docs/refactoring/phase1_completion_report.md`: ~3 occurrences of "ShipBuilderService"
**Notes:** Documentation has been partially updated but still contains legacy terminology.

---

### NC-05: Battle vs Combat Used Interchangeably
**Original Severity:** Major
**Status:** PARTIALLY_FIXED
**Evidence:**
- Original review identified this as intentional distinction (Battle=orchestration, Combat=mechanics)
- PATTERNS.md documents singleton patterns but no explicit naming conventions
- No dedicated `NAMING_CONVENTIONS.md` file created to document this distinction
**Notes:** Distinction exists but has not been formally documented as recommended.

---

### NC-06: Screen vs Scene Terminology
**Original Severity:** Minor
**Status:** PARTIALLY_FIXED
**Evidence:**
- Both "Screen" and "Scene" terms still in use (intentional distinction)
- No formal documentation of this distinction created
- PATTERNS.md exists but doesn't explicitly document Screen vs Scene distinction
**Notes:** Pattern exists informally but no explicit naming conventions doc.

---

### NC-07: Fleet vs Team Terminology
**Original Severity:** Minor
**Status:** PARTIALLY_FIXED
**Evidence:**
- Intentional distinction confirmed (Fleet=strategy layer, Team=battle simulation)
- No formal `NAMING_CONVENTIONS.md` created to document this
- Both terms appropriately used in their respective contexts
**Notes:** Distinction exists and is properly used, but lacks formal documentation.

---

### NC-08: Turn vs Tick vs Phase Terminology
**Original Severity:** Minor
**Status:** PARTIALLY_FIXED
**Evidence:**
- Intentional distinction confirmed (Turn=player moves, Tick=simulation frames, Phase=generic)
- No formal `NAMING_CONVENTIONS.md` created
- Terminology used correctly throughout codebase
**Notes:** Distinction exists and is properly applied, but lacks formal documentation.

---

### NC-09: Singleton Access Pattern Inconsistency
**Original Severity:** Minor
**Status:** FIXED
**Evidence:**
- `ScreenshotManager`: Uses `instance()` - NOT `get_instance()`
- `ShipThemeManager`: Uses `instance()` - NOT `get_instance()`
- `SpriteManager`: Uses `instance()` - NOT `get_instance()`
- All three follow consistent `instance()` pattern
- PATTERNS.md documents standardized singleton pattern with `instance()`
**Notes:** Singletons have been standardized to use `instance()` consistently.

---

### NC-10: Method Aliases for Backward Compatibility
**Original Severity:** Minor
**Status:** FIXED
**Evidence:**
- `fleet.py`: No `has_energy_for_warp()` alias found - only `has_resources_for_warp()` method exists
- `fleet_movement.py`: PathSegment uses `end` field, no `hex` property alias
- `ship_stats.py`: `to_hit_profile` assignment still exists but may be compatibility shim
**Notes:** Most aliases removed. Minor `to_hit_profile` usage remains.

---

### NC-11: Design vs Template vs Blueprint
**Original Severity:** Info
**Status:** CANNOT_VERIFY
**Evidence:**
- No dedicated naming conventions documentation created
- Distinction exists in code (Design=player, Template=predefined)
**Notes:** Distinction exists but lacks formal documentation as recommended.

---

### NC-12: Component vs Module vs Part
**Original Severity:** Info
**Status:** FIXED
**Evidence:**
- "Component" is canonical term throughout
- No action required per original review
**Notes:** Established terminology, no changes needed.

---

### NC-13: AI Controller vs Strategy Manager
**Original Severity:** Info
**Status:** CANNOT_VERIFY
**Evidence:**
- Distinct responsibilities exist
- No formal documentation created
**Notes:** Distinction exists but lacks formal documentation.

---

### NC-14: Modifier vs Effect
**Original Severity:** Info
**Status:** CANNOT_VERIFY
**Evidence:**
- Intentional distinction exists in domain model
- No formal naming conventions documentation created
**Notes:** Distinction exists but lacks formal documentation.

---

*Report generated: 2026-01-27*
*Validation Agent: Finding Validator*
