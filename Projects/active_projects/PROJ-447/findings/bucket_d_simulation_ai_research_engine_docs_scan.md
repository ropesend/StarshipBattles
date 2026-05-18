# Bucket D — Simulation + AI + Research + LowLevelEngine + Assets + Docs Residue Scan (2026-05-18 supplemental)

## Summary
- Total findings: 28
- By severity: high 0, medium 11, low 17
- By category: obsolete-code 14, test-inconsistency 3, missing-functionality 4, polish 7
- Files reviewed: ~50 production (full reads on the largest simulation files and all of `game/engine/`, `game/assets/`, `game/research/`), broad grep over `game/simulation/`, `game/ai/`, all of `docs/`
- Codex seed findings status: all 4 verified current (F-D-001..F-D-004)
- Archived/active project decisions.md scanned: PROJ-371 / PROJ-427 / PROJ-429 / PROJ-431 / PROJ-434 / PROJ-435 / PROJ-436 / PROJ-269 (skim)

Deduplicated against the 9 entries in `AgentCoordination/discovered_issues/log.jsonl` and the 84 findings already in `bucket_a_data_facade.md`, `bucket_b_engine_services.md`, `bucket_c_ui_core_tests.md`. In particular, F-A-007 (ship_instance.py 839 LOC), F-A-027 (`carried_vehicle.py` historical-comment block), F-B-015 (production_engine.py `_cargo_contents` docstring), F-B-016 (`conflict_modifier_collection` Phase-7 docstring), F-C-018 (DesignLibrary static guard) cover adjacent residue and are NOT refiled here.

## Findings

### F-D-001 — `SimulationDesignLoader` class docstring instructs callers to use deleted `DesignLibrary.load_design_data()`
- **Severity**: medium
- **Category**: obsolete-code (codex seed — verified)
- **File**: `game/simulation/services/design_loader.py:39`
- **Symbol**: `SimulationDesignLoader` (class docstring)
- **Source refactor**: PROJ-427 / PROJ-434 (`DesignLibrary` → `DesignCatalog` + `DesignRepository`)
- **What survived**: Class docstring still says "Strategy layer code should use ``DesignLibrary.load_design_data()`` to get raw design data without creating Ship objects." `DesignLibrary` was deleted in PROJ-434 Phase 2. The equivalent surface is now `DesignRepository.load_design_data(design_id)` (`game/strategy/systems/design_repository.py:280`) and the workshop-facing `DesignCatalog.load_design_data` at `game/strategy/systems/design_catalog.py:236`.
- **Why it's a problem**: Direct misdirection for maintainers — the docstring names a class that does not exist, and there is no automated guard catching the lie (cross-ref Bucket C F-C-018 which proposes the static guard but does not exist yet). New simulation-layer authors trying to follow this hint will hit `ImportError`.
- **Suggested action**: Replace "use ``DesignLibrary.load_design_data()``" with "use ``DesignRepository.load_design_data(design_id)`` (or the workshop-facing ``DesignCatalog.load_design_data``)". Also drop the PROJ-30 STRAT-01 framing in the module docstring (lines 7-12) which is six-projects-old provenance, or trim to a single line.
- **Effort**: tiny

### F-D-002 — `ShipStats._phase_zero_init` comment references retired `ShipInstance.carried_items` surface
- **Severity**: low
- **Category**: polish (codex seed — verified)
- **File**: `game/simulation/entities/ship_stats.py:208-211`
- **Symbol**: `ShipStats._phase_zero_init` (inline comment block)
- **Source refactor**: PROJ-431 Phase 1f + PROJ-436 Phase 9 (`carried_items` → typed `bay_inventory.bay` / `ShipCargoManager`)
- **What survived**: The inline comment says current bay usage "depends on what's in ``ShipInstance.carried_items`` and is exposed via ``ShipInstance.bay_current_mass`` / ``ShipCargoManager.get_vehicle_bay_capacity()``". The `carried_items` field on `ShipInstance` was retired by PROJ-436 Phase 9 (`carried_items` survives only as a `_CarriedItemsProxy` shim per `ship_instance.py:583`). The canonical typed substrate is `bay_inventory.bay`, not `carried_items`.
- **Why it's a problem**: Maintainer-facing inline comment narrates a state that has been gone for >1 refactor generation. Same pattern as the already-logged F-A-027.
- **Suggested action**: Rewrite the comment to "depends on what is in ``ShipInstance.bay_inventory.bay`` and is exposed via ``ShipInstance.bay_current_mass`` / ``ShipCargoManager.get_vehicle_bay_capacity()``". Same one-word swap as F-A-027.
- **Effort**: tiny

### F-D-003 — Test failure message instructs maintainers to add entries in deleted `game/strategy/engine/commands/specs.py`
- **Severity**: medium
- **Category**: test-inconsistency (codex seed — verified)
- **File**: `tests/unit/strategy/engine/test_command_specs_contract.py:85-87`
- **Symbol**: `test_every_command_class_has_a_spec`
- **Source refactor**: PROJ-371 Phase 2 (deleted `commands/specs.py`)
- **What survived**: Assertion message reads "Add an entry in game/strategy/engine/commands/specs.py." `commands/specs.py` was deleted by PROJ-371 Phase 2; the surviving guard `tests/unit/strategy/engine/test_no_specs_tuple_literal.py:3-7` explicitly forbids reintroducing it. A maintainer hitting this test failure today would follow the message into a path that doesn't exist.
- **Why it's a problem**: Test failure message contradicts the static guard right next to it. The canonical extension path is `@command_spec(...)` decorator + per-module `register(registry)` (per `docs/systems/orders_system.md:130-137` and `:418-422`).
- **Suggested action**: Rewrite the assertion message to "Add a `@command_spec(...)` decorator on the Command DTO and a `register(registry)` call in the owning handler module (see `docs/systems/orders_system.md`)."
- **Effort**: tiny

### F-D-004 — `docs/systems/ability_reference.md` instructs maintainers to update deleted `_ACTIVATABLE_ABILITIES` constant
- **Severity**: medium
- **Category**: obsolete-code (codex seed — verified)
- **File**: `docs/systems/ability_reference.md:554`
- **Symbol**: "Add A New Activatable Planet Ability" maintainer recipe
- **Source refactor**: PROJ-429 / TD-07 Phase 3 (deleted `_ACTIVATABLE_ABILITIES`)
- **What survived**: The recipe step reads: "Add persistent energy handling to `_ACTIVATABLE_ABILITIES` in `game/strategy/engine/planet_energy_engine.py`." `_ACTIVATABLE_ABILITIES` was deleted by PROJ-429 / TD-07 — confirmed by the dead-list comment at `game/strategy/engine/planet_energy_engine.py:92` and the strategy-layer docs at `docs/systems/strategy_layer.md:697`, `:717`. The current unified discovery path is `ability_metadata.py` with `EnergyFacet(drains_energy=True)`.
- **Why it's a problem**: A maintainer following this step will fail to find the constant, then either re-create it (regressing PROJ-429) or skip the step and end up with no energy handling on a new ability. `docs/guides/adding_abilities.md:416` already states the correct path; `ability_reference.md` contradicts it.
- **Suggested action**: Replace the bullet with "Register the ability in `game/strategy/services/ability_metadata.py` with an `EnergyFacet(drains_energy=True, ...)`; the PROJ-429 unified registry is the activation-discovery surface and `ability_drains_energy(name)` / `abilities_with_kind_tag(StrategicKind.ENERGY_DRAINING)` are the consumer queries." Mirrors the `docs/guides/adding_abilities.md:416` phrasing exactly.
- **Effort**: tiny

### F-D-005 — `docs/05_ERROR_HANDLING.md` cites deleted `game/strategy/systems/design_library.py`
- **Severity**: medium
- **Category**: obsolete-code
- **File**: `docs/05_ERROR_HANDLING.md:17` and `:335`
- **Symbol**: cross-reference list and targeted pytest commands
- **Source refactor**: PROJ-434 Phase 2 (deleted `design_library.py`)
- **What survived**: Two stale references — (1) cross-reference list entry says "`game/strategy/systems/design_library.py`: `DesignLoadResult` result-object pattern" (file does not exist; `DesignLoadResult` now lives in `game/strategy/systems/design_repository.py`); (2) "Targeted references" pytest command `pytest tests/unit/strategy/design_library/test_design_load_result.py` — `tests/unit/strategy/design_library/` does not exist on disk.
- **Why it's a problem**: Documentation-first culture rule (CLAUDE.md "Update docs in the same change") violated. Reader who runs the suggested `pytest ...` will get "collected 0 items" with a path-not-found message.
- **Suggested action**: Replace both citations with the current locations: `game/strategy/systems/design_repository.py` for the `DesignLoadResult` pattern; locate the active test (likely under `tests/unit/strategy/systems/`) and update the pytest command, or drop the targeted reference if no direct test file remains.
- **Effort**: tiny

### F-D-006 — `docs/systems/production_system.md` references deleted `design_library.py` in cross-reference table
- **Severity**: low
- **Category**: obsolete-code
- **File**: `docs/systems/production_system.md:553`
- **Symbol**: "Design library" row in the file-list table
- **Source refactor**: PROJ-434 Phase 2
- **What survived**: Table cell: `| Design library | game/strategy/systems/design_library.py |`. File does not exist.
- **Why it's a problem**: Cross-reference table is supposed to be the canonical "where does this thing live" map for the production system; the file it names is gone.
- **Suggested action**: Replace with two rows or one combined row: `Design repository (engine-internal): game/strategy/systems/design_repository.py` and `Design catalog (workshop / UI-facing): game/strategy/systems/design_catalog.py`.
- **Effort**: tiny

### F-D-007 — `docs/systems/strategy_layer.md` cross-reference table lists `DesignLibrary` as a UI collaborator
- **Severity**: low
- **Category**: obsolete-code
- **File**: `docs/systems/strategy_layer.md:32`
- **Symbol**: `facade_state` row in the attribute table
- **Source refactor**: PROJ-434
- **What survived**: Row says "UI collaborators (`DesignLibrary`, etc.) share this so per-turn caches stick across opens." `DesignLibrary` is deleted; the modern UI-facing collaborator is `DesignCatalog`.
- **Why it's a problem**: Same as F-D-005/F-D-006 — names a deleted class as a current collaborator.
- **Suggested action**: Replace `DesignLibrary` with `DesignCatalog` in the parenthetical example.
- **Effort**: tiny

### F-D-008 — `docs/systems/production_system.md` shows `PlanetaryFacility` constructor with positional-keyword `consumable_levels` as an example
- **Severity**: low
- **Category**: polish
- **File**: `docs/systems/production_system.md:50-61`
- **Symbol**: `PlanetaryFacility(...)` constructor example
- **Source refactor**: PROJ-436 Phase 0 D1 (deferred fold-in)
- **What survived**: The example signature uses `consumable_levels: dict[str, float] = {}`. The convention (CLAUDE.md "Public functions and methods require return-type annotations. Use modern syntax such as `int | None`") and PROJ-436 Phase 0 D1's "keep as internal state until a concrete transfer use case justifies fold-in" decision are both still in force, but the example uses a mutable default (`{}`) — anti-pattern in Python.
- **Why it's a problem**: Mutable-default in the doc example trains maintainers to mirror that shape. Even if the real source carries it as a `field(default_factory=dict)`, the doc presentation suggests `={}` is fine.
- **Suggested action**: Either drop the default value from the example signature ("`consumable_levels: dict[str, float],`") or annotate it as `field(default_factory=dict)` to be accurate.
- **Effort**: tiny

### F-D-009 — `game/simulation/battle_runner.py` module docstring claims `BattleController` / `BattleConfig` / `BattleMode` are "slated for deletion" — they are still production
- **Severity**: low
- **Category**: obsolete-code
- **File**: `game/simulation/battle_runner.py:8-12`
- **Symbol**: module docstring
- **Source refactor**: PROJ-269 Phase 6
- **What survived**: Docstring says "The legacy `BattleController` + `BattleConfig` + `BattleMode` chain is bypassed entirely — those types are slated for deletion in the same phase." `BattleController` lives at `game/simulation/battle_controller.py:43` and is actively used by `game/app.py:366`, `game/screen_router.py:482-503`, `game/ui/screens/battle_screen.py:28`, `game/ui/screens/test_lab/screen.py:429-477`. `BattleConfig` is used in 5+ production sites including `game/simulation/managers/battle_state_manager.py:16`. The "slated for deletion in the same phase" promise has expired.
- **Why it's a problem**: Module docstring lies about the migration status. A maintainer reading "slated for deletion" might assume `BattleController` is removable and try to migrate callers off it — only to discover the visual-mode battle screen and test-lab still depend on it.
- **Suggested action**: Update the docstring to "The legacy `BattleController` + `BattleConfig` + `BattleMode` chain remains the visual-mode and replay-replay path; this entry covers headless / spec-in run_battle. A future project to retire the legacy chain remains open." Or, if there is a current plan, point at it explicitly.
- **Effort**: tiny

### F-D-010 — `IEnvironmentalHazardEngine` docstring promises `AreaEffectManager` queries — `AreaEffectManager` is deleted
- **Severity**: low
- **Category**: obsolete-code
- **File**: `game/strategy/interfaces/engines/combat.py:82` (and `:87` example)
- **Symbol**: `IEnvironmentalHazardEngine` (class docstring)
- **Source refactor**: PROJ-300 Phase 7 (deleted `AreaEffectManager`)
- **What survived**: Docstring bullet says "Querying AreaEffectManager for effects at fleet locations" and the example shows `engine = EnvironmentalHazardEngine(area_effect_manager)`. `AreaEffectManager` was deleted in PROJ-300 Phase 7 — confirmed by `game/strategy/engine/environmental_hazard_engine.py:6,58` ("no longer takes AreaEffectManager") and the deletion notes in `docs/04_SERVICES.md:602`, `docs/systems/strategy_layer.md:1134`. NOTE: this file is in `game/strategy/interfaces/engines/` not under my bucket's `game/engine/` (low-level), but the residue is in the protocol/interface layer that simulation and strategy both consume; flagging here because the bucket-B scan ended at `game/strategy/engine/` and `game/strategy/services/` and missed `game/strategy/interfaces/`.
- **Why it's a problem**: Protocol docstring promises an injection point that doesn't exist; example is uncompileable.
- **Suggested action**: Rewrite the bullet to "Querying ability_iterator / SystemEffectsCollector at fleet locations" and the example to `engine = EnvironmentalHazardEngine()` (the current constructor signature per environmental_hazard_engine.py:58).
- **Effort**: tiny

### F-D-011 — Largest simulation files exceed the 500-LOC ceiling (cluster of 13)
- **Severity**: medium
- **Category**: polish
- **File**: see table below
- **Symbol**: module-level
- **Source refactor**: cumulative
- **What survived**: 9 simulation-layer files exceed the 500-LOC ceiling:
  - `game/simulation/battle_state.py` (832 LOC)
  - `game/simulation/battle_controller.py` (831 LOC)
  - `game/simulation/systems/battle_engine.py` (758 LOC)
  - `game/simulation/battle_runner.py` (734 LOC)
  - `game/simulation/replay/replay_serialization.py` (634 LOC)
  - `game/simulation/entities/ship.py` (607 LOC)
  - `game/simulation/systems/tactical_mine_resolver.py` (597 LOC)
  - `game/simulation/entities/stat_contributors/registry.py` (570 LOC)
  - `game/simulation/entities/ship_stats.py` (559 LOC)
  - `game/simulation/components/abilities/base.py` (535 LOC)
  - `game/simulation/systems/battle_end_conditions.py` (532 LOC)
  - `game/simulation/services/vehicle_design_service.py` (516 LOC)
  - `game/simulation/combat/fleet_aura_manager.py` (515 LOC)
- **Why it's a problem**: Same convention as Bucket C F-C-027 / F-C-028 / F-A-007 / F-A-008. The two worst offenders (`battle_state.py`, `battle_controller.py`) are nearly 70% over.
- **Suggested action**: `battle_state.py` is a serialization + result-DTO module — extract `BattleState` / `ShipState` / `BattleResults` to-dict/from-dict into `battle_state_serde.py` (PROJ-372-style split, ~250 LOC drop). `battle_controller.py` is largely orchestration; extract the spec-in `start_from_spec` flow into a sibling. Same pattern at `replay_serialization.py` (split capture vs replay paths). Defer the rest to next-touch.
- **Effort**: medium per file

### F-D-012 — `game/ai/controller.py` is 470 LOC (under ceiling); `behaviors.py` 424; `carrier_controller.py` 411 — collectively approaching the ceiling
- **Severity**: low
- **Category**: polish
- **File**: see above
- **Symbol**: module-level
- **Source refactor**: cumulative
- **What survived**: AI files are all under 500 but trending close. Listed for visibility only since CLAUDE.md says "Split by responsibility when a touched file approaches that ceiling."
- **Why it's a problem**: Touch-driven natural fissure points. Not residue per se.
- **Suggested action**: No action; flag-only. Re-evaluate on next AI-layer refactor.
- **Effort**: n/a (informational)

### F-D-013 — `game/research/data/tech_tree.py:31` `load_from_json(cls, file_path: str = None)` uses legacy `str = None` instead of `str | None = None`
- **Severity**: low
- **Category**: polish
- **File**: `game/research/data/tech_tree.py:31`
- **Symbol**: `TechTree.load_from_json`
- **Source refactor**: predates PEP-604 codebase convention
- **What survived**: Public classmethod signature `file_path: str = None` — type does not allow `None` per static analysis. Sibling pattern in `game/research/data/research_tracker.py:56` (`session_seed: int = None`), `:168` (`tech_levels: Dict[str, int] = None`); `game/research/systems/research_service.py:33` (`tech_levels: Dict[str, int] = None`). Same anti-pattern as Bucket C F-C-030 but on the research side.
- **Why it's a problem**: Lying type annotation. Strict type-checkers reject; modern syntax (`str | None`) is the project convention per CLAUDE.md.
- **Suggested action**: Mechanical sweep across the 4 research-layer signatures. Same recipe as F-C-030.
- **Effort**: tiny

### F-D-014 — `game/research/data/tech_tree.py:26` `TechTree.__init__(self):` missing return annotation
- **Severity**: low
- **Category**: polish
- **File**: `game/research/data/tech_tree.py:26`
- **Symbol**: `TechTree.__init__`
- **Source refactor**: none
- **What survived**: Public class `__init__` with no annotation. (Dunder return type is exempt from the CLAUDE.md rule, but the rest of the surrounding codebase consistently annotates `__init__` as `-> None`.)
- **Why it's a problem**: Minor consistency gap with surrounding annotation density.
- **Suggested action**: Add `-> None`.
- **Effort**: tiny

### F-D-015 — `game/assets/asset_manager.py` public methods missing parameter / return annotations
- **Severity**: medium
- **Category**: polish
- **File**: `game/assets/asset_manager.py:31`, `:54`, `:70`, `:95`, `:121`
- **Symbol**: `AssetManager.__init__`, `load_manifest`, `load_image`, `load_group`, `get_random_from_group`
- **Source refactor**: predates convention tightening
- **What survived**: Cluster of public methods missing annotations: `__init__(self)`, `load_manifest(self, path=None)`, `load_image(self, category, key)`, `load_group(self, category, group_key)`, `get_random_from_group(self, category, group_key, seed_id=None)`. Each carries a docstring but no parameter/return annotations. The `category, key` pair is untyped despite being public surface used by every UI screen.
- **Why it's a problem**: Per CLAUDE.md "Public functions and methods require return-type annotations." `AssetManager` is a public service consumed across the UI layer. Untyped string-key surface is a foot-gun for typo-driven cache misses.
- **Suggested action**: Annotate the 5-method cluster: `(self, category: str, key: str) -> pygame.Surface` etc. Use `str | None = None` for the optional `path` / `seed_id`.
- **Effort**: tiny

### F-D-016 — `game/assets/asset_manager.py` carries pre-PEP-604 `Optional` typing and module-level singleton accessor pattern without annotation
- **Severity**: low
- **Category**: polish
- **File**: `game/assets/asset_manager.py:5,15`
- **Symbol**: module-level imports + `_default_asset_manager: Optional['AssetManager']`
- **Source refactor**: pre-PEP-604 codebase migration
- **What survived**: `from typing import Optional` and `_default_asset_manager: Optional['AssetManager'] = None`. Sibling of Bucket C F-C-030. Note `from __future__ import annotations` already imported (line 1) so forward refs as strings are unnecessary.
- **Why it's a problem**: Inconsistent with modern syntax convention. Also `Optional[X]` adds visual noise when `X | None` would do.
- **Suggested action**: Drop the `Optional` import and rewrite as `_default_asset_manager: "AssetManager | None" = None`. Annotation can be a bare string since `__future__` annotations are active.
- **Effort**: tiny

### F-D-017 — `game/engine/collision.py:68` and `physics.py:53` constructor params untyped
- **Severity**: low
- **Category**: polish
- **File**: `game/engine/collision.py:68`, `game/engine/physics.py:53`
- **Symbol**: `CollisionSystem.__init__(self, rng: 'random.Random' = None)`, `PhysicsBody.__init__(self, x, y, angle=0)`
- **Source refactor**: predates convention tightening
- **What survived**: `CollisionSystem.__init__(self, rng: 'random.Random' = None)` — string-quoted forward ref + legacy `= None` default; `PhysicsBody.__init__(self, x, y, angle=0)` — 3 untyped params on a base class consumed by Ship / Projectile.
- **Why it's a problem**: `game/engine/` is the foundation layer; its public surface flows into all of `game/simulation/`.
- **Suggested action**: Annotate as `(self, rng: random.Random | None = None) -> None` (with `from __future__ import annotations` if not present) and `(self, x: float, y: float, angle: float = 0) -> None`. Verify `import random` location.
- **Effort**: tiny

### F-D-018 — `game/simulation/components/component_loader.py:78` and `:186` use `file_path: str = None`
- **Severity**: low
- **Category**: polish
- **File**: `game/simulation/components/component_loader.py:78,186`
- **Symbol**: `load_components_data(file_path: str = None, ...)`, `load_modifiers_data(file_path: str = None) -> dict`
- **Source refactor**: pre-PEP-604
- **What survived**: Same anti-pattern as F-D-013. Module-level loaders that mismatch annotation against the actual `None` default.
- **Why it's a problem**: Same as F-D-013.
- **Suggested action**: `file_path: str | None = None` and ensure `-> dict | None` (or whichever) for the public `load_components_data`.
- **Effort**: tiny

### F-D-019 — `game/simulation/entities/ship_loader.py:51,118` `file_path: str = None`
- **Severity**: low
- **Category**: polish
- **File**: `game/simulation/entities/ship_loader.py:51,118`
- **Symbol**: 2 public module-level loaders
- **Source refactor**: pre-PEP-604
- **What survived**: Same as F-D-018.
- **Why it's a problem**: Same as F-D-018.
- **Suggested action**: Mechanical sweep along with F-D-013 / F-D-018.
- **Effort**: tiny

### F-D-020 — `tests/integration/research_workflow/test_workflow.py:189-192` skip-on-FileNotFoundError for `tech_tree.json` is a wallpaper
- **Severity**: low
- **Category**: test-inconsistency
- **File**: `tests/integration/research_workflow/test_workflow.py:188-192`
- **Symbol**: `test_load_real_tech_tree`
- **Source refactor**: pre-PROJ-416
- **What survived**: `try: tree = TechTree.load_from_json()` then `except FileNotFoundError: pytest.skip("Tech tree JSON not found")`. The file `data/techtree.json` exists (verified) and the test exists specifically to test loading it. Skip path is wallpaper. Sibling to Bucket C F-C-021 but the line numbers there were off-by-one (the actual `pytest.skip` is on line 192, the try is at 188). The Bucket C entry confused `tech_tree.json` (non-existent) with `techtree.json` (the real filename — `data/techtree.json`).
- **Why it's a problem**: A "real tech tree" smoke test that silently skips when the production data file is missing defeats the test's purpose. Same anti-pattern as F-A-028, F-A-029, F-C-022, F-C-023.
- **Suggested action**: Drop the try/except. Let `FileNotFoundError` fail loudly so the missing-data condition is visible.
- **Effort**: tiny

### F-D-021 — `game/ai/carrier_controller.py:275-279` historical-comment paragraph narrates "legacy carried_items / CarriedVehicle.from_any discriminator path"
- **Severity**: low
- **Category**: polish
- **File**: `game/ai/carrier_controller.py:275-279`
- **Symbol**: `_pop_carried_vehicles_legacy` (docstring)
- **Source refactor**: PROJ-431 Phase 1e
- **What survived**: Block reads "PROJ-431 Phase 1e: reads through ``carrier.bay_inventory.bay`` (homogeneous ``list[CarriedVehicle]``) and writes back via ``carrier.set_bay_inventory(...)``. The legacy ``carried_items`` / ``CarriedVehicle.from_any`` discriminator path is gone." First half is correct current-behavior description; second half is provenance narration of the deletion. Same pattern as F-A-027.
- **Why it's a problem**: Method name is `_pop_carried_vehicles_legacy` — but the method is the **modern** typed-bay path, not legacy. The "legacy" suffix is itself misleading.
- **Suggested action**: Rename to `_pop_carried_vehicles_count_based` (matches the docstring's "Legacy count-based pop" intent — the legacy is the API shape, not the substrate). Drop the second half of the docstring's PROJ-431 narration; keep only the current-behavior description.
- **Effort**: tiny

### F-D-022 — `game/simulation/entities/stat_contributors/launch.py:103-118` `contribute_vehicle_bay` docstring references `ShipInstance.carried_items`
- **Severity**: low
- **Category**: polish
- **File**: `game/simulation/entities/stat_contributors/launch.py:111`
- **Symbol**: `contribute_vehicle_bay` (docstring)
- **Source refactor**: PROJ-FMS-A Phase 3 + PROJ-436 Phase 9
- **What survived**: Docstring reads "``bay_current_mass`` is *not* set here — it is a strategy-layer property (depends on what's actually loaded into ``ShipInstance.carried_items``) and is computed via ``ShipCargoManager.get_vehicle_bay_capacity()``." Same stale name as F-D-002 — `carried_items` is `bay_inventory.bay`.
- **Why it's a problem**: Maintainer-facing surface that points at a retired field name.
- **Suggested action**: Rewrite "depends on what's actually loaded into ``ShipInstance.bay_inventory.bay``". One-word swap.
- **Effort**: tiny

### F-D-023 — `game/simulation/components/abilities/vehicle_bay.py:5` "previous drop-pod-specific carried_items flow" docstring framing
- **Severity**: low
- **Category**: polish
- **File**: `game/simulation/components/abilities/vehicle_bay.py:5`
- **Symbol**: module docstring
- **Source refactor**: PROJ-FMS-A Phase 3 + PROJ-431 Phase 1d
- **What survived**: Docstring sentence: "Generalises the previous drop-pod-specific ``carried_items`` flow into a typed substrate." The previous flow is gone and this surface is the typed substrate. "Generalises the previous" framing reads like a migration-in-progress when the migration is done.
- **Why it's a problem**: Stale provenance framing in a module docstring; a fresh reader can't tell what's current vs historical.
- **Suggested action**: Reword to "Typed substrate for design-backed vehicles (mines / fighters / satellites) stored in ``BayInventory.bay``. Mass is the capacity gate." Drop the "Generalises the previous" historical narration.
- **Effort**: tiny

### F-D-024 — `game/strategy/services/fleet_speed_calculator.py:175` docstring references retired `EnvironmentalEffects`
- **Severity**: low
- **Category**: polish
- **File**: `game/strategy/services/fleet_speed_calculator.py:175`
- **Symbol**: `calculate_fleet_speed_with_environment` (docstring)
- **Source refactor**: PROJ-300 Phase 7
- **What survived**: Docstring mentions `calculate_fleet_speed_with_environment(EnvironmentalEffects)`. `EnvironmentalEffects` was deleted in PROJ-300 Phase 7 (per `docs/systems/strategy_layer.md:1135` and `docs/04_SERVICES.md:602`). Bucket B F-B-016 covers the related `conflict_modifier_collection.py:28-31` docstring; this is the parallel reference at `fleet_speed_calculator.py:175` that B explicitly mentioned but did not refile. Strictly speaking this file lives under `game/strategy/services/` which was a Bucket B target — flagging here because B's report explicitly named it as a follow-up sibling but did not file an entry.
- **Why it's a problem**: Same as F-B-016. Docstring promises a parameter shape that hasn't existed for ~5 projects.
- **Suggested action**: Rewrite to reference the current sector-effects list from `collect_sector_effects` (paired with F-B-016's fix).
- **Effort**: tiny

### F-D-025 — `tests/static_guards/` lacks AST guard against `commands/specs.py` re-emergence (companion to F-D-003)
- **Severity**: low
- **Category**: missing-functionality
- **File**: `tests/static_guards/` (would-be guard)
- **Symbol**: missing `test_no_commands_specs_module.py`
- **Source refactor**: PROJ-371 Phase 2
- **What survived**: `tests/unit/strategy/engine/test_no_specs_tuple_literal.py` guards against the *tuple literal* anti-pattern but not against re-creating the file. A future "I'll bring back specs.py as a thin re-export" regression would pass `test_no_specs_tuple_literal.py` (which only flags tuple literals containing `CommandSpec(...)` calls) and silently re-introduce the deleted module.
- **Why it's a problem**: Sibling gap to Bucket C F-C-018 (DesignLibrary) and F-C-019 (`_ACTIVATABLE_ABILITIES`). The retirements that have **both** an AST guard against the constant and a file-existence guard are more durable; this one has only the constant guard.
- **Suggested action**: Add `tests/static_guards/test_no_commands_specs_module.py` asserting `Path("game/strategy/engine/commands/specs.py").exists() is False`. ~10 LOC.
- **Effort**: tiny

### F-D-026 — `game/simulation/services/design_loader.py:1-13` module docstring carries PROJ-30 / PROJ-45 / PROJ-50 historical provenance that no longer describes current behavior
- **Severity**: low
- **Category**: polish
- **File**: `game/simulation/services/design_loader.py:1-13`
- **Symbol**: module docstring
- **Source refactor**: PROJ-30 / PROJ-45 / PROJ-50 (long-closed)
- **What survived**: Module docstring is mostly provenance: "Part of PROJ-30: Strategy Mode Layer Boundary Cleanup (STRAT-01 fix). Previously, this functionality was incorrectly placed in DesignLibrary (strategy layer)... PROJ-45: Added specific exception handling... PROJ-50: Added registries parameter..." Each of these is many refactor generations old.
- **Why it's a problem**: Stale-provenance noise. CLAUDE.md "Update docs in the same change" implies docstrings are part of docs; multi-project archaeology is the kind of thing CLAUDE.md F-A-023 already flagged on `fleet_capability_calculator.py:7`.
- **Suggested action**: Replace with a 2-3 line description of current behavior. Drop the PROJ-30 historical framing; keep nothing older than PROJ-422.
- **Effort**: tiny

### F-D-027 — `game/simulation/entities/ship_loader.py` and `component_loader.py` — public functions in scope of the strict-DI `registries: GameRegistries` contract may pre-date PROJ-50 / PROJ-435
- **Severity**: low
- **Category**: missing-functionality
- **File**: `game/simulation/entities/ship_loader.py:51,118`, `game/simulation/components/component_loader.py:78,186`
- **Symbol**: module-level loaders
- **Source refactor**: PROJ-50 (DI), PROJ-435 (constant retirement)
- **What survived**: The bucket scan did not deep-read these but the signatures with `file_path: str = None` defaults suggest they may share the DI pattern that `SimulationDesignLoader` adopted in PROJ-50. Verify each accepts a `registries` parameter and uses it for resource catalog lookups rather than reaching for module-level singletons.
- **Why it's a problem**: Out-of-scope for a single sweep; flagging as a deep-dive candidate. Bucket scope was breadth-first.
- **Suggested action**: Open a one-shot DI audit ticket: "Confirm `ship_loader` / `component_loader` public loaders accept `registries`, route resource-catalog lookups through it, and have no `get_default_*` reach-ins."
- **Effort**: small (audit + spot-fix)

### F-D-028 — `game/simulation/battle_state.py` carries no module-level provenance, but `BattleState`, `BattleResults`, `ShipState` cumulatively serialize the entire battle outcome surface in one 832-LOC file
- **Severity**: medium
- **Category**: polish
- **File**: `game/simulation/battle_state.py:1` (file-level)
- **Symbol**: module-level
- **Source refactor**: cumulative (predates PROJ-269 unified outcome / PROJ-436 typed substrates)
- **What survived**: The file is the largest in `game/simulation/` outside the systems. Contains the BattleState dataclass, ComponentState, ShipState, BattleResults — four serialization-heavy dataclasses + matching to_dict/from_dict methods. Natural extraction targets per the `planet_serde.py` precedent (Bucket A F-A-006 / F-A-008).
- **Why it's a problem**: Sibling of F-D-011 (file-LOC ceiling) but flagged separately because the split target is clean — to_dict/from_dict logic is ~250-300 LOC and lives in 4 paired places.
- **Suggested action**: Extract serialization to `battle_state_serde.py` (PROJ-372-style). Would drop battle_state.py to roughly 530-580 LOC, still over but tractable; next pass extracts the BattleResults dataclass to a sibling.
- **Effort**: medium

---

## Additional minor findings deferred (kept under the ~50 cap)

Skim-level observations not promoted to entries:

- `game/research/__init__.py` declares no public exports; `docs/systems/research_system.md:22` says "`game.research` has no stable package-level public API exports; import concrete classes from their data/system modules." This is consistent — flagged only to confirm no residue here.
- `game/engine/__init__.py` declares a 3-class `__all__`; matches `docs/01_ARCHITECTURE.md:19` description. Consistent.
- `game/simulation/components/abilities/__init__.py` is 393 LOC of re-exports — large but not over the ceiling.
- `game/simulation/interfaces/ability_protocols.py` (359 LOC) and `entity_protocols.py` (487 LOC) — under ceiling but worth scanning if Bucket C F-C-030 (`Dict/List/Optional` annotation modernization) is acted on, since these protocols are sibling surface.
- `docs/02_PATTERNS.md:984` and `:1238` reference `_cargo_contents` as a current substrate. The dataclass field `_cargo_contents` IS still present on `ShipInstance` (`ship_instance.py:164`) so the doc text is accurate today; cross-ref F-A-005 (the @property cluster slated for retirement). Re-evaluate the docs lines when F-A-005 retires.
- The `# noqa: F401` re-exports in `game/ai/__init__.py` were not audited; if a Bucket C-style F-A-021 sweep is run, the AI package surface is the natural sibling scan target.

Stop here per the supplemental-bucket scope and the ~50-finding cap (28 high-quality findings preserved; no padding).
