# PROJ-375 Verifier Report (Independent)

**Verifier:** Claude (subagent)
**Verifying:** OpenCode review report at sibling `report.md`
**Branch tip:** c0f58bb0b on `feat/03c-phase-aware-execution`
**Method:** Read each cited file:line directly, compare against parent commit (`2d2cc3566~1`), inspect type contracts, check test surfaces.

---

## Verdict Matrix

| ID | Severity | Verdict | Notes |
|----|----------|---------|-------|
| MAJ-001 | MAJOR | CONFIRM (low practical risk) | Behavior change is real; OpenCode's recommendation (a) preferred |
| MIN-001 | MINOR | CONFIRM | `ImplodePlanetMissionCommandHandler` indeed retains old inline pattern; intentionally outside DUP-X-07 line range, not addressed |
| MIN-002 | MINOR | CONFIRM_REMEDIATION_REVISE | Both `_collect_storage_from_facility` AND `_collect_staging_capacity` are unmigrated — recommendation should cover both for consistency |
| MIN-003 | MINOR | CONFIRM | Zero direct tests for new helpers; existing `_get_harvester_info` tests target a different module |
| INFO-001 | INFO | CONFIRM | Generator at `component_inspector.py:303-355` matches description |
| INFO-002 | INFO | CONFIRM | `_resolve_player_planet` at `handlers/base.py:186-209` adds null-empire guard |
| INFO-003 | INFO | CONFIRM | `_apply_planet_environmental_target` at `planet_command_handlers.py:129-160` correctly detects empty-dict via isinstance check |
| INFO-004 | INFO | CONFIRM | 6 `@property` shims at `race_description_llm_controller.py:140-164` (file actually under `game/strategy/services/`, not `game/services/llm/` as report's INFO body cites — minor path nit) |
| INFO-005 | INFO | CONFIRM | All 4 mission handlers route through `_emit_validated_order`; ImplodePlanet excluded as MIN-001 |
| INFO-006 | INFO | CONFIRM | Both helpers present at `workshop_event_router.py:441-499` with parameterized resolver/setter |
| INFO-007 | INFO | CONFIRM | Template at `data_list_window_mixin.py:90-130` matches |
| INFO-008 | INFO | CONFIRM | Module-level helper at `structure_list_items.py:25-80` with documented duck-type contract |

**Counts:** 1 CONFIRM (MAJ), 2 CONFIRM + 1 CONFIRM_REMEDIATION_REVISE (MIN), 8 CONFIRM (INFO). 0 REJECT, 0 UNCERTAIN.

---

## Per-Finding Details (MAJ + MIN)

### MAJ-001 — CONFIRM (low practical risk)

**Evidence checked:**
- `game/strategy/engine/handlers/base.py:253-273` — `_emit_validated_order` returns `result` (not `ValidationResult.success()`).
- `game/strategy/engine/superweapon_command_handlers.py:246-248, 280-282, 315-317, 344-346` — all 4 mission handlers `return self._emit_validated_order(...)`.
- Parent commit (`2d2cc3566~1`) at the same call sites — old code unconditionally returned `ValidationResult.success()` after `fleet.add_order(...)`.
- `game/core/validation.py:64-160` — `ValidationResult` does support warnings (`warnings: List[str]`, `add_warning()` method, merged via `merge()`).
- `game/strategy/validation/superweapon_validator.py` — `grep "add_warning|\.warnings"` returns zero hits. The validator never populates warnings.

**Reasoning:** The behavior change is real — the new code propagates the validator's `result` (with its potential warnings) to the caller, where the old code dropped them. However, since `SuperweaponValidator` never adds warnings, no current call path observes a different return value. The risk surfaces only if a future contributor adds `result.add_warning(...)` to a `validate_*` method.

**Internal consistency:** The 4 direct command handlers (`ImplodePlanetCommandHandler`, etc.) already used `_emit_validated_order` before this commit — the mission handlers are now consistent with them.

**Recommendation:** OpenCode's option (a) — add a docstring sentence on `_emit_validated_order` clarifying that the returned `result` may contain warnings — is the right choice. Option (b) (suppressing warnings) would be a regression vs. the direct command handlers which already preserve them. Recommend Claude amend the docstring at `handlers/base.py:261-268` to read something like: "Returns the same `result` (preserving any warnings the validator emitted)."

---

### MIN-001 — CONFIRM

**Evidence checked:**
- `game/strategy/engine/superweapon_command_handlers.py:186-219` — `ImplodePlanetMissionCommandHandler` retains inline `Order(...)` + `fleet.add_order(...)` + `logger.info(...)` + `return ValidationResult.success()` pattern.
- `Projects/active_projects/PROJ-375/findings/verification_report.md` — DUP-X-07 line range explicitly listed as `222-353`, which starts at `StellerateStarMissionCommandHandler` and excludes the implode handler at `186-219`. The exclusion is therefore an artifact of how the audit drew its line range, not a deliberate decision recorded anywhere.

**Reasoning:** The pattern is identical (`Order(OrderType.IMPLODE_PLANET, target=planet)` → `fleet.add_order(action_order)` → log → `return ValidationResult.success()`). Migrating it preserves consistency in the same file — the file currently has 4 handlers using the helper and 1 not. This is a low-risk follow-up.

**Recommendation:** Accept as a 3-line follow-up. Either fold into PROJ-375 closeout (preferred — keeps the cluster fully consolidated) or file a tiny follow-up ticket. Adopting OpenCode's MAJ-001 docstring fix as part of the same touch is natural since both edits live in the same file region.

---

### MIN-002 — CONFIRM_REMEDIATION_REVISE

**Evidence checked:**
- `game/strategy/engine/harvesting_engine.py:238-249` — `_collect_staging_capacity` does manual list-normalization (lines 245-246) before iteration.
- Same file, lines 258-275 — `_collect_storage_from_facility` ALSO does manual list-normalization (lines 269-270). It was not migrated either.
- The shared generator `iter_facility_ability_entries` (in `component_inspector.py:303-355`) handles dict/list/scalar normalization itself.
- INFO-001 in the report itself says "harvesting_engine.py … remain on old wrappers, not migrated (see design decision: harvesting_engine uses `get_harvester_info` et al. thin wrappers rather than direct generator calls)" — but neither the project decisions.md nor an inline comment records this as a deliberate design choice. It looks like an omission rather than a decision.

**Reasoning:** OpenCode's MIN-002 is correct that `_collect_staging_capacity` could be migrated, but it's incomplete: `_collect_storage_from_facility` and `_process_facility` (line 357) all use the same hand-rolled normalization pattern in the same file. A consistent follow-up should migrate all three together (or none).

**Revised recommendation:** Either (1) migrate all three loops (`_collect_storage_from_facility`, `_collect_staging_capacity`, and `_process_facility`) to `iter_facility_ability_entries` in one follow-up, or (2) add an explicit comment in `harvesting_engine.py` documenting the intentional choice to keep the thin-wrapper layer. Choosing one or the other ends the inconsistency. Recommend (1) — the migration is mechanical and the wrappers (`get_harvester_info`, `_get_storage_info`, `_get_staging_info`) can either be deleted (zero external callers in `tests/`) or kept as backward-compat aliases if any external code uses them.

---

### MIN-003 — CONFIRM

**Evidence checked:**
- `grep -n "_get_ability_info\|_get_ability_data_from_registry" tests/` — zero hits.
- Other `_get_harvester_info` matches in tests (`test_planet_report_panel.py`, `test_strategy_detail_formatter.py`) target `game/strategy/services/planet_economy_projector.py`, NOT the new `harvesting_engine` helpers. They are unrelated.
- `harvesting_engine.py:38-91` — the new `_get_ability_info` and `_get_ability_data_from_registry` have non-trivial branches: dict-with-inline-abilities, dict-with-only-id-then-registry, plain-string-id-via-registry, scalar-data-falls-through (returns None), missing-registry edge cases.

**Reasoning:** The integration tests for `HarvestingEngine` exercise a happy-path subset (dict-with-inline-abilities), but the registry-fallback path and the string-component-id path are reachable through real save data and aren't directly verified. MIN-003's recommendation is sound.

**Recommendation:** Accept the recommendation. 4-5 unit tests in `tests/unit/strategy/engine/test_harvesting_engine.py` (or a new dedicated test file) covering: (a) dict with inline ability, (b) dict with no inline → registry hit, (c) plain string ID → registry hit, (d) registry miss → None, (e) scalar ability data → None (falls through to registry path correctly). Trivial to add (~30 LOC).

---

## INFO Findings — One-Line Confirms

- **INFO-001:** CONFIRM — generator at `component_inspector.py:303-355` matches all four normalization rules (dict/list-of-dicts/list-of-non-dicts/scalar).
- **INFO-002:** CONFIRM — `_resolve_player_planet` at `handlers/base.py:186-209` includes the `active_empire is None` guard the inline sites lacked.
- **INFO-003:** CONFIRM — `_apply_planet_environmental_target` at `planet_command_handlers.py:129-160` uses `(value is None) or (isinstance(value, dict) and not value)` for the clear-detection — matches OpenCode's analysis.
- **INFO-004:** CONFIRM — 6 `@property` accessors at `race_description_llm_controller.py:140-164` (note: file lives at `game/strategy/services/race_description_llm_controller.py`, not the path the INFO body cites — irrelevant to correctness).
- **INFO-005:** CONFIRM — all 4 mission handlers cleanly route through `_emit_validated_order`; cosmetic log change ("Queued X mission" → "Issued X mission order") is the only string drift.
- **INFO-006:** CONFIRM — `_apply_resolver_dropdown` and `_apply_confirmation_dropdown` at `workshop_event_router.py:441-499` are present with the documented strategy split.
- **INFO-007:** CONFIRM — `_run_update_template` at `data_list_window_mixin.py:90-130` matches the documented 4-step template.
- **INFO-008:** CONFIRM — module-level `_rebuild_modifier_icons_for_item` at `structure_list_items.py:25-80` accesses only the duck-typed surface listed in its docstring.

---

## Recommended Actions for Claude

**Fix now (one small commit):**
1. **MAJ-001 docstring fix** — amend `_emit_validated_order` docstring at `game/strategy/engine/handlers/base.py:261-268` to clarify: "Returns the same `result` (preserving any warnings the validator emitted) so callers can `return self._emit_validated_order(...)`." Zero behavior change, locks in current contract.
2. **MIN-001 trivial migration** — route `ImplodePlanetMissionCommandHandler` (`superweapon_command_handlers.py:186-219`) through `_emit_validated_order`, mirroring the other 4 mission handlers. ~3 LOC, gets the file fully consistent.

**Defer to follow-up tickets:**
3. **MIN-002 (revised)** — file a small follow-up to migrate `_collect_storage_from_facility`, `_collect_staging_capacity`, AND `_process_facility` to `iter_facility_ability_entries` in one pass (not just `_collect_staging_capacity` as OpenCode wrote). Mechanical refactor; ~20 LOC reduction; probably retire the thin wrappers (`get_harvester_info` et al.) at the same time.
4. **MIN-003** — file a small test-only follow-up to add 4–5 unit tests for `_get_ability_info` covering branches the integration tests don't exercise (registry fallback, string component ID, missing registry, scalar fallthrough).

**Why this split:** Items (1) and (2) live in already-touched files in the consolidation commits and are consistency-preserving — natural to ship as part of PROJ-375 closeout. Items (3) and (4) are scope expansions that benefit from being scheduled and reviewed separately rather than rushed in.

**Merge readiness:** PROJ-375 is safe to merge as-is. None of the four findings block merge; (1) and (2) are quality-of-life improvements that would round out the project cleanly if applied before close.
