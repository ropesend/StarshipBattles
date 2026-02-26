# Safety Analysis: filter_ships Refactoring

**Target:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py` (lines 124-222)
**Cyclomatic Complexity:** 36 (high)
**Lines of Code:** ~99 lines

---

## 1. Edge Cases and Error Handling

### Currently Handled

| Edge Case | Handling | Line(s) |
|-----------|----------|---------|
| Empty ships list | Loop simply returns empty result | 141-142 |
| Missing filter keys | Uses `.get(key, True)` with True default | 144-145, 156-157, etc. |
| `cargo_contents` is None | N/A - code assumes dict exists | 170 |
| `cargo_contents` values are 0 | Correctly treated as "no cargo" via `sum() > 0` | 170 |

### NOT Handled (Potential Risks)

| Edge Case | Risk Level | Issue |
|-----------|------------|-------|
| **Ships with None `cargo_contents`** | MEDIUM | Line 170 would raise `TypeError` if `ship.cargo_contents` is `None` rather than empty dict |
| **Missing `is_alive` attribute** | LOW | Line 197 assumes attribute exists |
| **Missing `is_derelict` attribute** | LOW | Line 204 assumes attribute exists |
| **Missing `is_damaged()` method** | LOW | Line 211 assumes method exists |
| **filter_state is None** | MEDIUM | No explicit check; would fail on `.get()` calls |

### Recommendation
The code relies on the `ShipInstance` interface being correctly implemented. Consider adding defensive checks:
```python
has_cargo = ship.cargo_contents and sum(ship.cargo_contents.values()) > 0
```

---

## 2. Invariants That MUST Be Preserved

### Critical Invariants

1. **Filter evaluation order matters for status filters:**
   - Destroyed ships are checked FIRST (line 197)
   - Derelict ships are checked SECOND (line 204)
   - Damaged ships are checked THIRD (line 211)
   - Undamaged is the FALLBACK (line 218)

   **Rationale:** A derelict ship is also damaged. A destroyed ship might also be marked derelict. The priority order prevents double-counting.

2. **Default filter behavior is "show all" (True):**
   - All `.get()` calls default to `True`
   - This ensures missing filter keys show ships rather than hide them
   - **MUST preserve:** `filter_state.get('show_xyz', True)`

3. **Short-circuit optimization for binary filters:**
   - Lines 148, 158, 169, 184 check `if not show_X or not show_Y` before expensive lookups
   - If both are True, the check is skipped entirely
   - **MUST preserve:** Don't call `ShipStatsCalculator.has_warp_capability()` or `FleetCapabilityCalculator.ship_has_ability()` unless necessary

4. **Special capability filter key derivation:**
   - Line 182: `no_key = col_id.replace('can_', 'no_', 1)`
   - Maps `can_destroy_planet` -> `no_destroy_planet`
   - This naming convention MUST match `FleetListViewModel.get_filter_state()` keys

5. **Result list must maintain input order (for stable sorting):**
   - Ships are appended in iteration order
   - No reordering happens within filter_ships
   - Sorting is applied AFTER filtering in the caller

### Implicit Contracts

- `ship.is_alive` is a boolean property
- `ship.is_derelict` is a boolean property
- `ship.is_damaged()` is a callable returning boolean
- `ship.cargo_contents` is a dict (or falsy)
- `SPECIAL_CAPABILITY_COLUMNS` is a dict mapping column_id -> ability_name

---

## 3. Risk Areas

### HIGH RISK

| Area | Lines | Why Risky |
|------|-------|-----------|
| **Special capability loop with break** | 176-194 | Complex iteration with early exit. The `_skip` flag pattern is error-prone. Missing break would cause false positives. |
| **Status filter cascade** | 196-221 | The if/continue/append pattern must maintain strict priority. Incorrect ordering would cause ships to be misclassified. |
| **Filter key naming convention** | 182-183 | The `can_` -> `no_` transformation is implicit. Any new filter keys must follow this pattern. |

### MEDIUM RISK

| Area | Lines | Why Risky |
|------|-------|-----------|
| **Late imports inside loop** | 149, 159-160, 185-186 | Import statements inside the for loop. While intentional (to avoid circular imports), they add overhead per iteration and could cause import errors at runtime. |
| **Implicit dependency on SPECIAL_CAPABILITY_COLUMNS** | 178 | External constant imported from `fleet_data_source`. Changes there affect filter behavior here. |
| **Cargo check logic** | 170 | `bool(ship.cargo_contents) and sum(...)` - the `sum()` will fail if values aren't numeric |

### LOW RISK

| Area | Lines | Why Risky |
|------|-------|-----------|
| Warp capability check | 144-153 | Simple binary filter, well-isolated |
| Spaceyard capability check | 155-164 | Simple binary filter, well-isolated |

---

## 4. Missing Test Coverage

### Test File Analysis: `test_fleet_report_filters.py`

**Classes tested:**
- `TestFilterShips` - basic status filters (damaged, undamaged, derelict, destroyed)
- `TestFilterShipsWarp` - warp capability filters
- `TestFilterShipsSpaceyard` - spaceyard filters
- `TestFilterShipsCargo` - cargo filters
- `TestSpecialCapabilityFilter` - special ability filters

### GAPS Identified

| Gap | Severity | Description |
|-----|----------|-------------|
| **Empty filter_state dict** | HIGH | No test with `filter_ships(ships, {})` - defaults should apply |
| **None filter_state** | HIGH | No test with `filter_ships(ships, None)` - would crash |
| **All filters disabled** | MEDIUM | No test where ALL filters are False (should return empty list) |
| **Combined filter interactions** | MEDIUM | No tests for warp + cargo + spaceyard + special filters together |
| **Ships with None cargo_contents** | MEDIUM | Tests use `{}` or populated dict, never `None` |
| **Multiple special capabilities on same ship** | LOW | Only tests single ability per ship |
| **Filter key typos** | LOW | No test that unknown filter keys are safely ignored |
| **Very large ship lists** | LOW | No performance tests with 1000+ ships |

### Tests That SHOULD Exist But Don't

```python
def test_filter_ships_empty_filter_state():
    """Empty filter state should use all defaults (show all)."""
    ships = [make_mock_ship()]
    result = filter_ships(ships, {})
    assert len(result) == 1

def test_filter_ships_all_filters_false():
    """All filters False should return empty list."""
    ships = [make_mock_ship()]
    filter_state = {
        'show_damaged': False,
        'show_undamaged': False,
        'show_derelict': False,
        'show_destroyed': False,
    }
    result = filter_ships(ships, filter_state)
    assert len(result) == 0

def test_filter_ships_cargo_contents_none():
    """Ship with cargo_contents=None should not crash."""
    ship = make_mock_ship()
    ship.cargo_contents = None
    result = filter_ships([ship], {'show_no_cargo': False})
    # Should either include ship or handle gracefully

def test_filter_combined_warp_spaceyard_cargo():
    """Multiple capability filters combine correctly."""
    # Complex test with ships having various combinations
```

---

## 5. Refactorability Assessment

### Can This Function Be Refactored?

**YES**, but with care. The function is NOT irreducibly complex.

### Structural Analysis

The function has **three distinct filter categories:**

1. **Capability filters** (lines 143-194): Binary yes/no checks
   - Warp capability
   - Spaceyard capability
   - Cargo presence
   - Special abilities (5 types)

2. **Status filters** (lines 196-221): Mutually exclusive states
   - Destroyed -> Derelict -> Damaged -> Undamaged
   - **Priority cascade** - must check in this order

3. **Loop mechanics** (lines 141-142, 220): Ship iteration and result building

### Recommended Refactoring Approach

**Strategy: Extract + Compose**

```python
def filter_ships(ships, filter_state):
    result = []
    for ship in ships:
        if _passes_capability_filters(ship, filter_state):
            if _passes_status_filter(ship, filter_state):
                result.append(ship)
    return result

def _passes_capability_filters(ship, filter_state):
    """Check warp, spaceyard, cargo, and special abilities."""
    if not _check_binary_filter(ship, filter_state, 'warp',
                                lambda s: ShipStatsCalculator.has_warp_capability(s)):
        return False
    # ... etc
    return True

def _passes_status_filter(ship, filter_state):
    """Check destroyed/derelict/damaged/undamaged status."""
    if not ship.is_alive:
        return filter_state.get('show_destroyed', True)
    if ship.is_derelict:
        return filter_state.get('show_derelict', True)
    # ... etc
```

### Complexity Sources

| Source | Lines | Contribution | Reducible? |
|--------|-------|--------------|------------|
| Capability filter if-checks | 148-194 | ~10 branches | YES - extract helper |
| Status filter cascade | 196-221 | ~8 branches | YES - extract helper |
| Special capability loop | 176-194 | ~6 branches | YES - extract helper |
| Short-circuit checks | Various | ~8 branches | Partially - some are optimization |

### Irreducible Complexity

The following cannot be simplified without changing behavior:
- The status filter priority (destroyed > derelict > damaged > undamaged)
- The "show both = skip check" optimization pattern
- The `can_` -> `no_` key derivation for special capabilities

---

## 6. Final Recommendation

### Refactoring Verdict: PROCEED WITH CAUTION

**Risk Level:** MEDIUM

**Recommended Actions:**

1. **Before refactoring:**
   - Add missing tests for edge cases (empty filter_state, None cargo_contents)
   - Add tests for combined filter scenarios
   - Run full test suite to establish baseline

2. **Refactoring approach:**
   - Extract `_passes_capability_filters()` helper
   - Extract `_passes_status_filter()` helper
   - Keep the short-circuit optimizations
   - Preserve import locations (late imports are intentional)

3. **After refactoring:**
   - Verify all existing tests pass
   - Manually test in-game with various fleet compositions
   - Check performance with large fleets (100+ ships)

4. **Do NOT change:**
   - Filter default behavior (True = show)
   - Status filter priority order
   - Special capability key derivation logic
   - The fact that missing filter keys default to "show"

### Confidence Assessment

| Aspect | Confidence |
|--------|------------|
| Understanding of function behavior | HIGH |
| Test coverage adequacy | MEDIUM (gaps exist) |
| Safe refactoring path exists | HIGH |
| Risk of introducing bugs | MEDIUM |

The function is complex but follows consistent patterns. The main risks are in the special capability loop and the status filter cascade. Both can be safely extracted with proper test coverage.
