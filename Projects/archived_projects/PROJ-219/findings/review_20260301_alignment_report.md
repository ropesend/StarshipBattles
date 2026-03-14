# PROJ-219: Plan-Code Alignment Report

**Date:** 2026-03-01
**Reviewer:** Claude Code (Automated Analysis)
**Project:** Fleet Registration Consolidation

## Executive Summary

The PROJ-219 project plan has been reviewed against the current codebase to verify that all file references, line numbers, and code descriptions are accurate. This analysis identified **12 findings** requiring attention before implementation begins.

---

## Findings

### F-001: Empire.__init__ Line Numbers Off

**Task:** Task 1.1, Add `galaxy: 'Galaxy' = None` parameter to `__init__` signature
**Plan Reference:** `game/strategy/data/empire.py:16-17` -- Add parameter after `race_config`
**Actual Code:** Lines 16-17 contain:
```python
def __init__(self, empire_id, name, color, theme_path=None, empire_theme_id="Federation",
             flag_id: str = "", portrait_id: str = "", race_config=None):
```
**Impact:** Lines are correct. The `race_config` parameter is on line 17, so adding after it on line 17 works.
**Proposed Fix:** No fix needed - reference is accurate.

---

### F-002: Empire Body Line for _galaxy Storage

**Task:** Task 1.1, Add `self._galaxy = galaxy` in `__init__` body (after line 44)
**Plan Reference:** `game/strategy/data/empire.py` -- after line 44
**Actual Code:** Line 44 is:
```python
self.max_storage = {}     # Dict[str, float] - storage capacity per type
```
This is the last assignment in `__init__` before `add_colony()` method at line 46.
**Impact:** Correct placement point identified.
**Proposed Fix:** No fix needed - reference is accurate.

---

### F-003: set_galaxy() Insertion Point

**Task:** Task 1.2, Add `set_galaxy()` method after `get_next_serial()` (around line 86)
**Plan Reference:** `game/strategy/data/empire.py` -- around line 86
**Actual Code:** `get_next_serial()` method ends at line 85. Line 86 is blank, and line 87 starts the comment `# --- Resource Economy Methods (PROJ-75) ---`.
**Impact:** Correct insertion point.
**Proposed Fix:** No fix needed - reference is accurate.

---

### F-004: add_fleet() Lines Accurate

**Task:** Task 1.3, Modify `add_fleet()` (lines 56-58)
**Plan Reference:** `game/strategy/data/empire.py:56-58`
**Actual Code:**
```python
56:    def add_fleet(self, fleet):
57:        self.fleets.append(fleet)
58:        fleet.owner_id = self.id
```
**Impact:** Exact match.
**Proposed Fix:** No fix needed - reference is accurate.

---

### F-005: remove_fleet() Lines Accurate

**Task:** Task 1.4, Modify `remove_fleet()` (lines 60-62)
**Plan Reference:** `game/strategy/data/empire.py:60-62`
**Actual Code:**
```python
60:    def remove_fleet(self, fleet):
61:        if fleet in self.fleets:
62:            self.fleets.remove(fleet)
```
**Impact:** Exact match.
**Proposed Fix:** No fix needed - reference is accurate.

---

### F-006: GameInitializer Line Reference Off

**Task:** Task 2.1, In `initialize()` method, after line 53 (after `_setup_initial_scenario`), add set_galaxy loop
**Plan Reference:** `game/strategy/engine/game_initializer.py:45-55`
**Actual Code:** Lines 52-55:
```python
52:        # Set up initial scenario (homeworlds, colonies)
53:        GameInitializer._setup_initial_scenario(systems, empires, config)
54:
55:        return galaxy, empires
```
**Impact:** Line 53 calls `_setup_initial_scenario`. The `set_galaxy()` loop should be added between lines 53 and 55 (before the return).
**Proposed Fix:** Update plan to say "after line 53, before `return galaxy, empires`" for clarity.

---

### F-007: GameSession.from_dict Empire Deserialization Line Off

**Task:** Task 2.2, After empire deserialization (line 342), before fleet registration loop (line 353)
**Plan Reference:** `game/strategy/engine/game_session.py:339-357`
**Actual Code:**
- Lines 338-342: Empire deserialization list comprehension
- Line 349: Blank line after exception handling
- Lines 353-357: Fleet registration loop
```python
353:        # PROJ-216: Register all fleets with galaxy for O(1) lookup
354:        # Fleets are deserialized into empires but not automatically registered
355:        for empire in session.empires:
356:            for fleet in empire.fleets:
357:                session.galaxy.register_fleet(fleet)
```
**Impact:** The insertion point is correct (between empire creation at 338-342 and fleet registration at 353-357). However, line 342 is inside the list comprehension, so insertion should happen at line 349 (after exception block, before human_player_ids restoration) or line 350.
**Proposed Fix:** Update plan: "After line 348 (end of empire exception block), add `set_galaxy()` loop before line 350."

---

### F-008: ProductionEngine galaxy.register_fleet() Lines Off

**Task:** Task 3.1, Remove lines 641-643 (the conditional galaxy.register_fleet call)
**Plan Reference:** `game/strategy/engine/production_engine.py:641-643`
**Actual Code:** Lines 641-643:
```python
641:        # PROJ-216: Register fleet with galaxy for O(1) lookup
642:        if galaxy:
643:            galaxy.register_fleet(new_fleet)
```
**Impact:** Exact match - these are the lines to remove.
**Proposed Fix:** No fix needed - reference is accurate.

---

### F-009: CommandHandlers Line Reference Inaccurate

**Task:** Task 3.2, Remove line 692 (the explicit registration call)
**Plan Reference:** `game/strategy/engine/command_handlers.py:692`
**Actual Code:** Lines 690-694:
```python
690:        # 7. Register new fleet with empire and galaxy
691:        empire.add_fleet(new_fleet)
692:        session.galaxy.register_fleet(new_fleet)  # PROJ-216: O(1) lookup
693:
694:        logger.info(f"GameSession: Split fleet {cmd.fleet_id} -> new fleet {new_fleet_id} ({len(ships_to_move)} ships)")
```
**Impact:** Line 692 contains exactly `session.galaxy.register_fleet(new_fleet)` as expected.
**Proposed Fix:** No fix needed - reference is accurate.

---

### F-010: SuperweaponOrderProcessor unregister_fleet() Line Off

**Task:** Task 3.3, Remove line 239 (the explicit unregister)
**Plan Reference:** `game/strategy/engine/superweapon_order_processor.py:239`
**Actual Code:** Lines 236-242 (in `process_stellerate_star`):
```python
236:        all_fleets_in_system = galaxy.get_all_fleets_in_system(system, empires)
237:        for (owner_empire, victim_fleet) in all_fleets_in_system:
238:            # Unregister from galaxy (Galaxy always has unregister_fleet)
239:            galaxy.unregister_fleet(victim_fleet)
240:            # Remove from empire
241:            owner_empire.remove_fleet(victim_fleet)
```
**Impact:** Line 239 contains `galaxy.unregister_fleet(victim_fleet)`. However, this is in `process_stellerate_star()`, which is a suicide weapon that destroys ALL fleets in a system. This unregister happens BEFORE `remove_fleet()` and is intentional - the current code pattern calls unregister then remove_fleet. After PROJ-219, `remove_fleet()` will auto-unregister, so line 239 becomes redundant.
**Proposed Fix:** Reference is accurate. Task is to remove line 239.

---

### F-011: Bug Fix Location - conflict_resolution_engine.py Line Inaccurate

**Task:** Bug Fix - Combat destruction
**Plan Reference:** `conflict_resolution_engine.py:186`
**Actual Code:** Line 186 contains:
```python
186:            loser_empire.remove_fleet(loser)
```
This is in `_resolve_combat_at_hex()`.
**Impact:** The line number is accurate. The `remove_fleet()` call is at line 186 inside the combat resolution loop.
**Proposed Fix:** No fix needed - reference is accurate.

---

### F-012: Bug Fix Location - fleet_order_processor.py Lines Need Verification

**Task:** Bug Fixes - JOIN_FLEET merge (line 113), COLONIZE empty (line 216), Instant merge (line 663)
**Plan Reference:** `fleet_order_processor.py:113`, `fleet_order_processor.py:216`, `fleet_order_processor.py:663`
**Actual Code:**
- Line 113: `empire.remove_fleet(fleet)` in `process_join_fleet()` - ACCURATE
- Line 216: `empire.remove_fleet(fleet)` in `process_colonize()` - ACTUAL is line 216:
  ```python
  216:            empire.remove_fleet(fleet)
  ```
  ACCURATE
- Line 663: This should be in `process_instant_orders()`. Actual line 663:
  ```python
  663:            empire.remove_fleet(fleet)
  ```
  ACCURATE
**Impact:** All three line references are correct.
**Proposed Fix:** No fix needed - references are accurate.

---

### F-013: Bug Fix Location - maintenance_engine.py Line Accurate

**Task:** Bug Fix - Maintenance scuttle
**Plan Reference:** `maintenance_engine.py:286`
**Actual Code:** Line 286:
```python
286:            empire.remove_fleet(fleet)
```
This is in `_cleanup_empty_fleets()`.
**Impact:** The line number is accurate.
**Proposed Fix:** No fix needed - reference is accurate.

---

### F-014: Bug Fix Location - superweapon_order_processor.py Line 103

**Task:** Bug Fix - Superweapon finalize (line 103)
**Plan Reference:** `superweapon_order_processor.py:103`
**Actual Code:** Line 103:
```python
103:            empire.remove_fleet(fleet)
```
This is in `_finalize_superweapon()` method.
**Impact:** The line number is accurate.
**Proposed Fix:** No fix needed - reference is accurate.

---

## Summary Table

| Finding | Status | Action Required |
|---------|--------|-----------------|
| F-001 | OK | None |
| F-002 | OK | None |
| F-003 | OK | None |
| F-004 | OK | None |
| F-005 | OK | None |
| F-006 | MINOR | Clarify insertion point in plan |
| F-007 | MINOR | Update line reference (342 -> 349) |
| F-008 | OK | None |
| F-009 | OK | None |
| F-010 | OK | None |
| F-011 | OK | None |
| F-012 | OK | None |
| F-013 | OK | None |
| F-014 | OK | None |

## Conclusion

The PROJ-219 plan is **well-aligned** with the current codebase. All major file paths exist, and most line number references are accurate within a small margin.

**Minor adjustments recommended:**
1. **F-006**: Add clarification that `set_galaxy()` loop goes "before the return statement"
2. **F-007**: Update GameSession.from_dict insertion point to specify line 349 (after empire exception block)

**Ready for implementation**: Yes, with minor plan refinements noted above.

---

*Report generated by Plan-Code Alignment Analyst*
