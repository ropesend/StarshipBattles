# PROJ-179: PROJ-173 Post-Refactor Cleanup

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-179` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-179 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Fix Delegation & Docstring Issues | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Encapsulation & Performance Improvements | Complete | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-02-24
**Active Phase:** Complete
**Last Action:** Audit Cycle 1 passed - all objectives verified
**Next Action:** User verification required
**Blockers:** None
**Context for Next Agent:** Project is audit-complete. User needs to verify and close.

## Overview
Address 4 confirmed issues from the PROJ-173 post-refactor audit. The PROJ-173 God Class Decomposition extracted `GalaxySpatialIndex`, `GalaxyEntityRegistry`, and sub-routers from Galaxy and StrategyInputHandler. This cleanup fixes a bypassed delegate, a misleading docstring, an encapsulation violation in `from_dict()`, and an O(N) method that should leverage existing O(1) indexes.

## Goals
- Complete the facade/delegate pattern consistently (no bypassed delegates)
- Eliminate duplicate logic between `from_dict()` and `register_planet()`
- Leverage existing O(1) spatial indexes in `get_system_at_location()`
- Fix misleading documentation that could trap future developers

## Scope
**In:**
- Fix `Galaxy.get_zones_at_global_hex` to delegate to `GalaxySpatialIndex`
- Fix `get_system_of_object` docstring/signature (fleet-only method)
- Add `restore_planet()` to `GalaxyEntityRegistry` for deserialization
- Refactor `get_system_at_location()` to O(1) using existing indexes

**Out:**
- Audit Finding #5 (chain-of-responsibility) — independently verified as INCORRECT; code already works correctly
- Any changes to `StrategyInputHandler` sub-routers
- New feature work
- Changes to serialization format

## Key Files
| Component | File Path |
|-----------|-----------|
| Galaxy facade | `game/strategy/data/galaxy.py` |
| Spatial index delegate | `game/strategy/data/galaxy_spatial_index.py` |
| Entity registry delegate | `game/strategy/data/galaxy_entity_registry.py` |
| Galaxy tests | `tests/unit/strategy/data/test_galaxy.py` |
| Galaxy cleanup tests | `tests/unit/strategy/data/test_galaxy_cleanup.py` |
| System query integration tests | `tests/integration/strategy/facade/test_system_queries.py` |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Exclude audit finding #5 (chain-of-responsibility) | Independent verification confirmed code DOES check return values at lines 124-131. Audit was incorrect. |
| 2026-02-24 | Downgrade finding #1 from "critical bug" to "misleading docstring" | `get_system_of_object` is only called with Fleet objects (2 call sites). Planet would return None, not false-match. Fix is docstring + type hint. |
| 2026-02-24 | Add `restore_planet()` method instead of flag on `register_planet()` | Clean separation of concerns: `register_planet()` for new planets (assigns ID), `restore_planet()` for deserialization (preserves ID). No boolean flags. |
| 2026-02-24 | Add `_zone_to_system` index for O(1) zone→system lookup | Required by `get_system_at_location()` O(1) refactor. `_planet_to_system` exists for planets; zones need equivalent. |

## Initial Analysis
Independent agent swarm verified all 5 audit findings:
- **Finding 1** (get_system_of_object): Misleading docstring, not a runtime bug. Only fleets passed.
- **Finding 2** (bypassed delegate): CONFIRMED. Galaxy.get_zones_at_global_hex bypasses spatial index.
- **Finding 3** (O(N) complexity): CONFIRMED. Can be made O(1) using existing indexes + new zone→system map.
- **Finding 4** (from_dict encapsulation): CONFIRMED. Duplicates register_planet() logic, mutates 4 private properties.
- **Finding 5** (chain-of-responsibility): INCORRECT. Code properly checks return values.

## Swarm Findings Summary
### Architecture
- Galaxy uses facade/delegate pattern: `_spatial` (GalaxySpatialIndex) + `_registry` (GalaxyEntityRegistry)
- All other spatial methods delegate correctly; only `get_zones_at_global_hex` is inconsistent
- Both delegates access Galaxy internals via parent reference (`self._galaxy`)

### Key Patterns to Reuse
- **Existing delegation**: `get_planets_at_global_hex` → `self._spatial.get_planets_at_global_hex()` (line 257)
- **Planet restore pattern**: `from_dict()` restores IDs from saved data, cannot use `register_planet()` directly

### Risks Identified
1. **`from_dict()` ID restoration** — `restore_planet()` must NOT assign new IDs. Tests must verify ID preservation.
2. **Warp point index gap** — `get_system_at_location()` has no O(1) warp point lookup. Need `_global_hex_warp_points` or similar. Alternatively, warp points are rare enough to handle via zone/planet indexes.

---

## Phases

### Phase 1: Fix Delegation & Docstring Issues [Simple]
**Objective:** Fix the two simplest issues — the bypassed delegate and the misleading docstring.
**Status:** Not Started

#### Task 1.1: Fix Galaxy.get_zones_at_global_hex to delegate properly [Simple]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py tests/integration/strategy/facade/test_system_queries.py -x`
- [ ] Change line 306: `return self._global_hex_zones.get(global_hex, [])` → `return self._spatial.get_zones_at_global_hex(global_hex)`
- [ ] Add "Facade method delegating to GalaxySpatialIndex." to the docstring (line 298-305)
- [ ] Verify: Run tests, behavior unchanged (identical implementation in delegate)
**Notes:**

#### Task 1.2: Fix get_system_of_object docstring and type hint [Simple]
**File:** `game/strategy/data/galaxy_spatial_index.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py tests/integration/strategy/facade/test_system_queries.py -x`
- [ ] Update docstring at line 33: Change "Fleet, Planet, etc" to "Fleet" only
- [ ] Add note in docstring: "For planets, use get_system_of_planet() instead."
- [ ] Update Galaxy facade docstring at `game/strategy/data/galaxy.py` line 197 similarly
- [ ] Verify: No behavioral change, docstring-only fix
**Notes:**

### Phase 2: Encapsulation & Performance Improvements [Medium]
**Objective:** Fix from_dict() encapsulation violation and make get_system_at_location() O(1).
**Status:** Not Started

#### Task 2.1: Add restore_planet() to GalaxyEntityRegistry [Medium]
**File:** `game/strategy/data/galaxy_entity_registry.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py tests/unit/strategy/data/test_galaxy_cleanup.py -x`
- [ ] Add `restore_planet(self, system, planet)` method to `GalaxyEntityRegistry`:
  ```python
  def restore_planet(self, system: 'StarSystem', planet: 'Planet') -> None:
      """Register a planet with pre-existing ID (for deserialization).

      Unlike register_planet(), this does NOT assign a new ID.
      The planet.id must already be set (from Planet.from_dict()).
      """
      self._galaxy.planets_by_id[planet.id] = planet
      self._galaxy._planet_to_system[planet] = system
      global_hex = system.global_location + planet.location
      if global_hex not in self._galaxy._global_hex_planets:
          self._galaxy._global_hex_planets[global_hex] = []
      self._galaxy._global_hex_planets[global_hex].append(planet)
      if hasattr(planet, 'diameter_hexes') and planet.diameter_hexes > 0:
          self.register_zone(system, planet)
  ```
- [ ] Update `Galaxy.from_dict()` (lines 567-583 in `galaxy.py`) to call `galaxy._registry.restore_planet(system, planet)` instead of manual index rebuilding
- [ ] Write test: deserialize galaxy, verify planet IDs are preserved (not reassigned)
- [ ] Write test: deserialize galaxy, verify `get_system_of_planet()` works for all restored planets
- [ ] Verify: Full test suite passes, save/load works identically
**Notes:**

#### Task 2.2: Add zone-to-system index and refactor get_system_at_location() to O(1) [Medium]
**File:** `game/strategy/data/galaxy_entity_registry.py`, `game/strategy/data/galaxy_spatial_index.py`
**Tests:** `pytest tests/unit/strategy/data/ tests/integration/strategy/facade/test_system_queries.py tests/unit/strategy/validation/ -x`
- [ ] Add `_zone_to_system = {}` dict to `Galaxy.__init__()` (in `galaxy.py`, after line 164)
- [ ] Update `GalaxyEntityRegistry.register_zone()` to also set `self._galaxy._zone_to_system[obj] = system`
- [ ] Update `GalaxyEntityRegistry.unregister_zone()` to also remove from `_zone_to_system`
- [ ] Add `_global_hex_warp_points = {}` dict to `Galaxy.__init__()` for warp point O(1) lookup
- [ ] Register warp points into spatial index in `Galaxy.add_system()` and `Galaxy.from_dict()`
- [ ] Refactor `GalaxySpatialIndex.get_system_at_location()` to use O(1) lookups:
  ```python
  def get_system_at_location(self, location):
      # O(1) direct system lookup
      if location in self._galaxy.systems:
          return self._galaxy.systems[location]
      # O(1) planet lookup
      planets = self._galaxy._global_hex_planets.get(location, [])
      if planets:
          return self._galaxy._planet_to_system.get(planets[0])
      # O(1) zone lookup (stars, Dyson Spheres)
      zones = self._galaxy._global_hex_zones.get(location, [])
      if zones:
          return self._galaxy._zone_to_system.get(zones[0])
      # O(1) warp point lookup
      wp_system = self._galaxy._global_hex_warp_points.get(location)
      if wp_system:
          return wp_system
      return None
  ```
- [ ] Write test: `get_system_at_location()` finds system via planet hex
- [ ] Write test: `get_system_at_location()` finds system via star/zone hex
- [ ] Write test: `get_system_at_location()` finds system via warp point hex
- [ ] Write test: `get_system_at_location()` returns None for deep space hex
- [ ] Verify: All existing callers still work (14 production call sites)
**Notes:** Warp point index is new — need to register warp points the same way planets/zones are registered.

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/` - all tests pass (12,338 passed, 1 skipped)

### After Each Phase
- [x] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] Manual test: Load a saved game, verify galaxy rendering and fleet movement work
- [x] Verify: Zone lookups, planet lookups, system-at-location queries all work

### Final Verification
- [x] Run full test suite: `pytest tests/ -n 12` (NOT --testmon, full verification) - 12358 passed, 1 skipped
- [x] All facade methods delegate consistently (no direct dict access)
- [x] All spatial methods are O(1)

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | 2026-02-24 | External audit: 5 findings, 4 confirmed valid | PROJ-179 created |
| 2 | 2026-02-24 | All objectives verified, no issues found | PASSED |

## Completion Checklist
- [x] All Phase 1 tasks checked off
- [x] All Phase 2 tasks checked off
- [x] All tests passing (12358 passed, 1 skipped)
- [x] Regression tests passing
- [x] Audit passed (no significant issues)
- [ ] User verified
