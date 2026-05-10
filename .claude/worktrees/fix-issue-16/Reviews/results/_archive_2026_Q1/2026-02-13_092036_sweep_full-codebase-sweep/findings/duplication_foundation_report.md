# Duplication & Fragmentation Sweep: Foundation

## Summary
- **Shard:** Foundation
- **Directories:** game/core/, game/ai/, game/research/, game/engine/
- **Files Scanned:** 39
- **Total Issues Found:** 8
- **Critical:** 0 | **Major:** 3 | **Minor:** 4 | **Info:** 1

## Findings

#### MAJOR: IControllable Protocol Duplicates IShip Protocol
**ID:** DUP-FND-001
**Location:** `game/ai/interfaces/controllable.py:22-260` AND `game/core/protocols.py:380-450`
**Issue:** The `IControllable` interface in the AI layer duplicates significant portions of the `IShip` protocol from core/protocols.py. Both define identical concepts: position access, velocity access, rotation, team_id, is_alive, weapon range, formation methods, and component access. IControllable has 28 abstract methods; IShip has many of the same properties/methods.
**Impact:** Maintenance burden - changes to entity contracts need to be reflected in both places. Risk of divergence between what IControllable expects and what IShip provides.
**Recommendation:** Consider having IControllable extend IShip or consolidate into a single interface hierarchy. IControllable could focus only on AI-specific "write" methods (set_throttle, set_trigger_pulled, rotate) while inheriting the "read" methods from a shared protocol.
**Effort:** Medium - requires careful analysis of dependencies between AI and simulation layers

#### MAJOR: ResearchTracker and ResearchControlPanel State Management Duplication
**ID:** DUP-FND-002
**Location:** `game/research/data/research_tracker.py:84-109` AND `game/research/ui/research_controls.py:340-345`
**Issue:** Both ResearchTracker and ResearchControlPanel have methods for computing and displaying allocated/remaining RP with nearly identical logic. ResearchControlPanel.update_budget_display() recomputes totals that tracker already tracks. The slider range update logic in _update_allocation_slider_range also duplicates the remaining RP calculation.
**Impact:** Low maintenance risk but adds cognitive overhead. If allocation logic changes, multiple places need updating.
**Recommendation:** ResearchControlPanel should use tracker methods directly rather than reimplementing calculations. Consider adding a property to tracker that returns allocation state in a format ready for display.
**Effort:** Simple - straightforward delegation

#### MAJOR: Distance Calculation Pattern Repetition Across AI
**ID:** DUP-FND-003
**Location:** `game/ai/controller.py:197-201`, `game/ai/behaviors.py:155-156,213,296`, `game/ai/combat_utils.py:161`
**Issue:** The pattern `ship_pos.distance_to(target_pos)` or `ship_pos.distance_to(target.position)` appears 10+ times across AI files. While each call site is slightly different (different variable names, different contexts), the pre-computation of distance_cache in controller.py suggests this was identified as a performance concern that was only partially addressed.
**Impact:** Performance - distance calculations are repeated when they could be cached. The controller builds a distance_cache but behaviors don't use it (they calculate distance themselves).
**Recommendation:** Pass the distance_cache to behaviors that need distance calculations, or refactor to compute distances once per update cycle and store them on the controller for behavior access.
**Effort:** Medium - requires passing additional context to behavior.update()

#### MINOR: Singleton Clear/Reset Pattern
**ID:** DUP-FND-004
**Location:** `game/core/registry.py:217-237`, `game/core/profiling.py:39`, `game/core/strategy_metadata.py:54`, `game/ai/strategy_manager.py:53`
**Issue:** Multiple singleton classes implement very similar clear() methods that reset internal state. Each has the pattern: clear dictionaries/lists, reset any cached validators/instances, potentially handle frozen state.
**Impact:** Low - each clear() is appropriately customized for its class. The pattern is natural for singletons.
**Recommendation:** No action needed - this is reasonable singleton lifecycle management. Could potentially extract to SingletonMeta as a base implementation, but the customization needs make this low-value.
**Effort:** N/A

#### MINOR: to_dict/from_dict Serialization Pattern
**ID:** DUP-FND-005
**Location:** `game/research/data/research_tracker.py:22-37,236-255`, `game/core/input_actions.py:290-319`, `game/core/hex_math.py:227-250`
**Issue:** Multiple classes implement to_dict() and from_dict() serialization with similar structure: to_dict returns a dict of attributes, from_dict is a classmethod that creates an instance from a dict. No shared base class or mixin.
**Impact:** Low - this is a common Python pattern and each class has different fields. The boilerplate is acceptable.
**Recommendation:** No immediate action. If more serializable classes are added, consider a SerializableMixin or dataclass-based approach with automatic to_dict/from_dict generation.
**Effort:** N/A

#### MINOR: Flee Direction Calculation
**ID:** DUP-FND-006
**Location:** `game/ai/behaviors.py:70-85` AND inline uses at lines 114, 162, 226-227
**Issue:** The _flee_direction helper is well-extracted, but there's a similar pattern in controller.py's check_avoidance() at line 428-431 that computes `vec = ship_pos - closest.position` followed by normalization - essentially the same flee calculation but inline.
**Impact:** Very low - the check_avoidance pattern is slightly different (uses ship's own position rather than passed-in positions).
**Recommendation:** Could optionally refactor check_avoidance to use _flee_direction, but the benefit is marginal.
**Effort:** Simple

#### MINOR: Registry Provider get_* Methods Duplication
**ID:** DUP-FND-007
**Location:** `game/core/registry.py:319-330` AND `game/core/registry.py:366-376`
**Issue:** DefaultRegistryProvider and TestRegistryProvider both implement get_components(), get_modifiers(), get_vehicle_classes() with identical signatures. DefaultRegistryProvider delegates to singleton, TestRegistryProvider returns internal dicts.
**Impact:** Low - this is the expected pattern for the Strategy pattern (or Adapter pattern). Both providers implement the same interface.
**Recommendation:** No action needed - this is intentional interface compliance. Could define an explicit IRegistryProvider Protocol, but the duck-typing works fine.
**Effort:** N/A

#### INFO: Angle Difference Calculation Imported with Alias
**ID:** DUP-FND-008
**Location:** `game/ai/behaviors.py:67` AND `game/ai/controller.py:57`
**Issue:** behaviors.py imports angle_diff with an alias: `from game.core.math import angle_diff as calc_angle_diff`, while controller.py imports it directly as `angle_diff`. This creates mild cognitive overhead when reading the code (same function, different names).
**Impact:** Very low - purely stylistic inconsistency.
**Recommendation:** Standardize import naming across AI module. Either always use the original name or always use an alias.
**Effort:** Simple

## Top 5 Priority Issues

1. **DUP-FND-001 (MAJOR)**: IControllable/IShip protocol duplication - Highest risk of interface divergence as the codebase evolves. Should be addressed if AI system is refactored.

2. **DUP-FND-003 (MAJOR)**: Distance calculation repetition - Has actual performance implications. The distance_cache optimization in controller.py demonstrates awareness of the issue but the solution is incomplete.

3. **DUP-FND-002 (MAJOR)**: Research state management duplication - Clean architectural issue. ResearchControlPanel should not reimplement tracker calculations.

4. **DUP-FND-004 (MINOR)**: Singleton clear pattern - Acceptable duplication, standard singleton lifecycle.

5. **DUP-FND-005 (MINOR)**: Serialization pattern - Common Python idiom, acceptable boilerplate.

## Architecture Notes

The foundation layer is generally well-organized with minimal critical duplication:

- **game/core/** provides clean, focused utilities (math, json_utils, hex_math, registry, etc.) that are properly reused across the codebase
- **game/ai/** has good separation between controller, behaviors, and evaluators with the combat_utils module consolidating shared helpers
- **game/research/** is self-contained with appropriate separation between data, systems, and UI
- **game/engine/** is minimal and focused (physics, collision, spatial)

The main architectural concern is the IControllable interface in game/ai/ which creates a parallel contract to the protocols in game/core/. This was likely intentional (to decouple AI from simulation internals), but it creates maintenance overhead.
