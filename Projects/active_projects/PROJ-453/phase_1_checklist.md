# PROJ-453 Phase 1: Engine + services mechanical polish sweep

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-453 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Burn down 10 mechanical <30-LOC polish items in `game/strategy/engine/` + `game/strategy/services/`. Each task is self-contained; no inter-task dependencies. Order doesn't matter — check off as completed. The phase exists primarily to reduce noise during PROJ-454's larger retirement sweeps (Codex r4 redesign #5 → #6).

**Cross-bucket file-ownership rule:** This phase only touches files listed in [manifest.md](manifest.md). Do NOT touch any file PROJ-452 / PROJ-454 / PROJ-455 owns. Sibling projects are running in parallel.

**Source-of-truth findings:** [`findings/PROJ-453_findings.md`](findings/PROJ-453_findings.md) — read each finding's full text (severity, source refactor, what survived, why it's a problem, suggested action) before starting that task.

**TDD recipe per task:** For annotation-only changes, RED-then-GREEN is awkward (the change is pure type-hint, not behaviour). Use this recipe instead:
1. Read the current signature, confirm the gap matches the finding text.
2. Apply the annotation; run `pytest tests/unit/strategy/engine/<owning-module>.py -q` (or services equivalent) to confirm no behaviour regression.
3. Check off the task.

For F-B-012 (skip-guard deletion), the proper RED is git-stash-the-change, run the test, observe it still skips (or, after deletion, the import would fail — temporarily mutate `command_registry` import path to confirm the test now fails hard instead of silently skipping), then restore the deletion.

For F-B-015 / F-B-016 (stale docstrings), no behaviour test is feasible; verify the new text matches the current code surface and run targeted tests for the owning module to confirm import + class shape still load.

---

## Tasks

### Task 1.1: F-B-006 — annotate `SuperweaponOrderProcessor._get_system_at_hex`; drop `# type: ignore` [Simple]
**File:** `game/strategy/engine/superweapon_order_processor.py:340`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py -q`

- [ ] Read existing signature: `def _get_system_at_hex(galaxy, location):  # type: ignore[no-untyped-def]`
- [ ] Verify the imports at top of file include `Any` (likely) and `HexCoord`. If `Optional["StarSystem"]` requires a TYPE_CHECKING import, follow the existing pattern in the file (`if TYPE_CHECKING:` block).
- [ ] **GREEN**: Change to `def _get_system_at_hex(galaxy: Any, location: HexCoord) -> Optional["StarSystem"]:` (matching `GalaxyPathfindingService.get_system_at_hex` signature shape).
- [ ] Drop the `# type: ignore[no-untyped-def]` comment.
- [ ] Run targeted tests; confirm green.
- [ ] Verify: `rg -n "type: ignore" game/strategy/engine/superweapon_order_processor.py` returns no match for this line.

**Notes:** [Empty until implementation.]

---

### Task 1.2: F-B-007 — type `OrderProcessor.__init__` [Simple]
**File:** `game/strategy/engine/order_processor.py:64`
**Tests:** `pytest tests/unit/strategy/engine/ -q` (no dedicated `test_order_processor.py` file; the `OrderProcessor` surface is exercised by `tests/unit/strategy/test_fleet_order_processor.py`, `tests/unit/strategy/engine/test_order_processor_colonize.py`, `tests/unit/strategy/engine/test_order_processor_transfer.py`, `tests/unit/strategy/engine/test_order_processor_instant.py`, `tests/unit/strategy/engine/test_order_processor_no_legacy_helpers.py`, `tests/unit/strategy/engine/test_order_processor_fleet_merge.py`, and `tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py`. The broader engine path covers all of them.)

- [ ] Read existing signature: `def __init__(self, event_bus=None):`
- [ ] **GREEN**: Change to `def __init__(self, event_bus: Optional[Any] = None) -> None:`. Confirm `Optional` and `Any` are already in the typing imports at the top of the file (lines ~24-25 already import these per the current code shape).
- [ ] Run targeted tests.

**Notes:**

---

### Task 1.3: F-B-008 — type `SuperweaponOrderProcessor.__init__` [Simple]
**File:** `game/strategy/engine/superweapon_order_processor.py:56`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py -q`

- [ ] Read existing signature: `def __init__(self, event_bus=None, empire_mutator=None, nav_service=None):`
- [ ] **GREEN**: Change to `def __init__(self, event_bus: Optional[Any] = None, empire_mutator: Optional[Any] = None, nav_service: Optional[Any] = None) -> None:`. Use `Any` for the protocol-typed kwargs to match the established pattern in `BaseOrderHandler.__init__`.
- [ ] Run targeted tests.

**Notes:**

---

### Task 1.4: F-B-009 — annotate `resolve_requested` return + count param [Simple]
**File:** `game/strategy/engine/handlers/fms_shared.py:94`
**Tests:** `pytest tests/unit/strategy/engine/handlers/ -q`

- [ ] Read existing signature: `def resolve_requested(count, count_available: int):` plus the docstring at lines 95-99.
- [ ] Verify `ValidationResult` is imported at the top of the file. (It is — `from game.core.validation import ValidationResult`.) If `Optional` is not in the typing imports, add it.
- [ ] **GREEN**: Change to `def resolve_requested(count: Optional[int], count_available: int) -> int | ValidationResult:`. Use `int | ValidationResult` (PEP-604) per the new-code convention in `docs/03_CONVENTIONS.md`.
- [ ] Run targeted tests for any planet-FMS handler that calls `resolve_requested` (`test_recover_fighters.py`, `test_lay_mines.py`, etc.).

**Notes:** The function is in `__all__` at fms_shared.py:107-109 so this is a public-surface annotation, not a private-helper one.

---

### Task 1.5: F-B-010 — annotate `TurnEngine.planet_modifier_effect_engine` [Simple]
**File:** `game/strategy/engine/turn_engine.py:521`
**Tests:** `pytest tests/unit/strategy/turn_engine/ -q`

- [ ] Read existing property at lines 520-529: `@property` then `def planet_modifier_effect_engine(self):`
- [ ] Compare with sibling at line 516: `def water_engine(self) -> 'IWaterEngine':` — note the string-forward-ref pattern.
- [ ] **GREEN**: Change to `def planet_modifier_effect_engine(self) -> "PlanetModifierEffectEngine":` (string forward ref; the actual import is in the property body to avoid the layer-cycle the property was introduced to break).
- [ ] Run targeted tests.

**Notes:**

---

### Task 1.6: F-B-011 — annotate six `_get_*_mutator` accessors as `-> Any` [Simple]
**Files:**
- `game/strategy/engine/harvesting_engine.py:196` (`_get_planet_mutator`) + `:205` (`_get_empire_mutator`)
- `game/strategy/engine/atmosphere_engine.py:30` (`_get_planet_mutator`)
- `game/strategy/engine/planet_modifier_effect_engine.py:34` (`_get_planet_mutator`)
- `game/strategy/engine/production_spawner.py:101` (`_get_planet_mutator` — grep on 2026-05-19 confirms the accessor at this line is `_get_planet_mutator`, not `_get_ship_mutator` as listed in some manifest entries; annotate the live signature regardless of which mutator name appears)
- `game/strategy/engine/environmental_hazard_engine.py:65` (`_get_ship_mutator` — added by codex audit 2026-05-19; same shape as the others, lazy-defaults `ShipInstanceWriteService`)
- `game/strategy/engine/superweapon_order_processor.py:70` (`_get_empire_mutator` — added by codex audit 2026-05-19; same shape, lazy-defaults `EmpireWriteService`)

**Tests:** `pytest tests/unit/strategy/engine/ -q -k "harvesting or atmosphere or planet_modifier or production_spawner or environmental_hazard or superweapon"`

- [ ] **Verify count**: `rg -n "def _get_.*_mutator" game/strategy/engine/` to confirm all sites and exact line numbers. The original finding cited four; the codex audit (2026-05-19) added two more (`environmental_hazard_engine.py:65`, `superweapon_order_processor.py:70`) for a total of six. Verify before editing — annotated accessors elsewhere (e.g., `fleet_movement_engine.py:81`, `organics_consumption_engine.py:70`, `planet_energy_engine.py:167`, and `order_handlers/base.py:137,146`) already have the typed return and are out of scope.
- [ ] For each accessor, change the signature from `def _get_X_mutator(self):` to `def _get_X_mutator(self) -> Any:`. Use `Any` (not the concrete write-service type) to keep the change purely annotation — no new imports required if `Any` is already imported (verify per file).
- [ ] If `Any` is missing from the typing imports in any of the six files, add it.
- [ ] Note: `superweapon_order_processor.py:78` also has an untyped `_get_nav_service` accessor of the same lazy-default shape. It is NOT a `_mutator` accessor; treat as out of scope for F-B-011 (different naming and different finding family). If you want to address it, log a fresh DI entry.
- [ ] Run targeted tests.

**Notes:** Mirror the established pattern in `BaseOrderHandler._get_planet_mutator` at `game/strategy/engine/order_handlers/base.py:137` (already annotated `-> Any`).

---

### Task 1.7: F-B-012 — delete two dead `try / except ImportError → pytest.skip` guards [Simple]
**File:** `tests/unit/strategy/services/test_superweapon_registry_contract.py:148-154, 172-178`
**Tests:** `pytest tests/unit/strategy/services/test_superweapon_registry_contract.py -v`

- [ ] Read the two guard blocks. Both wrap `from game.strategy.engine.commands.registry import command_registry, seed_default_commands` in `try / except ImportError` and call `pytest.skip(...)` on the exception path.
- [ ] **RED equivalence check**: Confirm by inspection that the import works today (no ImportError raised). `python -c "from game.strategy.engine.commands.registry import command_registry, seed_default_commands; print('ok')"` should print `ok`. The guards are unreachable.
- [ ] **GREEN**: Promote the import to a top-of-test or top-of-class statement (the same import lines, without the `try / except` wrapper). Delete the `except ImportError: pytest.skip(...)` block in both methods.
- [ ] Run targeted tests; confirm both `test_order_types_match_command_specs` and `test_ability_names_match_command_specs` still pass (now without the skip path).
- [ ] **Sanity check**: temporarily break the import in your working copy (e.g., mutate the module path), run the test, observe a hard `ImportError` rather than a silent skip. Revert the break.

**Notes:** Removing the guard is the explicit intent of the finding — the skip silently masked legitimate import breakage.

---

### Task 1.8: F-B-015 — fix `_cargo_contents` → `ShipCargoManager` in `IProductionResourceSource` docstring [Simple]
**File:** `game/strategy/engine/production_engine.py:80`

- [ ] Read the docstring block at lines 60-95 around `IProductionResourceSource.production_consume_resource`.
- [ ] **GREEN**: Replace the phrase "`Fleet` over its `_cargo_contents` substrate" with "`Fleet` over its typed cargo manager (`ShipCargoManager`)". One-word edit.
- [ ] No test changes required — this is a docstring fix.
- [ ] Verify: `rg -n "_cargo_contents" game/strategy/engine/` should not match the production_engine.py docstring after this edit (the substrate name was retired in PROJ-436 Phase 3).

**Notes:** This is a pure documentation touch. If any stale `_cargo_contents` reference survives elsewhere in production code (excluding archived projects + the `.agent_reports/` scratch directory), surface it via discovered-issues log rather than fixing inline.

---

### Task 1.9: F-B-016 — drop "Phase 7 deletes the legacy path" stale docstring [Simple]
**Files:**
- `game/strategy/engine/conflict_modifier_collection.py:28-31`
- `game/strategy/services/fleet_speed_calculator.py:175` (parallel reference)

**Tests:** `pytest tests/unit/strategy/conflict_resolution/test_logging_and_lookups.py tests/unit/strategy/test_fleet_speed_calculator.py -q` (no dedicated `test_conflict_modifier_collection.py` or `test_fleet_speed_calculator.py` under `tests/unit/strategy/data/`; `test_logging_and_lookups.py` exercises `lookup_environmental_effects` and the strategy-layer `test_fleet_speed_calculator.py` covers `fleet_speed_calculator`. Both verify import + class shape; docstring changes have no behavioural assertion.)

- [ ] Read the `lookup_environmental_effects` docstring at conflict_modifier_collection.py:22-31. Current text mentions the "legacy EnvironmentalEffects object" and "Phase 7 deletes the legacy path."
- [ ] **GREEN**: Rewrite the docstring to describe the current behaviour: returns a sector-effects list from `collect_sector_effects` (consult the function body at lines 32+ for the actual return shape). Drop the "either / or" framing and the "Phase 7" promise.
- [ ] Open `game/strategy/services/fleet_speed_calculator.py:175` and remove or refresh the parallel `EnvironmentalEffects` reference. Replace with a description of the current source (sector-effects list).
- [ ] Run targeted tests for both files.

**Notes:** Verify with `rg -n "EnvironmentalEffects" game/strategy/` afterwards — should match only legitimate sites (if any survive at all).

---

### Task 1.10: F-B-021 — annotate `ReplayStore._iter_replay_files` [Simple]
**File:** `game/strategy/services/replay_store.py:434`
**Tests:** `pytest tests/unit/strategy/services/test_replay_store_eviction.py -q` (no dedicated `test_replay_store.py`; `test_replay_store_eviction.py` is the unit-level coverage and exercises the eviction path that iterates files. For broader coverage rely on the sharded suite, which includes the integration tests at `tests/integration/replay/test_replay_store.py`.)

- [ ] Read the static method at lines 433-450 (approximately). Current signature: `def _iter_replay_files(rd: Path):`
- [ ] Verify `Iterator` is in the typing imports at the top of the file. If not, add `from typing import Iterator` or `from collections.abc import Iterator` (prefer the latter under PEP-585; check the file's existing pattern).
- [ ] **GREEN**: Change to `def _iter_replay_files(rd: Path) -> Iterator[Path]:`.
- [ ] Run targeted tests.

**Notes:**

---

## Phase Completion Checklist

When all tasks above are checked off:

- [ ] All 10 findings closed
- [ ] Run `pytest tests/unit/strategy/engine/ tests/unit/strategy/services/ -q` — green
- [ ] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-453 1` — PASSED
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to "Project complete; awaiting end-of-project Codex consult per the standing workflow"
- [ ] No new entries in `AgentCoordination/discovered_issues/log.jsonl` from this project's work unless they are genuine out-of-scope discoveries

## Notes / Deferrals

- **F-B-001 / F-B-002 / F-B-014 / F-B-019 / F-B-020 / F-B-022** — already closed by archived PROJ-445 Phases 1-2; not in PROJ-453 scope.
- **F-B-003** — partial close in archived PROJ-445 Phase 2; remaining `ship._cargo_mgr` private-slot migration deferred to a future ShipInstance delegator project, not PROJ-453 scope.
- **F-B-004 / F-B-005 / F-B-017 / F-B-018** — owned by PROJ-454 (sibling retirement project). Do NOT touch in this phase.
- **F-B-013** — joint-phase staging-yard substrate work; deferred until the typed-staging-yard project lands (out of every active PROJ-452..455 scope).
- **DI-2026-05-18-001 ActionExecutionEngine half** — owned by PROJ-455. Do NOT touch in this phase.
