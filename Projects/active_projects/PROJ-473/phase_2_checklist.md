# Phase 2: Warp generation (incl. the `generate_warp_lanes` facade rng gap)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-473 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** Phase 1 (per-system star/planet pipeline seeded on the dedicated
`physics_rng`; Task 0.1 narrow GREEN guard green, full-snapshot xfail down to S10 warp
type/intrinsic fields only)
**Goal mapping:** All tasks serve **G2** (warp generation draws from the seeded rng).
**Objective:** Thread the **existing `physics_rng`** (the same instance Phase 1 threaded
through stars/planets) through `GalaxyWarpGenerator.generate_warp_lanes` internals and close
the `Galaxy.generate_warp_lanes` facade gap (hazard H4).

> **WARP-STREAM CONTRACT — read before touching anything (Codex sign-off Blocker 1).** Warp
> randomness splits into TWO slices with DIFFERENT contracts:
> - **S9 — warp GEOMETRY** (`_calculate_warp_distance` jitter `:47`, `_should_add_density_edge`
>   acceptance `:273`) is **ALREADY SEEDED today**. It draws from the same module-level
>   `random` that S4/S5 physics use, continuing that stream right after the last
>   planet-physics draw (warps are a second pass after `generate_systems`; nothing else
>   touches the module RNG in between — storms/intrinsics use child streams off the
>   placement rng at `galaxy_system_generator.py:163-166`). Two same-seed runs already
>   produce identical warp geometry (`warp_geometry_equal=True`, runtime-verified). To
>   preserve it byte-for-byte you MUST **continue the dedicated `physics_rng`** into warp
>   geometry — the SAME instance Phase 1 used, in the same draw order. **Do NOT build a
>   fresh `warp_rng = random.Random(galaxy_seed)`** — that resets the sequence to its start
>   and changes generated warp geometry (still deterministic, but a regression vs current
>   output). S9 is guarded by the golden baseline (decisions.md), so a geometry shift fails
>   the test.
> - **S10 — warp TYPE + warp intrinsic rolls** (`_apply_warp_point_intrinsic_abilities`,
>   `:351-352`, `:394-420`) are **UNSEEDED today** (fresh `Random()` fallback `:408-409`).
>   Making them deterministic is the intended fix; their values WILL change from
>   per-run-random to fixed, which is **allowed, not a regression**. They run at the tail of
>   `generate_warp_lanes` immediately after the S9 draws, so feed them the **same continued
>   `physics_rng`** to keep one coherent draw order.
>
> Net: warps add **no new stream**. They continue `physics_rng`. Warps run as a clean second
> pass *after* `generate_systems` at both entry points (`game_initializer.py:271`,
> `galaxy_mode.py:287`), so the continued stream is well-ordered and this phase is
> self-contained.

---

## Tasks

### Task 2.1: Thread `rng` through warp generation internals [Medium]
**File:** `game/strategy/data/galaxy_warp_generator.py`
**Symbol/area:** `_calculate_warp_distance` warp-distance jitter (`:47`),
`_should_add_density_edge` acceptance draw (`:273`); these flow from `create_warp_link`
(`:106-107`) and `_add_density_edges` (`:297-304`) up to `generate_warp_lanes` (`:314`,
which already has an `rng` param). The intrinsics roll `_apply_warp_point_intrinsic_abilities`
(`:352`, `:394-420`) already takes rng but defaults to unseeded (`:408-409`).
**Test that must fail first:** add a test that `generate_warp_lanes(galaxy, rng=Random(seed))`
produces identical warp geometry (warp-point `location` per `destination_id`) + warp_types +
intrinsics across two runs (fails until the distance/density-edge draws are threaded —
currently they use bare `random`).
**Run:** `pytest tests/ -k warp`; then `pytest tests/ --testmon`.

- [ ] Thread the `rng` already on `generate_warp_lanes` (`:319`) down into
      `_apply_mst_edges` → `create_warp_link` → `_calculate_warp_distance`, and into
      `_add_density_edges` → `_should_add_density_edge`. Replace bare `random.uniform`
      (`:47`) and `random.random()` (`:273`) with `rng.*`. **The rng passed in by the
      composition root (Task 2.2) is the `physics_rng`, continued — NOT a fresh warp rng.**
- [ ] Preserve draw order: density edges draw `random.random()` only after the structural
      pre-check chain (`:214-273`); MST runs before density edges (`:346` then `:349`). Do
      not reorder (hazard H5). This same-order continuation of `physics_rng` is what keeps
      S9 warp geometry byte-for-byte identical to current output (golden-baseline guarded).
- [ ] Confirm `_apply_warp_point_intrinsic_abilities` (S10) receives the SAME continued
      `physics_rng` (already wired through at `:351-352`) and remove reliance on its unseeded
      `random.Random()` fallback on this path (`:408-409`). S10 values change from per-run-
      random to fixed — that is allowed (asserted for determinism + presence only, NOT
      against the golden baseline).
- [ ] Verify: S9 warp geometry matches the golden baseline (decisions.md) byte-for-byte;
      S10 type/intrinsics are stable across two same-seed runs; the Task 0.1 narrow GREEN
      guard stays green.

### Task 2.2: Close the `Galaxy.generate_warp_lanes` facade rng gap [Medium]
**Files:** `game/strategy/data/galaxy.py`, `game/strategy/engine/game_initializer.py`,
`game/ui/screens/galaxy_test/galaxy_mode.py`
**Symbol/area:** the facade `Galaxy.generate_warp_lanes` (`galaxy.py:256-266`) takes NO
`rng` and passes none to `self._warp_gen.generate_warp_lanes(...)`. Both production callers
invoke it with no rng (`game_initializer.py:271`, `galaxy_mode.py:287`).
**Test that must fail first:** add a test (or extend Task 0.1) asserting that a full
`initialize()` run with a fixed seed produces identical warp_types/intrinsics across two
runs — fails today because the facade drops rng so warp-type rolls are unseeded (hazard H4).
**Run:** `pytest tests/ -k "warp or game_initializer"`; then `pytest tests/ --testmon`.

- [ ] Add an `rng: random.Random | None` parameter to `Galaxy.generate_warp_lanes`
      (`galaxy.py:256-266`) and forward it into `self._warp_gen.generate_warp_lanes(...,
      rng=rng)`.
- [ ] Update `game_initializer._initialize_galaxy` (`:271`) and `galaxy_mode.generate`
      (`:287`) to pass the **existing `physics_rng` (CONTINUED) into the facade — do NOT
      build a new warp rng.** **STREAM-IDENTITY CONTRACT (design.md H7 S9/S10 — Codex
      sign-off Blocker 1):**
      - **S9 warp geometry is ALREADY SEEDED today** and continues the module stream right
        after the last planet-physics draw (warps are a second pass after `generate_systems`;
        nothing else consumes the module RNG in between — storms/intrinsics use child streams
        off the placement rng). So there IS an existing byte-for-byte sequence to preserve.
        Building a fresh `warp_rng = random.Random(galaxy_seed)` would reset the sequence and
        **change generated warp geometry** (a regression vs current output, even though still
        deterministic). The composition root must therefore pass the **same `physics_rng`
        instance** Phase 1 threaded through stars/planets — continuing it, in the same draw
        order — so warp geometry matches the golden baseline byte-for-byte.
      - **S10 warp type/intrinsics are UNSEEDED today**, so making them deterministic changes
        their values (allowed). They continue the same `physics_rng` at the tail of
        `generate_warp_lanes`.
      Document this `physics_rng`-continuation contract in a code comment and in decisions.md.
- [ ] Verify: S9 warp geometry equals the golden baseline (decisions.md) byte-for-byte;
      S10 warp-type/intrinsic values are stable across two same-seed runs (determinism +
      presence only, NOT golden-baseline equality); the Task 0.1 narrow GREEN guard stays
      green; with S10 now deterministic, the only remaining xfail-tolerated fields are gone —
      **drop the `xfail` marker** so the full-snapshot test asserts: (a) golden-baseline
      equality for already-seeded outputs incl. S9 geometry, and (b) two-run determinism for
      the newly-deterministic S10 fields, from here on.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` green; Task 0.1 narrow GREEN guard still green; the full-
      save-visible equivalence test now passes strictly (xfail marker REMOVED): (a)
      already-seeded outputs incl. S9 warp geometry equal the golden baseline byte-for-byte;
      (b) newly-deterministic S10 warp type/intrinsics are stable across two same-seed runs
- [ ] No bare `random.*` remains reachable from the seeded warp path (S9 + S10 both continue
      `physics_rng`; no fresh `warp_rng` was introduced)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
