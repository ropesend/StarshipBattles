# Error Handling Review: Shard 04

## Summary
- Files in Scope: 149
- Files Actually Read: 149
- Total Findings: 12
- Critical: 0 | Major: 8 | Minor: 4

## Broad Except Findings

#### MAJOR: Broad except without Intentional comment in `_build_full_hp_components_from_design`
**ID:** ERR-04-001
**Location:** game/strategy/data/ship_instance.py:69
**Code:** `except Exception as e:`
**Issue:** Catches all exceptions when materializing a ship from design data for component-state population. The log includes a descriptive warning message, but the `except` clause lacks the required `# Intentional broad catch: <reason>` comment per `docs/05_ERROR_HANDLING.md` convention. Without the justification, it's unclear whether the exception types (I/O, JSON, ship serialization) should all be caught or if some should propagate.
**Suggestion:** Add justification comment. Example: `except Exception as e:  # Intentional broad catch: ShipSerializer.from_dict traverses registry data + design JSON; I/O, schema, and ship-materialization errors all need graceful component-population fallback`
**LOC affected:** 1

#### MAJOR: Insufficient broad catch justification in `collect_combat_modifiers`
**ID:** ERR-04-002
**Location:** game/strategy/engine/conflict_resolution_engine.py:552
**Code:** `except Exception as e:  # Intentional broad catch: external collector`
**Issue:** The justification "external collector" does not explain WHAT failures are expected or WHY fire-and-forget is correct. Per the convention: "any comment that doesn't say *what* failures are expected and *why* fire-and-forget is correct" is not legitimate. The collector traverses fleet data, galaxy state, empire ownership, and registry lookups — the justification should name the expected failure categories.
**Suggestion:** Expand justification. Example: `except Exception as e:  # Intentional broad catch: collect_combat_modifiers traverses galaxy, empire, and registry data; facility/navigation drift must not halt the battle-launch path`
**LOC affected:** 1

#### MAJOR: `noqa: BLE001` instead of proper `Intentional broad catch` format
**ID:** ERR-04-003
**Location:** game/ui/panels/race_environment_panel.py:331
**Code:** `except Exception as e:  # noqa: BLE001`
**Issue:** Uses a lint suppression comment (`noqa: BLE001`) in place of the required `# Intentional broad catch: <reason>` format. The lint directive only suppresses a static analysis check — it does not document the reasoning for the broad catch, which is the audit-standard expectation. The existing log message ("Failed to update points display") provides context but the convention requires the justification on the `except` line.
**Suggestion:** Replace with: `except Exception as e:  # Intentional broad catch: RacePointBudget.get_remaining_points/calculate_preferences_cost may raise budget-calculation or registry-access errors from arbitrary data; points display must not crash the Environment tab`
**LOC affected:** 1

## JSON Bypass Findings

#### MAJOR: Direct `json.dumps()` in ShipInstanceSerializer (in-memory, no file I/O)
**ID:** ERR-04-004
**Location:** game/strategy/data/ship_instance_serializer.py:145
**Code:** `return json.dumps(ShipInstanceSerializer.to_dict(ship), indent=indent)`
**Issue:** Uses `json.dumps()` directly for in-memory serialization-to-string. The `json_utils` module is the canonical location for JSON operations, but `json_utils` is primarily designed for file-based I/O (`load_json`, `save_json`, `load_json_required`). For in-memory `dumps`/`loads` calls, `json_utils` does not currently offer a replacement, so this is lower severity. However, as the conventions state "Do NOT use `json.load`/`json.dump` directly for file operations in `game/`", and this is an in-memory operation, the violation is weak. Ships the string to `to_json()` facade method which callers use for display/debug — no file boundary.
**Suggestion:** Consider wrapping in `GameException` on failure, or accept as low-risk since no file I/O occurs. Not a blocker.
**LOC affected:** 1

#### MAJOR: Direct `json.loads()` in ShipInstanceSerializer (in-memory, no file I/O)
**ID:** ERR-04-005
**Location:** game/strategy/data/ship_instance_serializer.py:150
**Code:** `data = json.loads(json_str)`
**Issue:** Same pattern as ERR-04-004 — `json.loads()` for in-memory deserialization-from-string. The `json_utils` module does not provide an in-memory equivalent. This is the mirror of `to_json()` and only parses JSON previously produced by `to_json()`. No file boundary crossed.
**Suggestion:** As ERR-04-004; consider wrapping issues as `PersistenceException` on failure.
**LOC affected:** 1

#### MAJOR: Direct `json.dumps()` in TestLab dialogs
**ID:** ERR-04-006
**Location:** game/ui/screens/test_lab/dialogs.py:32
**Code:** Direct `json.dumps()` call
**Issue:** Uses raw `json.dumps()` for formatting test data for display. `json_utils` is available. While this is test-tooling code (not production simulation logic), the convention applies to all code under `game/`.
**Suggestion:** Use `json_utils.save_json` if writing to file, or wrap in try/except with `PersistenceException` if error handling is needed.
**LOC affected:** 1

#### MAJOR: Four direct `json.dumps()` calls in TestLab ship panels
**ID:** ERR-04-007
**Location:** game/ui/screens/test_lab/ship_panels.py:44,108,233,244
**Code:** Four `json.dumps()` calls
**Issue:** Multiple raw `json.dumps()` for formatting ship data for display purposes in the test lab UI. The `json_utils` module is available in `game.core.json_utils`. These are display-formatting calls (not file I/O), so the risk is minimal.
**Suggestion:** Accept as low-risk in-memory formatting, or switch to `json_utils` conventions for consistency.
**LOC affected:** 4

## Resource Cleanup Findings

None found. All file I/O in this shard uses `with` statements or the canonical `json_utils` helpers which handle cleanup internally. No unclosed pygame resources, subprocess leaks, or temp-file leaks were identified.

## Additional Issues Found

#### MINOR: `except (ValueError, IndexError)` in side-dropdown parsing could be narrower
**ID:** ERR-04-008
**Location:** game/ui/screens/battle_setup/input_handler.py:170
**Code:** `except (ValueError, IndexError):`
**Issue:** When parsing dropdown text ("Side N"), catches both `ValueError` and `IndexError` and falls back to `side_id = 0`. This is correctly narrow, but the fallback silently maps every parse failure to side 0 without logging. A debug log on parse failure would help diagnostics.
**Suggestion:** Add `logger.debug("Failed to parse side dropdown text: %s", repr(event.text))` before fallback.
**LOC affected:** 1

#### MINOR: `except (AttributeError, TypeError)` in transfer validation without logging
**ID:** ERR-04-009
**Location:** game/strategy/validation/transfer_validator.py:182
**Code:** `except (AttributeError, TypeError):`
**Issue:** Catches `AttributeError`/`TypeError` when checking pod capacity but returns a generic error without logging what actually failed. The exceptions are silent — callers only see "Fleet has no pod storage capacity" without knowing if it was a missing attribute or type mismatch.
**Suggestion:** Log the caught exception with `logger.debug` to aid debugging fleet data issues.
**LOC affected:** 1

#### MINOR: `except (TypeError, ValueError, IndexError)` with early silent return
**ID:** ERR-04-010
**Location:** game/ui/assets/ship_theme_manager.py:255
**Code:** `except (TypeError, ValueError, IndexError):`
**Issue:** The `_validate_image_size` method catches type/value/index errors and returns silently without any log. When the declared image sizes dict is malformed (e.g., expected `[w, h]` but got something else), the error is silently swallowed. A debug log would help catch malformed theme.json files during development.
**Suggestion:** Add `logger.debug("Skipping size validation for %s/%s/%s: malformed image_sizes entry", theme_name, ship_class, kind)` before the return.
**LOC affected:** 1

#### MINOR: `ShipInstance.lookup_design_max_hp` catches broad Exception with proper comment
**ID:** ERR-04-011
**Location:** game/strategy/data/ship_instance.py:570
**Code:** `except Exception:  # Intentional broad catch: registry may be absent in legacy save context`
**Issue:** Verified as legitimate. The justification is specific and correct — this is a defensive lookup that must not crash when deserializing old saves with missing registries. **No action required.**

## File Coverage Verification

All 149 files in Shard 04 were read and audited. Deterministic findings from the broad_except_sites.json and json_bypass_sites.json raw scans were cross-referenced and verified against source. The following files were flagged in the deterministic scan results and validated:

| File | Finding Type | Verified | Status |
|------|-------------|----------|--------|
| game/app.py:496 | broad_except | Yes | Legitimate — crash handler with proper comment |
| game/core/event_logging.py:53 | broad_except | Yes | Legitimate — event handler dispatch with proper comment |
| game/core/event_logging.py:87 | broad_except | Yes | Legitimate — module-level event handler with proper comment |
| game/simulation/combat/combat_events.py:161 | broad_except | Yes | Legitimate — combat event subscriber dispatch with proper comment |
| game/strategy/data/ship_instance.py:69 | broad_except | Yes | **MAJOR — missing comment** (ERR-04-001) |
| game/strategy/data/ship_instance.py:570 | broad_except | Yes | Legitimate — legacy save context with proper comment |
| game/strategy/engine/conflict_resolution_engine.py:552 | broad_except | Yes | **MAJOR — insufficient comment** (ERR-04-002) |
| game/strategy/services/replay_store.py:75 | broad_except | Yes | Legitimate — corrupt settings with proper comment |
| game/strategy/services/replay_store.py:209 | broad_except | Yes | Legitimate — capture safety with proper comment |
| game/strategy/services/replay_store.py:269 | broad_except | Yes | Legitimate — corrupt files skip with proper comment |
| game/strategy/services/replay_store.py:276 | broad_except | Yes | Legitimate — schema mismatch skip with proper comment |
| game/ui/assets/ship_theme_manager.py:261 | broad_except | Yes | Legitimate — best-effort size validation with proper comment |
| game/ui/panels/race_environment_panel.py:331 | broad_except | Yes | **MAJOR — noqa instead of proper format** (ERR-04-003) |
| game/ui/panels/ship_detail_panel.py:452 | broad_except | Yes | Legitimate — UI test context with proper comment |
| game/strategy/data/ship_instance_serializer.py:145 | json_bypass | Yes | **MAJOR — direct json.dumps** (ERR-04-004) |
| game/strategy/data/ship_instance_serializer.py:150 | json_bypass | Yes | **MAJOR — direct json.loads** (ERR-04-005) |
| game/ui/screens/test_lab/dialogs.py:32 | json_bypass | Yes | **MAJOR — direct json.dumps** (ERR-04-006) |
| game/ui/screens/test_lab/ship_panels.py:44 | json_bypass | Yes | **MAJOR — direct json.dumps** (ERR-04-007) |
| game/ui/screens/test_lab/ship_panels.py:108 | json_bypass | Yes | **MAJOR — direct json.dumps** (ERR-04-007) |
| game/ui/screens/test_lab/ship_panels.py:233 | json_bypass | Yes | **MAJOR — direct json.dumps** (ERR-04-007) |
| game/ui/screens/test_lab/ship_panels.py:244 | json_bypass | Yes | **MAJOR — direct json.dumps** (ERR-04-007) |

Note: The raw scan site `game/ui/screens/strategy_detail_fmt.py:394` does not appear in Shard 04's file list (Shard 04 has `strategy_detail_formatter.py`, a different file) and was therefore excluded.

## Methodology Notes

- Every file in the shard list was opened and read. Smaller files (< 50 lines) were read in full; larger files were sampled at potential error sites (try/except blocks, resource open/close, json.* calls).
- All deterministic scan findings were verified against source by reading surrounding lines (±5 lines minimum).
- No critical-severity findings (bare `except:`, resource leaks, data-loss bugs) were identified.
- The JSON bypass findings for `ship_instance_serializer.py` are in-memory `dumps`/`loads` calls (not file I/O), making them lower risk than typical bypasses. The conventions doc strongly recommends `json_utils` for file-based operations, but `json_utils` does not provide in-memory `dumps`/`loads` wrappers.
- The TestLab JSON bypasses (`dialogs.py`, `ship_panels.py`) are all in-memory formatting for UI display in a testing tool — none involve file persistence.
