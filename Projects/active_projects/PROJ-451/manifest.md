# PROJ-451 File Manifest

> Files that this project touches, grouped by phase and by Production / Test / Doc type.
> DI-006 + DI-007 already pin the file:lines; no pre-flight audit phase required.

## Phase 1 — RED: rounded-to-zero stall reproduction tests

### Test
| File | Type | Notes |
|------|------|-------|
| `tests/integration/test_production_engine_fractional_fleet_cost.py` | Test (extend) | Add `test_fractional_cost_rounds_to_zero_emits_resource_shortage` integration test |
| `tests/unit/strategy/engine/test_production_engine_consumption.py` | Test (extend) | Add `test_apply_resource_consumption_emits_shortage_on_zero_consume` unit test |

## Phase 2 — GREEN: close DI-006 data-side gate asymmetry + engine-side RESOURCE_SHORTAGE emit + docstring polish

### Production
| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/fleet.py` | Production | **Task 2.0 (codex r5):** round the `Fleet.consume_cargo_resource` gate at `:285` from `if total < amount:` to `if total < int(round(amount)):` so it matches `has_cargo_resources`. Closes data-half asymmetry. |
| `game/strategy/engine/production_engine.py` | Production | **Task 2.1-2.3:** modify `_apply_resource_consumption` (lines 649-687) to detect `amount > 0 AND actually_consumed == 0` and route to `_log_resource_shortage` (existing path at :588-647) with cause "amount rounded to zero against integer cargo store". **Task 2.5 (codex r5 NEW-2):** update module docstring `:10-16` to drop pre-PROJ-436 "empire pool" framing. |

### Test (new + verification)
| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/data/test_fleet_consume_cargo_symmetry.py` | Test (new) | Task 2.0 ratchet: `has_cargo_resources` and `consume_cargo_resource` agree on rounded-to-zero costs |
| `tests/unit/strategy/data/test_fleet.py` | Test | Verify no regression after Task 2.0 |
| `tests/integration/test_production_engine_fractional_fleet_cost.py` | Test | Phase 1 RED test should now be GREEN |
| `tests/unit/strategy/engine/test_production_engine_consumption.py` | Test | Phase 1 RED test should now be GREEN |

## Phase 3 — Decision: option (a) defensive or option (b) strict assertion

### Production (option a path)
| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/production_engine.py` | Production | Capture bool return in `_apply_resource_consumption`; pass back to `_process_queue_tick_dynamic`; if False, skip tick_capacity decrement (option a path) |

### Production (option b path)
| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/production_engine.py` | Production | Add hard assertion in `_apply_resource_consumption`: `assert colony_or_fleet.production_consume_resource(res, amount), "Contract breach: ..."`; tighten Protocol contract docstring at :60-95 (option b path) |

### Test (per chosen option)
| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/engine/test_production_engine_consumption.py` | Test | Add tests proving the chosen behavior: option (a) capacity-skip test; option (b) misbehaving-implementer raises AssertionError |

### Doc
| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-451/decisions.md` | Doc | Record (a) vs (b) decision with rationale |

## Phase 4 — Ratchet tests for `IProductionResourceSource` implementers

### Test
| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/data/test_production_resource_source_ratchet.py` (new) | Test | New ratchet test file. Parametrize across Planet, Fleet, and any future implementer. Asserts: `has_resources(costs) → True implies consume(resource, amount) → True` for each (resource_type, amount) in costs. |

## Verification / sharded suite

| File | Type | Notes |
|------|------|-------|
| `python Tools/test_sharded/test_sharded.py` | Command | Run after each phase boundary |

## Cross-reference to PROJ-444 Phase 2 (already complete)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/fleet.py:245-269` | Production (read-only verify) | Data-layer half of DI-006 already closed: `Fleet.has_cargo_resources` now does `int(round(amount))` symmetric to `consume_cargo_resource`. PROJ-451 does NOT re-touch this site. |
