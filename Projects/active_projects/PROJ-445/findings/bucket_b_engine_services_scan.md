# Bucket B — Engine + Services Residue Scan (2026-05-18)

## Summary
- Total findings: 22
- By severity: high 2, medium 8, low 12
- By category: obsolete-code 4, test-inconsistency 3, missing-functionality 2, polish 13
- Files reviewed: ~50 (all `game/strategy/engine/**/*.py` + `game/strategy/services/**/*.py`, plus targeted tests under `tests/unit/strategy/engine/` + `tests/unit/strategy/services/`)
- Archived/active project decisions.md / findings_ledger.md scanned: PROJ-422 / PROJ-423 / PROJ-425 / PROJ-427 / PROJ-429 / PROJ-431 / PROJ-432 / PROJ-433 / PROJ-434 / PROJ-435 / PROJ-FMS-A / PROJ-FMS-B / PROJ-FMS-C / PROJ-FMS-D / PROJ-329A / PROJ-353A / PROJ-354A / PROJ-354B (archived); PROJ-436 / PROJ-437 / PROJ-438 (active).

Deduplicated against the 9 entries in `AgentCoordination/discovered_issues/log.jsonl` — the already-logged `ActionExecutionEngine._process_planet_action_tick` coverage gap, `CommandRegistry.serializer_codec_for` first-match ambiguity, `TransferBranches._dispatch_fleet_to_fleet` silent no-op for drop_pod/vehicle, `Container.remove` negative-quantity gap, `Fleet.has_cargo_resources` round-mismatch, and `ProductionEngine._apply_resource_consumption` ignore-bool finding are NOT refiled below.

## Findings

### F-B-001 — `LayMinesOrderHandler.execute_for_issuer` is missing the `registries` kwarg the planet-FMS dispatch passes
- **Severity**: high
- **Category**: obsolete-code (signature drift from the PROJ-438 Phase 6 unified contract)
- **File**: `game/strategy/engine/order_handlers/lay_mines.py:184`
- **Symbol**: `LayMinesOrderHandler.execute_for_issuer`
- **Source refactor**: PROJ-438 Phase 6 (unified 5-kwarg signature) + PROJ-FMS-B (handler)
- **What survived**: The `IOrderHandler` Protocol declares `execute_for_issuer(*, issuer, order_owner, empire, galaxy=None, registries=None)` (base.py:83-91). All four sibling handlers (`launch_fighters`, `launch_satellites`, `recover_fighters`, `recover_satellites`) implement the full 5-kwarg signature. `lay_mines.py:184-191` declares only 4 kwargs (no `registries`). `ActionExecutionEngine._execute_planet_action` (action_execution_engine.py:323-329) unconditionally passes `registries=getattr(empire, "_registries", None)`. The CommandSpec at `handlers/lay_mines.py:40` declares `subcategories=frozenset({"planet_fms"})`, so `planet_fms_action_order_types` includes `LAY_MINES` and the engine-mediated planet path dispatches into this handler.
- **Why it's a problem**: A planet-issued `LAY_MINES` order ticked through `ActionExecutionEngine._process_planet_action_tick → _execute_planet_action → handler.execute_for_issuer(..., registries=...)` will raise `TypeError: execute_for_issuer() got an unexpected keyword argument 'registries'`. There is no behavioural test that drives this path (the discovered-issues log entry DI-2026-05-18-001 already notes the broader planet-FMS coverage gap — but lay_mines specifically isn't even unit-tested under planet-issuer dispatch with the registries kwarg). The PROJ-438 Phase 6 retirement of the `try/except TypeError` reach-in fallback in `_execute_planet_action` made this a hard failure rather than a silent skip.
- **Suggested action**: Add `registries: Any = None` to the kwarg list at `lay_mines.py:184-191` and accept-and-ignore (mirror `recover_fighters.py:90-98` exactly). Add a planet-LAY_MINES dispatch test alongside the Phase 10 deferred work in the existing DI-2026-05-18-001 entry.
- **Effort**: tiny

### F-B-002 — `transfer_branches._dispatch_load_planet_drop_pod` direct-mutates `planet.staging_yard.append` on rollback
- **Severity**: medium
- **Category**: obsolete-code (direct list mutation bypassing the public `add_to_staging_yard` capacity-check API)
- **File**: `game/strategy/engine/order_handlers/transfer_branches.py:365`
- **Symbol**: `TransferBranches._dispatch_load_carried_vehicle` (in the `planet.staging_yard.append(removed)` restore path)
- **Source refactor**: PROJ-425 (transfer handler lift) — the verbatim `_execute_fleet_transfer` carry-over preserved the direct-mutation seam
- **What survived**: The rollback branch when a carried-vehicle load fails after `remove_from_staging_yard` succeeded falls back to `planet.staging_yard.append(removed)` — a raw list mutation. Everywhere else in the file (`production_spawner.py:362`, `transfer_branches.py:398`, `transfer_branches.py:446`, plus `issuer_adapter.py:356,363`) routes additions through `planet.add_to_staging_yard(item)` which respects mass capacity. The raw append silently bypasses the capacity gate that PROJ-372 / PROJ-436 codified.
- **Why it's a problem**: A restore-after-failure path can push the staging yard over its declared capacity. The only reason this hasn't been observed is that the carried-vehicle load failure branch is rarely hit; the moment a `target_ship._cargo_mgr.load_vehicle(cv)` returns False after a successful planet-side `remove_from_staging_yard`, capacity invariants drift.
- **Suggested action**: Replace `planet.staging_yard.append(removed)` at transfer_branches.py:365 with `planet.add_to_staging_yard(removed)`. The restore is best-effort anyway; if capacity is now insufficient, log and continue rather than corrupt the invariant.
- **Effort**: tiny

### F-B-003 — `TransferBranches._dispatch_load_carried_vehicle` reaches into `ship._cargo_mgr` private slot
- **Severity**: low
- **Category**: obsolete-code (private-slot access from outside the `ShipInstance` facade)
- **File**: `game/strategy/engine/order_handlers/transfer_branches.py:224-226, 355, 361, 389, 399`
- **Symbol**: `TransferBranches._dispatch_load_carried_vehicle`, `_dispatch_unload_carried_vehicle`
- **Source refactor**: PROJ-425 (lifted verbatim from legacy `_execute_fleet_transfer`)
- **What survived**: Six direct `ship._cargo_mgr.{get_pod_storage_capacity,get_pod_storage_used,can_carry_pod,can_accept_vehicle,load_vehicle,get_carried_vehicles,unload_vehicle}` calls. `ShipInstance` exposes public delegators for the load/unload operations; the cargo manager is supposed to be an internal collaborator post-PROJ-425. No other file under `game/strategy/engine/` or `game/strategy/services/` touches `ship._cargo_mgr` (grep verified).
- **Why it's a problem**: Hardens a private boundary as a de-facto public contract; the day `ShipInstance` migrates its cargo storage path (the PROJ-436 storage-substrate unification has already moved everything else), these reaches break out of the regular facade migration sweep and need a separate fix-up.
- **Suggested action**: Add public `ship.can_carry_pod(mass)`, `ship.load_vehicle(cv)`, `ship.unload_vehicle(idx)` delegators on `ShipInstance` (most already exist as `_cargo_mgr` is the storage delegate); switch transfer_branches.py call sites to the public surface.
- **Effort**: small

### F-B-004 — `effect_ability_metadata.py` shim is still in place after PROJ-429 (decisions.md flagged the collapse as a follow-up)
- **Severity**: low
- **Category**: obsolete-code (intentional deferred-shim per PROJ-429 decisions.md row 2)
- **File**: `game/strategy/services/effect_ability_metadata.py:1-131`
- **Symbol**: module-level (`EffectAbilityMetadata`, `EFFECT_ABILITY_METADATA`, `find_metadata`, `is_known_effect_ability`, `all_owner_aware_scopes`)
- **Source refactor**: PROJ-429 (unified `AbilityMetadataRegistry`) — explicitly deferred
- **What survived**: The file's own header documents the deferral: "Collapsing this shim is intentionally OUT of scope for PROJ-429 (decisions.md row 2). The shim isolates the migration; a follow-up project will collapse it once all downstream callers are ready to migrate to the unified registry directly." Live consumers: `system_effects_collector.py:42-45` (`find_metadata`, `is_known_effect_ability`), `effect_ability_display.py` (transitive). Equivalent symbols already exist on `ability_metadata.py`.
- **Why it's a problem**: It's deferred dead-on-arrival code — 131 LOC of pure delegation. Every change to the underlying registry has to be mirrored across two surfaces. Forward-friction is real because callers can't tell which is "current".
- **Suggested action**: Sweep the two callers (`system_effects_collector.py`, `effect_ability_display.py`) to import directly from `ability_metadata.py`; delete `effect_ability_metadata.py`. Move the `_OWNER_AWARE_SCOPES` constant inline at its single use-site or to `ability_metadata.py`.
- **Effort**: small

### F-B-005 — `component_inspector.py` re-export shim survives PROJ-433 split
- **Severity**: low
- **Category**: obsolete-code (intentional re-export shim — but unbounded in time)
- **File**: `game/strategy/services/component_inspector.py:1-67`
- **Symbol**: module-level re-exports
- **Source refactor**: PROJ-433 (file-split for 500-LOC ceiling)
- **What survived**: The full 67-line module is a re-export of names from `component_abilities` + `component_layers`. The header explicitly states "preserved as a thin re-export so the ~50 existing `from game.strategy.services.component_inspector import X` call sites across engines, UI, validators, and tests keep working unchanged."
- **Why it's a problem**: ~50 production + test imports still route through the shim rather than the canonical modules. Each round of new feature work that touches one of these callers is the natural moment to migrate the import — but the shim keeps the bypass alive indefinitely.
- **Suggested action**: One mechanical sweep — `from game.strategy.services.component_inspector import` → `from game.strategy.services.component_abilities import` (Surface A names) or `from game.strategy.services.component_layers import` (Surface B names). Then delete `component_inspector.py`.
- **Effort**: small

### F-B-006 — `SuperweaponOrderProcessor._get_system_at_hex` has `# type: ignore[no-untyped-def]` masking a missing annotation
- **Severity**: low
- **Category**: polish
- **File**: `game/strategy/engine/superweapon_order_processor.py:343`
- **Symbol**: `SuperweaponOrderProcessor._get_system_at_hex`
- **Source refactor**: PROJ-414 (the previous shim deletion left this internal method untyped)
- **What survived**: `def _get_system_at_hex(galaxy, location):  # type: ignore[no-untyped-def]` — a `type: ignore` comment is used to silence a missing-annotation warning rather than adding the annotation.
- **Why it's a problem**: `type: ignore` comments are a maintenance smell — they linger past the underlying issue and obscure real type problems.
- **Suggested action**: Add the annotations: `def _get_system_at_hex(galaxy: Any, location: HexCoord) -> Optional["StarSystem"]:` (matching `GalaxyPathfindingService.get_system_at_hex`). Drop the `type: ignore`.
- **Effort**: tiny

### F-B-007 — `OrderProcessor.__init__` missing return annotation and `event_bus` parameter has no type annotation
- **Severity**: low
- **Category**: polish (convention violation — public `__init__` is exempt per the dunder rule, but `event_bus` should be typed)
- **File**: `game/strategy/engine/order_processor.py:64`
- **Symbol**: `OrderProcessor.__init__`
- **Source refactor**: PROJ-368 (facade introduction)
- **What survived**: `def __init__(self, event_bus=None):` — no annotation on `event_bus`. (Dunder return is exempt; the parameter annotation is the actual gap.)
- **Why it's a problem**: Minor consistency gap; every other engine `__init__` in the layer types its event_bus parameter (e.g., `SuperweaponOrderProcessor.__init__` has the same issue at superweapon_order_processor.py:56).
- **Suggested action**: `def __init__(self, event_bus: Optional[Any] = None) -> None:` (matches the kwarg-default pattern used by `BaseOrderHandler.__init__`).
- **Effort**: tiny

### F-B-008 — `SuperweaponOrderProcessor.__init__` missing parameter and return annotations
- **Severity**: low
- **Category**: polish
- **File**: `game/strategy/engine/superweapon_order_processor.py:56`
- **Symbol**: `SuperweaponOrderProcessor.__init__`
- **Source refactor**: none — original signature carried forward
- **What survived**: `def __init__(self, event_bus=None, empire_mutator=None, nav_service=None):` — all three parameters are untyped.
- **Why it's a problem**: Same as F-B-007; layer convention violation.
- **Suggested action**: Add `Optional[Any]` annotations and `-> None` return.
- **Effort**: tiny

### F-B-009 — `resolve_requested` module-level helper missing return annotation
- **Severity**: low
- **Category**: polish (convention violation — public module-level function)
- **File**: `game/strategy/engine/handlers/fms_shared.py:94`
- **Symbol**: `resolve_requested`
- **Source refactor**: PROJ-FMS-shared
- **What survived**: `def resolve_requested(count, count_available: int):` — no return type, `count` parameter untyped. The docstring says it returns "either an `int` (resolved count) or a `ValidationResult`" — exactly the case where a `int | ValidationResult` union annotation should be required by the CLAUDE.md "Public functions and methods require return-type annotations" rule.
- **Why it's a problem**: The function is in `__all__` so it's public surface. Callers can't statically reason about whether they got an error result or a count.
- **Suggested action**: `def resolve_requested(count: Optional[int], count_available: int) -> int | ValidationResult:`.
- **Effort**: tiny

### F-B-010 — `TurnEngine.planet_modifier_effect_engine` property missing return annotation
- **Severity**: low
- **Category**: polish
- **File**: `game/strategy/engine/turn_engine.py:521`
- **Symbol**: `TurnEngine.planet_modifier_effect_engine` (property)
- **Source refactor**: PROJ-428 Phase 1 (TD-04 lazy-property addition)
- **What survived**: `def planet_modifier_effect_engine(self):` — public property, no return annotation. Sibling `TurnEngine.water_engine` at line 516 has the annotation; this one was missed.
- **Why it's a problem**: Convention violation; symmetry break with other engine properties.
- **Suggested action**: `def planet_modifier_effect_engine(self) -> "PlanetModifierEffectEngine":`.
- **Effort**: tiny

### F-B-011 — Two `_get_planet_mutator` accessors missing return annotations
- **Severity**: low
- **Category**: polish
- **File**: `game/strategy/engine/harvesting_engine.py:196`, `game/strategy/engine/atmosphere_engine.py:30`, `game/strategy/engine/planet_modifier_effect_engine.py:34`, `game/strategy/engine/production_spawner.py:101`
- **Symbol**: `_get_planet_mutator`, `_get_empire_mutator`, `_get_ship_mutator` (private accessors across multiple engines)
- **Source refactor**: PROJ-370 / PROJ-382 (mutator lazy-default pattern)
- **What survived**: Six private accessors of the form `def _get_planet_mutator(self):` with no return annotation. Strictly speaking the CLAUDE.md rule says public — but these all return a known protocol type, the annotation is trivial, and the typed sibling pattern (e.g., `BaseOrderHandler._get_planet_mutator` at `order_handlers/base.py:137` — uses `-> Any`) already exists.
- **Why it's a problem**: Mild consistency gap. Listed for completeness; lower priority than F-B-007 - F-B-010.
- **Suggested action**: Annotate as `-> Any` (matches `BaseOrderHandler._get_planet_mutator`) or with the concrete write-service type.
- **Effort**: tiny

### F-B-012 — `test_superweapon_registry_contract.py` has two unreachable `pytest.skip` clauses
- **Severity**: low
- **Category**: test-inconsistency (dead skip clauses on a module that always imports)
- **File**: `tests/unit/strategy/services/test_superweapon_registry_contract.py:154, 178`
- **Symbol**: `TestSuperweaponRegistryVsCommandSpecs.test_order_types_match_command_specs` and `test_ability_names_match_command_specs`
- **Source refactor**: PROJ-371 (command_registry introduction)
- **What survived**: Both tests open with `try: from game.strategy.engine.commands.registry import command_registry, seed_default_commands` then `except ImportError: pytest.skip("PROJ-371 command_registry not available")`. The module is in the live tree (it's verified by `tests/unit/strategy/engine/test_command_specs_contract.py` and many others); the import cannot raise `ImportError` today.
- **Why it's a problem**: Dead defensive code. If the test ever appears to skip on CI, future readers will conclude PROJ-371 surface is conditional when it's not. Worse — if the import path ever does break legitimately (typo, rename), the `pytest.skip` silently turns a hard failure into a green pass.
- **Suggested action**: Remove both `try / except ImportError` guards and the inner skip; let the top-level import fail loudly if the module ever disappears.
- **Effort**: tiny

### F-B-013 — `transfer_branches.py` flattens typed `DropPod` back to dict at the staging-yard boundary because "staging yard still consumes legacy dict shape" [JOINT-PHASE with PROJ-444]
- **Severity**: low-medium (tech debt, not user-facing functional risk today)
- **Category**: obsolete-code (typed `DropPod` substrate adoption is partial — boundary still dict)
- **File**: `game/strategy/engine/order_handlers/transfer_branches.py:416-446` (call sites); `game/strategy/data/planet.py:98, 253-262, 316-322` (substrate)
- **Symbol**: `TransferBranches._dispatch_drop_pod_unload` + `Planet._staging_yard` / `Planet.add_to_staging_yard`
- **Source refactor**: PROJ-431 Phase 1d (typed `DropPod` in `bay_inventory.pods`) — staging-yard half deferred
- **What survived**: The docstring at line 412-417 explicitly says "The planet staging yard still consumes legacy dict shape, so the typed `DropPod` is flattened to a dict at the boundary." Same pattern at production_spawner.py:358 ("Drop pods retain their legacy dict shape"). The staging-yard substrate is `Planet._staging_yard: List[Dict[str, Any]]` (in PROJ-444's data layer) while every other carried-vehicle storage uses typed `CarriedVehicle` / `DropPod`. The flatten/inflate round-trip is in `transfer_branches._staging_yard_carried_vehicle` (line 56-77).
- **Why it's a problem**: Inconsistent substrate forces a typed-to-dict-to-typed round-trip every time a pod crosses the boundary. Tech-debt risks: field drift between the typed dataclass and the dict payload schema; missing `mass` field if a pod is added through one path and read through another; the `_is_carried_vehicle_dict` runtime probe at line 213 / 348 is the kind of shape-discrimination the PROJ-431 work was designed to retire on the typed slots. No active drift bug observed today (Codex consult 2026-05-18 — recategorized from "missing-functionality" to "obsolete-code" tech debt accordingly).
- **Suggested action**: Add a typed `Planet._staging_yard: List[CarriedVehicle | DropPod]` slot (or migrate the existing list to typed entries with a one-shot save-data normalization). Drop the `_staging_yard_carried_vehicle` probe and the `pod.payload`/`pod.design_data`/`pod.mass` flatten block at transfer_branches.py:440-446 and production_spawner.py:358-360.
- **Effort**: medium
- **CROSS-BUCKET CLASSIFICATION**: STRUCTURAL JOINT-PHASE, not mere coordination. The root-cause field rename + serializer migration lives in PROJ-444 (`game/strategy/data/planet.py`); the engine-side call-site adoption lives here. **This finding requires a stacked PR (or one PR spanning both bucket file sets) and must NOT be attempted independently from either side.** Codex consult 2026-05-18 flagged the original "coordination point" framing as understating the seam.

### F-B-014 — `SuperweaponHandlers.close_warp_point` accepts pre-PROJ-228 plain-string target via legacy back-compat passthrough
- **Severity**: low
- **Category**: obsolete-code (legacy passthrough explicitly named in comments)
- **File**: `game/strategy/engine/superweapon_handlers/close_warp_point.py:29-43`, `game/strategy/engine/superweapon_order_processor.py:218-228`
- **Symbol**: `_parse_close_target`, `SuperweaponOrderProcessor._run_spec_pipeline` (CLOSE_WARP_POINT branch)
- **Source refactor**: PROJ-228 (typed warp-point target dict) — back-compat preserved
- **What survived**: The plain-string form is the pre-PROJ-228 shape; the new dict form is `{destination_id, target_hex}`. Two sites preserve the legacy passthrough: `_parse_close_target` accepts either; `superweapon_order_processor.py:218-228` has a special-case branch (`if spec.order_type == OrderType.CLOSE_WARP_POINT: pass`) inside the `not isinstance(order.target, dict)` guard so a string target bypasses the OPEN_WARP_POINT-style rejection.
- **Why it's a problem**: Forks the input contract; every reader and every test has to consider both shapes; new validations can drift between the dict path (with `target_hex` sector check at lines 77-89) and the string path (no sector check).
- **Suggested action**: Audit `IssueCloseWarpPointCommand` / `Order.to_dict` / save-load round-trip for any remaining sources that still emit the plain string. If none today, delete the string branch from `_parse_close_target`, the special-case at superweapon_order_processor.py:222, and the legacy comment block. Save-migration is unnecessary per CLAUDE.md "Old saves are disposable."
- **Effort**: small

### F-B-015 — `ProductionEngine` IProductionResourceSource docstring mentions "Fleet over its `_cargo_contents` substrate"; substrate was retired in PROJ-436 Phase 3
- **Severity**: low
- **Category**: polish (stale docstring referencing retired surface)
- **File**: `game/strategy/engine/production_engine.py:68`
- **Symbol**: `IProductionResourceSource.production_consume_resource` (docstring)
- **Source refactor**: PROJ-436 Phase 3 (`cargo_contents` → typed cargo manager) — docstring not updated
- **What survived**: Docstring reads "integer-typed sources (e.g. `Fleet` over its `_cargo_contents` substrate) MAY round the requested `amount` before consumption." `_cargo_contents` is the pre-PROJ-436 name; current code uses the `ShipCargoManager` API per PROJ-436 Phase 3.
- **Why it's a problem**: Stale name in protocol docstring; future readers searching for `_cargo_contents` won't find it in code. Same with `production_engine.py:68` (referenced from the discovered-issues log's existing entry context but worth pinning).
- **Suggested action**: Replace "`Fleet` over its `_cargo_contents` substrate" with "`Fleet` over its typed cargo manager (`ShipCargoManager`)" — one-word edit.
- **Effort**: tiny

### F-B-016 — `conflict_modifier_collection.lookup_environmental_effects` docstring says "Phase 7 deletes the legacy path" — Phase 7 has shipped
- **Severity**: low
- **Category**: polish (stale docstring promising future cleanup that has already happened)
- **File**: `game/strategy/engine/conflict_modifier_collection.py:28-31`
- **Symbol**: `lookup_environmental_effects`
- **Source refactor**: PROJ-300 Phase 7 (legacy `EnvironmentalEffects` path deleted)
- **What survived**: Docstring still says "The spec compiler accepts either the legacy EnvironmentalEffects object (effective during AreaEffectManager deprecation) or this new list. Phase 7 deletes the legacy path." Grep confirms `EnvironmentalEffects` is no longer used anywhere in the strategy layer except `fleet_speed_calculator.py:175` (also a stale docstring reference). PROJ-300 Phase 7 is closed.
- **Why it's a problem**: Docstring lies about the current state — implies the spec compiler still accepts both shapes when it doesn't.
- **Suggested action**: Drop the "either / or" phrasing; state that the function returns a sector-effects list from `collect_sector_effects`. Also clean up the parallel reference at `fleet_speed_calculator.py:175`.
- **Effort**: tiny

### F-B-017 — `OrderProcessor` facade still reshapes `OrderExecutionResult` back into pre-PROJ-368 legacy typed result dataclasses
- **Severity**: medium
- **Category**: obsolete-code (facade-side legacy result reshape blocking the Protocol unification from completing)
- **File**: `game/strategy/engine/order_handlers/base.py:36-56`, `game/strategy/engine/order_processor.py:97-143`
- **Symbol**: `OrderProcessor.process_join_fleet` / `process_colonize` / `process_transfer` + the legacy result types `JoinFleetResult` / `ColonizeResult` / `TransferResult`
- **Source refactor**: PROJ-368 (facade), PROJ-438 Phase 6 (unified `execute_for_issuer` — but the `execute_action_order` facade reshape was left as-is)
- **What survived**: The concrete handler signatures themselves are NOT mismatched — `JoinFleetHandler.execute_action_order` at `join_fleet.py:50-57`, `ColonizeHandler.execute_action_order` at `colonize.py:45-52`, and `TransferHandler.execute_action_order` at `transfer.py:64-71` all already accept the full 5-kwarg shape with defaults (verified by Codex consult 2026-05-18). What DOES survive is the facade-side reshape: `OrderProcessor.process_join_fleet/process_colonize/process_transfer` still wrap `OrderExecutionResult` back into `JoinFleetResult` / `ColonizeResult` / `TransferResult` for legacy callers, and `OrderExecutionResult` at `base.py:36-56` still carries the five per-handler "legacy fields" (`merged`, `cancelled`, `colonized`, `planet_name`, `amount_transferred`) explicitly to support that reshape.
- **Why it's a problem**: The Protocol unification is half-finished at the facade boundary. The handlers are already on the unified contract, but the facade still hand-rebuilds the pre-PROJ-368 typed dataclasses for external callers. Same survival pattern PROJ-438 Phase 6 cleaned up for `execute_for_issuer` is still present here for `execute_action_order` callers.
- **Suggested action**: Audit characterization callers (per the PROJ-333 comment at `order_processor.py:14-19`); migrate them to read `OrderExecutionResult` directly; then drop `JoinFleetResult` / `ColonizeResult` / `TransferResult` and the `process_join_fleet` / `process_colonize` / `process_transfer` facade methods. F-B-018 follows naturally once this lands.
- **Effort**: medium
- **Codex verification (2026-05-18)**: The original framing claimed handler signatures themselves were inconsistent; Codex traced the three concrete handlers and confirmed they already match the Protocol. Rewritten above to reflect the actual residue (facade-side reshape, not handler-side mismatch).

### F-B-018 — `OrderExecutionResult` carries 5 "legacy field" attributes documented as facade-reshape compensation
- **Severity**: low
- **Category**: obsolete-code (follow-on cleanup blocked by F-B-017)
- **File**: `game/strategy/engine/order_handlers/base.py:46-55`
- **Symbol**: `OrderExecutionResult` (fields `merged`, `cancelled`, `colonized`, `planet_name`, `amount_transferred`)
- **Source refactor**: PROJ-368
- **What survived**: Five per-handler "extras" on a unified result type so the facade can re-cast to legacy types. Inline comments explicitly label them: `# JoinFleet legacy field`, `# Colonize legacy field`, `# Transfer legacy field`.
- **Why it's a problem**: Couples the shared result type to specific handler outputs; new handlers can't follow the pattern cleanly. Untangle is blocked by F-B-017 — but worth tracking separately because it can ship in the same PR.
- **Suggested action**: Once F-B-017 is resolved, delete these fields. Handlers that need to communicate side-channel results should subclass or return a typed payload.
- **Effort**: tiny (after F-B-017)

### F-B-019 — `Container.add` / `Container.remove` audit not propagated to `Empire.resource_pool` and `IProductionResourceSource` symmetric invariants
- **Severity**: medium
- **Category**: missing-functionality (the invariant pinned at the Container substrate level — already in DI log — doesn't have a parallel at the engine-facing protocol level)
- **File**: `game/strategy/engine/production_engine.py:60-83` (Protocol contract)
- **Symbol**: `IProductionResourceSource.production_consume_resource`
- **Source refactor**: PROJ-436 Phase 8 (unified Protocol seam) + PROJ-436 Phase 12 (Option C truth-up)
- **What survived**: The Protocol contract docstring describes the actual-vs-requested-amount semantics but does NOT declare that `production_has_resources(...)` returning True implies `production_consume_resource(...)` returns True. The discovered-issues entry DI-2026-05-18-007 already flagged this on the engine side; this finding is its Protocol-side complement.
- **Why it's a problem**: Two engine-side problems flow from the unenforced Protocol contract: (a) future implementers can return False from `production_consume_resource` after `production_has_resources` returned True, burning tick_capacity without progress; (b) the affordability/consumption rounding mismatch in `Fleet.has_cargo_resources` (DI-2026-05-18-006) is a real-today instance of this exact contract gap.
- **Suggested action**: Pinned together with DI-2026-05-18-006 / DI-2026-05-18-007: declare in `IProductionResourceSource.production_consume_resource` Protocol docstring that "MUST return True when `production_has_resources(costs)` returned True for the same `(resource_type, costs[resource_type])`. Implementers that perform rounding (integer-typed sources) MUST do so symmetrically in both methods." Reflected by F-B-019 being closed alongside DI-006 / DI-007.
- **Effort**: tiny (Protocol docstring + a single ratchet test); the actual implementer fix is sized in DI-006

### F-B-020 — `commands/registry.py:312-325 planet_fms_action_order_types` derives from `subcategories` string-tag but no schema test guards the tag spelling
- **Severity**: low
- **Category**: test-inconsistency (data-driven dispatch with no spelling guard)
- **File**: `game/strategy/engine/commands/registry.py:312-325`
- **Symbol**: `CommandRegistry.planet_fms_action_order_types`
- **Source refactor**: PROJ-424 Phase 1 (subcategory-tag-driven derivation)
- **What survived**: `if "planet_fms" in s.subcategories` — a free-form string check. Typo a registration (`"planet-fms"`, `"planetfms"`, `"plnaet_fms"`) and the order silently drops out of the planet-FMS dispatch set without any test catching it. PROJ-FMS-B / PROJ-FMS-C / PROJ-FMS-D added the five handlers; no test pins the 5-entry shape of `planet_fms_action_order_types()`.
- **Why it's a problem**: Silent-loss class — exactly the kind that survived prior refactors (the "test_specs_sharing_order_type_declare_same_codec" ratchet pattern from PROJ-438 Phase 9 is the existing template).
- **Suggested action**: Add `test_planet_fms_subcategory_tag_spelling_or_set_size` under `tests/unit/strategy/engine/commands/` that asserts `len(command_registry.planet_fms_action_order_types()) == 5` and the set equals `{LAY_MINES, LAUNCH_FIGHTERS, RECOVER_FIGHTERS, LAUNCH_SATELLITES, RECOVER_SATELLITES}`. Optionally extract `"planet_fms"` to a `SUBCATEGORY_PLANET_FMS` module-level constant in `commands/__init__.py`.
- **Effort**: tiny

### F-B-021 — `replay_store.py:434 _iter_replay_files` module-level helper missing return annotation
- **Severity**: low
- **Category**: polish
- **File**: `game/strategy/services/replay_store.py:434`
- **Symbol**: `ReplayStore._iter_replay_files` (static method)
- **Source refactor**: none
- **What survived**: `def _iter_replay_files(rd: Path):` — no return annotation. It's a private static method on the class but visible enough that the convention applies.
- **Why it's a problem**: Minor convention gap.
- **Suggested action**: `def _iter_replay_files(rd: Path) -> Iterator[Path]:`.
- **Effort**: tiny

### F-B-022 — No behavioral test pins `_execute_planet_action` ↔ `LayMinesOrderHandler` dispatch path (compounding F-B-001)
- **Severity**: medium
- **Category**: test-inconsistency / missing-functionality
- **File**: `tests/integration/test_fms_planet_recovery.py`, `tests/integration/test_fms_planet_launch.py` (missing companion file for LAY_MINES)
- **Symbol**: `ActionExecutionEngine._process_planet_action_tick` for `OrderType.LAY_MINES` issued by a planet
- **Source refactor**: PROJ-FMS-B / PROJ-431 / PROJ-438 Phase 6
- **What survived**: Integration tests exist for planet-FMS launch and recovery flows (`tests/integration/test_fms_planet_launch.py`, `test_fms_planet_recovery.py`). Grep across `tests/` for any test that queues a `LAY_MINES` order on a planet and ticks `_process_planet_action_tick` returns zero results. The DI-2026-05-18-001 entry on `_process_planet_action_tick` covers the broader gap as planned future work; this is a specific subcase: even when that integration scaffold lands, LAY_MINES will hit F-B-001's signature mismatch and the test would catch the regression.
- **Why it's a problem**: F-B-001's TypeError is uncovered by tests; the planet-LAY_MINES path is reachable from the UI by issuing the planet-FMS lay-mines flow but no test exercises it end-to-end.
- **Suggested action**: When the planet-FMS engine-mediated dispatch tests are added (DI-2026-05-18-001 / PROJ-438 Phase 10), parametrize across all five `planet_fms_action_order_types()` entries — not just the launch + recovery handlers. Land alongside the F-B-001 fix.
- **Effort**: small (parametrize the deferred Phase 10 test)

---

No additional minor findings deferred — the scan reached the natural floor of the layer (subjective-style and speculative items skipped per the rules).
