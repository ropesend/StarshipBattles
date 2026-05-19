# PROJ-445 Phase 3: Annotation + ratchet test polish

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-445 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** Phase 2 complete (recommended; not strictly required — Phase 3 tasks are independent)
**Objective:** Mechanical polish across the engine + services layer: 6 missing return annotations on public methods/properties, 1 stale `IProductionResourceSource` docstring referencing retired `_cargo_contents`, 1 stale `conflict_modifier_collection` Phase-7 docstring, 1 `# type: ignore` masking a real annotation gap, 2 dead `pytest.skip` import guards in superweapon registry contract tests.

**Cross-bucket file-ownership rule:** Only edit `game/strategy/engine/`, `game/strategy/services/`, and engine/services-subject tests.

**Source-of-truth findings:** [`findings/bucket_b_engine_services_scan.md`](findings/bucket_b_engine_services_scan.md) — F-B-006, F-B-007, F-B-008, F-B-009, F-B-010, F-B-011, F-B-012, F-B-015, F-B-016, F-B-021.

---

## Tasks

### Task 3.1: F-B-006 — Annotate _get_system_at_hex, drop type: ignore [Simple]
**File:** `game/strategy/engine/superweapon_order_processor.py:343`

- [ ] Read the existing line: `def _get_system_at_hex(galaxy, location):  # type: ignore[no-untyped-def]`
- [ ] Read the sibling `GalaxyPathfindingService.get_system_at_hex` to find the canonical return type annotation
- [ ] **GREEN**: Change to `def _get_system_at_hex(galaxy: Any, location: HexCoord) -> Optional["StarSystem"]:`. Drop the `# type: ignore` comment.
- [ ] If type-checker still complains: investigate root cause; do not re-add the `type: ignore`.
- [ ] No test change needed; this is pure annotation polish.

### Task 3.2: F-B-007 + F-B-008 — Annotate event_bus parameters on engine __init__s [Simple]
**Files:** `game/strategy/engine/order_processor.py:64` (`OrderProcessor.__init__`); `game/strategy/engine/superweapon_order_processor.py:56` (`SuperweaponOrderProcessor.__init__`)

- [ ] F-B-007: Change `def __init__(self, event_bus=None):` → `def __init__(self, event_bus: Optional[Any] = None) -> None:`. Match `BaseOrderHandler.__init__` pattern. Add `Optional` import or use modern `Any | None` syntax matching existing module conventions.
- [ ] F-B-008: Change `def __init__(self, event_bus=None, empire_mutator=None, nav_service=None):` → `def __init__(self, event_bus: Optional[Any] = None, empire_mutator: Optional[Any] = None, nav_service: Optional[Any] = None) -> None:`.
- [ ] No test change needed.

### Task 3.3: F-B-009 — Annotate resolve_requested return [Simple]
**File:** `game/strategy/engine/handlers/fms_shared.py:94`

- [ ] Read existing `def resolve_requested(count, count_available: int):`
- [ ] **GREEN**: Change to `def resolve_requested(count: Optional[int], count_available: int) -> int | ValidationResult:`. Add the import for `ValidationResult` if not present.
- [ ] No test change.

### Task 3.4: F-B-010 — Annotate TurnEngine.planet_modifier_effect_engine [Simple]
**File:** `game/strategy/engine/turn_engine.py:521`

- [ ] Read the sibling `TurnEngine.water_engine` at line 516 for the canonical pattern (`-> "WaterEngine":` with string forward ref)
- [ ] **GREEN**: `def planet_modifier_effect_engine(self) -> "PlanetModifierEffectEngine":`
- [ ] No test change.

### Task 3.5: F-B-011 — Annotate 4 _get_*_mutator accessors [Simple]
**Files:** `game/strategy/engine/harvesting_engine.py:196`, `game/strategy/engine/atmosphere_engine.py:30`, `game/strategy/engine/planet_modifier_effect_engine.py:34`, `game/strategy/engine/production_spawner.py:101`

- [ ] Read the canonical pattern at `BaseOrderHandler._get_planet_mutator` at `game/strategy/engine/order_handlers/base.py:137` — uses `-> Any`
- [ ] **GREEN**: Annotate each of the 4 accessors as `-> Any`. Use the concrete protocol type if it's trivially known; default to `-> Any` to match the existing sibling pattern.
- [ ] No test change.

### Task 3.6: F-B-012 — Delete dead pytest.skip ImportError guards [Simple]
**File:** `tests/unit/strategy/services/test_superweapon_registry_contract.py:154, 178`
**Tests:** `pytest tests/unit/strategy/services/test_superweapon_registry_contract.py -v`

- [ ] Read both `try: from game.strategy.engine.commands.registry import command_registry, seed_default_commands ... except ImportError: pytest.skip("PROJ-371 command_registry not available")` blocks
- [ ] **GREEN**: Remove both `try / except ImportError` guards. Hoist the import to the top of the test module. Let `ImportError` fail loudly if the module ever disappears.
- [ ] Run targeted tests; both must pass.

### Task 3.7: F-B-015 — Update IProductionResourceSource docstring _cargo_contents → ShipCargoManager [Simple]
**File:** `game/strategy/engine/production_engine.py:68`

- [ ] Read existing docstring text mentioning `Fleet` over its `_cargo_contents` substrate
- [ ] **GREEN**: Replace with `Fleet` over its typed cargo manager (`ShipCargoManager`). One-word swap.
- [ ] No test change.

### Task 3.8: F-B-016 — Drop stale Phase-7-deletes-legacy-path docstring [Simple]
**File:** `game/strategy/engine/conflict_modifier_collection.py:28-31` (also coordinate with PROJ-447 F-D-024 sibling at `game/strategy/services/fleet_speed_calculator.py:175`)

- [ ] Read existing `lookup_environmental_effects` docstring claiming dual-shape acceptance
- [ ] **GREEN**: Rewrite to state that the function returns a sector-effects list from `collect_sector_effects`. Drop the "either / or" phrasing.
- [ ] **Pull in PROJ-447 F-D-024**: Update `game/strategy/services/fleet_speed_calculator.py:175` docstring in the same PR. PROJ-447's plan says to fold this sibling site into F-B-016. The file is in your bucket (`game/strategy/services/`); editing it is in-scope.
- [ ] No test change.

### Task 3.9: F-B-021 — Annotate ReplayStore._iter_replay_files [Simple]
**File:** `game/strategy/services/replay_store.py:434`

- [ ] **GREEN**: `def _iter_replay_files(rd: Path) -> Iterator[Path]:`. Add `Iterator` import if not present.
- [ ] No test change.

---

## Phase Completion Checklist

- [ ] All 9 task groups complete
- [ ] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-445 3` — PASSED
- [ ] Update status to `Complete`; plan.md phase table + Current State → Phase 4
- [ ] PROJ-447 F-D-024 marked `Complete` in PROJ-447's phase_2_checklist.md (since you closed it here)

## Notes

- Pure mechanical polish phase. No behavior change. If a type-checker complains during annotation, investigate root cause rather than silencing.
- Phase 4 (service-layer shim retirements + PROJ-368 facade unwinding) is the final phase.
