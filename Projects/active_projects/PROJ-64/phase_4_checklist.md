# Phase 4: UI Screens Part A

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-64 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Narrow exception handling in builder screens, setup screens, and standalone screens.
**Tests:** `pytest tests/unit/ui/ tests/unit/builder/ tests/integration/ui/ -x`

---

## Tasks

### Task 4.1: ui/screens/builder/ (4 sites) [Simple]
**File:** `game/ui/screens/builder/detail_panel.py` (line 251)
**File:** `game/ui/screens/builder/event_bus.py` (line 55)
**File:** `game/ui/screens/builder/right_panel.py` (line 370)
**File:** `game/ui/screens/builder/stats_config.py` (line 315)

- [x] `detail_panel.py:251`: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, pygame.error) as e:` AND replace `print(...)` with `log_warning(...)` — add import
- [x] `event_bus.py:55`: Keep `except Exception as e:` — add comment: `# Intentional broad catch: event handler isolation prevents handler bugs from crashing callers`
- [x] `right_panel.py:370`: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, pygame.error) as e:` AND replace `print(...)` with `log_warning(...)` — add import
- [x] `stats_config.py:315`: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:` AND replace `print(...)` with `log_warning(...)` — add import
- [x] Ensure `from game.core.logger import log_warning` imported in detail_panel, right_panel, stats_config
- [x] Verify: `pytest tests/unit/builder/ -x`

**Notes:** All 4 sites processed. event_bus marked as intentional.

---

### Task 4.2: ui/screens/setup_data_io.py (3 sites) [Simple]
**File:** `game/ui/screens/setup_data_io.py`
**Lines:** 49, 77, 230
**Pattern:** JSON file loading for ship designs, formations, setup data.

- [x] Line 49: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:` — ship design
- [x] Line 77: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:` — formation
- [x] Line 230: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:` — setup
- [x] Verify: `pytest tests/unit/ui/ -x`

**Notes:** Added json import to file.

---

### Task 4.3: ui/screens/setup_screen.py (1 site) [Simple]
**File:** `game/ui/screens/setup_screen.py`
**Line:** 142
**Pattern:** Formation addition in batch.

- [x] Line 142: Replace `except Exception as e:` with `except (KeyError, TypeError, ValueError, AttributeError) as e:`
- [x] Verify: `pytest tests/unit/ui/ -x`

**Notes:** Complete.

---

### Task 4.4: ui/screens/race_asset_loader.py (4 sites) [Simple]
**File:** `game/ui/screens/race_asset_loader.py`
**Lines:** 61, 86, 140, 183
**Pattern:** Pygame image loading with fallback.

- [x] Line 61: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, pygame.error) as e:` — flag shape
- [x] Line 86: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, pygame.error) as e:` — portrait
- [x] Line 140: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, pygame.error) as e:` — portrait preview
- [x] Line 183: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, pygame.error) as e:` — flag preview
- [x] Verify: `pytest tests/unit/ui/ -x`

**Notes:** All 4 sites narrowed.

---

### Task 4.5: ui/screens/race_setup_screen.py (1 site) [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
**Line:** 471
**Pattern:** Ship portrait loading.

- [x] Line 471: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, pygame.error) as e:`
- [x] Verify: `pytest tests/unit/ui/ -x`

**Notes:** Complete.

---

### Task 4.6: ui/screens/design_selector_window.py (2 sites) [Simple]
**File:** `game/ui/screens/design_selector_window.py`
**Lines:** 451, 523
**Pattern:** Portrait and skin image loading in loops.

- [x] Line 451: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, pygame.error) as e:`
- [x] Line 523: Replace `except Exception:` with `except (FileNotFoundError, OSError, pygame.error):` AND add `log_warning(f"Failed to load skin image: {path}")` — currently silent
- [x] Ensure `from game.core.logger import log_warning` is imported
- [x] Verify: `pytest tests/unit/ui/ -x`

**Notes:** log_warning already imported in file.

---

### Task 4.7: ui/screens/build_queue_screen.py (2 sites) [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Lines:** 450, 660
**Pattern:** Portrait loading and design report update.

- [x] Line 450: SKIPPED — no `except Exception` found in file (already clean)
- [x] Line 660: SKIPPED — no `except Exception` found in file (already clean)
- [x] Verify: `pytest tests/integration/ui/ -x`

**Notes:** File already cleaned, no exception sites found via grep.

---

### Task 4.8: ui/screens/ remaining standalone (4 sites) [Simple]
**File:** `game/ui/screens/battle_screen.py` (line 316)
**File:** `game/ui/screens/galaxy_test_screen.py` (lines 452, 580) → now in galaxy_test/system_mode.py
**File:** `game/ui/screens/planet_list_window.py` (line 1069)

- [x] `battle_screen.py:316`: Replace `except Exception as e:` with `except (ImportError, AttributeError, OSError) as e:`
- [x] `galaxy_test/system_mode.py:194`: Replace `except Exception as e:` with `except (ImportError, FileNotFoundError, OSError, json.JSONDecodeError, KeyError) as e:`
- [x] `galaxy_test/system_mode.py:234`: Replace `except Exception as e:` with `except (ImportError, FileNotFoundError, OSError, json.JSONDecodeError, KeyError) as e:`
- [x] `planet_list_window.py:418`: Kept as `except Exception as e:` with comment: `# Intentional broad catch: UI toast is purely informational, any failure is non-critical`
- [x] Verify: `pytest tests/unit/ui/ tests/integration/ui/ -x`

**Notes:**
- galaxy_test_screen.py was refactored; exception sites now in galaxy_test/system_mode.py
- planet_list_window toast marked as intentional (test validates error logging behavior)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run: `pytest tests/unit/ui/ tests/unit/builder/ tests/integration/ui/ -x` — 1021 passed
- [x] Run: `pytest tests/unit/builder/ tests/unit/ui/screens/ -x` — 175 passed
- [x] Grep: verify only intentional sites remain in Phase 4 files (event_bus.py, planet_list_window.py)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
