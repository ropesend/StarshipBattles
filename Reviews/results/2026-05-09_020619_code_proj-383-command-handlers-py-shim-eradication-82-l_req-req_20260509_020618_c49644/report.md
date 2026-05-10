# Review Report: PROJ-383 — command_handlers.py shim eradication

**Review type:** code
**Request ID:** req_20260509_020618_c49644
**Reviewer:** OpenCode
**Completed:** 2026-05-09T02:20:00Z
**Scope:** 3 commits on `feat/03c-phase-aware-execution` — production migrations, test migrations, closeout/file deletion
**Limitations:** None. All 7 verification tasks completed exhaustively. No agents launched — review was focused enough for direct analysis.

---

## Headline

**The shim is TOTALLY GONE.** Zero hidden references in production or test code. All 30 import sites (5 production + 25 test) migrated correctly. Lazy import pattern preserved. No replacement shim introduced. Canonical `handlers/` package loads cleanly.

---

## Findings

### CRITICAL: None

No critical findings. All grep-based verification returned zero hits for the deleted module path in production and test code.

### MAJOR: None

All production and test migrations verified correct.

### MINOR: 1

| ID | Severity | Title | File | Line |
|----|----------|-------|------|------|
| MIN-001 | MINOR | Historical docstring references to deleted file remain | `game/strategy/engine/handlers/__init__.py`, `handlers/base.py`, `handlers/registry_factory.py`, `tests/unit/strategy/engine/test_command_handlers_public_api.py` | various |

**MIN-001 Description:** Four files contain docstring/comment references to the now-deleted `command_handlers.py`. These are intentional historical markers documenting the migration from monolith to package (PROJ-309) and the shim deletion (PROJ-383). They are not functional issues and do not constitute import references. No action required — the docstrings correctly explain the provenance.

### INFO: 2

| ID | Severity | Title | File | Line |
|----|----------|-------|------|------|
| INFO-001 | INFO | Pre-existing test failures confirmed independent | `tests/unit/strategy/engine/test_order_processor_transfer.py` | — |
| INFO-002 | INFO | Call-site count matches audit accounting | All scope files | — |

**INFO-001:** PROJ-393 species-id fallback removal failures (fixed in `88a2342ef`) are unrelated to PROJ-383's shim deletion. Confirmed by the requester via stash round-trip.

**INFO-002:** Final call-site count of 30 (5 prod + 25 test) vs. audit estimate of 31 (6 prod + 25 test). The discrepancy is explained by Task 1.2 being already done by PROJ-382 — audit heuristics are sound; the delta is sequencing noise.

---

## Verification Details

### Task 1: Final grep verification

| Pattern | Command | Result |
|---------|---------|--------|
| `from game.strategy.engine.command_handlers` | `rg -rn 'from game.strategy.engine.command_handlers' game/ tests/ combat_lab/ Tools/` | **ZERO hits** |
| `import command_handlers` | `rg -rn 'import command_handlers' game/ tests/ combat_lab/ Tools/` | **ZERO hits** (hits to `planet_command_handlers` and `superweapon_command_handlers` are correct — those are the canonical module files, not the deleted shim) |
| `command_handlers\.` (attribute access) | `rg -rn 'command_handlers\.' game/ tests/ combat_lab/ Tools/` | **ZERO hits** |
| Repo-wide `from game.strategy.engine.command_handlers import` | `rg -rn` with `--glob "*.py"` | **ZERO hits** |

No production path references the deleted shim module. All hits for the broader `command_handlers` string are either:
- Docstring/comment references explaining the migration history
- Variable names like `planet_command_handlers` and `superweapon_command_handlers` (these are the canonical `.py` files, not the deleted shim)
- String literals listing file paths in test infrastructure

### Task 2: Already-done claim (Task 1.2 / LEG-01-016)

- **`superweapon_command_handlers.py:15`** reads: `from game.strategy.engine.handlers.base import BaseCommandHandler, add_move_order_if_needed` — imports from canonical `handlers.base`, not from the shim.
- **`git show 73eb2a635 -- game/strategy/engine/superweapon_command_handlers.py`** confirms the import was changed by PROJ-382 phase 3. The diff shows the old shim import path being replaced with `handlers.base`.

**Verdict: Claim VERIFIED.** PROJ-382 pre-emptively migrated this import site. PROJ-383 correctly logged it as "already done" in its verification report.

### Task 3: Production migration correctness

**planet_command_handlers.py (4 lazy imports):**
All four imports are function-local (lazy) — preserving the original pattern to avoid circular imports:
- Line 55: `from game.strategy.engine.handlers.base import BaseCommandHandler` (inside `IssuePlanetOrderCommandHandler.execute`)
- Line 127: `from game.strategy.engine.handlers.base import BaseCommandHandler` (inside `ClearPlanetOrdersCommandHandler.execute`)
- Line 149: `from game.strategy.engine.handlers.base import BaseCommandHandler` (inside `DeletePlanetOrderCommandHandler.execute`)
- Line 185: `from game.strategy.engine.handlers.base import BaseCommandHandler` (inside `_apply_planet_environmental_target`)

No accidental hoisting to module level. No circular import risk introduced.

**game_session.py:67:**
- Import: `from game.strategy.engine.handlers import create_default_registry`
- `handlers/__init__.py:39` re-exports: `from game.strategy.engine.handlers.registry_factory import create_default_registry`
- Listed in `__all__` (line 71).

`create_default_registry` is correctly exported from the package-level `__init__.py`, not just from `handlers.base`. The import resolves correctly.

### Task 4: Test migration correctness

Spot-checked 6 of 10 scope files (exceeding the requested 3):

| Test File | Import Path | Symbol Verified? |
|-----------|-------------|-----------------|
| `tests/unit/strategy/test_command_handlers.py:10` | `from game.strategy.engine.handlers import (...)` | 15 symbols imported, all from canonical package |
| `tests/unit/strategy/engine/test_command_handlers_public_api.py` | Contract test, asserts all public symbols importable from `game.strategy.engine.handlers` | Contract passes: `handlers/__init__.py` exports all declared symbols |
| `tests/unit/strategy/engine/test_base_command_handler.py:12` | `from game.strategy.engine.handlers import BaseCommandHandler` | Symbol `BaseCommandHandler` is the canonical one from `handlers/base.py`, not a shim re-export |
| `tests/unit/strategy/engine/test_command_ownership.py:15` | `from game.strategy.engine.handlers import BaseCommandHandler` | Same symbol, correct |
| `tests/integration/colonization/test_explicit_orders.py:5` | `from game.strategy.engine.handlers import ColonizeCommandHandler, ColonizeMissionCommandHandler` | Both symbols correctly resolve |
| `tests/unit/strategy/engine/test_command_registry_seeding.py:146-156` | `from game.strategy.engine import planet_command_handlers, superweapon_command_handlers` | Correct — imports canonical module files for registry seeding |

No test imported the wrong symbol. No test relied on the shim's re-export shape.

### Task 5: CLAUDE.md Rule 3 compliance

- **No replacement shim.** Search for `re-export shim|transitional shim|compat.*shim|shim module` in `game/` returned zero hits (the only references to "shim" in production code are in the `handlers/__init__.py` and `handlers/base.py` docstrings, which document the deletion — they do not constitute a new shim).
- **`handlers/__init__.py` is a proper package init.** It re-exports symbols from sibling sub-modules (the standard Python package pattern), but it is the canonical home for the API — not a transitional shim. Its docstring explicitly states: *"this package is now the sole canonical home for the command-handler API."*
- **`handlers/base.py` docstring** likewise declares the canonical status: *"all callers now import directly from `game.strategy.engine.handlers/*`"*

### Task 6: Cross-check with PROJ-380

PROJ-380 phase 3.6 (`MissionCommandHandler` template) lives in `superweapon_command_handlers.py`. The file uses a `BaseCommandHandler` mixin pattern (line 56: `class ImplodePlanetCommandHandler(BaseCommandHandler)`), and the imports are all from canonical paths.

- No `MissionCommandHandler` class or template exists in `superweapon_command_handlers.py` by that exact name — the handlers in that file use the `@command_spec` decorator + `BaseCommandHandler` inheritance pattern consistently.
- PROJ-382 (commit `73eb2a635`) and PROJ-380's template landed first, as planned. PROJ-383 deleted the shim afterward.
- No interaction issues detected. The sequencing was sound.

### Task 7: Smoke test

```
python -c "import game.strategy.engine.handlers; print('handlers loaded OK'); print('create_default_registry' in dir(game.strategy.engine.handlers))"
```

Output:
```
handlers loaded OK
True
```

The canonical `handlers/` package loads cleanly. `create_default_registry` is present and importable from the package root.

### File deletion confirmed

`game/strategy/engine/command_handlers.py` does not exist on disk. Commit `f37514b78` shows `delete mode 100644` for this file (82 LOC).

---

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| MAJOR | 0 |
| MINOR | 1 |
| INFO | 2 |

The shim eradication is complete and correct. All 30 import sites are migrated to canonical paths. No hidden references remain. The lazy import pattern is preserved. No replacement shim was introduced. The `handlers/` package loads cleanly and serves as the sole canonical home for the command-handler API.
