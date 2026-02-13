# PROJ-107: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Error Code System (PROJ-45 Legacy)
PROJ-45 established the ErrorCode enum in `game/core/error_codes.py` with 6 categories (V, S, R, P, F, C). However, adoption is incomplete:
- StrategyManager uses raw string "AI001" (no AI category exists)
- Docstring examples in exceptions.py and validation.py use invalid codes ("E001", "V002")
- The exceptions module docstrings show ErrorCode.value usage in one place but raw strings in others

**Fix:** Add AI category (A001-A099), update all raw strings to use ErrorCode enum values.

### Type Hint Coverage
The codebase has inconsistent type hint coverage:
- **AI layer:** Most methods have return type hints. Notable gaps: `get_engage_distance_multiplier`, module-level functions in target_evaluator.py
- **Simulation layer:** ShipStatsCalculator has 11+ methods with no return type hints. Ship stats calculation is a critical path.
- **Strategy layer:** `commands.py` uses `target_hex: Any` in 16 places where `HexCoord` is the actual type (and is already imported). `to_dict()` return types use bare `dict` vs `Dict[str, Any]` inconsistently.
- **UI layer:** BattleUIService private conversion methods (_convert_ship, etc.) lack return types despite returning well-defined DTOs.

**Fix:** Add type hints to all identified gaps. Replace `Any` with `HexCoord` in commands.

### Naming Inconsistencies
- `add_ship()` vs `add_ship_instance()` in Fleet class are identical methods (same body, same behavior). 6 external callers use `add_ship_instance()`.
- `_stat_*` prefix in AIController wraps TargetEvaluator `_default_*` methods with zero added value. Can be deleted.
- `check_missiles` parameter name is ambiguous ("verify" vs "search for"). Should be `include_missiles`.

**Fix:** Delete duplicates, rename ambiguous parameters, update all call sites.

### UI Service DI Patterns
Four UI services use four different DI conventions:

| Service | Pattern | Parameter Name |
|---------|---------|---------------|
| ComponentService | Optional with lazy default | `registry_provider` |
| VehicleClassService | Strict required | `registry_provider` |
| ShipFactory | Keyword-only, optional | `registries` |
| DesignLoaderAdapter | Dual params | `registries` |

The naming inconsistency (`registry_provider` vs `registries`) is the actionable issue. The strict-vs-optional choice was intentional per PROJ-50.

**Fix:** Standardize parameter name to `registry_provider` across all services.

### Simulation API Confusion
- `BattleResults` (battle_state.py) = battle outcome data (winner, ships)
- `BattleResult` (battle_service.py) = service operation result (success/errors)
- These are different concepts with nearly identical names, causing confusion.
- `get_winner()` returns `int` in BattleEngine but `Optional[int]` in BattleService. This is actually correct (BattleService adds the None case for "no engine") but undocumented.

**Fix:** Rename service-layer type to `BattleServiceResult`. Document return type semantics.

## Architecture

### Layer Dependency Flow
```
Core (error_codes, exceptions, validation, protocols)
  ^
  |
Simulation (battle_state, battle_engine, ship_stats, resource_manager)
  ^
  |
Strategy (fleet, commands, game_session)
  ^
  |
UI (services/*, screens/*)
  ^
  |
AI (controller, target_evaluator, strategy_manager)
```

### Key Patterns to Reuse

- **ErrorCode enum pattern:** `game/core/error_codes.py:52-138` - Well-structured enum with docstrings per value. New AI category follows same pattern.
- **Exception hierarchy:** `game/core/exceptions.py:81-227` - All exceptions support `code` and `context`. Use `StateException` for state violations, `ValidationException` for data validation.
- **DI lazy default pattern:** `game/ui/services/component_service.py:31-44` - Optional provider with `_get_provider()` lazy resolution. Standard pattern for new services.
- **DTO conversion pattern:** `game/ui/services/battle_ui_service.py:50-86` - Engine -> DTO conversion with None-safe engine checks. All conversion methods should have return type hints.

### Dependencies & Risks

1. **BattleServiceResult rename (Phase 5)** - Highest risk. Touches every BattleService caller. Mitigation: thorough grep before and after, run full test suite.
2. **add_ship_instance deletion (Phase 3)** - 6 call sites across production and test code. Mitigation: exact call sites documented in checklist.
3. **ShipFactory registry_provider rename (Phase 4)** - All call sites use keyword args. Mitigation: grep for `ShipFactory(` to find all callers.
4. **battle_controller exception type change (Phase 5)** - Tests that catch `ValueError` must be updated. Mitigation: grep for tests catching ValueError from these methods.

### Opportunities Discovered
- The codebase has good foundational patterns (ErrorCode enum, exception hierarchy, DI protocols) but incomplete adoption
- 13 findings are already covered by active God Class Decomposition projects (PROJ-86/87/88/89) - no duplicate work needed
- Event handler naming (handle_event vs process_event) affects ~50 files and warrants its own project

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
