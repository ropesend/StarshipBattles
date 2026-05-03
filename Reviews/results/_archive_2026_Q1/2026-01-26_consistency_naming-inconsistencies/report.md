# Code Review Report: Naming Inconsistencies

## Metadata
- **Date:** 2026-01-26
- **Type:** Consistency Review
- **Scope:** Entire codebase
- **Agents Used:** 3 (Terminology Hunter x2, Structure Analyzer)

## Executive Summary

- **Total Findings:** 14 naming inconsistency categories
- **Critical:** 1 (duplicate class definition)
- **Major:** 4 (terminology conflicts requiring code changes)
- **Minor:** 5 (documentation/comment updates)
- **Info:** 4 (intentional distinctions to document)
- **Overall Assessment:** The codebase has undergone significant refactoring and has existing cleanup plans. Most naming inconsistencies stem from a partially-completed Builder→Workshop migration. One critical code organization issue exists (duplicate BattleScene classes).

---

## Priority Findings (Top 10)

### 1. CRITICAL: Duplicate BattleScene Class Definitions
**ID:** NC-01
**Location:** `game/ui/screens/battle.py:15` and `game/ui/screens/battle_scene.py:29`
**Issue:** Two files define `class BattleScene` - this is a code organization problem, not just naming.
**Impact:** Potential import confusion, maintenance burden, unclear which implementation is canonical.
**Recommendation:** Delete `battle.py` (legacy version using BattleEngine directly). Keep `battle_scene.py` (modern version using BattleService).
**Effort:** Simple

---

### 2. MAJOR: Builder vs Workshop vs Design Terminology
**ID:** NC-02
**Location:** 214+ occurrences across 26 files
**Issue:** Three different terms used for the ship design feature:
- "Builder" - Legacy term, still in file names (`builder_utils.py`, `builder_selection.py`, `builder_widgets.py`)
- "Workshop" - New UI term (`WorkshopScreen`, `WorkshopViewModel`)
- "Design" - Domain term (`VehicleDesignService`, `DesignLibrary`, `DesignMetadata`)

**Files with "builder" in name (not shims):**
- `game/ui/screens/builder_utils.py`
- `game/ui/screens/builder_selection.py`
- `game/ui/panels/builder_widgets.py`
- `game/ui/screens/builder/` (directory)

**Shim files to delete:**
- `game/ui/screens/builder_screen.py`
- `game/ui/screens/builder_viewmodel.py`
- `game/ui/screens/builder_data_loader.py`
- `game/ui/screens/builder_event_router.py`
- `game/simulation/services/ship_builder_service.py`

**Impact:** Confusion about feature naming, inconsistent codebase.
**Recommendation:**
- Delete shim files (already planned in Phase 2 legacy cleanup)
- Rename utility files: `builder_*` → `workshop_*`
- Standardize: "Workshop" for UI, "Design" for domain
**Effort:** Medium

---

### 3. MAJOR: ShipBuilderService Shim Still Exists
**ID:** NC-03
**Location:** `game/simulation/services/ship_builder_service.py`
**Issue:** Shim file re-exports `VehicleDesignService` as `ShipBuilderService` for backward compatibility.
**Impact:** New code might accidentally use old names.
**Recommendation:** Delete shim, update any remaining imports.
**Effort:** Simple

---

### 4. MAJOR: Documentation Uses Old Terminology
**ID:** NC-04
**Locations:**
- `docs/architecture/SERVICES.md` (11 occurrences of "ShipBuilderService")
- `docs/refactoring/workshop_refactoring_plan.md` (28 occurrences)
- `docs/refactoring/CODE_REVIEW_ACTION_PLAN.md` (6 occurrences)
- `docs/refactoring/phase1_completion_report.md` (7 occurrences)

**Issue:** Documentation still references old names after code was refactored.
**Impact:** Misleading documentation, onboarding confusion.
**Recommendation:** Search/replace old terminology with canonical names.
**Effort:** Simple

---

### 5. MAJOR: Battle vs Combat Used Interchangeably
**ID:** NC-05
**Location:** 110+ files across codebase
**Issue:** Both terms appear to reference the core simulation:
- "Battle": `BattleEngine`, `BattleScene`, `BattleOrchestrator`, `BattleService`
- "Combat": `ShipCombatEngine`, `ShipCombatMixin`, `CombatConstants`, `combat_strategies.json`

**Analysis:** Upon investigation, these have **intentional semantic distinction**:
- **Battle** = Overall engagement orchestration (lifecycle, teams, victory)
- **Combat** = Individual ship fighting mechanics (weapons, damage)

**Recommendation:** Document this distinction in naming conventions guide. No code changes needed.
**Effort:** Simple (documentation only)

---

### 6. MINOR: Screen vs Scene Terminology
**ID:** NC-06
**Location:** `game/ui/screens/` directory
**Issue:** Mixed use of "Screen" and "Scene" for full-screen UI views:
- `BattleScene`, `StrategyScene`, `TestLabScene`
- `BattleSetupScreen`, `NewGameSetupScreen`

**Analysis:** Pattern appears intentional:
- **Scene** = Interactive game modes with continuous updates
- **Screen** = Configuration/setup interfaces

**Recommendation:** Document this distinction. Consider standardizing if team prefers.
**Effort:** Medium (if standardizing) / Simple (if documenting)

---

### 7. MINOR: Fleet vs Team Terminology
**ID:** NC-07
**Location:** Strategy and simulation layers
**Issue:** Both terms used:
- "Fleet": `Fleet` class, `fleet_movement.py`, `fleet_order_processor.py`
- "Team": `team_id`, `team0_ships`, `team1_ships` in BattleEngine

**Analysis:** **Intentional layer distinction**:
- **Fleet** = Strategy/campaign level unit
- **Team** = Battle simulation level grouping

**Recommendation:** Document this distinction. No code changes needed.
**Effort:** Simple (documentation only)

---

### 8. MINOR: Turn vs Tick vs Phase Terminology
**ID:** NC-08
**Location:** Strategy and simulation layers
**Issue:** Multiple timing terms:
- "Turn": `TurnEngine`, strategy layer time unit
- "Tick": `tick_count`, battle simulation frame
- "Phase": Used generically for stages

**Analysis:** **Intentional distinction** by time scale:
- **Turn** = Player-initiated strategic moves (hex-based)
- **Tick** = Automated simulation updates (continuous)
- **Phase** = Generic term for stages within turns/battles

**Recommendation:** Document this distinction. No code changes needed.
**Effort:** Simple (documentation only)

---

### 9. MINOR: Singleton Access Pattern Inconsistency
**ID:** NC-09
**Location:** Multiple singleton classes
**Issue:** Both `instance()` and `get_instance()` patterns used:
- `ScreenshotManager.get_instance()` (alias)
- `ShipTheme.get_instance()` (alias)
- `SpriteManager.get_instance()` (alias)

**Recommendation:** Standardize on `instance()`, remove `get_instance` aliases.
**Effort:** Simple

---

### 10. MINOR: Method Aliases for Backward Compatibility
**ID:** NC-10
**Locations:**
- `game/strategy/data/fleet.py`: `has_energy_for_warp()` → `has_resources_for_warp()`
- `game/strategy/engine/fleet_movement.py`: `PathSegment.hex` → `PathSegment.end`
- `game/simulation/entities/ship_stats.py`: `to_hit_profile` → `total_defense_score`

**Issue:** Old method names kept as aliases.
**Recommendation:** Update callers, remove aliases (already planned in Phase 2).
**Effort:** Simple

---

## Additional Findings

### 11. INFO: Design vs Template vs Blueprint
**ID:** NC-11
**Issue:** Multiple terms for ship configurations:
- "Design" - Player-created configurations (canonical)
- "Template" - Predefined test/data configurations (canonical)
- "Blueprint" - Not actively used (deprecated)

**Recommendation:** Document: Design=player, Template=predefined. Remove "Blueprint" references.
**Effort:** Simple

---

### 12. INFO: Component vs Module vs Part
**ID:** NC-12
**Issue:** "Component" is the canonical term (337+ files). "Module" and "Part" appear rarely.
**Recommendation:** No action needed. "Component" is well-established.
**Effort:** None

---

### 13. INFO: AI Controller vs Strategy Manager
**ID:** NC-13
**Location:** `game/ai/` directory
**Issue:** Both manage AI behavior:
- `AIController` - Per-ship AI decision making
- `StrategyManager` - Global strategy pattern management

**Analysis:** These have **distinct responsibilities**. Not an inconsistency.
**Recommendation:** Document the distinction.
**Effort:** Simple (documentation only)

---

### 14. INFO: Modifier vs Effect
**ID:** NC-14
**Issue:** Both terms used in component system:
- "Modifier" - Configuration/definition (`Modifier`, `ApplicationModifier`)
- "Effect" - Runtime result (`ModifierEffect`, `ModifierEffectEvaluator`)

**Analysis:** **Intentional distinction** in the domain model.
**Recommendation:** Document in naming conventions.
**Effort:** Simple (documentation only)

---

## Findings by Category

### Code Issues (Require Code Changes)

| ID | Severity | Title | Location | Effort |
|----|----------|-------|----------|--------|
| NC-01 | Critical | Duplicate BattleScene class | `battle.py`, `battle_scene.py` | Simple |
| NC-02 | Major | Builder file naming | `builder_*.py` files | Medium |
| NC-03 | Major | ShipBuilderService shim | `ship_builder_service.py` | Simple |
| NC-09 | Minor | Singleton pattern inconsistency | Multiple singletons | Simple |
| NC-10 | Minor | Method aliases | `fleet.py`, `fleet_movement.py`, etc. | Simple |

### Documentation Issues (Require Doc Updates)

| ID | Severity | Title | Location | Effort |
|----|----------|-------|----------|--------|
| NC-04 | Major | Old terminology in docs | `docs/` directory | Simple |
| NC-05 | Minor | Battle vs Combat undocumented | N/A | Simple |
| NC-06 | Minor | Screen vs Scene undocumented | N/A | Simple |
| NC-07 | Minor | Fleet vs Team undocumented | N/A | Simple |
| NC-08 | Minor | Timing terms undocumented | N/A | Simple |

### Intentional Distinctions (Document Only)

| ID | Severity | Title | Resolution |
|----|----------|-------|------------|
| NC-05 | Info | Battle vs Combat | Document distinction |
| NC-07 | Info | Fleet vs Team | Document distinction |
| NC-08 | Info | Turn vs Tick vs Phase | Document distinction |
| NC-11 | Info | Design vs Template | Document distinction |
| NC-13 | Info | AIController vs StrategyManager | Document distinction |
| NC-14 | Info | Modifier vs Effect | Document distinction |

---

## Existing Cleanup Plans

This review found that **Phase 2 of the Legacy Cleanup project** already addresses many of these issues:

**File:** `Projects/legacy_cleanup/PHASE_2_REMOVE_SHIMS_ALIASES.md`

**Already Planned:**
- [x] Remove Builder → Workshop shim files
- [x] Remove ShipBuilderService shim
- [x] Remove method aliases (Fleet warp, PathSegment.hex, to_hit_profile)
- [x] Remove singleton aliases

**Not Yet Planned (from this review):**
- [ ] Delete duplicate `battle.py` file
- [ ] Rename `builder_utils.py`, `builder_selection.py`, `builder_widgets.py`
- [ ] Rename `builder/` directory
- [ ] Update documentation terminology
- [ ] Create `NAMING_CONVENTIONS.md`

---

## Recommendations

### Immediate Actions (Critical/Major)

1. **Delete `game/ui/screens/battle.py`** - Removes duplicate BattleScene class
2. **Execute Phase 2 Legacy Cleanup** - Removes shims and aliases
3. **Rename builder utility files** - `builder_*` → `workshop_*`
4. **Update documentation** - Replace old terminology

### Short-Term Improvements

5. **Create `docs/NAMING_CONVENTIONS.md`** - Prevent future inconsistencies
6. **Update architecture docs** - Document intentional distinctions (Battle/Combat, Fleet/Team, etc.)

### Suggested Naming Conventions

| Concept | UI Term | Domain Term | Notes |
|---------|---------|-------------|-------|
| Ship design feature | Workshop | Design | Workshop (UI), Design (data) |
| Battle orchestration | Battle | Battle | Overall engagement |
| Ship fighting | Combat | Combat | Individual mechanics |
| Strategic unit | Fleet | Fleet | Campaign level |
| Battle grouping | Team | Team | Simulation level |
| Strategic time | Turn | Turn | Player-initiated |
| Simulation time | Tick | Tick | Automated frames |

---

## Statistics

| Metric | Count |
|--------|-------|
| Files analyzed | 500+ |
| Naming inconsistency categories | 14 |
| Critical issues | 1 |
| Major issues | 4 |
| Minor issues | 5 |
| Informational items | 4 |
| Files to delete | 6 |
| Files to rename | 4 |
| Documentation files to update | 10+ |

---

## Appendix: Files Referenced

### Files to Delete
- `game/ui/screens/battle.py`
- `game/ui/screens/builder_screen.py`
- `game/ui/screens/builder_viewmodel.py`
- `game/ui/screens/builder_data_loader.py`
- `game/ui/screens/builder_event_router.py`
- `game/simulation/services/ship_builder_service.py`

### Files to Rename
- `game/ui/screens/builder_utils.py` → `workshop_utils.py`
- `game/ui/screens/builder_selection.py` → `workshop_selection.py`
- `game/ui/panels/builder_widgets.py` → `workshop_widgets.py`
- `game/ui/screens/builder/` → `workshop/`

### Documentation to Update
- `docs/architecture/SERVICES.md`
- `docs/refactoring/workshop_refactoring_plan.md`
- `docs/refactoring/CODE_REVIEW_ACTION_PLAN.md`
- `docs/refactoring/phase1_completion_report.md`
- `docs/refactoring/CONSOLIDATION_PLAN.md`
- `docs/refactoring/REMAINING_ISSUES_PLAN.md`

---

*Report generated: 2026-01-26*
*Review type: Consistency (Naming Inconsistencies)*
