# Phase 3: ShipInstance residual state-surface consolidation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-438 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** Phase 2 (session/facade boundary clean) AND PROJ-436 Phase 9 (`_CarriedItemsProxy` deletion) — both confirmed on `main` at Phase 0 baseline (`eb8da3d85`).
**Objective:** Narrow the remaining post-storage `ShipInstance` state surface (`IShipInstance` protocol, serializer, bridge, DTO read contracts) without forcing the 910-caller entry-point shim sweep. Apply D2 default **(a)**: keep inline `design_data` as durable state for now, but narrow the public/protocol/serializer surface around it.

**Resolution (2026-05-18):** Phase 3 collapsed to a **documentation + invariant-pinning pass**, same model as Phase 2. The post-Phase-9 audit confirmed the residue is intentional and the explicit-shim entry points are PROJ-425 Phase 5d/5e load-bearing. See `decisions.md` row dated 2026-05-18 for the full rationale.

---

## Tasks

### Task 3.0: Re-audit current `ship_instance.py` shape [Simple, planning]
**Files:** `game/strategy/data/ship_instance.py`, `game/strategy/data/ship_instance_serializer.py`, `game/strategy/data/ship_instance_bridge.py`, `game/core/protocols/strategy_domain.py`
**Tests:** None (planning)

- [x] Map current `ShipInstance` public surface: durable fields, cache state, delegate slots, projection helpers, bridge/serializer shims. *(Post-Phase-9: 768 LOC. 13 owned dataclass fields + 4 delegate slots + 5 Protocol-alias properties + 2 status-cache properties + ~14 explicit shim methods (serializer, bridge, resource-manager, write-service). The legacy `consumable_levels` / `cargo_contents` survive as backward-compat property shims over `_consumable_levels` / `_cargo_contents` private dicts.)*
- [x] Identify which `IShipInstance` protocol attributes still advertise the old broad shape (e.g. legacy `cargo_contents`) and need narrowing. *(`cargo_contents` is the only entry; the protocol docstring already marks it as a backward-compat dict view pointing readers at `ShipCargoManager` / `cargo_container()`. Audit found 30+ files reference `cargo_contents` — removal is a sweep, not a Phase 3 in-scope narrowing.)*
- [x] List serializer/bridge methods whose surface is wider than what post-storage callers actually need. *(Audit confirms PROJ-425 Phase 5d/5e rationale stands: `to_dict`/`from_dict`/`to_json`/`from_json`/`clone` have ~18 callers; `to_ship`/`update_from_ship` have ~10. Migrating in one batch exceeds the slimming benefit. NOT a Phase 3 in-scope sweep.)*
- [x] Identify any DTO read contract in `game/strategy/facade/dto/fleet_dto.py` or `fleet_hierarchy_dto.py` that still depends on the broad pre-storage ship shape. *(DTOs read concrete `ship.design_data.get(...)`, `ship.get_hp_percentage()`, `ship.is_combat_capable()`, `ship.instance_id`, `ship.name`, `ship.design_id` — all post-storage stable. No DTO-side narrowing required.)*

### Task 3.1: Failing post-container surface test [Simple, TDD]
**Files:** `tests/unit/strategy/ship_instance/test_post_container_surface.py` (new)
**Tests:** `pytest tests/unit/strategy/ship_instance/test_post_container_surface.py`

- [x] Write a failing test that pins the post-Phase-9 categorical shape: 10 ratchets across (i) owned identity / durable / runtime state field presence, (ii) status flag presence, (iii) delegate-manager slot presence, (iv) legacy-shim property documentation contracts, (v) `IShipInstance` protocol minimum-surface contract, (vi) `cargo_contents` protocol docstring future-removal pointer.
- [x] Confirm 1 test fails before any production change (the class-docstring categorization assertion).

### Task 3.2: Categorical documentation on `ShipInstance` [Small]
**Files:** `game/strategy/data/ship_instance.py`
**Tests:** Task 3.1 tests + `pytest tests/unit/strategy/ship_instance/`

- [x] Add a categorical class docstring enumerating post-Phase-9 attribute/method categories (Owned identity / Owned durable state / Owned runtime state / Status flags / Cached & DI / Delegate-manager slots / Protocol-alias properties / Retained-shim entry points). Each category lists its concrete members.
- [x] Run Task 3.1: 10/10 green.
- [x] Run existing ship_instance test suite: 140/140 green.

### Task 3.3 (intentionally skipped — `IShipInstance` protocol surface)
- [x] Audit ruled out the narrowing as out of scope. Future project may revisit if Container-projection consumers reach critical mass.

### Task 3.4 (intentionally skipped — DTO narrowing)
- [x] Audit ruled out DTO narrowing — DTOs already read concrete post-storage attributes.

### Task 3.5: Sweep + sharded suite [Small]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] No sweep required — Phase 3 is documentation only.
- [x] Run the canonical sharded suite green.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `python Tools/test_sharded/test_sharded.py` green (no NEW failures vs. Phase 0 baseline; Phase 2 LOC budget regression on `game_session.py` already fixed during Phase 3 close-out)
- [x] Game still runnable / savable / loadable (no behavior changed)
- [x] No new 910-caller sweep work introduced
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
- [x] `python Projects/scripts/validate_phase.py PROJ-438 3` passes
