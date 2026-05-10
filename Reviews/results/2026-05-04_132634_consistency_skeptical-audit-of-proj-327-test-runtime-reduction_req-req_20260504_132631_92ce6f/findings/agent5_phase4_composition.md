# Agent 5: Phase 4 Compositional Construction — Skeptical Audit

**Auditor:** OpenCode (Agent 5)
**Date:** 2026-05-04
**Scope:** `game/ui/screens/strategy_screen_composition.py`, `tests/fixtures/strategy_screen_composition.py`, `StrategyScreen.__init__`, migrated tests

---

## Question 1: Protocol-to-Constructor Signature Match

**Verdict: PASS — all 8 factory calls match real constructor signatures.**

### Verified signatures

| Slot | Factory call | Real constructor | Match? |
|---|---|---|---|
| `make_renderer` | `StrategyRenderer(screen)` | `__init__(self, scene)` | **PASS** |
| `make_camera_navigator` | `CameraNavigator(screen)` | `__init__(self, scene)` | **PASS** |
| `make_fleet_ops` | `FleetOperations(screen, screen._facade)` | `__init__(self, scene, facade)` | **PASS** |
| `make_colonization` | `ColonizationSystem(screen, screen._facade)` | `__init__(self, scene, facade)` | **PASS** |
| `make_superweapons` | `SuperweaponOperations(screen, screen._facade)` | `__init__(self, scene, facade)` | **PASS** |
| `make_build_queue_manager` | `StrategyBuildQueueManager(screen)` | `__init__(self, screen: "StrategyScreen")` | **PASS** |
| `make_game_state_manager` | `StrategyGameStateManager(screen)` | `__init__(self, screen: "StrategyScreen")` | **PASS** |
| `make_input_handler` | `StrategyInputHandler(screen, input_mapper=screen.input_mapper)` | `__init__(self, scene, input_mapper=None)` | **PASS** |

### StrategyInputHandler detailed analysis
`game/ui/screens/strategy_input_handler.py:29`:

```python
def __init__(self, scene, input_mapper=None):
```

The factory at `strategy_screen_composition.py:111` calls:
```python
StrategyInputHandler(screen, input_mapper=screen.input_mapper)
```

- `input_mapper` is a regular parameter in the real constructor with a `None` default.
- The factory passes it as `input_mapper=screen.input_mapper` (keyword argument matching the parameter name).
- In production, `screen.input_mapper` is set at `strategy_screen.py:84` from the constructor parameter `input_mapper` (which defaults to `None`). If `input_mapper` is `None`, the call is equivalent to `StrategyInputHandler(screen, input_mapper=None)` — identical to the real constructor's default behavior.
- **No mismatch.** This is correct.

---

## Question 2: MockComposition Correctness — Same-MagicMock Risk

**Verdict: MINOR CONCERN — inherent to MagicMock but not specific to this PR.**

### Implementation analysis

`tests/fixtures/strategy_screen_composition.py:65-76` — the `MockStrategyScreenComposition.__init__` creates **8 distinct** `MagicMock` instances:

```python
self.renderer = MagicMock(name="renderer")          # distinct
self.camera_nav = MagicMock(name="camera_nav")      # distinct
self.fleet_ops = MagicMock(name="fleet_ops")        # distinct
self.colonization = MagicMock(name="colonization")  # distinct
self.superweapons = MagicMock(name="superweapons")  # distinct
self.build_queue = MagicMock(name="build_queue")    # distinct
self.game_state = MagicMock(name="game_state")      # distinct
self.input_handler = MagicMock(name="input_handler") # distinct
```

The checkmark's claim ("same mock on repeated `make_*` calls") is about idempotence per slot — calling `make_renderer()` twice returns the same `self.renderer` mock. This matches production behavior (sub-objects constructed once per `__init__`). The comment does **not** claim there's a single mock shared across all 8 slots.

### Risk assessment

The question's premise — "MockComposition returns the *same MagicMock* for EVERY sub-object" — is **incorrect**. They are 8 different instances. A test that accidentally references `mock_comp.fleet_ops` when it meant `mock_comp.renderer` WILL get a different object.

However, a subtler risk DOES exist: **every MagicMock accepts every attribute access and method call without error**. If a test does `mocks['renderer'].some_fleet_method()` (wrong mock), the MagicMock silently creates another mock, the test passes, and the SUT's actual call to `mocks['fleet_ops'].some_fleet_method()` goes unverified. This is not specific to the Composition refactor — it's inherent to MagicMock-based testing and existed in the pre-PROJ-327 code (where the helper did `screen._renderer = MagicMock()` directly).

**No new risk introduced.** The fixture's `_SLOTS` tuple mapping (`test/fixtures/strategy_screen_composition.py:54-63`) also provides a single canonical mapping that could be used for verification in future test audits.

---

## Question 3: Migration Fidelity — Did `patch.object` Patterns Get Removed?

**Verdict: PASS — all `patch.object(StrategyScreen, '__init__', ...)` patterns removed. Improvement is genuine but shallow.**

### Evidence

**`tests/unit/ui/screens/test_strategy_screen.py`:**
- Grep for `patch.*object.*__init__|patch\.object.*StrategyScreen` → **0 matches**.
- Helper `_make_strategy_screen` (line 28-103) uses `StrategyScreen.__new__(StrategyScreen)` (line 37) — no `patch.object`.
- Sub-objects wired via `MockStrategyScreenComposition().populate(screen)` (lines 81-82) instead of 8 inline `screen._X = MagicMock()` lines.

**`tests/unit/ui/screens/test_strategy_menu_actions.py`:**
- Grep for `patch.*object.*__init__|patch\.object.*StrategyScreen` → **0 matches**.
- Helper `_make_strategy_screen` (line 15-40) uses `StrategyScreen.__new__(StrategyScreen)` (line 26) — no `patch.object`.
- One surviving `patch.object(Game, '__init__', ...)` at line 271 — unrelated (targets `game.app.Game`, not `StrategyScreen`).

### Assessment of improvement depth

The migration did TWO things:

1. **Removed `patch.object(StrategyScreen, '__init__', ...)` monkey-patches** — a real improvement. This pattern was fragile (it no-ops the entire method globally, affecting any concurrent test that imports the module).

2. **Centralized 8 inline MagicMock lines into `MockStrategyScreenComposition().populate(screen)`** — a DRY improvement. Before, the helper had 8 lines of `screen._renderer = MagicMock()`, `screen._camera_nav = MagicMock()`, etc. Now it's 2 lines (`comp = MockStrategyScreenComposition(); comp.populate(screen)`).

**What did NOT change:**
- Tests still use `StrategyScreen.__new__(StrategyScreen)` to bypass `__init__` entirely.
- No test exercises the `composition=` parameter on the real `StrategyScreen(...)` constructor.
- The heavy upstream construction (Camera, StrategyUI, asset loading) is still bypassed.

The `MockStrategyScreenComposition` fixture docstring acknowledges this limitation explicitly (`tests/fixtures/strategy_screen_composition.py:16-21`):

> "Pass the composition through a real `StrategyScreen(...)` call — substitutes only the 8 sub-objects, lets the rest of `__init__` run. (Currently impractical because `StrategyScreen.__init__` also runs heavy upstream construction…)"

So the seam exists but is not exercised by any test. The net improvement is: one fewer monkey-patching pattern + centralized sub-object wiring. A real "compositional construction" test would look like `StrategyScreen(1920, 1080, composition=mock_comp)` — but no test does this.

---

## Question 4: Does `populate()` Silently Miss `__init__` Setup?

**Verdict: PASS — no setup is silently missing.**

### Analysis of `StrategyScreen.__init__` (lines 81-155)

The `_make_strategy_screen` helper manually replicates every attribute `__init__` sets:

| `__init__` block | Lines | Helper replication | Lines |
|---|---|---|---|
| Basic attributes (width, height, callback, input_mapper) | 81-84 | `screen.screen_width = 1920`, etc. | 40-43 |
| Session | 87-92 | `screen.session = MagicMock(...)` | 46-53 |
| Facade | 95 | `screen._facade = MagicMock()` | 57 |
| Camera | 98-108 | `screen.camera = MagicMock()` | 60-61 |
| StrategyUI | 111 | `screen.ui = MagicMock()` | 64-66 |
| State attributes | 114-137 | `screen.hover_hex = None`, etc. | 69-78 |
| `_race_loader` + `_load_assets()` | 140-142 | `screen._race_loader = MagicMock()` + `empire_assets = {}` | 85-86 |
| Sub-objects | 147-155 | `MockStrategyScreenComposition().populate(screen)` | 81-82 |

**After line 155, `__init__` ends.** There are zero method calls on constructed sub-objects within `__init__`.

### `_load_assets()` bypass

Helper sets `screen.empire_assets = {}` (empty) instead of calling `_load_assets()`. This is correct for unit tests — `_load_assets()` (`strategy_screen.py:662-670`) calls `get_asset_manager().load_manifest()` + `RaceAssetLoader.load_all_empire_assets()`, both requiring actual asset files on disk. Tests that need `empire_assets` populate it manually or mock `_get_object_asset` directly (observed at `test_strategy_screen.py:154, 166, 179, 191`).

**Resolution: No tests are silently missing setup that `__init__` used to provide.** The helper fully replicates the attribute surface that tests read.

### `populate()` vs `make_*` symmetry

One subtle observation: `populate()` directly assigns attributes (`screen._renderer = self.renderer`) rather than calling `self.make_renderer(screen)`. This means the `make_*` methods are only exercised by the 17 smoke tests, not by any of the 62 migrated strategy screen tests. If a `make_*` method had side effects beyond returning the mock (the production ones don't — they just construct), the test coverage would miss it. Given the production factory's trivial implementation (pure constructor calls), this is not a practical concern.

---

## Question 5: 1-Session Claim — Plausible or Cut Corners?

**Verdict: PLAUSIBLE for 1 session, but work is shallow — the "bypass-init" problem is repackaged, not solved.**

### What was built (LOC counts)

| Artifact | LOC | Complexity |
|---|---|---|
| `strategy_screen_composition.py` (Protocol + Factory) | 114 | Low — 8 straight-line methods |
| `tests/fixtures/strategy_screen_composition.py` (Mock) | 119 | Low — 8 return stubs + populate loop |
| `test_strategy_screen_composition.py` (smoke tests) | 124 | Low — 17 formulaic tests |
| `strategy_screen.py` `__init__` delta | +14 | Trivial — 8 inline calls → 8 factory calls |
| `test_strategy_screen.py` helper delta | ~-10 lines | Replaced 8 inline MagicMock lines with `populate()` call |
| `test_strategy_menu_actions.py` helper delta | ~-5 lines | Removed `patch.object` wrapper |
| `docs/02_PATTERNS.md` update | ~1 paragraph | Pattern #32 entry |

**Total: ~370 new LOC + ~15 modified lines.** All follow the identical `DefaultRaceSetupDelegateFactory` pattern from PROJ-325. No novel design work — apply known pattern to known structure.

### Evidence of corners cut

1. **No test exercises the `composition=` seam.** The production code accepts `composition=` but zero tests create a `StrategyScreen(...)` with a mock composition. The bypass-init helper (`__new__` + `populate()`) is the only test path. The readme in the fixture literally calls this "currently impractical" (`tests/fixtures/strategy_screen_composition.py:18-21`).

2. **`populate()` bypasses the `make_*` methods.** The helper at `test_strategy_screen.py:81-82` calls `composition.populate(screen)` which directly sets attributes — not `composition.make_renderer(screen)`, etc. The 62 migrated tests never call a single `make_*` method. The 17 smoke tests exercise them in isolation with a MagicMock `_stub_screen()`.

3. **"Compositional Construction" name overpromises.** True compositional construction would let tests do `StrategyScreen(1920, 1080, composition=mock_comp)` and have `__init__` run normally with only sub-objects mocked. This pattern was achieved for `RaceSetupScreen` (two-stage init), but Phase 4 explicitly deferred that for `StrategyScreen`. The delivered artifact is more accurately a "sub-object factory extraction" — a seam exists but isn't load-bearing.

4. **Migration was structural, not behavioral.** The 62 tests were migrated but none needed per-test mock customization — every test uses the exact same MagicMock defaults (checklist confirms this at `phase_4_checklist.md:117`). This means the migration was a search-and-replace of 8 lines in the helper, not a thoughtful re-audit of test boundaries.

### Plausibility

A single LLM session could absolutely produce this work:
- The pattern is formulaic (copy-paste-adapt from PROJ-325's delegate factory).
- The 8 factory methods are trivial one-liners.
- The fixture is mirrored from the factory.
- Smoke tests are parametrized copy-paste.
- `__init__` delta is a localized replacement of 8 lines.

The multi-day estimate in PROJ-322 likely assumed a deeper refactor (stratifying `__init__` into lightweight + heavyweight stages). That deeper refactor was **not done** — the estimate mismatch is explained by scope reduction, not speed.

---

## Summary

| Question | Finding |
|---|---|
| 1. Constructor signatures | **PASS** — All 8 match. No mismatches. |
| 2. MockComposition same-mock risk | **LOW** — 8 distinct MagicMocks, not 1 shared. Standard MagicMock hazard, not PR-specific. |
| 3. Migration fidelity | **PASS** — All `patch.object(StrategyScreen, '__init__')` removed. Improvement is real but shallow (DRY + fewer monkey-patches; `__new__` bypass persists). |
| 4. Missing `__init__` setup | **PASS** — Helper fully replicates attribute surface. `_load_assets()` skipped correctly (requires disk I/O). |
| 5. 1-session plausibility | **PLAUSIBLE** — ~370 LOC of formulaic code following a proven pattern. Multi-day estimate was for deeper `__init__` stratification that was deferred. |

**Overall assessment:** The Phase 4 delivery is correct but shallow. It wraps the existing bypass-init pattern in cleaner clothing (protocol + fixture) without solving the underlying problem (tests can't call the real constructor). The 17 smoke tests pin the contract; the 62 migrated tests are structurally unchanged from pre-PROJ-327. The "Compositional Construction" pattern entry in docs oversells what was achieved for `StrategyScreen` specifically — compare to `RaceSetupScreen`'s true two-stage init where tests genuinely construct the target class with a mock delegate.
