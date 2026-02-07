# Phase 5: UI Screens Part B — Workshop, Test Lab, Strategy

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-64 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Narrow exception handling in the largest/most complex screen files.
**Tests:** `pytest tests/unit/ui/ tests/integration/ -x`

---

## Tasks

### Task 5.1: ui/screens/workshop_screen.py (3 sites) [Simple]
**File:** `game/ui/screens/workshop_screen.py`
**Lines:** 594, 757, 930
**Pattern:** Data reload, design scan, Tkinter dialog.

- [ ] Line 594: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:` — data reload
- [ ] Line 757: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:` — design scan
- [ ] Line 930: Keep `except Exception as e:` — add comment: `# Intentional broad catch: Tkinter dialog is platform-dependent`
- [ ] Verify: `pytest tests/unit/ui/ -x`

**Notes:**

---

### Task 5.2: ui/screens/workshop_context.py (1 site) [Simple]
**File:** `game/ui/screens/workshop_context.py`
**Line:** 94
**Pattern:** Silent registry initialization fallback.

- [ ] Line 94: Replace `except Exception:` with `except (RuntimeError, AttributeError, ImportError) as e:`
- [ ] Add: `from game.core.logger import log_warning` and `log_warning(f"Workshop registries not available: {e}")`
- [ ] Verify: `pytest tests/unit/ui/ -x`

**Notes:**

---

### Task 5.3: ui/screens/workshop_data_loader.py (1 site) [Simple]
**File:** `game/ui/screens/workshop_data_loader.py`
**Line:** 150
**Pattern:** Data loading with result-based error collection.

- [ ] Line 150: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:`
- [ ] Verify: `pytest tests/unit/ui/ -x`

**Notes:**

---

### Task 5.4: ui/screens/test_lab_screen.py (6 sites) [Medium]
**File:** `game/ui/screens/test_lab_screen.py`
**Lines:** 2573, 2796, 3147, 3224, 3355, 3477
**Pattern:** Test validation, metadata, clipboard, test execution. No dedicated error tests (higher risk).

- [ ] Line 2573: Replace `except Exception as e:` with `except (TypeError, ValueError, KeyError, AttributeError, ImportError) as e:` — validation
- [ ] Line 2796: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:` — metadata refresh
- [ ] Line 3147: Replace `except Exception as e:` with `except (OSError, RuntimeError, pygame.error) as e:` — clipboard
- [ ] Line 3224: Replace `except Exception as e:` with `except (TypeError, ValueError, KeyError, AttributeError, ImportError, OSError) as e:` — visual test
- [ ] Line 3355: Replace `except Exception as e:` with `except (TypeError, ValueError, KeyError, AttributeError, ImportError, OSError) as e:` — headless test
- [ ] Line 3477: Replace `except Exception as e:` with `except (TypeError, ValueError, KeyError, AttributeError, ImportError, OSError) as e:` — batch test
- [ ] Verify: `pytest tests/ --testmon` (wider net for test lab)

**Notes:**

---

### Task 5.5: ui/screens/test_lab.py (3 sites) [Simple]
**File:** `game/ui/screens/test_lab.py`
**Lines:** 66, 68, 134
**Pattern:** Scenario instantiation, file loading, test execution. Uses `print()`.

- [ ] Line 66: Replace `except Exception as e:` with `except (TypeError, ValueError, AttributeError) as e:` AND replace `print(...)` with `log_warning(...)`
- [ ] Line 68: Replace `except Exception as e:` with `except (ImportError, ModuleNotFoundError, AttributeError, SyntaxError) as e:` AND replace `print(...)` with `log_warning(...)`
- [ ] Line 134: Replace `except Exception as e:` with `except (TypeError, ValueError, KeyError, AttributeError, ImportError, OSError) as e:`
- [ ] Ensure `from game.core.logger import log_warning` is imported
- [ ] Verify: `pytest tests/ --testmon`

**Notes:**

---

### Task 5.6: ui/screens/strategy_screen.py (2 sites) [Simple]
**File:** `game/ui/screens/strategy_screen.py`
**Lines:** 401, 520
**Pattern:** Report refresh and planet image loading.

- [ ] Line 401: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, pygame.error, AttributeError, KeyError) as e:`
- [ ] Line 520: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, pygame.error, AttributeError) as e:`
- [ ] Verify: `pytest tests/unit/ui/ -x`

**Notes:**

---

### Task 5.7: ui/screens/strategy_input_handler.py (1 site) [Simple]
**File:** `game/ui/screens/strategy_input_handler.py`
**Line:** 520
**Pattern:** Screenshot toast notification.

- [ ] Line 520: Replace `except Exception as e:` with `except (OSError, RuntimeError, pygame.error) as e:`
- [ ] Verify: `pytest tests/unit/ui/ -x`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run: `pytest tests/unit/ui/ tests/integration/ -x`
- [ ] Run: `pytest tests/ --testmon`
- [ ] Grep: verify only intentional sites remain in Phase 5 files (workshop_screen.py:930 only)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
