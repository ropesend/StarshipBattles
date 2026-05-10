# Phase 4: Migrate Remaining Hardcoded Paths

## Goal
Fix all remaining hardcoded paths that don't fall into the data/ or assets/ categories.

## Files to Migrate

### Formation Editor
- [ ] `game/ui/screens/formation_editor.py:738` — `os.path.join(base_path, "data", "formations")` → `Paths.FORMATIONS_DIR`
- [ ] `game/ui/screens/formation_editor.py:757` — same pattern → `Paths.FORMATIONS_DIR`
  - [ ] Write test
  - [ ] Update both lines
  - [ ] Run tests

### Setup Screen (battles directory)
- [ ] `game/ui/screens/setup_screen.py:110` — `os.path.join(base_path, "data", "battles")` → `Paths.BATTLES_DIR`
- [ ] `game/ui/screens/setup_screen.py:130` — same pattern → `Paths.BATTLES_DIR`
  - [ ] Write test
  - [ ] Update both lines
  - [ ] Run tests

### QA Observer (Tools/)
- [ ] `Tools/qa_observer/observer.py:223` — `project_root / "output" / "logs"` → `Path(Paths.LOGS_DIR)`
  - [ ] Update code
  - [ ] Verify observer still works

### Test Lab Data Extractor
- [ ] `game/ui/screens/test_lab/data_extractor.py:32` — `os.path.join(project_root, 'simulation_tests', 'data')` — evaluate whether this needs a `Paths` constant or is test-specific infrastructure
  - [ ] Decide: add `Paths.SIMULATION_TESTS_DATA_DIR` or leave as-is
  - [ ] If adding, update code and run tests

## Verify
- [ ] Run full test suite
- [ ] Grep for common hardcode patterns: `"data/"`, `"assets/"`, `"ships/"`, `"output/"`, `os.path.join(base_path,` in `game/` and `Tools/`
- [ ] Confirm zero remaining hardcoded production paths (excluding tests, scripts with CLI args, docstrings)
