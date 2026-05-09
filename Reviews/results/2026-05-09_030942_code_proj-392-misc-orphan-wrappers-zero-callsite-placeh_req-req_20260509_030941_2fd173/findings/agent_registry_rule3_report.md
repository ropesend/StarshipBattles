# LEG-03-016 Dispatch-Registry-Key Retention & Rule 3 Compliance Report

**Date:** 2026-05-09
**Scope:** PROJ-392 misc orphan wrappers / zero-callsite placeholders
**Focus:** LEG-03-016 dispatch-key retention verification + Rule 3 compliance sweep

---

## Task 1: Dispatch-Registry-Key Retention (LEG-03-016)

### 1.1 No `def get_crew_required` function definition exists

**Status: PASS**

`grep` for `def get_crew_required` across all `*.py` files returned **zero results**.

Evidence: The legacy wrapper `def get_crew_required(ship) -> Any` (previously in `stat_getters.py`) has been fully deleted. No function definition remains anywhere in the production or test codebase.

No `.py` file contains a reference to `get_crew_required` as a callable (all `.py` references found were either the string key `'get_crew_required'` in the GETTERS dict or historical audit report data under `Reviews/results/`).

---

### 1.2 The `_get_total_crew_requirement` rename is complete

**Status: PASS**

`grep` for `_get_total_crew_requirement` across all `*.py` files returned **zero results**.

The private helper has been fully renamed to `get_total_crew_requirement`. No stale references to the old private name remain anywhere in the production or test code.

---

### 1.3 The dispatch registry properly maps the legacy key

**Status: PASS**

File: `game/ui/screens/builder/stat_getters.py:396`

```python
GETTERS = {
    'get_mass_display': get_mass_display,
    'get_crew_required': get_total_crew_requirement,   # <-- line 396
    'get_crew_capacity': get_crew_capacity,
    ...
}
```

The GETTERS dict maps the string key `'get_crew_required'` to the renamed function `get_total_crew_requirement`. This is a configuration-level key-value mapping, not a code shim. The old function name is used purely as a **string lookup key** in a Registry pattern, not as a function name.

---

### 1.4 JSON data files reference the key by name

**Status: PASS**

| File | Line | Content |
|------|------|---------|
| `data/stats_sections.json` | 274 | `"getter": "get_crew_required"` |
| `data/stats_layout.json` | 284 | `"getter": "get_crew_required"` |

Both JSON configuration files reference the key `"get_crew_required"` as a string value for the `"getter"` property. These are **data configuration files**, not code files. The string value is a configuration identifier that the dispatch system resolves via the GETTERS registry.

---

### 1.5 Dispatch mechanism confirms Registry pattern

**Status: PASS**

File: `game/ui/screens/builder/stats_config.py:64`

```python
raw_getter = GETTERS.get(item_data.get('getter')) if item_data.get('getter') else None
```

The dispatch flow:
1. JSON config provides `"getter": "get_crew_required"` (a string identifier)
2. `stats_config.py:64` reads this string from the JSON item data
3. Looks it up in the `GETTERS` dict (the Registry)
4. Resolves to `get_total_crew_requirement` function
5. Stores in `StatDefinition.getter` for later invocation

This is the **standard Registry pattern** (Pattern 4, documented in `docs/02_PATTERNS.md`). The key `'get_crew_required'` functions as a configuration value / enum-like identifier, not as a code shim.

---

### 1.6 Rule 3 compliance assessment for LEG-03-016

**Status: PASS — NOT a Rule 3 violation**

**Analysis:**

- A **code shim** is a function/method added solely to maintain backward compatibility — named identically to the old function, wraps the new function, exists only to avoid updating call sites.
- A **configuration key** in a dispatch registry is a string identifier in a lookup table, like an enum value. The key `'get_crew_required'` is used by JSON data files to select which function from the GETTERS dict to dispatch to. The string `"get_crew_required"` is a **data reference**, not a code construct.
- Deleting the key from the GETTERS dict and renaming it in JSON would be a **data schema change** across two JSON files, not a code cleanup. The key name is stable configuration.
- This is analogous to renaming a column in a database: the application code function was renamed (`get_crew_required` → `get_total_crew_requirement`), but the configuration identifier in the data layer stays stable to avoid unnecessary data migration.

**Conclusion: This is legitimate configuration, NOT a Rule 3 violation.**

---

## Task 2: Broader Rule 3 Compliance Check

### 2.1 `find_path_deep_space` in `game/strategy/data/pathfinding.py`

**Status: PASS — Legitimate utility function, not a shim**

File: `game/strategy/data/pathfinding.py:40-42`

```python
def find_path_deep_space(start: HexCoord, end: HexCoord) -> List[HexCoord]:
    from game.core.hex_math import hex_linedraw
    return hex_linedraw(start, end)
```

**Note:** The module docstring (lines 1-17) describes the entire file as "Pathfinding free-function shims" from PROJ-372 Phase 4. However, `find_path_deep_space` differs from the other functions in the file:

| Function | Type | Delegates to |
|----------|------|-------------|
| `strip_start_hex` | **True shim** | `GalaxyPathfindingService.strip_start_hex` |
| `find_path_deep_space` | **Real implementation** | `hex_linedraw` (core hex math) |
| `find_path_interstellar` | **True shim** | `_pathfinder_for(galaxy).find_path_interstellar` |
| `get_system_at_hex` | **True shim** | `_pathfinder_for(galaxy).get_system_at_hex` |
| `find_nearest_system` | **True shim** | `_pathfinder_for(galaxy).find_nearest_system` |
| `find_hybrid_path` | **True shim** | `_pathfinder_for(galaxy).find_hybrid_path` |
| `calculate_intercept_point` | **True shim** | `_intercept_for(galaxy).calculate_intercept_point` |

`find_path_deep_space` is the only function in the module that does **real algorithmic work** — it calls `hex_linedraw` directly, not a service forwarding. It has a dedicated test suite (`tests/unit/strategy/pathfinding/test_basic_paths.py`, `test_edge_cases.py`) and multiple integration test callers. The static wrapper previously in `galaxy_pathfinding_service.py` was deleted in PROJ-392, leaving this as the sole implementation.

**Conclusion: Legitimate single-responsibility utility function, not a compatibility shim.** (The module as a whole does contain other shims, but those are outside PROJ-392 scope — they're tracked as PROJ-376.)

---

### 2.2 Remaining `get_asset_manager` references

**Status: PASS**

`grep` for `get_asset_manager` across all `*.py` files returned **zero results**. The wrapper has been fully removed.

---

### 2.3 Remaining `_get_sector_text` instance method

**Status: PASS**

`grep` for `_get_sector_text` across all `*.py` files returned **zero results**. The instance method has been fully removed.

---

### 2.4 `_load_*_image` wrapper definitions

**Status: PASS**

`grep` for `def _load_.*_image` found only two matches, both in `game/ui/assets/ship_theme_manager.py:297,392`:

- `_load_single_image(self, theme_name, ship_class)` — private method that reads a ship sprite from disk, applies alpha conversion, bounding-rect processing, and caching. **Real implementation, not a wrapper.**
- `_load_portrait_image(self, theme_name, ship_class)` — private method that loads ship portrait images. **Real implementation, not a wrapper.**

No standalone `_load_*_image` wrapper functions (compatibility pass-throughs) exist anywhere in the codebase.

---

### 2.5 `get_quickstart_*_dir` wrapper definitions in production code

**Status: PASS**

`grep` for `get_quickstart_.*_dir` found matches **only in test files** (`tests/unit/quickstart/`). No production `.py` file contains these definitions. Any production-level quickstart directory wrappers have been fully removed.

---

### 2.6 `priority_sort_key` function definition

**Status: PASS**

`grep` for `def priority_sort_key` across all `*.py` files returned **zero results**. The function has been fully removed.

---

### 2.7 `@deprecated` / `# DEPRECATED` shim markers

**Status: PASS**

`grep` for `@deprecated|# DEPRECATED` across all `*.py` files returned **zero matches** in production or test code. The only match was in `Tools/legacy_audit/legacy_audit.py:206`, which is the audit tool's own regex pattern for detecting deprecation markers — not a codebase deprecation.

---

## Task 3: `get_crew_required` JSON Config Verification

### 3.1 `data/stats_sections.json`

**Status: PASS**

File: `data/stats_sections.json:270-275`
```json
"items": [
    {
        "id": "crew_required",
        "label": "Crew Req",
        "getter": "get_crew_required"
    },
    ...
```

The `"getter"` property uses the string `"get_crew_required"` as a configuration value. This is resolved through the GETTERS registry.

### 3.2 `data/stats_layout.json`

**Status: PASS**

File: `data/stats_layout.json:280-285`
```json
"items": [
    {
        "id": "crew_required",
        "label": "Crew Req",
        "getter": "get_crew_required"
    },
    ...
```

Identical pattern — `"getter": "get_crew_required"` as a configuration value.

### 3.3 Dispatch resolution

**Status: PASS**

The dispatch chain is:
- JSON: `"getter": "get_crew_required"` → `stats_config.py:64` reads string → looks up in `GETTERS` dict → resolves to `get_total_crew_requirement` → stored in `StatDefinition.getter` → invoked at render time

This is the standard Registry pattern (Pattern 4). The string `"get_crew_required"` is a **configuration identifier**, not a code function name. It is no more a "shim" than a database column name or an enum value.

---

## Final Assessment: Rule 3 Compliance

### Overall: PASS

**There is no replacement shim anywhere in the PROJ-392 changes.**

| Check | Finding |
|-------|---------|
| `def get_crew_required` function | Deleted — zero occurrences |
| `_get_total_crew_requirement` references | Renamed — zero occurrences |
| `'get_crew_required'` in GETTERS dict | **Configuration key, not a shim** |
| `"getter": "get_crew_required"` in JSON | **Data reference, not a shim** |
| `get_asset_manager` | Fully removed — zero occurrences |
| `_get_sector_text` | Fully removed — zero occurrences |
| `_load_*_image` wrappers | Not present — only real implementation methods remain |
| `get_quickstart_*_dir` in production | Zero occurrences (test-only) |
| `priority_sort_key` | Fully removed — zero occurrences |
| `@deprecated` markers | Zero occurrences in production/test code |
| `find_path_deep_space` | Legitimate utility function, not a compat shim |

### Key distinction applied

The report distinguishes between:
1. **Code shim** (Rule 3 violation): a function/method added solely for backward compatibility, named like the old function, wrapping the new function.
2. **Configuration key** (not a violation): a string identifier in a data-driven dispatch registry that maps to a renamed implementation function. The key provides a stable contract between JSON data files and the function registry.
3. **Utility function** (not a violation): a single-responsibility function that performs real algorithmic work, even if thin.

The PROJ-392 changes maintain zero Rule 3 violations across all categories.
