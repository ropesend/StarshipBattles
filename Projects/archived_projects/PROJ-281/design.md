# PROJ-281: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### What the legacy shim is

[BattleScreen.start(team0, team1)](../../../game/ui/screens/battle_screen.py) is the pre-PROJ-269 entry point: callers handed two teams of `Ship` objects directly, no spec involved. Tests built ships in fixtures and called `screen.start(team0, team1)`.

After PROJ-269/270 unified the entry contract on `BattleSpec`, production code migrated to `BattleScreen.start_battle(controller)` where `controller` is a running `BattleController` with a spec attached. But ~46 unit tests still use the old shim.

`BattleScreen._build_fallback_outcome` (~90 lines) exists ONLY to synthesize a minimal `BattleOutcome` for these tests, since the spec-in path is what populates the outcome normally.

### Why deletion over preservation

Per the user's [no bandaids policy](../../../C:/Users/rossr/.claude/projects/c--Dev-Starship-Battles/memory/feedback_no_bandaids.md) and the codebase's [System Migration Policy](../../../CLAUDE.md):
- Old systems should be eradicated, not preserved alongside new ones
- Backward-compat layers accumulate cruft and confuse readers
- 90 lines of fallback outcome assembly is real maintenance burden — every change to `BattleOutcome`/`ShipOutcome` shape risks breaking it silently
- Tests that exercise the legacy path don't exercise the production path — they're testing a code branch that production never hits

### What the migration looks like

Most of the ~46 callers probably want very simple specs: "one team, one ship per side; default boundary; no modifiers; tick-limit end condition; MINIMAL telemetry." A test helper that produces this from `Dict[int, List[Ship]]` makes the migration almost mechanical.

```python
# tests/helpers/battle_spec_helpers.py (NEW)

def make_minimal_spec(
    ships_by_team: Dict[int, List[Ship]],
    *,
    seed: int = 0,
    max_ticks: int = 1000,
) -> BattleSpec:
    """Builds a minimal BattleSpec for unit tests:
    - UnboundedRegion boundary
    - Empty ModifierStack
    - TickLimitCondition(max_ticks)
    - MINIMAL telemetry
    - Each team gets one TaskForce/Squadron containing all its ships
    - ShipSpec.instance_id = f"test:{team_id}:{i}"
    - position/angle/velocity from the ship object as-is (caller positions ships)
    """
```

Calls then become:
```python
# Before:
screen.start(team0_ships, team1_ships)

# After:
spec = make_minimal_spec({0: team0_ships, 1: team1_ships})
controller = BattleController(...)
controller.start_from_spec(spec, ai_factory=AIControllerFactory())
screen.start_battle(controller)
```

The 3-line wrapper could itself become a helper if it's the dominant pattern: `start_battle_from_ships(screen, ships_by_team)`.

## Architecture

### Before
```
Test → BattleScreen.start(team0, team1)
       → internally creates engine, runs sim
       → at end, _build_fallback_outcome() synthesizes a BattleOutcome
       → BattleResultsScreen consumes it
```

### After
```
Test → make_minimal_spec(ships_by_team)
       → BattleController.start_from_spec(spec)
       → BattleScreen.start_battle(controller)
       → engine runs sim (same path as production)
       → controller.get_outcome() returns real BattleOutcome
       → BattleResultsScreen consumes it
```

After migration, `BattleScreen` has exactly one `start_*` method. The fallback outcome builder is gone. The class is ~90 lines lighter and has no test-only branches.

## Key Patterns to Reuse
- **Spec-in contract** — established by PROJ-269/270, see [game/simulation/battle_runner.py](../../../game/simulation/battle_runner.py) for shape
- **Test helpers in `tests/helpers/`** — check existing helpers directory for conventions

## Dependencies & Risks
1. **Tests that depend on `_build_fallback_outcome`'s specific output shape** — if any test asserts on outcome details that the fallback synthesizes differently from `extract_outcome`, the migration changes their assertions. **Mitigation:** Phase 2 runs each migrated test individually and inspects diff
2. **Tests that bypass `BattleController` for performance reasons** — some tests might want to skip controller setup. **Mitigation:** if needed, helper offers a headless variant `make_minimal_spec_and_run(ships_by_team) -> BattleOutcome` that calls `run_battle` directly
3. **Test count discrepancy** — review estimated "~46" but actual could differ. **Mitigation:** Phase 1.2 audits exact count; if significantly higher, escalate to user before proceeding

## Opportunities Discovered
- A general-purpose `tests/helpers/battle_spec_helpers.py` could host other useful test-spec builders (e.g. `make_two_team_spec_with_modifiers(...)`) for future test work
- Once the shim is gone, `BattleScreen.__init__` and `start_battle` can probably tighten typing (no more `Optional[BattleController]`)

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
