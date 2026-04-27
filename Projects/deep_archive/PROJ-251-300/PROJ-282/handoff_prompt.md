# Handoff: PROJ-282 — Phase 10 (user-led manual smoke)

**Status: Phases 1-9 + 11 are DONE** — all code + documentation work
complete. The only remaining phase is Phase 10 (user-led manual smoke)
which I cannot perform.

**What shipped this session (Phase 11, added post-hoc):** N-Side UI support.
`BattleSetupController.add_side()` / `remove_side(index)` methods with MIN/MAX
(2..8) bounds handling + view-model reconciliation; Add-Side / Remove-Side
buttons on the left panel with auto-disable at bounds; side dropdown populates
dynamically from `len(state.sides)` (drops hardcoded 2-entry + "(Left)"/"(Right)"
cosmetic suffixes); InputHandler dispatches the new buttons + parses `"Side N"`
format with malformed-input fallback. 16 new tests. 3561 tests green in
PROJ-282 scope.

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

## What's left

### Phase 10 — manual smoke (user-led)

Open `Projects/active_projects/PROJ-282/phase_10_checklist.md` for the
full scenario list:

1. **10.1** — Launch + render 2-side baseline
2. **10.2** — Fleet/TF/SQ CRUD (create/duplicate/delete)
3. **10.3** — 3-side setup (click "Add Side" to create 3rd side, add fleets/ships, launch)
4. **10.4** — 8-side max (click "Add Side" 6 times, verify disable at 8; click Remove)
5. **10.5** — Complex toggles + spec modifier_stack flow
6. **10.6** — Save/load roundtrip (including legacy `_complex_toggles` top-level key migration)
7. **10.7** — Edge cases (empty-side launch guard, large setup responsiveness)

All scenarios are now unblocked (Phase 11 shipped the N-side UI).

### Other known follow-ups (non-blocking)

**`controller.py` at 523 LOC** exceeds § 2.4's 300-LOC target. The
convention explicitly treats this as a **review signal**, not a blocker.
Natural split if desired: save/load + battle-launch into a
`LaunchController` sub-service (~100 LOC removed).

**`screen.py` property shims (~100 LOC)** keep `screen.py` at 184 LOC
(over the 150 target). Dropping them requires updating ~10 read sites in
`panels/{left,center}_panel.py` to go through `screen.view_model.*` /
`screen.controller.*` directly. Small, safe follow-up.

## If smoke finds defects

File as follow-up issues. Unless critical, don't block project closure
on them — after Phase 10 passes, PROJ-282 archives with the follow-up
backlog documented in [decisions.md](decisions.md).

**Known acceptable budget variances** (documented in [phase_8_checklist.md](phase_8_checklist.md) § 8.4):
- `game/ui/screens/battle_setup/controller.py` at 523 LOC exceeds the ≤300 convention — treated as a soft review signal per § 2.4
- `game/ui/screens/battle_setup/screen.py` at 184 LOC slightly over the 150 target — pure property-shim wiring

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
