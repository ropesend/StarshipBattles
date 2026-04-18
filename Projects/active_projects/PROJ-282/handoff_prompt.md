# Handoff: PROJ-282 — Phase 10 (user-led manual smoke)

**Status: Phases 1-9 are DONE.** All code + documentation work is complete.
The only remaining phase is user-led manual smoke testing (Phase 10),
which I cannot perform.

## What the previous session accomplished

In a single session, executed Phases 1-9 end-to-end:

- **Phase 1 (audit)** — 6 reports in `.agent_reports/PROJ-282-audit/`
- **Phase 2 (state)** — Added `system_complex_toggles`/`sector_complex_toggles` dicts to `BattleSetupSide`; fixed real N-team bug (hardcoded sides 0/1 in `_sync_complex_toggles_to_state`)
- **Phase 3 (ViewModel)** — Extracted `BattleSetupViewModel` (pure dataclass, 60 LOC)
- **Phase 4 (Renderer)** — Extracted `BattleSetupRenderer` + `panels/{left,center,right}_panel.py` (3 per-panel builders)
- **Phase 5 (InputHandler)** — Extracted `BattleSetupInputHandler` (26 tests)
- **Phase 6 (Controller)** — Extracted `BattleSetupController` with 15+ mutation methods (31 tests). Retargeted InputHandler from `screen._*` to `screen.controller.*` (4 new tests). **Fixed latent Phase 3 bug** (end-condition settings inside `@available_designs.setter`, resetting on every design scan).
- **Phase 7 (FleetHierarchyEditor)** — Extracted stateless helper owning TF/SQ CRUD + `_clone_ship` (11 tests). Killed the ship-cloning duplication between `duplicate_task_force` and `duplicate_squadron`.
- **Phase 8 (slim screen)** — Created `battle_setup/screen.py` (184 LOC thin shell) and `battle_setup/constants.py` (option tables). **Deleted old `battle_setup_screen.py`** (was 1172 LOC).
- **Phase 9 (docs)** — Added `§ 2.4 UI Screen Line Budget (PROJ-282)` to `docs/03_CONVENTIONS.md`. Cross-referenced from both MVVM exemplar screens' module docstrings.

Every phase passed `validate_phase.py PROJ-282 <N>`. Final PROJ-282-scope regression: **3545 tests green** (tests/unit/ui/ + tests/integration/ui/).

## What's left for the user / next agent

### Phase 10 — manual smoke (user-led)

Open `Projects/active_projects/PROJ-282/phase_10_checklist.md` for the
full scenario list. Tasks in brief:

1. **10.1 — Launch + render 2-side baseline** — game starts, panels display, resize works
2. **10.2 — Fleet/TF/SQ CRUD** — create/duplicate/delete operations flow correctly
3. **10.3 — 3-side setup** — ⚠️ **BLOCKED on missing UI.** See below.
4. **10.4 — 8-side max** — ⚠️ **BLOCKED on missing UI.** See below.
5. **10.5 — Complex toggles** — toggle → spec modifier_stack carries the effect
6. **10.6 — Save/load roundtrip** — including legacy `_complex_toggles` top-level key migration
7. **10.7 — Edge cases** — empty-side launch guard, large setup responsiveness

### ⚠️ Phase 10.3 + 10.4 have a gap

The Phase 1 audit [n_team_paths.md](.agent_reports/PROJ-282-audit/n_team_paths.md)
flagged that the **UI doesn't have Add Side / Remove Side buttons** — the
left panel's side dropdown is hardcoded to 2 entries. `BattleSetupState`
fully supports N=2..8 (PROJ-275, tested in `test_battle_setup_three_sides.py`),
and the spec compiler generates N-team specs correctly — but there's no
UI surface to drive it. PROJ-282's per-phase checklists never scheduled
"add Add-Side/Remove-Side buttons" as a task.

**User decision needed:**
- (a) Accept current 2-side UI for now; N-team setup via `BattleSetupState.add_side()` at the Python/save-file level
- (b) File a small follow-up project for N-team UI (would add buttons to `panels/left_panel.py` + `Controller.add_side/remove_side()` methods)
- (c) Block Phase 10 closure until (b) ships

### ⚠️ Small follow-up: 523-LOC controller

`controller.py` at 523 LOC exceeds the newly-documented 300 LOC convention
(from Phase 9). The convention explicitly treats this as a **review
signal**, not a blocker. If the user wants to cut it down: save/load +
battle-launch could split into a `LaunchController` sub-service (~100 LOC
removed). Optional polish — not required for Phase 10.

### ⚠️ Follow-up: property shim removal

The thin-shell `screen.py` (184 LOC) carries ~100 LOC of property shims
(`screen.active_side` → `view_model.active_side`, `screen.tick_limit` →
`controller.tick_limit`, etc.). They exist because panel renderers still
read state via `screen.*` paths. Dropping the shims requires updating
~10 read sites in `panels/{left,center}_panel.py` to go through
`screen.view_model.*` / `screen.controller.*` directly. Small, safe
follow-up — would bring `screen.py` under the 150 LOC target.

## If you're starting a new session to close Phase 10

Most of Phase 10 is manual clicking in the running game. But if the user
wants to add the Add-Side / Remove-Side UI (option b above), here's the
orientation:

### Orientation (read BEFORE touching the plan)

**Foundation:**
- `docs/README.md`, `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md` (especially § 2.4 added this project)
- `CLAUDE.md`

**Package tour (read all — they're each short):**
- `game/ui/screens/battle_setup/screen.py` (184 LOC — the thin shell)
- `game/ui/screens/battle_setup/view_model.py` (60 LOC)
- `game/ui/screens/battle_setup/renderer.py` + `panels/left_panel.py` (where Add/Remove Side buttons would live)
- `game/ui/screens/battle_setup/input_handler.py` (where button dispatch routes)
- `game/ui/screens/battle_setup/controller.py` — add `add_side()` / `remove_side()` methods delegating to `state.add_side()` / `state.remove_side(index)` (already exist on BattleSetupState)
- `game/ui/screens/battle_setup_state.py:177-207` — `add_side` + `remove_side` are there, tested
- `.agent_reports/PROJ-282-audit/n_team_paths.md` — the audit that flagged this gap + UX recommendations

**Tests to follow when extending:**
- `tests/unit/ui/screens/battle_setup/test_controller.py` — add `TestAddRemoveSide` class
- `tests/unit/ui/screens/battle_setup/test_input_handler.py` — add tests for new Add-Side / Remove-Side button dispatches
- `tests/integration/ui/test_battle_setup_three_sides.py` — existing; don't touch

### Project files

Read in order (after foundation + related code):
1. `Projects/active_projects/PROJ-282/design.md` — architectural rationale
2. `Projects/active_projects/PROJ-282/decisions.md` — 14 decisions logged across phases 2-7
3. `Projects/active_projects/PROJ-282/plan.md § Current State`
4. `Projects/active_projects/PROJ-282/manifest.md` — every file touched this project (30+ entries)
5. `Projects/active_projects/PROJ-282/phase_10_checklist.md`

### Protocol

Follow `Projects/protocols/03a_continue_working.md`. Phase 10 is the
terminal phase — after it closes, the project archives.
