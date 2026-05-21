# PROJ-473: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Origin

Deferred from PROJ-471 (state-hygiene). PROJ-471 findings ST-04-010 and ST-04-011 flagged
the two global `random.seed()` calls as Pattern #18 violations, but the orchestrator and a
dual independent + Codex review re-verified against live code that they are **load-bearing**
and cannot be removed in isolation. This project does the prerequisite rng-threading so the
seed calls can then be removed safely.

## Initial Analysis (verified against live code 2026-05-20)

- `game/strategy/engine/game_initializer.py:246-250` constructs a per-instance
  `rng = random.Random(galaxy_seed)` AND calls `random.seed(galaxy_seed)` with the comment
  "Also seed global random for star/planet generation". The instance `rng` is passed to the
  placement strategy; the global seed is what makes the bare-`random` generation
  reproducible.
- `game/strategy/generation/star_generator.py` uses **bare `random.*`** (26 draws:
  `random.lognormvariate`, `random.uniform`, etc.) with no `rng` parameter. This is the
  primary consumer of the global seed.
- `game/strategy/generation/placement_strategies.py` accepts an `rng` parameter but falls
  back to `rng = random.Random()` (unseeded) when `rng is None` (lines ~90-91, ~163). On the
  production path `game_initializer` passes the seeded rng, but the fallback is a latent
  determinism hole and must not silently consume global state.
- Planet/atmosphere/naming/warp generation (`game/strategy/data/planet_gen.py`,
  `planet_gen_surface.py`, `planet_physics.py`, `planet_atmosphere.py`, `naming.py`,
  `galaxy_warp_generator.py`) also use bare `random.*`.
- `game/ui/screens/galaxy_test/galaxy_mode.py:~239` calls `random.seed(self.galaxy_seed)`
  alongside a per-instance RNG at ~line 261, feeding the same bare-`random` generation path.

## Why the global seed cannot just be deleted

Deleting `random.seed(galaxy_seed)` while `star_generator.py` (and the planet generators)
still call bare `random.*` makes galaxy generation depend on whatever undefined global RNG
state exists at call time → **non-reproducible galaxies for a fixed seed**. The Pattern #18
guard test currently *excludes* strategy generation precisely because this debt exists; the
exclusion is a marker of the debt, not an endorsement.

## Design Approach

1. Add an explicit `rng: random.Random` parameter to `StarGenerator` (constructor or
   per-generate-call) and to every planet/atmosphere/naming/warp generation entry point.
   Replace every bare `random.X(...)` with `rng.X(...)`.
2. Thread the seeded `rng` that `game_initializer` already builds into all generation calls.
   Remove the placement-strategy `rng is None` global fallback on the generation path
   (require an explicit rng, or construct a seeded one at the single composition site).
3. Once no generation code reads global `random` state, delete the two
   `random.seed(...)` calls (ST-04-010, ST-04-011).
4. Tighten / re-scope the Pattern #18 guard exclusion for strategy generation.

## Key Patterns to Reuse
- **Pattern #18 (Per-Battle / Per-Instance RNG)**: combat already threads a seeded
  `random.Random` (see `BattleEngine.rng` → `DamageCalculator(rng=...)`, and PROJ-471's
  `CombatSubsystems` bundle). Mirror that explicit-injection shape for generation.
- **Single composition site for the seed**: `GameInitializer.initialize` /
  `_generate_galaxy` is the one place that knows `galaxy_seed`; build the `random.Random`
  there and inject downward, exactly as it already does for placement strategies.

## Dependencies & Risks
1. **Determinism regression (highest risk)** — mitigation: a before/after reproducibility
   characterization test on a fixed seed must be GREEN both before threading (proving the
   baseline) and after (proving equivalence). Because moving from `random.X` to `rng.X`
   draws the *same* sequence when the rng is seeded identically, outcomes should match
   byte-for-byte; if they do not, the threading order is wrong.
2. **Draw-order sensitivity** — replacing bare draws must preserve the exact call order so
   the seeded sequence is identical. Do not reorder generation calls.
3. **`galaxy_mode.py` is a dev/test tool** — lower stakes, but must still be threaded so the
   global seed can be removed without breaking the tool's own reproducibility.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
