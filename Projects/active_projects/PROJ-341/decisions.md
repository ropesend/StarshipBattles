# PROJ-341 — Decisions

Format: each decision is `D-NNN` with a short title, status, context, decision, and rationale. Observation-only entries (`OBS-NNN`) record apparent bugs found while reading production code; per master plan rule, we pin actual behavior and do not fix.

---

## D-001 — Characterization-only, no TDD, no production refactors
**Status:** Accepted
**Context:** This project follows the master plan testing philosophy.
**Decision:** Tests pin observable current behavior of the three in-scope files. We do not write red tests first; we read the code, identify the behavior, and write tests that lock it in. If a behavior looks wrong, we still pin the current behavior (so any future "fix" trips a red test) and record an observation here.
**Rationale:** Master plan rule. The arc's purpose is to catch regressions, not to drive new design.

---

## D-002 — Three new test files, do not edit existing test files
**Status:** Accepted
**Context:** The existing `test_superweapon_order_processor.py` is already 1232 LOC, well past the 500-LOC soft ceiling for production files (tests have a softer convention but it still applies). The existing `test_action_execution_engine.py` is shorter (~520 LOC) but mixing gap-fill into it would smear PROJ-341 changes across an existing file and complicate per-project commit discipline.
**Decision:** Each in-scope file gets a new sibling test file:
- `tests/unit/strategy/engine/test_environmental_hazard_engine.py` (new; green-field)
- `tests/unit/strategy/engine/test_superweapon_order_processor_gaps.py` (new; gap-fill, separate file)
- `tests/unit/strategy/engine/test_action_execution_engine_gaps.py` (new; gap-fill, separate file)
**Rationale:** Keeps PROJ-341 commits self-contained; respects the LOC ceiling; separates "what existed before" from "what this project added" for any future audit.

---

## D-003 — Mock at the engine's collaborators, not at HexCoord/Order/Fleet
**Status:** Accepted
**Context:** The existing tests already use a mix: real `Order`, `HexCoord`, `WarpPoint`, `Fleet`, `Empire`; `MagicMock` for `Galaxy`, `StarSystem`, `Star`, `Planet`, `Ship`, `EventBus`. This boundary works.
**Decision:** Continue the same boundary. Use real `Order(OrderType.X, target=...)` so order-type filtering exercises the real `OrderType` enum. Mock the galaxy / system / collector / SystemDestroyer / SuperweaponValidator at module level via `unittest.mock.patch`.
**Rationale:** Existing tests are stable at this boundary; matching it minimises fixture churn and keeps the new tests reading like the old tests.

---

## D-004 — Stabilizer-blocking paths via patched `find_blocking_stabilizer`
**Status:** Accepted
**Context:** `superweapon_order_processor._check_blocking_stabilizer` delegates to `game.strategy.services.stabilizer_registry.find_blocking_stabilizer` via a deferred import. The existing tests do not exercise the blocking-cancel branch for any superweapon.
**Decision:** Patch `game.strategy.services.stabilizer_registry.find_blocking_stabilizer` to return a `MagicMock(ability_name='ChronoStabilizer')` for the cancellation tests. Patch it to return `None` (the default) for happy-path tests and rely on the real registry returning `None` when there are no stabilizer-providing facilities.
**Rationale:** This is exactly how the production code wires the dependency; the patch keeps the test focused on the processor's branching, not on the registry's lookup logic (which has its own tests).

---

## D-005 — Damage / fuel-drain rates come from `collect_sector_effects`
**Status:** Accepted
**Context:** `EnvironmentalHazardEngine.process_environmental_tick` calls `game.strategy.services.system_effects_collector.collect_sector_effects` to get the list of `EnvironmentalDamage` and `FuelDrain` effect dicts.
**Decision:** Patch `collect_sector_effects` at the import site (`game.strategy.services.system_effects_collector.collect_sector_effects`) to return synthetic effect lists. Each effect dict has shape `{'ability_name': 'EnvironmentalDamage', 'aggregate_value': 50.0, 'providers': [{'source_label': 'Ion Storm Alpha'}]}`.
**Rationale:** The collector is one of the larger collaborators in the game. Patching it lets us pin the engine's branching on aggregate_value sums, the `damage_per_turn / 100.0` per-tick scaling, the per-ship-distribution math, and the source_label fallback without standing up real ability rows.

---

## D-006 — Per-tick scaling is exact, not approximate
**Status:** Accepted
**Context:** `damage_per_tick = damage_per_turn / 100.0` and `fuel_drain_per_tick = fuel_per_turn / 100.0`. With float division and 100 ticks per turn, this is exact for any input (no FP rounding). Per-ship damage is `damage_per_tick / len(combat_ships)` which can round.
**Decision:** Use `pytest.approx` only for the per-ship-distribution assertions. Use `==` for the per-turn-to-per-tick scaling.
**Rationale:** Tests should be tight where they can be tight. If a future change introduces FP slop, we want the test to flag it.

---

## OBS-001 — `_apply_damage_to_ship` resets `current_hp` to None when `new_hp >= max_hp`, but this branch is unreachable when `damage > 0`
**Status:** Observation only
**File:** `game/strategy/engine/environmental_hazard_engine.py:192-195`
**Observation:** The code says `if new_hp < max_hp: ship.current_hp = new_hp / else: ship.current_hp = None`. When `damage > 0`, `new_hp = max(0, current_hp - damage) < current_hp <= max_hp`, so the `else` branch ("Reset to full") cannot fire. The comment "won't happen with damage > 0" acknowledges this. If a future caller passes `damage <= 0`, the branch fires and silently resets HP to full.
**Action:** Pin the dead-branch behavior with a `damage = 0` test that records `ship.current_hp` was reset to None when `current_hp == max_hp`. This locks today's behavior; if someone later "fixes" the branch, the test catches it.

---

## OBS-002 — `process_environmental_tick` returns no event when `damage_per_turn <= 0 AND fuel_per_turn <= 0`, even if effect rows exist
**Status:** Observation only
**File:** `game/strategy/engine/environmental_hazard_engine.py:122-123`
**Observation:** Two filters: (a) the early `if not damage_effects and not fuel_effects: continue` skips fleets with zero effect rows; (b) the later `if damage_per_turn <= 0 and fuel_per_turn <= 0: continue` skips when both aggregates are non-positive. Negative `aggregate_value` is theoretically allowed by the schema (e.g. a "shield-projector" could be modelled as negative damage) and a single negative row would pass the early filter but be silently dropped at the second filter without contributing healing. Whether this is intentional is unclear.
**Action:** Pin the current behavior — a single negative-damage row produces zero events. Do not heal; do not raise.

---

## OBS-003 — `process_environmental_tick` aggregates fuel drain across ships **without** dividing by ship count
**Status:** Observation only
**File:** `game/strategy/engine/environmental_hazard_engine.py:140-143`
**Observation:** Damage is divided by `len(combat_ships)` then applied per-ship; fuel drain is **not** — every ship has `fuel_drain_per_tick` drained from it. The docstring says "Fuel drain is 1/100th of fuel_drain_per_tick per tick per ship" which is consistent with the implementation but contrasts with the damage-distribution model in the same loop. A 5-ship fleet in a fuel-draining storm loses 5x the fuel a 1-ship fleet does.
**Action:** Pin the per-ship-not-divided fuel-drain behavior with an explicit test asserting total drain scales with ship count.

---

## OBS-004 — `process_open_warp_point` far-end placement is deterministic but produces non-symmetric pairings
**Status:** Observation only
**File:** `game/strategy/engine/superweapon_order_processor.py:376-384`
**Observation:** Far-end direction is derived from `current_system.global_location - target_system.global_location`, normalized by `max(abs(direction_q), abs(direction_r), 1)` (NOT euclidean), then scaled by `orbit_distance = 6` and `round()`-ed. This gives a hex on the outer ring of the target system pointing back toward the source. With diagonal source/target placements (e.g. (50,50) opening to (10,10)), the rounding can produce non-symmetric pairings. This is probably intentional (visual placement on the map) but is untested.
**Action:** Pin the math with explicit input-output cases — straight-axis source/target gives a clean unit-direction far-end; diagonal source/target gives the round() result.

---

## OBS-005 — `process_close_warp_point` accepts a legacy plain-string `order.target` for back-compat
**Status:** Observation only
**File:** `game/strategy/engine/superweapon_order_processor.py:431-438`
**Observation:** If `order.target` is a dict, both `destination_id` and `expected_hex` are extracted; if it's a non-dict (legacy), the whole `order.target` is treated as the destination_id and `expected_hex` is None. Without `expected_hex`, the wrong-sector validation at line 465 is skipped and any fleet at the named system can close the link.
**Action:** Pin the legacy-string branch with a test that constructs `Order(OrderType.CLOSE_WARP_POINT, target='Beta')` and asserts the warp link is removed without sector-hex validation.

---

## OBS-006 — `_get_reference_planet` returns the **first** planet in the system, not the closest to the fleet
**Status:** Observation only
**File:** `game/strategy/engine/superweapon_order_processor.py:756-771`
**Observation:** The helper iterates `system.planets` and returns the first one. Comment says "Find any planet in the system... needed so the strategic ability scanner can resolve system/sector scope from a concrete planet reference." For system-scope stabilizer checks this is fine; for sector-scope it could matter. The fleet's actual hex is already passed separately to the stabilizer registry, so this is probably just a "give the registry a reference planet for system-scope traversal" hand-wave.
**Action:** Pin the "first-planet" semantics with a test that puts two planets in the system at different distances and asserts the first one is what gets passed to `find_blocking_stabilizer`.

---

## OBS-007 — `ActionExecutionEngine` does not pop completed orders; the order processor is responsible
**Status:** Observation only
**File:** `game/strategy/engine/action_execution_engine.py:170-184` and `superweapon_order_processor.py:_finalize_superweapon`
**Observation:** When `order.execution_progress >= action_time`, the engine calls `self._order_processor.execute_action_order(...)` and returns. The engine never calls `fleet.pop_order()` for completed action orders. The order processor pops the order in `_finalize_superweapon` (line 105) or in COLONIZE/TRANSFER handlers (not in scope here). The existing test `test_multi_order_chain` confirms this contract — the test simulates the processor calling `fleet.pop_order()` on first call.
**Action:** Pin this contract explicitly: in `test_action_execution_engine_gaps.py`, write a test that uses a mock processor which does NOT pop the order, then assert the engine's next-tick call still sees the same order (the engine itself does not pop).

---

## OBS-008 — `_validate_tick_inputs` raises **before** any mutation, but only checks `fleet.location is None`
**Status:** Observation only
**File:** Both `environmental_hazard_engine.py:60-69` and `action_execution_engine.py:70-79`
**Observation:** The PROJ-251 precondition check is identical in both engines. It catches `fleet.location is None` and raises `ValidationException`. It does not check empty `empires`, missing `fleet.id`, or `empire.id is None`. A fleet with `location=None` raises; a fleet with `location=HexCoord(0, 0)` and no other fields validates and proceeds.
**Action:** Pin both the raise (unhappy path) and the no-raise (happy path) with explicit tests. Do not test the missing checks — those would be aspirational.

---

## D-007 — Treat fixture sharing across files via copy, not module
**Status:** Accepted
**Context:** The existing `test_superweapon_order_processor.py` defines `mock_galaxy`, `mock_system`, `mock_planet`, `mock_fleet`, `mock_ship_with_ability`, `component_registry` as `@pytest.fixture` at module level. They are not in a `conftest.py`.
**Decision:** Copy the fixtures we need into the new gap-fill test files, not into a shared `conftest.py`. The existing fixtures are tied to specific tests and may evolve under the original file's authority.
**Rationale:** Avoids cross-file coupling. PROJ-341's tests stay self-contained; if the original fixtures change, our gap-fill tests do not silently break.
