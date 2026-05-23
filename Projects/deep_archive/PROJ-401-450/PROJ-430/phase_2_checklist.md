# Phase 2: Introduce grouped accessors as the new primary surface

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-430 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_1
**Review Mode:** standard
**Files (planned):**
- `game/strategy/facade/grouped_namespaces.py` (new)
- `game/strategy/facade/strategy_session_facade.py` (add 9 `@property` accessors; flat surface still present)

**Objective:** Add the new grouped namespace dataclasses and expose them via `@property` accessors on `StrategySessionFacade`. The behavior-parity tests from Phase 1 go green. The legacy flat surface and cache forwarders are **still present** — they go away in Phase 5. This phase is purely additive.

---

## Tasks

### Task 2.1: Author `game/strategy/facade/grouped_namespaces.py` [Medium]
**File:** `game/strategy/facade/grouped_namespaces.py` (new)
**Tests:** `pytest tests/unit/strategy/facade/test_facade_grouped_namespaces.py -q` — should go green after this task lands plus Task 2.2

The file hosts 8 thin dataclasses, each wrapping an existing slice and exposing the renamed verbs.

- [ ] `FacadeCommands` — wraps `CommandDispatchSlice`. Constructor takes `(helper_name, command_cls)` iterable as a parameter (decouples from `command_registry` reshape per TD-03 hedge). Strips `dispatch_` prefix from each helper. Mechanical: `dispatch_issue_move` -> `issue_move`, etc. Generate via `command_registry.specs_by_facade_helper()` and pass the result into the constructor at facade-init time.
- [ ] `FacadeFleetQueries` — wraps `FleetSlice`. Renames: `get_fleet` -> `get`, `get_fleets_at_hex` -> `at_hex`, `get_fleet_path_preview` -> `path_preview`, `get_fleet_path_projection` -> `path_projection`, `get_fleet_remaining_pods` -> `remaining_pods`.
- [ ] `FacadePlanetQueries` — wraps `PlanetSlice`. Renames: `get_planet` -> `get`; the second planet method follows the same prefix-strip pattern.
- [ ] `FacadeSystemQueries` — wraps `SystemSlice`. 6 read methods; strip `get_` prefix uniformly.
- [ ] `FacadeEmpireQueries` — wraps `EmpireSlice`. 6 read methods; strip `get_` prefix.
- [ ] `FacadeEventQueries` — wraps `EventSlice`. 3 read methods; strip `get_` prefix.
- [ ] `FacadeSessionInfo` — wraps the session-info slice (whichever slice owns turn number, save path, human IDs today). Decide property-vs-method during authoring; record the choice in `decisions.md`.
- [ ] `FacadeEconomyQueries` — wraps `EconomySlice`. Includes `resolve_config()` (renamed from `_resolve_economy_config`, no underscore prefix). Includes `race_registry`, `colony_demographic_view(...)`.
- [ ] `FacadeValidation` — wraps the validation surface. `can_colonize(...)`, `can_move_to(...)`.
- [ ] Each dataclass is `@dataclass(frozen=True, slots=True)` if practical — they should be cheap to construct, immutable, with no per-call state.
- [ ] Each wrapper holds only the slice reference (or, for `FacadeCommands`, the slice + the iterable). No new caching, no new state.
- [ ] Module docstring explicitly states: "Public surface namespaces for `StrategySessionFacade`. New facade methods land on the appropriate namespace, not on the facade class. This file is the public API contract for the facade."

**Notes:** [Filled during implementation. If a method name collides with a Python built-in (`get` is fine on a frozen dataclass; double-check `at_hex` etc. don't shadow dict methods if the dataclass is dict-like), pick a non-colliding alternative and record it in `decisions.md`.]

### Task 2.2: Wire the 9 `@property` accessors on `StrategySessionFacade` [Medium]
**File:** `game/strategy/facade/strategy_session_facade.py`
**Tests:**
- `pytest tests/unit/strategy/facade/test_facade_grouped_namespaces.py -q` — should go **green**
- `pytest tests/unit/strategy/facade/test_strategy_session_facade_public_api.py -q` — partial: `test_grouped_namespaces_expose_expected_methods` goes green; the legacy-flat-methods and legacy-cache-attrs assertions remain red until Phase 5

- [ ] Add 9 `@property` getters returning the namespace instances. Each is constructed lazily on first access (memoize on `self`), so a facade that never touches `fleets` doesn't pay the construction cost.
  ```
  @property
  def commands(self) -> FacadeCommands: ...
  @property
  def fleets(self) -> FacadeFleetQueries: ...
  # ... etc for systems, planets, empires, events, session_meta, economy, validation
  ```
  (`facade_state` is already public; no change there.)
- [ ] Construct each namespace by passing the existing slice instance (and, for `FacadeCommands`, the registry-derived iterable) — no new slice instantiation.
- [ ] **Do NOT delete** any existing top-level method, cache forwarder, or legacy alias in this phase. They stay until Phase 5. The grouped surface and the flat surface coexist for now.
- [ ] Run the focused facade tests:
  ```
  pytest tests/unit/strategy/facade -q
  ```
  Expected: `test_facade_grouped_namespaces.py` fully green; the public-API contract test still red on the legacy-flat-methods and legacy-cache-attrs assertions but **green** on `test_grouped_namespaces_expose_expected_methods`.

**Notes:** [Filled during implementation]

### Task 2.3: Verify no regressions in unrelated tests [Simple]
**Files:** none
**Tests:** wider facade and strategy test surface

- [ ] Run:
  ```
  pytest tests/unit/strategy/facade tests/unit/strategy/engine -q
  ```
- [ ] Confirm zero regressions outside the two TDD anchor files. The grouped surface is purely additive in Phase 2; any pre-existing test going red is a bug in the namespace dataclasses.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `grouped_namespaces.py` exists with all 8 dataclasses
- [ ] `StrategySessionFacade` exposes all 9 group accessor properties
- [ ] `test_facade_grouped_namespaces.py` is fully green
- [ ] `test_grouped_namespaces_expose_expected_methods` is green; the other two new contract assertions remain red by design
- [ ] No regression in `tests/unit/strategy/facade` or `tests/unit/strategy/engine` outside the documented red assertions
- [ ] `python Projects/scripts/validate_phase.py PROJ-430 2` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
