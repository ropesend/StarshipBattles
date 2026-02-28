# PROJ-160: Add Galaxy.get_planet_global_hex Method

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-160` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-160 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Add Galaxy Method | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Refactor Command Handlers | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Fix Test Mocks | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-02-22 16:10
**Active Phase:** Phase 3 - Fix Test Mocks
**Last Action:** Phase 2 complete - refactored ColonizeCommandHandler and TransferCommandHandler to use `get_planet_global_hex()`
**Next Action:** Phase 3 Task 3.1 - Add `get_planet_global_hex` mock to test_command_handlers.py
**Blockers:** None
**Context for Next Agent:** Both command handlers refactored at command_handlers.py:121 and command_handlers.py:411. Code compiles. Tests will fail until mocks are updated in Phase 3.

## Overview
Add an O(1) `get_planet_global_hex(planet)` method to the Galaxy class that encapsulates the pattern `system.global_location + planet.location`. This eliminates duplicate iteration over `galaxy.systems.values()` across multiple callers and simplifies testing.

## Goals
- Add `get_planet_global_hex(planet)` method to Galaxy class
- Refactor command handlers to use the new method
- Update test mocks to include the method
- Improve code maintainability by centralizing planet location lookup

## Scope
**In Scope:**
- Adding `get_planet_global_hex()` to Galaxy class
- Refactoring `ColonizeCommandHandler` (command_handlers.py:122-125)
- Refactoring `TransferCommandHandler` (command_handlers.py:418-421)
- Adding unit tests for the new method
- Updating failing test mocks

**Out of Scope:**
- Refactoring test fixture code (test_commands_colonization.py) - low priority
- Refactoring transfer_validator.py - needs system object, not global hex
- Refactoring visualization scripts - different purpose

## Key Files
| Component | File Path | Line(s) |
|-----------|-----------|---------|
| Galaxy class | `game/strategy/data/galaxy.py` | 198-204 |
| ColonizeCommandHandler | `game/strategy/engine/command_handlers.py` | 122-125 |
| TransferCommandHandler | `game/strategy/engine/command_handlers.py` | 418-421 |
| Galaxy unit tests | `tests/unit/strategy/data/test_galaxy.py` | 148-173 |
| Command handler tests | `tests/unit/strategy/test_command_handlers.py` | 97-111 |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

---

## Swarm Findings Summary

### Architecture Analysis
The Galaxy class uses a two-level coordinate system:
- **Global coordinates**: Absolute HexCoord in galaxy map space (e.g., `StarSystem.global_location`)
- **Local coordinates**: Relative HexCoord within a system (e.g., `Planet.location`)

Key data structures for O(1) lookups:
- `_planet_to_system`: Dict[Planet, StarSystem] - reverse lookup (line 106)
- `planets_by_id`: Dict[int, Planet] - ID lookup (line 103)
- `_global_hex_planets`: Dict[HexCoord, List[Planet]] - spatial lookup (line 107)

### Key Pattern to Reuse
**`get_system_of_planet(planet)`**: `galaxy.py:198-200` - exact pattern to follow
```python
def get_system_of_planet(self, planet: 'Planet') -> Optional['StarSystem']:
    """O(1) reverse lookup: Planet -> StarSystem."""
    return self._planet_to_system.get(planet)
```

### Callers Analysis
Found **18 occurrences** of `galaxy.systems.values()` iteration:

| File | Lines | Candidate? | Reason |
|------|-------|------------|--------|
| command_handlers.py | 122-125 | **YES** | Computes `sys.global_location + target_planet.location` |
| command_handlers.py | 418-421 | **YES** | Same pattern (duplicate code) |
| transfer_validator.py | 78-81 | No | Needs system object, not just hex |
| planet_list_filters.py | 23-27 | No | Bulk collection with system refs |
| pathfinding.py | 133-159 | No | System distance searches |

### Risks Identified
1. **MockGalaxy classes** - Integration tests use MockGalaxy that must include new method
   - Mitigation: Update mocks as part of Phase 3

---

## Phases

### Phase 1: Add Galaxy Method [Simple]
**Objective:** Add `get_planet_global_hex()` method with unit tests

#### Task 1.1: Add `get_planet_global_hex()` method [Simple]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py -v`
- [x] Add method after `get_planets_at_global_hex()` (after line 204):
  ```python
  def get_planet_global_hex(self, planet: 'Planet') -> Optional[HexCoord]:
      """O(1) lookup: get the global hex coordinate of a planet.

      Args:
          planet: Planet to get location for.

      Returns:
          Global HexCoord of the planet, or None if planet not registered.
      """
      system = self._planet_to_system.get(planet)
      if system:
          return system.global_location + planet.location
      return None
  ```
- [x] Verify no import changes needed (HexCoord already imported)

#### Task 1.2: Add unit tests for new method [Simple]
**File:** `tests/unit/strategy/data/test_galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py::TestGalaxyPlanetGlobalHex -v`
- [x] Add new test class after `TestGalaxySystemLookup` (after line 173)
- [x] Test: registered planet returns correct global hex
- [x] Test: unregistered planet returns None

---

### Phase 2: Refactor Command Handlers [Simple]
**Objective:** Replace system iteration with new method

#### Task 2.1: Refactor ColonizeCommandHandler [Simple]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/test_command_handlers.py::TestColonizeCommandHandler -v`
- [x] Replace lines 121-125 with single call:
  ```python
  planet_global_hex = session.galaxy.get_planet_global_hex(target_planet)
  ```

#### Task 2.2: Refactor TransferCommandHandler [Simple]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/test_command_handlers.py::TestTransferCommandHandler -v`
- [x] Replace lines 417-421 with single call:
  ```python
  planet_global_hex = session.galaxy.get_planet_global_hex(planet)
  ```

---

### Phase 3: Fix Test Mocks [Simple]
**Objective:** Update test mocks to include new method

#### Task 3.1: Fix TestColonizeCommandHandler mock [Simple]
**File:** `tests/unit/strategy/test_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/test_command_handlers.py::TestColonizeCommandHandler -v`
- [ ] Add `get_planet_global_hex` mock around line 104:
  ```python
  mock_session.galaxy.get_planet_global_hex.return_value = HexCoord(0, 0)
  ```

#### Task 3.2: Fix any other failing test mocks [Simple]
**Tests:** `pytest tests/ -n 12 --tb=no -q`
- [ ] Run full test suite and fix any MockGalaxy implementations
- [ ] Common files that may need updates:
  - `tests/integration/strategy/test_economy_e2e.py` (MockGalaxy lines 221-230)
  - `tests/integration/strategy/test_command_handlers.py` (MockGalaxy lines 35-66)

---

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Run full test suite: `pytest tests/` - establish baseline

### After Phase 1
- [ ] Run `pytest tests/unit/strategy/data/test_galaxy.py -v` - new tests pass

### After Phase 2
- [ ] Run `pytest tests/unit/strategy/test_command_handlers.py -v`

### After Phase 3
- [ ] Run `pytest tests/ -n 12` - verify failing tests are now passing

### Final Verification
- [ ] Run full test suite: `pytest tests/ -n 12` - no new failures

---

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-22 | Use O(1) lookup via `_planet_to_system` | Consistent with existing patterns like `get_system_of_planet()` |
| 2026-02-22 | Only refactor command_handlers.py | Other callers need system objects or have different purposes |
| 2026-02-22 | Follow Google-style docstrings | Match existing Galaxy class conventions |

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] Phase 1 tasks complete
- [ ] Phase 2 tasks complete
- [ ] Phase 3 tasks complete
- [ ] All tests passing (excluding pre-existing unrelated failures)
- [ ] User verified
