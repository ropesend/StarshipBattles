# Phase 1: Per-Battle RNG Injection

**Objective:** Replace global `random.seed()` with per-battle `random.Random(seed)` instances threaded through all simulation combat code.

**Key Principle:** No simulation code should import or use the module-level `random` functions. All randomness flows through an injected `random.Random` instance.

---

## Background

Currently `BattleEngine.start(seed=N)` calls `random.seed(N)` on the process-global Python RNG. All downstream code (`damage_calculator`, `collision`, `weapon_firing_system`) consumes from this shared state via `random.random()`, `random.choices()`, etc. This means:
- Determinism depends on call order across unrelated subsystems
- Strategy-layer RNG calls before battle seeding corrupt the sequence
- Parallel battles are impossible without process isolation

## Design

1. `BattleEngine.__init__` or `start()` creates `self._rng = random.Random(seed)`
2. `self._rng` is passed to `DamageCalculator`, `WeaponFiringSystem`, collision functions
3. `ConflictResolutionEngine` gets its own `self._rng = random.Random(strategy_seed)` for strategy-layer randomness
4. Remove all `random.seed()` calls on the module-level RNG from simulation code
5. Remove all direct `random.X()` calls from simulation combat code — use `rng.X()` instead

---

## Checklist

### Discovery
- [ ] Grep `game/simulation/` for all `import random` and `from random import` statements
- [ ] Grep `game/simulation/` for all `random.` calls (seed, random, choice, choices, sample, uniform, randint, etc.)
- [ ] Grep `game/engine/collision.py` for `random.` calls
- [ ] Grep `game/strategy/engine/conflict_resolution_engine.py` for `random.` calls
- [ ] Document complete list of call sites that need migration

### Tests First (TDD)
- [ ] Write test: two BattleEngine runs with same seed produce identical tick-by-tick results
- [ ] Write test: two BattleEngine runs with different seeds produce different results
- [ ] Write test: BattleEngine determinism is NOT affected by `random.random()` calls made before `start()`
- [ ] Write test: ConflictResolutionEngine with same seed produces identical outcomes
- [ ] Write test: BattleEngine RNG is isolated — calling `random.random()` after `start()` but outside engine doesn't affect battle
- [ ] Run tests — confirm they fail (global RNG means isolation tests fail)

### Implementation
- [ ] Add `rng: random.Random` field to `BattleEngine`, created in `start()` from seed
- [ ] Update `BattleEngine` to pass `self._rng` to subsystems that need randomness
- [ ] Update `DamageCalculator` to accept and use `rng` parameter instead of `random.choices()`
- [ ] Update `collision.py` functions to accept and use `rng` parameter instead of `random.random()`
- [ ] Update `WeaponFiringSystem` to accept and use `rng` parameter (if it calls random directly)
- [ ] Update `ConflictResolutionEngine` to create its own `self._rng = random.Random(seed)` instance
- [ ] Remove `random.seed()` call from `BattleEngine.start()`
- [ ] Remove module-level `random` imports from migrated files (or leave only for non-combat uses)
- [ ] Run tests — confirm they pass

### Verification
- [ ] Run full test suite (`python scripts/test_sharded.py`) — no regressions
- [ ] Run simulation tests (`python -m simulation_tests.run_tests`) — all pass
- [ ] Grep `game/simulation/` for remaining `random.seed(` calls — should be zero
- [ ] Grep `game/simulation/combat/` for remaining `random.random(` or `random.choices(` — should be zero
