# Review Scope: PROJ-378: galaxy cleanup test pattern update (post-PROJ-372 facade-delegate)

**Type:** code (delegated by Claude Code)
**Request ID:** req_20260507_042609_bb3683
**Review Mode:** Standard OpenCode review (inline analysis, 5 files)
**Parent:** None

## Scope

Commits in scope on branch `feat/03c-phase-aware-execution`:
- 9667eaa5a PROJ-378 phase 1: shared make_galaxy_stub fixture + migrate test_galaxy_cleanup.py
- 2611ce6e1 PROJ-378 phase 2: sweep test_empire + test_fleet_registration_lifecycle to make_galaxy_stub

Files reviewed:
- `tests/fixtures/galaxy_fixtures.py` (NEW, canonical impl)
- `tests/unit/strategy/data/conftest.py` (NEW, thin pytest fixture bridge)
- `tests/unit/strategy/data/test_galaxy_cleanup.py` (modified — 3 fixtures migrated)
- `tests/integration/strategy/test_empire.py` (modified — 5 sites migrated)
- `tests/integration/strategy/test_fleet_registration_lifecycle.py` (modified — 1 inline factory)

Reference docs read:
- `Projects/active_projects/PROJ-378/plan.md`
- `Projects/active_projects/PROJ-378/design.md`
- `Projects/active_projects/PROJ-378/decisions.md`
- `docs/02_PATTERNS.md` (Facade/Delegate §5, Fixture conventions)
- `docs/03_CONVENTIONS.md` (Test conventions §4)
- `tests/fixtures/README.md`
- `game/strategy/data/galaxy.py` (read-only reference)
- `game/strategy/data/galaxy_state.py` (read-only reference)
- `game/strategy/data/galaxy_spatial_index.py` (read-only reference)

## Instructions

1. Fixture correctness — does `make_galaxy_stub()` correctly construct a post-PROJ-372 Galaxy facade?
2. Migration correctness — verify each migrated fixture/call site preserves original test semantics.
3. Hidden coupling — MagicMock planet in `TestGalaxyGetAllFleetsInSystem`.
4. Layering / convention adherence — fixtures at `tests/fixtures/` + conftest bridge.
5. Completeness sweep — confirm zero `Galaxy.__new__(Galaxy)` or `patch.object(Galaxy, '__init__')` outside canonical.
6. Plan vs. implementation drift.
7. Pre-existing failure confirmation.

## Limitations

- Inline analysis only (5-file scope, well-bounded). No sub-agents needed.
- Did not run the sharded test suite; relied on plan self-reported green status.
- Production code (galaxy.py, galaxy_state.py, galaxy_spatial_index.py, galaxy_entity_registry.py) read for reference only — not reviewed for correctness.
