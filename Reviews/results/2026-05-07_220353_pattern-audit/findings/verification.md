# Verification Report

## Summary
- **Total CRITICAL reviewed: 2**
- Confirmed: 2 | Disputed: 0 | Inconclusive: 0
- **Total MAJOR reviewed: 6** (all 6 were spot-checked)
- Confirmed: 4 | Disputed: 1 | Inconclusive: 1

---

## Critical Findings Verification

### Finding: StrategyScreen dual-reference bypass
**Source Report:** `pattern_hunter_cross_shard.md`
**Cited Location:** `game/ui/screens/strategy_screen.py:79,83,86,155-182`
**Status:** CONFIRMED
**Evidence:** Line 79 stores a raw `GameSession` as `self.session`. Line 86 creates a facade wrapper `self._facade = StrategySessionFacade(self.session)`. Lines 155-192 define 7 public properties (`galaxy`, `empires`, `systems`, `active_empire`, `enemy_empire`, `human_player_ids`, `current_empire`) that all tunnel directly through `self.session` rather than `self._facade`. A docstring at line 149-151 explicitly acknowledges the split: "Properties (delegate to session for internal convenience) / External callers should use the facade for cross-layer communication." Despite the docstring intent, 21+ external UI call sites use the raw session properties, bypassing the facade. This violates Pattern #5's core rule that the facade must be "the only entry point from UI into strategy."
**Recommendation:** Replace all 7 tunneled properties with facade-backed equivalents. Route through `self._facade` for all reads. Consider making `self.session` a private attribute (`self._session`) to enforce the boundary, with a deprecation shim if migration must be gradual.

---

### Finding: Widespread `scene.session` access throughout UI (12 sites)
**Source Report:** `pattern_hunter_cross_shard.md`
**Cited Location:** 12 call sites spanning 8 files (see Evidence)
**Status:** CONFIRMED
**Evidence:** All 12 cited access sites were verified against live source code:

| File | Line(s) | Access Pattern | Verified |
|---|---|---|---|
| `strategy_detail_formatter.py` | 112 | `self.scene.session.registries` | Yes — direct registry access |
| `strategy_detail_formatter.py` | 278 | `self.scene.session.registries` | Yes — direct registry access |
| `strategy_detail_formatter.py` | 395-396 | `self.scene.session.turn_engine.validate_colonize_order(...)` | Yes — raw turn engine call (most severe) |
| `strategy_render/hex_outlines.py` | 30 | `r.scene.session.active_empire` | Yes |
| `strategy_render/fleets.py` | 85 | `r.scene.session.get_fleet_path_projection(fleet)` | Yes |
| `strategy_windows/empire_panel_ctrl.py` | 48 | `c.scene.session.registries` | Yes |
| `strategy_windows/list_windows.py` | 60-61 | `c.scene.session.empires`, `c.scene.session.registries` | Yes |
| `strategy_windows/build_queue_windows.py` | 73 | `session=c.scene.session` | Yes |
| `strategy_event_router.py` | 193 | `scene.session.get_empire(planet.owner_id)` | Yes |
| `strategy_event_router.py` | 338 | `scene.session.get_empire(planet.owner_id)` | Yes |
| `transfer_controller.py` | 137 | `session = scene.session` | Yes |

All 12 sites confirmed. The `strategy_detail_formatter.py:395-396` site is the worst offense: it reaches three layers deep (`scene → session → turn_engine`) to call `validate_colonize_order` directly, subverting CQRS-lite, the facade, and composition root boundaries.
**Recommendation:** Add facade methods for each missing access path. Specifically:
- `facade.get_empire(empire_id)` — already exists? Verify and route callers to it
- `facade.can_colonize(fleet_id, planet_id)` — already exists at `strategy_session_facade.py:379`; use it instead of the raw `turn_engine.validate_colonize_order()` call
- `facade.get_registries()` — add or route callers through `get_default_registry_provider()`
- `facade.get_fleet_path_projection(fleet)` — add facade wrapper
- `facade.active_empire` — add as read-only DTO property

---

## Major Findings Verification (Spot Check — 6 of 6 reviewed)

### Finding: Direct turn engine call bypassing all CQRS pathways
**Source Report:** `pattern_hunter_cross_shard.md`
**Cited Location:** `game/ui/screens/strategy_detail_formatter.py:395-396`
**Status:** CONFIRMED
**Evidence:** The code at lines 394-398 reads:
```python
if self.scene.session and self.scene.session.turn_engine:
    res = self.scene.session.turn_engine.validate_colonize_order(self.scene.galaxy, obj, None)
    if res.is_valid:
        self.btn_colonize.show()
```
This reaches three layers deep (`scene → session → turn_engine`), bypassing the facade, CQRS-lite command dispatch, and the composition root boundary. The facade already exposes `can_colonize(fleet_id, planet_id) -> ValidationResult` at `strategy_session_facade.py:379`. This is a genuine, severe bypass.
**Recommendation:** Replace with `res = self.scene.facade.can_colonize(fleet_id, planet_id)`.

---

### Finding: Zero usage of facade `dispatch_*` helpers
**Source Report:** `pattern_hunter_cross_shard.md`
**Cited Location:** `game/strategy/facade/strategy_session_facade.py:405-434` (installer), UI-wide (consumers)
**Status:** CONFIRMED
**Evidence:** The `_install_dispatch_forwarders()` function at line 405 generates bound `dispatch_*` methods on the `StrategySessionFacade` class, one per registered command. A `grep` for `dispatch_` across the entire `game/ui/` directory found:
- `build_queue_screen.py` — uses its own `_dispatch_add_to_queue_command()`, `_dispatch_remove_from_queue_command()`, `_dispatch_toggle_pause_command()` methods (local to the screen class, not facade dispatch)
- `strategy_click_dispatcher.py:69` — defines `dispatch_click()` for spatial click routing
- `strategy_input_handler.py:167` — calls `_click_dispatch.dispatch_click()`
No call site was found that uses `facade.dispatch_*`. The auto-generated methods are dead code. The comment at lines 390-402 provides the design intent.
**Recommendation:** Either (a) migrate UI callers to use `facade.dispatch_*` methods with kwargs, or (b) remove `_install_dispatch_forwarders()` as dead code (~30 LOC maintenance overhead with zero consumption).

---

### Finding: Direct domain object imports in UI for runtime use
**Source Report:** `pattern_hunter_cross_shard.md`
**Cited Location:** 6 files (see Evidence)
**Status:** PARTIALLY CONFIRMED — severity downgraded (Advisory from MAJOR)
**Evidence:** The report lists 6 import sites. Verification reveals the report mischaracterized 3 of 6:

| File | Line | Import | Report Claim | Actual Status |
|---|---|---|---|---|
| `battle_setup_state.py` | 14 | `from game.strategy.data.fleet import Fleet` | runtime, not TYPE_CHECKING | **CONFIRMED** — line 14 is before the `if TYPE_CHECKING:` block |
| `battle_setup/spec_compiler.py` | 74 | `from game.strategy.data.fleet import Fleet` | method-local runtime | **DISPUTED** — line 74 is inside `if TYPE_CHECKING:` block (lines 71-76). All 2 other `Fleet` references use string-quoted `"Fleet"` annotations. |
| `battle_setup/fleet_hierarchy_editor.py` | 22 | `from game.strategy.data.fleet import Fleet` | TYPE_CHECKING only, acceptable | **Acknowledged by report** — not disputed |
| `food_allocation_editor.py` | 40 | `from game.strategy.data.planet import Planet` | method-local runtime | **DISPUTED** — line 40 is inside `if TYPE_CHECKING:` block (lines 39-42). All 4 other `Planet` references use string-quoted `'Planet'` annotations. |
| `galaxy_test/galaxy_mode.py` | 18 | `from game.strategy.data.galaxy import Galaxy` | runtime | **CONFIRMED** — not in TYPE_CHECKING block. However, this is a dev-facing test utility screen (`GalaxyTestScreen`), not a production screen. Severity reduction warranted. |
| `strategy_superweapons.py` | 30 | `from game.strategy.data.fleet import Fleet` | method-local runtime | **DISPUTED** — line 30 is inside `if TYPE_CHECKING:` block (lines 28-30). All 20+ `Fleet` references use string-quoted `'Fleet'` annotations. |

Only 2 of 6 are genuine runtime imports, and one of those is in a dev test screen. The MAJOR severity for this finding is **overstated**. The report should have been rated MINOR with the sole confirmed production concern being `battle_setup_state.py:14`.
**Recommendation:** (a) Move `battle_setup_state.py:14` Fleet import under TYPE_CHECKING. (b) galaxy_mode.py is a developer utility — low priority but should still use DTOs if possible. Rewrite the original report entry to reflect that 4 of 6 cited examples are TYPE_CHECKING-only or not runtime violations.

---

### Finding: Simulation layer uses global `log_event` shim
**Source Report:** `pattern_hunter_cross_shard.md`
**Cited Location:** `game/simulation/entities/projectile.py:4,97,116`
**Status:** CONFIRMED
**Evidence:** Line 4: `from game.core.event_logging import log_event` (module-level global import). Lines 97 and 116 both call `log_event("SEEKER_EXPIRE", ...)` directly. The `BattleEngine` at `battle_engine.py:220-221` already creates a `CombatEventBus` instance, but it is not injected into projectile construction. This creates a process-global handler for simulation-layer event logging, violating the injection pattern and creating risk if two battles run concurrently (though concurrent battles are not a current feature).
**Recommendation:** Thread the `CombatEventBus` (or an injected event bus parameter) through to projectile construction, instead of using the module-level global `log_event`.

---

### Finding: LOC Ceiling Violation — `battle_runner.py` (730 lines)
**Source Report:** `pattern_review_03.md`
**Cited Location:** `game/simulation/battle_runner.py` (entire file)
**Status:** CONFIRMED
**Evidence:** `wc -l` confirms 730 lines. The AGENTS.md establishes a 500-line production file ceiling. The file contains several extraction candidates: `_apply_spec_components_to_ship` (72 lines), `_build_ship_outcome` (58 lines), and related helper functions totaling ~230 extractable lines.
**Recommendation:** Extract as proposed in the original report: `_apply_spec_components_to_ship` + `_extract_component_states` → `game/simulation/post_battle/component_state_applicator.py`; `_build_ship_outcome` + `_derive_end_reason` → `game/simulation/post_battle/outcome_assembly.py`.

---

### Finding: `build_context.py` Protocol location (shard 03)
**Source Report:** `pattern_review_03.md` (PAT-03-006)
**Cited Location:** `game/strategy/data/build_context.py`
**Status:** INCONCLUSIVE (already self-acknowledged as non-violation by the report)
**Evidence:** The `BuildContext` `@runtime_checkable Protocol` at `game/strategy/data/build_context.py` is consumed only by UI (a higher layer). The architecture allows strategy-local protocols (similar to `galaxy_protocols.py`). The report itself notes "This is an 'opportunity to adopt documented pattern' rather than a violation" and rates it MINOR. No action required under current architecture, but the `docs_validator.md` report identifies it as an undocumented pattern worth documenting.
**Recommendation:** Document as an example under Pattern #2 (Protocol + TypeGuard), as suggested by the docs validator report.

---

## Cross-Finding Severity Adjustment Notes

1. **Cross-shard MAJOR: "Direct domain object imports in UI"** — 4 of 6 cited examples are TYPE_CHECKING-only. Severity should be reduced to MINOR/ADVISORY. The 2 genuine runtime imports (`battle_setup_state.py:14` and `galaxy_test/galaxy_mode.py:18`) are in a battle-setup state file and a dev test utility respectively. Neither is a production strategy screen.

2. **Cross-shard MAJOR: "dispatch_* zero usage"** — Correctly rated MAJOR for architecture drift, but the underlying CQRS-lite contract is still honored (commands flow through `handle_command`). The dispatch layer is an unused convenience, not an active bypass.

3. **In-shard reports: 0 CRITICAL, 0-1 MAJOR** — Verification confirms. The in-shard reviewers read 100% of assigned files. The only MAJOR finding across all 4 in-shard reports is the `battle_runner.py` LOC ceiling, which is genuine.
