# PROJ-343: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis — Tier-1 firsthand verification

The planning instance (Claude Opus 4.7, 2026-05-04) verified each defect against live source, not the review-stream summaries. Findings below cite exact line numbers as observed.

### T1.1 — Fleet-to-fleet TransferDialog "Planet not found"

**Defect:** When a user transfers cargo between two fleets, `_resolve_endpoints` returns `(source["id"], None, target["id"], True, True)` (both `source_is_fleet` and `target_is_fleet`). The emitted command has `planet_id=None, target_fleet_id=<id>`. The handler's first action after fleet resolution is `_resolve_planet(session, cmd.planet_id)`, which returns "Planet not found." for `planet_id=None`. The fleet-to-fleet branch never runs.

**Evidence:**
- `game/ui/screens/transfer_controller.py:182-183` — `if source_is_fleet and target_is_fleet: return source["id"], None, target["id"], True, True`
- `game/ui/screens/transfer_controller.py:255-263` — `IssueTransferCommand(fleet_id=fleet_id, planet_id=planet_id, …, target_fleet_id=target_fleet_id)` emitted with `planet_id=None`.
- `game/strategy/engine/commands.py:106-129` — `IssueTransferCommand` declares `target_fleet_id: Optional[int] = None` as a real field. Docstring says transfers can be "between two fleets."
- `game/strategy/engine/handlers/transfer.py:46-49` — `planet, error = self._resolve_planet(session, cmd.planet_id); if error: return error`. Unconditional, regardless of `target_fleet_id`.
- `game/strategy/engine/handlers/transfer.py:79-85` — queued `transfer_params = {'direction', 'cargo_type', 'amount', 'planet_id', 'species_id'}` — `target_fleet_id` is NOT included. Even if the guard were bypassed, the persisted order wouldn't carry the target fleet.
- `tests/unit/ui/screens/test_transfer_dialog_characterization.py:418-432` — current test only asserts the mocked facade saw the command. False positive — the real handler is never exercised.

**Fix shape:** in `transfer.py:execute`, branch on `cmd.target_fleet_id is not None`:
- If yes: skip `_resolve_planet`; resolve target fleet via existing helper `_resolve_player_fleet` (or peer lookup if cross-empire is allowed); validate via existing fleet-to-fleet validator (or add one if missing); add TRANSFER order with `target_fleet_id` in `transfer_params`.
- If no: existing planet-target path unchanged.

Update `transfer_params` dict at lines 79-85 to conditionally include `target_fleet_id` so the persisted order can be executed against the target fleet at order-execution time. **Verify**: search the order executor for whether it currently understands `target_fleet_id` or only `planet_id`. If the executor doesn't, add a comment in [decisions.md](decisions.md) and treat the executor follow-up as scope-out.

### T1.2 — Turn rollback bypass (two distinct holes)

**Defect (snapshot):** Snapshot capture is wrapped in `except Exception as e: logger.error(...); # continue without snapshot — better to process the turn than abort`. If `TurnStateSnapshot.capture()` raises, `snapshot=None`. Later, the rollback site at `:583/:586` is gated `if snapshot and save_path` and `if snapshot and session`. With `snapshot=None`, rollback never happens — silently. The "fail-safe" comment misnames the failure mode: better-to-process-than-abort assumes capture is the only failure point, but it ALSO ensures the turn continues without rollback safety.

**Defect (engines):** The end-of-turn block runs after the tick loop:
```
self.organics_consumption_engine.process_consumption(empires)
self.happiness_engine.process_happiness(empires, galaxy)
self.population_engine.process_population_growth(empires)
QualityEngine(...).process_quality_improvement(empires)
AtmosphereEngine(...).process_atmosphere(empires)
WaterEngine(...).process_water_modification(empires)
```
None are wrapped in `_time_phase` (the helper used inside the tick loop, which catches engine exceptions and re-raises as `EnginePhaseError`). The outer `try` catches only `EnginePhaseError`. So a raw `RuntimeError` from any of these six engines bypasses rollback after ticks have already mutated state.

**Evidence:**
- `game/strategy/engine/turn_engine.py:514-524` — broad `except` swallows snapshot failures.
- `game/strategy/engine/turn_engine.py:550-573` — the six end-of-turn engines, all unwrapped.
- `game/strategy/engine/turn_engine.py:575-589` — `except EnginePhaseError`, the only rollback site, gated `if snapshot and …`.
- `tests/unit/strategy/turn_engine/test_turn_engine_end_of_turn_order.py:168-172` — pins raw `RuntimeError` propagation as expected behavior.
- `tests/unit/strategy/turn_engine/test_turn_engine_snapshot_integration.py:130-160` — pins `snapshot=None` silent rollback-skip as expected behavior.

**Fix shape (snapshot):** narrow the broad except. Treat capture failure as a fatal turn condition — re-raise (or escalate to `EnginePhaseError(phase_name="snapshot_capture")`) so the rollback path triggers OR the caller learns that this turn is unsafe. Re-raising is simpler; the caller already handles `EnginePhaseError`.

**Fix shape (engines):** wrap each end-of-turn engine call in `_time_phase("organics_consumption", lambda: …)` (or whatever the helper's signature is — implementer should re-read `_time_phase` to confirm the wrapping pattern, since the tick-loop pattern varies). This ensures raw exceptions become `EnginePhaseError` and route through the existing rollback path.

### T1.3 — Owned sector effects leak across teams

**Defect:** `collect_sector_effects(..., empire_id=None)` is called from both env-hazard and combat sites. The collector's `_aggregate` owner-filter is gated `if owner_id is not None and empire_id is not None and owner_id != empire_id: continue`. With `empire_id=None`, the filter is dead; owned sources (e.g., a colony's defensive EnvironmentalDamage facility) fall through to all empires querying that hex. Result: empire A's defensive hazard damages empire B's fleet that flies through.

**Evidence:**
- `game/strategy/engine/environmental_hazard_engine.py:111-113` — `effects = collect_sector_effects(system, fleet.location, empire_id=None, registries=None)`.
- `game/strategy/engine/conflict_resolution_engine.py:508-511` (per Codex; not personally re-verified, same shape).
- `game/strategy/services/system_effects_collector.py:298` — `if owner_id is not None and empire_id is not None and owner_id != empire_id: continue`.
- `game/strategy/services/ability_sources/facility.py:42-44` — `owner_id` from `planet.owner_id`.

**Fix shape:** at both call sites, pass `fleet.owner_id` (the querying empire's id) instead of `None`. The comment at `:109-110` claiming "owned facility-projected hazards are filtered by the collector" then becomes true. Storms (ownerless) still apply to all empires because their `owner_id is None` short-circuits the filter at `_aggregate:298`.

**Subtle risk to verify in Phase 5:** are there cases where `empire_id=None` was deliberate (e.g., for ownerless storms)? Re-read the call sites and the collector to confirm the new behavior is correct for ownerless sources too.

### T1.4 — TransferDialog `_on_confirm` always-kill regression

**Defect:** Pre-refactor, `_on_confirm` had three early-return abort paths that kept the dialog open so the user could fix input. PROJ-328 audit S1.2 added `try/finally: self.kill()` around `confirm_pending()`. Now ALL exits — including no-source, no-target, both-endpoints-non-fleet — kill the dialog. PROJ-328 Phase C checklist Note 3 says the prior behavior was "intentional cleanup"; that documentation is wrong.

**Evidence:**
- `game/ui/screens/transfer_dialog.py:372-378` — `def _on_confirm(self): try: self._controller.confirm_pending() finally: self.kill()`.
- `game/ui/screens/transfer_controller.py:200-280` — `confirm_pending` returns 0 (no commands issued) when source/target missing or both endpoints non-fleet.

**Fix shape:** read the controller's return contract and decide:
- Option A: controller raises a sentinel exception or returns a richer result (e.g., `ConfirmResult(orders_issued: int, aborted_for_correction: bool)`). Dialog kills only when `not aborted_for_correction`.
- Option B: dialog re-checks the same conditions itself before calling `confirm_pending` and skips `kill()` on validation-only abort.
- Option A is cleaner (single source of truth in controller). Implementer should pick one and document in [decisions.md](decisions.md).

Also: 4 tests use `patch.object(dialog, "kill")` to assert always-kill (per Codex). Find via `git grep -n 'patch.object.*kill' tests/unit/ui/screens/`. Update each.

### T1.5 — CargoQuickDialog cleanup gap

**Defect:** `_issue_orders` calls `self.controller.issue_orders(...)` then `self.kill()`. The controller can raise (it calls `facade.handle_command` which raises on dispatch failure). Exception propagates with the dialog still alive — exact bug class audit S1.2 fixed for TransferDialog.

**Evidence:**
- `game/ui/screens/cargo_quick_dialog.py:300-306` — no `try/finally`.
- `game/ui/screens/transfer_dialog.py:372-378` — fixed pattern (the audit S1.2 reference).

**Fix shape:** wrap `_issue_orders` body in `try: self.controller.issue_orders(...) finally: self.kill()`. UNLIKE T1.4, CargoQuickDialog has no validation-abort path that should keep the dialog open — verify by reading the controller. If validation-abort paths exist, follow T1.4's selective-close shape instead.

## Architecture Notes

### Reusable patterns

- **`_time_phase` wrapper** (turn_engine.py): wraps a callable in try/except that re-raises engine exceptions as `EnginePhaseError`. Already used by all tick-loop sub-engines. Same wrapper applies to end-of-turn engines.
- **`_resolve_player_fleet`** (`handlers/base.py`): existing fleet lookup helper. Reuse for T1.1's target-fleet resolution.
- **`try/finally: self.kill()`** (`transfer_dialog.py:372-378`): the audit S1.2 cleanup pattern. T1.5 uses it as-is; T1.4 uses a selective-close variant.
- **`empire_id`-filtered effect collection** (`system_effects_collector.py:_aggregate`): owner filter activates ONLY when `empire_id` is non-None. Pass the querying empire's id at every call site that should filter owned sources.

### Risks

1. **T1.1 order-execution depth.** The order-PERSISTENCE fix may not be complete unless the order-EXECUTION path also reads `target_fleet_id`. Phase 2 includes a verification step; if the executor needs changes, decide between extending PROJ-343 scope vs. opening a follow-up project. Default: extend — PROJ-343 is the bug-fix project.
2. **T1.2-engines wrapping breadth.** Wrapping all six engines in `_time_phase` may surface latent bugs in those engines (since they previously raised raw exceptions that nobody caught). Phase 4 verifies that the existing tests for those engines still pass.
3. **T1.3 ownerless-source check.** Confirm the fix doesn't break ownerless storms / sun hazards. Phase 5 includes a regression test for ownerless effects still applying to all empires.
4. **T1.4 controller-result contract.** Changing `confirm_pending` return type may ripple into other tests. Phase 6 includes a grep for callers.
5. **Concurrent commit hazard.** PROJ-342 is in flight. If both arcs commit close in time, `Projects/projects_index.md` row order may interleave. Each commit must `git status` first and not stage other arcs' files.

## Design Decisions

See [decisions.md](decisions.md) for the running log.
