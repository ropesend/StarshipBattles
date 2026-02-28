# Dead/Unused Code - Skeptical Verification Report

**Reviewer:** Skeptical Verification Agent
**Date:** 2026-02-27
**Scope:** 4 findings (AIR-003, AIR-007, LEG-001, STR-003)

---

## Finding AIR-003: Orphaned TypeGuard Protocol Functions

**Original Claim:** `game/ai/protocols.py:169-187` has 4 unused TypeGuard functions (`is_grid_entity`, `is_projectile`, `is_formation_master`, `is_component_health`).

**Verification Result:** PARTIALLY CONFIRMED

**Evidence:**

The original claim says all 4 functions are unused. This is **wrong for 2 of them**:

| Function | Production Usage | Test Usage | Verdict |
|---|---|---|---|
| `is_grid_entity` | NOT used in any production code. Only re-exported in `game/ai/interfaces/__init__.py` and tested in `tests/unit/ai/test_ai_protocols.py`. The controller imports `IGridEntity` (the Protocol class) directly, not the guard function. | Tests only | **Unused in production** |
| `is_projectile` | **ACTIVELY USED** in `game/ai/controller.py:127` and `game/ai/target_evaluator.py:202`. Also used in `game/simulation/combat/targeting_system.py:166` (though that one imports from `game.simulation.interfaces`, a separate definition). | Tests + production | **Used - NOT dead code** |
| `is_formation_master` | NOT used in any production code. `game/ai/behaviors.py` imports `IFormationMaster` (the Protocol class) for type annotation but never calls the guard function. Only re-exported and tested. | Tests only | **Unused in production** |
| `is_component_health` | NOT used in any production code. `IComponentHealth` protocol class is also not imported anywhere in production code outside `protocols.py` and the `__init__.py` re-export. Only tested. | Tests only | **Unused in production** |

**Important nuance:** The `is_projectile` function is very much alive and actively used. The original claim incorrectly lumped it in with the others. The original report text says "Five TypeGuard functions" are unused but lists only 4 names; `is_projectile` is clearly used.

Additionally, while `is_grid_entity`, `is_formation_master`, and `is_component_health` guard functions are not called in production, the corresponding **Protocol classes** `IGridEntity` and `IFormationMaster` ARE used in production code (`controller.py` and `behaviors.py` respectively). Only `IComponentHealth` is entirely unused outside of tests.

**Risk of Fix:**
- Removing `is_projectile` would **break production code** -- do NOT remove it.
- Removing `is_grid_entity`, `is_formation_master`, `is_component_health` functions: low risk. Would require updating `game/ai/interfaces/__init__.py` (remove from re-exports) and deleting tests. No runtime breakage.
- The Protocol classes themselves (`IGridEntity`, `IFormationMaster`) must be **kept** because they are used for type annotations in production.

**Recommendation:** MODIFY APPROACH

**Reasoning:** The claim is overly broad. Only 3 of the 4 TypeGuard *functions* are unused in production (`is_grid_entity`, `is_formation_master`, `is_component_health`). `is_projectile` is actively used and must not be touched. However, these 3 unused guard functions are small, well-tested, and follow a consistent pattern alongside `is_projectile`. They represent a minor public API surface for future consumers. Removing them saves ~15 lines and 3 test classes but provides little material benefit. This is a **low-priority cleanup** at best. The Protocol classes they wrap must stay regardless.

---

## Finding AIR-007: Unused is_vector2_like()

**Original Claim:** `game/ai/combat_utils.py:38-51` -- function `is_vector2_like()` is exported but never used.

**Verification Result:** DISPUTED

**Evidence:**

`is_vector2_like()` is **used internally** within the same module at line 88:

```python
# game/ai/combat_utils.py:86-89
def get_position(entity: Any) -> Optional[Vector2]:
    ...
    if isinstance(entity, IControllable):
        result = entity.get_position()
        if is_vector2_like(result):   # <-- USED HERE (line 88)
            return result
```

`get_position()` is one of the most important functions in the module, used by `safe_distance()`, `is_in_pdc_arc()`, and transitively by the AI controller and target evaluator.

The function is also:
- In `__all__` (line 27)
- Tested in `tests/unit/ai/test_combat_utils.py`

It is true that no **external** module imports `is_vector2_like` directly. The function's only caller is `get_position()` within the same file. But it is absolutely called at runtime during combat whenever an `IControllable` entity's position is retrieved.

**Risk of Fix:** Removing `is_vector2_like()` would **break `get_position()`**, which would cascade to break `safe_distance()`, `is_in_pdc_arc()`, and all AI targeting/distance calculations. This would be a **runtime-breaking change**.

**Recommendation:** KEEP

**Reasoning:** The original claim is factually incorrect. The function IS used -- it is called on line 88 of the same file. The fact that it is also exported in `__all__` is reasonable (it could be useful for external callers doing similar Vector2 validation). The claim appears to have been generated by searching only for cross-file imports without checking intra-file usage.

---

## Finding LEG-001: SimulationException Base Class Never Raised

**Original Claim:** `game/core/exceptions.py:183-189` -- `SimulationException` is defined but never directly raised; only subclasses are used.

**Verification Result:** CONFIRMED (the facts), but DISPUTED (the recommendation to remove)

**Evidence:**

Confirmed facts:
- 0 instances of `raise SimulationException` anywhere in the codebase
- 0 instances of `except SimulationException` anywhere in production code
- `SimulationException` is the parent class of `ComponentException` and `FormulaException`
- It IS exported in `__all__` and re-exported from `game/core/__init__.py`
- Tests verify the class hierarchy (`test_exceptions.py:175, 179, 184, 209, 212`)

However, the recommendation to remove it is **architecturally unsound** for several reasons:

1. **Base exception classes exist for hierarchy, not for direct use.** This is standard Python practice. `IOError`, `OSError`, `LookupError`, `ArithmeticError` in the stdlib are all base classes that are caught but rarely raised directly. Their purpose is to enable catch-all handling.

2. **Removing it breaks the hierarchy.** `ComponentException` and `FormulaException` inherit from `SimulationException`. If removed, they would need to inherit from `GameException` directly, losing the semantic grouping of "simulation-related errors." This makes it impossible to write `except SimulationException` as a catch-all for any simulation error in the future.

3. **The exception hierarchy documentation explicitly shows this as a base class** (lines 50-59 of the file itself, and in `docs/architecture/ERROR_HANDLING_GUIDELINES.md`). It was a deliberate design choice from PROJ-45.

4. **Future-proofing is legitimate here.** The comment "0 raises" is expected for base exception classes. The same logic would argue for removing `ResourceException` (which is also a base class for `MissingResourceException`) or `StateException` (base for `FrozenStateException`).

5. **Test code verifies this exact pattern.** `test_exceptions.py:208-212` explicitly tests that catching `SimulationException` catches both `ComponentException` and `FormulaException`. This test documents the intended usage pattern.

**Risk of Fix:** Removing would require:
- Changing `ComponentException` and `FormulaException` to inherit from `GameException`
- Updating all tests that verify the hierarchy
- Updating all documentation (exception hierarchy docs, ERROR_HANDLING_GUIDELINES.md, SVG/dot diagrams)
- Losing the ability to ever catch "any simulation error" with a single except clause

**Recommendation:** KEEP

**Reasoning:** Base exception classes in a well-designed hierarchy are not "dead code" even if never raised directly. They serve a structural and semantic purpose. The `StateException -> FrozenStateException` and `ResourceException -> MissingResourceException` pairs follow the exact same pattern. Singling out `SimulationException` for removal while keeping those would be inconsistent. This is a false positive from the dead code scan.

---

## Finding STR-003: Placeholder Economy Fields

**Original Claim:** `game/strategy/engine/empire_economy_calculator.py:101-116` has placeholder production/expense categories (trade, tribute, mining) initialized to zero, never modified.

**Verification Result:** CONFIRMED (the facts are accurate)

**Evidence:**

The following fields on `EmpireEconomySnapshot` are always set to all-zero dicts:
- `ship_production` (line 103)
- `trade_production` (line 104)
- `tribute_production` (line 105)
- `mining_production` (line 106)
- `tribute_expenses` (line 115)
- `construction_expenses` (line 116)

These are:
1. Defined as dataclass fields (lines 37-46)
2. Always initialized to `{r: 0.0 for r in PLANET_RESOURCES}` in `calculate()` (lines 102-116)
3. **Actively displayed in the UI** via `empire_treasury_panel.py:249-267`:
   - "From Ships" row
   - "From Trade" row
   - "From Tribute" row
   - "From Remote Mining" row
   - "Tributes" expense row
   - "Construction Queues" expense row
4. Tested in multiple test files

**Critical finding the original report may have underweighted:** These fields are **actively rendered in the UI panel**. The `_get_production_rows()` and `_get_expense_rows()` methods in `empire_treasury_panel.py` directly reference all of these fields. Removing them would break the UI panel.

The code explicitly marks them as "Placeholder production sources (future implementation)" (line 101) and "Placeholder expense categories (future implementation)" (line 114). This is intentional scaffolding for future game features.

**Risk of Fix:**
- Removing fields from `EmpireEconomySnapshot`: would break `empire_treasury_panel.py` (runtime `AttributeError`)
- Removing the zero-initialization in `calculate()`: fields would remain empty dicts, which would still display but with no resource keys (visual difference in UI)
- Removing the UI rows: would change the player-visible economy panel layout
- No serialization risk found (snapshot is not persisted to disk)

**Recommendation:** KEEP

**Reasoning:** These are not dead code in the traditional sense. They are:
1. Part of a deliberate data model design with documented future intent
2. Actively read by the UI rendering layer (removing them causes runtime errors)
3. Visible to players as rows in the economy panel (even if currently showing zeros, this communicates to players that these economic systems exist/will exist)
4. Well-documented with "future implementation" comments

The appropriate action would be to implement these features, not remove them. If the game design has changed and these features are permanently canceled, then removing them requires coordinated changes across the dataclass, calculator, UI panel, and tests -- it is not a simple deletion. In either case, this is a product/design decision, not a code quality issue.

---

## Summary Table

| Finding | Original Claim | Verification | Recommendation | Priority |
|---|---|---|---|---|
| AIR-003 | 4 TypeGuard functions unused | **PARTIAL** -- only 3 of 4 are unused in production; `is_projectile` is actively used | MODIFY APPROACH (only clean up 3, keep `is_projectile`) | Low |
| AIR-007 | `is_vector2_like()` unused | **DISPUTED** -- used internally on line 88 of same file | KEEP -- removing breaks runtime | N/A (false positive) |
| LEG-001 | `SimulationException` never raised | **DISPUTED** -- base class serving hierarchy purpose | KEEP -- standard exception hierarchy pattern | N/A (false positive) |
| STR-003 | Placeholder economy fields never modified | **CONFIRMED** facts, but KEEP recommendation | KEEP -- actively rendered in UI, deliberate scaffolding | N/A (design decision) |
