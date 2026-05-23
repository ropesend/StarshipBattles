# Phase 5: Audit remediation (Codex consult 2026-05-23)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-483 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete

**Objective:** Remediate the 5 in-scope findings from the Codex mid-project-review audit (2026-05-23). All findings are real and within PROJ-483's declared scope. Findings table: [findings/audit_verification.md](findings/audit_verification.md). Consult artifact: `AgentCoordination/Scratchpad/Consult/20260523T034521Z_audit-PROJ-483/response.md`.

Guiding rule (from CLAUDE.md / user feedback): no bandaids. The Phase 4 `# type: ignore` comments and the silent None-guard in `collision.py` are exactly the kind of symptom-masking these rules forbid. Each fix below converts a workaround into a real boundary.

---

## Tasks

### Task 5.1: collision.py — replace silent beam-ability None guard with assertion [Critical]
**File:** `game/engine/collision.py`

The Phase 4 change wrapped the beam hit/damage block in `if beam_ab is not None:` to satisfy mypy. `BeamResolution` is only built from an `AttackRequest` that already carries a live `weapon_ability` (`game/simulation/combat/families/_beam_common.py:28-40`), and the typed weapon contract (`game/simulation/combat/attack_contract.py:21-25,152-161,204-207`) treats missing dispatch state as programming-error territory. The current code silently drops the hit and the damage when the invariant breaks — a regression.

- [x] Replace `beam_ab = cast("BeamWeaponAbility | None", beam_comp.get_ability('BeamWeaponAbility'))` followed by `if beam_ab is not None:` (`game/engine/collision.py:117-156`) with a non-None cast plus an assertion. Concrete shape:
  ```python
  beam_ab = beam_comp.get_ability('BeamWeaponAbility')
  assert beam_ab is not None, (
      f"BeamResolution invariant: component {beam_comp.name!r} dispatched "
      f"as beam but has no BeamWeaponAbility"
  )
  beam_ab = cast("BeamWeaponAbility", beam_ab)
  ```
  (Or equivalent: `from typing import TYPE_CHECKING` already imports `cast`.) The point is: no `if` branch; failure is loud.
- [x] Re-indent the hit/damage block (`game/engine/collision.py:122-156`) one level out — it is no longer inside the `if beam_ab is not None:` branch.
- [x] Verify mypy still passes: `python -m mypy game/engine/`.
- [x] Add a focused regression test under `tests/unit/engine/` (or extend `tests/unit/engine/collision_edge_cases/test_beam_ramming.py`) that constructs a beam attack against a component that returns `None` from `get_ability('BeamWeaponAbility')` and asserts the engine raises `AssertionError`. This locks in the loud-failure contract. — Added `test_beam_missing_ability_raises_assertion` in `tests/unit/engine/collision_edge_cases/test_beam_ramming.py`.
- [x] Run: `pytest tests/unit/engine/ -k beam` — confirm green (with the new failing test now passing). — 24 passed.

### Task 5.2: controller.py — use is_grid_entity guard, drop type: ignore [Simple]
**File:** `game/ai/controller.py`

The loop at `game/ai/controller.py:435-441` reads `obj.position` and `obj.radius`, but it narrows with `is_combatant(obj)`. `ICombatant` / `is_combatant` only model `team_id`, `is_alive`, and a loose `position` — radius lives on `IGridEntity` (`game/ai/protocols.py:38-63,116-123`). The `# type: ignore[attr-defined]` workaround papers over the wrong guard.

- [x] Change the import: from `is_combatant` to `is_grid_entity` (both available; `is_grid_entity` is in `game.ai.protocols`). — Added `is_grid_entity` alongside existing `is_combatant` (which is still used by `find_target` at line 167).
- [x] At `game/ai/controller.py:435`, swap `if not is_combatant(obj):` → `if not is_grid_entity(obj):`.
- [x] Remove the `# type: ignore[attr-defined]` from `game/ai/controller.py:441`.
- [x] Remove the misleading explanatory comment lines 439-440 (or rewrite to note the guard provides radius). — Rewrote to reference the new guard.
- [x] Verify: `python -m mypy game/ai/`. — Success: no issues found in 23 source files.
- [x] Run: `pytest tests/unit/ai/ -k controller`. — 78 passed. Three avoidance tests in `tests/unit/ai/test_ai_controller_unit.py` (skips_non_combatants, handles_zero_distance, selects_closest_threat) updated to patch `is_grid_entity` instead of `is_combatant`; one return-target test as well. The skips_non_combatants test was failing under the new code because the prior patch of `is_combatant` was dead and Mock's `.radius` is not a float — fix is to patch the actual guard symbol.

### Task 5.3: target_evaluator.py — add get_components_by_layer to ICombatShip protocol, drop type: ignore [Simple]
**Files:** `game/simulation/interfaces/entity_protocols.py`, `game/ai/target_evaluator.py`

`ICombatShip` is documented as the combat/AI component-access surface (`game/simulation/interfaces/entity_protocols.py:49-60,197-232,473-474`) and already exposes `layers`. `target_evaluator._eval_least_armor_rule` calls `candidate.get_components_by_layer(LayerType.ARMOR)` after `is_combat_ship(candidate)` — the method belongs on the protocol but is not declared.

- [x] Add to `ICombatShip` in `game/simulation/interfaces/entity_protocols.py` (placed alongside `layers` for cohesion):
  ```python
  def get_components_by_layer(self, layer_type: Any) -> List[Any]:
      """Return all components in the given layer (keyed by LayerType)."""
      ...
  ```
  (Used `Any` for `layer_type` to match the existing convention in this protocol — `layers` itself is typed `Dict[Any, Any]`.)
- [x] Remove the `# type: ignore[attr-defined]` from `game/ai/target_evaluator.py:224` and the misleading comment on lines 222-223.
- [x] Verify Ship implements the method (it does — used widely; no change needed there).
- [x] Verify: `python -m mypy game/ai/ game/simulation/`. — `game/ai/` clean (in scope). `game/simulation/` is out of PROJ-483 scope and has 558 pre-existing errors unrelated to this change.
- [x] Run: `pytest tests/unit/ai/ -k target_evaluator`. — 106 passed.

### Task 5.4: Ship.layers class annotation — drop controllable.py type: ignore [Simple]
**Files:** `game/simulation/entities/ship.py`, `game/ai/interfaces/controllable.py`

`ShipLayerManager.initialize_layers()` assigns `ship.layers = {}` at `game/simulation/entities/ship_layer_manager.py:50` but `Ship` never declares `layers` as a class attribute, so mypy can't see it on the instance. Adding the class-level annotation is the proper fix.

- [x] In `Ship` class body (`game/simulation/entities/ship.py`), add a typed class-level annotation:
  ```python
  layers: Dict[LayerType, "LayerData"]
  ```
  Added `LayerData` to the `TYPE_CHECKING` block (LayerType was already imported).
- [x] Remove the `# type: ignore[attr-defined]` from `game/ai/interfaces/controllable.py:384`.
- [x] Fix the misleading comment at `game/ai/interfaces/controllable.py:382-383`: the real mapping is `dict[LayerType, LayerData]`, not `dict[str, Any]`. Rewrote the docstring.
- [x] Update `ShipControllableAdapter.get_layers` return type from `Dict[str, Any]` to `Dict[LayerType, LayerData]`. Also widened the abstract `IControllable.get_layers` declaration from `Dict[str, Any]` to `Dict[Any, Any]` so the concrete override is a valid Liskov-compatible widening on the key type.
- [x] Verify: `python -m mypy game/ai/ game/simulation/`. — `game/ai/` clean. `game/simulation/` out of scope (pre-existing errors).
- [x] Run: `pytest tests/unit/ai/ -k controllable or layers`. — 29 passed.

### Task 5.5: IEmpire.color — coerce list→tuple in Empire.from_dict [Simple]
**Files:** `game/strategy/data/empire.py`

`IEmpire.color: tuple[int, int, int]` (`game/core/protocols/strategy_domain.py:32-33`) is stricter than `Empire`'s storage. `Empire.from_dict` passes `data['color']` straight through (`game/strategy/data/empire.py:369`), so JSON-loaded empires can carry a list. We keep the narrower protocol (it expresses the desired contract) and convert at the deserialization boundary — the right place to enforce shape.

- [x] In `Empire.from_dict` (`game/strategy/data/empire.py:366-`), coerce `data['color']`:
  ```python
  raw_color = data['color']
  color = tuple(raw_color) if not isinstance(raw_color, tuple) else raw_color
  ```
  Then pass `color=color` to the constructor.
- [x] Optional: in `Empire.__init__`, accept `color: tuple[int, int, int] | list[int]` and coerce there too. — Skipped per checklist guidance (single boundary fix at `from_dict` is cleaner; no second list-callsite identified).
- [x] Verify: `python -m mypy game/strategy/data/empire.py`. — 15 pre-existing errors, all unrelated to this change (missing annotations, untyped functions); strategy is not in strict scope.
- [x] Run: `pytest tests/unit/strategy/data/ -k empire`. — 78 passed.

---

## Cross-cutting validation
- [x] After all 5 tasks: `python -m mypy game/research/ game/services/ game/assets/ game/engine/ game/ai/ game/core/` still returns "Success: no issues found in 83 source files".
- [x] Spot-check the touched test directories: `pytest tests/unit/engine/ tests/unit/ai/ tests/unit/simulation/interfaces/` — 493 passed.
- [x] Update PROJ-483 `plan.md` Quick Status table (add Phase 5 row) and Current State.

## Not in scope for Phase 5
- Re-auditing. One round only per orchestrator protocol.
- Further protocol redesign. The 5 fixes above are surgical.
- Any work in `game/strategy/` (PROJ-482's territory) beyond the single `Empire.from_dict` coercion — that file is shared, but the change is non-overlapping (PROJ-482 doesn't touch `from_dict`).
