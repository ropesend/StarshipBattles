# Phase 5: Telemetry Levels

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-269 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** `TelemetryLevel` (MINIMAL / NORMAL / DETAILED) on `BattleSpec` governs which `CombatEventBus` subscribers attach at battle start. `BattleOutcome.ships[i]` carries telemetry-level-appropriate data: MINIMAL attaches nothing (weapons=(), hits_taken=()); NORMAL adds per-weapon summaries and per-ship stats; DETAILED additionally records the full hit log with modifier trace. Per-context defaults: Strategy=NORMAL, Battle Setup=NORMAL, Combat Lab=DETAILED (scenarios can override).

---

### Task 5.1: Implement `WeaponSummaryAggregator` [Medium]
**Files:**
- `game/simulation/combat/telemetry.py` (extend — enum exists from Phase 1)

**Tests:** `pytest tests/unit/simulation/combat/test_weapon_summary_aggregator.py --testmon`

- [ ] Write failing tests:
  - Aggregator subscribes to weapon-fire + hit events
  - After simulating N shots and M hits on a weapon, `aggregator.get_summary(ship_id, weapon_component_id)` returns `WeaponSummary(shots=N, hits=M, resolved_shots=N-in_flight)`
  - Aggregator handles multiple ships, multiple weapons per ship
  - Aggregator is a no-op when no events are published (MINIMAL level case)
- [ ] Implement `WeaponSummaryAggregator` in `telemetry.py`:
  - `__init__(event_bus)` subscribes to weapon-fire and hit events
  - Maintains `Dict[(ship_id, weapon_id), WeaponSummary]`
  - `snapshot_at_end(engine) -> Dict[ship_id, Tuple[WeaponSummary]]` computes `resolved_shots = shots - in_flight` by inspecting remaining projectiles at battle end
- [ ] Verify: tests pass

**Notes:**

---

### Task 5.2: Implement `ShipStatsAggregator` [Medium]
**File:** `game/simulation/combat/telemetry.py` (extend)

**Tests:** `pytest tests/unit/simulation/combat/test_ship_stats_aggregator.py --testmon`

- [ ] Write failing tests:
  - Aggregator subscribes to damage-dealt and movement events
  - After a battle, `aggregator.get_stats(ship_id)` returns `ShipStats(total_damage_taken, peak_speed, ticks_derelict, ticks_alive)`
  - Stats are per-ship; zero for ships that took no damage / never moved
- [ ] Implement `ShipStatsAggregator`:
  - `__init__(event_bus)` subscribes to damage events + per-tick velocity samples
  - Maintains `Dict[ship_id, ShipStats]`
  - Track peak_speed via the tick callback (engine already tracks velocity — hook that)
  - Track `ticks_derelict` and `ticks_alive` via status-change events
- [ ] Verify: tests pass

**Notes:**

---

### Task 5.3: Implement `HitLogRecorder` [Medium]
**File:** `game/simulation/combat/telemetry.py` (extend)

**Tests:** `pytest tests/unit/simulation/combat/test_hit_log_recorder.py --testmon`

- [ ] Write failing tests:
  - Recorder subscribes to hit events (SHIELD_HIT, ARMOR_ABSORBED, COMPONENT_HIT, COMPONENT_DESTROYED)
  - Each hit produces a `HitRecord(tick, attacker_ship_id, weapon_component_id, weapon_ability_class, damage, modifiers_applied)`
  - `recorder.get_hits(ship_id) -> Tuple[HitRecord]` returns all hits taken by that ship
  - Modifier trace: each `HitRecord.modifiers_applied` is a tuple of `ModifierApplication(source, stack_group, value)` explaining where each modifier came from (e.g., "species:Terran contributed +0.2 accuracy")
- [ ] Implement `HitLogRecorder`:
  - `__init__(event_bus, modifier_stack)` — modifier_stack needed to explain which modifiers applied to each hit
  - Subscribe to the combat events
  - Append `HitRecord` to per-ship list
- [ ] Verify: tests pass

**Notes:** Modifier trace requires each `Modifier` to carry its `source` (added in Phase 1). If that didn't happen fully, it's a debt to pay here.

---

### Task 5.4: Wire telemetry subscribers in `run_battle` based on level [Medium]
**File:** `game/simulation/battle_runner.py`

**Tests:** `pytest tests/unit/simulation/test_battle_runner_telemetry.py --testmon`

- [ ] Write failing tests:
  - `run_battle(spec_minimal)` returns outcome with all `ShipOutcome.weapons == ()` and `hits_taken == ()`
  - `run_battle(spec_normal)` — `weapons` populated, `hits_taken == ()`, `stats` populated
  - `run_battle(spec_detailed)` — `weapons`, `hits_taken`, `stats` all populated
- [ ] Implement: in `run_battle`, before battle starts:
  - Instantiate `WeaponSummaryAggregator + ShipStatsAggregator` when level >= NORMAL
  - Instantiate `HitLogRecorder` when level == DETAILED
  - All aggregators subscribe to `engine.event_bus`
- [ ] Implement: in `extract_outcome`, query each aggregator and populate `ShipOutcome` fields accordingly (empty tuples when level too low)
- [ ] Verify: tests pass

**Notes:**

---

### Task 5.5: Performance smoke — measure overhead [Medium]
**File:** `tests/performance/test_telemetry_overhead.py` (new)

- [ ] Write benchmark:
  - Reference scenario: `BEAMWEAPON-005` (500 ticks, medium complexity)
  - Run 10 times each at MINIMAL / NORMAL / DETAILED
  - Record mean duration
- [ ] Assert:
  - MINIMAL is within ±5% of a baseline run with `telemetry_level=MINIMAL` + no subscribers attached (confirms we aren't paying for phantom subscriptions)
  - NORMAL overhead vs MINIMAL: document the delta (expect <20%)
  - DETAILED overhead vs NORMAL: document the delta (expect <50%)
- [ ] If MINIMAL overhead >5%: investigate — telemetry should be truly zero-cost when not subscribed

**Notes:** Document measured overhead in [decisions.md](decisions.md) as a perf baseline for future comparison.

---

### Task 5.6: Per-context telemetry defaults [Simple]
**Files:**
- `game/strategy/combat/spec_compiler.py`
- `game/ui/screens/battle_setup/spec_compiler.py`
- `combat_lab/spec_compiler.py`

**Tests:** (update existing compiler tests)

- [ ] Strategy compiler: `BattleSpec.telemetry_level = TelemetryLevel.NORMAL` by default
- [ ] Battle Setup compiler: `TelemetryLevel.NORMAL` default; UI may override (future)
- [ ] Combat Lab compiler: `TelemetryLevel.DETAILED` default; `TestScenario.metadata.telemetry_level` (new optional field on `TestMetadata`) overrides
- [ ] Add `telemetry_level: TelemetryLevel = TelemetryLevel.DETAILED` to `TestMetadata`
- [ ] Verify: existing scenarios work; one scenario can opt into MINIMAL for batch perf
- [ ] Verify: existing compiler tests still pass

**Notes:**

---

### Task 5.7: Combat Lab validation uses DETAILED telemetry [Simple]
**File:** `combat_lab/scenarios/templates.py` (adjust `validate()` methods if they depend on weapon stats that are now in telemetry)

- [ ] Audit: where in scenario `validate()` methods do we read `results['*_weapons']`, `results['*_total_shots_fired']`, etc.?
- [ ] Rewire those reads to pull from `BattleOutcome.ships[i].weapons` / `.stats` (which are populated because Combat Lab defaults to DETAILED)
- [ ] Verify: `python -m combat_lab.run_tests --fast` — 162+ passing (regression)

**Notes:**

---

### Task 5.8: Documentation updates [Simple]
**File:** `docs/systems/combat_simulation.md`

- [ ] Add "Telemetry" section: describe the three levels, what each populates on `BattleOutcome`, the event-bus subscriber architecture, per-context defaults
- [ ] Include the measured overhead numbers from Task 5.5
- [ ] Verify: doc renders; no stale claims about "always-on full instrumentation"

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` fully green
- [ ] `python -m combat_lab.run_tests --fast` — 162+ passing (regression gate)
- [ ] Telemetry-level tests demonstrate correct population for each level
- [ ] Performance overhead documented and within expected bounds
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6 Task 6.1
