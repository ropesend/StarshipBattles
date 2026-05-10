# PROJ-378: Design — Galaxy Cleanup Test Pattern Update

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source

Carried over from PROJ-372 (Galaxy/Planet/Star God-Class Decomposition). The verifier report for PROJ-372 noted:

> "These tests were written before PROJ-372 and use the old pattern. The PROJ-372 agent didn't update them because they're not in the focused test paths it was working on."

15 setup-errors surface in `tests/unit/strategy/data/test_galaxy_cleanup.py` against the post-PROJ-372 facade. The errors are mechanical: `galaxy.radius = 100` (the test's first state-mutation line at `:64`, `:168`, `:250`) hits the new property setter at `galaxy.py:73-75` which calls `self._state.radius = value` — but `_state` was never assigned because `Galaxy.__new__()` skipped `__init__`.

---

## Initial Analysis

### Pattern catalogue (from grep over `tests/`)

There are exactly **3 test files** using `Galaxy.__new__(Galaxy)` post-PROJ-372:

| File | # call sites | Status today | Why |
|------|-------------:|---------------|-----|
| `tests/unit/strategy/data/test_galaxy_cleanup.py` | 3 (lines 63, 167, 249) | **15 errors** | Sets `galaxy.radius = 100` first; `radius.setter` calls `self._state.radius = value` and `_state` does not yet exist. |
| `tests/integration/strategy/test_empire.py` | 5 (lines 11, 19, 26, 37, 45) | **All passing** | Only sets `galaxy._next_fleet_id = 1`; `_next_fleet_id.setter` at `galaxy.py:139-141` calls `self._ensure_state()` which **lazy-creates** `GalaxyState` + `_registry` + `_spatial`. |
| `tests/integration/strategy/test_fleet_registration_lifecycle.py` | 1 (lines 75-80) | **Passing** | Already migrated post-PROJ-372: the fixture explicitly does `gal._state = GalaxyState(radius=300)` + manually wires `_registry`, `_spatial`. This is the model for the new shared fixture. |

The escape hatch is `Galaxy._ensure_state()` (`galaxy.py:96-105`) — it lazy-creates `_state`, `_registry`, `_spatial` when called from a property accessor whose getter invokes it. **But only `_next_planet_id` and `_next_fleet_id` getters/setters call `_ensure_state()`**. The `radius` setter (and 9 other dict-field forwarders) does not — it directly does `self._state.radius = value`. That's why `test_empire.py` works (it touches `_next_fleet_id` first) and `test_galaxy_cleanup.py` fails (it touches `radius` first).

### What each test class actually needs (from reading the file)

| Test class (file:line) | State the fixture sets | Methods exercised |
|---|---|---|
| `TestGalaxyUnregisterPlanet` (`:55`) | radius, systems, name_map, planets_by_id, planet_to_system, global_hex_planets, global_hex_zones, fleets_by_id, `_registry: GalaxyEntityRegistry(galaxy)` (NB: pre-PROJ-372 signature — needs updating to `GalaxyEntityRegistry(galaxy._state)`) | `galaxy.unregister_planet(planet)` |
| `TestGalaxyRemoveWarpLink` (`:160`) | radius, systems, name_map, planets_by_id, planet_to_system, global_hex_planets, fleets_by_id (NB: no `_registry` — but `remove_warp_link` was implemented inline pre-PROJ-372; today it's at `galaxy.py:209-232` and reads `self._state.name_map` + `self._state.global_hex_warp_points` directly) | `galaxy.remove_warp_link(a, b)` |
| `TestGalaxyGetAllFleetsInSystem` (`:242`) | radius, systems, name_map, planets_by_id, planet_to_system, global_hex_planets, fleets_by_id (NB: no `_registry` and no `_spatial` — but `get_all_fleets_in_system` today delegates to `self._spatial.get_all_fleets_in_system(system, empires)`) | `galaxy.get_all_fleets_in_system(system, empires)` |

The second and third fixtures are missing `_spatial` and `_registry`. They worked pre-PROJ-372 because `remove_warp_link` and `get_all_fleets_in_system` were inline methods on `Galaxy`. Post-PROJ-372 they delegate to services — so the migrated fixture **must** wire `_registry` and `_spatial` for any test calling delegated methods. (The shared `make_galaxy_stub()` will always wire both, side-stepping the question.)

### Construction-cost finding (informs fix-option choice)

Measured on this Windows 11 / Python 3.13 dev box:

| Operation | Time |
|---|---|
| Cold import of `game.strategy.data.galaxy` | 118 ms |
| `Galaxy(radius=100)` first call (after import) | 39 ms |
| `Galaxy(radius=100)` average over 10 calls | 33 ms |

`Galaxy.__init__` at `galaxy.py:42-65` loads JSON from disk (`Paths.STAR_SYSTEM_NAMES_FILE`, `Paths.STORMS_FILE`), instantiates `NameRegistry`, `StarImageRegistry`, `StarGenerator`, `PlanetImageRegistry`, `PlanetGenerator`, optional `StormGenerator`, and four service delegates. **Risk R5 in PROJ-372's design.md** documents this is intentionally heavy.

15 fixture invocations × 33 ms ≈ 0.5 s added to the test file. Not a deal-breaker for the test file in isolation, but the pattern matters: the legacy `__new__` was deliberately faster, and the cumulative cost across the broader suite (today there are 9 `Galaxy.__new__` + 1 fixture-style call sites) would multiply if the pattern proliferates. **The right move is a fast stub.**

---

## Alternatives considered

### A. Direct `_state` assignment (option (a) in the brief)
Each test fixture sets `galaxy._state = GalaxyState(radius=100, ...)` directly, replacing the chain of `galaxy.radius = ...; galaxy.systems = ...; ...` lines.

**Pro:** Minimal indirection. Each fixture is self-documenting about what state it cares about.
**Pro:** No new shared module; the existing fixtures stay scoped to their classes.
**Con:** Three near-duplicate boilerplate blocks across the same file (the 9 dicts + 2 counters + `_registry` + `_spatial`). High drift risk — if `GalaxyState` ever gains a field, three places must update.
**Con:** Doesn't help `test_empire.py` (5 sites) or `test_fleet_registration_lifecycle.py` (1 site). Net legacy-pattern call count drops from 9 to 6, then re-grows whenever a new test is added.
**Con:** Still requires the test author to reach into `_state` private-prefixed attribute — weak signal that this is the supported testing surface.

### B. Shared `make_galaxy_stub()` factory in `tests/fixtures/galaxy_fixtures.py` (option (b) in the brief) — **RECOMMENDED**
Add a single function to `tests/fixtures/galaxy_fixtures.py` (canonical implementation; mirrors the existing `tests.fixtures.*` convention), with an optional thin `tests/unit/strategy/data/conftest.py` `@pytest.fixture` wrapper that delegates:

```python
def make_galaxy_stub(radius: int = 100) -> Galaxy:
    """Construct a minimal Galaxy for unit tests, bypassing __init__'s heavy I/O.

    Wires GalaxyState + GalaxyEntityRegistry + GalaxySpatialIndex for tests
    exercising methods that delegate to those services. For tests that need
    real generators (NameRegistry, StarGenerator, PlanetGenerator), use
    `Galaxy(radius=...)` instead — it costs ~33 ms.
    """
    galaxy = Galaxy.__new__(Galaxy)
    galaxy._state = GalaxyState(radius=radius)
    galaxy._registry = GalaxyEntityRegistry(galaxy._state)
    galaxy._spatial = GalaxySpatialIndex(galaxy._state)
    return galaxy
```

**Pro:** One canonical place. New `GalaxyState` fields require updating exactly one factory. Reads as documentation of "what minimal galaxy means."
**Pro:** Migrates `test_empire.py` (5 sites), `test_fleet_registration_lifecycle.py` (1 site), and `test_galaxy_cleanup.py` (3 fixtures) to the same idiom — net 9 legacy call sites collapse to one factory plus 8 callers.
**Pro:** Tests are still allowed to layer additional state on top: `galaxy = make_galaxy_stub(); galaxy._state.systems[loc] = sys` reads cleanly.
**Pro:** Implementation lives at `tests/fixtures/galaxy_fixtures.py` per the established `tests.fixtures.*` convention (see `tests/fixtures/README.md`, `tests/fixtures/ai.py`, `tests/fixtures/battle.py`, `tests/fixtures/common.py`, plus 8+ existing imports). The function is importable from any test directory via `from tests.fixtures.galaxy_fixtures import make_galaxy_stub`.
**Pro:** A thin optional `tests/unit/strategy/data/conftest.py` can expose a `galaxy_stub` pytest fixture that delegates to `make_galaxy_stub()`, giving unit tests in this directory a one-line fixture-injection API.
**Con:** New module file (small — ~30 LOC). Trivial.
**Note (corrected r004):** `tests/unit/strategy/data/__init__.py` does not exist, so a co-located `tests/unit/strategy/data/conftest.py` is NOT importable cross-tree (`importlib.util.find_spec` returns `None`). The original co-located plan would not have worked for `tests/integration/strategy/test_empire.py` and `tests/integration/strategy/test_fleet_registration_lifecycle.py`, which live in a different tree. The canonical `tests.fixtures.*` location resolves this.

### C. Use real `Galaxy(radius=N)` (option (c) in the brief)
Replace each fixture with a real `Galaxy(radius=100)` and rely on its constructor.

**Pro:** Zero stub maintenance. No new fixture file.
**Pro:** Closer to production semantics; the test exercises real init paths.
**Con:** ~33 ms per fixture × 15 fixtures × N runs (parallel shards execute fixtures repeatedly) = ~0.5 s added to the suite per shard, and that scales linearly if more `Galaxy.__new__` use sites adopt this approach. Not catastrophic but cumulative.
**Con:** Brings disk I/O dependencies (NameRegistry, StarImageRegistry, etc.) into a unit test that doesn't exercise them. Risks unrelated test failures from data-file drift (the very thing PROJ-372's GalaxyState extraction was designed to prevent — see decisions.md row "GalaxyState dataclass" rationale).
**Con:** Three of the test cases in `TestGalaxyRemoveWarpLink` and `TestGalaxyGetAllFleetsInSystem` rely on **synthetic** state (mock empires, mock fleets, hand-built `StarSystem` objects). Constructing a real `Galaxy` and then nuking `galaxy._state.systems = {}` to clear is the worst of both worlds.

### Recommendation: **Option B — `make_galaxy_stub()` shared fixture.**

It is the only option that:
1. Fixes all 15 failing tests with one mechanical edit per fixture.
2. Doesn't pay the 33 ms-per-call cost of real construction.
3. Generalizes to the other two test files using the same pattern.
4. Documents the "minimal galaxy" testing pattern in code as a single canonical location.

---

## Risks

- **R1: Imports across `tests/unit/` and `tests/integration/`.** *Resolved (r004):* the canonical implementation lives at `tests/fixtures/galaxy_fixtures.py`, which is importable cross-tree per the established `tests.fixtures.*` convention (`tests/conftest.py:23`, `tests/fixtures/ai.py`, `tests/fixtures/battle.py`, `tests/fixtures/common.py`, plus 8+ existing imports). Both `tests/integration/strategy/test_empire.py` and `tests/integration/strategy/test_fleet_registration_lifecycle.py` import directly from there.
- **R2: New `GalaxyState` fields drift.** If a future project adds a 14th field to `GalaxyState`, the stub factory must update.
  **Mitigation:** A 1-line dataclass-introspection assertion in the conftest can guard this — `assert len(dataclasses.fields(GalaxyState)) == 12` — but it's overkill for a fixture. Skip; rely on test failures if a field becomes mandatory and isn't passed.
- **R3: `_ensure_state()` might be removed if "no remaining `__new__` callers" sweep at Phase 2 close finds zero.** The shared fixture explicitly sets `_state` directly, bypassing `_ensure_state()`. After PROJ-378 closes, no test in the suite goes through `_ensure_state()` — so it becomes dead code.
  **Mitigation:** Phase 2 documents this observation but does NOT delete `_ensure_state()` from production. That's a separate cleanup project, with a stronger claim once PROJ-378 has shipped and stuck.
- **R4: Hidden delegate creation order.** The PROJ-372 `__init__` orders generators-then-services. The stub factory creates only `_state`, `_registry`, `_spatial` — not generators. If a test inadvertently calls `galaxy.generate_systems(...)` or `galaxy.generate_planets(...)`, it'll fail with `AttributeError: 'Galaxy' object has no attribute '_sys_gen'`.
  **Mitigation:** The stub's docstring spells out which methods are safe to call. None of the 15 failing tests calls a generator. If a future test needs a generator, use `Galaxy(radius=...)` instead — that's the right tool.
- **R5: `pygame_gui` / pygame dependencies in import chains.** `Galaxy.__init__` imports `StarImageRegistry` and `PlanetImageRegistry` which load images. The stub bypasses both. If conftest is imported in a no-pygame environment, the legitimate `Galaxy(radius=...)` constructor would fail — but that's a pre-existing condition, not a PROJ-378 concern.
  **Mitigation:** None needed.

---

## Open questions

1. **Q1: Where does the shared fixture live — `tests/unit/strategy/data/conftest.py` or `tests/fixtures/galaxy_fixtures.py`?** *Resolved (r004 joint review):* `tests/fixtures/galaxy_fixtures.py` is the canonical implementation module, mirroring the established `tests.fixtures.*` convention. A thin optional `tests/unit/strategy/data/conftest.py` may expose a `galaxy_stub` pytest fixture that delegates to it. The originally-leaning co-located plan was unreachable from integration tests because `tests/unit/strategy/data/__init__.py` does not exist (cross-tree `from tests.unit.strategy.data.conftest import …` returns `find_spec → None`).

2. **Q2: Should `make_galaxy_stub()` accept `**state_kwargs` to pre-populate `GalaxyState` fields?**
   *Recommendation:* No. Keep the factory minimal. Tests layer state via `galaxy._state.systems[k] = v` after construction — the existing pattern in `test_fleet_registration_lifecycle.py` is exactly this. A `**kwargs`-rich factory invites bloat.

3. **Q3: Should Phase 2 also delete `Galaxy._ensure_state()` from production?**
   *Recommendation:* No, defer. PROJ-378 is a test-only project; touching production is out-of-scope (per the brief). After PROJ-378 ships, an audit can confirm no remaining `__new__` callers and a 5-minute follow-up project removes `_ensure_state()`. Logged as a future opportunity in `decisions.md`.

4. **Q4: Should we add an AST-guard test that fails if any future test introduces a new `Galaxy.__new__(Galaxy)` call site?**
   *Recommendation:* Optional, low priority. The fixture's existence + a docstring note in `make_galaxy_stub()` is the soft enforcement; an AST guard adds 30 LOC of test infrastructure for marginal benefit. **Skip unless the user explicitly wants it.**
