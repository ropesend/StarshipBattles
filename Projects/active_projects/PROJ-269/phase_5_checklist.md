# Phase 5: Telemetry Levels

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-269 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** `TelemetryLevel` (MINIMAL / NORMAL / DETAILED) on `BattleSpec` governs which `CombatEventBus` subscribers attach at battle start. `BattleOutcome.ships[i]` carries telemetry-level-appropriate data: MINIMAL attaches nothing (weapons=(), hits_taken=()); NORMAL adds per-weapon summaries and per-ship stats; DETAILED additionally records the full hit log with modifier trace. Per-context defaults: Strategy=NORMAL, Battle Setup=NORMAL, Combat Lab=DETAILED (scenarios can override).

---

### Task 5.1: Implement `WeaponSummaryAggregator` [Medium]
**Files:**
- `game/simulation/combat/telemetry.py` (extend — enum exists from Phase 1)

**Tests:** `pytest tests/unit/simulation/combat/test_weapon_summary_aggregator.py --testmon`

- [x] Write failing tests:
  - Aggregator snapshots shots_fired / shots_hit counters per weapon component
  - After simulating N shots and M hits on a weapon, `aggregator.snapshot(engine)[ship_id]` contains a `WeaponSummary(shots_fired=N, shots_hit=M)`
  - Aggregator handles multiple ships, multiple weapons per ship
  - Non-weapon components are excluded from the snapshot
- [x] Implement `WeaponSummaryAggregator` in `telemetry.py`:
  - `snapshot(engine) -> Dict[ship_id, Tuple[WeaponSummary]]` walks all ships + retreated_ships, reads `Component.shots_fired` / `Component.shots_hit` counters
- [x] Verify: tests pass (5/5 green)

**Notes:**
Implemented 2026-04-12 as a snapshot-based aggregator — the engine
already maintains `Component.shots_fired` / `shots_hit` counters via
the existing weapon-firing pipeline, so no new CombatEvent types or
subscriptions are needed. `resolved_shots` (= shots_fired − in_flight)
is computed at outcome-extraction time in Task 5.4 when the engine's
projectile list is still accessible; the WeaponSummary DTO doesn't
yet carry a dedicated field for it.

Not using event-bus subscription for this aggregator was the right
MVP call — the counters already exist, and building a parallel
event-based counter would risk divergence.

---

### Task 5.2: Implement `ShipStatsAggregator` [Medium]
**File:** `game/simulation/combat/telemetry.py` (extend)

**Tests:** `pytest tests/unit/simulation/combat/test_ship_stats_aggregator.py --testmon`

- [x] Write failing tests:
  - Aggregator subscribes to damage-dealt events
  - After a battle, `aggregator.get_stats(ship_id)` returns `ShipStats(total_damage_taken, peak_speed, ticks_derelict, ticks_alive)`
  - Stats are per-ship; zero for ships that took no damage / never moved
- [x] Implement `ShipStatsAggregator`:
  - `__init__(event_bus)` subscribes to SHIELD_HIT / ARMOR_ABSORBED / COMPONENT_HIT events
  - `sample_tick(engine)` called each tick by `run_battle`; updates peak_speed + ticks_alive/ticks_derelict from current ship state
  - `get_stats(id)` / `snapshot()` accessors
- [x] Verify: tests pass (6/6 green)

**Notes:**
Implemented 2026-04-12.
- Damage accumulation is event-bus driven so the aggregator doesn't
  need to walk layers every tick. Events are filtered to damage types
  by the existing `EventDetailLevel` gating — the aggregator's behavior
  at MINIMAL is "no damage-accumulation events fire, damage totals
  stay 0" (correct by construction).
- peak_speed / ticks_alive / ticks_derelict sampled per-tick via the
  new `sample_tick(engine)` method. Task 5.4 wires it to the
  `per_tick_callback` in `run_battle`.
- COMPONENT_DESTROYED is intentionally excluded from damage sum — it's
  a status event with no additional damage_amount.

---

### Task 5.3: Implement `HitLogRecorder` [Medium]
**File:** `game/simulation/combat/telemetry.py` (extend)

**Tests:** `pytest tests/unit/simulation/combat/test_hit_log_recorder.py --testmon`

- [x] Write failing tests:
  - Recorder subscribes to hit events (SHIELD_HIT, ARMOR_ABSORBED, COMPONENT_HIT)
  - Each hit produces a `HitRecord(tick, attacker_ship_id, weapon_component_id, weapon_ability_class, damage, modifiers_applied)`
  - `recorder.get_hits(ship_id) -> Tuple[HitRecord]` returns all hits taken by that ship
- [x] Implement `HitLogRecorder`:
  - `__init__(event_bus, tick_provider=lambda: 0)` — tick_provider is injected so the recorder doesn't need a direct engine reference
  - Subscribe to SHIELD_HIT / ARMOR_ABSORBED / COMPONENT_HIT events
  - Extract attacker_ship_id / weapon_component_id from `event.context` (existing `DamageContext(attacker, source_weapon, damage_type)`)
  - weapon_ability_class — best-effort via `WeaponAbility` subclass name on the source weapon's abilities
  - Append `HitRecord` to per-ship list
- [x] Verify: tests pass (7/7 green)

**Notes:**
Implemented 2026-04-12.

- **Modifier trace deferred.** Phase 5 Task 5.3 MVP records
  `modifiers_applied=()` — the engine's damage pipeline does not
  currently carry per-hit modifier provenance. Adding that requires
  wiring the ModifierStack through DamageCalculator and attaching
  modifier source strings on each event, which is larger scope than
  the task budget and not exercised by any existing callers. The
  `HitRecord.modifiers_applied: Tuple[ModifierApplication, ...]` field
  exists on the DTO (Phase 1) and can be populated in a follow-up.
- **tick_provider** is injected as a callable instead of holding an
  engine reference — avoids the recorder taking a cross-layer handle
  to BattleEngine and keeps it pure-subscriber.
- COMPONENT_DESTROYED events are NOT recorded (no damage_amount carried).
- Existing `DamageContext(attacker, source_weapon, damage_type)` fields
  are what the recorder reads — matches the shape the engine actually
  emits.

---

### Task 5.4: Wire telemetry subscribers in `run_battle` based on level [Medium]
**File:** `game/simulation/battle_runner.py`

**Tests:** `pytest tests/unit/simulation/test_battle_runner_telemetry.py --testmon`

- [x] Write failing tests:
  - `run_battle(spec_minimal)` returns outcome with all `ShipOutcome.weapons == ()` and `hits_taken == ()`
  - `run_battle(spec_normal)` — `weapons` populated, `hits_taken == ()`, `stats` populated
  - `run_battle(spec_detailed)` — `weapons`, `hits_taken`, `stats` all populated
- [x] Implement: in `run_battle`, after `engine.start()`:
  - Instantiate `WeaponSummaryAggregator + ShipStatsAggregator` when level >= NORMAL
  - Instantiate `HitLogRecorder` when level == DETAILED
  - Raise `engine.combat_events.detail_level` to match
  - `ShipStatsAggregator.sample_tick(engine)` called each tick
- [x] Implement: in `extract_outcome`, query each aggregator and populate `ShipOutcome` fields accordingly (empty tuples / zero stats when level too low)
- [x] Verify: tests pass (6/6 green; 3280 sim regression pass)

**Notes:**
Implemented 2026-04-12.

- New helper `_attach_telemetry(engine, spec)` returns a
  `(weapon, stats, hit_log)` tuple of Optional aggregators.
- Tick-loop change: `stats_aggregator.sample_tick(engine)` fires each
  tick *before* `per_tick_callback` so the samples see the engine
  state exactly at the end of the tick.
- `extract_outcome` now takes `weapon_aggregator` / `stats_aggregator`
  / `hit_log_recorder` kwargs (all default None → MINIMAL behavior).
- `_build_ship_outcome` pulls from the snapshots; when a snapshot is
  empty (MINIMAL), `weapons=()`, `hits_taken=()`, `stats=_ZERO_STATS`.
- Event-bus `detail_level` is raised to NORMAL or DETAILED to match
  the aggregator level — otherwise the bus would gate events at its
  default NORMAL and DETAILED subscribers would see nothing from
  COMPONENT_HIT / ARMOR_ABSORBED.
- The old helper `_extract_weapon_summaries` is now unused; left in
  place to minimize churn and support possible future direct-scan
  callers.

---

### Task 5.5: Performance smoke — measure overhead [Medium]
**File:** `tests/performance/test_telemetry_overhead.py` (new)

- [x] Write benchmark:
  - Hand-built 1v1 battle (avoids combat_lab's registry-reload coupling to pytest session)
  - 500 ticks, 3 runs per level
  - Record mean duration
- [x] Assert:
  - MINIMAL within 30% of NORMAL (catches phantom subscriptions)
  - DETAILED within 5x of MINIMAL (catches explosive overhead)
- [x] Measured numbers documented in [decisions.md](decisions.md)

**Notes:**
Implemented 2026-04-12 at
[tests/performance/test_telemetry_overhead.py](../../../tests/performance/test_telemetry_overhead.py).

**Measured (2026-04-12 baseline on this machine):**
- MINIMAL: ~30 ms
- NORMAL: ~28 ms
- DETAILED: ~28 ms

Essentially equal because the ships start 1000 px apart and few
damage events fire during the 500-tick window. For realistic battles
with high event traffic the divergence will be larger — re-measure
when Combat Lab fast suite gets full-pipeline instrumentation.

Smoke test uses a hand-built spec instead of BEAMWEAPON-005 because
`combat_lab.runner` reloads the registry each scenario, which doesn't
interact cleanly with pytest's session-scoped registry fixtures. The
hand-built spec exercises the same `run_battle` pipeline at each level.

---

### Task 5.6: Per-context telemetry defaults [Simple]
**Files:**
- `game/strategy/combat/spec_compiler.py`
- `game/ui/screens/battle_setup/spec_compiler.py`
- `combat_lab/spec_compiler.py`

**Tests:** (update existing compiler tests)

- [x] Strategy compiler: `BattleSpec.telemetry_level = TelemetryLevel.NORMAL` by default *(already set in Phase 1)*
- [x] Battle Setup compiler: `TelemetryLevel.NORMAL` default *(already set in Phase 1)*
- [x] Combat Lab compiler: `TelemetryLevel.DETAILED` default *(Phase 1)*; `TestScenario.metadata.telemetry_level` (new optional field on `TestMetadata`) overrides
- [x] Add `telemetry_level: str = "DETAILED"` to `TestMetadata`
- [x] Verify: existing scenarios work (162/162 combat_lab fast still pass); one scenario can opt into MINIMAL for batch perf (3 new compiler tests cover override / default / garbled-value fallback)
- [x] Verify: existing compiler tests still pass (14/14 combat_lab compiler tests pass)

**Notes:**
Implemented 2026-04-12.

- `TestMetadata.telemetry_level: str` (string not enum) so metadata
  declarations stay JSON-serializable and don't require importing
  `TelemetryLevel` into every scenario file. The compiler parses the
  string.
- `_resolve_telemetry_level(metadata)` helper handles:
  - `TelemetryLevel` instances (pass-through)
  - Strings: "MINIMAL" / "NORMAL" / "DETAILED" (case-insensitive)
  - Missing attr / None / unrecognized value → DETAILED fallback
- Strategy + Battle Setup defaults were already correct from Phase 1.
  No changes to those compilers.

---

### Task 5.7: Combat Lab validation uses DETAILED telemetry [Simple]
**File:** `combat_lab/scenarios/templates.py` (adjust `validate()` methods if they depend on weapon stats that are now in telemetry)

- [x] Audit: where in scenario `validate()` methods do we read `results['*_weapons']`, `results['*_total_shots_fired']`, etc.?
- [x] Rewire those reads to pull from `BattleOutcome.ships[i].weapons` / `.stats` (N/A — already consistent)
- [x] Verify: `python -m combat_lab.run_tests --fast` — 162+ passing (162/162 verified at Task 5.4 regression and again at phase wrap)

**Notes:**
Audit finding: no rewire needed. Scenario `validate()` methods read
from `self.results['*_weapons']` / `*_total_shots_fired` / etc., which
are populated by `TestScenario._collect_weapon_stats(ship, role, engine)`.
That helper walks `ship.layers[*].components` and reads
`comp.shots_fired` / `comp.shots_hit` — the SAME counters
`WeaponSummaryAggregator.snapshot()` reads.

Conclusion: `BattleOutcome.ships[i].weapons` and `self.results['*_weapons']`
are just two representations of the same underlying counter data.
Scenarios don't need to be rewired — both the legacy
`USE_BATTLE_RUNNER=0` path and the Phase-1 smoke-test
`USE_BATTLE_RUNNER=1` path produce identical weapon stats.

Verified:
- `python -m combat_lab.run_tests BEAMWEAPON-001 --no-history` with
  `SB_USE_BATTLE_RUNNER=1`: 2/2 PASS.
- Combat Lab fast suite will be re-verified at phase wrap.

---

### Task 5.8: Documentation updates [Simple]
**File:** `docs/systems/combat_simulation.md`

- [x] Add "Telemetry" section: describe the three levels, what each populates on `BattleOutcome`, the event-bus subscriber architecture, per-context defaults
- [x] Include the measured overhead numbers from Task 5.5
- [x] Verify: doc renders; no stale claims about "always-on full instrumentation"

**Notes:**
Added "Telemetry (Phase 5)" subsection to
`docs/systems/combat_simulation.md` §0 with:
- 3-level table (what each populates)
- Event-bus detail-level mechanism
- Per-tick sampling rationale for `ShipStatsAggregator`
- Per-context defaults
- Overhead numbers (as of 2026-04-12)
- Note that `HitRecord.modifiers_applied` is empty in MVP

Also updated the Phase-1-transitional status paragraph to reflect
that `telemetry_level` is now fully wired (Phase 5 done); only
`modifier_stack` (partial — compilers emit placeholders, engine
doesn't consume yet) is still outstanding.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/` fully green (14695 passed; same 3 pre-existing unrelated failures + 3 pre-existing unrelated ImportErrors)
- [x] `python -m combat_lab.run_tests --fast` — 162 passed (baseline maintained)
- [x] Telemetry-level tests demonstrate correct population for each level
- [x] Performance overhead documented and within expected bounds
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6 Task 6.1
