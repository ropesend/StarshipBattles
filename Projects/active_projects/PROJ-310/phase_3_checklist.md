# Phase 3: Recommend remediation projects

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-310 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Agent-Done (awaiting user review)
**Objective:** Translate the categorized findings into concrete remediation projects. The final deliverable is `findings/nesting_review.md`.

**Prerequisites:** Phase 2 complete; archetype assignments done.

---

## Tasks

### Task 3.1: Draft the executive summary [Simple]
**File:** `findings/nesting_review.md` (NEW)
**Tests:** None.

3-5 sentence executive summary covering:
- How big is the problem (X% files affected, top function has depth N)
- What's the breakdown (M functions are legitimate, K are refactor candidates)
- What are the cross-cutting patterns
- Bottom line: how much of the 69% deep-nesting figure is really a problem?

- [x] Write the executive summary
- [x] Save to top of `findings/nesting_review.md`

**Notes:**

---

### Task 3.2: Insert quantitative tables [Simple]
**File:** `findings/nesting_review.md` (continue)
**Tests:** None.

- [x] Top-10 functions by max_depth (with file paths and depth values)
- [x] Top-10 files by total nested-statement count
- [x] Distribution histogram (how many functions at depth 4, 5, 6, 7+)

**Notes:**

---

### Task 3.3: Archetype catalog (with examples) [Simple]
**File:** `findings/nesting_review.md` (continue)
**Tests:** None.

For each archetype (defensive / try-ladder / state-machine / parser / loop-stack / accretion):
- 1-paragraph description
- 1-2 concrete examples from the codebase (file:line, with quoted code)
- Verdict (legitimate vs refactor) + suggested approach

- [x] Write the catalog

**Notes:**

---

### Task 3.4: Recommended follow-up projects [Medium]
**File:** `findings/nesting_review.md` (continue)
**Tests:** None.

For each refactor archetype with >1 site:
- Project size (S < 1 day, M ~1 week, L > 1 week)
- Files to touch
- Expected outcome (rough estimate of functions/files brought under depth 4)
- Whether it overlaps with PROJ-309

Example format:
```markdown
### Recommendation 1: Replace `defensive` chains with early-return guards
**Size:** Medium (~1 week)
**Files:** game/ui/screens/strategy_renderer.py, game/strategy/engine/order_processor.py, ... (12 files)
**Outcome:** ~25 functions drop from depth 5-6 to depth 2-3
**Overlap with PROJ-309:** strategy_renderer.py is in PROJ-309's top-10 — depth reduction will be a side-effect of decomposition. Don't double-count
**Suggested project ID:** PROJ-3xx (next available)
```

- [x] Write recommendations
- [x] Number recommendations 1, 2, 3, ...

**Notes:**

---

### Task 3.5: "What NOT to refactor" [Simple]
**File:** `findings/nesting_review.md` (continue)
**Tests:** None.

- [x] List functions/files where deep nesting IS legitimate (parsers, state machines mirroring real domain shape)
- [x] Future agents reading the review must NOT propose refactoring these
- [x] Brief explanation per item

**Notes:**

---

### Task 3.6: User review [Simple]
**File:** None — review step.
**Tests:** None.

- [ ] User reads `findings/nesting_review.md`
- [ ] User decides which recommended projects to spin up (each becomes its own PROJ-3xx)
- [ ] Annotate `findings/nesting_review.md` with which recommendations were ACCEPTED, REJECTED, or DEFERRED

**Notes:**
- Pending user — agent run leaves §7 of `findings/nesting_review.md` blank with the annotation table ready to fill in.

---

### Task 3.7: Update MEMORY.md [Simple]
**File:** `C:\Users\rossr\.claude\projects\c--Dev-Starship-Battles\memory\MEMORY.md`
**Tests:** None.

- [ ] After user review, add an entry under "Recently Archived":
  - `- **PROJ-310** — Deep Nesting Investigative Review (2026-MM-DD). All 3 phases complete. Read-only investigation. Output: findings/nesting_review.md categorizes the 69.1% deep-nesting figure into legitimate vs refactor archetypes. Recommended N follow-up projects ([accepted M, rejected K, deferred L]).`

**Notes:**
- Deferred to user — out of scope for the agent run per the prompt.

---

## Phase Completion Checklist
- [x] `findings/nesting_review.md` exists, complete
- [ ] User has reviewed the deliverable
- [ ] Recommendation status (accept/reject/defer) annotated
- [x] Update status at top of this file to `Agent-Done`
- [x] Update plan.md phase table row to `Awaiting User Review`
- [x] Update plan.md Current State to "Agent run complete — pending user review"
