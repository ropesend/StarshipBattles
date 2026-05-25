# Phase 4: Audit remediation (Codex consult 2026-05-23)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-497 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remediate verified in-scope findings from `findings/audit_verification.md`. Log out-of-scope findings as DIs.

Audit source: `AgentCoordination/Scratchpad/Consult/20260523T150131Z_audit-PROJ-497/response.md`
Verification: `Projects/active_projects/PROJ-497/findings/audit_verification.md`

---

## Tasks

### Task 4.1: Reduce mini_capital_missile endurance to yield range ≈ 200 [Complex]
**File:** `data/components.json`, `tests/unit/validation/test_proj497_mini_capital_missile_retype.py`
**Tests:** RED→GREEN TDD

User decision (verbatim, 2026-05-23): "reduce the endurance of the mini, so that it comes in at close to a 200 range."

Background: SeekerWeaponAbility's range default = `int(projectile_speed * endurance * 0.8)`. With projectile_speed=6000, current endurance=3.0 → range=14400. Endurance 0.05 → range 240. Endurance 0.04 → range 192. Endurance also controls projectile lifetime in seeker physics (`game/simulation/combat/families/seeker.py:69-70`), so reducing it makes the missile die faster — which is consistent with "short-range mini missile" semantics.

- [x] Pick endurance value: recommended **0.05** (range 240, clean round value, "close to 200" per user). Alternative 0.04 (range 192) is acceptable if you prefer exact-200. Document your choice and rationale in `decisions.md`.
- [x] Write/extend a failing test in `test_proj497_mini_capital_missile_retype.py` asserting effective range ≈ 240 (or your chosen value) — load the component, instantiate SeekerWeaponAbility, check `range` attribute equals expected. RED first.
- [x] Edit `data/components.json:1079` to set `"endurance": 0.05` (or your chosen value).
- [x] Confirm test passes GREEN.
- [x] Run full `tests/regression/modifier_ability_snapshots/` to confirm no snapshot drift.
- [x] Run sharded suite to confirm no broader regressions.
- [x] Update `decisions.md` with Decision 2.1 (endurance reduction): user wanted range close to 200; chose endurance=X yielding range=Y; rationale.

**Notes:** Chose **endurance = 0.05** (yields range = int(6000 * 0.05 * 0.8) = 240). Picked over endurance = 0.04 (range = 192, exact-200) because 0.05 reads cleaner and provides a small buffer above 200. Added test class `TestMiniCapitalMissileEffectiveRange` with 2 tests (raw-payload check + instantiated `SeekerWeaponAbility.range` check) to `tests/unit/validation/test_proj497_mini_capital_missile_retype.py`. RED confirmed: pre-edit range computed as 14400.0 (audit F1 verified). Edited `data/components.json:1079` from `"endurance": 3.0` to `"endurance": 0.05`. GREEN confirmed. Regression snapshots stable (70/70 + new 15 = 85+ assertions covered). Sharded suite stable at 24659/24658/0/0/1. Intentional side-effect: `endurance` also controls projectile lifetime per `game/simulation/combat/families/seeker.py:69-70` — the mini missile now dies after ~0.05 lifetime units, consistent with "short-range mini" semantics.

### Task 4.2: Update Projects/projects_index.md PROJ-497 status [Simple]
**File:** `Projects/projects_index.md`
**Tests:** N/A

- [x] Read `Projects/projects_index.md` to find the PROJ-497 row (per Codex audit: line :8 currently says "Planning")
- [x] Update status to match current actual state ("Awaiting Verification" if all phases including Phase 4 are complete, or whatever the canonical index status is per the file's existing conventions)
- [x] Verify the change matches the conventions used by other rows in the index

**Notes:** Canonical post-audit status is **"Awaiting Verification"** (verified by `validate_close_ready.py`/`validate_audit_ready.py` source, which compare against the literal string, and by `Projects/scripts/utils/config.py:22` allowed-status list). All currently-active rows in the index still read "Planning" because none have reached audit-complete state; PROJ-497 is the first. Updated `Projects/projects_index.md:8` `Planning` -> `Awaiting Verification`.

### Task 4.3: Log DI for stale seeker firing-arc doc claim [Simple]
**File:** `AgentCoordination/discovered_issues/log.jsonl`
**Tests:** N/A

- [x] Read `AgentCoordination/discovered_issues/README.md` for the DI entry format
- [x] Log a DI capturing: `docs/systems/ability_reference.md:287` says "seekers ignore firing arc" unqualified, but per PROJ-497 Decision 3 (`Projects/active_projects/PROJ-497/decisions.md`), seekers honor firing-arc/facing for **launch direction** but ignore arc for **target acquisition**. Doc needs clarification.
- [x] Use `/claude-di-log` or invoke the underlying tool directly. Source = PROJ-497 audit.
- [x] Confirm new DI ID is allocated (e.g., DI-2026-05-23-006).
- [x] Note the DI ID in `decisions.md`.

**Notes:** Logged as **DI-2026-05-23-007**. Category=`doc`, severity=`low`. Description captures the half-true wording and references PROJ-497 Decision 3 for the binding rationale. Suggested action: reword line 287 to "Guided missile; firing arc constrains launch direction but is ignored for target acquisition once launched." Recorded in decisions.md.

### Task 4.4: Log DI for inert "Weapon" tokens in turret_mount/rapid_fire [Simple]
**File:** `AgentCoordination/discovered_issues/log.jsonl`
**Tests:** N/A

- [x] Log a DI capturing: `data/modifiers.json:57-62` (turret_mount) and `:283-288` (rapid_fire) include `"Weapon"` in `allow_abilities` — a component `type` field value, not an ability key, so the token matches zero components. Rows function correctly via co-listed ability keys (ProjectileWeaponAbility, BeamWeaponAbility, SeekerWeaponAbility), but the `"Weapon"` token is dead data. Cosmetic cleanup candidate.
- [x] Confirm new DI ID is allocated.
- [x] Note the DI ID in `decisions.md`.

**Notes:** Logged as **DI-2026-05-23-008**. Category=`dead-code`, severity=`low`. File=`data/modifiers.json` line 58 (first occurrence, turret_mount); description covers both turret_mount (:58) and rapid_fire (:284). Suggested action: remove "Weapon" from both lists; optionally generalize via a static-scan over allow_abilities tokens that don't appear as keys in any component's abilities dict. Recorded in decisions.md.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `decisions.md` has new rows for the endurance choice + DI cross-references
- [x] All targeted tests pass; sharded suite stable
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to reflect PROJ-497 fully closed
