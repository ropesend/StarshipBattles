# PROJ-379: Design — Deterministic Golden-Save Fixture

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source

**OpenCode review of PROJ-377 (req_20260507_044410_7cfefd, 2026-05-07):**
> **MIN-002:** Double-seed Galaxy init pattern in capture script is fragile.
> The re-seed after `Galaxy.__init__` assumes that re-seeding the global `random` module will also control any `random.Random()` instances created during construction. If `Galaxy.__init__` (or any code it calls) creates an internal `random.Random()` instance, the re-seed has no effect on it. This is latent fragility.

PROJ-377 verifier confirmed the finding; the fix was deferred on the grounds that the docstring at `_capture_baseline.py:9-23` documents the trade-off and CI's contract is round-trip identity, not byte-equality. PROJ-379 closes that gap.

---

## Initial Analysis

### Non-determinism map (from Phase A exploration)

| Category | Site | Severity | Why unfixed today |
|---|---|---|---|
| **Star generation** | `game/strategy/generation/star_generator.py` (~20 module-level `random.*` calls in `_generate_mass:69`, `_determine_type_and_radius:109-131`, `_compute_stefan_boltzmann_type:168-183`, `_roll_star_type:200`, `_generate_spectrum:268`, `_generate_companions:309-355`, plus age/type rolls at 393/418/440/471) | CRITICAL | `StarGenerator` has no `rng` param at any level; `Galaxy.generate_systems(rng=...)` threads `rng` to placement strategies but stops at `_star_gen.generate_system_stars(name)` |
| **Planet generation** | `game/strategy/data/planet_gen.py` (~20 module-level `random.*` calls in `_generate_orbital_slots:119-170`, body shapes, atmosphere `planet_atmosphere.py:125,138`, density `planet_physics.py:60-64`, moon generation `:325`) | CRITICAL | `PlanetGenerator.generate_system_bodies(name, stars)` has no `rng` param; called from `GalaxySystemGenerator.generate_planets` which DOES have `rng` (used only for intrinsic-ability rolls, not body shapes) |
| **NameRegistry shuffle** | `game/strategy/data/naming.py:42` (`random.shuffle(self.available_names)` during `Galaxy.__init__`) | HIGH | Consumes module-level RNG entropy *before* the capture script's second `random.seed()` call; that's why the script seeds twice |
| **Image registries** | `PlanetImageRegistry.get_random_image(rng=None)` and `get_random_rotation(rng=None)` (lines 65, 98) and `StarImageRegistry.get_random_image(rng=None)` (line 70) all default to a fresh unseeded `random.Random()` when no rng passed | HIGH | Already accept `rng` — callers (`star_generator.py:58`, `planet_gen.py:395-396`) just don't thread it |
| **Warp generation** | `GalaxyWarpGenerator._calculate_warp_distance:46` (`random.uniform`), `_should_add_density_edge:272` (`random.random`), `_apply_warp_point_intrinsic_abilities:410` (defaults to unseeded Random) | MEDIUM | `Galaxy.generate_warp_lanes()` doesn't accept an `rng` param at the public Galaxy facade; the warp generator's `generate_warp_lanes(..., rng=None)` does — small plumbing gap |
| **PYTHONHASHSEED dict iteration** | `to_dict()` iterates `self._state.systems.items()` (galaxy.py:281) | LOW | `json.dumps(..., sort_keys=True)` recursively normalizes nested dict order; in-memory dict insertion order is the only fragile path |

**Key finding:** The current `_capture_baseline.py` already normalizes the cosmetic image fields (`image_id`, `image_rotation`) to deterministic placeholders, but cannot fix the body-shape rolls (mass, density, temperature, etc.), star image_ids, warp_type rolls, or warp-point intrinsic abilities without invasive production-code changes.

### Existing rng-threading convention (mature)

The codebase has a clear pattern (PROJ-301/302/303/304 — intrinsic-ability rolls):

1. Public function signature: `def generator(..., rng: Optional[random.Random] = None) -> ...`
2. Default behavior: `if rng is None: rng = random.Random()` (fresh unseeded — back-compat)
3. Spawn child rngs: `child_seed = rng.randint(0, 2**32 - 1); child_rng = random.Random(child_seed)`
4. Working precedent at `game/strategy/data/galaxy_system_generator.py:158-169`
5. Helper `_resolve_rng()` in `game/strategy/systems/race_randomizer.py:37-39`

PROJ-379 does NOT extend this pattern (Option B sidesteps generation entirely). It is the model for any future Option A project.

### Existing utilities the fixture builder will reuse

| Utility | Location | Role in PROJ-379 |
|---|---|---|
| `make_galaxy_stub()` | `tests/fixtures/galaxy_fixtures.py:42-48` (PROJ-378) | Construct minimal `Galaxy` via `Galaxy.__new__()` + `_state`/`_registry`/`_spatial` wiring. Starting point for fixture builder. |
| `create_test_planet`, `create_test_star`, `create_test_warp_point`, `create_test_system` | `tests/fixtures/strategy_entities.py` | Factory functions accepting `**overrides`. Reused for hand-built specs. |
| `_build_minimal_planet` | `tests/integration/strategy/test_save_round_trip.py:23-31` | Direct `Planet(**fields)` constructor pattern. Pattern model. |
| `_strip_storms` (kept conceptually) | `tests/fixtures/saves/_capture_baseline.py:36-39` | Will not be needed in the new builder — the hand-built path doesn't generate storms. |
| `Galaxy._registry.add_system()` / `register_planet()` | `game/strategy/data/galaxy_entity_registry.py` | Production registration paths. Fixtures route through these so `from_dict` reads exactly what `to_dict` writes. |

---

## Alternatives considered

### A. Full rng threading (deterministic by construction at the generation layer)

Thread `rng` through `StarGenerator`, `PlanetGenerator`, `PlanetImageRegistry` callers, `StarImageRegistry` callers, `NameRegistry`, and `GalaxyWarpGenerator._calculate_warp_distance` / `_should_add_density_edge`. Convert ~40 module-level `random.*` calls to `rng.X()` calls.

**Pro:** generators become seed-deterministic; the fixture stays generated; useful for any future "replay galaxy from seed" feature.
**Pro:** extends the existing PROJ-301/302/303/304 pattern.
**Con:** big production-code change spanning `game/strategy/generation/` + `game/strategy/data/`. ~3-5 phases. Touches `tests/integration/strategy/test_galaxy_gen.py` and other generator-shaped tests.
**Con:** PROJ-379's actual concern (golden-save fixture determinism) doesn't *need* generation determinism — it needs *fixture* determinism. Option A solves a bigger problem than is in scope.

**Rejected** — out of proportion to the problem; logged as a future opportunity in [decisions.md](decisions.md).

### B. Hand-built synthetic fixtures — **CHOSEN**

Replace the generation-then-normalize capture with hand-built `Galaxy` objects: walk a list of typed dataclass specs and instantiate `StarSystem` / `Planet` / `WarpPoint` directly with explicit field values, register them via the production `Galaxy._registry.add_system()` / `register_planet()` paths.

**Pro:** 100% deterministic by construction. Zero production-code changes.
**Pro:** The round-trip test's purpose has always been *serialization* drift detection, not generation-shape coverage. Generation has its own seed-deterministic check at `tests/integration/strategy/test_galaxy_gen.py::test_generate_with_rng_is_deterministic` (note: this test currently checks system coordinates only, per Codex peer review — it does not prove deterministic stars/planets/images/warp-intrinsic-abilities. That is fine for PROJ-379's purpose: PROJ-379 only needs *fixture* determinism, not *generation* determinism. A future generator-replay project would extend `test_galaxy_gen.py` to broader coverage; out of PROJ-379 scope).
**Pro:** Aligns with the existing `_build_minimal_planet` and `tests/fixtures/strategy_entities.py::create_test_*` factory pattern.
**Pro:** Fixture coverage becomes intentional — author commits to "this fixture exercises every Planet field with a non-default value" as a checkable invariant.
**Con:** Loses generation-pipeline coverage from the fixture (mitigated — generation has its own tests).
**Con:** A new `Planet` field must be deliberately added to the fixture — the Phase 1 field-coverage guard (using the serialized-baseline pattern: `planet_to_dict(_minimal_planet())` is the source of truth for both emitted keys and per-key defaults) catches this case at CI time.

**Accepted** — locked via AskUserQuestion 2026-05-07. This is the body of PROJ-379.

### C. Expanded normalization (extend `_normalize_image_fields` to also normalize warp_type, intrinsic_abilities, star image_ids, mass/temperature/etc.)

**Pro:** zero production-code changes; minimal LOC delta.
**Con:** strips ~80% of the realistic content from the fixture — at that point the fixture is mostly placeholders, defeating its purpose as a structural-drift detector.
**Con:** same footgun as today, just at more sites.

**Rejected** — converts a real fixture into a cosmetic placeholder.

### D. Static check-in only (no capture script — hand-author the JSON directly)

**Pro:** truly deterministic; trivial.
**Con:** fragile under schema changes (every `Planet` field add requires hand-editing two JSON files).
**Con:** loses the "build by Python factory, dump to JSON" round-trip-as-construction pattern.

**Rejected** — too brittle; Option B preserves the round-trip-as-construction without the determinism cost.

---

## Risks

- **R1: Hand-built fixtures drift from production reality.** A field added to `Planet` but not to the fixture means the fixture stops exercising it. *Mitigation:* the Phase 1 field-coverage guard at `tests/integration/strategy/test_golden_fixture_field_coverage.py` calls `planet_to_dict(_minimal_planet())` (the serializer is the single source of truth for emitted keys and per-key defaults). A new `Planet` field added to `planet_to_dict` without being populated in the fixture produces a clear test failure with the field name.
- **R2: Hand-built fixture loses generation-shape coverage.** A planet with hand-picked `mass = 5.97e24` doesn't exercise `_generate_mass`'s `random.lognormvariate`. *Mitigation:* this is intentional — `tests/integration/strategy/test_galaxy_gen.py` covers the generation path. The golden fixture is for serialization drift only.
- **R3: Constructor-side validation rejects a hand-built field combination.** `Planet.__init__` validates `surface_gravity > 0` etc. *Mitigation:* fixture builder uses defensible values; trivially fixable if surfaced.
- **R4: Field-coverage guard goes stale if `planet_to_dict` is later refactored from a single dict literal into programmatic construction.** *Mitigation:* the guard does NOT walk AST — it calls `planet_to_dict()` directly and uses its return value as the single source of truth. Resilient to any refactor that preserves return shape.
- **R5: PROJ-377 cross-link drift at closeout.** The PROJ-379 closeout updates PROJ-377 `decisions.md` to mark MIN-002 resolved. *Mitigation:* Phase 4 explicitly includes this cross-link as a checklist item; OpenCode review will catch the drift if it's missed.
- **R6: PYTHONHASHSEED dict order leaks.** Even with hand-built fixtures, if the builder uses `set` iteration anywhere (e.g., to build a list of warp points), insertion order varies across processes. *Mitigation:* builder uses explicit lists and tuples — never iterates a `set` to populate a fixture field. Phase 2 enforces this with subprocess tests setting `PYTHONHASHSEED` to varied values; `json.dumps(sort_keys=True)` is a backstop on the final emit path.

---

## Open questions

All resolved during planning via AskUserQuestion 2026-05-07.

- **Q1: Approach.** Option B (hand-built synthetic). User confirmed.
- **Q2: Field-coverage guard.** Yes — Phase 1 includes the field-coverage test using the serialized-baseline pattern (`planet_to_dict(_minimal_planet())`). User confirmed; pattern revised after Codex peer review (2026-05-08) — see decisions.md.
- **Q3: Skip `image_id` / `image_rotation` from the field-coverage check?** Yes — these are intentionally normalized to deterministic placeholders. The skiplist is documented inline in the guard test.

---

## Reference: file inventory after PROJ-379 ships

| Path | State | Notes |
|---|---|---|
| `tests/fixtures/saves/_build_galaxy_fixture.py` | NEW | Replaces `_capture_baseline.py`. Hand-built fixture builder. |
| `tests/fixtures/saves/galaxy_proj372_baseline.json` | REGENERATED | Smaller — no generated star/planet shapes. |
| `tests/fixtures/saves/galaxy_proj372_populated.json` | REGENERATED | Hand-decorated planet exercises every Planet field. |
| `tests/integration/strategy/test_save_round_trip.py` | MODIFIED | +6 tests: Phase 1 adds 2 in-process byte-determinism + 2 committed-fixture-vs-builder-output staleness checks; Phase 2 adds 2 cross-process subprocess + `PYTHONHASHSEED` tests. |
| `tests/integration/strategy/test_golden_fixture_field_coverage.py` | NEW | Field-coverage guard using the serialized-baseline pattern (`planet_to_dict(_minimal_planet())` for both emitted-keys set and per-key defaults). |
| `tests/fixtures/saves/_capture_baseline.py` | DELETED | Phase 3. |
| `Projects/active_projects/PROJ-377/decisions.md` | MODIFIED | Phase 4 appends MIN-002 resolution row. |
| `game/**` | UNCHANGED | Zero production-code changes. |
