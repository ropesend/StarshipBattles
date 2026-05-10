# General Code Review: Maintainability & Extensibility

**Date:** 2026-01-27
**Reviewer:** "Review Swarm" (Simulated)
**Scope:** Strategy Layer, Engine Core, UI Coupling

## Executive Summary
The codebase is currently in a **transitional state** (evident by `PROJ-12` refactoring comments). While there is a clear effort to move towards a modular architecture (e.g., extracting `FleetMovementEngine` and `StrategyRenderer`), the system currently suffers from "mid-refactor" fractures. The most critical risk is the Divergent Logic between the UI's prediction of events (pathfinding/movement) and the Engine's actual execution, caused by code duplication.

## Top 5 Issues

### 1. Duplicate Movement Logic ("Split Brain" Risk)
**Severity:** Critical
**Location:** `game/strategy/engine/fleet_movement.py` vs `game/strategy/engine/fleet_movement_engine.py` vs `pathfinding.py`

There are currently three different modules handling fleet movement and pathfinding logic:
- `FleetMovementSimulator` (`fleet_movement.py`): Used by `pathfinding.py` for UI path projection. Claims to be the "single source of truth" but is NOT used by the Turn Engine.
- `FleetMovementEngine` (`fleet_movement_engine.py`): Used by `TurnEngine` for actual game state updates.
- `pathfinding.py`: Contains core algorithms (`calculate_intercept_point`, `find_hybrid_path`) that call into the Simulator, creating a circular dependency risk and logic fork.

**Impact:** High risk of bugs where the UI shows a fleet moving one way (using Simulator) but the turn processor moves it differently (using Engine), leading to "ghost" fleets or invalid intercept calculations.

**Recommendation:** Unify into a single `FleetNavigationService` that is stateless and used by both the UI (for projection) and the TurnEngine (for execution).

### 2. Logic Leaking into UI (`StrategyScene`)
**Severity:** High
**Location:** `game/ui/screens/strategy_scene.py`

`StrategyScene` violates the separation of concerns by directly accessing deep simulation state:
- Direct property access: `self.session.galaxy`, `self.session.turn_engine`.
- Logic execution: Calls `calculate_hybrid_path` directly.
- State mutation: While it delegates some actions to `ColonizationSystem`, it still orchestrates too much "business logic" regarding when and how orders are validated.

**Impact:** Makes the UI fragile to engine changes and hard to test. Changing the underlying data structure of `Galaxy` would break the UI.

**Recommendation:** Implement a strict **Command Pattern**. The UI should only fire commands (e.g., `IssueMoveCommand(fleet_id, target_hex)`) to the `GameSession`, which then handles validation and execution. The UI should observe state changes rather than querying state properties directly.

### 3. Transitional God Class (`TurnEngine`)
**Severity:** Medium-High
**Location:** `game/strategy/engine/turn_engine.py`

Although `TurnEngine` has started delegating tasks (to `FleetMovementEngine`, `ProductionEngine`), it remains a "God Class" that knows too much.
- It still manually orchestrates the 5-phase tick loop.
- It contains legacy compatibility methods (`_calculate_next_hex`).
- It handles `validate_colonize_order` internally, mixing rules validation with turn processing.

**Impact:** Increases cognitive load for developers. Modifying turn order or adding new phases (e.g., "Diplomacy Phase") requires modifying this central, risky file.

**Recommendation:** Complete the decomposition. Move validation logic to `RuleValidators`. The `TurnEngine` should be a lightweight orchestrator that simply iterates over a list of `ISubSystem` (Movement, Production, Combat) without knowing their implementation details.

### 4. Fragile Asset Loading
**Severity:** Medium
**Location:** `game/ui/screens/strategy_scene.py` (lines 435-491)

Asset paths are hardcoded directly into the UI code:
- `Images/Flags/Processed`
- `Skins/Battlecruiser.png`
- Logic for color-based star asset selection is hardcoded (`if color[0] > 200...`).

**Impact:** Moving files or changing the art style requires code changes in UI classes. extremely brittle.

**Recommendation:** Move all asset path definitions to an external `asset_manifest.json` or a centralized `AssetConfiguration` class. The UI should request assets by logical key (e.g., `get_asset("ship_icon", class="battlecruiser")`) without knowing the file path.

### 5. Hidden Dependencies via Singleton (`RegistryManager`)
**Severity:** Medium
**Location:** `game/core/registry.py`

The use of a Singleton `RegistryManager` creates global state that is accessible from anywhere. While "safer" than raw global variables, it still hides dependencies.
- Classes like `ShipDesignUtils` likely pull from `RegistryManager.instance()` implicitly.

**Impact:** Unit testing becomes difficult because tests interact via this shared global state, requiring complex `setUp/tearDown` logic (`reset()`, `hydrate()`) to avoid pollution between tests.

**Recommendation:** Prefer **Dependency Injection**. Pass the required registries (ComponentRegistry, etc.) into the constructors of the classes that need them (e.g., `GameSession`, `TurnEngine`). Use the Singleton only at the very top level (`app.py`) to wire things up.

## Conclusion
The codebase has "good bones" but is suffering from growing pains. The highest priority is **Issue #1 (Split Brain Movement)**, as it directly compromises the reliability of the strategy layer. Issues #2 and #4 are strong candidates for "Technical Debt" cleanup to make future feature development (like new races or new UI skins) much faster.
