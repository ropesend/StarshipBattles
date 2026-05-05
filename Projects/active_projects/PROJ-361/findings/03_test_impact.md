# PROJ-351: Test Impact Analysis — Battle Resolver Registry Threading

## 1. Existing Tests Exercising SimulationBattleResolver

### tests/unit/strategy/adapters/

- **test_simulation_adapter.py:TestSimulationBattleResolverBehavior::test_resolve_battle_returns_battle_result** (L68)
  Verifies resolver returns BattleResult with winner, tick_count.

- **test_simulation_adapter.py:TestSimulationBattleResolverBehavior::test_resolve_battle_passes_seed_to_compiler** (L86)
  Confirms seed flows to spec builder.

- **test_simulation_adapter.py:TestSimulationBattleResolverBehavior::test_resolve_battle_constructs_two_teams** (L107)
  Asserts two teams (team 0, team 1) constructed from fleets.

- **test_simulation_adapter.py:TestSimulationBattleResolverBehavior::test_resolve_battle_handles_one_empty_fleet** (L132)
  Edge case: one empty fleet shortcuts to winner.

- **test_simulation_adapter.py:TestSimulationBattleResolverBehavior::test_resolve_battle_handles_both_empty_fleets** (L146)
  Both empty → winner=None, tick=0.

- **test_simulation_adapter.py:TestSimulationBattleResolverBehavior::test_resolve_battle_short_circuits_when_no_run_battle_needed** (L160)
  Mocks verify run_battle NOT called for sole-survivor branch.

- **test_simulation_adapter.py:TestSimulationBattleResolverBehavior::test_resolve_battle_determines_winner_from_outcome** (L176)
  Winner extracted from outcome; tick_count threaded through.

- **test_simulation_adapter.py:TestSimulationAdapterReplayId::test_simulator_branch_threads_replay_id_from_outcome** (L250)
  FEAT-26: replay_id flows from BattleOutcome → BattleResult.

- **test_simulation_adapter.py:TestSimulationAdapterReplayId::test_no_ships_shortcut_branch_replay_id_is_none_with_reason** (L286)
  No-ships edge case returns replay_unavailable_reason='no_ships'.

- **test_simulation_adapter.py:TestSimulationAdapterReplayId::test_sole_survivor_branch_replay_id_is_none_with_reason** (L301)
  Sole-survivor shortcut returns reason='sole_survivor'.

- **test_simulation_adapter.py:TestSimulationAdapterReplayId::test_no_capable_with_ships_runs_truncated_simulator_threads_replay_id** (L317)
  Issue #8: no combat-capable ships → runs brief tick budget, captures replay.

## 2. Tests Directly Constructing GameRegistries & Passing to resolve_battle

**No existing tests found** that:
1. Build a custom GameRegistries instance
2. Pass it to resolve_battle(..., registries=custom)
3. Assert the registry was used in ship materialization

**Current usage patterns** (from grep analysis):
- `test_simulation_adapter.py`: all tests mock `run_battle`, never inspect registries kwarg
- `test_battle_resolver_integration.py`: mock resolvers define `registries=None` param but never use it
- `test_battle_runner.py` & `test_battle_runner_di.py`: test `run_battle` directly with explicit `ship_builder` or `registry_provider`, not through SimulationBattleResolver

## 3. Existing Characterization of registry_provider Behavior

**No direct assertions** on which registry_provider was selected. Current coverage:

- **test_battle_runner_di.py:TestRunBattleRequiresProviderWhenNoBuilder::test_works_when_registry_provider_is_passed** (L131)
  Spy on materializer; verifies ship IDs round-trip when `registry_provider` passed to `run_battle`.
  Does NOT verify the materialized ship reflects custom registry data.

- **test_battle_runner_di.py:TestSimulationLayerHasNoGlobalLookup::test_no_simulation_call_to_get_default_registry_provider** (L182)
  AST guard: no `get_default_registry_provider()` call inside `game/simulation/`.

- **simulation_adapter.py:L255–260** (production code, not test):
  Calls `run_battle(..., registry_provider=get_default_registry_provider(), ...)`.
  **The resolver always uses DEFAULT provider, never the custom `registries` kwarg.**

## 4. Coverage Gap: Registry Threading to Ship Materialization

**CRITICAL GAP FOUND:**

The `SimulationBattleResolver.resolve_battle` signature accepts `registries: Optional[GameRegistries]` (L71),
but **it is NOT passed to run_battle**. Instead:

```python
# simulation_adapter.py:L255–260
outcome = run_battle(
    spec,
    ai_factory=self._ai_factory,
    registry_provider=get_default_registry_provider(),  # ← HARDCODED DEFAULT
    capture_context=capture_context,
)
```

The `registries` kwarg is:
1. Accepted by `resolve_battle` signature (for IBattleResolver contract)
2. Threaded to `_build_spec` (used by spec compiler)
3. **NOT threaded to run_battle** — no ship materializer receives the custom registries
4. Ignored in `_instances_to_ships` (L264: uses passed `registries`, not from run_battle)

**Result:** If a custom GameRegistries with unique components is passed to resolve_battle,
those components will NOT appear in materialized ships during the battle.
The battle always uses the global default registry provider's data.

**No test asserts that a non-default registry threads through to ship materialization.**

## 5. Recommended New Test Stub

**File:** `tests/unit/strategy/adapters/test_simulation_adapter_registry_injection.py`

**Test Class:** `TestRegistryThreadingToShipMaterialization`

**Test Name:** `test_custom_registry_with_marker_ability_appears_in_materialized_ship`

**What it asserts:**
1. Build a custom GameRegistries with a marker component (e.g., `"test_unique_ability"`) 
   not in default registries.
2. Build a mock fleet with ships that reference this custom component.
3. Inject a spy ship_builder (or materializer) that captures materialized ships.
4. Call `resolver.resolve_battle([fleet1, fleet2], registries=custom_registries)`.
5. **Assert:** The materialized ships contain the marker component from custom_registries.

**Marker design:**
```python
custom_component = {
    "id": "proj_351_test_marker",
    "name": "PROJ-351 Test Marker",
    "category": "special",
    "health": 1,  # Minimal footprint
    "cost": 0,
    "ability": {
        "id": "proj351_marker_ability",
        "name": "Test Marker"
    }
}
custom_registries.components["proj_351_test_marker"] = custom_component
```

Then assert the materialized ship has the marker ability, proving the custom registry was used.

## 6. Test Infrastructure Helpers (Reusable)

**Location:** `tests/conftest.py` (existing fixtures)

**Relevant helpers:**
- `session_registries()` (L154): Session-scoped GameRegistries loaded once per test session.
- `fresh_registries(session_registries)` (L190): Function-scoped deep-copy for test isolation.
- `minimal_registries()` (L228): Empty GameRegistries for isolated unit tests.
- `mock_registries(minimal_registries)` (L255): Alias for minimal_registries (clarity).

**New helper needed for PROJ-351:**
- `marker_registries(fresh_registries)`: A fresh_registries fixture with the test marker component pre-injected.
  Allows PROJ-351's new test to inject `marker_registries` and immediately test registry threading.

**Location suggestion:** `tests/unit/strategy/adapters/conftest.py` (new file)

```python
@pytest.fixture
def marker_registries(fresh_registries):
    """Fresh registries with PROJ-351 marker component injected."""
    marker_comp = {
        "id": "proj_351_test_marker",
        "name": "PROJ-351 Test Marker",
        "category": "special",
        "health": 1,
        "cost": 0,
    }
    fresh_registries.components["proj_351_test_marker"] = marker_comp
    return fresh_registries
```

---

**Summary:** No existing test verifies that a custom GameRegistries passed to resolve_battle
actually threads through to ship materialization. PROJ-351 must add this to prevent silent
registry-injection bugs in production.
