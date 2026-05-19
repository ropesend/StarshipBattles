# Phase 2: F-D-011 partial — extract `battle_controller.py` `start_from_spec` headless / spec-in flow

**Status:** Not Started
**Depends on:** Phase 1 complete (battle_state_serde extraction landed)
**Review Mode:** standard + **manual UI smoke verification required** (battle-screen-adjacent code)
**Files:**
- `game/simulation/battle_controller.py` (production; edit)
- `game/simulation/battle_controller_spec.py` (production; new — name decided in-phase)

**Objective:** Extract the body of `BattleController.start_from_spec` (battle_controller.py:242-368, ~125 LOC) into a sibling module. `BattleController.start_from_spec` becomes a 1-line facade. Closes the battle_controller.py portion of F-D-011.

**Spec-in flow context:** `BattleController.start_from_spec(spec, ai_factory, ship_builder=None, registry_provider=None)` is the spec-in path that constructs the engine from a `BattleSpec`. It's the primary entry point for visual-mode battle starts (`game/app.py`, `game/screen_router.py`, `game/ui/screens/test_lab/screen.py`). The flow is self-contained orchestration: it doesn't share state with the visual-mode controller's per-frame update logic.

---

## Tasks

### Task 2.1: Audit `start_from_spec` for extractability [Simple]

**File:** `game/simulation/battle_controller.py` (read-only)

- [ ] Read `BattleController.start_from_spec` (battle_controller.py:242-368) in full.
- [ ] Identify what state the method touches:
  - `self.service` / `self.engine` / `self._spec` / `self._tick_phases` / etc. — visual-mode controller state
  - `spec`, `ai_factory`, `ship_builder`, `registry_provider` — caller-supplied args
- [ ] Identify any cleanup or post-tick wiring that happens INSIDE this method that won't easily extract (e.g., callback wiring, pre-tick setup registry).
- [ ] Decision: Option A (free function taking controller as first arg) or Option B (move off the class entirely).
  - **Option A (default):** Free function `build_controller_from_spec(controller, spec, ai_factory, ship_builder=None, registry_provider=None) -> BattleServiceResult`. `BattleController.start_from_spec` becomes:
    ```python
    def start_from_spec(self, spec, ai_factory, ship_builder=None, registry_provider=None):
        from game.simulation.battle_controller_spec import build_controller_from_spec
        return build_controller_from_spec(self, spec, ai_factory, ship_builder, registry_provider)
    ```
  - **Option B:** Move `start_from_spec` entirely off `BattleController` into a free function. Callers change call sites. Larger diff; harder review; only choose if Option A doesn't drop battle_controller.py below ~700 LOC.
- [ ] Document the chosen option in `decisions.md`.

### Task 2.2: Create sibling module [Medium]

**File:** `game/simulation/battle_controller_spec.py` (new; name TBD — alternatives include `battle_spec_loader.py`, `controller_spec_init.py`)

- [ ] Pick the final module name. `battle_controller_spec.py` is the default; record the choice in `decisions.md` with one-sentence rationale.
- [ ] Create the new file with a module docstring describing its scope (spec-in initialization for `BattleController`).
- [ ] Implement `build_controller_from_spec(controller, spec, ai_factory, ship_builder=None, registry_provider=None) -> BattleServiceResult`:
  - Mirror the body of `BattleController.start_from_spec` exactly.
  - Take `controller` as the first arg (replaces `self` references with `controller.`).
  - All other args and return semantics unchanged.
- [ ] If sub-helpers exist (e.g., a pre-tick setup builder, an AI factory wrapper), extract them as module-private functions in the same file.
- [ ] Add `__all__`.

### Task 2.3: Replace `BattleController.start_from_spec` body with facade [Medium]

**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/battle_controller/test_start_from_spec.py tests/integration/replay/ -q -n 4`

- [ ] Replace the 125-LOC body with a 1-line delegate:
  ```python
  def start_from_spec(self, spec, ai_factory, ship_builder=None, registry_provider=None) -> BattleServiceResult:
      """Start a battle from a BattleSpec. See battle_controller_spec.py."""
      from game.simulation.battle_controller_spec import build_controller_from_spec
      return build_controller_from_spec(self, spec, ai_factory, ship_builder, registry_provider)
  ```
- [ ] Update any internal imports that may have become unused.
- [ ] Run `pytest tests/unit/simulation/battle_controller/test_start_from_spec.py` — confirm the existing test guards still pass.

### Task 2.4: Manual UI smoke verification [Simple]

**Critical:** battle_controller is visual-mode adjacent. Test-suite coverage alone is insufficient.

- [ ] Run `python -m game` to start the game.
- [ ] Navigate to BattleSetupScreen.
- [ ] Start a battle.
- [ ] Confirm:
  - Ships spawn correctly.
  - Ticks run (no immediate end-of-battle).
  - Pre-tick callbacks fire (mine setups, reboard setups if present in the chosen scenario).
  - AI fires weapons.
  - No exceptions in the console.
- [ ] Exit cleanly.
- [ ] If anything is off — even subtly — diagnose before committing. Pre-tick callback wiring is the most likely failure mode.

### Task 2.5: Verify LOC target met [Simple]

- [ ] Re-measure battle_controller.py. Target: ~700 LOC (down from 831, drop of ~125).
- [ ] If still over 700: consider whether any additional methods are extractable in the same project, OR document the residue for next-touch.
- [ ] Measure battle_controller_spec.py. Expected: ~150 LOC.

### Task 2.6: Commit [Simple]

- [ ] Commit message: `PROJ-460 Phase 2: extract battle_controller.start_from_spec to sibling module (F-D-011 partial; ~125 LOC drop)`
- [ ] Update `plan.md` Current State.

---

## Phase Completion Checklist
- [ ] start_from_spec audit done; Option A or Option B chosen and documented
- [ ] Sibling module created (`battle_controller_spec.py` or chosen name) at ~150 LOC
- [ ] `BattleController.start_from_spec` is a 1-line facade
- [ ] battle_controller.py drops to ~700 LOC
- [ ] `pytest tests/unit/simulation/battle_controller/ tests/integration/replay/` green
- [ ] **Manual UI smoke test passed** (start a battle via BattleSetupScreen)
- [ ] Sharded suite green
- [ ] F-D-011 partial status updated in findings file
