# Phase 3: F-D-011 partial — split `replay_serialization.py` into `replay_capture_serde.py` + `replay_outcome_serde.py` + `replay_serde_helpers.py`

**Status:** Not Started
**Depends on:** Phase 2 complete
**Review Mode:** standard (save-load + replay are critical regression gates)
**Files:**
- `game/simulation/replay/replay_serialization.py` (production; DELETE after migration)
- `game/simulation/replay/replay_capture_serde.py` (production; new — spec-side serialization)
- `game/simulation/replay/replay_outcome_serde.py` (production; new — outcome-side serialization)
- `game/simulation/replay/replay_serde_helpers.py` (production; new — shared helpers)
- `game/simulation/replay/__init__.py` (production; edit — update re-exports)
- All callers of `from game.simulation.replay.replay_serialization import ...` and `from game.simulation.replay import ...` (production; migrate / verify)

**Objective:** Split `replay_serialization.py` (634 LOC) into two direction-shaped serialization halves plus a shared-helper module. Closes the replay_serialization.py portion of F-D-011.

**File naming — non-collision (BLOCKER from audit feedback resolved):** `game/simulation/replay/replay_capture.py` already exists in the package as the runtime capture-sink hook (owns `IReplayCaptureSink`, `NullCaptureSink`, `ReplayCaptureContext`; verified at `game/simulation/replay/__init__.py:25-32`). The new modules use distinct names:
- **`replay_capture_serde.py`** — spec-side serialization.
- **`replay_outcome_serde.py`** — outcome-side serialization.
- **`replay_serde_helpers.py`** — shared helpers (`_vec_to_list`, `_list_to_vec`, `_component_state_to_dict`, `_component_state_from_dict`).

**Shared-helper plan (Option A — chosen per audit feedback):** The line-407 split is not clean as-is: outcome-side ship_outcome serde (`replay_serialization.py:481-518`) depends on `_vec_to_list`/`_list_to_vec` (defined at :78-85) and `_component_state_to_dict`/`_component_state_from_dict` (defined at :222-240). These helpers are extracted into `replay_serde_helpers.py` and imported by both serde halves. Option B (duplicate helpers) was rejected because the helpers are non-trivial and duplication invites drift. Option C (leader-follower) was rejected because it creates a non-obvious peer dependency.

**No shim policy:** Per CLAUDE.md "no compat shims" rule, delete `replay_serialization.py` after migration. Do NOT keep as a re-export module. The `__init__.py` re-exports keep package-root callers working.

---

## Tasks

### Task 3.0: Pre-flight LOC + split-boundary re-measurement [Simple]

**Files:** `game/simulation/replay/replay_serialization.py` (read-only); `Projects/active_projects/PROJ-460/decisions.md` (write).

**Why this task exists:** Added per Group 3 pre-execution review (codex consult + claude subagent independent review, 2026-05-19). LOC of the three PROJ-460 target files has drifted since the original plan was written; cited symbols still resolve to correct sites but file-level totals and the spec/outcome split boundary in `replay_serialization.py` have moved. The "split at line 407" guidance throughout this checklist is stale — the actual `def battle_outcome_to_dict(...)` boundary is now near line 540. Re-measure before starting Task 3.1.

- [ ] Re-measure LOC of all three target files (PowerShell):
  ```powershell
  (Get-Content game/simulation/battle_state.py | Measure-Object -Line).Lines
  (Get-Content game/simulation/battle_controller.py | Measure-Object -Line).Lines
  (Get-Content game/simulation/replay/replay_serialization.py | Measure-Object -Line).Lines
  ```
  2026-05-19 baseline: `battle_state.py` = 715 LOC (was 832 at original drafting); `battle_controller.py` = 682 LOC (was 831); `replay_serialization.py` = 516 LOC (was 634). Confirm or update.
- [ ] Re-derive the spec/outcome split boundary in `replay_serialization.py`:
  ```powershell
  rg -n "^def battle_outcome_to_dict" game/simulation/replay/replay_serialization.py
  ```
  2026-05-19 baseline: line 542. The originally-cited boundary line 407 is stale. The shared-helper locations (`_vec_to_list` / `_list_to_vec` near line 78; `_component_state_to_dict` / `_component_state_from_dict` near line 222) also need confirmation — re-grep if uncertain.
- [ ] Record the post-2026-05-19 LOC + spec/outcome boundary line in `decisions.md` BEFORE starting Task 3.1 (entry: "Pre-Phase-3 baseline: replay_serialization.py = N LOC; spec/outcome boundary at line M (battle_outcome_to_dict); shared helpers at lines X-Y").
- [ ] Anywhere this checklist references "line 407" as the split boundary, mentally substitute the re-derived boundary line from this measurement. The DIRECTION of the split (spec capture vs outcome load) and the shared-helper SET (`_vec_to_list`, `_list_to_vec`, `_component_state_to_dict`, `_component_state_from_dict`) remain correct — only the line numbers shifted.

**Notes:** This is a 60-second measurement task added solely to keep Task 3.1's audit pass from copying a stale line number into the split decision. If the re-measured boundary is significantly different from the original `~540` 2026-05-19 estimate, surface that to the user before continuing.

---

### Task 3.1: Audit `replay_serialization.py` for split lines [Simple]

**File:** `game/simulation/replay/replay_serialization.py` (read-only)

- [ ] Read in full. Confirm the natural split is at the spec/outcome boundary (re-derived in Task 3.0; was ~407 at original drafting; likely ~540-542 as of 2026-05-19):
  - Lines 67-72 (approx): `REPLAY_SCHEMA_VERSION` constant (used by both halves)
  - Lines 78-85 (approx): `_vec_to_list` / `_list_to_vec` — **shared helpers** (used by both spec and outcome halves)
  - Spec-side capture path (above the boundary): boundary serde, modifier_entry / modifier_stack serde, entry_vector serde, combat_policies serde, component_state serde at ~:222-240 (also used by outcome side — **shared**), ship_spec serde, squadron_spec serde, task_force_spec serde, team_spec serde, battle_spec_to_dict, battle_spec_from_dict
  - Outcome-side load path (below the boundary): modifier_application serde, hit_record serde, weapon_summary serde, ship_stats serde, ship_outcome serde at ~:481-518 (uses `_vec_to_list` AND `_component_state_to_dict`), team_outcome serde, battle_outcome_to_dict (the boundary symbol), battle_outcome_from_dict, `compute_components_registry_hash`
- [ ] Confirm the shared-helper set is exactly: `_vec_to_list`, `_list_to_vec`, `_component_state_to_dict`, `_component_state_from_dict`. If anything else is used by both halves, add it to the shared module.

### Task 3.2: Decide where `REPLAY_SCHEMA_VERSION` lives [Simple]

**Options (helpers go in `replay_serde_helpers.py` regardless):**
- **Option A:** Keep `REPLAY_SCHEMA_VERSION` in `replay_capture_serde.py`, import from `replay_outcome_serde.py` if needed. Simplest.
- **Option B:** Move `REPLAY_SCHEMA_VERSION` into `replay_serde_helpers.py` alongside the shared helpers. Cleanest if the constant logically belongs with the cross-cutting helpers.

- [ ] Pick Option B if `replay_serde_helpers.py` is already collecting cross-cutting concerns. Otherwise pick Option A.
- [ ] Document choice in `decisions.md`.

### Task 3.3: Enumerate all callers (direct AND package-root) [Simple]

Per audit feedback (Bucket D, response.md), the migration sweep MUST cover BOTH import forms:

```powershell
# Direct imports
rg -n "from game.simulation.replay.replay_serialization import" game/ tests/
rg -n "import game.simulation.replay.replay_serialization" game/ tests/

# Package-root imports (resolved via __init__.py re-exports)
rg -n "from game.simulation.replay import" game/ tests/
```

- [ ] Record the full caller list with the imported symbol(s) for each line. Known callers (from audit verification):
  - Direct form: `tests/integration/replay/*`, `tests/unit/simulation/replay/*`, `game/simulation/battle_runner.py`
  - Package-root form: `game/strategy/services/replay_store.py`, `game/strategy/services/replay_resolver.py`, `game/simulation/battle_runner.py`, `game/simulation/battle_controller.py`, `game/strategy/adapters/simulation_adapter.py`, `tests/integration/replay/*`, `tests/unit/strategy/services/test_replay_*.py`
- [ ] For each caller, classify which symbol(s) they import:
  - `battle_spec_*` / `boundary_*` / `modifier_stack_*` / `modifier_entry_*` → `replay_capture_serde`
  - `battle_outcome_*` / `compute_components_registry_hash` → `replay_outcome_serde`
  - `REPLAY_SCHEMA_VERSION` → per Task 3.2 decision
- [ ] Note which callers use the package-root form: those will keep working with a one-file update to `__init__.py` (Task 3.4). Direct-import callers need per-file rewrites (Task 3.8).

### Task 3.4: Create `replay_serde_helpers.py` (shared helpers) [Simple]

**File:** `game/simulation/replay/replay_serde_helpers.py` (new)

- [ ] Create the file with a module docstring describing the cross-cutting helper scope.
- [ ] Move `_vec_to_list`, `_list_to_vec` from `replay_serialization.py:78-85`.
- [ ] Move `_component_state_to_dict`, `_component_state_from_dict` from `replay_serialization.py:222-240`.
- [ ] If Option B chosen in Task 3.2: also move `REPLAY_SCHEMA_VERSION` here.
- [ ] Add `__all__` listing the public surface.
- [ ] Imports: minimal — `Vector2`, `ComponentStateSpec` (from `replay_spec.py`), `Dict`, `Any`, `List` from typing.

### Task 3.5: Create `replay_capture_serde.py` (spec-side) [Medium]

**File:** `game/simulation/replay/replay_capture_serde.py` (new)

- [ ] Move lines 1 through the spec/outcome boundary (re-derived in Task 3.0; was ~407 at original drafting, likely ~540-542 as of 2026-05-19) of `replay_serialization.py` into the new file, EXCEPT the shared helpers extracted in Task 3.4.
- [ ] Replace local references to `_vec_to_list` / `_list_to_vec` / `_component_state_to_dict` / `_component_state_from_dict` with imports from `replay_serde_helpers.py`.
- [ ] Update the module docstring to reflect the narrowed scope (spec-side serialization only).
- [ ] If Option A chosen in Task 3.2: keep `REPLAY_SCHEMA_VERSION` here at the top.
- [ ] Add `__all__` listing the public surface: `battle_spec_to_dict`, `battle_spec_from_dict`, `boundary_to_dict`, `boundary_from_dict`, `modifier_stack_to_dict`, `modifier_stack_from_dict`, `modifier_entry_to_dict`, `modifier_entry_from_dict`, plus `REPLAY_SCHEMA_VERSION` if Option A.
- [ ] Verify imports — drop any that are only used by the outcome-side code.

### Task 3.6: Create `replay_outcome_serde.py` (outcome-side) [Medium]

**File:** `game/simulation/replay/replay_outcome_serde.py` (new)

- [ ] Move lines from the spec/outcome boundary (re-derived in Task 3.0; was ~407 at original drafting, likely ~540-542 as of 2026-05-19) through EOF of `replay_serialization.py` into the new file (outcome-side serialization).
- [ ] Replace local references to `_vec_to_list` / `_list_to_vec` / `_component_state_to_dict` / `_component_state_from_dict` with imports from `replay_serde_helpers.py`.
- [ ] Add module docstring describing the outcome-side scope.
- [ ] If Option A chosen in Task 3.2 and `REPLAY_SCHEMA_VERSION` is needed here: `from game.simulation.replay.replay_capture_serde import REPLAY_SCHEMA_VERSION`. Otherwise leave the import out.
- [ ] Add `__all__` listing `battle_outcome_to_dict`, `battle_outcome_from_dict`, `compute_components_registry_hash`, and any helper exports.
- [ ] Verify imports.

### Task 3.7: Update `__init__.py` re-exports [Medium]

**File:** `game/simulation/replay/__init__.py`

- [ ] Replace the existing block (lines 33-45):

  ```python
  from game.simulation.replay.replay_serialization import (
      REPLAY_SCHEMA_VERSION,
      boundary_to_dict, boundary_from_dict,
      compute_components_registry_hash,
      modifier_entry_to_dict, modifier_entry_from_dict,
      modifier_stack_to_dict, modifier_stack_from_dict,
      battle_spec_to_dict, battle_spec_from_dict,
      battle_outcome_to_dict, battle_outcome_from_dict,
  )
  ```
  with imports that source each symbol from the correct new module:
  ```python
  from game.simulation.replay.replay_capture_serde import (
      REPLAY_SCHEMA_VERSION,    # or from replay_serde_helpers if Option B
      boundary_to_dict, boundary_from_dict,
      modifier_entry_to_dict, modifier_entry_from_dict,
      modifier_stack_to_dict, modifier_stack_from_dict,
      battle_spec_to_dict, battle_spec_from_dict,
  )
  from game.simulation.replay.replay_outcome_serde import (
      battle_outcome_to_dict, battle_outcome_from_dict,
      compute_components_registry_hash,
  )
  ```
- [ ] Keep `__all__` unchanged (the re-exported names are stable; only their source modules change).
- [ ] This single edit keeps ALL package-root callers (`from game.simulation.replay import ...`) working without per-file changes.

### Task 3.7b: Refresh `__init__.py` package docstring (lines 12-21) [Simple]

**File:** `game/simulation/replay/__init__.py:12-21`

**Why this task exists:** Added per Group 3 pre-execution review (codex consult + claude subagent independent review, 2026-05-19). The current package docstring at lines 12-21 says "serialization helpers — see `replay_serialization`" and "Phase 3 adds `replay_capture.py` which is the single hook." After Phase 3 lands, the first claim is FALSE (the module no longer exists; serialization lives in `replay_capture_serde.py` + `replay_outcome_serde.py` + `replay_serde_helpers.py`) and the second claim is WRONG-CONTEXT (`replay_capture.py` already existed pre-PROJ-460 as the runtime capture-sink hook; PROJ-460 Phase 3 does NOT add it). Leaving the docstring as-is leaves a newly-false header in a file Phase 3 already edits.

- [ ] Read the current docstring at `game/simulation/replay/__init__.py:12-21` to lock the exact text being replaced.
- [ ] Rewrite the Public API listing to reference the new module split:
  - Drop "serialization helpers — see ``replay_serialization``" line.
  - Add lines pointing at the three new modules: `replay_capture_serde` (spec-side serialization), `replay_outcome_serde` (outcome-side serialization), `replay_serde_helpers` (cross-cutting helpers).
  - Keep the `REPLAY_SCHEMA_VERSION`, `ReplaySpec`, `ReplayOutcome`, `ReplayRecord` lines (those classes/constants survive the split).
- [ ] Drop the trailing "Phase 3 adds `replay_capture.py` which is the single hook." sentence (it referred to a long-gone planning context and is now actively misleading; `replay_capture.py` already exists and is the runtime hook, not a new addition).
- [ ] Optionally add a one-line note that the package re-exports stable symbols from the three serde modules so package-root callers (`from game.simulation.replay import ...`) keep working.
- [ ] Verify: re-read the file to confirm the docstring now describes the current module set accurately.

**Notes:** This is a pure docstring touch — no code change, no import change, no behaviour change. Bundled with the Task 3.7 `__init__.py` edit because both touch the same file.

---

### Task 3.8: Migrate direct-import callers [Medium]

**Files:** all direct-import callers enumerated in Task 3.3.

- [ ] For each direct-import caller, rewrite the import to point at the new module:
  - `battle_spec_to_dict` / `battle_spec_from_dict` / `boundary_*` / `modifier_*` → `from game.simulation.replay.replay_capture_serde import ...`
  - `battle_outcome_to_dict` / `battle_outcome_from_dict` / `compute_components_registry_hash` → `from game.simulation.replay.replay_outcome_serde import ...`
  - `REPLAY_SCHEMA_VERSION` → per Task 3.2 decision (capture_serde OR helpers).
- [ ] Note: callers using the package-root form (`from game.simulation.replay import ...`) DO NOT need per-file changes; Task 3.7's `__init__.py` update handles them.
- [ ] Verify each caller still type-checks and tests pass.

### Task 3.9: Delete `replay_serialization.py` [Simple]

**File:** `game/simulation/replay/replay_serialization.py` (delete)

- [ ] Confirm all direct-import callers migrated:
  ```powershell
  rg -n "from game.simulation.replay.replay_serialization import" game/ tests/
  rg -n "import game.simulation.replay.replay_serialization" game/ tests/
  ```
  Both should return 0 results.
- [ ] Confirm `__init__.py` no longer imports from `replay_serialization`.
- [ ] Delete the file.
- [ ] Per CLAUDE.md: do NOT leave a re-export shim.

### Task 3.10: Verify replay capture + playback round-trips [Medium]

**Tests:**
```powershell
pytest tests/integration/replay/ tests/unit/simulation/replay/ -q -n 4
python Tools/test_sharded/test_sharded.py
```

- [ ] All replay tests green. The capture → save → load → verification round-trip is the highest-value gate.
- [ ] Sharded suite green; same count as baseline.

### Task 3.11: Verify LOC targets met [Simple]

- [ ] Re-measure (PowerShell):
  ```powershell
  (Get-Content game/simulation/replay/replay_capture_serde.py | Measure-Object -Line).Lines
  (Get-Content game/simulation/replay/replay_outcome_serde.py | Measure-Object -Line).Lines
  (Get-Content game/simulation/replay/replay_serde_helpers.py | Measure-Object -Line).Lines
  ```
- [ ] Target: `replay_capture_serde.py` ~310 LOC, `replay_outcome_serde.py` ~210 LOC, `replay_serde_helpers.py` ~30 LOC. All under 350 LOC.
- [ ] If any of the two serde halves is over: identify a sub-split candidate or document deferral.

### Task 3.12: Update findings + docs + commit [Simple]

**Files:**
- `Projects/active_projects/PROJ-460/findings/PROJ-460_findings.md`
- `docs/02_PATTERNS.md` (capture-vs-load split pattern)
- `docs/01_ARCHITECTURE.md` (simulation/replay/ listing)

- [ ] Update F-D-011 partial status in findings: "replay_serialization.py split into replay_capture_serde.py (~310 LOC) + replay_outcome_serde.py (~210 LOC) + replay_serde_helpers.py (~30 LOC); replay round-trip byte-identical; package-root callers still resolve via updated `__init__.py`."
- [ ] Add or extend the pattern entry in `docs/02_PATTERNS.md`: "Capture vs outcome serde split: when a serde module exceeds the ceiling and the spec/outcome halves share helpers, split into capture-side / outcome-side / shared-helpers modules (Option A). Avoid duplication; avoid leader-follower coupling between the halves."
- [ ] Update `docs/01_ARCHITECTURE.md` simulation/replay/ listing to include the three new modules.
- [ ] Commit message: `PROJ-460 Phase 3: split replay_serialization.py into replay_capture_serde + replay_outcome_serde + replay_serde_helpers (F-D-011 partial; all under 350 LOC)`
- [ ] Update `plan.md` Current State.

---

## Phase Completion Checklist
- [ ] replay_serde_helpers.py created (~30 LOC, shared helpers)
- [ ] replay_capture_serde.py created (~310 LOC, spec-side)
- [ ] replay_outcome_serde.py created (~210 LOC, outcome-side)
- [ ] replay_serialization.py deleted (no compat shim)
- [ ] `__init__.py` re-exports updated to source from the new modules
- [ ] Package docstring at `game/simulation/replay/__init__.py:12-21` updated to current module set (drops the stale `replay_serialization` reference + the wrong-context "Phase 3 adds `replay_capture.py`" sentence) — Task 3.7b
- [ ] All direct-import callers migrated; all package-root callers verified to still resolve
- [ ] Replay round-trip byte-identical (`pytest tests/integration/replay/`)
- [ ] Save-load round-trip preserved (`pytest tests/integration/save_load/`)
- [ ] Sharded suite green
- [ ] F-D-011 partial status updated in findings file
- [ ] Docs updated
