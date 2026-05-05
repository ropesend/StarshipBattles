# PROJ-320 — API & Interface Contract Reviewer Findings

## 1. `IConflictEngine` Protocol (`game/strategy/interfaces/engines.py:233-264`)

**Current signature:**
```python
@abstractmethod
def resolve_all_conflicts(
    self,
    empires: List,
    galaxy: Optional['Galaxy'] = None
) -> 'ConflictResult':
```

**Concrete implementations:**
- **Production:** `ConflictResolutionEngine` (`game/strategy/engine/conflict_resolution_engine.py:48`)
- **Tests:** `MockConflictEngine` (`tests/unit/strategy/mocks/mock_engines.py:150`)

**Assessment:** PROJ-320 will add an OPTIONAL `moved_fleet_ids: Optional[set[int]] = None` kwarg. Existing callers and the mock continue to work without modification (default None means "treat all fleets as potentially staying put"). Listed as required dependency in `TurnEngineConfig` (PROJ-259) field `conflict_engine: Optional[Any] = None` (`turn_engine_config.py:39`).

## 2. `IBattleResolver` Contract (`game/strategy/interfaces/battle_resolver.py:50-100`)

**Current signature (post-BUG-126):**
```python
@abstractmethod
def resolve_battle(
    self,
    fleets: Sequence['Fleet'],
    modifiers: Optional[Mapping[int, Any]] = None,
    seed: Optional[int] = None,
    registries: Optional['GameRegistries'] = None,
    environmental_effects: Any = None,
    empires: Optional[Mapping[int, Any]] = None,
) -> BattleResult:
```

**Multi-fleet support:** Already native N-team via `Sequence` (PROJ-275 Phase 7). Flat list of fleets — spec compiler maps by position (team_id = index). **No change needed.**

**Concrete impls:**
- **Production:** `SimulationBattleResolver` (`game/strategy/adapters/simulation_adapter.py:38, 66`)
- **Tests:** `InstantBattleResolver` (`tests/integration/strategy/test_fleet_registration_lifecycle.py:25`), `MockResolver` (`tests/unit/strategy/conflict_resolution/test_core.py:21`)

## 3. `BattleResult` DTO (`game/strategy/interfaces/battle_resolver.py:25-48`)

**Current fields:**
- `winner: Optional[int]` — surviving team id or None (draw)
- `tick_count: int` — battle duration
- `team_survivors: Dict[int, List[IPostBattleShip]]` — post-battle survivors per team (PROJ-275 Phase 7)
- `replay_id: Optional[str]` — captured replay uuid (FEAT-26)

**Assessment:** Fields are sufficient. No change.

## 4. `ConflictResult` DTO (`game/strategy/engine/conflict_resolution_engine.py:41-45`)

**Current shape:**
```python
@dataclass
class ConflictResult:
    combats_resolved: int
    fleets_destroyed: List[int]
```

**Callers & assertions:**
- TurnEngine: discards result (`turn_engine.py:698`) — no consumption
- Tests: `test_fleet_registration_lifecycle.py:179-180` asserts `result.combats_resolved == 1`
- Tests: `test_combat_shortcut_paths.py` directly mutates `engine._combats_resolved`

**Assessment:** No breaking changes. PROJ-320 increments `_combats_resolved` once per round fired.

## 5. Spec Compiler Signature (`game/strategy/combat/spec_compiler.py:70-81`)

Current signature stable. Compiler is called once per battle round; no new params needed. Seed regenerated per round via `_generate_battle_seed()`.

## 6. `PostBattleHook` Contract (`game/strategy/combat/post_battle_hook.py:40-86`)

**Multi-round idempotence:** Hook fires once per battle round. Each round, outcome state is applied to the fleets. **Idempotent**:
- Ship removal keyed by `instance_id` (line 72-73), safe to re-apply
- Component HP updates are authoritative (line 159, fresh overwrite each round)
- Empty fleet pruning checks fleet membership (line 192), safe to re-call

**Verdict:** Multiple rounds per encounter work correctly.

## 7. `Fleet` Public API (`game/strategy/data/fleet.py:39-100`)

**Methods changed by PROJ-320?** None. Fleet remains a stateless data holder for the scheduler.

## 8. `get_tick_interval` Public API (`game/strategy/services/fleet_speed_calculator.py:39-58`)

`ConflictResolutionEngine` becomes a second consumer (after `FleetMovementEngine`). **Safe, read-only expansion** — function signature unchanged.

## 9. Test Mocks

| File | Class | Type |
|------|-------|------|
| `tests/unit/strategy/mocks/mock_engines.py:150` | `MockConflictEngine` | Mock IConflictEngine |
| `tests/unit/strategy/mocks/mock_engines.py:31` | `MockMovementEngine` | Mock IMovementEngine (not conflict-related) |
| `tests/unit/strategy/conflict_resolution/test_core.py:21` | `MockResolver` | Inline mock IBattleResolver |
| `tests/integration/strategy/test_fleet_registration_lifecycle.py:25` | `InstantBattleResolver` | Mock IBattleResolver |

**Update requirements:**
- `MockConflictEngine`: **no change** — `resolve_all_conflicts(empires, galaxy=None)` signature stable; new optional kwarg defaults handle it
- `MockResolver` / `InstantBattleResolver`: **no change** — `resolve_battle(fleets, ...) -> BattleResult` signature stable

## 10. Static Guards

No AST-level entrypoint guards on `ConflictResolutionEngine` or `resolve_all_conflicts`. The conflict-engine entrypoint is unguarded.

## Summary

**Public-API breaking changes required: NO**

- `IConflictEngine.resolve_all_conflicts()` extended with optional kwarg (backward-compatible)
- All other interfaces stable

**Mock impls needing update: 0**

**Risk level: LOW.** Per-fleet-per-tick triggering is a private implementation detail inside `ConflictResolutionEngine`. All contracts remain stable.
