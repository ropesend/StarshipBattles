# Phase 1: Cross-doc consistency + terminology

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-469 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix the 3 surviving MAJOR cross-doc/terminology issues (the README "33 patterns" count finding was DROPPED in the 2026-05-20 revision — see decisions.md), applying canonical-term and canonical-location decisions uniformly, identified by audit `2026-05-20_073330_docs-audit`.

---

## Tasks

### Task 1.1: 03_CONVENTIONS.md pattern cross-reference [Simple]
**File:** `docs/03_CONVENTIONS.md`
**Verification:** Read the doc end-to-end after edits; check the cited cross-reference resolves; bump `Last verified:` stamp.

- [x] Change "Pattern #40" to "Pattern #41" at line 131 — the surrounding text discusses `IIssuerAdapter` / FMS command polymorphism, which is Pattern #41 (Polymorphic Order Issuer) per `docs/02_PATTERNS.md:75,1056`; #40 is "Named Pre-Tick Setup Registry"
- [x] Verify: the referenced pattern in `docs/02_PATTERNS.md` matches the text's subject (IIssuerAdapter = #41) — confirmed 02_PATTERNS.md:75 = Polymorphic Order Issuer (IIssuerAdapter)

### Task 1.2: README.md stale pattern count [DROPPED — revision 2026-05-20]
**File:** `docs/README.md`

- [x] DROPPED per dual independent+Codex review. `docs/README.md:169` already presents the count as a stale-name warning ("older \"33 patterns\" summary text is stale."), not a live assertion that the project has 33 patterns. Editing to "43 patterns" is churn. Verified against live repo 2026-05-20. See decisions.md.

### Task 1.3: satellites.md DeployedGroup terminology [Simple]
**File:** `docs/systems/satellites.md`
**Verification:** Read the doc end-to-end after edits; bump `Last verified:` stamp.

- [x] Replace the "distinct `satellite_group` fleet namespace" wording (lines 19-20) with deployed-group terminology — `SatelliteConstellation` is a `DeployedGroup`, NOT a Fleet; this is internally contradicted by the same doc's correct mention at line 42 ("SatelliteConstellation (DeployedGroup; ...") and confirmed by `game/strategy/data/deployed_group.py:375-379` (replaced the previous synthetic `Fleet(group_kind="satellite_group")`)
- [x] Sibling occurrences (revision): fix `IIssuerAdapter` (Pattern #40)` → `(Pattern #41)` at line 13 AND the `Pattern #40` in the "Planet-issued launch / recovery" section header (~line 217) — both describe IIssuerAdapter/polymorphic order issuing; same #40→#41 defect as Task 1.1, in this in-scope file
- [x] Verify: the doc no longer describes a SatelliteConstellation as a fleet/fleet-namespace; no remaining wrong Pattern #40 cross-ref (sweep confirms only the changelog stamp line 7 mentions #40, describing the fix)

### Task 1.4: testing_infrastructure.md newdocs cross-reference [Simple]
**File:** `docs/guides/testing_infrastructure.md`
**Verification:** Read the doc end-to-end after edits; check the cross-reference resolves; bump `Last verified:` stamp.

- [x] Change `newdocs/02_PATTERNS.md` to `docs/02_PATTERNS.md` at line 129 — `newdocs/` does not exist; the UI-construction-seam patterns (#32, #33) live in `docs/02_PATTERNS.md`
- [x] Verify: no `newdocs` remains; docs_audit run confirms 0 newdocs dead refs repo-wide

### Task 1.5: Phase-wide verification [Simple]
**File:** (multiple — verification only)

- [x] Verify: `Last verified:` stamps updated on all docs touched this phase (03_CONVENTIONS.md, satellites.md, testing_infrastructure.md); deterministic docs_audit re-run shows no new broken cross-references in modified files

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_073330_docs-audit/`. See `findings/source_audit.md` for the link._
