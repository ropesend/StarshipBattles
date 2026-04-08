# Phase 5: Verification & Documentation

## Goal
Confirm all paths are centralized, update documentation, run full test suite.

## Final Audit
- [ ] Grep `game/` for `os.path.join(.*"data"` — should find zero non-Paths hits
- [ ] Grep `game/` for `os.path.join(.*"assets"` — should find zero non-Paths hits
- [ ] Grep `game/` for `os.path.join(.*"ships"` — should find zero non-Paths hits
- [ ] Grep `game/` for `os.path.join(.*"output"` — should find zero non-Paths hits
- [ ] Grep `game/` for `"data/` string literals used as paths — zero hits
- [ ] Grep `Tools/` for hardcoded paths — zero hits (excluding CLI arg defaults in scripts/)

## Documentation Updates
- [ ] Review `docs/01_ARCHITECTURE.md` — update if directory structure section mentions `ships/` at root
- [ ] Review `docs/03_CONVENTIONS.md` — add convention: "All file paths must use `Paths` constants from `game/core/paths.py`"
- [ ] Review `game/core/paths.py` module docstring — update usage examples with new constants
- [ ] Verify `Paths` class docstring lists all constant categories

## Test Suite
- [ ] Run full test suite: `python scripts/test_sharded.py`
- [ ] Confirm test count is >= 14691 (no tests lost)
- [ ] Confirm 0 failures

## Cleanup
- [ ] Verify `ships/` directory no longer exists at project root
- [ ] Verify `output/ships/` contains the moved design files
- [ ] Update `.gitignore` if any entries reference `ships/` at root
