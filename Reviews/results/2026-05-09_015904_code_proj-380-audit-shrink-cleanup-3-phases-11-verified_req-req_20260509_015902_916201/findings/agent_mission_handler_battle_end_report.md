# Review Report: DUP-X-01 & DUP-X-11

**Reviewer:** OpenCode (ocode-review-request)
**Date:** 2026-05-09 01:59:04 UTC
**Request:** req_20260509_015902_916201
**Scope:** PROJ-380 — DUP-X-01 MissionCommandHandler template + DUP-X-11 BattleEndCondition base serialization

---

## Item A: DUP-X-01 — MissionCommandHandler Template

### FND-020 — VERIFIED: MissionCommandHandler is a genuine BaseCommandHandler subclass, not a shim

**Severity:** INFO
**File:** `game/strategy/engine/superweapon_command_handlers.py:245`

`MissionCommandHandler` inherits directly from `BaseCommandHandler` (line 245). It is not a wrapper, re-export, or compat shim. It extends the existing `BaseCommandHandler` infrastructure with one abstract hook `_validate_mission` and one concrete `execute` implementing the shared 5-step mission flow. The `register()` function at line 442 correctly lists all 5 mission handler subclasses alongside the 6 direct handlers.

---

### FND-021 — VERIFIED: All 5 mission handlers share the consolidated shape cleanly

**Severity:** INFO
**Files:** `game/strategy/engine/superweapon_command_handlers.py:301-439`

Each of the 5 handlers implements `_validate_mission(session, fleet, cmd) -> tuple[ValidationResult, Any]` with their own validator call and target construction:

| Handler | Lines | Validator method | Target type | Notes |
|---|---|---|---|---|
| `ImplodePlanetMissionCommandHandler` | 301-323 | `validate_implode_planet` | `Planet` | Includes planet resolution inside `_validate_mission`; error short-circuits via `(error, None)` |
| `StellerateStarMissionCommandHandler` | 333-349 | `validate_stellerate_star` | `None` | Clean, no extra logic |
| `OpenWarpPointMissionCommandHandler` | 359-381 | `validate_open_warp_point` | `dict` | Passes `skip_location_check=True`; builds `target_dict` |
| `CloseWarpPointMissionCommandHandler` | 391-413 | `validate_close_warp_point` | `dict` | Passes `skip_location_check=True`; builds `target_dict` with `cmd.target_hex` coords |
| `CreateDysonSphereMissionCommandHandler` | 423-439 | `validate_create_dyson_sphere` | `None` | Clean, no extra logic |

No parameter shoehorns found. The variable target type (`Planet`, `None`, `dict`) is the design contract — documented in the `MissionCommandHandler` docstring (line 254): *"a planet, None, or a target dict, varies"*. All 5 handlers fit the `(ValidationResult, Any)` return signature naturally.

---

### FND-022 — VERIFIED: Template design is minimal

**Severity:** INFO
**File:** `game/strategy/engine/superweapon_command_handlers.py:245-291`

The template has exactly:
- 2 class attributes (`_ORDER_TYPE: OrderType`, `_ORDER_LABEL: str`)
- 1 abstract hook (`_validate_mission`)
- 1 concrete `execute` method with 5 steps (fleet resolve → validate → bail → move → emit)

No lifecycle hooks, no statefulness, no guard methods. The design is appropriately minimal.

---

### FND-023 — VERIFIED: No conflict with PROJ-383 command_handlers shim deletion

**Severity:** INFO
**Files:** `game/strategy/engine/command_handlers.py:1-82`, `game/strategy/engine/superweapon_command_handlers.py`

PROJ-383 targets `command_handlers.py` (82-line re-export shim for the `game.strategy.engine.handlers/` package). `superweapon_command_handlers.py` is a separate, standalone module. The PROJ-383 verification report (`Projects/active_projects/PROJ-383/findings/verification_report.md:36`) explicitly confirms `LEG-01-016` (the import re-route for `superweapon_command_handlers.py:15`) was already handled by PROJ-382 and is a no-op for PROJ-383. **The agent's claim is correct — no conflict exists.**

---

### FND-024 — VERIFIED: All 11 handlers (6 direct + 5 mission) register correctly

**Severity:** INFO
**Files:**
- `game/strategy/engine/superweapon_command_handlers.py:442-460` (register function)
- `game/strategy/engine/commands/registry.py:353-385` (seed_default_commands)

All 11 handlers use the `@command_spec` metadata-only decorator pattern. The `register()` function iterates all 11 handler classes, reads each class's `__command_spec_kwargs__`, and constructs a `CommandSpec` for `registry.register()`. `seed_default_commands` at `registry.py:383` calls `superweapon_command_handlers.register(registry)` during seeding. Registration chain is complete and correct.

---

## Item B: DUP-X-11 — BattleEndCondition Base Serialization

### FND-025 — VERIFIED: Base `to_dict` correctly captures common logic; no subclass fields lost

**Severity:** INFO
**File:** `game/simulation/systems/battle_end_conditions.py:116-118`

The base `to_dict` produces `{"type": _TYPE_TAG, **_serialize_fields()}`. All 9 subclasses override `_serialize_fields()` (or inherit the default `{}`):

| Subclass | `_TYPE_TAG` | `_serialize_fields` fields |
|---|---|---|
| `TickLimitCondition` | `"tick_limit"` | `max_ticks` |
| `TeamEliminatedCondition` | `"team_eliminated"` | `check_derelict` |
| `TeamIncapacitatedCondition` | `"team_incapacitated"` | *(none — default `{}`)* |
| `EscapeCondition` | `"escape"` | `escape_radius`, `arena_center` (list), `escape_team`, `escape_all_ships` |
| `ShipDestroyedCondition` | `"ship_destroyed"` | `ship_name` |
| `NeverCondition` | `"never"` | *(none — default `{}`)* |
| `MassRatioCondition` | `"mass_ratio"` | `threshold` |
| `AnyCondition` | `"any"` | `conditions` (list of nested dicts) |
| `AllCondition` | `"all"` | `conditions` (list of nested dicts) |

No fields are lost. `TeamIncapacitatedCondition` and `NeverCondition` correctly inherit the base default.

---

### FND-026 — VERIFIED: EscapeCondition tuple coercion handled correctly

**Severity:** INFO
**File:** `game/simulation/systems/battle_end_conditions.py:302-318`

- **Serialization** (line 302-308): `arena_center` converted from `Tuple[float, float]` to `list` via `list(self.arena_center)`. This is JSON-safe.
- **Deserialization** (line 310-318): Reads `data.get("arena_center", [0.0, 0.0])`, converts back to `tuple(center)`. Default is `(0.0, 0.0)`, matching the constructor default.
- **Test coverage** at `test_battle_end_conditions.py:306`: `assert restored.arena_center == (100.0, 200.0)` confirms round-trip preservation.

---

### FND-027 — VERIFIED: AnyCondition and AllCondition handle nested recursion correctly

**Severity:** INFO
**Files:** `game/simulation/systems/battle_end_conditions.py:452-498` (composites), `tests/unit/simulation/systems/test_battle_end_conditions.py:481-522` (tests)

- **Serialization:** Both `_serialize_fields` call `c.to_dict()` on each child, producing nested dict trees.
- **Deserialization:** Both `from_dict` call `end_condition_from_dict(d)` for each child dict entry.
- **Nested test** (line 505-521): `AnyCondition([AllCondition([TickLimitCondition, ShipDestroyedCondition]), TeamEliminatedCondition])` round-trips correctly — all types and nested structure preserved.

---

### FND-028 — VERIFIED: All 9 subclasses inherit cleanly with no broken signatures

**Severity:** INFO
**File:** `game/simulation/systems/battle_end_conditions.py:125-498`

All 9 conditions (`TickLimitCondition`, `TeamEliminatedCondition`, `TeamIncapacitatedCondition`, `EscapeCondition`, `ShipDestroyedCondition`, `NeverCondition`, `MassRatioCondition`, `AnyCondition`, `AllCondition`) inherit from `BattleEndCondition`. All implement `is_met`, `_serialize_fields` (or inherit default), `from_dict` (classmethod), `description` (property), and `__repr__`. No broken signatures.

Minor gap: `TeamIncapacitatedCondition` does not explicitly define `_serialize_fields` — it relies on the base default `return {}`. While this is correct behavior, it would be clearer to explicitly define it (consistent with `NeverCondition` which also has no fields but doesn't define it either). Both are functionally identical.

---

### FND-029 — VERIFIED: Round-trip equivalence holds for all 9 conditions

**Severity:** INFO
**File:** `game/simulation/systems/battle_end_conditions.py:505-532`

`end_condition_from_dict(to_dict(condition))` is equivalent for each subclass:

- **TickLimitCondition**: `data["max_ticks"]` round-trips directly.
- **TeamEliminatedCondition**: `data.get("check_derelict", False)` matches constructor default.
- **TeamIncapacitatedCondition**: No fields — always reconstructs identically.
- **EscapeCondition**: `tuple(center)` reconstruction verified by test.
- **ShipDestroyedCondition**: Direct field round-trip.
- **NeverCondition**: No fields — always equivalent.
- **MassRatioCondition**: `data.get("threshold", 0.10)` matches default. (Tested in `test_mass_ratio_condition.py:87-91`.)
- **AnyCondition/AllCondition**: Recursive `end_condition_from_dict` verified including nesting.

The `_CONDITION_TYPES` dispatch table (lines 505-515) correctly maps all 9 type tags to their classes.

---

### FND-030 — CONFIRMED: `from_dict` correctly stays per-subclass

**Severity:** INFO
**File:** `game/simulation/systems/battle_end_conditions.py:100-104`

The extraction rules diverge across subclasses:
- Mandatory fields (`TickLimitCondition.max_ticks`, `ShipDestroyedCondition.ship_name`)
- Optional with defaults (`TeamEliminatedCondition.check_derelict=False`, `MassRatioCondition.threshold=0.10`)
- Type coercion (`EscapeCondition: list→tuple`)
- Nested recursion (`AnyCondition`, `AllCondition`)
- No-op (`TeamIncapacitatedCondition`, `NeverCondition`)

A single base `from_dict` would require a field-schema descriptor system adding more complexity than it removes. The decision to keep `from_dict` per-subclass is correct and consistent with the "template minimizes base surface" design philosophy.

---

### FND-031 — MINOR: MassRatioCondition missing from protocol conformance parametrize

**Severity:** MINOR
**File:** `tests/unit/simulation/systems/test_battle_end_conditions.py:583-592`

`_END_CONDITION_CASES` lists 8 of 9 condition classes. `MassRatioCondition` is included in the repr tests (line 562) and has its own dedicated test file (`test_mass_ratio_condition.py`), but is absent from the shared parametrized `TestProtocolConformance` class. This means `MassRatioCondition` is not tested via `isinstance(cond, IEndCondition)`, `cond.description` type, or `cond.to_dict()` having a `"type"` key in the main test file. Its dedicated test file does cover serialization round-trip but not protocol conformance.

**Recommendation:** Add `(MassRatioCondition, {"threshold": 0.10})` to `_END_CONDITION_CASES` (requires fixing the `TestProtocolConformance` parametrize which currently uses `pytest.mark.parametrize("cls,kwargs", ...)` on a class — this pattern applies `test_isinstance_check`, `test_has_description`, and `test_to_dict_has_type` to all cases; adding the tuple should work).

---

### FND-032 — MINOR: TeamIncapacitatedCondition missing explicit `_serialize_fields`

**Severity:** ADVISORY
**File:** `game/simulation/systems/battle_end_conditions.py:245-247`

`TeamIncapacitatedCondition` (no constructor fields) relies on the base `BattleEndCondition._serialize_fields` default `return {}`. This is functionally correct but inconsistent with the pattern used by the other fieldless condition `NeverCondition` (which also doesn't define `_serialize_fields`). Both rely on the base default. For readability, consider explicitly defining:

```python
def _serialize_fields(self) -> Dict[str, Any]:
    return {}
```

Consistency with `NeverCondition` (line 376-381, which also doesn't define it) is the prevailing convention — no action needed.

---

## Summary

| ID | Item | Severity | Verdict |
|---|---|---|---|
| FND-020 | MissionCommandHandler is genuine BaseCommandHandler subclass | INFO | VERIFIED |
| FND-021 | All 5 mission handlers fit consolidated shape | INFO | VERIFIED |
| FND-022 | Template design is minimal | INFO | VERIFIED |
| FND-023 | No conflict with PROJ-383 | INFO | VERIFIED |
| FND-024 | Registration correct for all 11 handlers | INFO | VERIFIED |
| FND-025 | Base to_dict captures all fields | INFO | VERIFIED |
| FND-026 | EscapeCondition tuple coercion correct | INFO | VERIFIED |
| FND-027 | Nested recursion in composites correct | INFO | VERIFIED |
| FND-028 | All 9 subclasses inherit cleanly | INFO | VERIFIED |
| FND-029 | Round-trip equivalence holds | INFO | VERIFIED |
| FND-030 | from_dict stays per-subclass — correct decision | INFO | VERIFIED |
| FND-031 | MassRatioCondition missing from protocol conformance parametrize | MINOR | GAP |
| FND-032 | TeamIncapacitatedCondition relies on base _serialize_fields default | ADVISORY | OK |

**Overall assessment:** Both DUP-X-01 and DUP-X-11 are correctly implemented. No regressions, no design flaws, no correctness issues. Two minor observations (FND-031, FND-032) are low-severity and do not block acceptance.
