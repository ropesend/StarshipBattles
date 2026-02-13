# PROJ-90: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Audit Claim vs Reality

The code review audit claimed "50+ TYPE_CHECKING import guards across 30+ files" indicating tangled dependencies. Deep analysis by 6 swarm agents found:

- **29 files** with `TYPE_CHECKING` blocks (not 50+)
- **28 files** with late/lazy imports
- **Most are LEGITIMATE patterns**, not workarounds
- **No true runtime circular dependency cycles exist** — all potential cycles are already broken
- **Layer architecture is fundamentally sound** — only 1 real layer violation found

### What's Actually Wrong (5 Issues)

1. **Core → Simulation violation** — `registry.py:reload_all_from_directory()` has 3 late imports from simulation
2. **BattleConfig/BattleMode placement** — co-located in `battle_controller.py`, forces late import in `battle_state_manager.py`
3. **No-op TYPE_CHECKING block** — `ship.py` lines 14-15: `if TYPE_CHECKING: pass`
4. **Unnecessary late imports in ship.py** — 4 late imports verified to NOT be real cycles
5. **ShipInstance→Ship coupling** — uses concrete Ship type where a protocol would suffice

### What's FINE (Legitimate Patterns)

- **TurnEngine 9 lazy properties** — proper service locator/DI pattern with constructor injection support
- **App.py lazy imports** — startup optimization for UI screens
- **UI TYPE_CHECKING imports** — proper downward dependencies (UI → Strategy/Simulation)
- **Fleet.py service late imports** — documented edge operations for navigation/speed
- **ShipInstance.to_ship()/from_ship() ShipSerializer imports** — intentional cross-layer calls in allowed direction

## Swarm Findings Summary

### Architecture Analysis
- Layer rules (Core → Simulation → Strategy → UI) are **well-enforced**
- Only violation: `game/core/registry.py` imports from `game/simulation/` (3 late imports in `reload_all_from_directory`)
- `game/engine/` belongs to Simulation layer, fully compliant
- No Simulation → Strategy, Simulation → UI, or AI → UI violations exist

### Dependency Cycle Classification

| Cycle | Type | Pattern | Verdict |
|-------|------|---------|---------|
| Ship ↔ ShipCombatEngine | Intra-module | Lazy property | Legitimate (init order) |
| Ship ↔ ShipSerializer | Intra-module | Late import | **Fixable** — no real cycle |
| BattleStateManager ↔ BattleController | Service layer | Late import | **Fixable** — extract config |
| TurnEngine → 9 engines | Service locator | Lazy properties | Legitimate (DI pattern) |
| Strategy → Simulation | Cross-layer | TYPE_CHECKING | Correct layering |
| UI → Internals | UI coupling | TYPE_CHECKING | Acceptable |
| Core/Registry | Service locator | Singleton DI | Correct |

### Ship.py Late Import Verification

All 4 late imports in ship.py were traced to confirm no real cycle exists:

| Import | Real Cycle? | Evidence |
|--------|-------------|----------|
| WeaponAbility (line ~244) | **No** | `abilities/weapons.py` doesn't import Ship |
| ModifierService (lines ~507, 552) | **No** | `modifier_service.py` doesn't import Ship |
| ShipCombatEngine (line ~219) | **No** | Uses TYPE_CHECKING only for Ship |
| ShipSerializer (lines ~835, 863) | **Pseudo** | Has runtime late import of Ship in `from_dict()`, but NOT at module level |

### Data Flow Analysis: Strategy ↔ Simulation Boundary

The boundary crossing points are:
1. `ShipInstance.to_ship()` — Strategy creates Ship via ShipSerializer (allowed direction)
2. `ShipInstance.from_ship()` — Strategy reads Ship state (allowed direction)
3. `ShipInstance.update_from_ship()` — Strategy reads post-battle Ship state
4. `Fleet.update_from_battle_results()` — Takes `List[Ship]` from battle
5. `SimulationBattleResolver` — The primary adapter crossing point

**Key insight:** `design_data` (dict) is already the natural boundary format. `ShipStatsCalculator` in strategy already works purely with dicts. The protocol formalizes what `update_from_ship()` actually reads.

### Dependencies & Risks
1. **Phase 3 (Ship.py import moves)** — Low risk. All verified safe. Worst case: import order issue caught immediately by import sanity check.
2. **Phase 2 (Registry extraction)** — Low risk. Only 1 test file calls `reload_all_from_directory`.
3. **Phase 1 (BattleConfig extraction)** — Low risk. Mechanical find-and-replace across 12 files.
4. **Phase 4 (Protocol)** — Very low risk. Type annotation changes only, no runtime behavior change.
5. **ShipSerializer bidirectional** — `ship_serialization.py` has runtime import of Ship inside `from_dict()` method body (NOT module level). Moving ShipSerializer import to module level in `ship.py` is safe because `ship_serialization.py` finishes loading before `from_dict()` is ever called.

### Opportunities Discovered
- `BattleResult.team0_survivors` and `team1_survivors` are typed as `List[Any]` — can be strengthened to `List[IPostBattleShip]`
- `ShipInstance.from_ship()` has **zero callers** in production code — could be deprecated in future
- `ship_component_manager.py` has the same unnecessary ModifierService late import as ship.py

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
