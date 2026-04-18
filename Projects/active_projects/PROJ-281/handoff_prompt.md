# Handoff: PROJ-281 — Phase 2 Tasks 2.2-2.5 (47-caller migration)

Resume **PROJ-281** at **Phase 2, Task 2.2**. The previous session ended at
~80% context after completing Phase 2 Task 2.1 (the module-level migration
helper). Tasks 2.2-2.5 (the actual 47-caller migration) are the bulk of
Phase 2 and were intentionally deferred to this fresh session.

## Orientation (read BEFORE touching the project plan)

The instinct is to open `plan.md` first. **Resist it.** The Phase 2
checklist's migration pattern assumes you understand the spec-based battle
flow (PROJ-269/270 unified entry), the Battle Setup→BattleController
contract, and the test-fixture patterns this codebase uses. Without that
orientation you'll make call-site replacements that are mechanically
correct but semantically wrong (the previous session already discovered
that some tests query `scene.ships` directly — call-site replacement alone
breaks them).

Prefer loading extra context. Err on the side of reading the file.

### 1. Foundation docs (always read these first)

- `docs/README.md` — doc index
- `docs/01_ARCHITECTURE.md` — layer structure, `game.simulation` + `game.ui.screens` packages, BattleSpec/BattleOutcome DTOs
- `docs/02_PATTERNS.md` — spec compiler pattern, BattleController wrapper pattern
- `docs/03_CONVENTIONS.md` — test file layout, pytest fixture conventions
- `CLAUDE.md` at project root — **non-negotiable** project instructions (Rule 1 TDD, Rule 2 docs, Rule 3 clean-sheet design)

### 2. Task-specific docs

- `docs/systems/combat_simulation.md` § "Battle Orchestration" — how `run_battle(spec)` and `BattleController.start_from_spec(spec)` relate. The migration swaps `BattleScreen.start(team0, team1)` for the controller path, so you need to understand what the controller path actually does.
- `docs/systems/combat_simulation.md` § "Unified Entry (PROJ-269 + PROJ-270)" — the history of why the legacy shim exists and what replaced it.

### 3. Related code (read for understanding, even if you won't modify it)

- `tests/fixtures/battle.py` — **READ IN FULL** (~200 lines). Defines both `make_minimal_spec` and `start_battle_screen_with_minimal_spec`. The second is the helper you'll use 47 times. Its docstring encodes the migration contract: ship identity is preserved, config kwargs mirror the legacy shim, returns the `BattleController`. Do NOT re-invent this helper per-file.
- `tests/fixtures/test_make_minimal_spec.py` — **READ IN FULL.** 23 tests demonstrate the helper's invariants. Your migrations' assertions should respect these invariants.
- `tests/integration/test_make_minimal_spec_smoke.py` — 2 tests showing the helper feeding both `BattleController.start_from_spec` (visual-mode) and `run_battle(spec)` (headless). Tells you when to use which.
- `game/ui/screens/battle_screen.py` lines 220-260 — the CURRENT legacy `BattleScreen.start(team0_ships, team1_ships, ...)` method. Read so you understand what's being replaced. Lines 220-500 include `_build_fallback_outcome` — don't touch it yet (Phase 3's job).
- `game/simulation/battle_controller.py::start_from_spec` (line ~245) — what the helper actually invokes internally.
- `game/simulation/battle_runner.py::materialize_spec_ships` + `run_battle` — the headless path.
- `game/simulation/battle_spec.py` — the ShipSpec/TeamSpec/BattleSpec frozen dataclasses the helper constructs.
- `tests/fixtures/ships.py::create_test_ship` — the ship factory the helper's ship_builder returns.

### 4. Related tests (read so you know what "working" looks like)

Target files (will be modified):
- `tests/unit/ui/screens/test_battle_setup_logic.py` — **Task 2.4 target** (3 callers at lines 78, 100, 104). **START HERE** — smallest file, validates the pattern end-to-end.
- `tests/unit/ui/test_battle_screen.py` — **Task 2.2 target** (7 callers at lines 57, 67, 83, 93, 117, 137, 149). Medium.
- `tests/unit/ui/test_battle_screen_simulation.py` — **Task 2.3 target** (37 callers — bulk of the work).

Read the target files IN FULL before migrating each. Some tests assert
on post-start state (`scene.ships`, `scene.ai_controllers`, `scene.projectiles`)
that lives on the controller's engine after migration, NOT on the screen
directly. These tests need assertion reshaping, not just call-site
replacement.

Also read (for context, not modification):
- `tests/fixtures/README.md` — how `tests/fixtures/` is organised
- `tests/unit/simulation/test_unified_entry_guard.py` around line 565 — guard test that documents the shim's retention. Phase 3 will flip this; don't touch during Phase 2.

## Only now: read the project files

Read in this order — the plan depends on all of the above:

1. `Projects/active_projects/PROJ-281/design.md` — architectural rationale
2. `Projects/active_projects/PROJ-281/decisions.md` — decision log
3. `Projects/active_projects/PROJ-281/plan.md` § **Current State** — authoritative handoff from previous session (updated 2026-04-18)
4. `Projects/active_projects/PROJ-281/phase_2_checklist.md` — task list for Phase 2. Task 2.1 is complete (check the notes for helper details). Tasks 2.2, 2.3, 2.4, 2.5 are what you'll do.
5. `Projects/active_projects/PROJ-281/manifest.md` — full file manifest with Phase 2/3/4 targets annotated

## First action

Literal next checklist item from `phase_2_checklist.md`:

> **Task 2.4: Migrate `tests/unit/ui/screens/test_battle_setup_logic.py` [Simple]**
> - [ ] Read the full file
> - [ ] Migrate 3 callers using the canonical pattern
> - [ ] Run `pytest tests/unit/ui/screens/test_battle_setup_logic.py` — all pass
> - [ ] Grep verify zero remaining callers

Migration pattern (using the helper shipped in Phase 2.1):

```python
# Before:
scene.start([ship1], [ship2], headless=True)

# After:
from tests.fixtures.battle import start_battle_screen_with_minimal_spec
controller = start_battle_screen_with_minimal_spec(
    scene, {0: [ship1], 1: [ship2]}, headless=True,
)
```

**Suggested order: 2.4 → 2.2 → 2.3 → 2.5**. The checklist lists them
2.2 → 2.3 → 2.4 → 2.5, but starting with the smallest file (2.4, 3 callers)
validates the pattern end-to-end before you commit to 37 edits in Task 2.3.

## Watchouts (from the previous session)

- **Assertion reshape required, not just call-site replacement.**
  `test_battle_setup_logic.py::test_battle_scene_start_assignment` asserts
  on `scene.ships`, `scene.ai_controllers`, and AI enemy_team_ids. After
  migration these live on `controller.service.get_engine()`. Your helper
  call returns the controller — use it: `engine = controller.service.get_engine()`.

- **`test_battle_scene_clear_state` is a shim-specific test.** It tests
  that calling `.start()` twice on the same screen clears previous state.
  Under the spec-based path, each battle creates a fresh controller — the
  "double-start clearing" contract doesn't map cleanly. **Recommendation:
  delete this test** (its behavior is migrating away). Escalate to the
  user if ambiguous — don't silently rewrite to test something else.

- **`headless=True` callers in `test_battle_screen_simulation.py`:**
  these tests may care only about the outcome, not the live-visual-mode
  lifecycle. Consider using headless `run_battle(spec, ship_builder=...)`
  directly instead of `start_battle_screen_with_minimal_spec(...)` for
  those — simpler, fewer moving parts, no controller dangling.

- **`BattleConfig` kwargs carry forward:** the helper passes
  `headless`/`start_paused`/`seed` into a `BattleConfig`. If any test
  uses `test_mode=True` (a legacy arg the shim accepted), it doesn't map
  1:1 — read `BattleScreen.start`'s current code around line 250 to see
  what `test_mode` did and decide whether the migration needs to preserve
  that semantic (hint: it sets `ReturnDestination.TEST_LAB`, which lives
  in `BattleConfig.return_destination`).

- **Pre-existing baseline concern** (noted in PROJ-279 / PROJ-280 memos):
  `tests/unit/strategy/data/` has ~78 unrelated pre-existing failures
  (`TypeError: cannot unpack non-iterable ValidationResult object`).
  These are NOT yours to fix. Confine regression checks to
  `tests/unit/ui/`, `tests/unit/test_lab/`, `tests/unit/combat_lab/`,
  `tests/unit/simulation/`, `tests/fixtures/`, `tests/integration/`.

- **`validate_phase.py` FAIL at mid-phase is expected.** The protocol
  update clarifies this: distinguish structural-FAIL (you claimed
  completion that isn't real) from mid-phase-FAIL (you finished some
  tasks and stopped cleanly). See 03a_continue_working.md §
  "Interpreting the result".

## Protocol

Follow `Projects/protocols/03a_continue_working.md` (recently updated
with mid-phase FAIL interpretation + stronger handoff requirements).
Check context at natural handoff points via
`python Tools/check_context/check_context.py`.
