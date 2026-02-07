# Phase 3: UI Panels & Renderer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-64 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Narrow exception handling in UI panels and renderer (primarily asset loading patterns).
**Tests:** `pytest tests/unit/ui/ -x`

---

## Tasks

### Task 3.1: ui/renderer/sprites.py (2 sites) [Simple]
**File:** `game/ui/renderer/sprites.py`
**Lines:** 116, 143
**Pattern:** Sprite/atlas image loading.

- [ ] Line 116: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, pygame.error) as e:` — individual sprite
- [ ] Line 143: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, pygame.error) as e:` — atlas loading
- [ ] Verify: `pytest tests/unit/ui/ -x`

**Notes:**

---

### Task 3.2: ui/panels/design_report_panel.py (3 sites) [Simple]
**File:** `game/ui/panels/design_report_panel.py`
**Lines:** 176, 270, 403
**Pattern:** Portrait loading, stat config, stat row creation.

- [ ] Line 176: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, pygame.error) as e:` — portrait image
- [ ] Line 270: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:` — stat config loading
- [ ] Line 403: Replace `except Exception as e:` with `except (TypeError, ValueError, AttributeError, KeyError) as e:` — stat row creation
- [ ] Ensure `import json` present if needed for json.JSONDecodeError
- [ ] Verify: `pytest tests/unit/ui/ -x`

**Notes:**

---

### Task 3.3: ui/panels/race_portrait_gallery.py (1 site) [Simple]
**File:** `game/ui/panels/race_portrait_gallery.py`
**Line:** 147
**Pattern:** Portrait thumbnail scaling.

- [ ] Line 147: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, pygame.error) as e:`
- [ ] Verify: `pytest tests/unit/ui/ -x`

**Notes:**

---

### Task 3.4: ui/panels/race_flag_gallery.py (1 site) [Simple]
**File:** `game/ui/panels/race_flag_gallery.py`
**Line:** 154
**Pattern:** Flag thumbnail scaling.

- [ ] Line 154: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, pygame.error) as e:`
- [ ] Verify: `pytest tests/unit/ui/ -x`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run: `pytest tests/unit/ui/ -x`
- [ ] Run: `pytest tests/ --testmon`
- [ ] Grep: `grep -rn "except Exception" game/ui/panels/ game/ui/renderer/` — should be 0
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
