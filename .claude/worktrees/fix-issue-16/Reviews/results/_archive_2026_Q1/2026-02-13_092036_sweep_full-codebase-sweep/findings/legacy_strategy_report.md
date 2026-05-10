# Legacy System Holdovers Report: game/strategy/

**Scope:** `game/strategy/` (all subdirectories)
**Agent:** Sweep Agent - Strategy Shard
**Date:** 2026-02-13
**Files Scanned:** 95 Python files

---

## Summary

The `game/strategy/` directory shows a well-maintained codebase with evidence of systematic refactoring (PROJ-12, PROJ-35, PROJ-36, PROJ-42, PROJ-43, PROJ-50, PROJ-55, PROJ-58, PROJ-75, PROJ-87, PROJ-102). Most "backward compatibility" comments refer to legitimate API stability patterns rather than technical debt. However, several issues warrant attention.

**Statistics:**
- Files with potential legacy patterns: 8
- CRITICAL issues: 0
- MAJOR issues: 2
- MINOR issues: 3
- INFO observations: 4

---

## Findings

### MAJOR Issues

#### LEG-STR-001: MAJOR: Legacy behavior dual code path in FleetOrderProcessor.process_colonize()

**File:** `C:\Dev\Starship Battles\game\strategy\engine\fleet_order_processor.py`
**Lines:** 179-232

**Description:**
The `process_colonize()` method has an explicit "legacy behavior" code path that removes the entire fleet when `component_registry` is None, versus removing only the colony ship when the registry is provided.

```python
# PROJ-55: Remove only colony ship when registry is provided
if component_registry is not None:
    # ... new behavior - remove only colony ship ...
else:
    # Legacy behavior: remove entire fleet
    empire.remove_fleet(fleet)
```

**Rationale:**
This dual code path creates two different behaviors for the same operation depending on whether a registry is passed. Per project policy, the registry-based path should be the only path. The comment explicitly labels this as "legacy behavior."

**Recommendation:**
Remove the legacy code path. Make `component_registry` required (or always resolve it from DI) and delete the else branch. Update tests that rely on the legacy behavior.

---

#### LEG-STR-002: MAJOR: Legacy items without cost tracking in ProductionEngine

**File:** `C:\Dev\Starship Battles\game\strategy\engine\production_engine.py`
**Lines:** 96-97, 154-156, 220-221

**Description:**
The production engine has multiple comments about "legacy items without cost tracking" being skipped for resource consumption:

```python
# Skip legacy items without cost tracking
if cost_per_tick is None:
    return

# Legacy items without cost tracking - fall back to old behavior
if cost_per_tick is None:
    return
```

**Rationale:**
PROJ-75 Phase 4 introduced per-tick resource consumption, but kept fallback for items without the new `cost_per_tick` field. This creates two production models running in parallel - items with cost tracking use the new tick-based system while legacy items use the old turn-decrement model.

**Recommendation:**
Add a migration script or game startup routine that upgrades all queue items to include cost tracking fields. Then remove the `cost_per_tick is None` fallbacks.

---

### MINOR Issues

#### LEG-STR-003: MINOR: O(n) fallback for fleet lookup in GameSession._get_fleet_by_id()

**File:** `C:\Dev\Starship Battles\game\strategy\engine\game_session.py`
**Lines:** 208-232

**Description:**
The fleet lookup has an O(n) fallback "for backward compatibility with tests":

```python
# Try O(1) registry lookup first
fleet = self.galaxy.get_fleet_by_id(fleet_id)
if fleet is not None:
    return fleet

# Fallback to O(n) iteration (for backward compatibility)
for emp in self.empires:
    for f in emp.fleets:
        if f.id == fleet_id:
            return f
```

**Rationale:**
The comment explicitly states this is for "backward compatibility with tests that don't register fleets with the galaxy." Tests should use proper fixtures.

**Recommendation:**
Update tests to properly register fleets with the galaxy registry. Remove the O(n) fallback after verifying all tests pass with proper registration.

---

#### LEG-STR-004: MINOR: Fallback to expected_stats in ShipStatsCalculator

**File:** `C:\Dev\Starship Battles\game\strategy\services\ship_stats_calculator.py`
**Lines:** 129-143

**Description:**
When no components are found in a design's layers, the calculator falls back to `expected_stats`:

```python
# Fallback to expected_stats if no components found in layers
# This handles test fixtures and designs without component registry entries
if not components_found:
    expected = design_data.get('expected_stats', {})
    return {...}
```

**Rationale:**
This exists to support "test fixtures" which may not have proper component structures. Real designs should always have component layers.

**Recommendation:**
Audit test fixtures to ensure they have proper component structures. Consider making this fallback emit a warning in non-test contexts.

---

#### LEG-STR-005: MINOR: Backward-compatible defaults in RaceConfig.from_dict()

**File:** `C:\Dev\Starship Battles\game\strategy\data\race_config.py`
**Lines:** 197-244

**Description:**
The `from_dict()` method uses extensive `.get()` with defaults for "backward-compatible defaults":

```python
@classmethod
def from_dict(cls, data: dict) -> 'RaceConfig':
    """Deserialize from dictionary with backward-compatible defaults."""
    return cls(
        race_id=data.get("race_id", ""),
        name=data.get("name", ""),
        # ... many more fields with defaults ...
    )
```

**Rationale:**
This is a deserialization method that provides defaults for missing fields. Per project policy, old saves are discarded, not migrated. If the save format has changed, the version check should reject it rather than silently defaulting.

**Recommendation:**
Verify SaveGameService version checking rejects incompatible saves. If it does, the defaults are defensive programming and acceptable. If not, add stricter validation.

---

### INFO Observations

#### LEG-STR-006: INFO: Internal API consistency note in FleetNavigationService

**File:** `C:\Dev\Starship Battles\game\strategy\services\fleet_navigation_service.py`
**Lines:** 83-91

**Description:**
The `PathSegment.to_dict()` method includes a 'hex' field with a note about "internal API consistency":

```python
def to_dict(self) -> Dict[str, Any]:
    """Convert to dict for serialization.

    Note: The 'hex' field duplicates 'end' for consistency with internal
    path projection code in pathfinding.py that accesses pt['hex'].
    This is not external backward compatibility - it's internal API consistency.
    """
```

**Rationale:**
The comment explicitly clarifies this is NOT external backward compatibility. This is legitimate API design.

**Recommendation:**
No action needed. This is a proper adapter pattern.

---

#### LEG-STR-007: INFO: NavigationState supports both Fleet and NavigationState in pathfinding

**File:** `C:\Dev\Starship Battles\game\strategy\data\pathfinding.py`
**Lines:** 379-408

**Description:**
The `calculate_intercept_point()` function accepts both Fleet and NavigationState objects "for backward compatibility and pure function usage":

```python
def calculate_intercept_point(
    chaser: Union['Fleet', 'NavigationState'],
    target_fleet,
    galaxy
) -> Optional[HexCoord]:
    """
    ...
    Args:
        chaser: Fleet or NavigationState representing the pursuing fleet.
                Supports both for backward compatibility and pure function usage.
    """
```

**Rationale:**
The `_ChaserProxy` class comment (lines 275-287) explicitly states this is "an intentional adapter pattern (not legacy compatibility)" reviewed in PROJ-42.

**Recommendation:**
No action needed. This is documented and intentional.

---

#### LEG-STR-008: INFO: Backward compat for populations in Planet.from_dict()

**File:** `C:\Dev\Starship Battles\game\strategy\data\planet.py`
**Lines:** 363-370

**Description:**
Populations deserialization uses empty list default "for backward compat":

```python
# Deserialize populations (default empty for backward compat)
populations = [
    SpeciesPopulation(...) for p in data.get('populations', [])
]
```

**Rationale:**
This is defensive deserialization. The SaveGameService should reject incompatible versions before this code runs.

**Recommendation:**
Verify version checking handles this. If saves without populations are rejected, this comment is misleading and should be updated to "default empty for robustness."

---

#### LEG-STR-009: INFO: Legacy string fallback in FleetBattleAdapter

**File:** `C:\Dev\Starship Battles\game\strategy\data\fleet_battle_adapter.py`
**Lines:** 47-48

**Description:**
Comment notes that "legacy strings cannot be converted":

```python
"""Convert fleet ships to simulation Ship objects for battle.

Only works with ShipInstance objects - legacy strings cannot be converted.
```

**Rationale:**
This appears to be documentation of a limitation rather than active legacy code. The code only iterates ShipInstance objects.

**Recommendation:**
Verify no code path still uses string-based ship references. If confirmed, update comment to remove "legacy" framing.

---

## Top 5 Priority Issues

| Rank | ID | Severity | Summary | Effort |
|------|-----|----------|---------|--------|
| 1 | LEG-STR-001 | MAJOR | Dual code path in process_colonize() | Medium |
| 2 | LEG-STR-002 | MAJOR | Legacy items without cost tracking | High |
| 3 | LEG-STR-003 | MINOR | O(n) fallback for fleet lookup | Low |
| 4 | LEG-STR-004 | MINOR | Fallback to expected_stats | Low |
| 5 | LEG-STR-005 | MINOR | Backward-compatible defaults in RaceConfig | Low |

---

## Conclusion

The strategy layer is relatively clean with most "backward compatibility" patterns being either:
1. Legitimate adapter patterns (documented and reviewed in PROJ-42)
2. Defensive deserialization (acceptable if version checking is proper)
3. Test fixture accommodation (should be cleaned up)

The two MAJOR issues (LEG-STR-001, LEG-STR-002) represent actual dual code paths that should be unified. The MINOR issues are test-related fallbacks that create technical debt but are lower priority.

The codebase shows evidence of active maintenance and refactoring - most legacy patterns are documented with PROJ references and clear rationale.
