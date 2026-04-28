# FEAT-12: Race Setup Randomization — Environment, Aptitudes, and Master "Randomize All"

## Description
Extend the existing "Generate Random" button on the Race Setup screen
([game/ui/screens/race_setup_screen.py](../../../game/ui/screens/race_setup_screen.py))
so that randomization is available for every category except Description,
and add a master "Randomize All" button on the Summary tab that fills
every category in one click.

Today the button is dispatched by `_on_randomize()` at
[race_setup_screen.py:845](../../../game/ui/screens/race_setup_screen.py#L845)
and is only shown on the Identity, Visuals, and Ships tabs
([race_setup_screen.py:707](../../../game/ui/screens/race_setup_screen.py#L707)).
Environment and Aptitudes have no randomize support.

### Required additions

1. **Environment tab — "Generate Random" button**
   - Iterate `FACTOR_REGISTRY` in
     [game/strategy/data/habitability_factors.py](../../../game/strategy/data/habitability_factors.py)
     and pick a random setpoint AND tolerance for every factor (gravity,
     temperature, water, pressure, tectonic, magnetic, radiation, and the
     10 gas factors).
   - Each setpoint must respect that factor's `min_value` / `max_value`.
   - **Tolerance is randomized** — but tolerance deviations from the
     factor default cost points (see point-budget rule below).
   - Write the result to `race_config.preferences` keyed by factor id.

2. **Aptitudes tab — "Generate Random" button**
   - Randomly distribute aptitude scores across the 7 paid aptitudes
     (strength, intelligence, constitution, dexterity,
     tolerance_other_species, cooperation, conflict_tolerance).

3. **Master "Randomize All" button — Summary tab**
   - Lives on the Summary tab (TAB_SUMMARY=0); not shown on per-category
     tabs.
   - Randomizes Identity, Visuals, Ships, Environment, and Aptitudes in
     sequence.
   - **Description is excluded** (the user explicitly opted it out — it
     is intended to be LLM-generated; see the companion LLM-description
     feature ticket).
   - Reuses the per-tab handlers rather than duplicating logic.

### Point-budget constraint (applies to per-category AND master modes)
Aptitudes and environmental tolerances share the same point budget
(see [race_point_budget.py:10-23](../../../game/strategy/data/race_point_budget.py#L10-L23)
— setpoints are free, but tolerance deviations and aptitude scores
above/below 50 cost from a 100-point pool).

The randomizer **MUST** keep the resulting RaceConfig within budget
(`get_remaining_points() >= 0`). For the master button this means the
budget has to be apportioned across aptitudes AND environmental
tolerances, not blown by either alone. The implementation will need a
strategy for this — e.g. budget-aware allocation, or randomize then
clamp/rebalance.

### UX notes
- The button on the Environment and Aptitudes tabs reuses the existing
  bottom-bar "Generate Random" pattern; update the tab visibility
  filter at
  [race_setup_screen.py:707](../../../game/ui/screens/race_setup_screen.py#L707).
- The master "Randomize All" on the Summary tab can be the same bottom
  button repurposed, or a distinct button — implementer's call, but it
  must be visually clear that it affects every tab.

## Priority
Medium

## Status
Awaiting Confirmation

## Work Log
- 2026-04-26: Created from QA Session 20260426_083959.
- 2026-04-26: Deep dive (Protocol 02b) executed. 4-agent swarm, user interview, complexity assessment, implementation strategy below.
- 2026-04-26: All 6 sub-tasks complete (TDD throughout). Files modified:
  - `game/strategy/systems/race_randomizer.py` — RNG retrofit on existing 4 methods + 3 new methods (`randomize_aptitudes`, `randomize_environment`, `randomize_all`). Existing methods now accept optional `rng: random.Random` per `docs/02_PATTERNS.md` §18; defaults preserved for the 4 production callers. New methods compute cost via `RacePointBudget` and rebalance toward registry defaults when over budget.
  - `game/ui/screens/race_setup_screen.py` — visibility filter (line 707) extended to TAB_ENVIRONMENT + TAB_APTITUDES. `_on_randomize` dispatcher (line 845) extended with elif branches. New `_randomize_environment`, `_randomize_aptitudes`, `_randomize_all` handlers. Master button event-handled in `process_event`. Per-tab handlers compute residual budget = `100 - cost(other categories)`.
  - `game/ui/panels/race_summary_panel.py` — added `btn_randomize_all` widget parallel to `btn_load`, plus `on_randomize_all_callback` constructor parameter. Tooltip explains the master action.
  - `tests/unit/strategy/test_race_randomizer.py` — added `TestRaceRandomizerRngThreading` (6 tests), `TestRandomizeAptitudes` (8 tests), `TestRandomizeEnvironment` (10 tests), `TestRandomizeAll` (4 tests). 23 → 51 tests.
  - `tests/unit/ui/screens/test_race_setup_screen.py` — added `TestFeat12NavigationButtonVisibility` (7), `TestFeat12OnRandomizeDispatch` (2), `TestFeat12RandomizeEnvironmentHandler` (2), `TestFeat12RandomizeAptitudesHandler` (2), `TestFeat12RandomizeAllHandler` (1). +14 tests.
  - `tests/unit/ui/test_race_summary_panel.py` — added `TestFeat12RandomizeAllButton` (3 tests).
  - `docs/02_PATTERNS.md` — added pattern #27 "Budget-Aware Randomization (FEAT-12)" with reference to the canonical Per-Battle RNG (#18) it builds on. Bumped pattern count 25 → 27 (also added missing #26 entry to TOC).
  - `Tracking/features/active/FEAT-12.md`, `Tracking/feature_plan.md` — status tracking.

  Test counts (FEAT-12 affected suites): 122 passed (51 randomizer + 30 summary panel + 41 race setup screen). Existing 23 randomizer tests + existing 27 summary panel tests preserved. No baseline regressions in affected suites.

---

## Analysis Report (Phase 1 — Agent Swarm)

### Architecture Impact

- **Layers touched:** Strategy (`game/strategy/systems/race_randomizer.py` extended) and UI (`game/ui/screens/race_setup_screen.py`, `game/ui/panels/race_environment_panel.py`, `game/ui/panels/race_aptitudes_panel.py`, `game/ui/panels/race_summary_panel.py`).
- **Layer rules:** Fully compliant with `docs/01_ARCHITECTURE.md`. UI imports Strategy (allowed); Strategy never imports UI. Static randomizer methods stay in Strategy.
- **Files modified:** 5 production + 2 test files + 1 doc + 2 tracking files.
- **Files reused read-only:** `race_config.py`, `race_point_budget.py`, `habitability_factors.py` (FACTOR_REGISTRY), `homeworld_presets.py` (`apply_preset_to_config`).
- **Hidden field coupling:** `RaceConfig.homeworld_type` lives on the Environment tab via the homeworld preset dropdown — env randomizer must decide whether to set it. **User decision: pick a random preset, apply it, then add jitter** (so `homeworld_type` IS set, and preferences feel coherent).

### Dependency Map

- **Production callers of `RaceRandomizer`:** 1 site — `race_setup_screen.py` (4 calls in `_randomize_identity/_randomize_visuals/_randomize_ships`). No hidden game-logic dependencies.
- **Production callers of `RacePointBudget`:** 5 UI files (`race_setup_screen`, `race_validator`, `race_aptitudes_panel`, `race_summary_panel`, `race_environment_panel`).
- **Production callers of `FACTOR_REGISTRY`:** `race_config.py` (defaults), `habitability.py` (scoring), `race_environment_panel.py` (UI rows).
- **Affected test count:** 133 tests across 4 suites must keep passing (`test_race_randomizer.py` 23, `test_race_setup_screen.py` 37, `test_race_point_budget_v2.py` 28, `test_race_config.py` 45).
- **Regression risks:** LOW. Optional `rng=None` parameter is backward-compatible; budget reads are read-only; no shared-state races.

### Similar Patterns Found

- **Existing RaceRandomizer pattern** — static class, `randomize_xxx() -> Dict` returning a dict the screen layer applies. New methods follow the same shape.
- **`apply_preset_to_config(preset, race_config)`** in `game/strategy/data/homeworld_presets.py` — reusable utility; the env randomizer will call it as a seed before adding jitter.
- **Per-Battle RNG (PROJ-252, `docs/02_PATTERNS.md` §18)** — documented convention to thread `rng: Optional[random.Random] = None` through randomization code. Existing `RaceRandomizer` violates this. **User decision: retrofit all 4 existing methods + thread rng through new methods.**
- **No documented "Budget-Aware Randomization" pattern** exists. **User decision: add a new entry to `docs/02_PATTERNS.md` once implementation is final.**

### Documentation Discrepancies

| Discrepancy | Resolution |
|---|---|
| `RaceRandomizer` uses module-level `random` despite documented PROJ-252 pattern | Retrofit all 4 methods with `rng: Optional[random.Random] = None` (Sub-task 1 below). |
| No documented pattern for constraint-respecting random generation | Add "Budget-Aware Randomization" pattern to `docs/02_PATTERNS.md` after implementation (Sub-task 6 below). |
| Strategy docs separate preset application from budget mechanics | `strategy_layer.md` §7 already covers FACTOR_REGISTRY; minor note can be added if implementation reveals friction. |

---

## Requirements Context (Phase 2 — User Interview)

User-confirmed design decisions (gathered across plan-mode and deep-dive interviews):

| Question | Decision |
|---|---|
| Master-mode budget split | **Random per-run fraction** in `[0.3, 0.7]` apportioned to aptitudes; remainder to env. |
| Repro/happiness in env randomizer | **Both randomized** (repro is priced into the budget; happiness is free). |
| Aptitude distribution shape | **2-3 high (55-80), 2-3 low (20-45), rest = 50.** Easy to keep in budget; gives the race a clear "personality." |
| Master button UX | **Distinct button** labeled "Randomize All", on the Summary panel parallel to its existing `btn_load` "Load Race" button. |
| Homeworld coupling | Env randomizer picks a **random homeworld preset**, applies it via `apply_preset_to_config`, then adds per-factor jitter. Sets `RaceConfig.homeworld_type` to the chosen planet type. |
| RNG retrofit | **Retrofit all 4 existing methods** plus thread rng through new methods (closes PROJ-252 docs discrepancy). |
| New pattern doc entry | **Yes** — add "Budget-Aware Randomization" to `docs/02_PATTERNS.md` after implementation. |

---

## Complexity Assessment (Phase 3)

| Metric | Estimate |
|---|---|
| Production files modified | 5 (race_setup_screen, race_environment_panel, race_aptitudes_panel, race_summary_panel, race_randomizer) |
| Test files modified | 2 (test_race_randomizer, test_race_setup_screen); plus possibly minor tweaks to existing budget/config tests |
| Doc files modified | 1 (docs/02_PATTERNS.md — new pattern entry) |
| Tracking files modified | 2 (this ticket, feature_plan.md) |
| **Total file count** | **~10** |
| Layers touched | 2 (Strategy, UI) |
| New abstractions | 1 small (budget-aware random helper, lives inside `RaceRandomizer`); 1 documented pattern |
| New LOC (production) | ~250 (randomizer methods + UI wiring + button widgets + RNG retrofit) |
| New LOC (tests) | ~250 (randomizer determinism, budget-edge, distribution shape, UI dispatch, RNG retrofit coverage) |
| New LOC (docs) | ~30 (pattern entry) |
| **Total LOC** | **~500–550** |

**Rating:** **Complex** (per the protocol's rubric: 9+ files, 2 layers, new pattern needed, 300+ LOC). NOT project-scale — no new architecture, no new test infrastructure, no cross-cutting refactor.

The complexity comes from breadth (touches several panels + ticket-included docs/RNG retrofit), not depth (each individual change is small and well-understood).

---

## Implementation Strategy (Phase 4)

Six TDD sub-tasks in dependency order. Each is independently testable and could be its own commit.

### Sub-task 1: RNG retrofit on existing `RaceRandomizer` methods (foundation)

**Files:** `game/strategy/systems/race_randomizer.py`, `tests/unit/strategy/test_race_randomizer.py`.

- Add `rng: Optional[random.Random] = None` parameter to `randomize_identity`, `randomize_flag`, `randomize_portrait`, `randomize_theme` (and helpers `_pick_name_entry`, `_pick_leader`).
- When `rng is None`, fall back to module-level `random` (preserves all 23 existing test behaviors).
- Replace `random.choice(...)` with `(rng or random).choice(...)` style.

**Tests (TDD — write first):**
- New: deterministic-with-seed test for each of the 4 methods (same seed → same output).
- All 23 existing tests must continue to pass unmodified.

**Why first:** Zero behavior change for existing callers; subsequent sub-tasks adopt the threaded `rng` immediately.

### Sub-task 2: `randomize_aptitudes(budget, rng=None) -> Dict[str, int]`

**Files:** `game/strategy/systems/race_randomizer.py`, `tests/unit/strategy/test_race_randomizer.py`.

- Iterate `APTITUDE_NAMES` from [race_config.py:67](../../../game/strategy/data/race_config.py#L67).
- Pick 2–3 aptitudes for high (55–80), 2–3 for low (20–45), rest = 50.
- Compute total cost via `RacePointBudget._single_aptitude_cost`. If over `budget`, deterministically reduce the highest-cost aptitude one step toward 50 until within budget.
- Returns `{aptitude_name: value}` (no mutation).

**Tests (TDD — write first):**
- All 7 aptitudes present, values in `[1, 100]`.
- Cost ≤ budget for budgets `[20, 50, 100]` over 100 seeds each.
- 2–3 above 50, 2–3 below 50 (count check).
- Determinism with seeded `Random`.

### Sub-task 3: `randomize_environment(budget, rng=None) -> Dict[str, Any]`

**Files:** `game/strategy/systems/race_randomizer.py`, `tests/unit/strategy/test_race_randomizer.py`.

- Pick a random homeworld preset id from `load_homeworld_presets()`. Set returned `homeworld_type` accordingly.
- Apply that preset to a fresh `RaceConfig` via `apply_preset_to_config`.
- For each factor in `FACTOR_REGISTRY` not pinned by the preset, add jitter:
  - Setpoint: uniform within `[factor.min_value, factor.max_value]`.
  - Tolerance: `factor.default_tolerance × uniform(0.4, 2.0)`, clamped to `[factor.step, factor.default_tolerance × 4]`.
- Reproduction rate: uniform in `[0.005, 0.10]`. Happiness: uniform in `[0.0, 1.0]`.
- Total cost = `preferences_cost + reproduction_cost`. If over `budget`, rebalance most-expensive tolerances toward defaults.
- Returns `{"preferences": {factor_id: EnvironmentalPreference}, "homeworld_type": str, "base_reproduction_rate": float, "base_happiness": float}`.

**Tests (TDD — write first):**
- All 17 factors present in `preferences`; setpoints within `[min_value, max_value]`.
- Tolerances never zero or absurd.
- `homeworld_type` is a valid preset id.
- `repro` in `[0.005, 0.10]`, `happiness` in `[0.0, 1.0]`.
- Cost ≤ budget for budgets `[20, 50, 100]` over 100 seeds.
- Determinism with seeded `Random`.

### Sub-task 4: Per-tab "Generate Random" buttons (UI integration)

**Files:** `game/ui/screens/race_setup_screen.py`, `tests/unit/ui/screens/test_race_setup_screen.py`.

- Update visibility filter at line 707 — add `TAB_ENVIRONMENT` and `TAB_APTITUDES`.
- Extend `_on_randomize` at line 845 — dispatch to `_randomize_environment()` and `_randomize_aptitudes()`.
- New handlers:
  - `_randomize_environment()` — compute `budget = 100 - aptitude_cost - reproduction_cost (current)`, call randomizer, write `preferences`/`homeworld_type`/`base_reproduction_rate`/`base_happiness` to `race_config`, refresh env panel.
  - `_randomize_aptitudes()` — compute `budget = 100 - preferences_cost - reproduction_cost`, call randomizer, write aptitudes to `race_config`, refresh aptitudes panel.
- Both handlers refresh the budget displays on every panel that reads from it (env, aptitudes, summary).

**Tests (TDD — write first):**
- Per-tab dispatch routes to the right handler.
- Visibility filter shows the button on the four expected tabs.
- After randomize, `RacePointBudget.is_within_budget(race_config)` is True.
- Panel `set_from_config` and `update_budget_display` are called.

### Sub-task 5: Master "Randomize All" button on Summary panel

**Files:** `game/ui/panels/race_summary_panel.py`, `game/ui/screens/race_setup_screen.py`, `game/strategy/systems/race_randomizer.py`, `tests/unit/ui/screens/test_race_setup_screen.py`, `tests/unit/ui/panels/test_race_summary_panel.py` (if exists).

- Add `randomize_all(rng=None) -> Dict[str, Any]` to `RaceRandomizer`:
  1. Roll repro + happiness; price `reproduction_cost`.
  2. `available = 100 - reproduction_cost; f = uniform(0.3, 0.7); apt_budget = round(available * f); env_budget = available - apt_budget`.
  3. Call `randomize_aptitudes(apt_budget, rng)` and `randomize_environment(env_budget, rng)`.
  4. Final assert `RacePointBudget(...).get_remaining_points() >= 0`; if violated by rounding, strip one tolerance step from the most-expensive factor.
  5. Delegate identity/visuals/ships to existing `randomize_identity/flag/portrait/theme`.
  6. Return a single dict the screen layer applies.
- Add `btn_randomize_all` to `RaceSummaryPanel` parallel to `btn_load`. Constructor takes new `on_randomize_all_callback` parameter.
- Screen wires the callback to `_randomize_all` handler that calls `RaceRandomizer.randomize_all` and applies the result via `_populate_ui_from_config()` ([race_setup_screen.py:803](../../../game/ui/screens/race_setup_screen.py#L803)).
- Description tab is left untouched.

**Tests (TDD — write first):**
- Result includes identity/visuals/ships + env + aptitudes keys; description fields untouched.
- Final `RacePointBudget.is_within_budget(config)` is True over 100 seeds.
- Apportionment fraction varies between runs (sanity check on `[0.3, 0.7]` randomness).
- Button click on Summary panel invokes orchestrator and refreshes every panel.

### Sub-task 6: Documentation (closes Rule 2 + the docs discrepancy)

**Files:** `docs/02_PATTERNS.md`, this ticket.

- Add new pattern entry "Budget-Aware Randomization" to `docs/02_PATTERNS.md` (~30 lines):
  - **Where:** `game/strategy/systems/race_randomizer.py`.
  - **How it works:** roll candidate values, validate against shared cost function, rebalance toward defaults if over-budget.
  - **When to use:** any randomization where a global resource limit must hold.
- Update FEAT-12 Work Log + flip status to `Awaiting Confirmation`.
- Update `Tracking/feature_plan.md` row.

### Verification (end-to-end)

1. **Unit tests** — `pytest tests/unit/strategy/test_race_randomizer.py tests/unit/ui/screens/test_race_setup_screen.py tests/unit/ui/panels/test_race_summary_panel.py -v`. All Sub-task tests must run + fail before each implementation step (Rule 1).
2. **Sharded full suite** — `python Tools/test_sharded/test_sharded.py` — confirm 15112 baseline preserved.
3. **Manual smoke** — launch game, open Race Setup:
   - Click Generate Random on each of Identity / Visuals / Ships / Environment / Aptitudes; verify each updates only that tab and the Aptitudes "Points Remaining" stays ≥ 0 after every click.
   - Click Randomize All on Summary multiple times; verify all 5 categories populate, Description stays empty, budget ≥ 0, and races vary between clicks.
   - Verify the chosen homeworld_type matches the rolled preset and preferences feel "Earth-like" / "Jovian" / etc. accordingly.
   - Save a randomized race; reload it; verify round-trip is clean.

### Files modified (summary)

| File | Sub-task | Change |
|---|---|---|
| `game/strategy/systems/race_randomizer.py` | 1, 2, 3, 5 | RNG retrofit + 3 new methods. |
| `game/ui/screens/race_setup_screen.py` | 4, 5 | Visibility filter + 2 new handlers + master callback wiring. |
| `game/ui/panels/race_summary_panel.py` | 5 | Add `btn_randomize_all` + callback param. |
| `tests/unit/strategy/test_race_randomizer.py` | 1, 2, 3 | New test classes + RNG-determinism cases. |
| `tests/unit/ui/screens/test_race_setup_screen.py` | 4, 5 | Per-tab dispatch + master button tests. |
| `tests/unit/ui/panels/test_race_summary_panel.py` | 5 | Button construction + callback invocation tests (if file exists; else create). |
| `docs/02_PATTERNS.md` | 6 | Add "Budget-Aware Randomization" pattern entry. |
| `Tracking/features/active/FEAT-12.md` | 6 | Status → Awaiting Confirmation; Work Log entries. |
| `Tracking/feature_plan.md` | 6 | Row status update. |

---
### 📝 User Update [2026-04-27]

Verified during QA Session 20260427_151244. The feature works end-to-end: clicking "Randomize All" on the Summary tab generates Identity, Visuals, Ships, Environment, and Aptitudes correctly. **However**, the Summary tab itself does not visually refresh — its left-column labels (Faction, Species, Government, Physical, Society) stay blank until the user switches to another tab and back.

Filed as **BUG-118** with root cause analysis: `RaceSetupController.populate_ui_from_config()` updates `race_config` references on every panel but skips calling `_summary_panel.refresh()`. FEAT-12 stays Awaiting Confirmation pending BUG-118 fix.

See [BUG-118.md](../../bugs/active/BUG-118.md).
