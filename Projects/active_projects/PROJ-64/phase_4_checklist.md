# Phase 4: UI Screens Part A

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-64 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Narrow exception handling in builder screens, setup screens, and standalone screens.
**Tests:** `pytest tests/unit/ui/ tests/unit/builder/ tests/integration/ui/ -x`

---

## Tasks

### Task 4.1: ui/screens/builder/ (4 sites) [Simple]
**File:** `game/ui/screens/builder/detail_panel.py` (line 251)
**File:** `game/ui/screens/builder/event_bus.py` (line 55)
**File:** `game/ui/screens/builder/right_panel.py` (line 370)
**File:** `game/ui/screens/builder/stats_config.py` (line 315)

- [ ] `detail_panel.py:251`: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, pygame.error) as e:` AND replace `print(...)` with `log_warning(...)` — add import
- [ ] `event_bus.py:55`: Keep `except Exception as e:` — add comment: `# Intentional broad catch: event handler isolation prevents handler bugs from crashing callers`
- [ ] `right_panel.py:370`: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, pygame.error) as e:` AND replace `print(...)` with `log_warning(...)` — add import
- [ ] `stats_config.py:315`: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:` AND replace `print(...)` with `log_warning(...)` — add import
- [ ] Ensure `from game.core.logger import log_warning` imported in detail_panel, right_panel, stats_config
- [ ] Verify: `pytest tests/unit/builder/ -x`

**Notes:**

---

### Task 4.2: ui/screens/setup_data_io.py (3 sites) [Simple]
**File:** `game/ui/screens/setup_data_io.py`
**Lines:** 49, 77, 230
**Pattern:** JSON file loading for ship designs, formations, setup data.

- [ ] Line 49: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:` — ship design
- [ ] Line 77: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:` — formation
- [ ] Line 230: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:` — setup
- [ ] Verify: `pytest tests/unit/ui/ -x`

**Notes:**

---

### Task 4.3: ui/screens/setup_screen.py (1 site) [Simple]
**File:** `game/ui/screens/setup_screen.py`
**Line:** 142
**Pattern:** Formation addition in batch.

- [ ] Line 142: Replace `except Exception as e:` with `except (KeyError, TypeError, ValueError, AttributeError) as e:`
- [ ] Verify: `pytest tests/unit/ui/ -x`

**Notes:**

---

### Task 4.4: ui/screens/race_asset_loader.py (4 sites) [Simple]
**File:** `game/ui/screens/race_asset_loader.py`
**Lines:** 61, 86, 140, 183
**Pattern:** Pygame image loading with fallback.

- [ ] Line 61: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, pygame.error) as e:` — flag shape
- [ ] Line 86: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, pygame.error) as e:` — portrait
- [ ] Line 140: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, pygame.error) as e:` — portrait preview
- [ ] Line 183: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, pygame.error) as e:` — flag preview
- [ ] Verify: `pytest tests/unit/ui/ -x`

**Notes:**

---

### Task 4.5: ui/screens/race_setup_screen.py (1 site) [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
**Line:** 471
**Pattern:** Ship portrait loading.

- [ ] Line 471: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, pygame.error) as e:`
- [ ] Verify: `pytest tests/unit/ui/ -x`

**Notes:**

---

### Task 4.6: ui/screens/design_selector_window.py (2 sites) [Simple]
**File:** `game/ui/screens/design_selector_window.py`
**Lines:** 451, 523
**Pattern:** Portrait and skin image loading in loops.

- [ ] Line 451: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, pygame.error) as e:`
- [ ] Line 523: Replace `except Exception:` with `except (FileNotFoundError, OSError, pygame.error):` AND add `log_warning(f"Failed to load skin image: {path}")` — currently silent
- [ ] Ensure `from game.core.logger import log_warning` is imported
- [ ] Verify: `pytest tests/unit/ui/ -x`

**Notes:**

---

### Task 4.7: ui/screens/build_queue_screen.py (2 sites) [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Lines:** 450, 660
**Pattern:** Portrait loading and design report update.

- [ ] Line 450: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, pygame.error) as e:`
- [ ] Line 660: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, KeyError, TypeError, ValueError, AttributeError) as e:`
- [ ] Verify: `pytest tests/integration/ui/ -x`

**Notes:**

---

### Task 4.8: ui/screens/ remaining standalone (4 sites) [Simple]
**File:** `game/ui/screens/battle_screen.py` (line 316)
**File:** `game/ui/screens/galaxy_test_screen.py` (lines 452, 580)
**File:** `game/ui/screens/planet_list_window.py` (line 1069)

- [ ] `battle_screen.py:316`: Replace `except Exception as e:` with `except (ImportError, AttributeError, OSError) as e:`
- [ ] `galaxy_test_screen.py:452`: Replace `except Exception as e:` with `except (ImportError, FileNotFoundError, OSError, json.JSONDecodeError, KeyError) as e:`
- [ ] `galaxy_test_screen.py:580`: Replace `except Exception as e:` with `except (ImportError, FileNotFoundError, OSError, json.JSONDecodeError, KeyError) as e:`
- [ ] `planet_list_window.py:1069`: Replace `except Exception as e:` with `except (OSError, RuntimeError, pygame.error) as e:`
- [ ] Verify: `pytest tests/unit/ui/ tests/integration/ui/ -x`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run: `pytest tests/unit/ui/ tests/unit/builder/ tests/integration/ui/ -x`
- [ ] Run: `pytest tests/ --testmon`
- [ ] Grep: verify only intentional sites remain in Phase 4 files (event_bus.py only)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
