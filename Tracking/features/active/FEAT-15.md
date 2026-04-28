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
Pending

## Work Log
- 2026-04-27: Created from QA Session 20260427_151244.
