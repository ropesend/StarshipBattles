# PROJ-439: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source

This charter comes from two verified inputs:

- The shared roadmap discussion outcome at `AgentCoordination/Scratchpad/Discussion/20260518T030705Z_tech-debt-roadmap/plans/tech_debt_roadmap_r001.md`.
- Direct local code review during project creation, including a fresh baseline run of `python Tools/test_sharded/test_sharded.py` (`21233/21233` passed).

No new Codex subagent swarm was launched during project creation because the
current Codex instructions forbid unrequested delegation. The findings below are
therefore sequential-review findings, not a fresh local swarm artifact set.

## Initial Analysis

### Current production content seams

The current content system has multiple independent load paths:

- `game/core/resources.py`
  - `ResourceDefinition` at line 30
  - `ResourceCatalog` at line 53
  - `from_json()` at line 85
  - `from_data()` at line 114
- `game/simulation/components/component_loader.py`
  - `load_components_data()` at line 77
  - `load_components()` at line 139
  - `load_modifiers_data()` at line 186
  - `load_modifiers()` at line 240
- `game/simulation/entities/ship_loader.py`
  - `load_vehicle_classes_data()` at line 50
  - `load_vehicle_classes()` at line 117
- `game/simulation/services/registry_loader.py`
  - `reload_registries_from_directory()` at line 31
- `game/app_bootstrap.py`
  - resource hydration at lines 228-246
- `game/strategy/systems/design_repository.py`
  - `DesignRepository` at line 102
  - `load_design_data()` at line 280
- `game/ui/services/design_loader_adapter.py`
  - `DesignLoaderAdapter` at line 22
  - `load_ship_from_file()` at line 83

These paths do not currently share one validation helper or one failure policy.

### Current contract weaknesses

1. **No shared production schema layer**
   - There is no top-level `data/schemas/` directory.
   - `grep -r "jsonschema|schema_validate" game/` returns zero hits.

2. **Manual registry drift**
   - `ABILITY_REGISTRY` is a hand-maintained dict in
     `game/simulation/components/abilities/__init__.py:130`.
   - `create_ability()` and `get_ability_default_scope()` depend on this map at
     lines 236-278.

3. **Formula overreach**
   - `FormulaEvaluator` is a custom AST walker in
     `game/core/formula_evaluator.py:81-203`.
   - It uses the blocklist `DANGEROUS_NAMES` at line 35, which is a safety
     measure but also a signal that free-form string formulas are carrying real
     complexity in the content model.

4. **Inconsistent error handling**
   - `ResourceCatalog.from_json()` warns and returns an empty catalog on failure.
   - `load_modifiers_data()` warns when `validate_modifier_v2()` fails but still
     attempts to load the modifier.
   - `RegistryLoader` logs per-family errors and continues.

### Existing precedent worth reusing

`game/simulation/components/modifier_schema.py:193` already has a local
`validate_modifier_v2()` helper. That is not a full project solution, but it is
proof that schema-style validation is already an accepted pattern in this code
base. PROJ-439 should generalize that idea rather than building a parallel
"contracts" culture.

## Review Findings Summary

### Architecture

- Validation belongs in a Core-layer shared helper, not in a Simulation-only
  module. Startup (`game/app_bootstrap.py`), design loading
  (`game/strategy/systems/design_repository.py`), UI loaders
  (`game/ui/services/design_loader_adapter.py`), and registry reloads all need
  to consume the same validation logic without creating new upward imports.
- Loader validation must happen on raw JSON payloads before runtime objects are
  instantiated and cached. This matters especially for
  `game/simulation/components/component_loader.py`, where the cache manager can
  clone already-instantiated objects on repeated loads.

### Key Patterns to Reuse

- **Shared loader helper pattern**: `game/core/json_utils.py:119` already
  centralizes required JSON loading. PROJ-439 should add validation beside this
  helper instead of replacing it.
- **Partial schema precedent**: `game/simulation/components/modifier_schema.py`
  shows how to validate a content family before object construction.
- **Registry DI discipline**: `game/simulation/services/registry_loader.py`
  keeps Simulation loaders free of global provider lookup; validation must not
  regress that boundary.

### Dependencies and Risks

1. **Schema breadth risk**
   - `data/components.json` is the hardest content surface because abilities use
     multiple legal shapes: booleans, scalars, dicts, lists, and formula
     strings.
   - Mitigation: add schema coverage incrementally and pin current legal shapes
     with characterization tests before tightening anything.

2. **Behavior-change risk**
   - Loaders currently tolerate some malformed data. Moving directly to
     hard-fail could break workflows or tests unexpectedly.
   - Mitigation: Phase 1 explicitly decides boundary behavior for startup,
     tooling, and on-demand loads before Phase 3 changes code.

3. **Dependency risk**
   - If JSON Schema consumption introduces a new runtime dependency, startup,
     packaging, and test environments must all agree on it.
   - Mitigation: make the dependency decision in Phase 1 and log it before
     creating the shared helper.

4. **Formula-regression risk**
   - Some formulas are truly runtime-sensitive (for example weapon damage by
     range), while others are just data-shaped configuration.
   - Mitigation: Phase 5 narrows bounded/static cases first and leaves
     genuinely dynamic formulas for a later project if needed.

### Opportunities Discovered

- One shared validation helper can cover startup, design tools, and on-demand
  loaders with one contract surface.
- A typed registrar pattern for abilities can remove one of the most visible
  manual maps without forcing a whole-object-model rewrite.
- Better validation at load boundaries should reduce the amount of downstream
  defensive code and shrink the need for later cleanup projects.

## Phase Rationale

### Phase 1
Create the exact content/loader inventory first so the project does not
accidentally hard-fail a path that is currently allowed to warn-and-continue.

### Phase 2
Land schema assets and a shared helper before touching startup or runtime
behavior. This keeps the first code change narrow and testable.

### Phase 3
Thread the new helper through real load paths only after the contracts exist and
the failure semantics are decided.

### Phase 4
Move high-churn registry surfaces and normalization logic toward typed registrars
and intermediate models after validation is already working.

### Phase 5
Reduce the formula surface only after the loader and registrar work is in place,
so formula removal does not get mixed up with the earlier contract changes.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
