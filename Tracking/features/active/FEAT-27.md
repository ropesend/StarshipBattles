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

Pending

## Work Log

- 2026-04-28: Created from QA Session 20260428_190154 [19:03:57 –
  19:05:05]. Code investigation completed during triage.
