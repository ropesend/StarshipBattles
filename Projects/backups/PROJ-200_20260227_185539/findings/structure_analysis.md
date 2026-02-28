# Structure Analysis: `filter_ships` Function

**File:** `game/ui/screens/fleet_report_filters.py`
**Function:** `filter_ships` (lines 124-222)
**Purpose:** Filter ships based on status filter state dictionary

---

## 1. Branches/Conditions Contributing Most to Complexity

### 1.1 Binary Filter Pattern (High Repetition)
The function applies the same binary filtering pattern **5 times** for different capabilities:

| Lines | Filter Type | show_X | show_not_X |
|-------|-------------|--------|------------|
| 144-153 | Warp capability | `show_warp_capable` | `show_not_warp_capable` |
| 156-164 | Spaceyard capability | `show_has_spaceyard` | `show_no_spaceyard` |
| 167-174 | Cargo presence | `show_has_cargo` | `show_no_cargo` |
| 176-194 | Special capabilities (loop) | `show_{col_id}` | `show_{no_key}` |

Each instance adds 2 conditionals checking `if not show_X or not show_not_X`, then 2 more conditionals for inclusion/exclusion.

### 1.2 Status Category Cascade (Lines 196-220)
The ship status filtering uses a 4-way cascade with mutual exclusivity assumptions:
- Destroyed (lines 197-201)
- Derelict (lines 204-208)
- Damaged (lines 211-215)
- Undamaged/Healthy (lines 218-220)

Each category has:
- A status check (`not ship.is_alive`, `ship.is_derelict`, `ship.is_damaged()`)
- A filter state check
- Either `continue` or `result.append(ship)` followed by `continue`

### 1.3 Special Capabilities Loop (Lines 176-194)
This nested loop iterates over `SPECIAL_CAPABILITY_COLUMNS` (5 items), applying the binary filter pattern within a loop. Uses a `_skip` flag to break out and continue the outer loop.

**Complexity contribution:** O(n * 5) where n = number of ships, with up to 10 conditional checks per capability.

---

## 2. Nested Conditionals That Could Be Flattened

### 2.1 Double-Nested Filter Checks (Lines 148-153, 158-164, 169-174)
```python
# Current pattern (lines 148-153):
if not show_warp or not show_not_warp:
    is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
    if is_warp_capable and not show_warp:
        continue
    if not is_warp_capable and not show_not_warp:
        continue
```

**Nesting depth:** 2 levels within the main loop (total depth: 3)

This pattern appears 3 times with identical structure but different capability checks.

### 2.2 Special Capabilities Loop Nesting (Lines 176-194)
```python
for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
    # ...derive filter keys...
    if not show_has or not show_not:
        # ...import...
        has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
        if has_ability and not show_has:
            _skip = True
            break
        if not has_ability and not show_not:
            _skip = True
            break
if _skip:
    continue
```

**Nesting depth:** 3 levels within the main loop (total depth: 4)

### 2.3 Status Cascade Nesting (Lines 196-220)
```python
if not ship.is_alive:
    if not filter_state.get('show_destroyed', True):
        continue
    result.append(ship)
    continue
```

**Nesting depth:** 2 levels within the main loop (total depth: 3)

This pattern repeats 4 times for different status categories.

---

## 3. Early Returns/Continues That Could Simplify Logic

### 3.1 Current `continue` Usage
The function uses `continue` extensively (10 occurrences) to skip ships that don't match filters. This is appropriate but could be consolidated.

### 3.2 Potential Guard Clause Pattern
Lines 196-220 could use an early classification followed by a single filter check:

**Current:** Each status category separately checks filter, appends, and continues.

**Potential simplification:** Classify ship into a status category first, then apply a single filter lookup.

### 3.3 Missing Early Return for Empty Filter State
No early return exists when all filters are `True` (no filtering needed). If all 12+ filter keys are `True`, the function still iterates and performs checks.

---

## 4. Repeated Patterns That Could Be Extracted

### 4.1 Binary Capability Filter Pattern
**Occurrences:** 4 explicit + 5 in loop = 9 total applications

**Pattern structure:**
```python
show_has = filter_state.get('show_X', True)
show_not = filter_state.get('show_not_X', True)
if not show_has or not show_not:
    has_capability = <capability_check>(ship)
    if has_capability and not show_has:
        continue/skip
    if not has_capability and not show_not:
        continue/skip
```

**Extraction candidate:** A helper function like:
```python
def _should_exclude_by_capability(ship, filter_state, has_key, not_key, capability_fn) -> bool
```

### 4.2 Status-Based Inclusion Pattern
**Occurrences:** 4 (destroyed, derelict, damaged, undamaged)

**Pattern structure:**
```python
if <status_check>:
    if not filter_state.get('show_X', True):
        continue
    result.append(ship)
    continue
```

**Extraction candidate:** A lookup table mapping status to filter key:
```python
STATUS_FILTER_MAP = {
    'destroyed': lambda s: not s.is_alive,
    'derelict': lambda s: s.is_derelict,
    'damaged': lambda s: s.is_damaged(),
    'undamaged': lambda s: True  # fallback
}
```

### 4.3 Repeated Import Statements
**Lines:** 159, 185 (FleetCapabilityCalculator imported twice within the same function)

The import occurs inside conditional blocks, meaning it may execute multiple times per ship iteration.

---

## 5. Data Transformations That Could Be Separated

### 5.1 Filter State Normalization
The function reads filter state with defaults scattered throughout:
- `filter_state.get('show_warp_capable', True)` (line 144)
- `filter_state.get('show_not_warp_capable', True)` (line 145)
- etc.

**Separation opportunity:** Pre-process filter state into a normalized structure with all defaults applied once at the start.

### 5.2 Ship Status Classification
Lines 196-220 implicitly classify ships into categories (destroyed, derelict, damaged, undamaged).

**Separation opportunity:** Create a `classify_ship_status(ship) -> str` function that returns the canonical status, then use a single lookup for the filter key.

### 5.3 Capability Computation
The function computes capabilities inline:
- `ShipStatsCalculator.has_warp_capability(ship)` (line 149)
- `FleetCapabilityCalculator.ship_has_spaceyard(ship)` (line 160)
- `FleetCapabilityCalculator.ship_has_ability(ship, ability_name)` (line 186)
- Cargo check: `bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0` (line 170)

**Separation opportunity:** Pre-compute all relevant capabilities for a ship into a dict before filtering, avoiding repeated method calls and simplifying the filter logic to pure boolean operations.

### 5.4 Filter Key Derivation (Lines 179-183)
```python
show_has = filter_state.get(f'show_{col_id}', True)
no_key = col_id.replace('can_', 'no_', 1)
show_not = filter_state.get(f'show_{no_key}', True)
```

This string manipulation derives filter keys from column IDs at runtime for each ship.

**Separation opportunity:** Pre-compute the mapping from column IDs to filter key pairs once, outside the ship loop.

---

## Summary of Complexity Sources

| Source | Lines | Impact |
|--------|-------|--------|
| Binary filter pattern repetition | 144-194 | High (5x similar code blocks) |
| Status cascade | 196-220 | Medium (4 sequential if blocks) |
| Nested conditionals | Throughout | Medium (max depth 4) |
| Loop over special capabilities | 176-194 | Medium (inner loop with flag) |
| Inline capability computation | Throughout | Low (efficiency) |
| Repeated imports | 159, 185 | Low (potential performance) |

**Estimated Cyclomatic Complexity:** ~18-22 (based on branch count)
