# Phase 1: F-D-028 — extract `battle_state.py` serde into `battle_state_serde.py`

**Status:** Not Started
**Depends on:** none
**Review Mode:** standard (save-load + replay are the regression gates)
**Files:**
- `game/simulation/battle_state.py` (production; edit)
- `game/simulation/battle_state_serde.py` (production; new)
- `tests/integration/save_load/test_battle_state_serde_roundtrip.py` (test; new — TDD-first)

**Objective:** Extract the 10 paired `to_dict` / `from_dict` methods on the 5 dataclasses in `battle_state.py` (ComponentState, ShipState, ProjectileState, BattleState, BattleResults) into a sibling `battle_state_serde.py` module modeled on `planet_serde.py` and `fleet_serde.py` (post-PROJ-459). Closes F-D-028.

**Save-format invariant:** byte-identical output before and after the extraction. Replay capture + playback round-trips must remain byte-identical.

**Discipline framing:** This is a **characterization-first refactor**, not RED-then-GREEN strict TDD. The extraction introduces no new behavior, so the standard RED test is replaced by comprehensive round-trip tests for each of the 5 dataclasses that PASS against current code (characterize the current dict shape verbatim) and are then locked as frozen comparison constants. The post-extraction test run is the regression gate — any drift between pre- and post-extraction dict output is a real failure. Per CLAUDE.md's allowance for pure-refactor work, this is the correct discipline for no-behavior-change extraction. (Optional alternative: a structural-RED test asserting `game/simulation/battle_state_serde.py` exists, which would fail before extraction and pass after; record in `decisions.md` if added alongside the characterization tests.)

**Reference templates:**
- `game/strategy/data/planet_serde.py` (219 LOC; single-class serde — the original PROJ-372 model)
- `game/strategy/data/fleet_serde.py` (TBD LOC; single-class serde threading `registries` — post-PROJ-459 sibling)
- This phase introduces the *multi-class* variant of the pattern.

---

## Tasks

### Task 1.1: Characterization-first — write the byte-identical round-trip tests [Simple]

**File:** `tests/integration/save_load/test_battle_state_serde_roundtrip.py` (new)
**Tests:** `pytest tests/integration/save_load/test_battle_state_serde_roundtrip.py -q`

- [ ] Create the test file. Add tests covering each of the 5 dataclasses:
  - `test_component_state_round_trip`
  - `test_ship_state_round_trip`
  - `test_projectile_state_round_trip`
  - `test_battle_state_round_trip` (full BattleState with ships, projectiles, end_condition_data)
  - `test_battle_results_round_trip`
- [ ] For BattleState specifically: capture a frozen dict comparison constant pre-extraction so the post-extraction assertion can verify byte-identity.
- [ ] Run the tests against current code (pre-extraction baseline). They should all pass. This is the **characterization step**, not a RED step — the test capturing current behavior is exactly the point.

### Task 1.2: Read serde templates [Simple]

**Files:** `game/strategy/data/planet_serde.py`, `game/strategy/data/fleet_serde.py` (read-only)

- [ ] Read planet_serde.py end-to-end.
- [ ] Read fleet_serde.py end-to-end if PROJ-459 has landed.
- [ ] Note the single-class shape. Then think about how to extend it to a 5-class module:
  - **Option A:** Module-level free functions for each pair: `component_state_to_dict`, `component_state_from_dict`, ..., `battle_state_to_dict`, `battle_state_from_dict`, etc.
  - **Option B:** Classmethods/methods on each dataclass that 1-line-delegate to a single free `*_to_dict` / `*_from_dict_kwargs` family.
  - Pick Option B for consistency with `from_dict` being a classmethod (it currently is on all 5; changing to module-level functions would change call sites everywhere). Document the choice in `decisions.md`.

### Task 1.3: Create `battle_state_serde.py` [Medium]

**File:** `game/simulation/battle_state_serde.py` (new)
**Tests:** `pytest tests/integration/save_load/test_battle_state_serde_roundtrip.py -q -n 4`

- [ ] Create the new file with a module docstring:
  ```python
  """Save/load helpers for the simulation BattleState dataclass family.

  Free functions for the 5 dataclasses (ComponentState, ShipState,
  ProjectileState, BattleState, BattleResults). The dataclass
  ``to_dict`` / ``from_dict`` methods are 1-line facades that call
  into these helpers.

  Modeled on ``game/strategy/data/planet_serde.py`` (PROJ-372) and
  ``game/strategy/data/fleet_serde.py`` (PROJ-459). Multi-class variant.
  """
  ```
- [ ] Add `TYPE_CHECKING` imports for the 5 dataclasses, `GameRegistries`, `BattleEngine`, `Projectile`.
- [ ] Write 10 free functions, paired:
  - `component_state_to_dict(state) -> Dict[str, Any]`
  - `component_state_from_dict(data) -> ComponentState`
  - `ship_state_to_dict(state) -> Dict[str, Any]`
  - `ship_state_from_dict(data) -> ShipState`
  - `projectile_state_to_dict(state) -> Dict[str, Any]`
  - `projectile_state_from_dict(data) -> ProjectileState`
  - `battle_state_to_dict(state) -> Dict[str, Any]`
  - `battle_state_from_dict(data) -> BattleState`
  - `battle_results_to_dict(results) -> Dict[str, Any]`
  - `battle_results_from_dict(data) -> BattleResults`
- [ ] Each function mirrors the current method body exactly. No semantic changes.
- [ ] Add `__all__` exporting only the public surface.
- [ ] Leave `capture_from_engine`, `from_component`, `from_ship`, `from_projectile`, `to_ship`, `to_projectile` on the dataclasses — these are construction-from-runtime helpers, not save-load.

### Task 1.4: Replace 10 method bodies on the dataclasses with facades [Medium]

**File:** `game/simulation/battle_state.py`
**Tests:** `pytest tests/integration/save_load/ tests/integration/replay/ tests/unit/simulation/ -q -n 4`

- [ ] Replace `ComponentState.to_dict` body (battle_state.py:48) with a 1-line call to `component_state_to_dict(self)`.
- [ ] Replace `ComponentState.from_dict` body (battle_state.py:59) with a 1-line call.
- [ ] Repeat for the other 8 methods (ShipState x2, ProjectileState x2, BattleState x2, BattleResults x2).
- [ ] Verify imports: each method needs a lazy `from game.simulation.battle_state_serde import ...` inside the method body, OR a top-level import (no circular concern since serde imports from battle_state with TYPE_CHECKING only).
- [ ] Run the byte-identical round-trip tests from Task 1.1 — they MUST pass.

### Task 1.5: Verify and tighten [Simple]

**Tests:**
```powershell
pytest tests/integration/replay/ tests/integration/save_load/ tests/unit/simulation/ -q -n 4
python Tools/test_sharded/test_sharded.py
```

- [ ] Save-load tests green (`tests/integration/save_load/`).
- [ ] Replay tests green (`tests/integration/replay/`) — replay capture serializes BattleState through this surface.
- [ ] Sharded suite green; same count as baseline.
- [ ] Re-measure battle_state.py LOC (PowerShell): `(Get-Content game/simulation/battle_state.py | Measure-Object -Line).Lines`. Target: 530-580 LOC (down from 832).
- [ ] Measure battle_state_serde.py LOC: `(Get-Content game/simulation/battle_state_serde.py | Measure-Object -Line).Lines`. Expected: ~280 LOC.
- [ ] Update `findings/PROJ-460_findings.md`: F-D-028 status → "closed via Phase 1 extraction; battle_state_serde.py created; save-format + replay byte-identical".

### Task 1.6: Docs sync [Simple]

**Files:** `docs/02_PATTERNS.md`, `docs/01_ARCHITECTURE.md`

- [ ] Extend the serde pattern entry in `docs/02_PATTERNS.md` to cover the multi-class variant.
- [ ] Update `docs/01_ARCHITECTURE.md` simulation/ listing to include `battle_state_serde.py`.

### Task 1.7: Commit [Simple]

- [ ] Commit message: `PROJ-460 Phase 1: extract battle_state serde to battle_state_serde.py (closes F-D-028; ~250 LOC drop)`
- [ ] Update `plan.md` Current State.

---

## Phase Completion Checklist
- [ ] battle_state_serde.py created (~280 LOC) with 10 free functions
- [ ] battle_state.py drops to 530-580 LOC
- [ ] 10 method bodies on the 5 dataclasses are 1-line facades
- [ ] Save-load round-trip byte-identical
- [ ] Replay round-trip byte-identical
- [ ] `pytest tests/integration/save_load/ tests/integration/replay/` green
- [ ] Sharded suite green
- [ ] F-D-028 marked closed in findings file
- [ ] Docs updated
