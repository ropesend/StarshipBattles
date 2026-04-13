# Unified Entry/Exit Contract — Skeptical Audit

## Verdict

**Contract upheld in letter only; material gaps remain in spirit.** The `run_battle(spec) → BattleOutcome` contract is genuinely enforced for *headless* paths (strategy, Combat Lab headless/batch). The *visual* path, however, is not really a `run_battle` driver — it is a hand-rolled replica that skips `run_battle` entirely, and the regression guards are narrow enough to miss the real bypass surface. Several "acceptance criteria satisfied" claims in `acceptance_audit.md` are demonstrably overstated once the guard patterns are inspected.

## Findings

### Finding 1: Visual mode does NOT go through `run_battle` — it is a hand-rolled replica

**Severity:** High
**Location:** `game/ui/screens/test_lab/screen.py:396-463`, `combat_lab/services/test_execution_service.py:56-111`, `game/app.py:543-599`
**What's wrong:** All three visual-mode "entry points" bypass `run_battle` and `start_engine_from_spec`. They manually: (1) build a `BattleConfig`, (2) reach into `controller.service.get_engine()` and mutate `engine.boundary` / `engine.modifier_stack` externally, (3) call `materialize_spec_ships` directly, (4) call `controller.add_ships(...) + controller.start()` — the legacy two-phase dance that PROJ-270's plan explicitly listed as a target for elimination ("`controller.add_ships(ships, 0)` + `controller.start()`" is precisely the pattern Decision 3 was meant to replace for visual mode). The spec is handed to the controller only so `extract_outcome` can fire at battle end — it is never consumed as the construction authority. This is a hybrid path: spec-in for outcome emission only, add_ships+start for everything else.
**Evidence:**
```python
# game/ui/screens/test_lab/screen.py:432-453
controller = BattleController(ai_factory=AIControllerFactory())
controller.configure(config, spec=spec)
engine = controller.service.get_engine()
if spec.boundary is not None:
    engine.boundary = spec.boundary            # spec fields re-threaded manually
engine.modifier_stack = spec.modifier_stack
teams_by_id, ships_by_role = materialize_spec_ships(...)
for team_id, ships in teams_by_id.items():
    controller.add_ships(ships, team_id=team_id)  # legacy two-phase
controller.start()                                 # legacy two-phase
```
Essentially identical code appears in `test_execution_service.py:60-95` and `game/app.py:553-597`. PROJ-270 Task 4.2 was explicitly scope-trimmed: *"Decision — did NOT route through `start_engine_from_spec` from within `configure()`"* (phase_4_checklist.md line 43). That trim left the visual path in a half-migrated state: the spec is data-pass-through for outcome only, not the construction contract.
**Recommended fix:** Add a `BattleController.start_from_spec(spec, *, ai_factory, ship_builder)` method that calls `start_engine_from_spec` internally so spec.boundary/modifier_stack/materialization flow through a single path. Migrate all 3 call sites to it. Delete the `engine.boundary = …; engine.modifier_stack = …` lines from the callers. This is what Decision 3 in `PROJ-270/decisions.md` originally required — the scope trim should be revisited as a Phase 9 task.

---

### Finding 2: `BattleScreen._build_fallback_outcome` is a shim that violates the spirit of the contract

**Severity:** Medium
**Location:** `game/ui/screens/battle_screen.py:227-260` (`start(team0, team1, ...)`) and `488-571` (`_build_fallback_outcome`)
**What's wrong:** `BattleScreen.start(team0_ships, team1_ships, ...)` takes two ship lists (no spec!), constructs a `BattleConfig`, calls `controller.configure(config)` with **no spec**, then `add_ships + start`. When the battle ends, `_build_fallback_outcome()` synthesizes a `BattleOutcome` from live engine state — including fabricating `seed=0`, `telemetry_level=NORMAL` with empty aggregator data, and `end_reason=EndReason.TEAM_ELIMINATED` regardless of what actually happened. This is precisely the kind of "synthesize a fake outcome so the claim 'every battle emits outcome' is technically true" bandaid the user's audit request flagged. The acceptance_audit.md admits this openly: *"Fallback path emits a synthesized outcome → criterion met."* That's letter, not spirit. The fallback is called from `BattleScreen._on_battle_ended()` (line 486) which is the **only** on-battle-end path, so any bug that leaves `_controller._spec` unset in production will silently fall through to the shim instead of raising.
**Evidence:**
```python
# battle_screen.py:565-571
return BattleOutcome(
    end_reason=EndReason.TEAM_ELIMINATED,   # Hard-coded; may be wrong
    duration_ticks=engine.tick_counter,
    seed=0,                                  # Fabricated
    teams=team_outcomes,
    telemetry_level=TelemetryLevel.NORMAL,   # Claims NORMAL with empty aggregator data
)
```
The `start(team0, team1)` API has ~60 tests using it (phase_4_checklist.md line 55), but these are test fixtures — the architectural claim should NOT be softened to accommodate them.
**Recommended fix:** Delete `BattleScreen.start(team0, team1)` and `_build_fallback_outcome()`. Migrate the ~60 tests to build a minimal `BattleSpec` via a shared test helper (there's already `build_manual_battle_spec` infrastructure). If a shim is genuinely needed, make it raise `NotImplementedError` in production (guarded by `sys.gettrace()` or an explicit test marker) so the fallback can never mask a production bug.

---

### Finding 3: Direct `self.engine.update()` bypass in `BattleScreen._run_single_tick`

**Severity:** High
**Location:** `game/ui/screens/battle_screen.py:401-410`
**What's wrong:** `_run_single_tick` contains a fall-through that drives the engine directly without the controller:
```python
# Delegate to controller if available, else direct engine update
if self._controller:
    self._controller.update()
else:
    self.engine.update()   # <-- direct engine tick, no outcome extraction path
```
If the `else` branch ever executes in production, (a) `BattleController._extract_outcome_on_battle_end` never fires, so `_controller.get_outcome()` returns None forever, (b) `_build_fallback_outcome` takes over silently. The regression guard `test_unified_entry_guard.py` never grep-matches `\.engine\.update\(`, only `BattleEngine(` construction and `scenario\.setup\(` calls. Pattern is invisible to the guard suite.
**Evidence:** Guard `TestNoDirectBattleEngineConstruction` only looks for `\bBattleEngine\(`. There is no guard covering direct `engine.update()` or `engine.start()` calls outside the whitelisted `BattleService._engine.start(...)` at `game/simulation/services/battle_service.py:207`.
**Recommended fix:** Delete the `else: self.engine.update()` branch. If `self._controller` is None at this point, raise `StateException("BattleScreen ticking without a controller — invariant violation")`. Add a guard test that greps for `\bengine\.update\(` outside `BattleEngine` / `BattleService`.

---

### Finding 4: Guard (e) ("zero `deprecated` comments") is NOT enforced — criterion is falsely claimed satisfied

**Severity:** Medium
**Location:** `tests/unit/simulation/test_unified_entry_guard.py:122-133`, `Projects/active_projects/PROJ-270/findings/acceptance_audit.md` §Criterion (e)
**What's wrong:** Decisions.md Decision 3 specifies criterion (e) as *"Zero `Legacy-compatible` / `retained for` / `deprecated` comments in live code"*. The acceptance audit claims this is satisfied. The guard regex is:
```python
pattern = re.compile(r"Legacy-compatible|retained for")
```
`deprecated` (case-insensitive or otherwise) is **not in the pattern**. A quick grep shows ~17 live-code files with `DEPRECATED` or `deprecated` markers, including:
- `game/simulation/components/ability_manager.py:286` `# ---- DEPRECATED static methods (kept for transition) ----`
- `game/simulation/components/modifier_manager.py:221` `# ---- DEPRECATED static methods (kept for Task 1.3 transition) ----`
- `game/ui/screens/builder/modifier_logic.py:175-181` `# Deprecated: ModifierLogic static wrapper`
- `game/app.py:171` `# PROJ-181: Deprecated set_default_registries() removed.` (historical, OK)
Some are unrelated to PROJ-269/270 but several are explicit System Migration Policy violations ("kept for transition"). The audit signed off without checking.
**Evidence:** See the grep output above. Also `game/ui/screens/battle_screen.py:116-118` contains the marker `# Legacy state — kept as instance vars for backward compatibility with Combat Lab code that still sets them directly. Will be fully removed when Combat Lab migrates to controller flow.` — this is the exact shape of a PROJ-270 legacy-compat shim but neither the word `Legacy-compatible` (hyphenated) nor `retained for` appears literally, so the regex passes.
**Recommended fix:** Expand the guard regex to `r"\b(Legacy-compatible|Legacy state|retained for|kept for (?:transition|backward|legacy)|backward[- ]compat(?:ibility)?|DEPRECATED)\b"`. Re-run and work the hit list. Note that many of the `backward compat` matches (e.g. `engine.start(team0, team1)` 2-team wrapper) are arguably legitimate — each needs a case-by-case decision.

---

### Finding 5: Integration test Task 4.1 "de-facto satisfied" — no true end-to-end test exists

**Severity:** Medium
**Location:** `Projects/active_projects/PROJ-270/phase_4_checklist.md:17-26`, `tests/unit/simulation/battle_controller/test_outcome_emission.py`
**What's wrong:** Task 4.1 required a new integration test `tests/integration/ui/test_visual_battle_outcome.py` exercising the visual path end-to-end. It was closed as "DE FACTO SATISFIED" pointing to `test_outcome_emission.py`. But that file mocks `BattleService`, mocks `BattleEngine`, mocks `is_battle_over`, and monkey-patches `extract_outcome`. It proves only that the *plumbing between controller methods* is connected. It does NOT prove:
1. A real `BattleController` driving a real `BattleEngine` emits a real `BattleOutcome`.
2. The visual per-frame loop (`BattleScreen._run_single_tick → _controller.update → _extract_outcome_on_battle_end`) actually wires up end-to-end.
3. `test_execution_service.run_visual` / `_switch_to_battle` / `Game.start_battle` correctly populate the controller such that the outcome is non-empty.
Given Finding 1 and Finding 3, #2 in particular is load-bearing and currently unverified.
**Recommended fix:** Write `tests/integration/ui/test_visual_battle_outcome.py` — construct a real `BattleSpec` with minimal ships, drive it through the full `Game.start_battle(spec)` → `BattleScreen._run_single_tick` loop until `is_battle_over()`, assert `controller.get_outcome()` is non-None and is NOT the `_build_fallback_outcome` synthesizer.

---

### Finding 6: `load_state` fallback-to-`UnboundedRegion` is a bandaid, not a clean-sheet design

**Severity:** Low
**Location:** `game/simulation/battle_controller.py:478-483`
**What's wrong:** `BattleController.load_state(state)` constructs a `RetreatManager(boundary=UnboundedRegion())` because saves don't carry a spec. CLAUDE.md's System Migration Policy says "save files are disposable — do not write compatibility shims." Yet this is exactly a compatibility shim: it silently disables edge retreat for loaded battles instead of (a) saving the boundary in `BattleState`, (b) rejecting loads that lack boundary, or (c) rehydrating a spec from state. The PROJ-270 closure comment *"load_state has no spec in hand, and saves are disposable (CLAUDE.md) — default boundary to UnboundedRegion"* is self-contradictory: if saves are disposable, delete load_state entirely; if they aren't, fix the shim.
**Evidence:** No production callers of `load_state` (grep `load_state` across `game/` returns only the definition + `restore_config_from_state` inside `battle_state_manager.py`). The method is test-only as of today. Keeping it with a silent degradation is dead code with teeth.
**Recommended fix:** If load_state is dead, delete it. If it's live, either serialize the boundary or rehydrate a spec from `BattleState.seed + ships`. Raise on unrecognized states rather than silently swapping in `UnboundedRegion`.

---

### Finding 7: Stale docstring contradicts the contract in `test_executor.py`

**Severity:** Low
**Location:** `game/ui/screens/test_lab/test_executor.py:113-115`
**What's wrong:** Comment reads: `# Switch to battle scene for visual execution / # (_switch_to_battle handles engine.start + scenario.setup)`. This is false — `_switch_to_battle` does NOT call `engine.start` (it calls `controller.start`) and `scenario.setup` was deleted in Phase 1.3. The `setup` reference in live code is exactly the kind of drift Phase 8.5 docstring sweep was meant to catch. The Phase 8.5 sweep claimed to have caught the residual `scenario.setup(` / `battle_engine.start(` in `docs/systems/combat_simulation.md`, `combat_lab/battle_state_capture.py`, and `tests/unit/combat_lab/test_test_metadata_end_conditions.py` (plan.md line 57) — this one was missed.
**Recommended fix:** Update the comment to `# (_switch_to_battle compiles spec, starts controller, wires scenario to engine)`. Trivial edit; just evidence that the docstring sweep is incomplete.

---

### Finding 8: Guard (a) whitelist allows the entire `battle_service.py`, including `engine.start(team0, team1)`

**Severity:** Low
**Location:** `tests/unit/simulation/test_unified_entry_guard.py:64-68`, `game/simulation/services/battle_service.py:207-213`
**What's wrong:** Criterion (a) says "zero direct `engine.start*()` calls outside `run_battle`, `start_engine_from_spec`, `BattleService.create_battle`, and `BattleController` lifecycle methods." But `BattleService.start_battle` at line 207 calls `self._engine.start(team0_ships=..., team1_ships=...)` — i.e., it uses the 2-team backward-compat wrapper (see `battle_engine.py:385`, which admits "2-team backward-compat wrapper around `start_teams` (PROJ-269 Phase 3)"). Visual-mode battles route through `BattleService.start_battle` → `engine.start()` (2-team) while headless battles route through `start_engine_from_spec` → `engine.start_teams()` (N-team). Two code paths do the same thing by different routes, and visual mode silently loses N-team support.
**Evidence:** `BattleService.start_battle` is not called from `run_battle` — `run_battle` uses `start_engine_from_spec` → `engine.start_teams` directly. So `BattleService.start_battle`'s `engine.start` call exists *only* to support `BattleController.start()`, which is *only* called from visual-mode paths.
**Recommended fix:** Make `BattleService.start_battle` call `engine.start_teams(teams_by_id, ...)` with a dict — or better, remove `BattleService.start_battle` and have `BattleController.start_from_spec` (see Finding 1) call `start_engine_from_spec` directly. The 2-team `engine.start` wrapper should remain only for tests; no production caller should hit it.

---

## Summary of Recommended Phase 9 Tasks

Ordered by severity:

1. **(High)** Implement `BattleController.start_from_spec(spec, ai_factory, ship_builder)` + migrate all 3 visual call sites (Findings 1, 3, 8).
2. **(High)** Delete `BattleScreen._run_single_tick` else-branch + `BattleScreen.start(team0, team1)` + `_build_fallback_outcome` + migrate ~60 tests to a spec-based helper (Findings 2, 3).
3. **(Medium)** Write real integration test `tests/integration/ui/test_visual_battle_outcome.py` that doesn't mock the service/engine (Finding 5).
4. **(Medium)** Expand guard regex to cover `deprecated`, `backward compat`, `Legacy state`, `kept for transition`; fix the hit list or explicitly whitelist per case (Finding 4).
5. **(Low)** Resolve `load_state` — delete or fix (Finding 6).
6. **(Low)** Update stale comment in `test_executor.py:113-115` (Finding 7).

The regression guards at `tests/unit/simulation/test_unified_entry_guard.py` are the load-bearing piece of the PROJ-270 closure story — they need to actually match the contract described in `decisions.md` Decision 3. Today they match a narrower interpretation that lets several real violations through.
