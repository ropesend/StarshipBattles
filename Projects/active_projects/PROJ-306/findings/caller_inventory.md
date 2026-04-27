# Phase 1.1: Caller Inventory for `run_battle` / `BattleController.start_from_spec`

Generated 2026-04-27. All entries verified against source.

## Production callers of `run_battle(...)` (game/ + combat_lab/)

| Caller | Lines | Passes `ship_builder`? | Category |
|--------|-------|------------------------|----------|
| `game/strategy/adapters/simulation_adapter.py` | 152-155 | NO | **B** — relies on context fallback |
| `combat_lab/services/scenario_run_helper.py::run_scenario_via_run_battle` | 111-117 | YES — wraps `_default_ship_builder_from_context()` for role-tagging | **A** with hidden import |
| `combat_lab/scenarios/templates.py::ComparisonScenario._run_baseline_battle` | 886-892 | YES — same pattern | **A** with hidden import |
| `combat_lab/services/ab_battle_runner.py::ABBattleRunner._run_one` | 102 | Pass-through (whatever caller injected, possibly None) | **B** — relays |

## Production callers of `BattleController.start_from_spec(...)`

| Caller | Lines | Passes `ship_builder`? | Category |
|--------|-------|------------------------|----------|
| `game/app.py::start_battle` | 574-578 | NO | **B** |
| `combat_lab/services/test_execution_service.py::run_visual` | 100-104 | NO; ALSO calls `_default_ship_builder_from_context()` at line 91 explicitly to pre-materialize for snapshots | **B** + hidden import |

## Test callers
- `tests/unit/simulation/test_battle_runner*.py` — many call sites, ALL pass an explicit `ship_builder` stub. **Category A**.
- `tests/integration/strategy/combat/*.py`, `tests/integration/simulation/*.py` — explicit stubs. **A**.
- `tests/fixtures/battle.py:214` — explicit ship_builder closure. **A**.
- `tests/integration/test_make_minimal_spec_smoke.py:33,68` — explicit. **A**.
- `tests/performance/test_telemetry_overhead.py:118` — explicit. **A**.

## Three production sites import the private fallback DIRECTLY

These are the truly load-bearing sites and the reason the function must remain available in some form:

1. `combat_lab/services/test_execution_service.py:86-92` — pre-materializes ships for `initial_state` snapshot using `_default_ship_builder_from_context()` directly.
2. `combat_lab/services/scenario_run_helper.py:72-75,77-84` — pulls a context-backed builder, wraps it in role-tagging closure.
3. `combat_lab/scenarios/templates.py::ComparisonScenario._run_baseline_battle` (line 832-844) — same pattern.

These sites need a public successor (renamed function) that lives outside `game/simulation/` OR accepts the `registry_provider` as a required argument.

## Categories totals

- **Category A (passes explicit ship_builder)**: 4 production + ~50 test sites
- **Category B (relies on default fallback)**: 3 production sites (simulation_adapter, app.py, test_execution_service.run_visual)
- **Hidden import sites**: 3 production (the 3 combat_lab files above)

## Migration pattern (decision-locked in decisions.md)

**Pattern B (context-fetch) for `run_battle` and `BattleController.start_from_spec` AT THE PUBLIC EDGE** — keep the `ship_builder=None` ergonomics so the 3 Category-B production callers don't need to be modified.

**Pattern A (required parameter) for the underlying helper** — rename `_default_ship_builder_from_context` to a public name AND have it accept an explicit `registry_provider`. The public callers that use this helper (3 combat_lab sites) supply the provider themselves, since `combat_lab/` is NOT inside `game/simulation/` and IS allowed to call `get_default_registry_provider()`.

**The Simulation-layer call site at `battle_runner.py:198` must reach the registry provider via injection.** Since `run_battle` and `start_from_spec` are entry points called from many layers, the cleanest move is:

1. Add a `registry_provider: Optional[IRegistryProvider]` kwarg to `run_battle`.
2. When `ship_builder is None` AND `registry_provider is None`, raise `RuntimeError` with guidance — no global lookup from inside `game/simulation/`.
3. Migrate the 3 Category-B production callers (in non-Simulation layers: `game/strategy/`, `game/app.py`, `combat_lab/services/test_execution_service.py`) to pass `registry_provider=get_default_registry_provider()`.

This is consistent with how PROJ-252 already mandates Simulation-layer DI.

## Layer note

`game/strategy/`, `game/app.py`, and `combat_lab/` are all OUTSIDE `game/simulation/`. They MAY call `get_default_registry_provider()` (it's pattern #2 in `docs/02_PATTERNS.md` §3). The PROJ-252 prohibition is specifically that **Simulation code** must not. So the migration moves the global lookup OUT of Simulation, satisfying the rule.
