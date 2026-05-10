# Strategy Layer Legacy Code Audit

**Audit Date:** 2026-02-27
**Scope:** `game/strategy/` directory - production code only

---

## Summary

- **Total Issues Found:** 5
- **Critical:** 0
- **Major:** 2
- **Minor:** 2
- **Info:** 1

---

## Findings

### 1. MAJOR: Placeholder Fields in Design Metadata - Save File Compatibility
**ID:** STR-001
**Location:** `game/strategy/data/design_metadata.py:36-41`
**Issue:** The `sprite_preview` field is marked as reserved for future UI implementation but still serialized to save files as a backward compatibility placeholder.
**Evidence:**
- Line 36-41 defines `sprite_preview: Optional[str] = None` with comment "Reserved for future use"
- Line 40: "This field exists as a placeholder for save file compatibility"
- The field is serialized in `to_dict()` (line 58) and deserialized in `from_dict()` (line 85)
- No code in the codebase uses or reads this field

**Recommendation:** Remove `sprite_preview` field entirely. Per project policy, placeholder fields for "just in case" compatibility should be deleted. The UI will store sprite previews in its own cache, not in strategy-layer metadata. Delete the field definition and all serialization/deserialization code for this field.

**Effort:** Simple

---

### 2. MAJOR: Legacy Behavior in Fleet Colonization - Component Registry Fallback
**ID:** STR-002
**Location:** `game/strategy/engine/fleet_order_processor.py:242-278`
**Issue:** The `process_colonize()` method maintains two code paths: one for modern behavior (with component_registry) and legacy behavior (without component_registry). The legacy path removes the entire fleet instead of just the colony ship.
**Evidence:**
- Line 191-193: Method docstring states "When None, entire fleet is removed (legacy behavior)"
- Lines 242-244: Explicit legacy fallback when `component_registry is None`
- Line 277: Comment "Legacy behavior: remove entire fleet"
- The component_registry parameter is optional with default None (line 176)

**Recommendation:** Remove the legacy behavior path entirely. Either mandate component_registry in the signature or set a reasonable default. The modern behavior (removing only the colony ship) is more correct. Update all call sites to pass component_registry. This is a backward compatibility shim that should be eradicated per project policy.

**Effort:** Medium (requires updating all call sites in production_engine.py, action_execution_engine.py, etc.)

---

### 3. MINOR: Future Production/Expense Sources Placeholder Code
**ID:** STR-003
**Location:** `game/strategy/engine/empire_economy_calculator.py:101-116`
**Issue:** The EmpireEconomyCalculator initializes production and expense categories as zero placeholders for future game features (trade, tribute, mining, etc.) that may never be implemented.
**Evidence:**
- Lines 101-106: Explicitly commented "Placeholder production sources (future implementation)"
- Lines 114-116: Explicitly commented "Placeholder expense categories (future implementation)"
- All these fields are initialized to empty zeros but never modified
- No other code depends on these specific fields

**Recommendation:** Either implement the missing feature categories (trade, tribute, mining) or delete the placeholder fields from `EmpireEconomySnapshot`. If these features are not in the roadmap, remove the placeholder code to keep the snapshot focused on what's actually implemented (colony production and maintenance). Decision depends on game design roadmap.

**Effort:** Simple (if removing) or Complex (if implementing)

---

### 4. MINOR: Metadata Preservation During Design Updates
**ID:** STR-004
**Location:** `game/strategy/systems/design_library.py:148-153`
**Issue:** When a design is updated, the code loads the old metadata to preserve creation date and build history. This is defensive code that would only run if a design is re-saved, which is an edge case.
**Evidence:**
- Lines 148-153: Loads old design file to extract `created_date`, `times_built`, and `is_obsolete`
- Lines 164-167: Updates metadata dict in the design file with preserved metadata
- Similar pattern in `load_design_data()` and elsewhere

**Recommendation:** This is reasonable defensive code, but verify it's actually needed. If designs are created once and only marked obsolete (never modified), the preservation logic can be simplified. Consider whether updates to designs should reset the creation date instead of preserving it.

**Effort:** Simple

---

### 5. INFO: Fleet Order Processing Legacy Note
**ID:** STR-005
**Location:** `game/strategy/engine/fleet_order_processor.py:6`
**Issue:** Header comment mentions "not by TurnEngine at end-of-turn. Name retained for compatibility" in reference to `process_end_turn_orders()`.
**Evidence:**
- Line 6: Comment indicates the method name is retained for compatibility despite behavior change
- The method is called by ActionExecutionEngine during ticks (PROJ-187) not TurnEngine at end-of-turn

**Recommendation:** The name is fine - it accurately describes the purpose of end-turn-action processing. This is documentation of a refactoring, not legacy code. No action needed. Keep the comment for context.

**Effort:** N/A

---

## Non-Issues (Verified as Active Code)

The following items appeared as potential issues but are actively used:

- **`SpatialIndex.get_k_nearest()` / `has_neighbor_within_distance()`** - Used by `GalaxyWarpGenerator` and `PlacementStrategies` for system distribution
- **`Galaxy.get_system_of_object()` / `get_system_of_planet()`** - Used throughout codebase in UI, production, and pathfinding
- **`FleetBattleAdapter`** - Bridge pattern for fleet-to-ship conversion, actively used by conflict resolution
- **`design_library.py metadata preservation`** - Reasonable defensive code, not legacy
- **Save game version checking** - Strict version checking (2.0.0 only) is intentional per policy

---

## Top 5 Priority Issues

### 1. **Remove legacy fleet colonization behavior** (STR-002)
- **Impact:** Fixes inconsistent ship removal logic that could lead to orphaned ships
- **Effort:** Medium
- **Rationale:** This is the clearest backward compatibility shim that should be eradicated

### 2. **Remove `sprite_preview` placeholder field** (STR-001)
- **Impact:** Cleaner save file format, reduces serialization overhead
- **Effort:** Simple
- **Rationale:** No code uses it, it's explicitly a "placeholder for future use"

### 3. **Evaluate placeholder expense/production sources** (STR-003)
- **Impact:** Cleaner data structure if features aren't planned
- **Effort:** Simple (if removing)
- **Rationale:** Avoid maintaining dead code for features that may never ship

### 4. **Verify design metadata preservation necessity** (STR-004)
- **Impact:** Potential simplification of save file logic
- **Effort:** Simple
- **Rationale:** Edge case logic that may be unnecessary

### 5. **Update fleet colonization call sites** (for issue STR-002)
- **Impact:** Eliminates the legacy behavior path entirely
- **Effort:** Medium
- **Rationale:** Required after removing legacy colonization behavior

---

## Recommendations

### Immediate Actions
1. Remove `sprite_preview` from `design_metadata.py` - this is clearly dead placeholder code
2. Create a follow-up task to remove legacy colonization behavior (requires design decision on fleet removal semantics)

### Design Decisions Needed
1. **Colony Ship Removal:** Decide if colonization should always remove only the colony ship (modern) or the entire fleet (legacy). If modern is correct, eradicate the legacy path.
2. **Future Economy Features:** Confirm whether trade, tribute, and mining will be implemented. If not, remove placeholder fields.

### Process Improvement
- The codebase is generally clean with minimal legacy code
- The identified issues are mostly placeholders and compatibility shims
- Project policy of eradicating backward compatibility is being followed well
- No significant technical debt found in the strategy layer

