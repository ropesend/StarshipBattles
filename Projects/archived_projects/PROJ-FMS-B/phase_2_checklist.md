# PROJ-FMS-B Phase 2: Warhead detonation + Laserhead beam behavior with threshold

> See [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) for full design context.

**Goal:** Round out the strategic-entry damage by adding the laserhead pass and tightening warhead damage application. After this phase, both warhead and laserhead mines work at the strategic layer.

## Tasks

### Warhead detonation
- [x] Confirm Phase 1 already applied `Warhead.damage` through the damage pipeline; if not (e.g., placeholder direct HP subtraction), wire properly via [`damage_calculator.py:44-84`](../../../game/simulation/combat/damage_calculator.py#L44).
- [x] Multiple warheads on a single mine (rare but supported): apply each warhead's damage as a separate pass through the pipeline (or sum and apply once — pick whichever matches existing weapon-stacking semantics; document the decision in [`decisions.md`](decisions.md)).
- [x] Verify shields-first / armor-second / hull-third order is honored for warhead damage.

### Laserhead pass
- [x] Replace the Phase 1 TODO in `minefield_resolver.py` with a real laserhead pass.
- [x] For each laserhead mine in the group (in some deterministic order — design choice in [`decisions.md`](decisions.md)):
  - Compute `expected_hit_chance` for the target ship using `BeamWeaponAbility.calculate_hit_chance()` at [`weapons.py:312-331`](../../../game/simulation/components/abilities/weapons.py#L312). Inputs: laserhead's beam attrs, mine's `SmallTargetingSensor` accuracy modifiers (via existing stat aggregator), target's `defense_score`.
  - If `expected_hit_chance < mine_group.expected_hit_chance_threshold`, **skip** the laserhead (don't fire, don't consume).
  - Otherwise: roll standard beam hit roll, apply damage via damage pipeline regardless of hit/miss source. Consume the laserhead.
- [x] Laserheads consumed by one ship's pass are unavailable to subsequent ships in the same entry sequence.
- [x] Emit `CombatEvent`s for both hits and misses (so UI can show "laserhead fired").

### Strategic detonation order
- [x] Document final order in [`decisions.md`](decisions.md): per ship, warhead pass first then laserhead pass? Or all warheads across all ships, then all laserheads? Recommend per-ship interleaving: warhead → laserhead → next ship, since the user's instinct was "ship enters → field reacts."

### Tests
- [x] Lay 5 warhead + 5 laserhead mines via two `StrategicMineLayerAbility` invocations.
- [x] Enemy destroyer enters: confirm both passes run; warheads can trigger; laserheads fire only if `expected_hit_chance >= threshold`.
- [x] Lower threshold below the destroyer's hit-chance for a given laserhead → laserhead fires. Raise above → laserhead skipped (no consume).
- [x] `CombatSensor` on a laserhead mine increases its `expected_hit_chance` vs the same target — verify via the existing stat aggregator path.
- [x] Threshold = 0.0 → laserheads always fire when in range (since hit chance ≥ 0 always).
- [x] Threshold = 1.0 → laserheads never fire (since hit chance < 1 in practice).
- [x] Many-trial statistical check: laserhead hit rate ≈ standard beam hit-chance against the same target.

## Verification
- `python Tools/test_sharded/test_sharded.py`
- `pytest tests/unit/strategy/engine/test_minefield_resolver.py -v -k laserhead`
- Manual: lay mixed mine designs in a hex, raise/lower threshold, observe laserhead behavior.

## Exit criteria
- Both warhead and laserhead passes work at strategic entry.
- Threshold gate is purely deterministic (no random roll for the gate itself; only the standard beam roll after gate passes).
- `SmallTargetingSensor` improves laserhead expected hit chance.
- No regressions.
