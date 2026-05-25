# Phase 3: Doc + decisions update

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-497 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Make sure docs and decisions reflect the chosen data surface so PROJ-498's matrix test encodes the intended truth.

**Precondition:** Phase 2 complete; all approved edits applied + green.

---

## Tasks

### Task 3.1: Update `docs/guides/modifier_system.md` allow_abilities section [Simple]
**File:** `docs/guides/modifier_system.md`
**Tests:** N/A (docs)

- [x] Find allow_abilities discussion (PROJ-489 audit F7 noted line 98, 285)
- [x] Add a "data-intent decisions" reference pointing at PROJ-497's decisions.md (or the index of decisions)
- [x] If `efficient_engines` was deleted, remove references in this doc
- [x] Confirm doc/code consistent per CLAUDE.md "keep code and docs consistent"

**Notes:** Added a follow-on paragraph after the restrictions caveat (line 98 area) covering (a) the ability-key namespace warning with `Engine/Generator/Weapon/Thruster` listed as anti-pattern names, and (b) a link to `Projects/active_projects/PROJ-497/decisions.md` for per-row decisions. User REVERSED Decision 1 to DELETE; the doc was already aligned because it does not name `efficient_engines` anywhere — only the generic anti-pattern names — so no further edit needed after the reversal.

### Task 3.2: Update `docs/guides/adding_modifiers.md` [Simple]
**File:** `docs/guides/adding_modifiers.md`
**Tests:** N/A

- [x] Locate allow_abilities/allow_types guidance
- [x] Add note that allow_abilities keys MUST match component ability key namespace (`CombatPropulsion`/`ResourceGeneration`/`ManeuveringThruster`/... — NOT `Engine`/`Generator`/`Weapon`/`Thruster`)
- [x] Add a brief example of a row that would silently match zero components

**Notes:** Added a "Namespace warning" paragraph + an anti-pattern JSON example (a row with `allow_abilities: [Engine, Generator, Thruster]` that silently matches zero components). Cross-referenced PROJ-497 decisions.md.

### Task 3.3: Handoff note to PROJ-498 [Simple]
**File:** `Projects/active_projects/PROJ-498/findings/source_review.md` (append)
**Tests:** N/A

- [x] Append "PROJ-497 outcomes" section listing the final data surface (which rows changed, which decisions were "leave alone")
- [x] PROJ-498's rejection-matrix test must encode this final surface, not the surface at PROJ-489's audit time

**Notes:** Appended a per-row outcomes table covering all 4 decisions (initial pass: efficient_engines BLOCKED, mini_capital_missile RETYPED with full cascade, facing/turret_mount KEPT, override-pairs NONE). After the user reversed Decision 1 to DELETE, updated the handoff entry to reflect the final state: `efficient_engines` row removed entirely; PROJ-498's matrix test no longer needs to plan around it (it simply will not appear in the live `data/modifiers.json` payload PROJ-498 derives from).

### Task 3.4: Resolve or update DI-2026-05-23-004 [Simple]
**File:** `AgentCoordination/discovered_issues/log.jsonl`
**Tests:** N/A

- [x] If `efficient_engines` was deleted/fixed, mark DI-2026-05-23-004 as `resolved` with the PROJ-497 reference
- [x] If user chose (c) keep inert, mark DI as `accepted-known` with rationale

**Notes:** RESOLVED via canonical prune. The DI README explicitly states "No `status` field — the log only holds open issues. Pruning is the resolution." Used `python Tools/agent_coordination/triage_discovered_issues.py --prune DI-2026-05-23-004`. Output: "pruned 1 entry". Verified the entry is gone (log went from 28 to 27 entries; `DI-2026-05-23-004` no longer present). Git history preserves the original entry for traceability; the PROJ-497 decisions.md row "Decision 1 (REVISED — DELETE)" carries the resolution provenance for any future reader.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Docs match data
- [x] PROJ-498 has the handoff note
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Awaiting audit"
