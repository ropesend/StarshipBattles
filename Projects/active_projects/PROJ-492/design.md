# PROJ-492 Design

## Background

PROJ-479 Phase 6 (HLP helper consolidation) completed 4 of 6 cluster items but deferred:
- Task 6.2 — 12+ nested `MockPlanetType` copies (canonical fixture in place; nested call sites remain)
- Task 6.4 — full 43-file `_make_fleet` sweep (canonical `_make_mock_fleet` in place; signature variation needs per-site triage)
- Task 6.5 — `setup_tmpdir` consolidation (chdir-vs-Paths-patching strategy decision needed before consolidating)

## Approach

Three phases, executable independently. Phase 3 contains a strategy decision but does NOT block Phases 1 or 2.

### Phase 1 — HLP-002 nested MockPlanetType migration
The canonical `MockPlanetType` Enum exists at `tests/fixtures/colonization_fixtures.py`. Migration is purely mechanical:
- `class MockPlanetType(Enum): CONTINENTAL = "continental"; ...` → `from tests.fixtures.colonization_fixtures import MockPlanetType`.

Risk: enum member name drift. If a nested copy uses an enum member not in the canonical (e.g. a per-test `EXOTIC` member), extend the canonical Enum first, then migrate.

### Phase 2 — HLP-004 _make_fleet sweep
The canonical `_make_mock_fleet` exists at `tests/conftest.py`. The blocker is signature variation across ~40 call sites. Approach:

1. **Triage pass:** open each file, compare its local `_make_fleet` signature to the canonical. Categorize:
   - **A — identical signature:** delete local, import canonical. Trivial.
   - **B — superset signature (canonical has extra optional kwargs):** delete local, import canonical. Tests pass unchanged.
   - **C — divergent signature (local uses different param names or different defaults):** rewrite test call sites to match canonical signature, then delete local.
   - **D — semantically different (local builds a different kind of fleet):** rename local to `_make_<purpose>_fleet`, document intent. Do NOT force-merge.

2. **Sequence:** start with category A (lowest risk), proceed through B, C; defer D files to per-site decision.

### Phase 3 — HLP-005 setup_tmpdir
**Strategy decision (per Codex consult evidence):** standardize on patching `Paths.SAVES_DIR`.

Rationale (`AgentCoordination/Scratchpad/Consult/20260523T125621Z_plan-PROJ-479-followthrough/response.md`):
- Production code uses `os.path.join(Paths.SAVES_DIR, save_name)` when `game_session.save_path` is absent (`game/strategy/systems/save_game_service.py:107-121`).
- Canonical fixture `setup_tmpdir` is at `tests/unit/strategy/save_game_service/conftest.py:48` (note: PROJ-479 phase_6_checklist cited line 42; current location is :48 — refresh on entry).
- `Paths.SAVES_DIR` is an absolute repo-root-derived path (`game/core/paths.py:46-60`).
- `tests/unit/ui/test_save_selection.py` already follows this contract by patching `Paths.SAVES_DIR` (`tests/unit/ui/test_save_selection.py:21-33`).
- Only `test_auto_save.py` uses `chdir` (`tests/unit/strategy/test_auto_save.py:26-33`) — out of step with production contract.

Implementation:
1. Rewrite `test_auto_save.py` harness to:
   - Stop using `os.chdir(tmpdir)`.
   - Patch `Paths.SAVES_DIR` to `tmpdir`.
   - Assert through returned `save_path` and created files (not cwd-relative paths).
2. Verify the canonical `setup_tmpdir` fixture at `tests/unit/strategy/save_game_service/conftest.py:42` covers `test_auto_save.py`'s needs. Extend if not.
3. Delete `test_auto_save.py`'s local tmpdir setup; import canonical.

## Why standardize on Paths.SAVES_DIR (not dual-mode)

The Codex consult considered a dual-mode fixture (chdir OR Paths.SAVES_DIR via parameter) and rejected it absent evidence the cwd contract serves a real need. Production callers all go through `Paths.SAVES_DIR`. Maintaining two harnesses doubles the maintenance surface for no observable benefit.

If a future test genuinely needs cwd-relative save behavior for a non-production caller, the dual-mode fixture can be added at that time with an explanatory note.

## Risks

- **Risk:** Some `_make_fleet` Category-D files build fundamentally different fleet structures (e.g. fleets-with-cargo-state for cargo tests, fleets-with-orders for order tests).
  **Mitigation:** rename rather than force-merge. The DRY win isn't worth obscuring intent.

- **Risk:** Migrating `test_auto_save.py` to Paths.SAVES_DIR may surface latent file-lock flakes (PROJ-479 Phase 6 Task 6.1 notes a pre-existing xdist file-lock flake on `output/saves/AutoSaveTest`).
  **Mitigation:** ensure the canonical fixture uses a unique tmpdir per test (already does, per pytest tmpdir contract). If flake persists after migration, it's the same pre-existing issue, not caused by this project.

- **Risk:** Some `MockPlanetType` consumers may have enum-member-name typos relative to the canonical (`ICE_DWARF` vs `IceDwarf`).
  **Mitigation:** grep for usages in each file before deleting the local definition; rename usages to canonical member names.

## Source evidence

- Codex consult response: `AgentCoordination/Scratchpad/Consult/20260523T125621Z_plan-PROJ-479-followthrough/response.md` (sections 4 and 6)
- PROJ-479 Phase 6 checklist: `Projects/active_projects/PROJ-479/phase_6_checklist.md:11-13,34-35,50-58`
- Production save path: `game/strategy/systems/save_game_service.py:107-121`
- Paths constant: `game/core/paths.py:46-60`
