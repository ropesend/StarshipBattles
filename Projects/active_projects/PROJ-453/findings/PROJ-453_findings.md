# PROJ-453 Findings (consolidated)

Source: `Projects/archived_projects/PROJ-445/findings/bucket_b_engine_services_scan.md` (verbatim entries below). All file:line references **re-verified against current code on 2026-05-19** before this file was written.

10 findings, all severity `low`, all closed by Phase 1's mechanical polish sweep.

---

## F-B-006 — `SuperweaponOrderProcessor._get_system_at_hex` has `# type: ignore[no-untyped-def]` masking a missing annotation
- **Severity**: low
- **Category**: polish
- **File**: `game/strategy/engine/superweapon_order_processor.py:340` (verified 2026-05-19; was cited at `:343` in the original scan — the `@staticmethod` decorator landed 3 lines earlier than the def in the current code shape)
- **Symbol**: `SuperweaponOrderProcessor._get_system_at_hex`
- **Source refactor**: PROJ-414 (the previous shim deletion left this internal method untyped)
- **What survived**: `def _get_system_at_hex(galaxy, location):  # type: ignore[no-untyped-def]` — a `type: ignore` comment is used to silence a missing-annotation warning rather than adding the annotation.
- **Why it's a problem**: `type: ignore` comments are a maintenance smell — they linger past the underlying issue and obscure real type problems.
- **Suggested action**: Add the annotations: `def _get_system_at_hex(galaxy: Any, location: HexCoord) -> Optional["StarSystem"]:` (matching `GalaxyPathfindingService.get_system_at_hex`). Drop the `type: ignore`.
- **Effort**: tiny
- **Status as of 2026-05-19**: open. Method body unchanged since PROJ-414; the `# type: ignore` comment is still present at line 340.

---

## F-B-007 — `OrderProcessor.__init__` missing return annotation and `event_bus` parameter has no type annotation
- **Severity**: low
- **Category**: polish (convention violation — public `__init__` is exempt per the dunder rule, but `event_bus` should be typed)
- **File**: `game/strategy/engine/order_processor.py:64` (verified 2026-05-19)
- **Symbol**: `OrderProcessor.__init__`
- **Source refactor**: PROJ-368 (facade introduction)
- **What survived**: `def __init__(self, event_bus=None):` — no annotation on `event_bus`. (Dunder return is exempt; the parameter annotation is the actual gap.)
- **Why it's a problem**: Minor consistency gap; every other engine `__init__` in the layer types its event_bus parameter (e.g., `SuperweaponOrderProcessor.__init__` has the same issue at superweapon_order_processor.py:56).
- **Suggested action**: `def __init__(self, event_bus: Optional[Any] = None) -> None:` (matches the kwarg-default pattern used by `BaseOrderHandler.__init__`).
- **Effort**: tiny
- **Status as of 2026-05-19**: open. Unchanged.

---

## F-B-008 — `SuperweaponOrderProcessor.__init__` missing parameter and return annotations
- **Severity**: low
- **Category**: polish
- **File**: `game/strategy/engine/superweapon_order_processor.py:56` (verified 2026-05-19)
- **Symbol**: `SuperweaponOrderProcessor.__init__`
- **Source refactor**: none — original signature carried forward
- **What survived**: `def __init__(self, event_bus=None, empire_mutator=None, nav_service=None):` — all three parameters are untyped.
- **Why it's a problem**: Same as F-B-007; layer convention violation.
- **Suggested action**: Add `Optional[Any]` annotations and `-> None` return.
- **Effort**: tiny
- **Status as of 2026-05-19**: open. Unchanged.

---

## F-B-009 — `resolve_requested` module-level helper missing return annotation
- **Severity**: low
- **Category**: polish (convention violation — public module-level function)
- **File**: `game/strategy/engine/handlers/fms_shared.py:94` (verified 2026-05-19)
- **Symbol**: `resolve_requested`
- **Source refactor**: PROJ-FMS-shared
- **What survived**: `def resolve_requested(count, count_available: int):` — no return type, `count` parameter untyped. The docstring says it returns "either an `int` (resolved count) or a `ValidationResult`" — exactly the case where a `int | ValidationResult` union annotation should be required by the CLAUDE.md "Public functions and methods require return-type annotations" rule.
- **Why it's a problem**: The function is in `__all__` so it's public surface. Callers can't statically reason about whether they got an error result or a count.
- **Suggested action**: `def resolve_requested(count: Optional[int], count_available: int) -> int | ValidationResult:`.
- **Effort**: tiny
- **Status as of 2026-05-19**: open. Verified verbatim signature at fms_shared.py:94 still untyped.

---

## F-B-010 — `TurnEngine.planet_modifier_effect_engine` property missing return annotation
- **Severity**: low
- **Category**: polish
- **File**: `game/strategy/engine/turn_engine.py:521` (verified 2026-05-19)
- **Symbol**: `TurnEngine.planet_modifier_effect_engine` (property)
- **Source refactor**: PROJ-428 Phase 1 (TD-04 lazy-property addition)
- **What survived**: `def planet_modifier_effect_engine(self):` — public property, no return annotation. Sibling `TurnEngine.water_engine` at line 516 has the annotation `-> 'IWaterEngine'`; this one was missed.
- **Why it's a problem**: Convention violation; symmetry break with other engine properties.
- **Suggested action**: `def planet_modifier_effect_engine(self) -> "PlanetModifierEffectEngine":`.
- **Effort**: tiny
- **Status as of 2026-05-19**: open. Unchanged.

---

## F-B-011 — Six private `_get_*_mutator` accessors missing return annotations
- **Severity**: low
- **Category**: polish
- **File**: six sites (verified 2026-05-19):
  - `game/strategy/engine/harvesting_engine.py:196` (`_get_planet_mutator`)
  - `game/strategy/engine/atmosphere_engine.py:30` (`_get_planet_mutator`)
  - `game/strategy/engine/planet_modifier_effect_engine.py:34` (`_get_planet_mutator`)
  - `game/strategy/engine/production_spawner.py:101` (`_get_planet_mutator`)
  - `game/strategy/engine/environmental_hazard_engine.py:65` (`_get_ship_mutator`) — added by 2026-05-19 audit fix
  - `game/strategy/engine/superweapon_order_processor.py:70` (`_get_empire_mutator`) — added by 2026-05-19 audit fix
- **Symbol**: `_get_planet_mutator`, `_get_empire_mutator`, `_get_ship_mutator` (private accessors across multiple engines)
- **Source refactor**: PROJ-370 / PROJ-382 (mutator lazy-default pattern)
- **What survived**: Six private accessors of the form `def _get_planet_mutator(self):` with no return annotation. Strictly speaking the CLAUDE.md rule says public — but these all return a known protocol type, the annotation is trivial, and the typed sibling pattern (e.g., `BaseOrderHandler._get_planet_mutator` at `order_handlers/base.py:137` — uses `-> Any`) already exists.
- **Why it's a problem**: Mild consistency gap. Listed for completeness; lower priority than F-B-007 - F-B-010.
- **Suggested action**: Annotate as `-> Any` (matches `BaseOrderHandler._get_planet_mutator`) or with the concrete write-service type. Phase 1 picks `-> Any` for the sweep so the change stays purely annotation (no new imports).
- **Effort**: tiny
- **Status as of 2026-05-19**: open. Verified `harvesting_engine.py:196 def _get_planet_mutator(self):` still untyped; live grep on 2026-05-19 confirmed all six sites unannotated.
- **2026-05-19 audit-fix**: scope expanded from 4 → 6 sites; see `plan.md` and `phase_1_checklist.md` Task 1.6 for the canonical list.

---

## F-B-012 — `test_superweapon_registry_contract.py` has two unreachable `pytest.skip` clauses
- **Severity**: low
- **Category**: test-inconsistency (dead skip clauses on a module that always imports)
- **File**: `tests/unit/strategy/services/test_superweapon_registry_contract.py:148-154, 172-178` (verified 2026-05-19 — original scan cited `:154, :178`; current code shows the `try / except ImportError → pytest.skip` blocks span 148-154 and 172-178)
- **Symbol**: `TestSuperweaponRegistryVsCommandSpecs.test_order_types_match_command_specs` and `test_ability_names_match_command_specs`
- **Source refactor**: PROJ-371 (command_registry introduction)
- **What survived**: Both tests open with `try: from game.strategy.engine.commands.registry import command_registry, seed_default_commands` then `except ImportError: pytest.skip("PROJ-371 command_registry not available")`. The module is in the live tree (it's verified by `tests/unit/strategy/engine/test_command_specs_contract.py` and many others); the import cannot raise `ImportError` today.
- **Why it's a problem**: Dead defensive code. If the test ever appears to skip on CI, future readers will conclude PROJ-371 surface is conditional when it's not. Worse — if the import path ever does break legitimately (typo, rename), the `pytest.skip` silently turns a hard failure into a green pass.
- **Suggested action**: Remove both `try / except ImportError` guards and the inner skip; let the top-level import fail loudly if the module ever disappears.
- **Effort**: tiny
- **Status as of 2026-05-19**: open. Both skip blocks present and unchanged.

---

## F-B-015 — `ProductionEngine` IProductionResourceSource docstring mentions "Fleet over its `_cargo_contents` substrate"; substrate was retired in PROJ-436 Phase 3
- **Severity**: low
- **Category**: polish (stale docstring referencing retired surface)
- **File**: `game/strategy/engine/production_engine.py:80` (verified 2026-05-19 — original scan cited `:68`; the docstring shifted to line 80 after PROJ-445 Phase 2 added the affordability/consumption symmetry clause earlier in the same docstring)
- **Symbol**: `IProductionResourceSource.production_consume_resource` (docstring)
- **Source refactor**: PROJ-436 Phase 3 (`cargo_contents` → typed cargo manager) — docstring not updated
- **What survived**: Docstring reads "integer-typed sources (e.g. `Fleet` over its `_cargo_contents` substrate) MAY round the requested `amount` before consumption." `_cargo_contents` is the pre-PROJ-436 name; current code uses the `ShipCargoManager` API per PROJ-436 Phase 3.
- **Why it's a problem**: Stale name in protocol docstring; future readers searching for `_cargo_contents` won't find it in code.
- **Suggested action**: Replace "`Fleet` over its `_cargo_contents` substrate" with "`Fleet` over its typed cargo manager (`ShipCargoManager`)" — one-word edit.
- **Effort**: tiny
- **Status as of 2026-05-19**: open. Verified at production_engine.py:80 — `_cargo_contents` substrate phrasing unchanged.

---

## F-B-016 — `conflict_modifier_collection.lookup_environmental_effects` docstring says "Phase 7 deletes the legacy path" — Phase 7 has shipped
- **Severity**: low
- **Category**: polish (stale docstring promising future cleanup that has already happened)
- **File**: `game/strategy/engine/conflict_modifier_collection.py:28-31` (verified 2026-05-19) and parallel `game/strategy/services/fleet_speed_calculator.py:175` (the live file is under `services/`, not `data/`; codex audit correction 2026-05-19)
- **Symbol**: `lookup_environmental_effects`
- **Source refactor**: PROJ-300 Phase 7 (legacy `EnvironmentalEffects` path deleted)
- **What survived**: Docstring still says "The spec compiler accepts either the legacy EnvironmentalEffects object (effective during AreaEffectManager deprecation) or this new list. Phase 7 deletes the legacy path." Grep confirms `EnvironmentalEffects` is no longer used anywhere in the strategy layer except `game/strategy/services/fleet_speed_calculator.py:175` (also a stale docstring reference). PROJ-300 Phase 7 is closed.
- **Why it's a problem**: Docstring lies about the current state — implies the spec compiler still accepts both shapes when it doesn't.
- **Suggested action**: Drop the "either / or" phrasing; state that the function returns a sector-effects list from `collect_sector_effects`. Also clean up the parallel reference at `fleet_speed_calculator.py:175`.
- **Effort**: tiny
- **Status as of 2026-05-19**: open. Verified both stale docstring references still present.

---

## F-B-021 — `replay_store.py:434 _iter_replay_files` module-level helper missing return annotation
- **Severity**: low
- **Category**: polish
- **File**: `game/strategy/services/replay_store.py:434` (verified 2026-05-19)
- **Symbol**: `ReplayStore._iter_replay_files` (static method)
- **Source refactor**: none
- **What survived**: `def _iter_replay_files(rd: Path):` — no return annotation. It's a private static method on the class but visible enough that the convention applies.
- **Why it's a problem**: Minor convention gap.
- **Suggested action**: `def _iter_replay_files(rd: Path) -> Iterator[Path]:`. Add the `Iterator` import to the typing block if not already present.
- **Effort**: tiny
- **Status as of 2026-05-19**: open. Unchanged.

---

## Out-of-scope clarifications (not closed by this project)

Findings cited in the same bucket-B scan that this project explicitly does **not** close:

- **F-B-001** (LayMines TypeError) — closed by archived PROJ-445 Phase 1.
- **F-B-002** (`transfer_branches` rollback bypassing capacity gate) — closed by archived PROJ-445 Phase 2.
- **F-B-003** (`ship._cargo_mgr` private-slot reaches from transfer_branches) — partial close in archived PROJ-445 Phase 2; remaining migration sweep deferred to a future ShipInstance delegator project (not in PROJ-453 scope).
- **F-B-004** (`effect_ability_metadata.py` shim retirement) — **owned by PROJ-454** (Phase 1).
- **F-B-005** (`component_inspector.py` shim retirement) — **owned by PROJ-454** (Phase 2).
- **F-B-013** (`transfer_branches` DropPod boundary flatten/inflate) — joint-phase with retired PROJ-444 staging-yard work; deferred until typed-staging-yard substrate project (out of every active PROJ-452..455 scope).
- **F-B-014** (CLOSE_WARP_POINT legacy string branch) — closed by archived PROJ-445 Phase 2.
- **F-B-017** (OrderProcessor facade reshape) — **owned by PROJ-454** (Phase 3).
- **F-B-018** (OrderExecutionResult legacy fields) — **owned by PROJ-454** (Phase 4).
- **F-B-019** (IProductionResourceSource Protocol docstring tightening) — closed by archived PROJ-445 Phase 2.
- **F-B-020** (`planet_fms` subcategory tag spelling guard) — closed by archived PROJ-445 Phase 1 (test_planet_fms_subcategory_tag_spelling_or_set_size landed).
- **F-B-022** (planet-LAY_MINES dispatch test) — closed by archived PROJ-445 Phase 1 (parametrised in `tests/integration/test_fms_planet_lay_mines.py`).
- **DI-2026-05-18-001 ActionExecutionEngine half** (planet-FMS `_process_planet_action_tick` end-to-end coverage) — **owned by PROJ-455**.
