# FEAT-27: Allow new-game galaxy size as low as 1 system

## Description

FEAT-24 lowered the galaxy slider minimum from 25 → 5 systems. The user
now wants the slider to go all the way down to **1 system**, with the
following semantics:

- **Default:** start at **2 systems** so a new game is the simplest
  possible interaction case — 1 empire / 1 system on each side, separated
  by a single warp lane.
- **Slider range:** 1 – 150 systems.
- **systems = 1:** no warp points are generated; **all empires start in
  the same system on different planets** (or on the same planet's
  different colonies if the system has only one planet).
- **systems ≥ 2:** existing invariant continues to apply — every empire
  starts in a *different* star system.

The user explicitly flagged that systems=1 is the harder case
because the assumption "every empire owns a unique starting system" is
implicit in the placement code today.

## Code investigation findings

Generator entry: `GameInitializer.initialize()` →
[`game/strategy/engine/game_initializer.py:35`](../../../game/strategy/engine/game_initializer.py#L35)
delegates to `Galaxy.generate_systems()` →
[`game/strategy/data/galaxy.py:524`](../../../game/strategy/data/galaxy.py#L524) →
`GalaxySystemGenerator.generate_systems()` at
[`game/strategy/data/galaxy_system_generator.py:103`](../../../game/strategy/data/galaxy_system_generator.py#L103).

**Warp generation already early-returns at <2 systems:**
[`game/strategy/data/galaxy_warp_generator.py:356`](../../../game/strategy/data/galaxy_warp_generator.py#L356)
has `if len(systems) < 2: return`. systems=1 silently produces 0 warp
points; systems=2 generates exactly one MST link.

**Empire placement currently fails to enforce uniqueness at low N:**
[`game/strategy/engine/game_initializer.py:194`](../../../game/strategy/engine/game_initializer.py#L194)
`_setup_initial_scenario()`:
- 1 empire → `home_indices = [0]`
- 2 empires → `home_indices = [0, num_systems - 1]` (first and last)
- 3 empires → `home_indices = [0, mid, num_systems - 1]`
- 4+ empires → `step = max(1, num_systems // num_empires)`

With **systems=1, empires=2**, `home_indices = [0, 0]` — both empires
land in system 0, silently. The code does not crash, but it also does
not honour the "different systems" invariant the user expects when N≥2.
With **systems=2, empires=4**, `step = max(1, 0) = 1` and the loop
distributes `[0, 1, 2, 3]` modulo bounds — bug-prone.

**Slider state (post-FEAT-24):**
[`game/ui/screens/new_game_setup_screen.py:150`](../../../game/ui/screens/new_game_setup_screen.py#L150)
`self.system_count = 5`; line 154 `value_range=(5, 150)`; line 582
default `system_count: int = 5`. No `MIN_SYSTEMS` constant exists.
`GameConfig` does not validate `system_count` in `__post_init__`.

**No integration tests exercise generation at systems ≤ 5.** FEAT-24
added UI-level tests only.

## Required changes

### Slider and default
- `new_game_setup_screen.py:150` `system_count = 5` → `2`
- `new_game_setup_screen.py:154` `value_range=(5, 150)` → `(1, 150)`
- `new_game_setup_screen.py:582` default `system_count: int = 5` → `2`
- `new_game_setup_screen.py:592` docstring `"default: 5"` → `"default: 2"`

### Validation
- Add `GameConfig.__post_init__` validator: `1 ≤ system_count ≤ 150` and
  `num_empires ≥ 1`.
- Document the systems=1 contract in the `GameConfig` docstring.

### Empire placement
Rework `GameInitializer._setup_initial_scenario()` empire-to-system
assignment:
- **N=1, E≥1:** every empire goes to system 0; allocate distinct
  *planets* within that system. If the system has fewer planets than
  empires, fall back to distinct *colonies on the same planet* with a
  warning, OR refuse the configuration in `GameConfig` validation
  (decide during implementation).
- **N≥2:** enforce **distinct systems per empire**. If E > N (more
  empires than systems), raise a clear `GameConfig` validation error.
  Replace the current uneven `step = max(1, N//E)` with an exact
  even-spread index list (e.g. `np.linspace(0, N-1, E, dtype=int)` or
  hand-rolled equivalent) so 4 empires in 2 systems is a hard error,
  not a silent collision.

### Warp generation
Already correct at systems=1 (early return). Add a regression test that
asserts `len(galaxy.warp_points) == 0` when systems=1.

### Tests (TDD-first per CLAUDE.md Rule 1)
- `tests/unit/strategy/data/test_galaxy_system_generator.py` — assert
  generation succeeds at N=1 and N=2.
- `tests/unit/strategy/data/test_galaxy_warp_generator.py` — assert 0
  warp points when N=1, exactly 1 link when N=2.
- `tests/unit/strategy/engine/test_game_initializer.py` — assert
  N=1/E=2 places both empires in the same system on different planets;
  N=2/E=2 places them in different systems; N=2/E=4 raises a validation
  error.
- `tests/unit/ui/test_new_game_setup.py` — assert default is 2 and
  slider min is 1.

## Acceptance

- New Game Setup screen opens with the slider at **2** and can drag
  down to 1 and up to 150.
- Starting a game with systems=1 and 2 empires produces a single-system
  galaxy with 0 warp lanes; both empires colonised in the same system
  on different planets.
- Starting a game with systems=2 and 2 empires produces two systems
  joined by exactly one warp lane; each empire in a different system.
- Misconfigurations (more empires than available systems when N≥2)
  raise a clear validation error rather than silently collapsing.

## Out of scope

- AI / behaviour tuning for tiny galaxies.
- Performance optimisation of empire-vs-empire interaction in shared
  systems.
- Tutorial / UX explanation of the "shared starting system" mode.

## Priority

Medium — the user has explicitly flagged this as harder than FEAT-24
because of the implicit "one system per empire" invariant that needs
to be made explicit and enforced.

## Status

Awaiting Confirmation

## Work Log

- 2026-04-28: Created from QA Session 20260428_190154 [19:03:57 –
  19:05:05]. Code investigation completed during triage.
- 2026-04-29: Marked Blocked during deep-dive-parallel session.
  Investigator agent (`investigator-feat-27`) made substantial
  progress (8 files modified in worktree
  `.claude/worktrees/feat-feat-27`) but stalled mid-implementation
  with no commit. Worktree HEAD was `2064952cb` — pre-merge baseline.
  Four tickets had merged into main since the agent started (BUG-126,
  BUG-123, FEAT-26, FEAT-20).
- 2026-04-29: Resumed under deep-dive-resume team. Worktree rebased
  cleanly onto main `9885acd0d` (BUG-125 head); the auto-merge of
  `tests/integration/strategy/test_command_handlers.py` preserved
  BUG-125's `Command.empire_id` removal alongside FEAT-27's 19
  `system_count=0 → 1` sentinel updates. Confirmed the partial work
  matched the user-clarified continuous quadratic slider design
  (NOT the outdated piecewise step from the investigation report
  §7), so retained it in full.

  **Implementation:**
  - `game/strategy/engine/game_config.py` — added
    `DEFAULT_SYSTEM_COUNT = 2`, `MIN_SYSTEM_COUNT = 1`,
    `MAX_SYSTEM_COUNT = 150` module-level constants as the single
    source of truth. Bumped dataclass field default from `25` → 2.
    `__post_init__` validates `1 ≤ system_count ≤ 150` and rejects
    `len(players) > system_count` at N≥2; N=1 explicitly bypasses
    (intentional shared-system mode). `from_dict` default also
    uses the constant. Class docstring documents the contract.
  - `game/strategy/engine/game_initializer.py` — `initialize()`
    drives a planet-shortage retry loop (up to 10 attempts,
    perturbing `galaxy_seed` via `dataclasses.replace`); clears
    `empire.colonies` between attempts; raises
    `ValidationException` on exhaustion. Extracted
    `_empire_home_indices(num_empires, num_systems)` returning a
    hand-rolled linspace `[round(i * (N-1) / (E-1)) for i in
    range(E)]` that spreads empires evenly (vs. the old stair-step
    that clustered at the low end). At N=1 every empire shares
    `systems[0]` and gets a *different* planet via a per-system
    `next_planet_in_system` counter — fixes the silent
    `Planet.owner_id` overwrite from the original code.
  - `game/ui/screens/new_game_setup_screen.py` — imports
    `DEFAULT_SYSTEM_COUNT`. New module-level
    `system_count_slider_curve(t)` and
    `system_count_slider_inverse(value)` implement a quadratic
    curve over an internal `[0, 1000]` slider range, mapping to
    `[1, 150]` system_count. Fine-grained at the low end (each
    pixel near `t=0` is a 1-system change), coarser at the high
    end (top 10% of slider travel covers ~28× as many systems
    as the bottom 10%). `build_game_config` signature default
    sourced from `DEFAULT_SYSTEM_COUNT`.

  **Tests added/modified (TDD-first):**
  - `tests/unit/strategy/engine/test_game_config.py` — NEW: dataclass
    default, bounds (0/151/-1/10000 rejected; 1/2/150 accepted),
    `len(players) > system_count` rejection at N≥2, N=1 multi-empire
    accepted (shared-system mode).
  - `tests/unit/strategy/engine/test_game_initializer.py` — extended:
    N=1/E=1, N=1/E=2 shares system on distinct planets with correct
    `owner_id`, N=1/E=2 zero warp points, N=2/E=2 distinct systems,
    N=2/E=2 one warp link, N=5/E=4 distinct + evenly-spread, planet-
    shortage retries-then-raises, planet-shortage retries-then-
    succeeds-on-attempt-2.
  - `tests/unit/strategy/data/test_galaxy_warp_generator.py` — NEW:
    N=0 zero warps, N=1 zero warps, N=2 one link.
  - `tests/unit/ui/test_new_game_setup.py` — extended:
    `build_game_config` default is 2; signature default sourced from
    `DEFAULT_SYSTEM_COUNT`; 9 tests covering the slider curve
    (boundary clamping, monotonicity, fine-low/coarse-high contract,
    landing coverage, default-2 reachability). Updated 2 existing
    tests with explicit `system_count=4` for 4-player cases.
  - `tests/integration/strategy/test_command_handlers.py` — 19
    `system_count=0 → 1` sentinel updates (auto-merged cleanly
    with BUG-125 fixture changes during rebase).

  **Collateral test fixes (discovered during full sharded run):**
  - `tests/unit/strategy/test_game_config.py` — pinned
    `system_count=3` for the 3-player test.
  - `tests/unit/strategy/save_game_service/test_save_load_ops.py` —
    pinned `system_count=3` for the two 3-empire tests.
  - `tests/integration/strategy/test_fleet_command_authorization.py`
    — pinned `system_count=2` (was `0`, pre-FEAT-27 sentinel) on
    the `_two_empire_session` fixture; galaxy is replaced with a
    mock so the value only needs to satisfy validation.

  **Documentation:**
  - `docs/systems/strategy_layer.md` — added §6 "Galaxy Size
    Contract (FEAT-27)" subsection documenting both modes (N=1
    shared-system, N≥2 separated), the `DEFAULT_SYSTEM_COUNT`
    single-source-of-truth contract, the linspace placement, and
    the quadratic slider curve. Bumped `> **Last verified:**`.

  **Tests:** Full pytest run on Python 3.13.13 with -n 12:
  **16167 passed, 3 skipped** in 71s. (Sharded runner reports 0
  tests via JUnit XML aggregation due to a pre-existing tooling
  issue on Windows where shard subprocesses don't write
  `--junitxml`; the inline pytest invocation produces the
  authoritative count and shows no failures.)
