# Phase 4: Tooling & Hygiene

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-297 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Two small hygiene fixes: replace 2 bare `except:` clauses with `except Exception:`, and add `radon` + `vulture` to dev dependencies for ongoing complexity/dead-code scans.

---

## Tasks

### Task 4.1: Replace bare `except:` in `Reviews/scripts/calculate_agents.py` [Simple]
**File:** `Reviews/scripts/calculate_agents.py`
**Tests:** Run the script to confirm it still works (or its test if one exists)

Bare `except:` catches `SystemExit`, `KeyboardInterrupt`, and other base exceptions — almost always a mistake.

- [ ] Read `Reviews/scripts/calculate_agents.py` lines 85-105 to see surrounding context
- [ ] Identify what kind of exception is actually expected at line 94 (likely `ValueError`, `KeyError`, `OSError`, etc.)
- [ ] Replace `except:` with the most specific applicable exception type. If unclear, use `except Exception:` — never leave it bare
- [ ] **Verification:** `grep -n "^[[:space:]]*except:" Reviews/scripts/calculate_agents.py` returns zero results

**Notes:**

---

### Task 4.2: Replace bare `except:` in `Tools/check_orphans/check_orphans.py` [Simple]
**File:** `Tools/check_orphans/check_orphans.py`
**Tests:** Run the script (`python Tools/check_orphans/check_orphans.py --help` and a basic invocation)

- [ ] Read `Tools/check_orphans/check_orphans.py` lines 55-75 to see surrounding context
- [ ] Identify the expected exception type
- [ ] Replace with specific exception or `except Exception:`
- [ ] **Verification:** `grep -n "^[[:space:]]*except:" Tools/check_orphans/check_orphans.py` returns zero results

**Notes:**

---

### Task 4.3: Add `radon` and `vulture` to dev dependencies [Simple]
**File:** `pyproject.toml`
**Tests:** `pip install -e .[dev]` (or equivalent), then `radon --version && vulture --version`

These tools enable ongoing complexity (radon) and dead-code (vulture) scanning. Currently absent from any dependency list.

- [ ] Read `pyproject.toml` and identify the current dependency layout. There may already be a `[project.optional-dependencies]` section with a `dev` group, or there may not — inspect first
- [ ] If `[project.optional-dependencies]` with a `dev` group exists: add `radon` and `vulture` to the list
- [ ] If no `dev` group exists: create `[project.optional-dependencies]` with a `dev` array containing `radon`, `vulture`, and any test-only deps already in `requirements.txt` that are clearly dev-only (pytest, pytest-xdist, pytest-testmon, pytest-cov)
- [ ] Pin both tools to recent stable versions (check PyPI for current — probably `radon>=6` and `vulture>=2.10`). Use `>=` not `==` to allow patch updates
- [ ] In the active venv, install: `pip install -e ".[dev]"` (or the equivalent for whatever pattern the project uses)
- [ ] **Verification:** `radon --version` and `vulture --version` both succeed
- [ ] **Verification:** `radon cc game/ -a -nb` produces output without crashing (smoke test)
- [ ] **Verification:** `vulture game/ --min-confidence 80` produces output without crashing (smoke test — high false-positive rate is expected; we're just confirming the tool runs)

**Notes:** Optional follow-up — add a `Tools/quality_scan.py` wrapper that runs both with sensible defaults. Out of scope for this task; capture as a follow-up if desired.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `grep -rn "^[[:space:]]*except:" Reviews/ Tools/ game/ tests/` returns zero results
- [ ] `radon --version && vulture --version` both succeed in the project venv
- [ ] Full sharded suite (`python Tools/test_sharded/test_sharded.py`) at 15112+ passing — should be unchanged from Phase 1 since this phase doesn't touch production code
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete; ready for audit
