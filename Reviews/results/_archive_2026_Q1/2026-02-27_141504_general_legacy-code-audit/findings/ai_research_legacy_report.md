# AI & Research Legacy Code Audit
**Date:** 2026-02-27
**Scope:** `game/ai/`, `game/research/`, `game/app.py`, `game/exit_dialog.py`, `game/data/`

---

## Summary
- **Total issues found:** 7
- **Critical:** 0
- **Major:** 3
- **Minor:** 4
- **Info:** 0

**Overall Assessment:** The AI and research subsystems are relatively clean with minimal legacy code. Most code is active and well-maintained. Issues identified are primarily design/architecture improvements and one potential dead code pattern.

---

## Findings

### MAJOR: Unused test-only AI behaviors in production code
**ID:** AIR-001
**Location:** `game/ai/behaviors.py:405-483`
**Issue:** Test-specific behavior classes (`StraightLineBehavior`, `RotateOnlyBehavior`, `ErraticBehavior`) are exported and instantiated alongside production behaviors but appear to be test-only. These add production code complexity without gameplay value.
**Evidence:**
- Classes documented as "TEST-SPECIFIC BEHAVIORS" in comments
- Only instantiated in `AIController.__init__()` at lines 86-89
- No usage found in production battle/strategy code
- Grep search finds no references outside of controller initialization
- Used only in isolated test scenarios

**Recommendation:** Move to `game/simulation_tests/` module or create separate test-only controller variant. If test-only behaviors are needed, create a `TestAIController` in test suite.
**Effort:** Medium

---

### MAJOR: Global state mutation in exit_dialog.py
**ID:** AIR-002
**Location:** `game/exit_dialog.py:8-10, 22, 51, 64`
**Issue:** Module-level global variables `_exit_yes_rect` and `_exit_no_rect` are mutated during rendering and accessed during click handling. This is fragile coupling between rendering and input handling.
**Evidence:**
- Lines 8-10 define module globals
- Lines 51, 64 mutate these during `draw_exit_dialog()`
- Lines 84, 99 read these during click handling
- No synchronization or state validation
- Brittle to call order dependencies

**Recommendation:** Refactor to stateful dialog class with methods:
```python
class ExitDialog:
    def __init__(self, screen, font_large, font_med):
        self.yes_rect = None
        self.no_rect = None

    def draw(self, screen):
        # Updates self.yes_rect, self.no_rect

    def handle_click(self, pos) -> bool:
        # Returns True if yes clicked
```
**Effort:** Simple

---

### MAJOR: Orphaned protocol definitions unused in production
**ID:** AIR-003
**Location:** `game/ai/protocols.py:169-187` (TypeGuard functions)
**Issue:** Five TypeGuard functions (`is_grid_entity`, `is_projectile`, `is_formation_master`, `is_component_health`) are defined but never imported or used anywhere in the codebase.
**Evidence:**
- Functions at lines 169-187 in protocols.py
- No `from game.ai.protocols import is_*` found in any file
- `is_projectile()` is used in controller/target_evaluator but imported as:
  `from game.ai.protocols import is_projectile` yet the actual usage is duck-typing checks: `isinstance(obj, IProjectile)`
- Other guard functions completely unused
- These were likely added in PROJ-192 for type safety but adoption was incomplete

**Recommendation:** Either:
1. Remove unused guard functions (`is_grid_entity`, `is_formation_master`, `is_component_health`)
2. Update codebase to use `is_projectile()` guard consistently instead of `isinstance()` checks
3. Document in CLAUDE.md when protocol checks should be preferred

**Effort:** Simple

---

### MINOR: BUG FIX marker in target_evaluator.py not documented
**ID:** AIR-004
**Location:** `game/ai/target_evaluator.py:190-191`
**Issue:** Comment references a bug fix about `.current_hp` vs `.hp` but no associated issue number or decision log entry.
**Evidence:**
```python
# BUG FIX: Component has .current_hp, not .hp (getattr(c, 'hp', 0) always returned 0)
armor_hp = sum(c.current_hp for c in armor_comps)
```

**Recommendation:** Add PROJ issue number or link to decision log. This should be tracked in the codebase history.
**Effort:** Simple

---

### MINOR: Formation behavior uses hardcoded magic numbers for correction
**ID:** AIR-005
**Location:** `game/ai/behaviors.py:270-275, 376`
**Issue:** Formation behavior has magic numbers (`2.0` deadband, `0.2` correction factor, `500px` max correction) that should be configurable parameters or at least named constants.
**Evidence:**
- Line 270: `DEADBAND_ERROR: float = AIConfig.FORMATION_DEADBAND_ERROR` (good)
- Line 376: `if dist_error > self.DEADBAND_ERROR:` (uses constant correctly)
- But hardcoded `0.2` factor in line 379: `correction = vec_to_spot * self.CORRECTION_FACTOR`
- Actually uses `AIConfig.FORMATION_CORRECTION_FACTOR` - this is fine
- Line 381-382: Correction capped at `self.MAX_CORRECTION_FORCE` which comes from config

**Recommendation:** Verify all magic numbers have corresponding AIConfig entries. This appears mostly correct; minor documentation improvement only.
**Effort:** Simple

---

### MINOR: Research system isolated from core game loop
**ID:** AIR-006
**Location:** `game/research/` (entire package)
**Issue:** Research subsystem is completely disconnected from core game. It appears as a "sandbox for testing tech tree balance" (per `__init__.py` docstring) but is not integrated into actual gameplay.
**Evidence:**
- Docstring states: "A standalone sandbox for testing tech tree balance"
- Research data models exist (TechNode, TechTree, ResearchTracker)
- Research service exists (ResearchService for leaky bucket mechanics)
- But zero integration with GameSession or strategy layer
- UI components exist in `game/ui/research/` but never instantiated in main game flow
- No research.json data file exists (only homeworld_presets.json in game/data/)

**Recommendation:** Either:
1. Complete research subsystem integration (requires data file, GameSession integration, UI flow)
2. Mark as experimental/disabled feature with clear documentation
3. Move to separate research-only testing module outside main game package

Current state is neither prototype nor production - it exists in limbo.
**Effort:** Complex (if integrating) or Simple (if documenting as experimental)

---

### MINOR: Unused test-only function in combat_utils.py
**ID:** AIR-007
**Location:** `game/ai/combat_utils.py:38-51`
**Issue:** Function `is_vector2_like()` is exported (in `__all__`) but never imported or used anywhere in the codebase.
**Evidence:**
- Defined at lines 38-51
- Included in `__all__` at line 27
- Checks for MagicMock vs real Vector2
- Only useful in test contexts but never called from tests
- Grep finds zero imports of this function

**Recommendation:** Remove from `__all__` exports. Keep in codebase as internal utility (remove from `__all__`) if might be useful; otherwise delete.
**Effort:** Simple

---

## Detailed Analysis by Module

### game/ai/ (Clean)
**Status:** Well-maintained, minimal legacy code

**Positive observations:**
- Clear separation of concerns (controller, behaviors, targeting, strategy)
- Comprehensive documentation and exception handling
- All behaviors are referenced and used in combat system
- Factory pattern properly implements layer separation (PROJ-126)
- Strategy manager uses singleton pattern appropriately for config loading

**Issues:** 3 (test-only behaviors, protocol guards, vector2 utility)

---

### game/research/ (Abandoned/Prototype)
**Status:** Functional code but disconnected from game

**Positive observations:**
- Clean architecture with data/systems separation
- Leaky bucket algorithm properly implemented
- Good test data loading with error handling
- Proper fuzzy requirement resolution

**Issues:** 1 major (orphaned subsystem)

**Notes:** This looks like a prototype or previous game feature that was not fully integrated. Code quality is high but integration was never completed. Recommend either full integration or clear documentation as experimental.

---

### game/app.py (Clean)
**Status:** Main entry point, well-structured

**Assessment:** No legacy code issues detected. Scene management, registries, and initialization all follow current architecture. PROJ-199 noted the elimination of lazy init - this is good.

---

### game/exit_dialog.py (Legacy pattern)
**Status:** Functional but uses outdated patterns

**Issue:** Global state mutation for UI state (1 major)

**Notes:** This is a legacy pattern from older pygame-only era before pygame_gui. Consider modernizing to class-based approach if exit functionality remains important.

---

### game/data/ (Minimal)
**Status:** Clean

**Contents:** Only `homeworld_presets.json` - no orphaned data files found.

---

## Top 5 Priority Issues

1. **AIR-002** (exit_dialog.py global state) - **Effort: Simple, Impact: High**
   - Remove module-level globals, refactor to class-based dialog
   - Eliminates fragile state coupling
   - Priority: Medium (only affects exit path, rarely used)

2. **AIR-001** (test-only behaviors in production) - **Effort: Medium, Impact: Medium**
   - Move test behaviors to test module
   - Reduces production code complexity
   - Priority: Medium (doesn't affect gameplay, just cleanliness)

3. **AIR-006** (research system orphaned) - **Effort: Complex, Impact: Low**
   - Decide: integrate fully, document as experimental, or remove
   - Currently exists in limbo (neither prototype nor production)
   - Priority: Low (not used in gameplay, can defer)

4. **AIR-003** (unused protocol guards) - **Effort: Simple, Impact: Low**
   - Remove 4 unused guard functions or complete PROJ-192 adoption
   - Clarify protocol usage patterns in docs
   - Priority: Low (cleanup only)

5. **AIR-007** (unused combat_utils function) - **Effort: Simple, Impact: Low**
   - Remove `is_vector2_like` from exports or codebase
   - Priority: Low (cleanup only)

---

## Recommendations Summary

### Immediate (Next Sprint)
- [ ] AIR-002: Refactor exit_dialog to class-based pattern (1-2 hours)
- [ ] AIR-004: Document BUG FIX with issue number (15 min)

### Short-term (This Quarter)
- [ ] AIR-001: Move test behaviors to test module (2-3 hours)
- [ ] AIR-003: Remove unused protocol guards or complete PROJ-192 (1-2 hours)
- [ ] AIR-007: Remove unused vector2 function (15 min)

### Long-term (Decision Required)
- [ ] AIR-006: Resolve research subsystem status (review required)
  - Schedule architecture review to decide on research system's future
  - If keeping: full integration required
  - If removing: delete entirely per "eradicate old systems" policy

---

## Code Quality Assessment

| Metric | Rating | Notes |
|--------|--------|-------|
| Architecture | ✅ Good | Clear layer separation, proper patterns |
| Type Safety | ⚠️ Partial | Protocols defined but adoption incomplete (PROJ-192) |
| Documentation | ✅ Good | Comprehensive docstrings and module-level docs |
| Dead Code | ✅ Minimal | Only 2 functions truly unused (vector2 check, behavior classes) |
| Testing | ✅ Good | Test behaviors properly isolated in most cases |
| Legacy Patterns | ⚠️ Minor | One module (exit_dialog) uses outdated global state pattern |

---

## Conclusion

The AI and research subsystems are relatively clean with high code quality. No critical issues found. The main concerns are:

1. **Incomplete refactoring** (PROJ-192 protocol adoption, test behavior isolation)
2. **One orphaned subsystem** (research system prototype status unclear)
3. **Legacy pattern** (exit dialog global state)

No eradication of dead systems required. All issues are cleanup/completion work rather than architectural problems.

**Estimated cleanup effort:** 6-10 hours (excluding research subsystem decision)
