# Bucket A — Data + Facade Residue Scan (2026-05-18)

## Summary
- Total findings: 32
- By severity: high 1, medium 13, low 18
- By category: obsolete-code 9, test-inconsistency 3, missing-functionality 5, polish 15
- Files reviewed: ~35 production + ~10 test (cross-checked against `discovered_issues/log.jsonl` for de-duplication)
- Archived/active project decisions.md / findings_ledger.md scanned:
  - `Projects/active_projects/PROJ-436/decisions.md`
  - `Projects/active_projects/PROJ-437/decisions.md`
  - `Projects/active_projects/PROJ-438/decisions.md` (skim — engine layer mostly)
  - `Projects/archived_projects/PROJ-{422..435}` decisions.md (skim where my-layer hits surfaced)

Findings already in `AgentCoordination/discovered_issues/log.jsonl` (skipped — NOT re-filed):
- DI-2026-05-18-005 `Container.remove()` non-negative guard (container.py:225)
- DI-2026-05-18-006 `Fleet.has_cargo_resources` vs `consume_cargo_resource` rounding mismatch (fleet.py:245)
- DI-2026-05-18-003 `FleetInfo.from_fleet` hardcoded 8-resource tuple (fleet_dto.py:217-226)

## Findings

### F-A-001 — `BayInventory.remove_resource` / `remove_population` accept negative `amount`
- **Severity**: low
- **Category**: obsolete-code
- **File**: `game/strategy/data/bay_inventory.py:140` (and `:176`)
- **Symbol**: `BayInventory.remove_resource`, `BayInventory.remove_population`
- **Source refactor**: PROJ-436 Phase 2 (added these slots)
- **What survived**: `add_resource` and `add_population` both raise `ValueError` on `amount < 0` (lines 132, 172). The sibling `remove_resource` / `remove_population` do NOT have the symmetric guard — a negative `amount` passes `if amount > current + 1e-9` and SUBTRACTS-a-negative, i.e. grows the slot.
- **Why it's a problem**: Identical invariant gap to DI-005 (`Container.remove`) but on the typed BayInventory side. Same forward-contract drift risk. No current production caller passes negative removals, but the policy is inconsistent with the matching `add_*` validation.
- **Suggested action**: Mirror the `add_*` guard at the top of both `remove_*` methods (`if amount < 0: raise ValueError(...)` / `if count < 0: raise ValueError(...)`). Add 2 unit tests in `tests/unit/strategy/data/test_bay_inventory.py`.
- **Effort**: tiny

### F-A-002 — `Planet` class is a dataclass with 47 fields and a wrapped `__init__` legacy-kwargs shim
- **Severity**: medium
- **Category**: obsolete-code
- **File**: `game/strategy/data/planet.py:398-420` (wrapper definition + assignment); `game/strategy/data/planet_serde.py:160-162` (non-test dependent)
- **Symbol**: `_planet_init_with_legacy_kwargs` (module-level wrapper assigned to `Planet.__init__`)
- **Source refactor**: PROJ-436 Phase 4f
- **What survived**: A module-level wrapper that translates `stockpile=...`, `max_stockpile=...`, `staging_yard=...` kwargs to their private-field spellings, so test fixtures don't have to migrate. The comment at line 387 says "rather than sweep those mechanically (planet_serde itself, `_build_galaxy_fixture` and ~15 other test files)". Mirrors PROJ-443 Phase 5b retention rationale for `_ship_instance_init_with_legacy_kwargs`.
- **Why it's a problem**: Two coupled deletion shims (this + `_ship_instance_init_with_legacy_kwargs` at `ship_instance.py:809`) survive because the test sweep was scoped out. Per CLAUDE.md "saves are disposable" + "no compatibility shims" — and `planet_serde.planet_to_dict` ALSO uses the public name `"stockpile"` for the save key (line 53), plus `planet_from_dict_kwargs` reconstructs through the wrapper at planet_serde.py:160-162. So the wrapper isn't just protecting test files; it's load-bearing for serialization too. Either (a) sweep test files + `planet_serde` to the private spelling and delete the wrapper, or (b) keep the wrapper and accept the divergence between dataclass field name and public/save-format name.
- **Suggested action**: Audit-then-decide. Get a fresh `rg -n "Planet\\(.*stockpile=" tests/` count BEFORE committing to effort. Codex consult 2026-05-18 indicates the real footprint exceeds the original "~15 test files" Phase-4f comment estimate. Migration target is the post-PROJ-436 private kwargs (`_stockpile=`, `_max_stockpile=`, `_staging_yard=`) or factory helpers, plus a rewrite of `planet_from_dict_kwargs`; then delete the wrapper.
- **Effort**: small (audit) → medium (sweep) — sizing depends on the audit count. Resize the phase before committing.
- **Codex verification (2026-05-18)**: Wrapper confirmed at planet.py:398-420 (start line was 398, not 382 — corrected). `planet_serde.py:160-162` confirmed as non-test dependent. Effort estimate revised; sweep footprint is materially larger than the original Phase-4f comment suggests.

### F-A-003 — `_ship_instance_init_with_legacy_kwargs` constructor wrapper (kept-with-rationale per PROJ-443 5b)
- **Severity**: low
- **Category**: obsolete-code
- **File**: `game/strategy/data/ship_instance.py:787-833`
- **Symbol**: `_ship_instance_init_with_legacy_kwargs`
- **Source refactor**: PROJ-436 Phase 3f, retained per PROJ-443 Phase 5b
- **What survived**: Same shape as F-A-002 — translates `consumable_levels=` / `cargo_contents=` kwargs to private-field spellings. Comment block at lines 797-804 documents the explicit retention rationale (18 test files would have to change). Counted as low severity because of the explicit documented decision; flagged here for visibility in the cross-bucket scan since the same pattern repeats on Planet.
- **Why it's a problem**: Compat shim that ought eventually to be retired in the same pass as F-A-002. Survives intentionally; no current bug; tracking visibility only.
- **Suggested action**: Reassess when F-A-002 ships — if the planet-side wrapper deletion sweep is small, this one is similar in shape and could be deleted in the same pass. Otherwise leave alone.
- **Effort**: medium (18-file test sweep) if eventually retired

### F-A-004 — `Planet.stockpile` / `max_stockpile` / `staging_yard` Phase-4f deletion-shim @property cluster
- **Severity**: low
- **Category**: obsolete-code
- **File**: `game/strategy/data/planet.py:224-262`
- **Symbol**: `Planet.stockpile`, `Planet.max_stockpile`, `Planet.staging_yard` (+ their setters)
- **Source refactor**: PROJ-436 Phase 4f
- **What survived**: Three @property/@setter pairs that expose private `_stockpile`/`_max_stockpile`/`_staging_yard` under the public legacy names. The docstrings state these are "Phase 4f deletion shim" entries kept so test infrastructure that does `planet.stockpile[k] = v` keeps working. `planet_serde.py:53-55` also reads through these properties, so they are NOT purely a test surface.
- **Why it's a problem**: Three thin property pairs (~30 LOC) survive on Planet because deletion would force the test sweep in F-A-002. Production writers route through `IPlanetMutator` and the helper methods (`add_to_stockpile`, etc.) so the @property accessors are mostly read-paths plus test pokes.
- **Suggested action**: Bundle with F-A-002. Once the kwarg wrapper deletion sweep lands, also retire these three @property pairs and let `planet_serde` read directly from `_stockpile` / `_max_stockpile` / `_staging_yard`.
- **Effort**: small (mechanical, must land with F-A-002)

### F-A-005 — `ShipInstance.consumable_levels` / `cargo_contents` Phase-3f deletion-shim @property cluster
- **Severity**: low
- **Category**: obsolete-code
- **File**: `game/strategy/data/ship_instance.py:237-262`
- **Symbol**: `ShipInstance.consumable_levels`, `ShipInstance.cargo_contents`
- **Source refactor**: PROJ-436 Phase 3f
- **What survived**: Same shape as F-A-004 on the ship side — @property/@setter pairs over `_consumable_levels` / `_cargo_contents`.
- **Why it's a problem**: Same as F-A-004.
- **Suggested action**: Bundle with F-A-003. The two ship-side shim clusters (kwarg wrapper + @property) retire together.
- **Effort**: small

### F-A-006 — `Planet` data class exceeds 420 LOC despite Phase 4f extractions; `planet_serde` docstring says 350 LOC target
- **Severity**: low
- **Category**: polish
- **File**: `game/strategy/data/planet.py:1` (file is 420 LOC); `game/strategy/data/planet_serde.py:4-6` (stale comment)
- **Symbol**: module-level
- **Source refactor**: PROJ-372 Phase 2 split
- **What survived**: `planet_serde.py` was extracted from `planet.py` "to keep the data class file under the 350 LOC ceiling". The ceiling is 500 LOC in current CLAUDE.md; planet.py is at 420 LOC. The serde docstring is stale.
- **Why it's a problem**: Stale comment misleads about the project ceiling. Planet.py is currently under the actual 500-LOC ceiling but the docstring's `350` reference is wrong.
- **Suggested action**: Fix the comment in `planet_serde.py:4` to reference the current 500-LOC ceiling per CLAUDE.md, or drop the LOC reference entirely.
- **Effort**: tiny

### F-A-007 — `ShipInstance` is 839 LOC, well over the 500-LOC production ceiling
- **Severity**: medium
- **Category**: polish
- **File**: `game/strategy/data/ship_instance.py:1` (file is 839 LOC)
- **Symbol**: module-level
- **Source refactor**: PROJ-425 + PROJ-431 + PROJ-436 (multiple extraction passes)
- **What survived**: The class docstring at lines 47-125 explicitly acknowledges and rationalizes the size: "intentionally large because of D2 default (a) — keep inline ``design_data``". 910-caller entry-point sweep declared OUT of PROJ-438 scope; PROJ-443 Phase 5b found 18-file test footprint and kept the kwarg wrapper. Five high-value shim entry points (`create`, `to_dict`, `clone`, `to_ship`, `update_from_ship`) explicitly retained per TD-06 Weak-LLM Guardrail #1 (PROJ-436 decisions.md row 122). Net: ceiling violation IS the documented residue.
- **Why it's a problem**: Single largest data-layer file by 200+ LOC. The retained shims occupy roughly ship_instance.py:419-783 (~360 LOC of forwarding methods). Each shim has 4-10 callers; the 910-caller migration is the blocker. CLAUDE.md says "Production files under `game/` should stay under 500 LOC. Split by responsibility when a touched file approaches that ceiling." The file is 67% over.
- **Suggested action**: NOT a quick sweep. Bundle into a future "ShipInstance shim retirement" project — likely 2-3 phases of mechanical caller migration per shim cluster (serializer, bridge, resource manager). The class docstring already documents the explicit removal conditions; act on them when bandwidth allows.
- **Effort**: large

### F-A-008 — `Fleet.py` is 677 LOC, over the 500-LOC ceiling
- **Severity**: low
- **Category**: polish
- **File**: `game/strategy/data/fleet.py:1` (file is 677 LOC)
- **Symbol**: module-level
- **Source refactor**: PROJ-87, PROJ-210, PROJ-222, PROJ-238, PROJ-269, PROJ-382, PROJ-431, PROJ-436 (progressive extraction passes)
- **What survived**: Five delegate classes already extracted (`FleetBattleAdapter`, `FleetCapabilityCalculator`, `FleetConsumableAggregator`, `FleetPursuerTracker`, `FleetHierarchy`). What remains is mostly: order-queue management (~120 LOC), to_dict/from_dict (~140 LOC), and merge_with logic (~50 LOC). The serialization helpers are a natural extraction target into `fleet_serde.py` per PROJ-372's planet_serde precedent.
- **Why it's a problem**: Modest ceiling violation (35% over). Less acute than ship_instance.py but a natural candidate when next touched.
- **Suggested action**: Extract `Fleet.to_dict` + `Fleet.from_dict` (+ `resolve_order_references` already delegating to OrderSerializer) into a sibling `fleet_serde.py` modeled on `planet_serde.py`. Would drop fleet.py by ~140 LOC to ~537 LOC.
- **Effort**: small

### F-A-009 — `planet_gen.py` is 610 LOC, over the ceiling
- **Severity**: low
- **Category**: polish
- **File**: `game/strategy/data/planet_gen.py:1` (file is 610 LOC)
- **Symbol**: module-level
- **Source refactor**: PROJ-372 (planet split)
- **What survived**: Procedural planet generation logic. Likely splittable along atmosphere-gen / surface-conditions-gen / orbital-arrangement axes. (Not deep-read in this scan — flagging the LOC ceiling violation only.)
- **Why it's a problem**: Modest ceiling violation (22% over). Out-of-scope for any other current finding.
- **Suggested action**: When next touched, split by sub-concern (atmosphere / surface / orbits).
- **Effort**: medium

### F-A-010 — `Fleet.consume_cargo_resource` int-rounds float `amount` before unloading
- **Severity**: medium
- **Category**: obsolete-code
- **File**: `game/strategy/data/fleet.py:262`
- **Symbol**: `Fleet.consume_cargo_resource`
- **Source refactor**: predates PROJ-436 (commit `6d9d6fe15` per PROJ-436 Phase 11 audit)
- **What survived**: `consume_cargo_resource(resource_type, amount)` calls `self._resource_agg.unload_cargo_from_fleet(resource_type, int(round(amount)))` — silently converting the float request to int. **Note**: this is downstream of DI-006 (the affordability vs consumption rounding mismatch), which is already in `discovered_issues/log.jsonl`. The actual int-coercion site is here. DI-006 captures the policy-level concern; this finding captures the code-level fix site for completeness.
- **Why it's a problem**: Cross-reference with DI-006. The fix lives at this line: either widen `_resource_agg.unload_cargo_from_fleet` to accept float and propagate through the integer-typed cargo store widening (Option A in PROJ-436 Phase 11), or round in `Fleet.has_cargo_resources` (Option B) to make affordability semantics match consumption. PROJ-436 Phase 12 picked Option C (engine-side diff truth-up) which closes accounting but leaves this site untouched.
- **Suggested action**: When PROJ-436 Phase 12's deferred "RESOURCE_SHORTAGE event when actually-consumed < requested" lands, also pick Option A or B here. Track via DI-006 — this is its fix site.
- **Effort**: small (Option B) or medium (Option A widens the cargo store)

### F-A-011 — `Empire.resource_pool` is a pure aggregation walked every read; Phase-0 D2 deferred caching
- **Severity**: low
- **Category**: missing-functionality
- **File**: `game/strategy/data/empire.py:229-250`
- **Symbol**: `Empire.resource_pool`
- **Source refactor**: PROJ-436 Phase 5 (deleted `_fleet_resource_pool`)
- **What survived**: Phase 5's commit comment explicitly says "Per Phase 0 D2 default this stays an uncached pure query; if post-Phase-5 profiling shows the aggregation is hot at large-empire scale, caching with explicit invalidation (PROJ-293 pattern) can land as a sibling sub-phase." No profiling has happened. Used by UI affordability checks (`Empire.has_resources`, `Empire.get_resource`).
- **Why it's a problem**: Documented missing-functionality / deferred decision. At large-empire scale (200+ colonies, several reads per UI frame), this walks every colony stockpile every call. Cheap until it's not.
- **Suggested action**: Profile under late-game save. If hot, add cache with explicit invalidation hooks on `Planet.add_to_stockpile` / `consume_from_stockpile` / `IPlanetMutator.set_stockpile_amount` and on `Empire.add_colony` / `remove_colony`.
- **Effort**: small (profile is the gate)

### F-A-012 — `PlanetaryFacility` consumable_levels not folded into Container substrate (PROJ-436 D1 deferred)
- **Severity**: medium
- **Category**: missing-functionality
- **File**: `game/strategy/data/planetary_facility.py:32` (+ `get_fuel_storage`, `add_fuel`, `withdraw_fuel`, `get_max_fuel_storage` at :136-193)
- **Symbol**: `PlanetaryFacility.consumable_levels`, `add_fuel`, `withdraw_fuel`
- **Source refactor**: PROJ-436 Phase 0 D1 — deferred
- **What survived**: PlanetaryFacility still carries `consumable_levels: Dict[str, float]` plus a "fuel"-specific API (`get_fuel_storage`, `add_fuel`, `withdraw_fuel`, `get_max_fuel_storage`). Phase 0 D1 default was "(b) keep as internal state until a concrete transfer use case justifies (a)". Note the resource is hardcoded to `"fuel"` — same anti-pattern as DI-003 and DI-004 (hardcoded resource ids). Adding e.g. an organics-storage facility would require new symmetric methods or a hardcoded second branch.
- **Why it's a problem**: Two-fold: (1) the resource ID `"fuel"` is hardcoded in 4 method signatures/bodies; (2) the slot exists outside the unified Container substrate, so facility-level resources cannot participate in transfers. Per `Projects/active_projects/PROJ-437/decisions.md` row 39: facility-component planet containers were explicitly deferred to PROJ-436 Phase 8 (which has shipped but did not touch this).
- **Suggested action**: Replace `add_fuel`/`withdraw_fuel` with generic `add_consumable(resource_id, amount)` / `withdraw_consumable(resource_id, amount)` that iterate `ResourceCatalog.all_ids()` for capacity. Eventually fold the slot into a per-facility `Container` per D1 option (a) — but only when a transfer-UI use case emerges.
- **Effort**: small (generic API) → medium (Container fold-in)

### F-A-013 — `FleetSlice._ship_container_snapshot` projects capacity from `ship._cargo_mgr` but uses `inf` policy projection
- **Severity**: low
- **Category**: polish
- **File**: `game/strategy/facade/slices/fleet_slice.py:165-193`
- **Symbol**: `_ship_container_snapshot` (module-level helper)
- **Source refactor**: PROJ-437 Phase 1a
- **What survived**: The function projects each ship's `bay_inventory` into a snapshot. To avoid Container's per-resource capacity rejection at projection time, it builds the view at `capacity_mass=inf`, then reports the real bay capacity from `_cargo_mgr.get_vehicle_bay_capacity()`. Comment lines 180-182 acknowledges: "Phase 2 validation decides how to treat the uncapped case." The decisions.md row 39 confirms "Future work should not assume those design.md aspirations [per-facility planet containers + per-container acceptance validation] are realized."
- **Why it's a problem**: The snapshot can legally report `mass_used > capacity_mass`, which is fine but means downstream consumers (TransferValidator, UI mass-preview) must handle that case explicitly. PROJ-437 Phase 5 Codex consult flagged it as a documented residual risk (transfer_branches.py:458 — see DI-2026-05-18-001 in `discovered_issues/log.jsonl`).
- **Suggested action**: Cross-reference with DI-2026-05-18-001. When the fleet-to-fleet pod/vehicle transfer fix lands, also tighten the snapshot's capacity model to match what the engine handlers actually enforce.
- **Effort**: small (paired with DI-001 fix)

### F-A-014 — `PlanetSlice._planet_stockpile_snapshot` uses `sum(max_stockpile.values())` as a proxy for total mass capacity
- **Severity**: medium
- **Category**: missing-functionality
- **File**: `game/strategy/facade/slices/planet_slice.py:155-180`
- **Symbol**: `_planet_stockpile_snapshot` (module-level helper)
- **Source refactor**: PROJ-437 Phase 1a — documented residual
- **What survived**: The function computes `capacity_mass = float(sum(max_stockpile.values()))` if any caps are set, otherwise `inf`. PROJ-437 decisions.md row 24 explicitly notes this is "a rough proxy; revisit in Phase 2 once mass-remaining preview needs a real cap model".
- **Why it's a problem**: `max_stockpile.values()` are PER-RESOURCE caps in resource units, not total mass — summing them treats every resource as having `mass_per_unit == 1.0`, which is wrong for vapors (0.001), fuel (0.0001), exotics (0.001), etc. (per `data/resources.json` first-pass values documented in PROJ-436 Phase 0 D3). The mass-preview UI built on top of this will display nonsense for capacity remaining.
- **Suggested action**: Replace the sum with `sum(amount * ResourceCatalog.from_json().get_mass_per_unit(rid) for rid, amount in max_stockpile.items())`. Cross-references the same `ResourceCatalog` iteration pattern as DI-003.
- **Effort**: tiny (3-line fix)

### F-A-015 — `BuildQueueSourceDTO.construction_queue` is a mutable `List[Dict[str, Any]]` inside a frozen dataclass
- **Severity**: low
- **Category**: polish
- **File**: `game/strategy/facade/dto/build_queue_dto.py:16`
- **Symbol**: `BuildQueueSourceDTO.construction_queue`
- **Source refactor**: none — discovered in this scan
- **What survived**: `@dataclass(frozen=True)` prevents field reassignment but `construction_queue: List[Dict[str, Any]]` is a mutable list of mutable dicts. The `from_domain` constructor does `[deepcopy(item) for item in ...]` to defend against UI mutation of the origin entity, but UI can still mutate the DTO's own list (`dto.construction_queue.append(...)`, `dto.construction_queue[0]["turns_remaining"] = -1`).
- **Why it's a problem**: Breaks the CQRS-lite "facade hands UI a read-only snapshot" contract that `ColonyDemographicView.__post_init__` enforces with `MappingProxyType`. Same problem; weaker defence.
- **Suggested action**: Either (a) wrap `construction_queue` in `tuple(...)` of `MappingProxyType(...)` after deepcopy, or (b) document the contract gap. Pattern (a) is what `ColonyDemographicView.total_upkeep` does (`colony_demographic_view.py:79-87`).
- **Effort**: tiny

### F-A-016 — `BuildQueueSourceDTO.build_rate` and `construction_queue` use `Dict[str, Any]` / `List[Dict[str, Any]]` instead of typed structures
- **Severity**: low
- **Category**: polish
- **File**: `game/strategy/facade/dto/build_queue_dto.py:16,20`
- **Symbol**: `BuildQueueSourceDTO`
- **Source refactor**: none — discovered in this scan
- **What survived**: `build_rate: Dict[str, float]` is fine, but `construction_queue: List[Dict[str, Any]]` is untyped. The dicts have a known shape (`{"design_id", "type", "turns_remaining", "resources_consumed", ...}`) per `Planet.add_production` at planet.py:359-365.
- **Why it's a problem**: UI code reading the queue uses string keys with no IDE/lint support; field name typos surface only at runtime.
- **Suggested action**: Introduce a `BuildQueueItemDTO` frozen dataclass with the known fields, retype the list as `Tuple[BuildQueueItemDTO, ...]`.
- **Effort**: small (mechanical, ~6 call sites in UI per `rg "construction_queue\["`)

### F-A-017 — `FleetInfo.from_fleet` swallows `(ValueError, AttributeError)` from capabilities listing
- **Severity**: low
- **Category**: polish
- **File**: `game/strategy/facade/dto/fleet_dto.py:192-196`
- **Symbol**: `FleetInfo.from_fleet`
- **Source refactor**: none — discovered in this scan
- **What survived**: ```try: capabilities = tuple(fleet.capabilities.list_abilities())\nexcept (ValueError, AttributeError): capabilities = ()```. The comment says "No registry available or no ships - empty capabilities". This is a 2-exception narrow catch (compliant with CLAUDE.md broad-catch rule — narrow types listed, no comment needed) but silently masks two distinct failure modes.
- **Why it's a problem**: ValueError from `list_abilities()` could mean "no registry"; AttributeError could mean "test stub fleet". Treating both as "empty capabilities" hides DI configuration bugs in production paths.
- **Suggested action**: Either log at DEBUG when caught, or split into two narrower catches (AttributeError → test-stub path → return ()  ; ValueError → re-raise or log WARN with the fleet id).
- **Effort**: tiny

### F-A-018 — `EmpireInfo` lacks fleet_resource_pool / total stockpile aggregate fields
- **Severity**: low
- **Category**: missing-functionality
- **File**: `game/strategy/facade/dto/empire_dto.py:76-116`
- **Symbol**: `EmpireInfo.from_empire`
- **Source refactor**: PROJ-436 Phase 5
- **What survived**: `EmpireInfo` carries `colony_count` and `fleet_count` but no aggregate resource totals. `Empire.resource_pool` (F-A-011) is the production source of truth but the facade does not project it. UI consumers that want empire-wide resource totals walk `empire.colonies[*].stockpile` themselves, defeating the facade boundary.
- **Why it's a problem**: Pre-Phase-5 there was a durable `_fleet_resource_pool` field; the facade may have surfaced it implicitly. Post-Phase-5 the aggregate is a pure query; the DTO doesn't expose it. UI code that needs empire resource totals must either dive into the domain layer (boundary violation) or call `facade.empires.get(eid)` and find the aggregate missing.
- **Suggested action**: Add `total_resources: Tuple[Tuple[str, float], ...]` to `EmpireInfo`, populated from `empire.resource_pool` (which is itself the pure aggregation). Use `ResourceCatalog.all_ids()` iteration to keep ordering stable.
- **Effort**: tiny

### F-A-019 — `PlanetInfo.stockpile` is `Tuple[Tuple[str, float], ...]` — order is dict-insertion order, not catalog order
- **Severity**: low
- **Category**: polish
- **File**: `game/strategy/facade/dto/planet_dto.py:78-79` + `_dict_to_tuple` helper at :34-41
- **Symbol**: `PlanetInfo.from_planet`
- **Source refactor**: none — discovered in this scan
- **What survived**: `_dict_to_tuple(d)` returns `tuple((k, v) for k, v in d.items())`. For `planet.stockpile` (a Dict[str, float]) this is dict-insertion order, which is arbitrary across saves and gen seeds.
- **Why it's a problem**: UI rendering will show resources in different orders per planet depending on insertion history. Same problem the FleetInfo hardcoded-tuple solves (deterministically) at the cost of being hardcoded (DI-003).
- **Suggested action**: Iterate `ResourceCatalog.all_ids()` for stable canonical order (same pattern proposed for DI-003).
- **Effort**: tiny

### F-A-020 — `OrderSerializer._deserialize_target` Format 7 "raw fallback" silently catches unknown `type:` keys
- **Severity**: low
- **Category**: polish
- **File**: `game/strategy/data/order_serializer.py:148-152`
- **Symbol**: `OrderSerializer._deserialize_target`
- **Source refactor**: PROJ-210
- **What survived**: After 6 explicit format branches, "Unknown format - return as-is" silently returns the raw dict. If a future save format introduces a new target type (e.g. `{'type': 'star_ref', ...}`), it lands here and propagates as a dict target through the order pipeline, where it'll cause `AttributeError` deep inside an order handler.
- **Why it's a problem**: Save-format drift would fail at order execution rather than at load with a clear error. Per CLAUDE.md "fail-fast" preference (see PROJ-436 Phase 0 D3 default rejecting silent defaults).
- **Suggested action**: Raise `PersistenceException` with `ErrorCode.CORRUPT_DATA` when `target_data` has a `'type'` field that doesn't match any known format. Pass-through for dicts without a `'type'` key remains correct (backward-compatible with pre-typed save formats).
- **Effort**: tiny

### F-A-021 — `Galaxy.py` re-exports `PlanetType` with `# noqa: F401` — `# noqa` likely outlives the actual need
- **Severity**: low
- **Category**: obsolete-code
- **File**: `game/strategy/data/galaxy.py:10`
- **Symbol**: `from game.strategy.data.planet import Planet, PlanetType  # noqa: F401  (PlanetType re-export)`
- **Source refactor**: PROJ-394 (split)
- **What survived**: The `# noqa: F401` re-export keeps `from game.strategy.data.galaxy import PlanetType` working for legacy callers. No `git grep` was run in this scan to verify whether any non-test caller still uses this import path.
- **Why it's a problem**: `# noqa` markers often outlive their justification. If no production caller imports `PlanetType` from `galaxy`, the line is dead.
- **Suggested action**: `rg -n "from game.strategy.data.galaxy import.*PlanetType"` to count callers. If only tests, migrate them to `from game.strategy.data.planet import PlanetType` and delete the re-export.
- **Effort**: tiny

### F-A-022 — `Stars.py:155` carries a `# PROJ-372 Phase 1 backwards-compat shim` for `StarGenerator`
- **Severity**: low
- **Category**: obsolete-code
- **File**: `game/strategy/data/stars.py:155`
- **Symbol**: `StarGenerator` (re-export shim)
- **Source refactor**: PROJ-372 Phase 1
- **What survived**: Comment at :155 says "PROJ-372 Phase 1 backwards-compat shim. ``StarGenerator`` lives in ...". Phase 1 is long-closed. The shim's removal condition was probably "once callers migrate".
- **Why it's a problem**: PROJ-372 Phase 1 closed long enough ago that the migration window may have lapsed. Verify and delete if dead.
- **Suggested action**: `rg -n "stars\.StarGenerator|from game.strategy.data.stars import.*StarGenerator"` and if only the test guard remains, retire the shim.
- **Effort**: tiny

### F-A-023 — `FleetCapabilityCalculator.py` carries `# PROJ-211 Task 5.7: Removed fallback to global registry` historical comment
- **Severity**: low
- **Category**: polish
- **File**: `game/strategy/data/fleet_capability_calculator.py:7`
- **Symbol**: module-level docstring
- **Source refactor**: PROJ-211 Task 5.7 (long-closed)
- **What survived**: Historical commentary on changes done several refactor generations back. Doesn't describe current behavior.
- **Why it's a problem**: Stale provenance comment in a docstring. Doesn't actively mislead but adds noise.
- **Suggested action**: Either prune to current-behavior description or move to a changelog. Low priority — only act on next touch.
- **Effort**: tiny

### F-A-024 — `Storm.py` carries `# PROJ-300 D19: legacy 'effects' shape on saves fails loudly` migration guard for a long-retired shape
- **Severity**: low
- **Category**: obsolete-code
- **File**: `game/strategy/data/storm.py:127-131`
- **Symbol**: `Storm.from_dict` legacy-shape guard
- **Source refactor**: PROJ-300 D19
- **What survived**: An explicit raise on `'effects'` key in save data. Comments at lines 5-27 explain the Phase 7 deletion of the `StormEffect` class. Per CLAUDE.md "saves are disposable — no migration shim", a guard that rejects old saves is technically a migration-aware path.
- **Why it's a problem**: The guard fails loudly (good per fail-fast), but it's a save-shape concern for a save format that's been disposable since PROJ-300 closed. The branch is dead in any user's current save history.
- **Suggested action**: Delete the legacy-effects-shape check; let the natural KeyError / TypeError from passing the wrong shape to the new constructor surface. Save migration is not supported per CLAUDE.md.
- **Effort**: tiny

### F-A-025 — `planet_serde.py:159` carries `deposits=data.get("deposits", data.get("resources", {}))` legacy-key alias
- **Severity**: low
- **Category**: obsolete-code
- **File**: `game/strategy/data/planet_serde.py:159`
- **Symbol**: `planet_from_dict_kwargs`
- **Source refactor**: none — predates PROJ-372
- **What survived**: The `data.get("deposits", data.get("resources", {}))` fallback accepts an old `"resources"` key. Per CLAUDE.md "saves are disposable", any save predating the rename is invalid.
- **Why it's a problem**: Same as F-A-024 — supports a save-shape that shouldn't exist.
- **Suggested action**: Drop the `data.get("resources", {})` fallback. `data.get("deposits", {})` is sufficient.
- **Effort**: tiny

### F-A-026 — `Empire.to_dict` writes a deleted-field comment but the deletion is upstream of the comment
- **Severity**: low
- **Category**: polish
- **File**: `game/strategy/data/empire.py:323-326`
- **Symbol**: `Empire.to_dict`
- **Source refactor**: PROJ-436 Phase 5
- **What survived**: Comment "PROJ-436 Phase 5: ``_fleet_resource_pool`` is deleted; the save shape no longer carries an empire-level resource pool." Documentation of the deletion — not residue itself, but the next `empire.from_dict` at line 392-396 reaffirms the same thing.
- **Why it's a problem**: Duplicated deletion-comments at to_dict + from_dict for the same removed field. After 6+ months these self-documenting comments rot.
- **Suggested action**: Collapse to a one-line comment at the empire.py:60-63 field-comment block where the deletion is already documented. Don't repeat it in to_dict/from_dict.
- **Effort**: tiny

### F-A-027 — `CarriedVehicle.py:112` carries `legacy ``ShipInstance.carried_items``` historical comment
- **Severity**: low
- **Category**: polish
- **File**: `game/strategy/data/carried_vehicle.py:112` (and surrounding block)
- **Symbol**: comment block on `CarriedVehicle.from_dict`
- **Source refactor**: PROJ-431 Phase 1f
- **What survived**: Comment referencing the deleted `ShipInstance.carried_items` (deleted in PROJ-436 Phase 9 per ship_instance.py:79). Comment claims it's "while both lived in the same legacy ShipInstance.carried_items" — they don't anymore.
- **Why it's a problem**: Stale comment narrates a historical state.
- **Suggested action**: Rewrite the comment to describe current behavior (typed `bay_inventory.bay` storage) without the legacy reference.
- **Effort**: tiny

### F-A-028 — `tests/integration/strategy/facade/test_facade_integration.py` has 5 conditional `pytest.skip` calls when RNG-dependent fixtures fail
- **Severity**: medium
- **Category**: test-inconsistency
- **File**: `tests/integration/strategy/facade/test_facade_integration.py:158, 184, 226, 325, 346`
- **Symbol**: 5 `pytest.skip` call sites
- **Source refactor**: none — discovered in this scan
- **What survived**: Tests skip when the procedurally-generated galaxy doesn't yield an uncolonized planet, a home colony, an enemy fleet, etc. ("No uncolonized planets available for test", "No home colony for test", "Need enemy fleet for intercept test").
- **Why it's a problem**: Tests that conditionally skip on RNG state run sometimes-zero-sometimes-not. A flaky CI green could mean every assertion was skipped. Per CLAUDE.md TDD principles, these tests should construct deterministic fixtures rather than gamble on galaxy generation.
- **Suggested action**: Replace the procedural-gen fixtures with explicit fixture builders that inject a known uncolonized planet, a home colony, and an enemy fleet. Remove the 5 `pytest.skip` calls. Each test then deterministically exercises its target path.
- **Effort**: small (5 fixture rewrites)

### F-A-029 — `tests/integration/save_load/test_resupply_persistence.py` skips 2 tests when generated session has no colonies or no fleets
- **Severity**: low
- **Category**: test-inconsistency
- **File**: `tests/integration/save_load/test_resupply_persistence.py:234, 283`
- **Symbol**: 2 `pytest.skip` call sites
- **Source refactor**: none — discovered in this scan
- **What survived**: Same pattern as F-A-028 — "No colonies in generated session to test facility persistence" and "No fleets with ships in generated session". These persistence tests are primary subjects for save/load round-trips through the facade + data layer.
- **Why it's a problem**: Same as F-A-028.
- **Suggested action**: Inject the colony + fleet explicitly rather than relying on procedural-gen.
- **Effort**: tiny

### F-A-030 — `CommandDispatchSlice.__getattr__` re-resolves the registry on every call
- **Severity**: low
- **Category**: polish
- **File**: `game/strategy/facade/slices/command_dispatch_slice.py:73-107`
- **Symbol**: `CommandDispatchSlice.__getattr__`
- **Source refactor**: PROJ-363 Phase 4
- **What survived**: Resolver imports `command_registry` and calls `command_registry.specs_by_facade_helper()` on EVERY `dispatch_X` access. Comment at lines 61-63 says "The resolver returns a fresh closure on every call — there's no caching needed because the closure is cheap and the call sites resolve once per UI action." However, `specs_by_facade_helper()` walks the registry every call.
- **Why it's a problem**: Hot-path on UI command dispatch. The grouped namespace at `grouped_namespaces.py:111` calls `verb_to_helper[verb]` (cached at construction) and then `getattr(self._slice, helper_name)` — which triggers the registry walk. So every facade.commands.X(...) call does an O(N) walk over CommandSpecs.
- **Suggested action**: Cache `specs_by_facade_helper()` result on first call in a module-level dict (with explicit invalidation on registry mutation if that's a thing).
- **Effort**: tiny

### F-A-031 — `EmpireSlice.get_empire_by_id` linear-scans empires instead of using a cached index
- **Severity**: low
- **Category**: polish
- **File**: `game/strategy/facade/slices/_facade_state.py:113-118`
- **Symbol**: `FacadeSessionState.get_empire_by_id`
- **Source refactor**: PROJ-254 / PROJ-411 (per-turn cache framework)
- **What survived**: `FacadeSessionState` has cached indices for planets and fleets-by-hex (lines 66, 69) but empires get linear-scanned. Comment at line 114 just says "Look up an empire by ID via linear scan." Empires are O(1-10) so the perf concern is mild.
- **Why it's a problem**: Inconsistent with the rest of the cache holder's pattern. Modders pushing to 50+ empires would feel it.
- **Suggested action**: Add `empire_index` per the same per-turn invalidation pattern as `planet_index` (lazy build on first call, cleared in `invalidate_all`).
- **Effort**: tiny

### F-A-032 — `_facade_state.py` carries `stars_cache_new` field — `_new` suffix suggests an in-progress rename
- **Severity**: low
- **Category**: polish
- **File**: `game/strategy/facade/slices/_facade_state.py:82`
- **Symbol**: `FacadeSessionState.stars_cache_new`
- **Source refactor**: PROJ-411 Phase 1
- **What survived**: Field name `stars_cache_new` with comment "Distinct from `all_stars_cache` which holds DTO objects." The `_new` suffix suggests a deliberate rename to distinguish from the older field, but it now carries the rename artifact permanently.
- **Why it's a problem**: Names with `_new` suffixes tend to accumulate as `_new`, `_newer`, `_v2`, etc., when a real rename pass would consolidate them.
- **Suggested action**: Rename to something semantic: `raw_star_list_cache` or `stars_galaxy_cache` (raw star list vs DTO list). 1 file rename + ~3 internal callers.
- **Effort**: tiny

---

## Additional minor findings deferred

Capped at 32 findings; the highest-impact / clearest items above. Skim of additional sites left for the de-dup-against-discovered-issues pass:

- `Planet.from_dict` accepts `data.get('id', -1)` — `-1` sentinel for "unregistered" is a non-typed magic value. Polish.
- `Planet.__eq__` compares on `(name, location, orbit_distance)` ignoring `id` — could lead to spurious equality across galaxies. Need product-policy decision; not residue per se.
- `Fleet.__eq__` compares on `id` only — surprising given `Planet.__eq__` ignores `id`. Inconsistent equality semantics across the two main entity classes. Polish.
- `Empire` is the only major data class NOT using `@dataclass` (uses plain `__init__`). Stylistic but inconsistent.
- `Empire.from_dict` swallows old-save `resource_pool` key silently — same shape as F-A-025 / F-A-024. Polish.
- `OrderType` and `Order` re-imported from `order_types` at various sites; minor coupling artifact.
- `bay_inventory.from_dict` accepts `CarriedVehicle` instances OR dicts (line 313-316) — dual-shape input is a small back-compat shim. Polish.
- `ColonySpeciesConfig` test at `test_colony_species_config.py:163` carries `"last_food_ratio": 0.0,  # ignored (PROJ-284 back-compat)` save-shape test — old shape coverage. Low-priority test polish.

Stop here per the 80-finding cap rule and the bucket-A scope guard.
