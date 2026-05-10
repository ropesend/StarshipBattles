# FEAT-15: Per-planet probability roll for intrinsic abilities (make planet effects rare)

## Description
Today, planet intrinsic abilities are assigned **deterministically by planet
type**. Every `ICE_GIANT` rolls `ShieldModifier`, every `CRYOPLANET` rolls
`ThrustModifier`, etc. (`data/planet_types.json`).

This produces too many affected planets. The user wants intrinsic abilities to
remain possible but to occur **rarely** on a per-planet basis — flavour, not
default behaviour.

## Required changes
1. **Schema extension** — `data/planet_types.json` ability entries gain a
   `chance` field (float, default `1.0` for backward compat with stars/storms
   if shared). For planets, default new entries to a low value (e.g., `0.1`)
   and tune from there.
2. **Roll path** — extend `roll_intrinsic_abilities`
   (`game/strategy/services/ability_sources/intrinsic_roll.py:12-61`) or the
   planet-specific wrapper `_apply_planet_intrinsic_abilities` in
   `game/strategy/data/galaxy_system_generator.py:240-268` to consult the
   `chance` field and skip the ability entirely on a failed roll. Keeps the
   value-min/max roll as-is when the ability does fire.
3. **Test coverage** — unit tests for: chance=1.0 always fires; chance=0.0
   never fires; chance=0.1 fires roughly 10% over a deterministic seed sweep.
4. **Tune existing planet abilities** — set explicit low chances on
   `ShieldModifier` (ICE_GIANT) and `ThrustModifier` (CRYOPLANET) and any
   other planet abilities currently set to deterministic.

## Out of scope
- Adding new planet ability types.
- Changing star or storm ability rates (those are fine as-is).
- Per-empire / per-difficulty modifiers on the chance.

## Acceptance
- A typical 100-planet galaxy contains a noticeable minority — not majority —
  of planets with abilities.
- Generation is deterministic for a given seed (chance roll uses the same RNG
  stream as the value rolls).
- The chance field is honoured for every planet ability declared in
  `planet_types.json`.

## Priority
Medium

## Status
Awaiting Confirmation

## Work Log
- 2026-04-27: Created from QA Session 20260427_151244.
- 2026-04-27: Investigation complete. Approved approach: extend the shared `roll_intrinsic_abilities` helper (Option A) — schema-consistent across all four PROJ-301..304 registries; default `chance=1.0` consumes zero extra RNG so stars/warps/archetypes remain byte-identically deterministic. Recommended tuning table approved; DYSON_SPHERE stays at `chance=1.0` (defining feature).
- 2026-04-27: Implementation complete.
  - **Helper** (`game/strategy/services/ability_sources/intrinsic_roll.py`): per-ability `chance` field gates the roll. When `chance < 1.0`, draws `rng.random()` once and `continue`s on failure. The `chance` key is stripped from the output dict (it's a generation-time gate, not runtime state). Templates without `chance` consume zero extra RNG draws — preserves byte-identical determinism.
  - **Data** (`data/planet_types.json`): version bumped 1.0 → 1.1; description extended; `chance` populated per the table below.
  - **Tests:**
    - 6 new unit tests in `tests/unit/strategy/services/ability_sources/test_intrinsic_roll.py` under `TestRollIntrinsicAbilitiesChanceGate` (chance=1.0 always fires; chance=0.0 never fires; chance=0.1 ≈ 10% over 1000 seeds; chance key stripped; seeded RNG determinism; chance-less templates produce byte-identical output).
    - 1 new schema test in `tests/integration/data/test_intrinsic_registries_coverage.py` (`test_planet_types_chance_fields_in_valid_range`) walks every ability with a `chance` field and asserts numeric in [0.0, 1.0].
    - All 5 existing tests in `tests/unit/strategy/data/test_intrinsic_rng_determinism.py` still pass — confirms star/warp/archetype RNG streams are unshifted.
  - **Docs:** `docs/systems/strategy_layer.md` and `docs/04_SERVICES.md` updated; both `Last verified:` timestamps bumped.
  - **Test results:**
    - Targeted (FEAT-15 scope): 114/114 pass.
    - Broader (`tests/unit/strategy/`, `tests/integration/strategy/`, `tests/integration/data/`): 3550 pass, 1 skipped.
    - Full sharded suite: 15731 pass / 15732, 1 pre-existing test-isolation flake in `test_collect_movements_respects_speed` (passes when run alone; unrelated to FEAT-15 — fleet movement engine, not intrinsic abilities).
  - **Estimated effect on a 100-planet galaxy** (uniform type distribution, ~8 planets per type):
    - Before: ~50 planets with abilities (~50%).
    - After: 8 × (0.20 + 0.10 + 0.15 + 0.10 + 0.25 + 1.00) = ~14 planets with abilities (~14%). Likely lower in practice — DYSON_SPHERE/CHTHONIAN are intrinsically rarer types.

### Tuning table applied
| Planet type | Ability | Chance | Rationale |
|---|---|---|---|
| MAGMA | EnvironmentalDamage (thermal, 0.1–0.5/tick) | 0.20 | Magma planets are dramatic — slightly above baseline so the type still feels distinct. |
| CRYOPLANET | ThrustModifier (0.85–0.95) | 0.10 | Mild thrust debuff — nuisance, not crisis. |
| JOVIAN | StrategicSpeedModifier (0.7–0.9) | 0.15 | Strategic-layer effect on a common type — keep occasional. |
| ICE_GIANT | ShieldModifier (0.85–0.95) | 0.10 | Per ticket call-out. |
| CHTHONIAN | EnvironmentalDamage (radiation, 0.05–0.2/tick) | 0.25 | Rare planet type; when one exists radiation should usually be on. |
| DYSON_SPHERE | EnvironmentalDamage (radiation, 0.3–0.6/tick) | 1.00 (omitted = default) | Defining feature of a Dyson sphere; kept deterministic. |
