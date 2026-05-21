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

> **IMPORTANT:** "thread the rng" below does NOT mean "consolidate everything onto one
> root stream." The live code has multiple independent seeded streams plus several
> unseeded fallbacks (see **H7 — RNG stream topology**). The migration must REPRODUCE the
> existing stream topology, not flatten it. In particular star/planet *physics* must get
> their OWN `random.Random(galaxy_seed)` instance (NOT the placement rng, which has
> already had two `randint` draws pulled for the storm/intrinsic child streams).

1. Add an explicit `rng: random.Random` parameter to `StarGenerator` (constructor or
   per-generate-call) and to every planet/atmosphere/naming/warp generation entry point.
   Replace every bare `random.X(...)` with `rng.X(...)`, preserving exact call order (H5).
2. Wire the streams per H7's "stream-instance plan": a dedicated `physics_rng =
   random.Random(galaxy_seed)` (separate instance, same seed) for star+planet physics +
   image registries, kept distinct from the placement rng S1 and its derived storm/
   intrinsic child streams S2/S3; **the SAME `physics_rng` is then continued into warp
   geometry (S9) and the warp type/intrinsic rolls (S10)** — warps are a second pass after
   `generate_systems` and S9 already continues the module stream today, so byte-for-byte
   preservation requires continuing `physics_rng`, NOT a fresh `warp_rng` (Codex sign-off
   Blocker 1); a seeded name shuffle for S8. Remove the unseeded `random.Random()`
   fallbacks (S6/S7/S10) on the generation path.
3. Once no generation code reads global `random` state, delete the two
   `random.seed(...)` calls (ST-04-010, ST-04-011).
4. ADD `game/strategy/generation` + `game/strategy/data` to the Pattern #18 guard (there
   is no pre-existing strategy exclusion to "tighten" — see H6).

## Key Patterns to Reuse
- **Pattern #18 (Per-Battle / Per-Instance RNG)**: combat already threads a seeded
  `random.Random` (see `BattleEngine.rng` → `DamageCalculator(rng=...)`, and PROJ-471's
  `CombatSubsystems` bundle). Mirror that explicit-injection shape for generation.
- **Single composition site for the seeds**: `GameInitializer._initialize_galaxy` (and
  `galaxy_mode.generate`) is the one place that knows `galaxy_seed`; build the seeded
  `random.Random` instances there and inject downward, exactly as it already does for the
  placement strategy. **Note (H7):** this is *multiple* instances seeded with the same
  `galaxy_seed` (placement rng + dedicated `physics_rng`), kept distinct to reproduce the
  current independent-stream topology — NOT one consolidated root rng. Warp geometry (S9)
  and warp type/intrinsics (S10) do NOT get a separate warp rng — they **continue the
  `physics_rng`** (warps are a second pass after `generate_systems`, and S9 already
  continues the module stream today; see H7).

## Dependencies & Risks
1. **Determinism regression (highest risk)** — mitigation: a two-part reproducibility
   test on a fixed seed. (a) **Class-(a) already-seeded** fields (placement, star/planet
   physics, **warp GEOMETRY S9**, storms, intrinsic abilities, archetype — H7
   S1/S2/S3/S4/S5/**S9**) are compared against a **GOLDEN BASELINE** captured from the
   CURRENT pre-change code (Phase 0 Task 0.0) — they must equal it byte-for-byte on the
   unchanged baseline and after every phase; any regression there means a draw-order error.
   A two-run same-impl check is NOT sufficient for class (a) — only the golden comparison
   catches a deterministic-but-sequence-shifting rewrite (Codex sign-off Blocker 2). (b) The
   full-save-visible end-to-end determinism test is **NOT** green on baseline — the
   **class-(b)** fields names (S8), images (S6/S7), and warp **type**/intrinsics (**S10
   only**) are unseeded today and differ across two same-seed runs, so this is an
   **expected-RED** characterization that turns green progressively as names (P0), images
   (P1), and warp type/intrinsics (P2) move onto seeded streams. (Warp geometry S9 is NOT in
   this set — it is already seeded and golden-guarded.) Because moving `random.X` → `rng.X`
   draws the *same* sequence when the rng is seeded identically (and a dedicated
   `physics_rng = random.Random(galaxy_seed)` reproduces what the global
   `random.seed(galaxy_seed)` produced), the class-(a) fields must match the golden baseline
   byte-for-byte; if they do not, the threading order is wrong.
2. **Draw-order sensitivity** — replacing bare draws must preserve the exact call order so
   the seeded sequence is identical. Do not reorder generation calls.
3. **`galaxy_mode.py` is a dev/test tool** — lower stakes, but must still be threaded so the
   global seed can be removed without breaking the tool's own reproducibility.

## Architecture Hazards (from the code-grounded consult, re-verified 2026-05-21)

Source: `AgentCoordination/Scratchpad/Consult/proj473_preflesh3/advice.md`. Line numbers
below were re-checked against live code; where they drifted, the live number is given.

### H1 — Name shuffle fires BEFORE the seed exists (Phase 0 must move first)
`GameInitializer.initialize` constructs `Galaxy(radius=...)` at `game_initializer.py:84`,
inside the retry loop, *before* `_initialize_galaxy` builds the generation RNG at
`game_initializer.py:248`. `Galaxy.__init__` immediately constructs `NameRegistry`
(`galaxy.py:44`), whose `load_data` calls `random.shuffle(self.available_names)` at
`naming.py:42`. **Therefore system-name order is drawn from the unseeded global stream
today** — full save-visible reproducibility is impossible until names are brought into the
seeded stream. Fix shape (consult §2): constructor-inject the rng into `NameRegistry`, or
defer the shuffle to a seeded step. Note `NameRegistry` is constructed once per `Galaxy`,
so the rng must be available at `Galaxy` construction OR the shuffle must be deferred to a
post-seed call. This is *why* Phase 0 reorders the composition root.

### H2 — `system_count == 1` retry seed-bump sensitivity (highest behavioral risk)
At N=1 with multiple empires, `initialize` regenerates the lone system up to 10 times
(`_PLANET_SHORTAGE_RETRY_ATTEMPTS`, `game_initializer.py:33`), and on each retry perturbs
the seed: `replace(config, galaxy_seed=config.galaxy_seed + attempt)`
(`game_initializer.py:86-91`). The retry fires when `len(lone.planets) < num_empires`
(`game_initializer.py:331-337`). **Any draw-order change in planet generation can flip
whether attempt 0 succeeds or falls through to attempt 1, which generates a completely
different galaxy.** The reproducibility characterization test must therefore exercise an
N=1-multi-empire configuration (or assert at the post-`initialize` boundary, not just the
raw `generate_systems` boundary) so a draw-count shift that changes retry outcome is
caught, not masked.

### H3 — Image fields are save-visible and registry-RNG is dropped on the per-system path
`Star.image_id`, `Planet.image_id`, `Planet.image_rotation` are persisted generation
outputs. The registries already accept a seeded `rng` (`star_image_registry.py:70`,
`planet_image_registry.py:65,98`), **but the generators never forward one**:
`StarGenerator._get_image_id` calls `get_random_image(star_type)` with no rng
(`star_generator.py:51-58`), and `PlanetGenerator._create_single_planet` calls
`get_random_image(p_type)` / `get_random_rotation()` with no rng
(`planet_gen.py:397-398`). So image selection draws from global state today. The
reproducibility snapshot must **include** `image_id`/`image_rotation` (do NOT inherit the
golden-save skiplist at `_build_galaxy_fixture.py:53-59`, which normalizes them to
placeholders for a different purpose).

### H4 — The `Galaxy.generate_warp_lanes` facade drops `rng` (Phase 2 gap)
`GalaxyWarpGenerator.generate_warp_lanes` has an `rng` parameter
(`galaxy_warp_generator.py:314-320`) and forwards it to
`_apply_warp_point_intrinsic_abilities` (`:352`), which defaults to an unseeded
`Random()` when `rng is None` (`:408-409`). **But the `Galaxy` facade method takes no
`rng` and passes none** (`galaxy.py:256-266`), and both production callers invoke the
facade with no rng (`game_initializer.py:271`, `galaxy_mode.py:287`). So warp-**type** and
warp-**intrinsic** rolls (S10) are unseeded today even though the plumbing exists one layer
down. Separately, `_calculate_warp_distance` (`:47`) and `_should_add_density_edge` (`:273`)
use bare module-level `random.*` for warp-distance jitter and density-edge acceptance (S9
geometry) — but note (corrected per H7 + Codex sign-off Blocker 1) these S9 draws are
**already seeded today**: they continue the same module stream the global
`random.seed(galaxy_seed)` set, so warp geometry is reproducible now. Threading them to
`rng.*` must therefore CONTINUE the dedicated `physics_rng` (preserving the existing
sequence byte-for-byte), NOT introduce a fresh warp rng. Only the S10 type/intrinsic rolls
are newly-deterministic. A partial migration that fixes stars/planets but not this facade
leaves warps "half old, half new."

### H5 — Draw-order fragility sites (do NOT reorder; preserve exact call sequence)
Moving `random.X` → `rng.X` is sequence-preserving *only if the call order is unchanged*.
The branch-dependent draw counts make reordering catastrophic:
- **Per-system loop** interleaves naming → stars → planets → storms → archetype in one
  pass (`galaxy_system_generator.py:171-209`). Note it already derives separate seeded
  `storm_rng` / `intrinsic_rng` sub-streams from the main rng (`:158-169`); stars+planet
  *physics* still draw from global. Threading must respect that the placement rng, the
  intrinsic_rng, and the storm_rng are *distinct streams*.
- **Star type branches** consume different draw counts per branch (blue giant, red dwarf,
  neutron star, black hole, Stefan-Boltzmann) — `star_generator.py:108-145`,
  `_compute_stefan_boltzmann_type` `:147-193`. `_generate_spectrum` adds 9 jitter draws
  (`:267-280`); `_generate_companions` adds conditional ring jitter + collision retries
  (`:301-321`).
- **Orbital slots** loop with a hot-jupiter branch + per-attempt retries
  (`planet_gen.py:153-178`); `_generate_moons` is a `while random.random() < chance` loop
  so moon-draw count is data-dependent (`:266-277`).
- **Atmosphere** gas-composition draw count depends on retained gases + mass
  (`planet_atmosphere.py:91`, `:119-146`).
- **Surface** has conditional chthonian stripping then two draws per resource id
  (`planet_gen_surface.py:101-102`, `:199-218`).
- **Density edges** consume `random.random()` only after a long structural pre-check chain
  (`galaxy_warp_generator.py:214-273`), so any topology change shifts every later draw.

### H7 — RNG stream topology (THE load-bearing contract — read before any threading)

**The live code does NOT use one root rng.** It runs several *independent* seeded
streams plus several *unseeded* fallbacks. Full save-visible equivalence requires the
migration to **reproduce these same independent streams**, NOT consolidate them into a
single root stream and NOT derive a later stream from an already-consumed earlier one.
Re-verified against live code 2026-05-21:

| # | Consumer | Today's source | Draw order / notes |
|---|----------|----------------|--------------------|
| S1 | **System placement** (`sample_location`) | per-instance `rng = random.Random(galaxy_seed)` built at `game_initializer.py:248`, passed to `generate_systems(..., rng=rng)` (`:269`) and consumed in the placement loop at `galaxy_system_generator.py:173-178` | This stream ALSO yields the two seeds for the child streams below, drawn *once up front* at `galaxy_system_generator.py:163-164` BEFORE the placement loop. |
| S2 | **Storm generation** | `storm_rng = random.Random(storm_seed)` where `storm_seed = rng.randint(0, 2**32-1)` (`galaxy_system_generator.py:163,165`) | Derived from S1's *first* `randint` draw. Already fully threaded; storms reproducible today. |
| S3 | **Intrinsic-ability + archetype rolls** | `intrinsic_rng = random.Random(intrinsic_seed)` where `intrinsic_seed = rng.randint(...)` (`galaxy_system_generator.py:164,166`) | Derived from S1's *second* `randint` draw. Passed as `rng=intrinsic_rng` to `generate_planets` (`:197`) and `_apply_system_archetype` (`:206`). Reproducible today. |
| S4 | **Star physics** (`StarGenerator`, 26 bare draws) | the **module-level `random`** object, which `game_initializer.py:250` separately seeds via `random.seed(galaxy_seed)` | `generate_system_stars(name)` is called with NO rng (`galaxy_system_generator.py:193`). Draws come from global module state. |
| S5 | **Planet physics** (mass/orbits/moons/atmosphere/surface, bare draws in `planet_gen.py`, `planet_physics.py`, `planet_atmosphere.py`, `planet_gen_surface.py`) | the **module-level `random`** (same `random.seed(galaxy_seed)`) | The `rng=intrinsic_rng` passed to `generate_planets` is used ONLY for intrinsic-ability rolls (S3), NOT for physics. Physics draws from global. |
| S6 | **Star image_id** | `StarImageRegistry.get_random_image(star_type)` with NO rng → fresh **unseeded** `random.Random()` (`star_image_registry.py:81-82`) | Different every run; NOT reproducible today. |
| S7 | **Planet image_id / image_rotation** | `PlanetImageRegistry.get_random_image()` / `get_random_rotation()` with NO rng → fresh **unseeded** `random.Random()` (`planet_image_registry.py:76-77`, `:107-108`) | Different every run; NOT reproducible today. |
| S8 | **Name shuffle** | module-level `random.shuffle` at load time (`naming.py:42`), fired in `Galaxy.__init__` (`galaxy.py:44`) BEFORE any seeding | At `initialize()` time the galaxy is built at `game_initializer.py:84` before `random.seed` at `:250`, so the name order is drawn from whatever global state pre-exists — different every run (H1). |
| S9 | **Warp GEOMETRY: warp-distance jitter / density-edge acceptance** | bare module-level `random.uniform` (`galaxy_warp_generator.py:47`) and `random.random()` (`:273`) | These are the **same module-level `random` instance** that S4/S5 physics drew from, seeded once by `random.seed(galaxy_seed)` (`game_initializer.py:250`). `Galaxy.generate_warp_lanes()` runs as a second pass *after* `generate_systems` (`game_initializer.py:271`) and its `rng` param arrives as `None` (`galaxy.py:256-266`), so warp geometry **continues the same module stream right after the last planet-physics draw**. Nothing consumes the module RNG between the last planet physics draw and the first warp-geometry draw — storms (S2) and intrinsics/archetype (S3) use the *child* streams derived from the placement rng (`galaxy_system_generator.py:163-166`), not the module RNG. **Therefore S9 IS reproducible across two same-seed runs today** (verified by read-only runtime probe: `warp_geometry_equal=True`). It must be PRESERVED byte-for-byte. |
| S10 | **Warp TYPE / warp intrinsic rolls** | `_apply_warp_point_intrinsic_abilities(rng=None)` → fresh **unseeded** `random.Random()` (`galaxy_warp_generator.py:408-409`) | Different every run; NOT reproducible today (H4). This is the ONLY genuinely-unseeded slice of warp randomness. |

**Why the module-level `random.seed` reproduction is exact (the key migration fact):**
CPython's module-level `random.*` functions are bound methods of a single hidden
`random.Random` instance. So `random.seed(s)` followed by draws in a fixed order yields
the *identical* sequence as `random.Random(s)` with the same draws in the same order.
Therefore S4+S5 can be migrated to a dedicated `physics_rng = random.Random(galaxy_seed)`
**only if** (a) it is seeded with the *same* `galaxy_seed`, (b) it is a **separate
instance** from the placement rng S1 (do NOT derive it from S1, which has already had two
`randint` draws pulled for S2/S3), and (c) the star→planet draw order is preserved
exactly (H5). Because today S4 and S5 share one global stream (stars are drawn first per
system at `:193`, then planet physics at `:197`), the migration must keep S4 and S5 on
**one shared `physics_rng`** in that same star-then-planet order — splitting them into two
instances would change the sequence each sees and break equivalence.

**Stream-instance plan after migration (preserves byte-for-byte output):**
- S1 placement rng: unchanged — `random.Random(galaxy_seed)`, still yields S2/S3 seeds.
- S2 storm_rng / S3 intrinsic_rng: unchanged — derived from S1 exactly as today.
- S4+S5 physics: NEW dedicated `physics_rng = random.Random(galaxy_seed)`, a *separate*
  instance seeded with the same `galaxy_seed`, threaded star-then-planet in current order.
  This reproduces the sequence the global `random.seed(galaxy_seed)` produced.
- S6/S7 images: forward `physics_rng` at the exact point the registry call fires today
  (inside the per-star / per-planet build). **DRAW-ORDER HAZARD (flagged during sign-off,
  verify in Phase 1):** images do NOT draw from the module stream today — `get_random_image`
  uses a *fresh unseeded* `Random()` when `rng is None` (`star_image_registry.py:81-82`,
  `planet_image_registry.py:76-77`/`:107-108`), so the baseline module sequence is
  star-physics → planet-physics → … → warp-geometry (S9) with NO image draws in it.
  Forwarding `physics_rng` into the registries INSERTS image draws into that stream,
  shifting every later draw — including S9 warp geometry — off its golden-baseline position.
  Two mitigations are possible; Phase 1 must pick one and confirm S9 stays golden:
  (i) draw images from a SEPARATE seeded image stream (e.g. a child `image_rng` derived
  once from `physics_rng` up front, like storms/intrinsics derive from the placement rng) so
  the physics stream's draw positions are untouched and S9 geometry is preserved; or
  (ii) keep images on `physics_rng` but accept that S9's stream POSITION moves — only
  workable if S9 is also re-anchored so its golden values still match (harder; not
  recommended). Option (i) is the safe default: it keeps S6/S7 newly-deterministic (class b)
  WITHOUT perturbing the class-(a) physics + S9 sequence. The Phase 0 golden baseline + the
  class-(a) guard will CATCH a regression here, but the design intent is option (i).
- S8 names: seed the shuffle from a stream available at `Galaxy.__init__` time. Because
  the shuffle currently fires before `galaxy_seed` exists, names are NOT reproducible on
  the baseline — bringing them into the seeded stream is a Phase 0 *behavior change to a
  previously-nondeterministic field*, not a preservation. (See the Phase 0 RED test note.)
- **S9 warp GEOMETRY (distance jitter + density-edge acceptance): MUST CONTINUE the
  dedicated `physics_rng` — NOT a fresh `warp_rng`.** This is the load-bearing correction
  (Codex sign-off Blocker 1). Today S9 draws from the SAME module-level `random` instance
  as S4/S5 physics, continuing that stream right after the last planet-physics draw (warps
  are a second pass after `generate_systems`; nothing else touches the module RNG in
  between — storms/intrinsics use child streams off the placement rng). Because the
  dedicated `physics_rng = random.Random(galaxy_seed)` reproduces exactly what the global
  `random.seed(galaxy_seed)` produced (CPython module-`random` == a single `Random`
  instance), warp geometry stays byte-for-byte ONLY if it continues that **same
  `physics_rng` instance** in the **same draw order** (star→planet physics for all systems,
  then warp geometry: MST `create_warp_link` distance draws, then density-edge acceptance
  draws). Threading S9 onto a fresh `warp_rng = random.Random(galaxy_seed)` would reset the
  sequence to its start and **change generated warp geometry** — a regression, even though
  it would still be deterministic. So Phase 2 forwards the existing `physics_rng` (the one
  Phase 1 threaded through stars/planets) into the warp facade; it does NOT build a new
  warp rng for geometry.
- **S10 warp TYPE + warp intrinsic rolls: newly-deterministic (values WILL change).** These
  are the only unseeded warp draws today (fresh `Random()` fallback at `:408-409`). Making
  them deterministic is the intended fix; their values change from per-run-random to fixed,
  which is **allowed, not a regression** (like S6/S7/S8). They draw from the **continued
  `physics_rng` stream** as well — `_apply_warp_point_intrinsic_abilities` runs at the tail
  of `generate_warp_lanes` (`:351-352`) immediately after the S9 geometry draws, so feeding
  it the same `physics_rng` keeps a single coherent draw order with no extra stream. (They
  could in principle take any stable stream, but reusing `physics_rng` avoids introducing a
  new instance and keeps the order well-defined.)

**Consequence for the Phase 0 reproducibility test:** S4, S5, S2, S3 **and S9** are seeded
today, so their fields (star/planet *physics*, storms, intrinsic abilities, archetype, and
**warp geometry** — warp-point `location` per `destination_id`) are already reproducible
across two same-seed `initialize()` runs. (S9 was previously mis-listed here as unseeded;
verified `warp_geometry_equal=True` by runtime probe — Codex sign-off Blocker 1.) But S6,
S7, S8, S10 are unseeded today, so `image_id`, `image_rotation`, system `name` order,
`warp_type`, and warp `intrinsic_abilities` **differ across two same-seed runs on the
unchanged baseline**. The full-save-visible equality test therefore CANNOT be green on
baseline — it is an expected-RED end-to-end characterization for the **S6/S7/S8/S10** fields
that turns green once Phases 0–2 bring names (P0), images (P1), and warp type/intrinsics
(P2) onto seeded streams. The already-seeded fields — including warp geometry (S9) — are
NOT part of the expected-RED set; they are guarded from the start (golden baseline, below
and in plan.md / decisions.md). (See H1/H3/H4.)

### H6 — Pattern #18 guard does not currently cover `game/strategy`
`tests/unit/quality/test_no_unseeded_random.py:37` guards only
`("game/simulation", "game/engine", "game/ai")`. There is **no** strategy exclusion to
"tighten" — Phase 3 ADDS the strategy generation dirs to the guard. See decisions.md.

## Threading shape summary (per consult §2; stream identity per H7)
- `placement_strategies.py`, `planet_*` free functions, `star_image_registry`,
  `planet_image_registry`, `galaxy_warp_generator`: **per-call `rng` parameter**.
- `StarGenerator.generate_system_stars`, `PlanetGenerator.generate_system_bodies`:
  **per-call `rng`** — and that rng is the dedicated **`physics_rng`** (H7 S4+S5), one
  shared instance threaded star-then-planet, NOT the placement rng and NOT the
  intrinsic_rng. Image registries (H7 S6/S7) receive a **separate seeded image stream**
  (a child `image_rng` derived once from `physics_rng`), NOT `physics_rng` directly — see the
  H7 S6/S7 draw-order hazard: images are unseeded today and absent from the physics stream,
  so feeding them `physics_rng` would shift S9 warp geometry off its golden baseline.
- `NameRegistry`: **constructor-injected rng** (or deferred seeded shuffle) — the random
  op is at load time, not at `get_system_name()`. Brings S8 into a seeded stream.
- `galaxy_warp_generator` (H7 S9 geometry + S10 type/intrinsics): the **`physics_rng`**
  (the same instance Phase 1 threaded through stars/planets) is threaded through the
  `Galaxy.generate_warp_lanes` facade gap (H4) from the composition root. **No separate
  warp rng** — S9 already continues the module stream today, so byte-for-byte preservation
  requires continuing `physics_rng`. S10 (type/intrinsics) continues the same stream at the
  tail of `generate_warp_lanes`.
- `game_initializer.py`, `galaxy_mode.py`: **local seeded roots**. Each builds the
  placement rng `random.Random(galaxy_seed)` (already present) PLUS the dedicated
  `physics_rng = random.Random(galaxy_seed)` — two instances, not one root. The same
  `physics_rng` is forwarded into `generate_warp_lanes` for S9/S10. They are seeded with
  the same `galaxy_seed` but kept as separate streams to reproduce the current
  independent-stream behavior.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
