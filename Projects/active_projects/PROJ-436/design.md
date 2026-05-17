# PROJ-436: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source

This design distills the converged charter from two artifacts. Read them before implementing any phase.

- Inter-agent discussion outcome: [AgentCoordination/Scratchpad/Discussion/20260517T230029Z_post-435-project-creation/](../../../AgentCoordination/Scratchpad/Discussion/20260517T230029Z_post-435-project-creation/) — Claude+Codex converged plan, especially `plans/post_435_project_set_r001.md`.
- User-confirmed design sketch: [AgentCoordination/Scratchpad/reports/unified_container_design_sketch.md](../../../AgentCoordination/Scratchpad/reports/unified_container_design_sketch.md) — the 12-question Q&A that resolved A2, mass-per-unit, life support / launch / production separation, and per-species population semantics.

## Initial Analysis

### Audit at project-creation time (2026-05-17)

**Current storage abilities — three competing abstractions:**
- `ResourceStorage` ([game/simulation/components/abilities/resources.py:157](../../../game/simulation/components/abilities/resources.py#L157)) — `{resource, amount}`, single resource, count-based.
- `CargoStorage` ([game/simulation/components/abilities/cargo.py:14](../../../game/simulation/components/abilities/cargo.py#L14)) — `{cargo_type, capacity}`, single cargo type, count-based.
- `VehicleBay` (in `data/components.json:4184-4279`) — `{capacity_mass, allowed_types}`, multi-type allowed, **mass-based**.

`VehicleBay` is already the shape the unified `Container` wants. The other two converge onto it.

**Current entity-level storage fields — eight surfaces:**
- `Planet.stockpile`, `Planet.max_stockpile`, `Planet.staging_yard` ([game/strategy/data/planet.py:79-81](../../../game/strategy/data/planet.py#L79-L81)).
- `Planet.populations: List[SpeciesPopulation]` ([game/strategy/data/planet.py:84](../../../game/strategy/data/planet.py#L84)) — typed, multi-species ready.
- `ShipInstance.cargo_contents: Dict[str, int]` — counts.
- `ShipInstance.consumable_levels: Dict[str, float]` — onboard fuel/energy/ammo.
- `ShipInstance.bay_inventory: BayInventory` — typed + mass-based (PROJ-431 substrate, pods + vehicles only today).
- `Empire._fleet_resource_pool: Dict[str, float]` ([game/strategy/data/empire.py:58-60](../../../game/strategy/data/empire.py#L58-L60)) — self-flagged "temporary storage for fleet construction until Phase 6 (fleet cargo)".
- `Empire.resource_pool` (property at [empire.py:227](../../../game/strategy/data/empire.py#L227)) — read-only aggregate.
- `PlanetaryFacility.consumable_levels` ([planetary_facility.py:32](../../../game/strategy/data/planetary_facility.py#L32)) — separate facility storage.

**Validation surfaces:**
- `TransferValidator.VALID_CARGO_TYPES` ([transfer_validator.py:17](../../../game/strategy/validation/transfer_validator.py#L17)) — hardcoded whitelist.
- `transfer_view_model.RESOURCE_TYPES` ([transfer_view_model.py:26](../../../game/ui/screens/transfer_view_model.py#L26)) — hardcoded ordered list.

**Routing branches:**
- `ProductionEngine.context_type` reads at lines 516, 549, 606 of `game/strategy/engine/production_engine.py`.
- Build-queue UI `context_type` reads at [build_queue_controller.py:483-513](../../../game/ui/panels/build_queue_controller.py#L483-L513).

**Protocol surface to consolidate:**
- `IEmpire.resource_pool` / `IEmpire.max_storage` at [strategy_domain.py:64-72](../../../game/core/protocols/strategy_domain.py#L64-L72).
- `IStockpileHolder` / `IStagingYardHolder` at [galaxy_protocols.py:130-180](../../../game/strategy/data/galaxy_protocols.py#L130-L180).

**Existing canonical resource catalog (Core layer):**
- `game/core/resources.py:ResourceCatalog` + `ResourceDefinition` (frozen dataclass: `id`, `name`, `description`, `display_group`, `has_quality`). Loaded once from `data/resources.json` (existing canonical file with 8 entries: metals / organics / vapors / radioactives / exotics / fuel / energy / ammo). The catalog is documented as "the single source of truth for what resources exist in the game" — both planetary materials and operational consumables are defined here. **The mass-per-unit field extends THIS catalog; no parallel strategy-local registry is introduced.**

**Test gate cleared:** 21132 tests, 0 failed, 0 errors, 0 skipped at 2026-05-17 baseline (sharded suite, 85.9s wall time).

## Architecture

### Target data model

```
ContainableKind = enum(RESOURCE, ITEM, POPULATION)

Containable (abstract):
  kind: ContainableKind
  type_id: str         # "metals" | "fighter_design_42" | "human"
  mass_per_unit: float # resolved from ResourceCatalog (Core) for resources, design metadata for items, species/race JSON for population

ContainerPolicy:
  allowed_kinds: Set[ContainableKind]
  allowed_type_ids: Optional[Set[str]]   # None = any type_id in allowed_kinds

Container:
  capacity_mass: float
  policy: ContainerPolicy
  resources: Dict[str, float]     # resource_id -> amount (continuous)
  items: List[ItemRef]            # discrete + identity preserved
  population: Dict[str, int]      # species_id -> count

  mass_used = sum across all three slices, each multiplied by mass_per_unit
  mass_remaining = capacity_mass - mass_used

  accepts(c) -> bool                       # policy check
  add(c, quantity) -> AddResult            # policy + mass validation, then mutate
  remove(c, quantity) -> RemoveResult
  contents() -> Iterable[ContainerEntry]   # unified read view
```

### Single component ability

```
"Container": {
  "capacity_mass": 250,
  "allowed_kinds": ["ITEM"],
  "allowed_type_ids": ["mine", "fighter", "satellite"]
}
```

Replaces `ResourceStorage`, `CargoStorage`, `VehicleBay`. Legacy parsers in Phase 1 compile to this shape internally so existing data files keep loading until they're migrated in their own pass.

### Direction rule for the substrate-then-sweep migration

Per the converged checkpoint rule from [blank_sheet_remediation_r003.md](../../../AgentCoordination/Scratchpad/Discussion/20260517T150720Z_strategy-layer-blank-sheet/plans/blank_sheet_remediation_r003.md):

- During a sweep, the new `Container` is a projection over the legacy field. The legacy field remains the durable representation until the final cutover commit, at which point it is deleted and the new substrate becomes durable.
- This is the **default** direction for high-fanout storage sweeps, not a universal law. Each phase picks the direction in its checklist.

### Phase blast-radius (estimated, audit-validated where possible)

| Phase | Estimated callers / files |
|---|---|
| 0 (substrate) | new files; no callers migrated |
| 1 (ability parser) | data file changes deferred; ~5-10 abilities-registry / component-definitions test files |
| 2 (BayInventory widening) | PROJ-431 audit: 6 launch/recover handlers + MineGroupService + ~10 test files |
| 3 (ship cargo/consumables) | ShipCargoManager, ShipConsumableManager, ShipInstanceBridge, ShipDisplayFormatter, serializer, plus their tests — likely 25-40 files |
| 4 (planet stockpile/staging) | Planet methods at planet.py:198-244 have ~20 caller sites; planet integration tests; production_engine reads |
| 5 (empire pool) | empire.py:226-292 methods plus build-queue projector + treasury panel + economy calculator — likely 10-15 files |
| 6 (protocol churn) | every implementer of `IEmpire` / `IStockpileHolder` / `IStagingYardHolder` plus the build-queue UI controller — likely 8-12 files |
| 7 (transfer validator + UI list) | transfer_validator + transfer_view_model + transfer_dialog + transfer_branches + ~15 test files |
| 8 (production engine context_type) | production_engine.py only, plus its tests |
| 9 (_CarriedItemsProxy) | ship_instance.py production cut + test fixture sweep (PROJ-431 phase 1f audit estimated ~51 test files) |
| 10 (docs) | 4-6 doc files |
| 11 (consult) | TBD per findings |

### Key patterns to reuse

- **Substrate-then-sweep-then-delete** ([PROJ-431/decisions.md:2026-05-17](../../../Projects/active_projects/PROJ-431/decisions.md)) — every phase 2-9 migration uses sub-phases (1a, 1b, …) per the PROJ-431 1a-1f template. Each sub-phase is a separate commit + tests + grep gate.
- **AST guard test for legacy substrate** ([tests/unit/strategy/data/test_phase_1f_deletion_guard.py](../../../tests/unit/strategy/data/test_phase_1f_deletion_guard.py)) — Phase 9 pattern; static assertion that a deleted field/proxy stays deleted.
- **Typed projection over legacy storage** (`ShipInstance.bay_inventory` was added as a projection over `carried_items` in PROJ-431 phase 1 before the field deletion in 1f). The same pattern applies to every storage migration here.
- **Single dispatch through data-driven policy** (`VehicleBay.allowed_types` is the seed) — `ContainerPolicy.allowed_kinds` + `allowed_type_ids` replaces every hardcoded type-check in the storage layer.
- **End-of-project Codex consult** ([Projects/active_projects/PROJ-431/plan.md "Phase 5"](../../../Projects/active_projects/PROJ-431/plan.md)) — Phase 11 pattern; verified findings become added phases.

## Dependencies & Risks

### Hard dependencies

- **None.** PROJ-422..PROJ-435 prerequisite tranche is complete per `Projects/active_projects/PROJ-435/findings/Completion Repot`. Baseline 21132/21132 green.

### Soft dependencies

- **PROJ-437 starts after PROJ-436 Phase 7** (TransferValidator deletion → unified `Container.accepts()` API stable).

### Risks

1. **Test blast radius for `_CarriedItemsProxy` deletion** (Phase 9). PROJ-431 estimated 51 test files still poke `ship.carried_items` directly. Phase 9 needs to enumerate + rewrite these. Mitigation: run a comprehensive grep audit at Phase 9 task 1, scope the work, decompose into sub-phases.

2. **`Empire.resource_pool` query cost at scale** (Phase 5 D2). Pure-query default may be slow on large empires. Mitigation: profile at Phase 5 close; if hot, add caching with explicit invalidation per PROJ-293 pattern.

3. **`PlanetaryFacility.consumable_levels` model decision** (Phase 0 D1). Default (b) keep as internal state; if Phase 4 discovers a transfer flow that needs (a), Phase 4 reverts the default — adds work mid-project.

4. **Component data file migration** (data/components.json). The 3 legacy abilities live in data. Phase 1 keeps legacy parsers working, but at some point components.json should be rewritten to native `Container` shape. Decision: defer the data-file rewrite to a post-project hygiene task; do NOT block Phase 7 / Phase 8 on it. Legacy parsers stay until a separate clean-up.

5. **Static guard tests may need updating** as storage moves. Existing guards in `tests/static_guards/test_facade_bypass_guard.py` (661 tests) and similar may catch new container-pattern moves that look like bypass. Mitigation: audit guard tests at Phase 6 close.

6. **Save format breaks at the end of the project.** Per CLAUDE.md, no migration shim. After Phase 9, old saves predating PROJ-436 do not load. User has confirmed this is acceptable (`feedback_no_bandaids.md` + the CLAUDE.md disposability rule).

## Opportunities Discovered

- **`VehicleBay` is the spec answer.** Phase 1's "compile legacy parsers to Container internally" lets us delete `VehicleBay` cleanly because the runtime shape is already what we want.
- **`BayInventory` (PROJ-431) is the runtime answer.** Phase 2 widening is mostly additive — three-slice extends a class that already does the right thing.
- **`SpeciesPopulation` (planet.py:84) is the population slice answer.** Phase 0 / Phase 3 population work can lean on it.
- **PROJ-431 sub-phase model is the migration answer.** Sub-phases 1a-1f gave the team a working template — every phase 2-9 here can use the same shape.
- **`ResourceCatalog` is the mass-per-unit answer.** The existing Core-layer catalog already loads `data/resources.json` and is the single source of truth for resource metadata. Phase 0 extends it with `mass_per_unit` rather than creating a parallel strategy-local registry. Strategy and UI layers consume mass-per-unit through the existing public API — no new import path, no parallel cache invalidation surface, no duplicated definitional metadata.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
