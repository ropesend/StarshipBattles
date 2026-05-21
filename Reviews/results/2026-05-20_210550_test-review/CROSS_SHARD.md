# Cross-Shard Duplicate Report

## Summary
- Shard reports analyzed: 16
- Cross-shard duplicates found: 6
- Helper duplications found: 6

---

## Cross-Shard Duplicates

### DUP-001: `_make_fleet` + `_make_empire` helpers near-identical across combat round budget tests
- **SUT**: `ConflictResolutionEngine.resolve_all_conflicts` (unit), `TurnEngine` round budget (integration), round budget benchmark (perf)
- **Shard 01**: `tests/integration/strategy/test_combat_round_budget.py:75-91` — `_make_fleet(fleet_id, owner_id, location, speed)` + `_make_empire(empire_id, fleets)` both ~10-line MagicMock constructors
- **Shard 16**: `tests/performance/test_contested_hex_round_budget.py:60-76` — `_make_fleet(fleet_id, owner_id, location, speed=5)` + `_make_empire(empire_id, fleets)` same body, same fields
- **Shard 11**: `tests/unit/strategy/engine/test_conflict_round_budget.py:35-51` — `_make_fleet(fleet_id, owner_id, location, speed, orders=None)` slightly extended (adds `orders`) but same core structure
- **Similarity**: Near-identical (same fields, same mock pattern, 90% shared code)
- **Recommendation**: Consolidate into `tests/conftest.py` shared helper (already has analogous `make_mock_ship_instance` per PROJ-40). Move `_make_fleet` to shared location accepting kwargs for per-context fields.
- **Estimated LOC savings**: ~60

### DUP-002: `_draw_setup` + `_stub_fonts` helper patterns used identically in two battle panel test files
- **SUT**: `game.ui.panels.battle_panels.BattlePanel.draw`
- **Shard 02**: `tests/unit/ui/test_battle_panels_characterization.py:419-433` — `_draw_setup` creates panel+screen mocks, `_stub_fonts` patches `get_default_font`
- **Shard 14**: `tests/unit/ui/test_battle_panels_extended.py:36-69` — `_install_battle_panels_pygame_mock` does `sys.modules` replacement + `importlib.reload`; then `TestBattlePanelBaseClass.setup_mocks` (line 482) duplicates the same pygame patching without using the shared helper
- **Similarity**: Both test files construct the same `BattlePanel` class with mocks, verifying draw behavior. `test_battle_panels_extended.py` contains a CAT-9 finding (line 474-520) for not reusing its own `_install_battle_panels_pygame_mock` helper.
- **Recommendation**: Merge `test_battle_panels_characterization.py` into `test_battle_panels_extended.py` or extract a shared `@pytest.fixture` that provides a pre-mocked `battle_panels` module.
- **Estimated LOC savings**: ~70

### DUP-003: Ship serialization roundtrip test pattern duplicated across different SUTs but with identical assertion structure
- **SUT**: `Ship.to_dict()` / `Ship.from_dict()` (SHARD_11) and `ShipIO.save_ship()` / `load_ship()` (SHARD_08)
- **Shard 08**: `tests/unit/ui/services/test_ship_io.py:395-541` — 7 near-identical round-trip tests (`test_round_trip_preserves_ship_name`, `_ship_class`, `_team_id`, `_color`, `_component_count`, `_movement_policy`, `_recalculates_stats`)
- **Shard 11**: `tests/unit/simulation/entities/test_ship_serialization.py:328-419` — 5 identical-structure roundtrip tests (`preserves_name`, `_ship_class`, `_theme_id`, `_team_id`, `_color`)
- **Similarity**: Identical pattern: `ship.to_dict()` → `Ship.from_dict(data, registries=...)` → assert single property. 4 of 5 properties tested in both files (name, class, team_id, color). `test_ship_io.py` adds component_count and movement_policy.
- **Recommendation**: Keep `test_ship_serialization.py` for raw Ship serialization tests. Remove overlapping property-preservation tests from `test_ship_io.py`, keeping only the IO-layer-specific tests (file read/write, temp_path handling).
- **Estimated LOC savings**: ~80

### DUP-004: `ship.to_dict()` → `ship.from_dict()` roundtrip for ShipInstance also duplicated
- **SUT**: `ShipInstance.to_dict()` / `ShipInstance.from_dict()`
- **Shard 01**: `tests/unit/strategy/fleets/test_ship_instance_roundtrip.py` — roundtrip tests via fleet save/load
- **Shard 16**: `tests/unit/strategy/ship_instance/test_ship_instance_serializer.py` — `ShipInstanceSerializer` roundtrip tests
- **Shard 16**: `tests/unit/strategy/ship_instance/test_serialization.py` — `ShipInstance.to_dict()` / `from_dict()` direct tests
- **Similarity**: All three test ShipInstance serialization fidelity. `test_ship_instance_roundtrip.py` (SHARD_01) and `test_serialization.py` (SHARD_16) both test dict roundtrip with the same assertion pattern (assert original.x == roundtripped.x).
- **Recommendation**: Move all ShipInstance serialization tests into a single file. `test_ship_instance_serializer.py` tests the Serializer adapter, which is distinct and should stay separate.
- **Estimated LOC savings**: ~40

### DUP-005: `_make_colony` / `_make_planet` / `_make_empire` helper proliferation across strategy engine tests
- **SUT**: Various strategy engine sub-engines (harvesting, resupply, energy, action, etc.)
- **Shard 03**: `tests/unit/strategy/engine/test_planet_action_engine.py:91` — `_make_empire(colonies=None)`
- **Shard 05**: `tests/unit/strategy/engine/test_harvesting_engine.py:27` — `_make_empire(colonies=None, resource_pool=None, max_storage=None, empire_id=0)`
- **Shard 09**: `tests/unit/strategy/engine/test_planet_energy_engine.py:64` — `_make_empire(colonies=None)`
- **Shard 10**: `tests/unit/strategy/engine/test_resupply_engine.py:95` — `_make_empire(colonies=None)`
- **Shard 06**: `tests/unit/strategy/engine/test_component_activation_engine.py:41` — `_make_empire(colonies=None)`
- **Shard 04**: `tests/unit/strategy/engine/test_environmental_hazard_engine.py:61` — `_make_empire(empire_id=0, fleets=None)`
- **Similarity**: At least 6 files define `_make_empire(colonies=None)` with identical implementation pattern (create Empire, attach mock colonies). Each file also defines a `_make_colony()` or `_make_planet()` helper. The `tests/unit/strategy/engine/` directory has no shared conftest.py, forcing each test file to reinvent these mocks.
- **Recommendation**: Create `tests/unit/strategy/engine/conftest.py` with shared fixture factories (`mock_empire_factory`, `mock_colony_factory`). The existing `tests/unit/strategy/engine/conftest.py` (SHARD_16) currently contains only one fixture (`economy_calculator`).
- **Estimated LOC savings**: ~180

### DUP-006: Stub `Modifier` classes duplicated across builder/worskhop/test_utils test files
- **SUT**: Ship design modifier display and selection logic
- **Shard 07**: `tests/unit/ui/screens/builder/test_modifier_utils.py:10-17` — `_Modifier` and `_SpecialModifier` stub classes
- **Shard 07**: `tests/unit/ui/screens/test_workshop_viewmodel_selection.py` — similar stub classes
- **Shard 07**: `tests/unit/ui/screens/test_builder_selection.py` — similar stub classes
- **Shard 02**: `tests/unit/modifiers/test_propulsion_ability_bindings.py:13-186` — three classes with identical `test_*_has_*_binding`, `test_*_get_consumed_stats`, `test_*_recalculate` patterns (CAT-4 flagged)
- **Similarity**: The `_Modifier` stub pattern (simple class with `id`, `name`, `operation`, `value`, `primary_scalar` attrs) is redefined locally in 3+ test files in Shard 07 alone. CAT-9 noted in SHARD_07 report (line 98).
- **Recommendation**: Extract to a shared fixture module (e.g., `tests/fixtures/modifier_stubs.py`). Already suggested by SHARD_07 reviewer but needs cross-shard consolidation to include SHARD_02's `test_propulsion_ability_bindings.py`.
- **Estimated LOC savings**: ~40

---

## Cross-Shard Helper Duplication

### HLP-001: `MockGameSession`
- **Defined in** (5 identical copies, 4 different shards):
  - `tests/unit/strategy/save_game_service/conftest.py:12` — SHARD_16
  - `tests/unit/strategy/save_game_service/test_save_load_ops.py:24` — SHARD_16 (duplicate of conftest in same dir!)
  - `tests/unit/strategy/save_game_service/test_error_handling.py:24` — SHARD_07
  - `tests/unit/ui/test_save_selection.py:36` — SHARD_03
  - `tests/unit/strategy/test_auto_save.py:14` — SHARD_15
- **Identicality**: Identical `__init__` (config, turn_number, num_empires → MagicMock empires with id/name), identical `to_dict()` method (same dict structure with `turn_number`, `save_path`, `config`, `galaxy`, `empires`, `human_player_ids`). The conftest copy and `test_save_load_ops` copy are byte-for-byte identical.
- **Recommendation**: Delete all local copies. Import from `tests/unit/strategy/save_game_service/conftest.py` (or move to a higher-level shared conftest). The conftest is the natural single source of truth for its directory.
- **Estimated LOC savings**: ~110

### HLP-002: `MockPlanetType(Enum)`
- **Defined in** (10+ files, 8 different shards):
  - `tests/unit/strategy/turn_engine/conftest.py:18` — SHARD_03 (module-level, one value: CONTINENTAL)
  - `tests/integration/strategy/turn_engine/conftest.py:125` — SHARD_04 (inline in method)
  - `tests/unit/strategy/validation/test_colonize_validator.py:21` — SHARD_06 (module-level, three values)
  - `tests/integration/colonization/test_planet_specific_colonization.py:33` — SHARD_09 (module-level, three values)
  - `tests/integration/strategy/test_commands.py:18,154` — SHARD_09 (module-level + inline in method)
  - `tests/integration/ui/test_colonization_facade.py:71,377,438,488,571,625,675,724,787` — SHARD_04 (inline in 8 methods, noted CAT-9)
  - `tests/unit/ui/screens/test_strategy_colonization.py:21` — SHARD_12 (inline)
  - `tests/unit/strategy/test_engine_event_emission.py:440,540,938,999` — SHARD_02 (inline in 4+ classes)
  - `tests/unit/strategy/test_fleet_order_processor.py:157,282,484` — SHARD_15 (inline in 3+ classes)
- **Identicality**: Same two-field Enum (ICE_DWARF, CONTINENTAL) repeated verbatim. Some variants add ARID or DYSON_SPHERE. Same pattern, same purpose (mock planet type for colonize/facade/menu item tests).
- **Recommendation**: Define a single `MockPlanetType` in a shared fixture module (e.g., `tests/fixtures/colonization_fixtures.py` or `tests/conftest.py`). The turn_engine conftest version with only CONTINENTAL is the minimal fit — extend it to include ICE_DWARF and use everywhere.
- **Estimated LOC savings**: ~80

### HLP-003: `make_mock_ship_instance` — local redefinitions despite canonical copy in root conftest
- **Defined in** (canonical + 4 local copies, 5 shards):
  - `tests/conftest.py:350` — SHARD_03 (canonical, PROJ-40 consolidated)
  - `tests/integration/ui/test_fleet_build_button.py:12` — SHARD_15 (adds `has_yard` param; otherwise identical to canonical)
  - `tests/integration/ui/test_strategy_buttons.py:13` — SHARD_16 (identical except variable naming order)
  - `tests/unit/strategy/test_advanced_fleet_orders.py:20` — SHARD_08 (nearly identical; uses `registries=None` same pattern)
  - `tests/repro_issues/test_bug_27_ordertype.py:12` — SHARD_15 (identical signature to canonical)
- **Identicality**: All create a `ShipInstance` with `instance_id`, `design_id`, `name`, `owner_id`, `design_data` in the same order. All accept `registries` for DI. The root conftest is intentionally the canonical version per PROJ-40.
- **Recommendation**: Delete local copies; import from root conftest. For `test_fleet_build_button.py` which adds `has_yard`, extend the canonical helper to accept `**kwargs` or add the parameter.
- **Estimated LOC savings**: ~60

### HLP-004: `_make_fleet` — 43+ definitions with overlapping signatures
- **Defined in** (43 files total; key clusters with near-identical signatures):
  - `tests/integration/strategy/test_combat_round_budget.py:75` — SHARD_01 (MagicMock with id, owner_id, location, speed, ships, task_forces, orders)
  - `tests/integration/strategy/test_three_empire_battle.py:63` — SHARD_06 (same fields, no orders)
  - `tests/performance/test_contested_hex_round_budget.py:60` — SHARD_16 (same fields, no orders)
  - `tests/unit/strategy/combat/test_battle_assembly_third_party_mines.py:33` — SHARD_02 (similar)
  - `tests/unit/strategy/combat/test_battle_assembly.py:33` — SHARD_07 (similar)
  - `tests/unit/strategy/engine/test_superweapon_event_payloads.py:63` — SHARD_04 (MagicMock with single loc param)
  - `tests/unit/strategy/engine/test_superweapon_order_pop_matrix.py:66` — SHARD_06 (same)
  - `tests/unit/strategy/engine/test_environmental_hazard_engine.py:43` — SHARD_02 (MagicMock with more fields)
  - `tests/unit/strategy/adapters/test_simulation_adapter.py:33` — SHARD_04 (real Fleet-friendly mock)
  - `tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py:48` — SHARD_07 (similar)
- **Identicality**: Varies — not identical byte-for-byte but ~70% of these create `MagicMock()` with `fleet.id`, `fleet.owner_id`, `fleet.location`, `fleet.speed`, `fleet.ships`, and `fleet.orders` set. Many differ only in whether they include `orders` or `task_forces`.
- **Recommendation**: Create `tests/conftest.py:_make_mock_fleet(**overrides)` that produces a MagicMock with the common 6 fields. Test files override specific fields via kwargs. This is lower priority (signatures differ in appropriate ways) but the 43-definitions proliferation suggests even the partially-similar ones would benefit from consolidation into 3-4 canonical factories.
- **Estimated LOC savings**: ~200 (if all 43 reduced to ~8 canonical factories)

### HLP-005: `auto_save pytest.fixture(autouse=True)` + `setup_tmpdir` fixture pattern duplicated
- **Defined in** (identical name and autouse pattern):
  - `tests/unit/strategy/save_game_service/test_save_load_ops.py:57` — SHARD_16 (creates tempdir, patches Paths.SAVES_DIR)
  - `tests/unit/strategy/save_game_service/test_error_handling.py:58` — SHARD_07 (same pattern)
  - `tests/unit/strategy/test_auto_save.py:48` — SHARD_15 (same pattern)
  - `tests/unit/ui/test_save_selection.py:65` — SHARD_03 (named `_patched_saves_tmpdir`, same logic)
- **Identicality**: All four create temporary directories via `tempfile.mkdtemp()`, patch `Paths.SAVES_DIR`, yield, then `shutil.rmtree()`. Identical 10-line pattern.
- **Recommendation**: Move to `tests/conftest.py` as a session-scoped fixture (or a reusable context manager). The save_game_service conftest already has the canonical `setup_tmpdir` at line 42.
- **Estimated LOC savings**: ~30

### HLP-006: `_make_empire(colonies=None)` pattern duplicated
- **Defined in** (6 files with the same `colonies=None` signature, 6 shards):
  - `tests/unit/strategy/engine/test_planet_action_engine.py:91` — SHARD_03
  - `tests/unit/strategy/engine/test_harvesting_engine.py:27` — SHARD_05 (extended with more params)
  - `tests/unit/strategy/engine/test_planet_energy_engine.py:64` — SHARD_09
  - `tests/unit/strategy/engine/test_resupply_engine.py:95` — SHARD_10
  - `tests/unit/strategy/engine/test_component_activation_engine.py:41` — SHARD_09
  - `tests/unit/strategy/data/test_empire.py:17` — SHARD_07
- **Identicality**: All create an `Empire` with `empire_id`, `resource_pool` dict, and assign mock colonies. 4 of 6 use identical `_make_empire(colonies=None)` signature and body.
- **Recommendation**: Extract to `tests/unit/strategy/engine/conftest.py` (already exists at line 13 with one fixture). Add a shared `mock_empire` fixture factory.
- **Estimated LOC savings**: ~50

---

## Additional Observations

### Cross-Shard SUT Coverage Overlap (not duplicates, but note-worthy adjacency)

These are files in different shards testing the same production class/method — not duplicates (they test different aspects), but noted for awareness if future consolidation is considered:

| SUT | Shard A | Shard B | Overlap |
|-----|---------|---------|---------|
| `Ship.stats` / `ShipStatsStrategy` | SHARD_01: `test_ship_stats_strategy_attributes.py` | SHARD_07: `test_ship_stats.py` | Similar stat-aggregation tests |
| `ConflictResolutionEngine` | SHARD_05: `test_battle_engine_tick.py` | SHARD_11: `test_conflict_round_budget.py` | Tick count / round budget tested separately but related |
| `FleetAuraManager` | SHARD_07: `test_fleet_aura_cache.py` | SHARD_14: `test_fleet_aura_provider_identity.py` | Same class, different subsystems |
| `WorkshopScreen.handle_event` | SHARD_01: `test_workshop_screen.py` | SHARD_06: `test_workshop_event_router_select_component.py` | Event routing tested in both |
