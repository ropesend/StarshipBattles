# PROJ-342 Pattern Scout Findings

**Investigation Date:** 2026-05-04
**Scope:** Does the proposed refactor follow established patterns or introduce new ones?

## Executive Summary

The proposed refactor introduces **one new pattern** (_require_X() precondition helper raising RuntimeError), reuses **four well-established patterns** consistently, and threads one inter-screen dependency via constructor injection that has **no precedent in the codebase but is consistent with MVVM composition**. Recommendation: document the precondition pattern; thread-parameter is justified as a targeted injection, not systemic.

---

## Pattern 1: Screen Constructor Signature

### Question
Is the canonical screen-constructor signature established? What does the proposal deviate from?

### Findings

**Canonical signature documented at docs/03_CONVENTIONS.md § 2.4:**

UI screen classes (anything implementing IScene) should stay under 300 lines. The MVVM pattern established by TestLabScreen and FleetBattleSetupScreen post-PROJ-282 prescribes delegate classes for mutations, rendering, and event handling.

**Four modern screens examined:**

| Screen | Constructor | Source |
|--------|-----------|--------|
| BattleScreen | __init__(self, screen_width: int, screen_height: int, scene_callback=None) | game/ui/screens/battle_screen.py:68 |
| FleetBattleSetupScreen | __init__(self, width: int, height: int, scene_callback=None) | game/ui/screens/battle_setup/screen.py:43 |
| StrategyScreen | __init__(self, screen_width: int, screen_height: int, session=None, scene_callback=None, input_mapper=None, *, composition=...) | game/ui/screens/strategy_screen.py:45-54 |
| DesignWorkshopScreen | __init__(self, screen_width, screen_height, context: WorkshopContext) | game/ui/screens/workshop_screen.py:51 |

**Pattern structure observed:**
1. Positional dimensions first: screen_width, screen_height (always, or width/height alias).
2. Domain dependencies as positional args: session, context (optional, per-screen needs).
3. Cross-cutting concerns as optional args: scene_callback, input_mapper, composition.
4. Keyword-only boundary: StrategyScreen uses * to separate cross-cutting from domain (PROJ-327).

**Current TestLabScreen signature:**
` python
def __init__(self, game, scene_callback=None):  # line 61
`

**Proposed refactored signature (per design.md):**
` python
def __init__(self, screen_width, screen_height, battle_scene, scene_callback)
`

### Verdict

**FOLLOWS ESTABLISHED PATTERN.** Positioning matches StrategyScreen(screen_width, screen_height, session=None, ...) — domain first, callbacks last. Recommend keeping scene_callback optional with default None for consistency.

---

## Pattern 2: Accessing Pygame Display Surface

### Question
How do screens access the pygame display surface? Is pygame.display.get_surface() idiomatic for this codebase, or novel?

### Findings

Only game/ui/screens/strategy_game_state_manager.py uses pygame.display.get_surface() (1 match). This is not the canonical pattern.

**Canonical pattern: draw(screen) surface-as-parameter**

All four modern screens use parameter passing in draw methods. The proposal uses pygame.display.get_surface() for out-of-cycle rendering (executor batch mode, not normal draw() dispatch).

### Verdict

**NOVEL BUT JUSTIFIED.** The proposal introduces pygame.display.get_surface() for **out-of-cycle rendering** (executor batch mode). This is appropriate for the constrained use case — internal executor paths with guaranteed initialization.

---

## Pattern 3: Inter-Screen Dependencies

### Question
Do any other screens hold a direct reference to another screen instance?

### Findings

Grep search finds zero screens holding references to other screens. All screens use scene_callback for transitions, not direct screen references.

**What the proposal introduces:**

TestLabScreen(screen_width, screen_height, battle_scene, scene_callback) — direct reference to self.battle_scene as a constructor parameter.

However, MVVM delegates DO receive screen references (e.g., BattleSetupInputHandler, StrategyRenderer), and the proposal is **justified by the use case** — TestLabScreen needs live access to attle_scene.engine and battle state during executor runs.

### Verdict

**INTRODUCES NEW INTER-SCREEN DEPENDENCY PATTERN.** Breaking screen isolation is justified as a special case for executor engine access, not a systemic shift. Recommendation: document as exception in design.md; add comment at construction site.

---

## Pattern 4: Precondition Validation with _require_X()

### Question
Do any screens already use _require_X() helpers that check preconditions and raise RuntimeError?

### Findings

**Established in strategy/simulation layers (PROJ-251):**

- game/strategy/engine/turn_engine.py:113 — aise RuntimeError("TurnEngine not started yet")
- game/simulation/services/ship_materializer.py:149 — aise RuntimeError(...) for missing precondition

This pattern is well-established in core engine code, just not yet applied to UI screens.

### Verdict

**RuntimeError for preconditions is idiomatic.** Adding _require_display_surface() in TestLabScreen follows established engine pattern, applied to UI for the first time. Recommendation: document in docs/05_ERROR_HANDLING.md with PROJ-251 reference.

---

## Pattern 5: Service Deletion Patterns

### Question
Are there git-history examples of similar "orphan service deletion" refactors?

### Findings

PROJ-321 Phase 3 (commits 96f63d026, deed107b8) provides the most similar precedent:
- Identified all callers via git grep
- Deleted whole-file units when orphaned
- Logged deletions in commit message with line counts
- Included verification step in phase checklist

### Verdict

**TestExecutionService and TestResultsService deletion follows PROJ-321 precedent.** Per design.md, grep found zero external callers. Recommendation: log deletions in commit message per PROJ-321 style; include grep verification evidence.

---

## Summary Table: Pattern Conformance

| Pattern | Established | Conforms | Status | Note |
|---------|-------------|----------|--------|------|
| Screen constructor (width, height, deps, callback) | Yes | Yes | Follow | Keep scene_callback optional |
| draw(screen) surface-as-parameter | Yes | Yes | Follow | Main cycle ✓ |
| pygame.display.get_surface() for out-of-cycle | Partial (1 use) | Justified | New | Out-of-cycle rendering only |
| Inter-screen constructor dependency | No | Introduces | New | Document as exception |
| _require_X() precondition → RuntimeError | Yes (engines) | Introduces | New | Document in error-handling guide |
| Orphan service deletion | Yes (PROJ-321) | Follows | Follow | Log per PROJ-321 style |

---

## Recommendations

### 1. Screen Constructor API (Priority: LOW)
Keep scene_callback=None as optional parameter. File: game/ui/screens/test_lab/screen.py:61

### 2. Inter-Screen Dependency Exception (Priority: MEDIUM)
Add comment in game/screen_router.py:125 explaining PROJ-342 exception to screen isolation pattern.

### 3. Precondition Helper Documentation (Priority: MEDIUM)
Document _require_display_surface() in docs/05_ERROR_HANDLING.md with new §UI Layer subsection referencing PROJ-251.

### 4. Service Deletion Verification (Priority: HIGH)
Phase 4 checklist: verify TestExecutionService and TestResultsService zero-caller status via grep before deletion.

### 5. Documentation Updates (Priority: HIGH)
Verify stale references in:
- combat_lab/COMBAT_LAB_DOCUMENTATION.md (lines 73-74, 161-162, 222-226, 259)
- combat_lab/runner.py (lines 62-64, 88-90)
- game/simulation/battle_controller.py (lines 113-116, 254-260)

---

## Conclusion

The proposed refactor **follows established patterns** for screen construction and service deletion. It **introduces new patterns** (_require_X() helpers in UI, pygame.display.get_surface() justification, inter-screen dependency exception), all **justified by use case and consistent with existing patterns**. Proceed with implementation; document the three new patterns to prevent misapplication.
