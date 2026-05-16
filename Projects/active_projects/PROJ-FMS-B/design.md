# PROJ-FMS-B Design — Mines slice

This project's slice of the shared design. **See [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) for the canonical, end-to-end design.** Only PROJ-FMS-B-specific notes go here.

## In scope
- `StrategicMineLayerAbility` and `TacticalMineLayerAbility` behavior.
- `WarheadAbility` detonation + `LaserheadAbility` beam fire behavior.
- `RamTargetAbility` behavior (since it relies on warheads).
- `minefield_resolver.py` for strategic entry damage.
- Per-tick tactical mine behavior in `battle_engine`.
- Sector scatter (deterministic, battle-boundary-or-fallback).
- Sensitivity (LOW/MED/HIGH) and laserhead threshold per minefield with UI.
- Selective self-destruct UI.

## Out of scope
- Fighter combat behavior (PROJ-FMS-C). Note: ramming for fighters/ships is in PROJ-FMS-B because it's a warhead-detonation behavior; fighter-as-combatant is PROJ-FMS-C.
- Satellites (PROJ-FMS-D).

## Key risks
- **Statistical correctness of the trigger formula**: the math must satisfy both invariants (`P_trigger < 1` for any N, `P_trigger > 0` for `N ≥ 1`). Easy to mis-implement edge cases (e.g., precision loss at large N). Test with both small and large N.
- **Per-tick vs per-pass scaling**: tactical per-tick chance must integrate over the time a ship spends near a mine to roughly equal the strategic per-pass chance. Without careful scaling, tactical mines either feel too lethal (one entry = guaranteed multi-trigger) or trivial (one tick = nothing). Document the scaling explicitly in `decisions.md`.
- **Sector scatter determinism across saves**: PRNG seeding must use stable inputs (`group_id` or stable composite of `owner_id` + `hex` + `launch_turn`); not Python's default `random` module unless seeded explicitly.
- **Ramming damage stacking**: multiple warheads on a single rammer must apply correctly. Existing damage pipeline behavior under repeated applications needs verification.
- **Conflict with point-defense fire**: mines with `signature_bonus` should be hard to shoot down but not impossible. Tuning may need iteration after first playthroughs.

## Decisions deferred to implementation (PROJ-FMS-B)
- Exact warhead/laserhead damage tier values (placeholder values from PROJ-FMS-A; final balance pass here).
- `warhead_proximity_radius` for tactical mines.
- Detonation order across multiple ships in the same entry.
- Whether mid-battle-laid mines persist to `mine_group` or are battle-local.
- Per-tick scaling factor mapping strategic per-pass chance to tactical per-tick chance.
