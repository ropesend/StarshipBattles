# PROJ-473 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/strategy/generation/star_generator.py` | Production | Thread `rng: random.Random`; replace 26 bare `random.*` draws with `rng.*` (primary work) |
| `game/strategy/generation/placement_strategies.py` | Production | Remove `rng is None: rng = random.Random()` global fallback on the generation path; require explicit rng |
| `game/strategy/data/planet_gen.py` | Production | Thread `rng`; replace bare `random.*` |
| `game/strategy/data/planet_gen_surface.py` | Production | Thread `rng`; replace bare `random.*` |
| `game/strategy/data/planet_physics.py` | Production | Thread `rng`; replace bare `random.*` |
| `game/strategy/data/planet_atmosphere.py` | Production | Thread `rng`; replace bare `random.*` |
| `game/strategy/data/naming.py` | Production | Thread `rng`; replace bare `random.*` |
| `game/strategy/data/galaxy_warp_generator.py` | Production | Thread `rng`; replace bare `random.*` |
| `game/strategy/engine/game_initializer.py` | Production | Inject seeded `rng` into all generation; delete global `random.seed(galaxy_seed)` (~line 250, ST-04-010) — LAST |
| `game/ui/screens/galaxy_test/galaxy_mode.py` | Production | Inject seeded `rng`; delete global `random.seed(self.galaxy_seed)` (~line 239, ST-04-011) — LAST |
| `tests/unit/quality/test_no_unseeded_random.py` | Test | Tighten / re-scope the strategy-generation Pattern #18 exclusion once draws are seeded-instance only |
| `tests/unit/strategy/generation/` (reproducibility characterization) | Test | New: fixed-seed galaxy generation is reproducible before AND after; global RNG no longer perturbed by generation |
