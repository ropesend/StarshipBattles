# Code Quality Analysis Report: Inconsistency-Driven Quality Issues

**Codebase:** `game/` (429 Python files, ~106K lines)
**Date:** 2026-03-13
**Analyst:** Code Quality Analyst (automated)

---

## Summary

- **Total issues found:** 14
- **Critical:** 2
- **Major:** 5
- **Minor:** 5
- **Info:** 2

---

## Findings

### CRITICAL: Inconsistent Error Signaling in Command Handlers

**ID:** CQ-001
**Location:** `game/strategy/engine/command_handlers.py:155-222`
**Issue:** The `BaseCommandHandler` class uses three different error-signaling patterns within the same class:
1. `_resolve_fleet()` raises `ValueError` on failure (line 175)
2. `_resolve_planet()` returns `tuple[None, ValidationResult]` on failure (line 195)
3. `_resolve_planet_optional()` raises `ValueError` on failure (line 219)

All 19 command handler `execute()` methods return `ValidationResult`, but the internal resolution helpers use incompatible error mechanisms. This forces each handler to use inconsistent try/except and tuple-unpacking patterns.

**Impact:** High bug risk. A developer implementing a new command handler must know which resolution method uses which error pattern. Getting it wrong causes either unhandled `ValueError` exceptions or silently ignored tuple errors. The mixed patterns also make it impossible to write generic error-handling middleware.

**Recommendation:** Standardize all resolution helpers to return `ValidationResult` (matching the `execute()` contract). Remove `ValueError` raises from internal helpers. The `_resolve_planet` tuple pattern is already close; convert `_resolve_fleet` and `_resolve_planet_optional` to match.

**Effort:** Simple

---

### CRITICAL: Validation Return Type Split - `ValidationResult` vs `tuple[bool, str]`

**ID:** CQ-002
**Location:** Multiple files across `game/strategy/` and `game/ui/`
**Issue:** The codebase has a well-designed `ValidationResult` class in `game/core/validation.py` (with `is_valid`, `errors`, `warnings`, `error_code`, and `merge()`), yet 13+ validation methods return `tuple[bool, str]` instead:
- `game/strategy/data/race_config.py`: 6 private validation methods return `tuple[bool, str]`
- `game/strategy/systems/design_library.py`: 3 methods return `Tuple[bool, str]`
- `game/strategy/systems/race_library.py`: `save_race()` returns `Tuple[bool, str]`
- `game/strategy/systems/save_game_service.py`: 3 methods return various `Tuple[bool, ...]` shapes
- `game/ui/services/ship_io.py`: `save_ship()` returns `Tuple[bool, Optional[str]]`
- `game/ui/screens/new_game_setup_screen.py`: `validate_save_name()` returns `Tuple[bool, str]`

Furthermore, the tuple variants use inconsistent shapes: `Tuple[bool, str]`, `Tuple[bool, Optional[str]]`, and `Tuple[bool, str, Optional[str]]`.

**Impact:** Callers must handle validation results differently depending on which module they call. The tuple pattern loses multi-error accumulation, error codes, and warnings. The `race_config.py` `validate()` method bridges the gap by calling `tuple[bool, str]` helpers and wrapping into `ValidationResult`, adding unnecessary translation code.

**Recommendation:** Migrate all validation/operation-result methods to return `ValidationResult`. For save/delete operations, consider extending `ValidationResult` or using a `OperationResult` dataclass that wraps `ValidationResult` with additional context.

**Effort:** Medium

---

### MAJOR: UI Event Handler Naming Split - `handle_event` vs `process_event`

**ID:** CQ-003
**Location:** `game/ui/` (47+ classes)
**Issue:** The UI layer uses two competing names for the same concept:
- `handle_event()`: 30 implementations across screens, panels, and widgets
- `process_event()`: 17 implementations across windows and dialogs

The return types are also inconsistent:
- Some return `-> bool` (consumed the event)
- Some return `-> None`
- Some have no type annotation at all

The protocol in `game/core/protocols.py:776` defines `handle_event(self, event: Any) -> None`, but many implementations return `bool`.

**Impact:** Developers cannot predict which method name a UI component uses without checking the source. The inconsistent return types mean callers cannot reliably chain event processing (checking if an event was consumed). This increases cognitive load and makes refactoring the event system harder.

**Recommendation:** Standardize on `handle_event() -> bool` across all UI components. Update the protocol definition. Rename all `process_event` methods. This is a large but mechanical change.

**Effort:** Medium

---

### MAJOR: `clamp()` Utility Exists But Is Universally Ignored

**ID:** CQ-004
**Location:** `game/core/math.py:187` (definition), 30+ sites across `game/` (inline `max(min(...))`)
**Issue:** A `clamp(value, min_val, max_val)` function exists in `game/core/math.py` and is exported via `game/core/__init__.py`, but the codebase has 30+ instances of `max(a, min(b, value))` or `min(b, max(a, value))` instead. Only one file imports `clamp`.

Examples of inline clamping:
- `game/ui/renderer/camera.py:131`: `max(self.min_zoom, min(self.max_zoom, self.target_zoom))`
- `game/ui/screens/builder/modifier_row.py:99`: `max(min_v, min(max_v, self.current_value))`
- `game/strategy/formulas/habitability.py:179,214,285`: `max(0.0, min(1.0, factor))`
- `game/research/data/research_tracker.py:139,213`: `max(0, min(rp, remaining))`
- Many more in `game/ui/screens/builder/`, `game/simulation/`, `game/strategy/`

Additionally, `game/strategy/generation/density/primitives/density_primitive.py:36` defines its own `clamp_density()` that duplicates the core function.

**Impact:** Readability suffers because `max(min(...))` requires mental parsing to understand the clamping direction. The argument order is easy to get wrong (and the reversed `min(max(...))` variant appears too). A dedicated `clamp()` call is immediately clear about intent.

**Recommendation:** Replace all `max(a, min(b, x))` / `min(b, max(a, x))` patterns with `clamp(x, a, b)`. Remove the duplicate `clamp_density()`. This is a safe, mechanical refactor.

**Effort:** Simple

---

### MAJOR: `os.path` vs `pathlib.Path` Split

**ID:** CQ-005
**Location:** 48 files use `os.path` (255 call sites), 6 files use `pathlib.Path` (12 call sites)
**Issue:** The codebase overwhelmingly uses `os.path` for file system operations (255 usages across 48 files) while `pathlib.Path` is used in only 6 files (primarily `game/core/paths.py` and `game/core/json_utils.py`). The core utilities accept `Union[str, Path]`, but callers almost always pass strings.

54 files `import os`, often only for `os.path.join`, `os.path.exists`, and `os.path.isdir`.

**Impact:** The mixed approach means path manipulation code is inconsistent. `os.path.join` calls are more verbose and error-prone than `Path` operations. However, since `os.path` is the dominant pattern (96% of usages), this is more of a modernization concern than an active bug source.

**Recommendation:** This is a long-term modernization target. For new code, prefer `pathlib.Path`. Do not pursue a bulk migration unless combining with other refactoring work.

**Effort:** Complex (low priority)

---

### MAJOR: God Classes with 40+ Methods

**ID:** CQ-006
**Location:** Multiple files
**Issue:** Several classes have grown to excessive sizes, indicating they handle too many responsibilities:
- `TestLabScreen` (55 methods) - `game/ui/screens/test_lab/screen.py`
- `FormationEditorScreen` (51 methods) - `game/ui/screens/formation_editor.py`
- `ShipInstance` (47 methods) - `game/strategy/data/ship_instance.py`
- `EmpireBuildQueueWindow` (47 methods) - `game/ui/screens/empire_build_queue_window.py`
- `TestLabViewModel` (43 methods) - `game/ui/screens/test_lab/viewmodel.py`
- `Ship` (42 methods) - `game/simulation/entities/ship.py`
- `StrategyScreen` (41 methods) - `game/ui/screens/strategy_screen.py`

Note: The memory file indicates PROJ-86 through PROJ-89 are planned God Class Decomposition projects targeting these exact classes. This finding validates that plan.

**Impact:** High maintenance cost. Each god class is a merge-conflict hotspot, hard to test in isolation, and difficult for developers to navigate. `ShipInstance` (47 methods, 755 lines) and `Ship` (42 methods, 858 lines) are particularly concerning as they are core domain objects touched by many modules.

**Recommendation:** Proceed with the planned PROJ-86 through PROJ-89 decomposition projects. Prioritize `ShipInstance` and `Ship` as they affect the most downstream code.

**Effort:** Complex (already planned)

---

### MAJOR: Inconsistent `ValueError` Usage Where Custom Exceptions Exist

**ID:** CQ-007
**Location:** 7 files, 12 occurrences
**Issue:** The codebase has a well-designed exception hierarchy (`game/core/exceptions.py`) with `ValidationException`, `StateException`, `ComponentException`, etc. Yet 12 call sites still raise bare `ValueError`:
- `game/strategy/engine/command_handlers.py:175,178,219` - Fleet/planet not found (should be `ValidationException`)
- `game/simulation/components/component.py:566,672` - Missing registry provider (should be `StateException`)
- `game/strategy/data/fleet_capability_calculator.py:72,135` - Invalid fleet state (should be `ValidationException`)
- `game/strategy/data/ship_instance.py:284` - Invalid data (should be `ValidationException`)
- `game/simulation/entities/ship_loader.py:136` - Missing registry (should be `StateException`)

**Impact:** Catching code uses `except (ValueError, ...)` with long exception tuples (e.g., `battle_controller.py:173` catches 5 exception types). If these were proper custom exceptions, catch clauses could be more targeted. The bare `ValueError` also loses the `code` and `context` attributes that custom exceptions provide.

**Recommendation:** Replace `raise ValueError(...)` with appropriate custom exceptions from the hierarchy. This will enable more precise error handling at catch sites.

**Effort:** Simple

---

### MINOR: Layer Iteration DRY Violation

**ID:** CQ-008
**Location:** 3 files bypass `layer_iterator`, ~40 files iterate Ship.layers directly
**Issue:** `game/core/patterns/layer_iterator.py` provides centralized utilities (`iter_components`, `iter_layers_and_components`) for iterating design_data layer structures, handling both list and dict formats. However:
1. Three files still manually iterate design_data layers with inline format checks: `build_queue_source.py:93-95`, `resupply_engine.py:151-153`, `planet_report_panel.py:486-488`
2. The layer_iterator only works on `design_data` dicts (raw JSON), not on `Ship.layers` (which uses `LayerData` objects). About 40 call sites iterate `ship.layers` with their own patterns.

**Impact:** The 3 bypass sites duplicate the format-handling logic and could diverge if the format changes. The lack of a Ship-level iteration utility means ~40 sites have slightly different iteration patterns.

**Recommendation:** Fix the 3 bypass sites to use `layer_iterator`. Consider adding a `Ship.iter_components()` convenience method (which already exists at line 678 but is underutilized).

**Effort:** Simple

---

### MINOR: `from __future__ import annotations` Applied Inconsistently

**ID:** CQ-009
**Location:** 51 of 429 files (12%) use `from __future__ import annotations`
**Issue:** Only 51 files use `from __future__ import annotations` for PEP 563 deferred evaluation. This creates two annotation regimes: files where annotations are strings (deferred) and files where they are evaluated at import time. Mixed with the 299 files importing from `typing`, the project has an inconsistent type annotation approach.

**Impact:** Low immediate impact since Python 3.10+ handles most cases. However, it can cause subtle issues with runtime annotation introspection (e.g., `get_type_hints()`) and makes the codebase inconsistent about whether forward references need quotes.

**Recommendation:** Low priority. Either adopt `from __future__ import annotations` everywhere or remove it from the 51 files. The former is the forward-looking choice.

**Effort:** Simple (mechanical, but touches 378+ files)

---

### MINOR: Functions Exceeding 80 Lines

**ID:** CQ-010
**Location:** 20+ functions exceed 80 lines
**Issue:** Several functions are excessively long:
- `create_strategy_panels()`: 284 lines (`strategy_panel_manager.py:91`)
- `build_sidebar()`: 242 lines (`planet_list_sidebar.py:13`)
- `SystemTreePanel.set_items()`: 211 lines (`system_tree_panel.py:135`)
- `Ship.__init__()`: 169 lines (`ship.py:31`)
- `ShipStatsCalculator.calculate_stats()`: 156 lines (`ship_stats_calculator.py:87`)
- `ResearchService.process_turn()`: 153 lines (`research_service.py:32`)

**Impact:** Long functions are harder to test, review, and maintain. The 284-line `create_strategy_panels()` and 242-line `build_sidebar()` are UI builder functions that could be decomposed into smaller helper methods.

**Recommendation:** Extract logical subsections into named helper methods. For UI builder functions, consider a builder pattern or configuration-driven approach.

**Effort:** Medium

---

### MINOR: Print Statements in Docstring Examples (Not Actual Debug Prints)

**ID:** CQ-011
**Location:** `game/core/protocols.py`, `game/simulation/interfaces/`, `game/core/input_actions.py`
**Issue:** Several `print()` calls exist in the codebase. Upon inspection, most are in docstring `Usage` examples (protocols, interfaces), not actual debug output. Only 15 total `print()` calls exist, and they are benign.

**Impact:** Minimal. The docstring examples using `print()` are standard Python documentation style. The codebase correctly uses the `logging` module (141 logger instances across the codebase) for actual output.

**Recommendation:** No action needed. Logging is well-standardized.

**Effort:** N/A

---

### MINOR: Ability Constructor Data Parsing Pattern Repeated Across 10+ Classes

**ID:** CQ-012
**Location:** `game/simulation/components/abilities/` (all ability files)
**Issue:** Every ability class in the abilities package repeats the same data-parsing boilerplate:
```python
if isinstance(data, (int, float)):
    self.value = data
elif isinstance(data, dict):
    self.value = data.get('value', default)
```

This pattern appears 23+ times across `weapons.py`, `resources.py`, `cargo.py`, `harvester.py`, `defense.py`, `propulsion.py`, `colonize.py`, and `base.py`. While `base.py:126` has a `_parse_primary_value()` helper, it is only used in a few subclasses.

**Impact:** Adding a new data format (e.g., supporting lists or nested configs) would require updating 23+ sites. The `_parse_primary_value()` helper in `Ability` base class exists but is underutilized.

**Recommendation:** Migrate all ability constructors to use `_parse_primary_value()` from the base class, or create a `parse_ability_data()` utility function.

**Effort:** Simple

---

### INFO: Tuple Type Hint Style Inconsistency

**ID:** CQ-013
**Location:** Throughout `game/`
**Issue:** The codebase mixes `Tuple[bool, str]` (from `typing` module) with `tuple[bool, str]` (Python 3.9+ built-in syntax). For example:
- `game/strategy/data/race_config.py` uses `tuple[bool, str]` (lowercase)
- `game/strategy/systems/design_library.py` uses `Tuple[bool, str]` (typing module)
- Both styles appear in the same packages

**Impact:** Purely cosmetic. Both forms work identically. However, the inconsistency adds minor cognitive friction.

**Recommendation:** Standardize on `tuple[bool, str]` (built-in) for new code. Low-priority to migrate existing code.

**Effort:** Simple (low priority)

---

### INFO: Serialization Uses `to_dict`/`from_dict` Consistently

**ID:** CQ-014
**Location:** 30+ classes across `game/`
**Issue:** This is a positive finding. The codebase consistently uses the `to_dict()`/`from_dict()` pattern for serialization across all domain objects. Only `BattleState` and `BattleResults` add `to_json()`/`from_json()` convenience methods (which delegate to `to_dict()`/`from_dict()`). The `ShipInstance` follows this same pattern.

**Impact:** None - this is well-standardized.

**Recommendation:** No action needed.

**Effort:** N/A

---

## Top 5 Priority Issues

1. **CQ-001 (CRITICAL):** Inconsistent error signaling in `BaseCommandHandler` - Three different error patterns in one class. Quick fix with high impact on developer experience and correctness.

2. **CQ-002 (CRITICAL):** Validation return type split (`ValidationResult` vs `tuple[bool, str]`) - The canonical `ValidationResult` class exists but is bypassed by ~13 methods. Consolidation improves the entire validation surface area.

3. **CQ-003 (MAJOR):** UI event handler naming split (`handle_event` vs `process_event`) - 47 classes with inconsistent method names and return types. Standardizing enables reliable event propagation and reduces cognitive load.

4. **CQ-007 (MAJOR):** Bare `ValueError` where custom exceptions exist - 12 sites use `ValueError` despite a comprehensive exception hierarchy. Quick mechanical fix that enables better error handling.

5. **CQ-004 (MAJOR):** `clamp()` utility ignored in 30+ sites - A canonical utility exists but is universally bypassed. Simple search-and-replace with immediate readability improvement.

---

## Observations

**Well-Standardized Areas:**
- JSON file I/O is properly centralized in `game/core/json_utils.py` (no raw `json.load()` outside the utility)
- Serialization pattern (`to_dict`/`from_dict`) is consistent across 30+ classes
- Logging uses the standard `logging` module consistently (141 loggers, no stray `print()` for debug)
- Custom exception hierarchy is well-designed and widely adopted (30+ import sites)
- No `== None` or `!= None` usage (proper `is None` throughout)
- Type hints are present in 96% of files (356/371 non-init files)

**Root Cause Pattern:**
Most inconsistencies stem from incremental growth without enforcement. The codebase has good utilities (`clamp`, `ValidationResult`, `layer_iterator`, custom exceptions) but no mechanism to enforce their usage. New code often takes the quick inline approach rather than discovering and using existing utilities.
