# Legacy Code Sweep Report: game/strategy/

**Scope:** `game/strategy/` (all subdirectories)
**Date:** 2026-02-13
**Agent:** Sweep Agent (Legacy Holdovers)

---

## Executive Summary

Scanned 60+ Python files in `game/strategy/`. Found **2 MINOR** findings and **5 INFO** items. The strategy module is generally well-maintained with no critical or major legacy issues. Most "backward compatibility" mentions are intentional adapter patterns or save format requirements rather than obsolete code.

---

## Findings

### MINOR Issues

#### MINOR: Save metadata duplicates turn_number field for compatibility
**File:** `C:\Dev\Starship Battles\game\strategy\systems\save_game_service.py`
**Lines:** 87-88

```python
'latest_turn_number': game_session.turn_number,
'turn_number': game_session.turn_number,  # For compatibility
```

**Impact:** Minor data redundancy. The comment suggests `turn_number` is kept for older code that may still read this field instead of `latest_turn_number`.

**Recommendation:** Per CLAUDE.md "Save files are disposable", this compatibility field can be removed. Update any code reading `turn_number` to use `latest_turn_number` and remove the duplicate field.

---

#### MINOR: _get_fleet_by_id has O(n) fallback for backward compatibility
**File:** `C:\Dev\Starship Battles\game\strategy\engine\game_session.py`
**Lines:** 208-232

```python
def _get_fleet_by_id(self, fleet_id: int):
    """
    Find fleet by ID, using Galaxy registry for O(1) lookup with fallback.

    PROJ-87 Phase 6: Tries galaxy.get_fleet_by_id() first for O(1) performance.
    Falls back to O(n) empire iteration for backward compatibility with tests
    that don't register fleets with the galaxy.
    ...
    """
    # Try O(1) registry lookup first
    fleet = self.galaxy.get_fleet_by_id(fleet_id)
    if fleet is not None:
        return fleet

    # Fallback to O(n) iteration (for backward compatibility)
    for emp in self.empires:
        for f in emp.fleets:
            if f.id == fleet_id:
                return f
    return None
```

**Impact:** Performance fallback exists to support tests that don't properly register fleets. This is a known workaround for test infrastructure gaps.

**Recommendation:** Fix test fixtures to properly register fleets with the galaxy, then remove the O(n) fallback. The comment explicitly states this is for "backward compatibility with tests" - not production code.

---

### INFO Items (Not Requiring Action)

#### INFO: PlayerConfig backwards compatibility comment is valid serialization logic
**File:** `C:\Dev\Starship Battles\game\strategy\engine\game_config.py`
**Lines:** 82-88

```python
# Only include race fields if set (backwards compatibility)
if self.race_id:
    data['race_id'] = self.race_id
if self.flag_id:
    data['flag_id'] = self.flag_id
```

**Assessment:** This is valid optional field serialization, not a compatibility shim. Race fields were added later and shouldn't be serialized when empty. No action needed.

---

#### INFO: FleetOrderProcessor legacy behavior is intentional API design
**File:** `C:\Dev\Starship Battles\game\strategy\engine\fleet_order_processor.py`
**Lines:** 178-181, 230-232

```python
component_registry: Optional component registry for colony pod lookup.
               When provided, only the colony ship is removed.
               When None, entire fleet is removed (legacy behavior).
...
# Legacy behavior: remove entire fleet
empire.remove_fleet(fleet)
```

**Assessment:** This is not dead code. It's intentional API design where `component_registry=None` triggers simpler behavior. The "legacy" label is a misnomer - this is the default behavior when component-level tracking isn't needed. No action required.

---

#### INFO: project_path_as_dicts backward compatibility is intentional API
**File:** `C:\Dev\Starship Battles\game\strategy\services\fleet_navigation_service.py`
**Lines:** 403-423

```python
def project_path_as_dicts(self, fleet: 'Fleet', galaxy, max_turns: int = 10) -> List[Dict]:
    """
    Project fleet path and return as list of dicts for backward compatibility.
    ...
    """
```

**Assessment:** The docstring mentions "backward compatibility" but review of callers shows this is the primary API for UI consumption (pathfinding.project_fleet_path delegates to it). The dict format is the expected interface, not a legacy shim. No action needed.

---

#### INFO: expected_stats fallback in ShipStatsCalculator is intentional
**File:** `C:\Dev\Starship Battles\game\strategy\services\ship_stats_calculator.py`
**Lines:** 129-143

```python
# Fallback to expected_stats if no components found in layers
# This handles test fixtures and designs without component registry entries
if not components_found:
    expected = design_data.get('expected_stats', {})
    return {
        'max_hp': expected.get('max_hp', 0),
        ...
    }
```

**Assessment:** This is intentional fallback for test fixtures and lightweight designs. The comment explicitly documents the purpose. The stats calculator needs to handle designs that don't have full component data. No action needed.

---

#### INFO: DesignMetadata sprite_preview placeholder is documented future work
**File:** `C:\Dev\Starship Battles\game\strategy\data\design_metadata.py`
**Lines:** 35-38

```python
# NOTE: When sprite_preview is implemented, the preview image should be
# stored in a separate UI cache, not in this strategy-layer metadata.
# This field exists as a placeholder for save file compatibility.
sprite_preview: Optional[str] = None  # Reserved for future use
```

**Assessment:** This is explicitly documented as a placeholder for forward compatibility, not legacy code. The comment correctly notes that the actual implementation should go in UI layer. No action needed now.

---

## Non-Findings (Reviewed and Cleared)

The following patterns were reviewed and determined to NOT be legacy issues:

1. **Production engine "legacy items" comments** (`production_engine.py:96,154,220`) - Refers to queue items without cost-tracking fields, which is valid data state during migration.

2. **_ChaserProxy adapter** (`pathfinding.py:275-296`) - Explicitly documented as "intentional adapter pattern (not legacy compatibility)" per PROJ-42 review.

3. **RaceConfig backward-compatible defaults** (`race_config.py:198`) - Standard defensive deserialization, not a shim.

4. **Planet.from_dict empty populations default** (`planet.py:355`) - Standard empty list default for optional field.

5. **FleetBattleAdapter "legacy strings" comment** (`fleet_battle_adapter.py:47`) - Documents that old string-based ship data format is no longer supported, which is correct behavior.

6. **Fleet order target formats** (`fleet.py:374-408`) - Multiple serialization formats for different order types, all actively used.

7. **Design obsolete/mark_obsolete methods** (`design_library.py`) - This is a feature (designs can be marked obsolete), not legacy code.

---

## Summary Statistics

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| MAJOR | 0 |
| MINOR | 2 |
| INFO | 5 |

**Total findings requiring action:** 2 (both MINOR)

---

## Recommendations

1. **Low Priority:** Remove `turn_number` compatibility field from save metadata once confirmed no code depends on it.

2. **Low Priority:** Update test infrastructure to register fleets properly with galaxy, then remove O(n) fallback in `_get_fleet_by_id`.

The strategy module shows good code hygiene with minimal legacy debt. The PROJ-87 decomposition (God Class Decomposition) and related migrations appear complete. No critical or major issues found.
