# Phase 5: Codex consult + verified-finding remediation

**Status:** Complete (2026-05-18)
**Depends on:** phase_4
**Review Mode:** standard

**Objective:** End-of-project Codex consult. Verify each finding against current code. Verified-but-out-of-scope findings logged in `decisions.md`; verified-and-in-scope findings would become remediation sub-phases.

---

## Tasks (executed)

### Task 5.1: Run Codex consult

- [x] Invoked `claude-consult --with codex --mode pre-final-check --allow-tests` against the six landed commits.
- [x] Codex independently ran the focused suite: `72 passed in 1.84s`.
- [x] Read [`findings/codex_consult_response_20260518.md`](findings/codex_consult_response_20260518.md) in full (copied from the gitignored Scratchpad/Consult leaf so it persists alongside the project artifacts).

### Task 5.2: Per-finding verification

All 10 asks (a–j) confirmed by Codex with file:line evidence. Cross-verified independently:

- **(a) Source/dest enumeration scope** — fleet ships + planet stockpile/staging_yard; facility-component containers correctly NOT pulled in (PROJ-436 Phase 8 territory). ✅
- **(b) Cross-kind pending dispatch** — `TransferController.confirm_pending` correctly emits IssueTransferCommand per cargo_key kind. ✅
- **(c) Mass-preview math** — sign convention, sentinel resolution, mass-per-unit lookup verified. ✅
- **(d) Resource-key gating** — `TransferValidator._is_known_cargo_type` matches the row builder's catalog-driven emission. ✅ (Note: dialog does not literally call `Container.accepts()` per row — confirmed intentional; gating via `ResourceCatalog.has()` is the analogous seam.)
- **(e) MAX_LOAD / MAX_DROP sentinels** — preserved end-to-end. ✅
- **(f) Alt registrar in sync** — same constructor signature; no alt-path branching. ✅
- **(g) `RESOURCE_TYPES` / `RESOURCE_DISPLAY_NAMES` absence** — pinned at `tests/static_guards/test_no_legacy_storage_fields.py:195-265`. ✅
- **(h) UI labels catalog-driven** — `ResourceDefinition.name` end-to-end; no production hardcoded "Ammo" string remains. ✅
- **(i) Tangential leaks don't trip the guard** — guard scope is intentionally `transfer_view_model` + `transfer_dialog`; tangential leaks documented for a separate TD ticket. ✅
- **(j) Residual risk: fleet-to-fleet pod/vehicle execution** — see verdict below.

### Task 5.3: Remediation verdicts

**Codex finding (j) — fleet-to-fleet drop_pod / vehicle execution**

- Verified at [`game/strategy/engine/order_handlers/transfer_branches.py:458-487`](../../../game/strategy/engine/order_handlers/transfer_branches.py#L458-L487). `_dispatch_fleet_to_fleet` routes through `source.resources.get_fleet_cargo_current(cargo_type)` for all cargo types; item storage actually lives in `bay_inventory.pods` / `bay_inventory.bay`.
- Verified as **pre-existing**: `git log -- game/strategy/engine/order_handlers/transfer_branches.py` shows last touched by PROJ-425 commit `e269a9dbf` (well before PROJ-437). The legacy DTO row builder also surfaced pod rows for fleet entities via `FleetInfo.carried_items_summary`, so this seam was equally reachable pre-PROJ-437; the container-driven row builder just preserves the user-facing opportunity.
- **Verdict: out of PROJ-437 scope.** Engine handler work, not data-model migration. Recommend a future TD ticket: "fleet-to-fleet pod/vehicle transfer routes through BayInventory rather than ship.resources."

**Codex findings — design.md aspiration vs shipped scope**

- Per-facility planet containers NOT iterated; per-container `accepts()` validation NOT called in the dialog. Both deferred intentionally per Phase 0 finding §3.2 + decisions.md (PROJ-436 Phase 8 territory). Logged in decisions.md row "Phase 5 residual risk: design.md aspiration vs shipped scope."

**Source-mass-remaining symmetric warning flag**

- Codex noted that the mass preview is target-centric (only target has explicit over-capacity flag); source remaining can go negative without its own flag. Recorded as a UX-polish follow-up — symmetric warning needs renderer styling that wasn't in scope.

### Task 5.4: Author remediation phases

No remediation phases needed. All Codex-flagged risks are either (a) pre-existing and out-of-scope for PROJ-437 or (b) intentional Phase-0-deferred scope choices.

---

## Phase Completion Checklist
- [x] Codex consult run; response read; verdicts logged in `decisions.md`
- [x] No verified-and-in-scope findings → no remediation phases authored
- [x] Full sharded suite green (23307 passed, 2 skipped at Phase 4 close; no Phase-5 code changes)
- [x] Project ready for final audit + user verification
- [x] Update status to Complete; update plan.md + phase_state.json
- [ ] Notify user that PROJ-437 is ready for `verified` label / archive (user-action)
