# PROJ-370 Verifier Report — Independent Verification of OpenCode's Code Review

**Verifier:** Claude (independent)
**Source review:** `Reviews/results/2026-05-06_090316_code_proj-370-data-layer-boundary-protocols-mutator-rou_req-req_20260506_090314_5da777/report.md`
**Scope:** 6 commits on `feat/03c-phase-aware-execution` (`b7696ad9a` → `65c3fe17f`)

---

## Verdicts Table

| ID | Severity | Verdict | One-line note |
|---|---|---|---|
| MAJ-001 | MAJ | CONFIRM | Dead `_prune_empty_fleets` confirmed; stale comment in `conflict_resolution_engine.py:15` confirmed. |
| MAJ-002 | MAJ | CONFIRM_REMEDIATION_REVISE | Direct writes confirmed; allowlist documented in test comment but NOT in `decisions.md`; either remediation is feasible. Prefer (a) routing for parity with manifest. |
| MIN-001 | MIN | CONFIRM | `post_battle_hook.py` allowlist entry is genuinely redundant (zero direct ShipInstance writes remain in the file); `builder/layer_panel.py` has zero ShipInstance refs. |
| MIN-002 | MIN | CONFIRM | Docstring still says "18"; counted 22 fields (18 engines + 4 mutators). |
| MIN-003 | MIN | CONFIRM (out-of-scope-for-fix) | Both broad excepts pre-date PROJ-370 (commit `13f8b9455d`, 2026-04-11). Pre-existing convention gap, not a PROJ-370 regression. |
| MIN-004 | MIN | CONFIRM | Asymmetry confirmed; `Empire.remove_colony` exists at `empire.py:61-73`; `hasattr` pattern used in `prune_empty_fleets` is appropriate analog. |
| MIN-005 | MIN | CONFIRM | `Planet.pop_order` at `planet.py:399-401` is index-0-only; workaround at `planet_write_service.py:107-108` is correct. |
| INFO-001 | INFO | CONFIRM | `_is_internal_owner` check at lines 129, 149, 173 of walker excludes `self`/`cls`. |
| INFO-002 | INFO | CONFIRM (sample) | All 4 BoundarySpecs in test_mutator_boundary_ast_guard.py have non-empty target_attributes. |
| INFO-003 | INFO | CONFIRM | Spot-checked `is_alive` and `populations.append`: only mutator + game_initializer hit; all other matches are self-writes or simulation-side. |
| INFO-004 | INFO | CONFIRM (trust) | Not re-verified beyond report; cited line ranges look plausible. |
| INFO-005 | INFO | CONFIRM (trust) | Not re-verified. |
| INFO-006 | INFO | CONFIRM | `create_default()` lazy-defaults at lines 188-202 of `turn_engine_config.py` match report exactly. |
| INFO-007 | INFO | CONFIRM (trust) | Not re-verified. |
| INFO-008 | INFO | CONFIRM (trust) | Not re-verified line counts. |

---

## MAJOR Findings

### MAJ-001 — CONFIRM

**Evidence:**
- `game/strategy/combat/post_battle_hook.py:251-269` defines `_prune_empty_fleets` exactly as described.
- `apply_outcome_to_fleets` (lines 114-119) routes through `empire_mutator.prune_empty_fleets(...)` instead.
- Repo-wide grep for `_prune_empty_fleets` shows zero production callers; only references are: (a) the definition itself, (b) the test file `test_empire_write_service.py:132` (test name only), (c) the stale comment at `game/strategy/engine/conflict_resolution_engine.py:15`, (d) the docstring comment in `empire_write_service.py:105`, (e) docs and historical project notes.
- Docs hit: `docs/systems/combat_simulation.md:1104` also references the now-dead function.

**Verdict:** CONFIRM. OpenCode's deletion + comment-fix recommendation is correct. Should also update `docs/systems/combat_simulation.md:1104` and the docstring at `empire_write_service.py:105` (which references "lines 200-218" of the old function).

---

### MAJ-002 — CONFIRM (with remediation revision)

**Evidence:**
- `game/strategy/engine/game_initializer.py:344` does `home_planet.populations.append(initial_pop)` directly.
- `game/strategy/engine/game_initializer.py:86` does `empire.colonies.clear()` directly.
- `Projects/active_projects/PROJ-370/manifest.md:56` explicitly says: `Routed: home_planet.populations.append(initial_pop) (line 344) + empire.colonies.clear() (line 86 — Phase 4 territory but flagged).` Manifest line 71 reaffirms the colonies.clear routing intent.
- `tests/unit/strategy/data/test_mutator_boundary_ast_guard.py` allowlists `game/strategy/engine/game_initializer.py` for both Planet (line 127) and Empire (line 144). The inline comment justifies it as "Initialization-time writers — homeworld setup, race-tuning. Legitimate construction writes; not engine-tick boundary crossings."
- `Projects/active_projects/PROJ-370/decisions.md` has a single 2026-05-05 entry on AST guard policy and **does not document the deviation** from manifest's "Routed" plan to "allowlisted" implementation. Documentation drift confirmed.

**Verdict:** CONFIRM_REMEDIATION_REVISE.

The intent (init-time writes are not boundary crossings) is a defensible architectural call, but it deviates from the manifest's explicit "Routed" commitment and the deviation is unrecorded in `decisions.md`. Two issues stack here:

1. The implementation choice itself.
2. The undocumented deviation from manifest.

OpenCode's option (a) (route via kwargs) is feasible — `GameInitializer._setup_initial_scenario` is already a static method called once per game, so threading `planet_mutator`/`empire_mutator` kwargs is mechanical (the engines that own those services are constructed in `GameSession`, which calls into init). Option (b) (per-attribute allowlist tightening) does not actually prevent future tick-phase writes from sneaking in; it just narrows the bypass surface.

**Recommended fix:** Pursue option (a) for both writes — routes through the same mutator surface the rest of the codebase uses, eliminates the allowlist exception, and matches the manifest. Update `decisions.md` either way to record the choice.

---

## MINOR Findings

### MIN-001 — CONFIRM

`post_battle_hook.py` has zero direct attribute writes to any of the 12 ShipInstance target attributes (grepped `is_alive=`, `is_derelict=`, `current_hp=`, `components=`, `cargo_contents`, `carried_items`, `consumable_levels`, `component_toggles`, `activation_states`, `experience=`, `kills=`, `battles_survived=` — all matches are inside the mutator service, simulation-side classes, or `self.*` writes inside data-class methods). The allowlist entry is genuinely redundant.

`builder/layer_panel.py` has zero `ShipInstance` references — it operates on Vehicle/design components, as the comment in the allowlist already states. Removing both entries from the ShipInstance allowlist would tighten the guard with no behavior change.

### MIN-002 — CONFIRM

`turn_engine_config.py:3` reads `Bundles the 18 engine dependencies into a single frozen dataclass.` Counting fields at lines 58-90: 18 engines + 4 mutators = 22 fields. The class docstring at line 50 (`Frozen configuration bundling 18 engine dependencies for TurnEngine.`) and the `create_default` docstring at line 105 (`Eagerly construct all 18 default engines and bundle them.`) are also stale.

### MIN-003 — CONFIRM (out-of-scope-for-fix)

`git blame` confirms both broad excepts at `design_validator.py:76,92` were introduced in commit `13f8b9455d` (2026-04-11), well before PROJ-370. Per CLAUDE.md "Root Cause Fixes" rule and PROJ-308 closure (24 sites already justified), this is a pre-existing convention gap that should be fixed but is not a PROJ-370 regression. OpenCode's suggested comment text is appropriate.

### MIN-004 — CONFIRM

`Empire.remove_colony` exists at `game/strategy/data/empire.py:61-73` and is symmetric with `add_colony` (no side effects yet, but the docstring notes future caller responsibility for `planet.owner_id`). `EmpireWriteService.add_colony` at line 32 delegates to `empire.add_colony(planet)`, while `remove_colony` at line 37 does direct list manipulation citing test-mock concerns. The asymmetry is real. The same `hasattr` pattern at `prune_empty_fleets` line 126 (`if hasattr(empire, "remove_fleet")`) is the right precedent — preserves test-mock compatibility and future side-effect parity.

### MIN-005 — CONFIRM

`game/strategy/data/planet.py:399-401` defines `pop_order(self) -> Optional[Order]: return self.orders.pop(0) if self.orders else None` — index-0 only, no parameter. The mutator workaround at `planet_write_service.py:107-108` is safe and the only call site is the mutator itself (which is allowlisted), so no boundary leak. OpenCode's low-priority `pop_order_at(index)` suggestion is reasonable cleanup but not blocking.

---

## INFO Spot-Checks

- **INFO-001 (self/cls exclusion):** Walker at `tests/unit/strategy/data/_mutator_ast_walker.py:48` defines `_INTERNAL_OWNERS = frozenset({"self", "cls"})` and lines 129, 149, 173 all gate target writes with `not _is_internal_owner(target.value)`. Confirmed.
- **INFO-003 (write-site routing):** Spot-grepped `\.is_alive\s*=` (only `ship_instance_write_service.py:32` and `ship_instance_bridge.py:129,131` on strategy side; rest are simulation-side `Ship`/`Projectile`/`damage_calculator`/etc.) and `\.populations\.append` (only `planet_write_service.py:39` and `game_initializer.py:344`). Matches report.
- **INFO-006 (create_default lazy defaults):** Lines 188-202 of `turn_engine_config.py` lazy-construct `PlanetWriteService()`, `EmpireWriteService()`, `ShipInstanceWriteService()` exactly as report describes. Confirmed.

---

## Recommended Actions for Claude

**Fix now (low risk, blocking-quality):**

1. **MAJ-001** — Delete `_prune_empty_fleets` from `post_battle_hook.py:251-269`. Update stale comment at `conflict_resolution_engine.py:15` to point to `EmpireWriteService.prune_empty_fleets`. Also update the docstring at `empire_write_service.py:105` (currently references "lines 200-218" of the dead function) and `docs/systems/combat_simulation.md:1104`.
2. **MIN-002** — Update three docstrings in `turn_engine_config.py` (lines 3, 50, 105) to "22 fields (18 engines + 4 mutator protocols)".
3. **MIN-001** — Remove `post_battle_hook.py` from the ShipInstance allowlist in `test_mutator_boundary_ast_guard.py:182`. Re-run the AST guard test to confirm zero hits.
4. **MIN-004** — Change `EmpireWriteService.remove_colony` to use the `hasattr` pattern that `prune_empty_fleets` uses, delegating to `empire.remove_colony(planet)` when available.

**Decide and fix (architectural):**

5. **MAJ-002** — Pursue option (a) per OpenCode's recommendation: thread `planet_mutator`/`empire_mutator` kwargs through `GameInitializer._setup_initial_scenario`, route the two writes, remove `game_initializer.py` from both Planet and Empire allowlists. Update `decisions.md` to record either this choice or (if option (b) is chosen) the explicit deviation from manifest with rationale.

**Defer (out-of-scope-for-fix in PROJ-370):**

6. **MIN-003** — Pre-existing broad-except convention gap. File a separate cleanup ticket; do not bundle into PROJ-370 closure.

**Defer (low priority, not blocking):**

7. **MIN-005** — Adding `Planet.pop_order_at(index)` is reasonable but the current workaround is safe. Track as a follow-up note.

**Also recommended (process):**

8. Update `Projects/active_projects/PROJ-370/decisions.md` to record the MAJ-002 deviation and any choice made.
