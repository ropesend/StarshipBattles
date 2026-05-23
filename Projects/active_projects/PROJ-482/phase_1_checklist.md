# Phase 1: Critical Strategy missing returns

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-482 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Resolve 4 CRITICAL strategy findings — the `GameSession` 10-property cluster (one combined fix), and 3 standalone missing-return CRITICALs that are called cross-module.

---

## Tasks

### Task 1.1: GameSession mutator+registry property cluster — combined fix [Medium]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/ -k game_session` then `mypy game/strategy/engine/game_session.py`

Per Phase D bundling decision: ONE combined task replaces 10 individual line-by-line edits because the fix is the same mechanical pattern on every line. Both the missing annotation AND the `# type: ignore[no-untyped-def]` come off together.

- [ ] Add return annotation `-> EventBus` (or `-> Any` if circular) to `_event_bus` (line 202); remove the `# type: ignore[no-untyped-def]`
- [ ] Add return annotation `-> IFleetMutator` to `fleet_mutator` property (line 217); remove the `# type: ignore[no-untyped-def]`
- [ ] Add return annotation `-> IFleetMutator` to `_fleet_mutator` (line 227); remove the `# type: ignore[no-untyped-def]`
- [ ] Add return annotation `-> IPlanetMutator` to `planet_mutator` (line 231); remove the `# type: ignore[no-untyped-def]`
- [ ] Add return annotation `-> IPlanetMutator` to `_planet_mutator` (line 236); remove the `# type: ignore[no-untyped-def]`
- [ ] Add return annotation `-> IEmpireMutator` to `empire_mutator` (line 240); remove the `# type: ignore[no-untyped-def]`
- [ ] Add return annotation `-> IEmpireMutator` to `_empire_mutator` (line 245); remove the `# type: ignore[no-untyped-def]`
- [ ] Add return annotation `-> IShipInstanceMutator` to `ship_mutator` (line 249); remove the `# type: ignore[no-untyped-def]`
- [ ] Add return annotation `-> IShipInstanceMutator` to `_ship_mutator` (line 254); remove the `# type: ignore[no-untyped-def]`
- [ ] Add return annotation `-> CommandRegistry` to `_command_registry` (line 258); remove the `# type: ignore[no-untyped-def]`
- [ ] Ensure mutator protocols + `CommandRegistry` + `EventBus` are imported under `TYPE_CHECKING` to avoid runtime cycles
- [ ] Verify: `pytest tests/ -k game_session` passes; `mypy game/strategy/engine/game_session.py` shows no new errors (10 `no-untyped-def` errors should be gone, no new ones introduced)

### Task 1.2: OrderMetadataView._registry annotation [Simple]
**File:** `game/strategy/engine/commands/order_metadata_view.py`
**Tests:** `pytest tests/ -k order_metadata` then `mypy game/strategy/engine/commands/order_metadata_view.py`

- [ ] Add `-> CommandRegistry` to `_registry` static method (line 76); the lazy-import-then-seed pattern returns `command_registry` singleton
- [ ] Verify: tests pass; `mypy` clean

### Task 1.3: SuperweaponOrderProcessor._get_nav_service annotation [Simple]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/ -k superweapon` then `mypy game/strategy/engine/superweapon_order_processor.py`

- [ ] Add `-> FleetNavigationService` to `_get_nav_service` (line 85). Despite `_` prefix, this is called externally from `close_warp_point.py:102` and `open_warp_point.py:91`
- [ ] Verify: tests pass; `mypy` clean

### Task 1.4: StarSystem.primary_star property annotation [Simple]
**File:** `game/strategy/data/star_system.py`
**Tests:** `pytest tests/ -k star_system` then `mypy game/strategy/data/star_system.py`

- [ ] Add `-> Star | None` to `primary_star` property (line 85). Public property with 15+ call sites across strategy data/engine and UI
- [ ] Verify: tests pass; `mypy` clean

### Task 1.5: Phase verification [Simple]
- [ ] Verify: `python Tools/test_sharded/test_sharded.py` passes
- [ ] Verify: `mypy` clean across all touched files

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_210540_type-audit/`. See `findings/source_audit.md` for the link._
