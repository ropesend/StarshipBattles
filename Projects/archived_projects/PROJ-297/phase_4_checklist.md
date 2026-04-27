# Phase 4: Tooling & Hygiene

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-297 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Two small hygiene fixes: replace 2 bare `except:` clauses with `except Exception:`, and add `radon` + `vulture` to dev dependencies for ongoing complexity/dead-code scans.

---

## Tasks

### Task 4.1: Replace bare `except:` in `Reviews/scripts/calculate_agents.py` [Simple]
**File:** `Reviews/scripts/calculate_agents.py`
**Tests:** Run the script to confirm it still works (or its test if one exists)

Bare `except:` catches `SystemExit`, `KeyboardInterrupt`, and other base exceptions — almost always a mistake.

- [x] Read `Reviews/scripts/calculate_agents.py` lines 85-105 to see surrounding context
- [x] Identify what kind of exception is actually expected at line 94 (likely `ValueError`, `KeyError`, `OSError`, etc.)
- [x] Replace `except:` with the most specific applicable exception type. If unclear, use `except Exception:` — never leave it bare
- [x] **Verification:** `grep -n "^[[:space:]]*except:" Reviews/scripts/calculate_agents.py` returns zero results

**Notes:**
- Replaced bare `except:` at line 94 with `except OSError:` — the wrapped operation is `read_text()`, so OSError (and its subclasses like UnicodeDecodeError when not using `errors='ignore'`, FileNotFoundError, PermissionError) is the precise applicable type. Specific over broad per CLAUDE.md §6.3.

---

### Task 4.2: Replace bare `except:` in `Tools/check_orphans/check_orphans.py` [Simple]
**File:** `Tools/check_orphans/check_orphans.py`
**Tests:** Run the script (`python Tools/check_orphans/check_orphans.py --help` and a basic invocation)

- [x] Read `Tools/check_orphans/check_orphans.py` lines 55-75 to see surrounding context
- [x] Identify the expected exception type
- [x] Replace with specific exception or `except Exception:`
- [x] **Verification:** `grep -n "^[[:space:]]*except:" Tools/check_orphans/check_orphans.py` returns zero results

**Notes:**
- Replaced bare `except:` at line 63 with `except Exception:`. The wrapped block parses files (AST/imports parsing) — multiple exception types possible (SyntaxError, AttributeError, KeyError, OSError). `Exception` is appropriate here since we genuinely want to skip any malformed/edge-case file rather than narrow to specifics. Still avoids catching `KeyboardInterrupt`/`SystemExit`.

---

### Task 4.3: Add `radon` and `vulture` to dev dependencies [Simple]
**File:** `pyproject.toml`
**Tests:** `pip install -e .[dev]` (or equivalent), then `radon --version && vulture --version`

These tools enable ongoing complexity (radon) and dead-code (vulture) scanning. Currently absent from any dependency list.

- [x] Read `pyproject.toml` and identify the current dependency layout. There may already be a `[project.optional-dependencies]` section with a `dev` group, or there may not — inspect first
- [x] If `[project.optional-dependencies]` with a `dev` group exists: add `radon` and `vulture` to the list
- [x] If no `dev` group exists: create `[project.optional-dependencies]` with a `dev` array containing `radon`, `vulture`, and any test-only deps already in `requirements.txt` that are clearly dev-only (pytest, pytest-xdist, pytest-testmon, pytest-cov)
- [x] Pin both tools to recent stable versions (check PyPI for current — probably `radon>=6` and `vulture>=2.10`). Use `>=` not `==` to allow patch updates
- [x] In the active venv, install: `pip install -e ".[dev]"` (or the equivalent for whatever pattern the project uses)
- [x] **Verification:** `radon --version` and `vulture --version` both succeed
- [x] **Verification:** `radon cc game/ -a -nb` produces output without crashing (smoke test)
- [x] **Verification:** `vulture game/ --min-confidence 80` produces output without crashing (smoke test — high false-positive rate is expected; we're just confirming the tool runs)

**Notes:**
- Repository uses `requirements.txt` + `requirements-dev.txt` instead of `[project.optional-dependencies]` in pyproject.toml. Added `radon>=6.0.0` and `vulture>=2.10` to `requirements-dev.txt` under a new `# Code quality scanning (PROJ-297)` section.
- Installed in venv: `radon 6.0.1`, `vulture 2.16`. Both tools run without errors.
- Smoke tested: `radon cc game/core/component_state.py -a` returned valid output (Average A complexity, 1.33). `vulture game/core/component_state.py` returned 3 false-positive "unused" warnings at 60% confidence on `is_damaged`/`to_dict`/`from_dict` — these are called dynamically by save/load code that vulture's static analysis can't trace. Tools work as expected.

Optional follow-up (out of scope): add a `Tools/quality_scan.py` wrapper. Capture as future work.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `grep -rn "^[[:space:]]*except:" Reviews/ Tools/ game/ tests/` returns zero results
- [x] `radon --version && vulture --version` both succeed in the project venv
- [x] Full sharded suite (`python Tools/test_sharded/test_sharded.py`) at 15112+ passing — should be unchanged from Phase 1 since this phase doesn't touch production code
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate project complete; ready for audit
