# PROJ-382 Pattern Docs & PROJ-381 Cross-Impact Review

**Review date:** 2026-05-08
**Scope:** `docs/02_PATTERNS.md` Patterns #7, #12, #23, #36; PROJ-381/PROJ-382 cross-impact on `game_session.py`, `turn_engine.py`, `exceptions.py`, `json_utils` audit sites.

---

## Findings

### DOC-01-P36: MAJOR — Pattern #36 "when not to use" missing explicit facade-bypass (Pattern #5) guard

**File:** docs/02_PATTERNS.md:761-769
**Evidence:** The "When NOT to use" section lists three prohibitions:
1. Compatibility with old save files or external API consumers (Rule 3)
2. Papering over genuinely unmigrated state — "does not legitimize a permanent two-path import surface"
3. When the canonical home is uncertain

None of the three mention Pattern #5 (Facade/Delegate) bypass.
**Assessment:** PROJ-382 Phase 1 specifically detected and removed facade-bypass violations. If Pattern #36 is documented without an explicit prohibition on bypassing the Facade, the pattern could later be cited as rubber-stamp justification for a shim that re-exports internal delegate symbols — reopening the very holes Phase 1 closed. The "unmigrated state" bullet addresses permanence but not architectural layering. A shim that re-exports symbols the Facade is supposed to hide is an architectural violation regardless of whether it's temporary.
**Recommendation:** Add a fourth bullet to "When NOT to use":
```
- To create a public import surface that bypasses a Facade (Pattern #5).
  If the canonical module exposes internal delegates that the Facade
  hides, the shim inherits that exposure — a facade-bypass.
  Facade-bypass sites must route through the Facade, not through a
  re-export shim.
```

---

### DOC-02-P36: MINOR — Pattern #36 structure diverges from neighboring pattern templates

**File:** docs/02_PATTERNS.md:722-778
**Evidence:** Neighboring patterns (#35, #34, #33) follow a consistent "Where: → Contract:" template with bullet-point rules. Pattern #36 uses a unique prose structure: "Problem the pattern solves → Structure → When to use → When NOT to use → Retirement." Pattern #12 (Configuration Classes) uses a hybrid "Last verified → Where → Contracts: → three variants" approach that's closer to the template.
**Assessment:** The prose structure is clear and thorough but breaks the skimmable reference contract of "Where" then "Contract" bullet points that every other pattern uses. Automated doc tooling and grep-based pattern lookups won't find "Contract:" anchored rules in this section.
**Recommendation:** Restructure to match the prevailing template:
```
## 36. Re-Export Shim

> **Last verified:** 2026-05-08

Where (4 confirmed sites at PROJ-382 verification, 2026-05-07):
    - `game/ui/screens/race_setup_screen.py` — re-exports from `race_setup/`.
    - `game/ui/screens/test_lab/test_run_details.py` — re-exports from `details/`.
    - `game/simulation/components/component.py:395-405` — re-exports loader symbols.
    - `game/strategy/engine/command_handlers.py` — re-exports from `handlers/base.py`.

Contract:
    - A thin module (≤~30 LOC) containing only `from <canonical> import <name>` plus `__all__`.
    - Header docstring identifies the canonical module and introducing project/migration.
    - Tests import from the canonical module; only import-path coverage tests remain on the shim.
    - Use when decomposing a god-module, renaming a module, or promoting an internal symbol.
    - Do NOT use for save-file compat, unmigrated-state permanence, uncertain canonical
      homes, or facade (Pattern #5) bypass.
    - Each shim ties to a tracked migration project; delete when zero call sites remain.
```

---

### DOC-03-P36: MINOR — Two of four confirmed shim sites lack retirement migration projects

**File:** docs/02_PATTERNS.md:771-778
**Evidence:** Retirement section states: "Each shim should reference the project responsible for migrating its callers (e.g. PROJ-302 for race_setup, PROJ-382 audit for the command_handlers shim)." This covers only 2 of 4 sites. The `component.py:395-405` loader-symbol shim and the `test_run_details.py` shim have no tracked migration project.
**Assessment:** Without assigned retirement owners, these two shims risk becoming permanent fixtures, contradicting the "transitional" contract in the same documentation. The clause "a future audit may add a static check" is aspirational with no timeline.
**Recommendation:** Either (a) file PROJ tickets for `component.py` loader-shim and `test_run_details.py` shim retirement, or (b) add explicit "not-yet-scheduled" entries acknowledging the gap and the retirement-owner requirement.

---

### DOC-04-P23: INFO — Pattern #23 phase count is correct (6 phases, not 5)

**File:** docs/02_PATTERNS.md:447-451; game/simulation/systems/tick_phase.py:183-201
**Evidence:** Doc lists six phases: `RebuildGridPhase(100)`, `AIAndShipUpdatePhase(200)`, `BoundaryEnforcementPhase(250)`, `AttackProcessingPhase(300)`, `RammingPhase(400)`, `ProjectileUpdatePhase(500)`. Code's `create_default_phases()` registers exactly these 6 in the same priority order. All six class names carry the `Phase` suffix as documented.
**Assessment:** The doc drift concern in the request ("If it still lists 5, the doc drift wasn't fixed") was either already addressed by Phase 3 or was never present. The documentation is accurate.
**Recommendation:** No fix needed.

---

### DOC-05-P7: INFO — Pattern #7 canonical path is correct and references the re-export shim

**File:** docs/02_PATTERNS.md:164-170; game/strategy/engine/command_handlers.py:1-82; game/strategy/engine/handlers/base.py:1-30
**Evidence:** Doc canonical path: `game/strategy/engine/handlers/base.py` (line 167). The legacy `command_handlers.py` is described as "a transitional re-export shim" with a cross-reference to Pattern #36 (lines 168-170). The shim file itself has a docstring explicitly identifying the canonical module and PROJ-309 sub-phase 3.5 as the decomposition origin (lines 1-6 of `command_handlers.py`). The `handlers/base.py` file confirms it owns `BaseCommandHandler`, `CommandHandlerRegistry`, `ICommandHandler`, and `add_move_order_if_needed`.
**Assessment:** Documentation is accurate and internally consistent.
**Recommendation:** No fix needed.

---

### DOC-06-P12: INFO — Pattern #12 third variant (module-accessor pair) properly documented with justification

**File:** docs/02_PATTERNS.md:281; game/strategy/config/economy_config.py:132-147
**Evidence:** Pattern #12 documents three variant flavors. The third ("Module-accessor pair `get_default_*` / `set_default_*`") is documented at line 281 with: (a) precise file reference `economy_config.py:136-149`, (b) in-code justification reproduced verbatim, (c) transparent note that it "was below the usual 3-site bar" but elevated because "the in-code justification is explicit and the variant is intentional rather than accidental." Code matches: `_default = None` module variable, `get_default_economy_config()` lazy-loads, `set_default_economy_config(cfg)` allows test-swap.
**Assessment:** Well-documented. The transparent acknowledgement of the exception to the 3-site bar demonstrates good documentation practices.
**Recommendation:** No fix needed.

---

### CROSS-01-GS: INFO — Tautology guard removal and PROJ-381 null-object init are independent — no conflict

**File:** game/strategy/engine/game_session.py:369-372, 153-174
**Evidence:** The tautology guard removal (PROJ-382 Phase 3) affected `handle_command()` at line 369 — the command dispatch path. The null-object recovery (PROJ-381 Phase 2 B-11) is in `__init__` at lines 153-174 — the session creation path. These are disjoint code sections. `SessionInitializationError` is imported from `game.core.exceptions` (line 157), raised from the `except Exception` block (line 171), and correctly preserves the original exception via `from e`. The null-object assignments (`galaxy = None`, `empires = []`, etc.) precede the `raise`, establishing a deterministic partial-construction state.
**Assessment:** No conflict. Both changes apply to completely separate methods. `SessionInitializationError` is properly raised. The tautology guard removal does not drop any call site that PROJ-381's null-object recovery relied on.
**Recommendation:** No fix needed.

---

### CROSS-02-GS: MINOR — `from_dict` has no null-object recovery equivalent

**File:** game/strategy/engine/game_session.py:418-550
**Evidence:** `__init__` (lines 153-174) wraps `GameInitializer.initialize()` in try/except that sets null-object state (`galaxy=None`, `empires=[]`, etc.) and raises `SessionInitializationError`. `from_dict` (lines 418-550) loads Galaxy (line 492) and Empires (line 503) with individual `PersistenceException` raises for missing keys, but has no top-level safety net. If Galaxy loads successfully then Empire deserialization fails, `from_dict` returns a `GameSession` with `self.galaxy` populated but only partial empires — the exception propagates but the caller may hold a reference to the broken session.
**Assessment:** This is a pre-existing gap, not introduced by PROJ-381 or PROJ-382. PROJ-381's `SessionInitializationError` was designed for init-time `GameInitializer` failures, not `from_dict` reconstruction. The `__new__` bypass pattern in `from_dict` makes a null-object safety net harder to implement (many attributes are set in scattered order). This is a lower-severity observation because `from_dict` is a classmethod that either fully succeeds or raises — callers that catch the exception should not use the returned session.
**Recommendation:** Add a comment noting the intentional divergence from `__init__`'s null-object contract, or file a follow-up ticket to add a `from_dict` safety net in a future phase.

---

### CROSS-03-TE: INFO — TurnEngine correctly publics turn_number/save_path in EnginePhaseError context

**File:** game/strategy/engine/turn_engine.py:229-233, 292-308, 506-511
**Evidence:** PROJ-381 Phase 3 (B-2) seeds `_current_turn_number` and `_current_save_path` at `process_turn()` entry (lines 506-511, defensive `getattr` on session), then surfaces both in `_time_phase`'s `EnginePhaseError` context (lines 300-303). The `getattr(self, "_current_turn_number", 0)` pattern in `_time_phase` provides defense in depth against future refactors.
**Assessment:** Correct. The crash-dump breadcrumb contract is fulfilled.
**Recommendation:** No fix needed.

---

### CROSS-04-SWH: INFO — Superweapon command handlers correctly import from canonical path

**File:** game/strategy/engine/superweapon_command_handlers.py:15
**Evidence:** `BaseCommandHandler` and `add_move_order_if_needed` are imported from `game.strategy.engine.handlers.base` — the canonical path per Pattern #7. Unlike `game_session.py` (line 67, which still imports `create_default_registry` from the legacy shim), this file uses the canonical path directly.
**Assessment:** Correct usage. Demonstrates progressive migration from shim to canonical path.
**Recommendation:** No fix needed.

---

### JSON-01: INFO — All three bare `json` imports pass audit legitimacy check

**File:** game/strategy/systems/race_library.py:20, game/ui/screens/setup_data_io.py:18, game/ui/screens/builder/detail_panel.py:15
**Evidence:**
- `race_library.py` - imports `json` solely for `json.JSONDecodeError` (lines 101, 140). Deserialization routes through `RaceConfig.load` → `json_utils`. Comment at lines 14-19 documents the rationale.
- `setup_data_io.py` - imports `json` solely for `json.JSONDecodeError` (lines 76, 231). All file I/O uses `json_utils` (`load_json`, `load_json_required`, `save_json`). Comment at lines 15-18 documents the rationale.
- `detail_panel.py` - imports `json` for `json.dumps()` at line 201 — in-memory pretty-printing for a debug popup window. Not persistence. Comment at lines 11-14 documents that `json_utils` has no string-formatter helper (only file I/O wrappers).
**Assessment:** Legitimate per audit PAT-01-CFG-003 self-rejection criteria. All three files carry explicit comments explaining the exception. Two use only the exception type; one uses `json.dumps()` for a non-persistence purpose that `json_utils` does not cover.
**Recommendation:** No fix needed.

---

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 0     |
| MAJOR    | 1     |
| MINOR    | 3     |
| INFO     | 7     |
| **Total**| **11**|

**Key concerns:**
1. **MAJOR (DOC-01-P36):** Pattern #36's "when not to use" section does not mention Pattern #5 facade-bypass — a gap that could allow PROJ-382 Phase 1's work to be undone.
2. **MINOR (DOC-02-P36):** Pattern #36's prose structure doesn't match the template used by all other patterns.
3. **MINOR (DOC-03-P36):** Two of four confirmed shim sites have no tracked retirement projects.
4. **MINOR (CROSS-02-GS):** `from_dict` has no null-object recovery equivalent to `__init__`'s PROJ-381 safety net.
