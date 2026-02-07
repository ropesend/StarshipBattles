# Phase 2: Strategy Layer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-64 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Narrow exception handling in strategy systems (save, design library, race library, data loading).
**Tests:** `pytest tests/unit/strategy/ tests/integration/ -x`

---

## Tasks

### Task 2.1: save_game_service.py (5 sites) [Medium]
**File:** `game/strategy/systems/save_game_service.py`
**Lines:** 114, 214, 230, 352, 451
**Pattern:** Save/load/delete. Already has specific catches above broad catches.

- [ ] Line 114: Replace `except Exception as e:` with `except (KeyError, AttributeError, ImportError) as e:` — save fallback after (PermissionError, OSError, TypeError, ValueError) catches
- [ ] Line 214: Replace `except Exception as e:` with `except (KeyError, TypeError, ValueError, AttributeError) as e:` — turn reconstruction fallback
- [ ] Line 230: Replace `except Exception as e:` with `except (KeyError, TypeError, ValueError, AttributeError) as e:` — load game fallback
- [ ] Line 352: Replace `except Exception as e:` with `except (PermissionError, OSError) as e:` — delete save
- [ ] Line 451: Replace `except Exception as e:` with `except (json.JSONDecodeError, KeyError, TypeError, OSError) as e:` — read metadata
- [ ] Verify: `pytest tests/unit/strategy/ -x`

**Notes:**

---

### Task 2.2: design_library.py (6 sites) [Medium]
**File:** `game/strategy/systems/design_library.py`
**Lines:** 102, 192, 229, 269, 313, 401
**Pattern:** Design file operations. Most already have specific catches above.

- [ ] Line 102: Replace `except Exception as e:` with `except (AttributeError, TypeError, ValueError) as e:` — scan fallback after specific catches
- [ ] Line 192: Replace `except Exception as e:` with `except (AttributeError, TypeError, ValueError, OSError) as e:` — save design
- [ ] Line 229: Replace `except Exception as e:` with `except (json.JSONDecodeError, OSError, KeyError, TypeError) as e:` — load design data
- [ ] Line 269: Replace `except Exception as e:` with `except (json.JSONDecodeError, OSError, KeyError, TypeError) as e:` — mark obsolete
- [ ] Line 313: Replace `except Exception as e:` with `except (json.JSONDecodeError, OSError, KeyError, TypeError) as e:` — update metadata
- [ ] Line 401: Replace `except Exception as e:` with `except (OSError, PermissionError) as e:` — delete design
- [ ] Verify: `pytest tests/unit/strategy/ -x`

**Notes:**

---

### Task 2.3: race_library.py (4 sites) [Simple]
**File:** `game/strategy/systems/race_library.py`
**Lines:** 115, 154, 197, 227
**Pattern:** Race file operations. Similar to design_library.

- [ ] Line 115: Replace `except Exception as e:` with `except (AttributeError, TypeError, ValueError) as e:` — scan fallback after specific catches
- [ ] Line 154: Replace `except Exception as e:` with `except (json.JSONDecodeError, OSError, KeyError, TypeError) as e:` — get race
- [ ] Line 197: Replace `except Exception as e:` with `except (OSError, PermissionError, TypeError, ValueError) as e:` — save race
- [ ] Line 227: Replace `except Exception as e:` with `except (OSError, PermissionError) as e:` — delete race
- [ ] Verify: `pytest tests/unit/strategy/ -x`

**Notes:**

---

### Task 2.4: strategy/data/ files (3 sites) [Simple]
**File:** `game/strategy/data/classification_config.py` (line 140)
**File:** `game/strategy/data/naming.py` (line 33)
**File:** `game/strategy/data/ship_instance.py` (line 198)

- [ ] `classification_config.py:140`: Replace `except Exception:` with `except (ImportError, FileNotFoundError, OSError, KeyError, TypeError, ValueError) as e:` and add `log_warning(f"Failed to load classification config: {e}")`
- [ ] `naming.py:33`: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, UnicodeDecodeError) as e:`
- [ ] `ship_instance.py:198`: Replace `except Exception:` with `except (RuntimeError, AttributeError) as e:` and add `log_warning(f"Default registries unavailable, using fallback: {e}")`
- [ ] Ensure logging imports are present in all 3 files
- [ ] Verify: `pytest tests/unit/strategy/ -x`

**Notes:**

---

### Task 2.5: strategy/ remaining files (3 sites) [Simple]
**File:** `game/strategy/quickstart_builder.py` (line 226)
**File:** `game/strategy/facade/strategy_session_facade.py` (line 398)
**File:** `game/strategy/engine/turn_engine.py` (line 130)

- [ ] `quickstart_builder.py:226`: Replace `except Exception as e:` with `except (OSError, PermissionError) as e:` — file copy
- [ ] `strategy_session_facade.py:398`: Replace `except Exception:` with `except (RuntimeError, AttributeError) as e:` and add logging
- [ ] `turn_engine.py:130`: Replace `except Exception:` with `except (RuntimeError, AttributeError) as e:` and add logging
- [ ] Verify imports: logging in facade and turn_engine
- [ ] Verify: `pytest tests/unit/strategy/ tests/integration/ -x`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run: `pytest tests/unit/strategy/ tests/integration/ -x`
- [ ] Run: `pytest tests/ --testmon`
- [ ] Grep: `grep -rn "except Exception" game/strategy/` — should be 0 broad catches remaining
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
