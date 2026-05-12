# Ticket Workflow (TDD)
**Role:** Senior Software Engineer

> Renamed from `Tracking/protocols/02_work_ticket.md` on 2026-05-12 as part
> of legacy-system deprecation. The workflow content is unchanged; the file
> now lives alongside other cross-agent protocols (`partner_cli.md`,
> `consult_prompt_block.md`, `interagent_discussion.md`). Used by
> `claude-gi-work` and available for codex-side use too.

## Configuration

This protocol is parameterized by ticket type. The calling skill sets these values:

| Variable | Bug | Feature |
|----------|-----|---------|
| TYPE | Bug | Feature |
| PREFIX | BUG | FEAT |

Tickets live on GitHub Issues with `type:bug` or `type:feature` labels. The
{TYPE} and {PREFIX} variables describe taxonomy, not storage. Status labels
(`status:pending`, `status:in-progress`, `status:awaiting-confirmation`,
etc.) are the source of truth; "dashboards" are dynamic queries
(`gh issue list --label "type:bug" --label "status:pending"`); the
historical narrative index is `gh issue list --state closed --label "verified"`.

---

**CRITICAL CONSTRAINT:** You do NOT have the authority to mark a {TYPE} as `verified` or close the issue. Your authority ends at `status:awaiting-confirmation`, `status:needs-clarification`, or (Feature only) `status:needs-refactor`.

### [Bug Only] Anti-Reversion Rules

*These rules apply to ALL phases of bug resolution:*

- NEVER undo a recent refactor to fix a bug. Fix forward.
- If a bug was CAUSED by a refactor, the fix must work WITHIN the new architecture.
- If you cannot find a forward-fix, escalate to `[Needs Clarification]`.
- Check `git log` on affected files. If a PROJ-XX commit touched them in the last 60 days, read that project's design docs before coding anything.
- A fix that increases tech debt requires explicit justification in the Work Log.
- Refer to CLAUDE.md principles: "When a new system replaces an old one, ERADICATE the old system completely." Your fix must not resurrect eradicated code.

### Documentation Discrepancy Rules

*These rules apply to ALL phases of both bug and feature resolution:*

When you find that the code contradicts the `docs/` documentation, use this decision framework:

1. **Determine which is more recent.** Run `git log --oneline -5 -- <docs_file>` on the relevant `docs/` file and compare against the code's last modification date.
2. **Apply context-dependent truth:**
   - **If the code changed MORE recently than the docs** -- the code is likely correct and the docs are stale. Update the `docs/` file to match the code as part of your fix.
   - **If the docs are MORE recent than the code** (e.g., docs were just verified/rewritten) -- the docs are correct and the code has drifted. Your fix should align the code with the documented pattern.
   - **If it's unclear which is correct** (similar dates, or the discrepancy is about design intent rather than factual accuracy) -- **escalate to `[Needs Clarification]`**. Add a `## Questions for User` entry: "Discrepancy found: `docs/XX.md` says [X], but the code does [Y]. Which is the intended behavior?"
3. **Always document the discrepancy** in the `## Work Log` under a `### Documentation Discrepancy` heading, regardless of how you resolve it.
4. **Always update `docs/` inline** when you resolve a discrepancy -- do not leave stale docs for later.

---

**Selection Logic:**
* **If User Specified an ID:** Load that specific ticket.
* **If No ID Specified:** Read `{DASHBOARD}`, pick the top "Pending" item.

---

## Execution Steps

### 1. Context Loading

* Read `{ACTIVE_DIR}/[{PREFIX}-ID].md`.
* Update `{DASHBOARD}`: Set status to `[In-Progress]`.

### 2. Phase 0: Deep Review & Context Gathering

#### [Bug Only] Step 0a: Architectural Context Gathering (MANDATORY)

Before assessing fix approach, gather context from these sources:

1. **Git History Check:** Run `git log --oneline -20 -- <affected_files>` for each file implicated in the bug. Note any commits in the last 60 days that are refactors, renames, or part of a PROJ-XX project.
2. **Active Project Check:** Scan `Projects/active_projects/` for any PROJ-XX whose `plan.md` or phase checklists reference the affected files or modules. If found, read that project's `design.md` to understand design intent.
3. **Architecture Doc Check:** Review `CLAUDE.md` (Key Conventions, Architecture Principles) and the relevant `docs/` files for any principles relevant to the affected code area:
   - `docs/01_ARCHITECTURE.md` (Layer Structure, Dependency Rules)
   - `docs/02_PATTERNS.md` (Established Design Patterns)
   - `docs/03_CONVENTIONS.md` (Naming and Coding Conventions)
   - Any relevant system doc from `docs/systems/` for the affected area
4. **Documentation Discrepancy Check:** Compare the affected code against the `docs/` files you just read. Does the code follow the documented patterns, conventions, and architecture? If not, note the specific discrepancy (what the docs say vs. what the code does). Apply the Documentation Discrepancy Rules above to determine which is correct.
5. **Document Findings:** Append to `## Work Log`:
   ```
   ### Phase 0: Architectural Context
   **Recent refactors:** [list relevant commits or "None found"]
   **Active projects touching this code:** [PROJ-XX or "None"]
   **Relevant architecture rules:** [brief list or "None specific"]
   **Documentation discrepancies:** [specific discrepancies found, or "None -- code matches docs"]
   ```

#### [Bug Only] Step 0b: Ambiguity & Anti-Reversion Assessment

* **Assess** whether the correct architectural fix is clearcut or ambiguous.
* **ANTI-REVERSION CHECK:** If git history shows the affected code was recently refactored (within last 60 days) as part of a project or intentional redesign, the fix MUST NOT revert that refactor. Instead:
  - Understand WHY the refactor was done (read the project plan/design docs)
  - Fix FORWARD: find a solution that preserves the refactored architecture
  - If no forward-fix is apparent, escalate to `[Needs Clarification]`
* **Decision gate:**
  * **If clearcut AND no architectural conflicts:** Proceed to Phase 1.
  * **If ambiguous OR fix would conflict with recent refactors:**
    1. Add a `## Questions for User` section to `{ACTIVE_DIR}/[{PREFIX}-ID].md` with specific questions about the intended behavior or architectural direction.
    2. In the `## Work Log`, note what was reviewed and why escalation is needed.
    3. Update `{DASHBOARD}`: Set status to `[Needs Clarification]`.
    4. **STOP.** Do not attempt a fix. Inform the user: "{TYPE} requires clarification before a fix can be attempted. Questions have been posted in the ticket."

#### [Feature Only] Step 0: Context Gathering & Ambiguity Check

* **Read relevant `docs/` files** for the area being modified:
  - `docs/01_ARCHITECTURE.md` (Layer Structure, Dependency Rules)
  - `docs/02_PATTERNS.md` (Established Design Patterns)
  - `docs/03_CONVENTIONS.md` (Naming and Coding Conventions)
  - Any relevant system doc from `docs/systems/` for the affected area
* **Documentation discrepancy check:** Compare the area where the feature will be implemented against the `docs/` files. Does the existing code follow documented patterns? If not, note discrepancies and apply the Documentation Discrepancy Rules above. Discrepancies may affect your implementation approach.
* **Review** the feature requirements for clarity and completeness.
* **Assess** whether the requirements are clear enough to implement.
* **Document Findings:** Append to `## Work Log`:
  ```
  ### Phase 0: Feature Context
  **Relevant architecture rules:** [brief list or "None specific"]
  **Documentation discrepancies:** [specific discrepancies found, or "None — code matches docs"]
  **Planned approach:** [brief description of implementation strategy]
  ```
* **Decision gate:**
  * **If clear AND no unresolvable discrepancies:** Proceed to Phase 1.
  * **If ambiguous** (requirements are vague, multiple valid interpretations exist, or acceptance criteria are unclear):
    1. Add a `## Questions for User` section to `{ACTIVE_DIR}/[{PREFIX}-ID].md` with specific questions about the intended behavior.
    2. In the `## Work Log`, note what was reviewed and why the requirements are ambiguous.
    3. Update `{DASHBOARD}`: Set status to `[Needs Clarification]`.
    4. **STOP.** Do not attempt implementation. Inform the user: "Feature requires clarification before implementation can begin. Questions have been posted in the ticket."
  * **If documentation discrepancy is unresolvable** (unclear whether docs or code is correct):
    1. Add a `## Questions for User` section with the specific discrepancy.
    2. Update `{DASHBOARD}`: Set status to `[Needs Clarification]`.
    3. **STOP.**

### 3. Phase 1: Analysis

#### [Bug Only] Phase 1: Reproduction (Red)

* Create a test case that fails (reproduces the bug).
* Update `{ACTIVE_DIR}/[{PREFIX}-ID].md` `## Work Log` with the failing test output.

#### [Feature Only] Phase 1: Component Review

* Update `{DASHBOARD}`: Set status to `[Analysis]`.
* Identify the component/module where the feature will live.
* Examine related files in that component (imports, dependencies, existing patterns).
* Assess: Can this be implemented cleanly without significant refactoring?

**[Feature Only] Decision Point:**
* **If refactor is recommended:**
  - Update status to `[Needs Refactor]` in `{DASHBOARD}`.
  - Append refactor report to Work Log (see Refactor Report Format below).
  - **STOP.** Inform user: "Feature requires refactoring. See Work Log for details."
* **If clean implementation is possible:** Continue to Phase 2.

### 4. Phase 2: Test (Red)

* Create a test case that fails (tests the expected behavior).
* Update `{ACTIVE_DIR}/[{PREFIX}-ID].md` `## Work Log` with the failing test details.

> **Note for bugs:** Phase 1 already created the failing test. Phase 2 is the fix. See below.

### 5. Phase 3: Implementation (Green)

* **For bugs:** Modify code to pass the test from Phase 1.
* **For features:** Implement the feature to pass the test from Phase 2.
* Run regression tests to ensure no breaks.

### [Bug Only] 5.5. Phase 2.5: Post-Fix Integrity Check (MANDATORY GATE)

Before documenting, verify the fix maintains architectural integrity:

1. **Reversion Check:** Run `git diff HEAD` and compare against the Phase 0 git history findings. Does the diff UNDO any recent refactor commits? Specifically:
   - Does it re-introduce code that was deliberately deleted?
   - Does it restore old API signatures that were intentionally changed?
   - Does it add backward-compatibility shims or fallback paths?
   If YES to any: **STOP. Do not proceed.** Set status to `[Needs Clarification]` with explanation: "Proposed fix would revert [commit hash / PROJ-XX change]. Needs architectural guidance."

2. **Layer Boundary Check:** Does the fix introduce any forbidden dependency? (e.g., Core importing from Strategy, Simulation importing from UI) If YES: Rework the fix to respect layer boundaries.

3. **Convention Check:** Does the fix follow `CLAUDE.md` conventions and `docs/` standards?
   - Follows patterns documented in `docs/02_PATTERNS.md`?
   - Follows conventions documented in `docs/03_CONVENTIONS.md`?
   - Proper refactor over quick fix?
   - Root cause fix over workaround?
   - No magic numbers, no broad exception catches?
   If NO: Rework the fix before proceeding.

4. **Duplication Check (MANDATORY):** Does the fix re-implement logic that already exists elsewhere in the codebase?
   - Search for existing functions/methods that perform the same calculation, resolution, or transformation.
   - If existing logic is found: **delegate to it** (import and call) rather than writing a new copy.
   - If the existing logic needs minor adaptation, extract a shared utility and have both call sites use it.
   - If you wrote a new function: search the codebase for any other function with similar inputs/outputs/purpose.
   - **Red flags that indicate duplication:**
     - Importing private helpers (`_function_name`) from another module to reuse internally
     - Writing a formula that matches one in another file
     - Creating a method that walks the same data structure as an existing method
   If duplication is found: **Refactor to eliminate it before proceeding.** Extract the shared logic into a public utility in the module that owns the data, then have all call sites delegate to it.

5. **Design Quality Gate (MANDATORY):** Step back and evaluate the fix as if reviewing someone else's PR. Ask:
   - **"Is this what I would build if designing from scratch?"** If the answer is no, the fix is a workaround. Rework it.
   - **"Would I approve this in a code review?"** If you'd request changes (monkey-patching, overriding internal methods, suppressing behavior rather than fixing architecture), rework it.
   - **"Does this fix the root cause or mask the symptom?"** A fix that disables, overrides, or suppresses a behavior (e.g., `obj.method = lambda: False`) is masking the symptom. Find the architectural solution instead.
   - **"If a new developer read only this diff, would they understand why it works?"** If the fix requires comments explaining non-obvious workarounds, it's likely not the right design.
   Document your answers briefly in the Work Log under `### Phase 2.5: Design Review`.

6. **Tech Debt Assessment:** Does this fix reduce, maintain, or increase tech debt? A fix that increases tech debt requires justification documented in the Work Log. Prefer fixes that actively reduce tech debt.

* **If all checks pass:** Proceed to Phase 4 (Documentation).
* **If reversion detected:** Set `[Needs Clarification]`, document the conflict, **STOP**.
* **If layer/convention/duplication/design issues found:** Rework fix, re-run tests, then re-check.

### 6. Phase 4: Documentation & Gatekeeper

* Append your technical approach to `{ACTIVE_DIR}/[{PREFIX}-ID].md` `## Work Log`.
* State clearly which files were modified.

#### Documentation Sync (MANDATORY)

- If the fix/implementation changed architecture, patterns, or conventions -- update the relevant `docs/` file in this session.
- If you found a discrepancy in Phase 0 that you resolved -- update the `docs/` file to match your resolution.
- If you found a discrepancy you could not resolve -- it should already be escalated as `[Needs Clarification]`. If not, escalate now.
- **[Bug]** If the bug's root cause was an undocumented pattern or convention -- add it to the relevant `docs/` file.
- **[Feature]** If the feature introduced a new pattern, convention, or architectural element -- add it to the relevant `docs/` file.
- List all `docs/` files updated in the Work Log.

#### Status Update

* **Update Dashboard:** In `{DASHBOARD}`, change status to `[Awaiting Confirmation]`.
* **Action:** STOP. Do not update `{INDEX}`. Do not move the file.
* **Output:** Inform the user: "{TYPE} is fixed/implemented and passing tests. Status set to Awaiting Confirmation. Please verify."

---

## [Feature Only] Refactor Report Format

*For Phase 1 when refactor is needed:*

```markdown
---
### Refactor Recommended [YYYY-MM-DD HH:MM]
**Component Reviewed:** [list of files examined]
**Current Structure:** [brief description of existing code architecture]
**Issue:** [why clean implementation isn't feasible]
**Recommendation:** [suggested refactor approach]
**Impact:** [what files/systems would need to change]
---
```

---

## The Handoff Rule

If you run out of context or get stuck, write a summary in the Work Log and ask for a restart.
