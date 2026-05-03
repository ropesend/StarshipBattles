# Size & Impact Estimator Report

## Summary
- Total dead code identified: ~4,900 LOC in Python files + 22.8MB __pycache__
- Total files to delete: ~30 Python files + 1,593 .pyc files
- Configuration files to update: 1 (pytest.ini)
- CI/CD references found: 0 (no CI/CD configuration exists)
- Documentation references to dead code: 0
- Overall risk level: **VERY LOW**

---

## Findings

### Major: Total Dead Code Impact

**ID:** IMPACT-001
**Issue:** Significant dead code accumulation across multiple categories
**Details:**

### Dead Code to Remove

| Category | Files | Lines | ~KB | Notes |
|----------|-------|-------|-----|-------|
| A: Legacy Migration Scripts | 10 | 904 | 56 | docs/_legacy_docs/Tools/ |
| B: Duplicate formatimg.py | 5 | 405 | 12 | assets/ShipThemes/ |
| D: Tools/ dead files | 8 | 1,671 | 70 | All except formation_editor |
| E: scripts/ dead files | 13 | 967 | 40 | One-time scripts |
| E: planet_qc/ subdirs | 4 | 327 | 15 | Batch processing utilities |
| I: Unused imports | 14 | 14 | <1 | Standard library imports |
| **Python Subtotal** | **54** | **4,288** | **~193** | |
| F: __pycache__ | 176 dirs | 1,593 .pyc | 22,800 | Git tracking only |
| **Grand Total** | **54 + 176 dirs** | **4,288 + 1,593 .pyc** | **~23,000** | |

### Structural Cleanup (Not Dead Code, But Cleanup)

| Item | Type | Action |
|------|------|--------|
| Tools/formation_editor.py | Duplicate (1,055 LOC) | Delete after import migration |
| tests/refactor/ | Misnamed directory | Rename to tests/regression/ |
| game/ui/hud/ | Empty directory | Delete |
| game/simulation/entities/mixins/ | Empty directory | Delete |
| tests/unit/builder/test_formation_editor_logic.py | Misplaced test | Move to tests/unit/ui/screens/ |

---

### Minor: Configuration References Found

**ID:** IMPACT-002
**Issue:** One configuration file references dead code paths

**pytest.ini:**
- Line 3: `--ignore=Tools` — prevents Tools/ from being collected as tests (harmless after deletion, but should be removed)
- Line 5: `pythonpath = . Tools` — adds Tools to Python path for formation_editor import. **MUST UPDATE** to `pythonpath = .` after Tools/ cleanup

**No references found in:**
- .gitignore (only general patterns like `__pycache__/`)
- conftest.py files (no sys.path manipulation for dead code)
- pyproject.toml / setup.cfg (don't exist)
- CLAUDE.md (references Projects/scripts, not scripts/)
- docs/*.md files (no specific references to dead code paths)
- .vscode/settings.json (no dead code references)

---

### Info: No CI/CD Configuration Exists

**ID:** IMPACT-003
**Issue:** No CI/CD to worry about
**Details:**
- No `.github/workflows/` directory
- No `Makefile`
- No deployment scripts
- No Docker configuration
- **Impact:** Zero CI/CD risk from deletions

---

### Info: Before/After Impact Estimates

**ID:** IMPACT-004

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Python files in dead code areas | 54 | 0 | -54 |
| Dead Python LOC | 4,288 | 0 | -4,288 |
| __pycache__ tracked in git | 176 dirs / 1,593 files | 0 | -1,769 items |
| Git repo size (tracked .pyc) | +22.8 MB | 0 | -22.8 MB |
| Unused imports in game/ | 14 | 0 | -14 |
| Tools/ directory files | 10 | 0 | Directory removed |
| scripts/ directory files | ~28 | 11 | -17 files |

---

## Risk Assessment

### Zero Risk Deletions (Phase 1)
- docs/_legacy_docs/Tools/ — completely isolated, no imports
- assets/ShipThemes/**/formatimg.py — standalone scripts, no imports
- __pycache__ untracking — standard git hygiene

### Low Risk Deletions (Phase 2)
- Tools/ dead files — confirmed zero imports from game/ or tests/
- scripts/ one-time scripts — confirmed zero imports
- planet_qc/ subdirectories — confirmed zero imports

### Low Risk Migrations (Phase 3)
- formation_editor.py consolidation — requires import updates
- pytest.ini update — simple config change
- test file relocation — pytest auto-discovers

### Trivial Cleanup (Phase 4)
- Unused imports — mechanical removal, zero behavior change
- Empty directories — pure clutter removal
- tests/refactor/ rename — no code changes

### Dynamic Loading Check
- **No dead code is dynamically loaded.** Searched for `importlib`, `__import__`, and string-based module references — none reference dead code paths.

### Runtime Reference Check
- **No runtime code references dead paths.** No string literals containing dead code file paths found in game/ code.

---

## Recommended Execution Order

**Phase 1: Zero-Risk Deletes** (~10 minutes)
1. Delete docs/_legacy_docs/Tools/ (10 files)
2. Delete 5 formatimg.py files
3. `git rm -r --cached **/__pycache__`

**Phase 2: Script & Tool Cleanup** (~20 minutes)
1. Delete 8 dead Tools/ files
2. Delete Tools/__init__.py
3. Delete 13 dead scripts/ files
4. Delete planet_qc/ and planet_qc_v2/ directories

**Phase 3: Formation Editor Migration** (~30 minutes)
1. Delete Tools/formation_editor.py
2. Update game/app.py import
3. Move test_formation_editor_logic.py
4. Update pytest.ini pythonpath
5. Remove `--ignore=Tools` from pytest.ini
6. Delete Tools/ directory entirely

**Phase 4: Polish** (~15 minutes)
1. Remove 14 unused imports across 10 files
2. Rename tests/refactor/ → merge into tests/regression/
3. Delete empty directories (game/ui/hud/, game/simulation/entities/mixins/)

**Total estimated effort: ~75 minutes**

---

## Top 5 Priority Issues

1. **IMPACT-001** — 4,288 LOC of dead Python code across 54 files
2. **IMPACT-001** — 22.8MB of __pycache__ tracked in git (biggest size impact)
3. **IMPACT-002** — pytest.ini needs updating after Tools/ cleanup
4. **IMPACT-004** — scripts/ directory can be reduced from ~28 to 11 files
5. **IMPACT-003** — No CI/CD risk — safe to proceed with all deletions
