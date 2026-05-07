# PROJ-361: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

**The bug:** `SimulationBattleResolver._run_simulated_battle` at `game/strategy/adapters/simulation_adapter.py:255-260` constructs a battle spec from the injected `registries` argument, then calls `run_battle(..., registry_provider=get_default_registry_provider())` — ignoring `registries` for ship materialization.

The PROJ-306 comment at lines 242-244 ("Strategy layer is allowed to call `get_default_registry_provider()`; the Simulation layer cannot") justifies *using* the default provider. It does **not** justify ignoring an explicitly injected one.

**Why it matters:**
- `ConflictResolutionEngine` always threads `self._registries` into `resolve_battle` (`conflict_resolution_engine.py:450-457`). Whenever session/mod-specific registries differ from the default, simulation ship materialization silently uses the default — divergent from spec construction.
- Tests that build a custom `GameRegistries` may pass spec construction but materialize ships from defaults.

## Swarm Findings Summary

### Architecture (findings/01_architecture.md)
- `IRegistryProvider` is a Protocol at `game/core/protocols/registry.py:7-39` with four methods: `get_components`, `get_modifiers`, `get_vehicle_classes`, `get_resources`.
- **`GameRegistries` already implements `IRegistryProvider` directly** (PROJ-211; `game/core/registry.py:66-112` exposes the four methods as pass-throughs at lines 93-107).
- **No adapter needed.** Structurally a one-line change.
- `run_battle` accepts `registry_provider: Optional["IRegistryProvider"] = None` at `game/simulation/battle_runner.py:255-265`.

### Dependencies (findings/02_dependencies.md)
- Production caller: only `ConflictResolutionEngine` (`conflict_resolution_engine.py:450-457`), which always passes `registries=self._registries`. The bug is internal; no consumer changes needed.
- Test resolvers (`InstantBattleResolver`, `MockResolver`) accept `registries` but bypass it — unaffected.
- No external code path depends on `get_default_registry_provider` being used when an injected registry exists.

### Test Impact (findings/03_test_impact.md)
- Existing tests at `tests/unit/strategy/adapters/test_simulation_adapter.py` (~14 cases) mock `run_battle`; they pass `registries=None` in 9+ cases. All continue to work (the default-fallback is preserved).
- Coverage gap: no test asserts a non-default registry threads through to ship materialization. PROJ-361 closes that gap.

### Risks
**None for production.** Tests passing `registries=None` keep their default-provider behavior. The change is additive.

### Key Patterns to Reuse
- **Default-fallback pattern:** `provider = registries if registries is not None else get_default_registry_provider()` — present at similar boundaries; follows PROJ-306 convention.
- **Marker-design fixture pattern:** test by injecting a `GameRegistries` whose component registry contains a unique design name not in defaults; assert the materialized ship reflects it.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
