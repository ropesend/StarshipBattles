# Code Quality Report — PROJ-360 ShipStatsCalculator Domain Decomposition

**Review:** Code Quality
**Date:** 2026-05-05
**Files reviewed:** 8

---

## Summary

| Severity | Count |
|----------|-------|
| CRIT     | 0     |
| MAJ      | 1     |
| MIN      | 4     |
| NIT      | 2     |
| **Total**| **7** |

---

## Detailed Findings

### FM-01: [MAJ] `aggregate_targeting_scores` return type annotation is wrong

**File:** `game/simulation/entities/stat_contributors/weapons.py:36`
**Description:** The function signature declares `-> None` but actually returns `ecm_score` (a `float` or `int`). The caller at `ship_stats.py:432` explicitly consumes this return value: `ecm_score = _wep.aggregate_targeting_scores(ship, component_pool)`. The function docstring (line 44) correctly states "Returns the ECM score", contradicting the type annotation. A mypy strict-mode run would flag this as `error: "None" not assignable to variable of type "float"`.
**Remediation:** Change return type to `-> float` and update the body to guarantee a float return: e.g. `return float(ecm_score)` at the end.

---

### FM-02: [MIN] Unused imports `Dict` and `Optional` in `registry.py`

**File:** `game/simulation/entities/stat_contributors/registry.py:34`
**Description:** `Dict` and `Optional` are imported from `typing` but never referenced anywhere in the module. Confirmed via AST analysis — only `Callable`, `List`, and `TYPE_CHECKING` are consumed.
**Remediation:** Remove `Dict` and `Optional` from the import line:
```python
from typing import Callable, List, TYPE_CHECKING
```

---

### FM-03: [MIN] Redundant `max_mass_budget` computation across two phases

**File:** `game/simulation/entities/stat_contributors/command.py:76-78` and `game/simulation/entities/ship_stats.py:389-392`
**Description:** `ship.max_mass_budget` is set in Phase 2 (`command.allocate_crew_and_life_support`) and then recomputed identically in Phase 4 (`ShipStatsCalculator._check_mass_limits`). Both read `vehicle_classes[ship.ship_class].get("max_mass", DEFAULT_MAX_MASS)`. This is a side-by-side artifact of the extraction — the legacy calculator computed it once, but the extracted functions now duplicate the lookup.
**Remediation:** Compute once (e.g., in Phase 2) and have `_check_mass_limits` read `ship.max_mass_budget` without overwriting it, or centralize to a single site.

---

### FM-04: [MIN] Module-level mutable list state with `global` keyword for cleanup

**File:** `game/simulation/entities/stat_contributors/registry.py:95,173`
**Description:** `unregister_crew_priority` and `unregister_stat_contributor` use the `global` keyword to reassign the module-level `CREW_PRIORITY_REGISTRY` and `STAT_CONTRIBUTOR_REGISTRY` lists. While this is intentional (tests use these to clean registries between cases — see `test_stat_contributor_extension.py:57-60`), it constitutes module-level mutable state that diverges from Pattern #18 (no global mutable singletons). The test fixture explicitly documents this tradeoff. No race issues arise because the registries are write-once in production and only test teardown mutates.
**Remediation:** Consider a `RegistrySnapshot` context manager pattern that replaces the global assignment with a context-bound view, or document the tradeoff as intentional in a comment referencing the test fixture.

---

### FM-05: [MIN] `_get_or_resolve_planetary_ids` returns bare `list` type

**File:** `game/simulation/entities/ship_stats.py:94`
**Description:** The private method's return type is `list` rather than `list[str]`. While the method is private (`_` prefix), the other private helper `_get_planetary_resource_ids` (line 67) properly uses `List[str]`. This inconsistency weakens type-checking within the class — callers get a `list` with unknown element type.
**Remediation:** Change to `list[str]`:
```python
def _get_or_resolve_planetary_ids(self) -> list[str]:
```

---

### FM-06: [NIT] `__init__.py` uses absolute self-import instead of relative imports

**File:** `game/simulation/entities/stat_contributors/__init__.py:17`
**Description:** The package's `__init__.py` does `from game.simulation.entities.stat_contributors import (command, defense, launch, movement, registry, weapons)` — importing from its own package path. Python handles this correctly (submodule lookups resolve before the package `__init__` completes), but it is unconventional and could confuse static analysis tools. The idiomatic form is relative imports.
**Remediation:** Replace with:
```python
from . import command, defense, launch, movement, registry, weapons
```

---

### FM-07: [NIT] `_check_mass_limits` missing docstring

**File:** `game/simulation/entities/ship_stats.py:385`
**Description:** Every other private method in `ShipStatsCalculator` carries a docstring (`_reset_base_state`, `_phase_damage_check_and_supply`, `_phase_stats_aggregation`, etc.), but `_check_mass_limits` has none. While private methods aren't strictly required to have docstrings, the inconsistency stands out given the thorough documentation elsewhere.
**Remediation:** Add a one-line docstring, e.g.:
```python
def _check_mass_limits(self, ship: "Ship") -> None:
    """Compute per-layer mass ratios and flag if any exceed their budget."""
```

---

## Check Results Summary

| # | Check | Result |
|---|-------|--------|
| 1 | **LOC Verification** | PASS — `ship_stats.py` is **495 lines** (confirmed via `wc -l`). Under the 500 LOC ceiling. The claim of reduction from 643 to 495 LOC cannot be verified against the pre-refactor file (the old 643-line version is not in this review scope), but the current line count is within limits. |
| 2 | **Type Annotations** | FAIL — `aggregate_targeting_scores` in `weapons.py` has `-> None` but returns a value. One private method returns bare `list` instead of `list[str]`. All other public functions/methods have correct return-type annotations. |
| 3 | **Naming Conventions** | PASS — All modules are `snake_case`. All classes are `PascalCase`. All functions are `snake_case`. No naming collisions found. |
| 4 | **Import Order** | PASS — All files follow the 3-group convention: `from __future__` / stdlib / blank line / third-party / blank line / `game.*`. No third-party imports exist in any reviewed file. |
| 5 | **Docstring Quality** | PASS — Module-level docstrings present in all 8 files. All public functions have docstrings. One nit on a private method lacking a docstring where peers have them. |
| 6 | **Function/Method Size** | PASS — No function exceeds 50 lines. Maximum nesting depth is 3 (in `allocate_crew_and_life_support`). |
| 7 | **Mutable Defaults** | PASS (with note) — No mutable default arguments in any function signature. Module-level mutable state exists in `registry.py` by design (append-only registries) with `global` used in `unregister_*` for test cleanup. No `random.seed()` bypass. |
| 8 | **Public API Stability** | PASS — `ShipStatsCalculator.calculate(ship)` signature is `(self, ship: "Ship") -> None`, unchanged. `calculate_ability_totals` and `_priority_sort_key` legacy passthroughs preserved. The external-stats bridge at `ship_stats.py:338-347` reads `ship.external_stats` directly, consistent with the `ability_stat_registry` modifier pipeline. All callers reference the same class. |
| 9 | **Error Handling** | PASS — No `bare except` blocks. No `except Exception` without the required `# Intentional broad catch` comment. Structured `raise TypeError(...)` and `raise ValueError(...)` used where appropriate. |
| 10 | **Dead Code / Unused Imports** | FAIL — `Dict` and `Optional` imported but unused in `registry.py`. All other imports are consumed. `__init__.py` exports (6 submodules) match actual import usage in `ship_stats.py`. |

---

## Overall Assessment

The domain decomposition is well-executed. The 8 files are clean, well-documented, and conform to most conventions. The sole MAJ issue is the incorrect return type on `aggregate_targeting_scores` — a one-line fix. The 4 MIN issues (unused imports, redundant computation, global state, bare list annotation) are low-risk and straightforward to remediate. The 2 NITs are cosmetic.
