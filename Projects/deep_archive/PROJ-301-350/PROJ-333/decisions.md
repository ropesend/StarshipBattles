# PROJ-333 — Decisions

Testing-approach decisions for the per-turn engines characterization.

## Decisions

| ID | Decision | Rationale |
|---|---|---|
| D-001 | One test file per production file (split when needed) | Master plan default. Split `production_engine` into `test_production_engine_queue.py` + `test_production_engine_consumption.py` if a single combined file would exceed 500 LOC. Split `order_processor` into COLONIZE, TRANSFER, and instant-orders modules by responsibility. |
| D-002 | Mock at boundaries: `Empire`, `Galaxy`, `Planet`, `Fleet`, registries | These engines mutate state on rich domain objects. Existing per-engine conftests under `tests/unit/strategy/{consumable_management_engine,fleet_movement_engine}/conftest.py` are the templates. Use existing `tests/fixtures/` helpers (`mock_planet`, `cargo_mock_ship`, etc.). |
| D-003 | No shared cross-engine fixture | Each engine takes a different combination of (empires, galaxy, registries, save_path). A god-fixture would obscure the engine boundaries. Per-engine conftest mirrors existing layout. |
| D-004 | Pin event-bus calls via `Mock` + `assert_called_with(...)` | Both engines emit structured events (`RESOURCE_SHORTAGE`, `COMPLEX_BUILT`, `SHIP_BUILT`, `FLEET_JOIN_CANCELLED`, `COLONY_FOUNDED`). Event payloads ARE behavior. |
| D-005 | Use real `HexCoord` (pure dataclass), mock `Galaxy` | `HexCoord` is pure math. `Galaxy` has heavy registry/system deps. Mock `get_planets_at_global_hex`, `get_system_of_planet`, `get_system_at_location`, `get_next_fleet_id`. |
| D-006 | No save-path filesystem in tests | `production_spawner._load_design` reads `DesignLibrary(save_path, empire.id)`. Mock `DesignLibrary` at the module path. |
| D-007 | Document apparent bugs as observations only | Per master plan philosophy. Suspected weirdnesses surfaced during read are listed below as observations and pinned as the *current* behavior. They are NOT fixed in this project. |
| D-008 | Per-file commit | Each new test file = one commit. Keeps history bisectable per engine. |

---

## Observations (apparent issues — pin current behavior, do not fix)

The items below were noted during the source-read pass for the plan. Each is pinned as-is by the characterization tests. Any decision to alter the behavior belongs in a follow-up project, not this one.

- **`production_engine._validate_queue_item`** returns `STOP` (not `SKIP`) when an `is_complex_only` queue encounters a non-complex item — this halts the entire queue for that tick. Whether this is intended (queue invariant) or accidental (one bad item shouldn't poison the rest) is ambiguous. Pin the STOP behavior.
- **`production_engine MAX_QUEUE_ITERATIONS = 10`** silently exits the inner loop after 10 items per tick; not logged. If 11+ free items accumulate, the rest carry over silently to the next tick.
- **`production_engine._apply_resource_consumption`** writes to `item['resources_consumed'][res]` without ensuring the key exists — relies on the caller seeding `resources_consumed`. Pin behavior with seeded dicts.
- **`consumable_management_engine`** consumes `total_cost / 100.0` per tick regardless of `TICKS_PER_TURN` (hard-coded `100.0`, not the `TICKS_PER_TURN` constant). Drift hazard if the constant is ever retuned.
- **`fleet_movement_engine._get_effective_fleet_speed`** floors via `int(...)` AFTER multiplication, so a 0.6× modifier on speed 1 yields 0 (immobile). Pin.
- **`fleet_movement_engine._filter_jump_past_collisions`** only handles distance-1 swap parity; broader leapfrog explicitly deferred. Document as a known limit.
- **`order_processor.process_transfer`** looks up the target fleet via `getattr(galaxy, 'empires', [])` — silently returns empty if `galaxy` lacks an `empires` attr, leading to a "No fleet found" cancellation with no diagnostic. Pin the silent-fallback behavior.
- **`order_processor.process_join_fleet`** (single-fleet path) pops the order on "Not at same location"; the analogous case in `process_instant_orders` does NOT pop — inconsistent. Pin both behaviors verbatim.
