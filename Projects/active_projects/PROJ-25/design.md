# PROJ-25: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source
- **Origin:** Future work identified in PROJ-24 plan
- **Dependency:** PROJ-24 (ShipControllableAdapter interface migration)

## Initial Analysis

### The Problem: Dual AI Implementations

Two parallel AIController implementations exist in active production use:

| Implementation | Location | Status |
|---------------|----------|--------|
| **Simulation Layer** | `game/ai/controller.py` + `behaviors.py` | Modern, refactored, modular |
| **UI/Legacy Layer** | `game/ai/core/system.py` + `core/behaviors.py` | Legacy, monolithic (~625 lines) |

### Architecture Comparison

| Aspect | Simulation (`controller.py`) | Legacy (`core/system.py`) |
|--------|------------------------------|---------------------------|
| Structure | Modular (separate files) | Monolithic (~625 lines) |
| StrategyManager | External class with thread-safe singleton | Inline + lazy proxy pattern |
| TargetEvaluator | External class, injectable helpers | Inline + static methods |
| Config values | BattleConfig/AIConfig constants | Hardcoded (200000 radius, etc.) |
| Ship wrapping | ShipControllableAdapter | Plain ship object |
| Documentation | Comprehensive docstrings | Minimal |
| Thread safety | Double-check locking singleton | Simple global variable |
| Test support | `reset()`, `clear()` methods | None |

## Swarm Findings Summary

### Feature Parity Analysis: CONFIRMED

**All behaviors exist in both implementations:**

| Behavior | Legacy | Refactored | Notes |
|----------|--------|------------|-------|
| RamBehavior | Yes | Yes | Equivalent |
| FleeBehavior | Yes | Yes | Refactored uses AIConfig |
| KiteBehavior | Yes | Yes | Refactored uses AIConfig |
| AttackRunBehavior | Yes | Yes | Refactored uses AIConfig |
| FormationBehavior | Yes | Yes | Refactored uses AIConfig |
| OrbitBehavior | Yes | Yes | Refactored uses AIConfig |
| DoNothingBehavior | Yes | Yes | Equivalent |
| StraightLineBehavior | Yes | Yes | Equivalent |
| RotateOnlyBehavior | Yes | Yes | Equivalent |
| ErraticBehavior | Yes | Yes | Refactored uses AIConfig |
| StationaryFireBehavior | No | Yes | **NEW in refactored** |

**AIController methods: 100% parity** - All methods exist in both with equivalent logic.

### Consumer Analysis

**Simulation Layer (`game/ai/controller.py`):**
- `game/simulation/systems/battle_engine.py` - Primary consumer
- `game/ui/orchestration/battle_orchestrator.py` - Creates controllers for UI layer
- 14 test files

**Legacy Layer (`game/ai/core/system.py`):**
- `game/ui/screens/battle.py` - **UNUSED import** (AIController never instantiated)
- `game/ui/screens/setup.py` - Uses `COMBAT_STRATEGIES` for dropdown
- `game/ui/screens/builder/right_panel.py` - Uses `STRATEGY_MANAGER` for dropdown
- `game/ui/hud/panels.py` - Uses `COMBAT_STRATEGIES` for display
- 7 test files

### What UI Actually Needs

| File | Import | Actual Usage | Migration |
|------|--------|--------------|-----------|
| `battle.py` | `AIController` | **UNUSED** | Remove import |
| `setup.py` | `COMBAT_STRATEGIES` | `.keys()`, `.get()` for dropdown | `StrategyManager.instance().strategies` |
| `right_panel.py` | `STRATEGY_MANAGER` | `.strategies` for dropdown | `StrategyManager.instance()` |
| `panels.py` | `COMBAT_STRATEGIES` | `.get()` for display names | `StrategyManager.instance().strategies` |

## Key Patterns to Reuse

- **Singleton Pattern**: `game/ai/strategy_manager.py` - `StrategyManager.instance()` with thread-safe double-check locking
- **Direct Access**: Use `StrategyManager.instance().strategies` instead of proxy dict

## Dependencies & Risks

1. **COMBAT_STRATEGIES API Change (MEDIUM)**
   - Legacy provides dict-like proxy (`COMBAT_STRATEGIES.keys()`)
   - Refactored requires direct access: `StrategyManager.instance().strategies`
   - **Mitigation:** Only 3 files use it; straightforward search-replace

2. **Lazy Initialization (LOW)**
   - Legacy auto-loads strategy data on first access
   - Refactored needs explicit `ensure_loaded()` call
   - **Mitigation:** Verify game startup calls ensure_loaded()

3. **Import Path Changes (LOW)**
   - All imports change from `game.ai.core.system` to `game.ai.strategy_manager`
   - **Mitigation:** Simple find-replace, run tests to verify

4. **Test File Updates (MEDIUM)**
   - ~7 test files need import updates
   - 2 root-level test files need relocation
   - **Mitigation:** Systematic migration with test runs after each change

## Opportunities Discovered

1. **StationaryFireBehavior** - New behavior in refactored version not in legacy (bonus feature)
2. **Better Test Support** - Refactored StrategyManager has `reset()` and `clear()` methods for test isolation
3. **Configurable Constants** - All magic numbers moved to AIConfig for easier tuning

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

### Key Decisions

1. **Canonical Implementation:** Simulation Layer (`controller.py`)
   - Modern, refactored, modular
   - Uses ShipControllableAdapter (required for PROJ-24)
   - Better documented and tested

2. **No Compatibility Shim:** Direct migration
   - Cleaner than proxy layers
   - Only 4 UI files to update
   - Makes future maintenance easier

3. **Move Root Test Files:** To `tests/integration/`
   - Consistent with project test structure
   - Improves discoverability
