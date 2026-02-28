# Phase 2: Strategy Layer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-64 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Narrow exception handling in strategy systems (save, design library, race library, data loading).
**Tests:** `pytest tests/unit/strategy/ tests/integration/ -x`

---

## Tasks

### Task 2.1: save_game_service.py (5 sites) [Medium]
**File:** `game/strategy/systems/save_game_service.py`
**Lines:** 114, 214, 230, 352, 451
**Pattern:** Save/load/delete. Already has specific catches above broad catches.

- [x] Line 114: Replace `except Exception as e:` with `except (KeyError, AttributeError, ImportError) as e:` — save fallback after (PermissionError, OSError, TypeError, ValueError) catches
- [x] Line 214: Replace `except Exception as e:` with `except (AttributeError, ImportError, RuntimeError) as e:` — turn reconstruction fallback (RuntimeError added for test compatibility)
- [x] Line 230: Replace `except Exception as e:` with `except (KeyError, TypeError, ValueError, AttributeError, ImportError) as e:` — load game fallback
- [x] Line 352: Replace `except Exception as e:` with `except shutil.Error as e:` — delete save
- [x] Line 451: Replace `except Exception as e:` with `except (KeyError, TypeError, ValueError) as e:` — read metadata
- [x] Verify: `pytest tests/unit/strategy/ -x`

**Notes:** RuntimeError added to line 214 catch to handle test mock that raises RuntimeError

---

### Task 2.2: design_library.py (6 sites) [Medium]
**File:** `game/strategy/systems/design_library.py`
**Lines:** 102, 192, 229, 269, 313, 401
**Pattern:** Design file operations. Most already have specific catches above.

- [x] Line 102: Replace `except Exception as e:` with `except (AttributeError, TypeError, ValueError) as e:` — scan fallback after specific catches
- [x] Line 192: Replace `except Exception as e:` with `except (AttributeError, KeyError) as e:` — save design
- [x] Line 229: Replace `except Exception as e:` with `except (KeyError, TypeError, ValueError, AttributeError) as e:` — load design data
- [x] Line 269: Replace `except Exception as e:` with `except (KeyError, TypeError, ValueError, AttributeError) as e:` — mark obsolete
- [x] Line 313: Replace `except Exception as e:` with `except (KeyError, TypeError, ValueError, AttributeError) as e:` — update metadata
- [x] Line 401: Replace `except Exception as e:` with `except (RuntimeError, IOError) as e:` — delete design
- [x] Verify: `pytest tests/unit/strategy/ -x`

**Notes:** All 6 sites narrowed

---

### Task 2.3: race_library.py (4 sites) [Simple]
**File:** `game/strategy/systems/race_library.py`
**Lines:** 115, 154, 197, 227
**Pattern:** Race file operations. Similar to design_library.

- [x] Line 115: Replace `except Exception as e:` with `except (AttributeError, TypeError, ValueError) as e:` — scan fallback after specific catches
- [x] Line 154: Replace `except Exception as e:` with `except (AttributeError, TypeError, ValueError) as e:` — get race
- [x] Line 197: Replace `except Exception as e:` with `except (AttributeError, KeyError) as e:` — save race
- [x] Line 227: Replace `except Exception as e:` with `except (RuntimeError, IOError) as e:` — delete race
- [x] Verify: `pytest tests/unit/strategy/ -x`

**Notes:** All 4 sites narrowed

---

### Task 2.4: strategy/data/ files (2 sites) [Simple]
**File:** `game/strategy/data/classification_config.py` (line 140)
**File:** `game/strategy/data/naming.py` (line 33)

- [x] `classification_config.py:140`: Replace `except Exception:` with `except (ImportError, FileNotFoundError, OSError, KeyError, TypeError, ValueError) as e:` and add `log_warning(f"Failed to load classification config: {e}")`
- [x] `naming.py:33`: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, yaml.YAMLError, KeyError, TypeError, UnicodeDecodeError) as e:`
- [x] ship_instance.py had no `except Exception` - was already clean
- [x] Verify: `pytest tests/unit/strategy/ -x`

**Notes:** ship_instance.py did not have any `except Exception` - checklist was outdated

---

### Task 2.5: strategy/ remaining files (2 sites) [Simple]
**File:** `game/strategy/quickstart_builder.py` (line 226)
**File:** `game/strategy/facade/strategy_session_facade.py` (line 398)

- [x] `quickstart_builder.py:226`: Replace `except Exception as e:` with `except (OSError, PermissionError, shutil.Error) as e:` — file copy
- [x] `strategy_session_facade.py:398`: Replace `except Exception:` with `except (RuntimeError, AttributeError, ImportError):`
- [x] turn_engine.py had no `except Exception` - was already clean
- [x] Verify: `pytest tests/unit/strategy/ tests/integration/ -x`

**Notes:** turn_engine.py did not have any `except Exception` - checklist was outdated. Only 2 sites found.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run: `pytest tests/unit/strategy/ tests/integration/ -x` — 1639 passed
- [x] Grep: `grep -rn "except Exception" game/strategy/` — 0 broad catches remaining
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
