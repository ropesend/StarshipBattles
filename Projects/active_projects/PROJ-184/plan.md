# PROJ-184: Type-Safe Spatial Query API

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-184` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-184 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Add type-safety guard to get_system_of_object | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Remove legacy hasattr checks | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-02-24
**Active Phase:** Phase 2
**Last Action:** Phase 1 complete - isinstance guard added, 4 tests added
**Next Action:** Execute Phase 2 - remove 3 legacy hasattr checks
**Blockers:** None
**Context for Next Agent:** Tests: 12366 passed, 1 skipped. Files modified: galaxy_spatial_index.py, galaxy.py, test_galaxy.py

## Overview
Add structural type-safety to `GalaxySpatialIndex.get_system_of_object()` to prevent silent misuse with local-coordinate objects (Planet, Star, WarpPoint), and remove 3 legacy `hasattr` defensive checks that are no longer needed since PROJ-179 established these methods permanently.

## Goals
- Eliminate the "landmine" where passing a Planet/Star/WarpPoint to `get_system_of_object()` could silently return `None` or the wrong system
- Auto-route Planet objects to the correct `get_system_of_planet()` method
- Remove 3 unnecessary `hasattr` checks that guard for methods that always exist
- Add test coverage for the type-safety guard

## Scope
**In:**
- `get_system_of_object()` type-safety guard (isinstance check + auto-route)
- Corresponding facade method docstring update
- 3 legacy `hasattr` removals in callers
- New unit tests for the guard behavior

**Out:**
- Renaming `get_system_of_object` to `get_system_of_fleet` (would break external callers - separate project)
- Broader `hasattr` cleanup (covered by existing review report, separate scope)
- StrategyInputHandler chain-of-responsibility issues (confirmed correct, no action needed)

## Key Files
| Component | File Path |
|-----------|-----------|
| Spatial index (main fix) | `game/strategy/data/galaxy_spatial_index.py` |
| Galaxy facade | `game/strategy/data/galaxy.py` |
| hasattr cleanup 1 | `game/strategy/engine/game_session.py` |
| hasattr cleanup 2 | `game/ui/screens/empire_build_queue_window.py` |
| hasattr cleanup 3 | `game/ui/screens/empire_build_queue_formatter.py` |
| Existing tests | `tests/unit/strategy/data/test_galaxy.py` |

## Initial Analysis

### Swarm Review (6 agents)
- **Architecture Agent:** Confirmed delegate pattern is clean. All 7 spatial methods properly delegated. No bypasses remain.
- **Caller Agent:** Found exactly 2 callers of `get_system_of_object` (both pass Fleet). Found 5 callers of `get_system_of_planet` (all pass Planet). No cross-contamination today, but no guard prevents it.
- **Type/Coordinate Agent:** Confirmed coordinate split: Planet/Star/WarpPoint use LOCAL coords, Fleet/StarSystem use GLOBAL coords. All share `.location` attribute name, making misuse easy.
- **Test Agent:** Found 0 tests for `get_system_of_object()` directly. No test verifies what happens when a Planet is passed. 14+ tests exist for other spatial methods.
- **Input Handler Agent:** Confirmed chain-of-responsibility is correct. All routers return bool and parent uses `if ... return`. No fall-through bugs.
- **Galaxy Delegate Agent:** Confirmed `from_dict()` properly uses `restore_planet()`. Zone `id()` usage is acceptable given rebuild during load.

### The Bug
`get_system_of_object(obj)` at `galaxy_spatial_index.py:32-51`:
1. Accepts `Any` object with a `location` attribute
2. Checks `obj.location` against `self._galaxy.systems` (keyed by GLOBAL coords)
3. Planet/Star/WarpPoint have LOCAL `.location` attributes
4. If a local coord accidentally matches a global system coord → **wrong system returned silently**
5. If it doesn't match → returns `None` (silent failure, no error)

### The Fix
Add `isinstance(obj, Planet)` check at the top of the method to auto-route to the correct method. This is both defensive (prevents misuse) and helpful (auto-corrects the call).

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Auto-route Planet via isinstance rather than raising TypeError | More forgiving API; existing callers unaffected; future callers get correct behavior |
| 2026-02-24 | Add logging.warning when auto-routing | Makes misuse visible without breaking anything |
| 2026-02-24 | Include hasattr cleanup in same project | Same code area, related defensive-programming cleanup, tiny scope |
| 2026-02-24 | Do NOT rename method to get_system_of_fleet | Would need broader caller audit; separate project if desired |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

---

## Phases

### Phase 1: Add Type-Safety Guard to get_system_of_object [Simple]
**Objective:** Prevent silent misuse by auto-routing Planet objects and logging a warning
**Status:** Not Started

#### Task 1.1: Add isinstance guard to GalaxySpatialIndex.get_system_of_object [Simple]
**File:** `game/strategy/data/galaxy_spatial_index.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py -x`
- [ ] Add runtime import of `Planet` inside method body (to avoid circular import) (line 44)
- [ ] Add isinstance check before the existing hasattr check:
  ```python
  def get_system_of_object(self, obj: Any) -> Optional['StarSystem']:
      """Find the system containing a Fleet (by its global location).

      Auto-routes Planet objects to get_system_of_planet(). Planets have
      local coordinates relative to their system, not global coordinates.

      Args:
          obj: Object with a 'location' attribute (global HexCoord).

      Returns:
          StarSystem or None.
      """
      # Auto-route planets to the correct lookup method
      from game.strategy.data.planet import Planet
      if isinstance(obj, Planet):
          return self.get_system_of_planet(obj)

      if not hasattr(obj, 'location'):
          return None

      # If object location matches a system's global_location
      if obj.location in self._galaxy.systems:
          return self._galaxy.systems[obj.location]

      return None
  ```
- [ ] Update facade docstring in `game/strategy/data/galaxy.py` (lines 203-217) to match
**Notes:**

#### Task 1.2: Add unit tests for the type-safety guard [Simple]
**File:** `tests/unit/strategy/data/test_galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py -x`
- [ ] Add test: `test_get_system_of_object_autoroutes_planet` — passes a registered Planet to `get_system_of_object()`, asserts correct system returned
- [ ] Add test: `test_get_system_of_object_returns_none_for_no_location` — passes object without location attribute
- [ ] Add test: `test_get_system_of_object_returns_system_for_fleet_at_system` — passes a Fleet-like object at a system's global coord
- [ ] Add test: `test_get_system_of_object_returns_none_for_fleet_in_deep_space` — passes a Fleet-like object NOT at a system coord
- [ ] Run `pytest tests/unit/strategy/data/test_galaxy.py -x` — all pass
**Notes:**

#### Task 1.3: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] Run `pytest tests/ -n 12` — 12,366+ passed, 0 failed
**Notes:**

---

### Phase 2: Remove Legacy hasattr Checks [Simple]
**Objective:** Remove 3 unnecessary `hasattr` guards for methods that always exist on Galaxy
**Status:** Not Started

#### Task 2.1: Remove hasattr in game_session.py [Simple]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/unit/strategy/engine/ tests/integration/strategy/ -x`
- [ ] Remove the `hasattr` guard at line 133-134:
  ```python
  # Change this:
  if not hasattr(self.galaxy, 'get_system_of_object'):
      return None

  # To: (just delete the 2 lines, keeping the for loop below)
  ```
**Notes:**

#### Task 2.2: Simplify hasattr in empire_build_queue_window.py [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py -x`
- [ ] Simplify the guard at line 348:
  ```python
  # Change this:
  if self.galaxy and hasattr(self.galaxy, 'get_system_of_planet'):

  # To:
  if self.galaxy:
  ```
**Notes:**

#### Task 2.3: Simplify hasattr in empire_build_queue_formatter.py [Simple]
**File:** `game/ui/screens/empire_build_queue_formatter.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_formatter.py -x`
- [ ] Simplify the guard at line 83:
  ```python
  # Change this:
  if galaxy and hasattr(galaxy, 'get_system_of_planet'):

  # To:
  if galaxy:
  ```
**Notes:**

#### Task 2.4: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] Run `pytest tests/ -n 12` — 12,366+ passed, 0 failed
**Notes:**

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/` — 12,366 passed, 1 skipped (baseline established)

### After Each Phase
- [ ] Run `pytest tests/ -n 12` — all tests pass
- [ ] Verify `get_system_of_object(planet)` returns correct system (new test)
- [ ] Verify `get_system_of_object(fleet)` still works (new test)

### Final Verification
- [ ] Run full test suite: `pytest tests/ -n 12` (NOT --testmon, full verification)
- [ ] All new tests pass
- [ ] No hasattr guards remain for spatial query methods

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All tests passing (12,366+)
- [ ] Audit passed (no significant issues)
- [ ] User verified
