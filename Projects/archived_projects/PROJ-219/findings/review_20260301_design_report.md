# PROJ-219: Design Pattern Analysis Report

**Date:** 2026-03-01
**Analyst:** Design Pattern Analyst
**Scope:** Verify proposed Empire-Galaxy back-reference pattern against current codebase

---

## Executive Summary

The project plan proposes adding a `_galaxy` back-reference to `Empire` to enable automatic fleet registration/unregistration. After analyzing the current codebase state, **the design remains valid and aligned with existing patterns**. Three minor concerns were identified, all with straightforward resolutions that do not require plan changes.

**Findings:** 3 total
- 0 Critical (blocks implementation)
- 0 Major (requires plan modification)
- 3 Minor (implementation guidance)

**Recommendation:** Proceed with implementation as designed.

---

## Design Pattern Verification

### 1. Empire-Galaxy Back-Reference Pattern

**Plan Assumption:** Empire can hold an optional `_galaxy` reference for auto-registration.

**Current Reality:** The pattern is consistent with existing codebase conventions:
- `FleetMovementEngine` uses `self._nav_service = None` for lazy initialization (similar optional dependency)
- `Empire.add_colony()` already sets `planet.owner_id` (similar ownership pattern)
- `GalaxyEntityRegistry` holds `self._galaxy` back-reference (precedent for galaxy references in registry classes)
- Many classes use `if self._dependency:` guards for optional dependencies

**Impact:** Pattern is appropriate. No conflict.

---

### 2. Registration/Unregistration API

**Plan Assumption:** `galaxy.register_fleet(fleet)` and `galaxy.unregister_fleet(fleet)` exist with expected signatures.

**Current Reality:** Verified at:
- `galaxy.py:365-373` - `register_fleet()` delegates to `GalaxyEntityRegistry`
- `galaxy.py:375-383` - `unregister_fleet()` delegates to `GalaxyEntityRegistry`
- `galaxy_entity_registry.py:129-143` - Implementation uses `fleets_by_id[fleet.id]` and `pop(fleet.id, None)`

**Impact:** APIs exist exactly as expected. `pop(id, None)` is idempotent as noted in decisions.md.

---

### 3. Layer Architecture Compliance

**Plan Assumption:** Empire-Galaxy coupling is acceptable (both in Strategy layer).

**Current Reality:**
- `Empire` is in `game/strategy/data/empire.py`
- `Galaxy` is in `game/strategy/data/galaxy.py`
- Both are strategy-layer entities with existing cross-references (Empire stores colony_ids referencing Planet objects)

**Impact:** No layer violation. Coupling is appropriate.

---

## Findings

### DP-01: Stellarate Double-Unregister Order

**Plan Assumption:** Phase 3 Task 3.3 instructs removing line 239 (`galaxy.unregister_fleet(victim_fleet)`) before `owner_empire.remove_fleet(victim_fleet)` since auto-unregistration will handle it.

**Current Reality:** In `superweapon_order_processor.py:238-241`, the code is:
```python
# Unregister from galaxy (Galaxy always has unregister_fleet)
galaxy.unregister_fleet(victim_fleet)
# Remove from empire
owner_empire.remove_fleet(victim_fleet)
```

After PROJ-219, if we remove line 239, `remove_fleet()` will call `unregister_fleet()` internally. However, the `victim_fleet.owner_id` is for the **victim's empire** (could be ANY empire in the galaxy), not necessarily the acting empire. The stellarate loop iterates over `all_fleets_in_system` which includes fleets from all empires.

**Impact:** LOW - The design works correctly because:
1. `victim_fleet.owner_id` points to the correct owning empire
2. `owner_empire.remove_fleet(victim_fleet)` uses the owning empire from the loop
3. The owning empire will have `_galaxy` set (via Phase 2 wiring)

**Proposed Resolution:** No plan change needed. The implementation will work as designed because the loop correctly identifies the owning empire for each fleet. Add a comment for clarity:
```python
# PROJ-219: remove_fleet() auto-unregisters via owner_empire._galaxy
owner_empire.remove_fleet(victim_fleet)
```

---

### DP-02: Test Import Path for HexCoord

**Plan Assumption:** Phase 1 Task 1.5 test template imports `from game.core.hex_utils import HexCoord`.

**Current Reality:** The correct import is `from game.core.hex_math import HexCoord`. The module is `hex_math.py`, not `hex_utils.py`.

**Impact:** LOW - Test will fail to run with ImportError if template is copied verbatim.

**Proposed Resolution:** Update test template in Phase 1 checklist:
```python
# Change:
from game.core.hex_utils import HexCoord
# To:
from game.core.hex_math import HexCoord
```

---

### DP-03: GameSession.from_dict Fleet Registration Loop Placement

**Plan Assumption:** Phase 2 Task 2.2 instructs adding galaxy wiring "after empire deserialization (line 342), before fleet registration loop (line 353)".

**Current Reality:** Looking at `game_session.py:339-357`:
```python
# Step 2: Load Empires (resolves planet references via galaxy)
try:
    session.empires = [
        Empire.from_dict(emp_data, galaxy=session.galaxy)  # Line 340
        for emp_data in data.get('empires', [])
    ]
...
# PROJ-216: Register all fleets with galaxy for O(1) lookup  (Line 353)
# Fleets are deserialized into empires but not automatically registered
for empire in session.empires:
    for fleet in empire.fleets:
        session.galaxy.register_fleet(fleet)
```

The explicit fleet registration loop (lines 353-357) MUST remain because:
1. Fleets are deserialized inside `Empire.from_dict()` via `Fleet.from_dict()`
2. This happens BEFORE `set_galaxy()` is called
3. Deserialized fleets bypass `add_fleet()` - they're directly appended to `empire.fleets`

**Impact:** MEDIUM - If the loop were incorrectly removed, loaded games would have unregistered fleets.

**Proposed Resolution:** The plan already correctly states "Keep the existing fleet registration loop (lines 353-357)". This finding confirms the design is correct. Add explicit comment explaining WHY:
```python
# PROJ-219: Set galaxy back-references for future operations
for empire in session.empires:
    empire.set_galaxy(session.galaxy)

# NOTE: Deserialized fleets still need explicit registration because
# Empire.from_dict() populates empire.fleets directly, bypassing add_fleet().
# Future runtime add_fleet() calls will auto-register.
for empire in session.empires:
    for fleet in empire.fleets:
        session.galaxy.register_fleet(fleet)
```

---

## Codebase Patterns Reviewed

### Existing Back-Reference Patterns

| Class | Back-Reference | Purpose |
|-------|---------------|---------|
| `GalaxyEntityRegistry` | `self._galaxy` | Access galaxy state for registration |
| `GalaxySpatialIndex` | `self._galaxy` | Access galaxy state for lookups |
| `GalaxyWarpGenerator` | N/A (pure) | Takes galaxy as method parameter |
| `GalaxySystemGenerator` | N/A (pure) | Takes galaxy as method parameter |

The proposed `Empire._galaxy` follows the `GalaxyEntityRegistry` precedent - storing a reference to enable operations that need galaxy context.

### Similar Two-Method Lifecycle Patterns

| Owner | Add Method | Remove Method | Auto-Registration |
|-------|------------|---------------|-------------------|
| `Empire` | `add_colony(planet)` | `remove_colony(planet)` | Sets `planet.owner_id` |
| `Empire` | `add_fleet(fleet)` | `remove_fleet(fleet)` | **PROPOSED:** Auto-registers with galaxy |
| `StarSystem` | `add_warp_point()` | (manual list ops) | N/A |

The proposed change makes `add_fleet/remove_fleet` consistent with `add_colony/remove_colony` pattern.

---

## Ghost Fleet Bug Fix Coverage

The plan identifies 6 locations calling `remove_fleet()` without unregistering. After PROJ-219, ALL will auto-unregister:

| Location | File:Line | Status After PROJ-219 |
|----------|-----------|----------------------|
| Combat destruction | `conflict_resolution_engine.py:186` | FIXED - auto-unregisters |
| JOIN_FLEET merge | `fleet_order_processor.py:113` | FIXED - auto-unregisters |
| COLONIZE empty | `fleet_order_processor.py:216` | FIXED - auto-unregisters |
| Instant merge | `fleet_order_processor.py:663` | FIXED - auto-unregisters |
| Superweapon finalize | `superweapon_order_processor.py:103` | FIXED - auto-unregisters |
| Maintenance scuttle | `maintenance_engine.py:286` | FIXED - auto-unregisters |
| Stellarate (explicit) | `superweapon_order_processor.py:239-241` | Redundant explicit call removed |
| Self-destruct | `superweapon_order_processor.py:613` | FIXED - auto-unregisters |

**Note:** One additional location was found: `superweapon_order_processor.py:613` (self-destruct). This was not in the original plan bug list but will also be fixed automatically.

---

## Recommendations

1. **Proceed with implementation** - The design is sound and aligns with existing patterns.

2. **Fix test import path** (DP-02) - Update `hex_utils` to `hex_math` in Phase 1 checklist before starting implementation.

3. **Add explanatory comments** (DP-03) - When implementing Phase 2 Task 2.2, add comments explaining why the explicit fleet registration loop must remain.

4. **Verify 7 locations fixed** - Add `superweapon_order_processor.py:613` (self-destruct) to Phase 4 integration test coverage.

---

## Conclusion

The proposed Empire-Galaxy back-reference design is well-suited to the codebase. It follows established patterns, fixes real bugs, and simplifies the fleet lifecycle model. The three minor findings are implementation details that do not require plan modifications.

**Verdict: APPROVED FOR IMPLEMENTATION**
