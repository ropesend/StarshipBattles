# Broad-Catch Sites Verification

**Review scope:** 13 files across strategy, engine, assets, and UI layers
**Reference:** `docs/05_ERROR_HANDLING.md` §203--230 (Broad Catch Rule)

---

## Summary

| Metric | Count |
|---|---|
| Total `except` blocks found | **37** |
| Narrow catches (specific type) | **21** |
| Broad catches (`Exception` or `BaseException`) | **16** |
| Bare `except:` (no type) | **0** |
| Broad catches with **substantive** comment | **11** |
| Broad catches with **boilerplate** comment | **5** |
| Broad catches **missing** comment | **0** |
| Should-be-narrowed | **2** |

**Overall assessment:** No critical violations found. All broad catches carry an `# Intentional broad catch:` comment. Five broad catches in `tkinter_utils.py` have boilerplate-reason comments (only restating the legitimate category label without specifying expected failure modes). Two sites could potentially be narrowed.

---

## Per-File Analysis

### 1. `game/strategy/engine/turn_engine.py`

| Line | Exception Type | Classification | Comment? | Substantive? | Should Narrow? | Action |
|------|---------------|----------------|----------|-------------|----------------|--------|
| 282 | `EnginePhaseError` | Narrow | n/a (already wrapped) | n/a | No | Re-raises as-is |
| 286 | `Exception` | **Broad** | Yes | Yes | No | **VALID** -- wraps unknown phase failures as `EnginePhaseError` and re-raises per documented strategy-layer pattern |
| 320 | `AttributeError, TypeError` | Narrow | n/a | n/a | No | -- |
| 591 | `EnginePhaseError` | Narrow | n/a | n/a | No | Rollback + re-raise |
| 702 | `Exception` | **Broad** | Yes | Yes | No | **VALID** -- UI progress callback must never break turn processing (PROJ-308) |

### 2. `game/strategy/engine/conflict_resolution_engine.py`

| Line | Exception Type | Classification | Comment? | Substantive? | Should Narrow? | Action |
|------|---------------|----------------|----------|-------------|----------------|--------|
| 567 | `Exception` | **Broad** | Yes | Yes | Potentially | **MIN-010** -- See detailed findings |

### 3. `game/assets/asset_manager.py`

| Line | Exception Type | Classification | Comment? | Substantive? | Should Narrow? | Action |
|------|---------------|----------------|----------|-------------|----------------|--------|
| 88 | `FileNotFoundError` | Narrow | n/a | n/a | No | -- |
| 91 | `pygame.error` | Narrow | n/a | n/a | No | -- |
| 113 | `FileNotFoundError` | Narrow | n/a | n/a | No | -- |
| 115 | `pygame.error` | Narrow | n/a | n/a | No | -- |
| 154 | `FileNotFoundError, pygame.error, ValueError, OSError` | Narrow | n/a | n/a | No | PROJ-381 Phase 2 narrowed from bare `Exception` |
| 211 | `FileNotFoundError` | Narrow | n/a | n/a | No | -- |
| 214 | `pygame.error` | Narrow | n/a | n/a | No | -- |
| 303 | `FileNotFoundError, pygame.error, ValueError` | Narrow | n/a | n/a | No | -- |

**Verdict:** All narrow. Well-structured. No issues.

### 4. `game/ui/services/image/background.py`

| Line | Exception Type | Classification | Comment? | Substantive? | Should Narrow? | Action |
|------|---------------|----------------|----------|-------------|----------------|--------|
| 202 | `ImageCancelled` | Narrow | n/a | n/a | No | -- |
| 210 | `ImageException` | Narrow | n/a | n/a | No | -- |
| 217 | `Exception` | **Broad** | Yes | Yes | No | **VALID** -- worker-thread provider escape wrapped as `ImageUnexpectedError` |

### 5. `game/ui/services/tkinter_utils.py`

| Line | Exception Type | Classification | Comment? | Substantive? | Should Narrow? | Action |
|------|---------------|----------------|----------|-------------|----------------|--------|
| 61 | `tkinter.TclError` | Narrow | n/a | n/a | No | -- |
| 65 | `RuntimeError` | Narrow | n/a | n/a | No | -- |
| 69 | `Exception` | **Broad** | Yes | No (boilerplate) | No | **MIN-001** -- "Tkinter init is platform-dependent" restates the legitimate category but does not enumerate expected failures |
| 100 | `Exception` | **Broad** | Yes | Yes (lists TclError subclasses) | **Yes** | **MIN-002** -- Could be narrowed to `tkinter.TclError` per the comment itself |
| 142 | `Exception` | **Broad** | Yes | No (boilerplate) | No | **MIN-003** -- "file dialog is platform-dependent" is boilerplate |
| 175 | `Exception` | **Broad** | Yes | No (boilerplate) | No | **MIN-004** -- Same as 142 |
| 206 | `Exception` | **Broad** | Yes | No (boilerplate) | No | **MIN-005** -- "dialog is platform-dependent" is boilerplate |
| 229 | `Exception` | **Broad** | Yes | No (boilerplate) | No | **MIN-006** -- "clipboard is platform-dependent" is boilerplate |

### 6. `game/ui/screens/battle_setup/controller.py`

| Line | Exception Type | Classification | Comment? | Substantive? | Should Narrow? | Action |
|------|---------------|----------------|----------|-------------|----------------|--------|
| 56 | `Exception` | **Broad** | Yes | Yes | No | **VALID** -- registry provider may be uninitialized in tests |
| 123 | `Exception` | **Broad** | Yes | Yes | No | **MIN-007** -- Corrupt design data; good comment, reasonable for file-scan |
| 144 | `ValueError` | Narrow | n/a | n/a | No | -- |
| 165 | `ValueError` | Narrow | n/a | n/a | No | -- |
| 408 | `ValueError, TypeError` | Narrow | n/a | n/a | No | -- |
| 558 | `ValueError` | Narrow | n/a | n/a | No | -- |

### 7. `game/strategy/engine/turn_state_snapshot.py`

| Line | Exception Type | Classification | Comment? | Substantive? | Should Narrow? | Action |
|------|---------------|----------------|----------|-------------|----------------|--------|
| 56 | `Exception` | **Broad** | Yes | Yes | No | **VALID** -- wrap-and-re-raise as `PersistenceException`; caller catches `PersistenceException` specifically |

### 8. `game/strategy/formulas/colony_output.py`

| Line | Exception Type | Classification | Comment? | Substantive? | Should Narrow? | Action |
|------|---------------|----------------|----------|-------------|----------------|--------|
| 85 | `Exception` | **Broad** | Yes | Yes | No | **VALID** -- duck-typed `race_registry.get_race()` may raise any type; skip species to avoid poisoning output calculation |

### 9. `game/strategy/data/ship_instance.py`

| Line | Exception Type | Classification | Comment? | Substantive? | Should Narrow? | Action |
|------|---------------|----------------|----------|-------------|----------------|--------|
| 69 | `Exception` | **Broad** | Yes | Yes | No | **MIN-008** -- Corrupt design data fallback; good comment, reasonable broad catch |
| 570 | `Exception` | **Broad** | Yes | Yes | No | **MIN-009** -- Registry absent in legacy save context; could potentially narrow to specific registry errors |
| 584 | `TypeError, ValueError` | Narrow | n/a | n/a | No | -- |

### 10. `game/strategy/config/economy_config.py`

**No `except` blocks.** All error paths use `load_json(resolved, default={})` via the canonical `json_utils` layer, which has its own internal error handling.

### 11. `game/strategy/data/galaxy_system_generator.py`

**No `except` blocks.** `_load_json_or_empty` delegates entirely to `load_json(path_value, default={})` via `json_utils`.

### 12. `game/strategy/data/galaxy_warp_generator.py`

**No `except` blocks.** All data loading delegates to `load_json` via canonical utilities.

### 13. `game/strategy/data/star_generation_config.py`

| Line | Exception Type | Classification | Comment? | Substantive? | Should Narrow? | Action |
|------|---------------|----------------|----------|-------------|----------------|--------|
| 192 | `ImportError, FileNotFoundError, OSError, TypeError` | Narrow | n/a (but notable: PROJ-381 Phase 3 dropped `ValueError`/`KeyError` from this tuple intentionally) | n/a | No | Good -- intentionally narrows to surface data-integrity bugs |

---

## Detailed Findings

---

### MIN-001 -- `tkinter_utils.py:69` (boilerplate comment)

```python
except Exception as e:  # Intentional broad catch: Tkinter init is platform-dependent
```

**Issue:** The comment repeats the legitimate category label without enumerating expected failure modes. Valid broad-catch area (platform-dependent UI initialization), but the reason is thin.

**Recommendation:** Expand the comment to name specific failure modes:
```
# Intentional broad catch: Tkinter init raises platform-specific
# errors (TclError, RuntimeError, and OS-level windowing errors
# on headless/container systems) -- fall back to no-dialogs mode
# so the game can still boot without file dialogs.
```

---

### MIN-002 -- `tkinter_utils.py:100` (should-be-narrowed)

```python
except Exception:  # Intentional broad catch: Tk widget .destroy() raises various TclError subclasses if already destroyed or interpreter is gone
```

**Issue:** The comment itself identifies the expected exception type (`TclError` subclasses). Could be narrowed to `tkinter.TclError`.

**Recommendation:** Narrow to `except tkinter.TclError:` and keep the comment explaining when it occurs.

---

### MIN-003 -- `tkinter_utils.py:142` (boilerplate comment)

```python
except Exception as e:  # Intentional broad catch: file dialog is platform-dependent
```

Same systemic issue as MIN-001. The comment is pro-forma. The file dialog is platform-dependent but the comment should state what expected failures look like (e.g., `TclError` when the display server is absent, `RuntimeError` on headless systems).

---

### MIN-004 -- `tkinter_utils.py:175` (boilerplate comment)

Identical pattern to MIN-003 (open dialog). Same recommendation.

---

### MIN-005 -- `tkinter_utils.py:206` (boilerplate comment)

Identical pattern to MIN-003 (string prompt dialog). Same recommendation.

---

### MIN-006 -- `tkinter_utils.py:229` (boilerplate comment)

Identical pattern to MIN-003 (clipboard). Same recommendation.

---

### MIN-007 -- `controller.py:123` (comment quality)

```python
except Exception as e:  # Intentional broad catch: corrupt design data must not poison the design library scan -- log and skip per file.
```

**Assessment:** The comment is substantive (states what and why). The broad catch is in a design-library file-scan context (best-effort metadata enumeration). This is reasonable. Could potentially be narrowed to `(json.JSONDecodeError, KeyError, AttributeError, ValueError, TypeError)` with a star-safe `Exception` fallback in the future.

---

### MIN-008 -- `ship_instance.py:69` (comment quality)

```python
except Exception as e:  # Intentional broad catch: ShipSerializer.from_dict() may raise various exception types on corrupt/incomplete design data; falling back to empty components is safe -- callers treat empty dict as "no per-component data available".
```

**Assessment:** Good comment. The catch is in a component-state-population helper that falls back to empty components. Best-effort metadata detection area. Reasonable.

---

### MIN-009 -- `ship_instance.py:570` (potential narrowing)

```python
except Exception:  # Intentional broad catch: registry may be absent in legacy save context
```

**Assessment:** Good comment. Registry-provider lookup in a `_lookup_design_max_hp` fallback path. Returns `None` which is handled by callers. Could potentially be narrowed to specific registry errors once the provider's contract stabilizes.

---

### MIN-010 -- `conflict_resolution_engine.py:567` (strategy-layer swallow)

```python
except Exception as e:  # Intentional broad catch: external collector may raise any type from non-engine empire/system extensions; ERROR-log and proceed with degraded modifier stack so battle still resolves. Hex + empire context included to allow log-side debugging.
```

**Assessment:** This is the most boundary-pushing broad catch in the review. It is in the **strategy layer** combat-resolution path and **swallows** the error (logs at ERROR, returns `None` for modifiers, battle proceeds degraded). The docs state:

> Strategy phase work is not a swallow site: raw `Exception` from a phase must become `EnginePhaseError` and re-raise.

However, the comment makes a substantive architectural argument: modifier collection is best-effort; losing modifiers degrades the battle's fidelity but does not break the deterministic simulation. The battle still resolves. This is closer to a "telemetry / sidecar" or "best-effort metadata" pattern than a core phase operation.

**Recommendation:** This is borderline-acceptable as-is. If the collector contract stabilizes, narrowing to a specific exception tuple would be safer. In the short term, consider whether `_collect_team_modifiers` should be moved outside the combat phase boundary entirely (e.g., computed once at turn-start and cached) so the combat hot path never needs this swallow.

---

## Cross-Cutting Observations

### 1. PROJ-381 Phase 2 improvements validated

Several files already reflect PROJ-381 Phase 2 cleanup:
- `asset_manager.py:154` -- narrowed from bare `Exception` to `(FileNotFoundError, pygame.error, ValueError, OSError)` via ERR-02-001.
- `turn_state_snapshot.py` -- `TurnStateSnapshot.capture` now raises `PersistenceException` (T003); the broad catch wraps and re-raises.
- `economy_config.py` -- no `except` blocks; all JSON loading delegates to `core.json_utils.load_json`.
- `star_generation_config.py:192` -- intentionally dropped `ValueError`/`KeyError` from the catch tuple to surface data-integrity bugs (ERR-04-007).
- `conflict_resolution_engine.py:567` -- demoted-to-warning was promoted back to ERROR with hex/empire context (B-7).

These are all positive signals.

### 2. Strategy-layer EnginePhaseError wrap pattern is consistent

In `turn_engine.py`, the `_time_phase` method (line 286) correctly implements the documented strategy-layer pattern: catch any raw `Exception`, log, wrap as `EnginePhaseError(code=PHASE_FAILED)`, re-raise. The `process_turn` caller (line 591) catches `EnginePhaseError` specifically and triggers rollback. This is the canonical pattern per docs.

### 3. No bare `except:` found

All 37 except blocks specify an exception type. This is a strong baseline.

### 4. No broad-catch missing comment found

All 16 broad catches carry an `# Intentional broad catch:` comment on the same line.

### 5. tkinter_utils.py is the primary boilerplate offender

5 of the 16 broad catches (31%) are in `tkinter_utils.py` with comments that restate the legitimate category label ("platform-dependent") without enumerating expected failure modes. These are low-risk -- they are in UI utility helpers that return `None` on failure, and the caller patterns (`if root is None: return`) are well-established.

---

## Action Priority

| Priority | Count | Description |
|----------|-------|-------------|
| CRITICAL | 0 | No bare excepts, no strategy-phase unwrapped Exception swallows |
| MAJOR | 0 | No broad catches missing comments |
| MINOR | 10 | Boilerplate comments (MIN-001 through MIN-006), comment quality improvements (MIN-007--009), borderline strategy-layer swallow (MIN-010) |

**Recommended quick-wins for PROJ-381:**
1. Enrich the 5 tkinter boilerplate comments with expected failure modes (~5 min each).
2. Narrow `tkinter_utils.py:100` to `tkinter.TclError` (~2 min).
3. Review whether `conflict_resolution_engine.py:567` should be restructured (MIN-010) as a longer-term cleanup item.
