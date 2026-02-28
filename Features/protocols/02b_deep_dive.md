# PROTOCOL 02b: Feature Deep Dive (Complexity Analysis)
**Role:** Lead Feature Analyst

**Goal:** Perform thorough analysis of a feature that has turned out to be more complex than expected, or has been rejected 2+ times. Determine whether it can be implemented within the feature track or should be escalated to a formal Project.

**CRITICAL CONSTRAINT:** You do NOT have the authority to mark a feature as [Completed]. You do NOT have the authority to move files to `archived_features/`. Your authority ends at [Awaiting Confirmation] or [Needs Project].

**Trigger:** Manual — user explicitly requests deep dive for a specific FEAT-ID.

---

## Phase 1: Agent Swarm Exploration

Launch **4 Explore agents IN PARALLEL**, each focused on a different dimension:

**Agent 1 — Architecture Impact Analysis:**
* Trace which systems/layers would be affected by this feature.
* Map the module boundaries (core, simulation, strategy, ui, ai).
* Identify cross-layer dependencies that the feature would introduce.
* Output: List of affected systems and their relationships.

**Agent 2 — Dependency Mapping:**
* Find all code that depends on the systems identified by the feature scope.
* Assess blast radius: how many files/tests would need changes.
* Identify potential regression risks.
* Output: Dependency graph and blast radius estimate.

**Agent 3 — Similar Pattern Search:**
* Look for similar features/patterns already implemented in the codebase.
* Identify reusable abstractions, utilities, or patterns.
* Note any prior attempts that succeeded or failed.
* Output: Reusable code references and pattern recommendations.

**Agent 4 — Scope Assessment:**
* Review the feature request against the codebase architecture.
* Determine if this is truly a "feature" (small, isolated change) or a "project" (multi-phase, cross-cutting refactor).
* Compare to the definition: features are minor additions/changes that don't need a full project.
* Output: Feature vs Project recommendation with justification.

**After all agents complete:**
* Append findings to the ticket as `## Analysis Report` with subsections:
  - Architecture Impact
  - Dependency Map
  - Similar Patterns Found
  - Scope Assessment

---

## Phase 2: User Interview (Interactive)

Use AskUserQuestion to gather detailed requirements context:

1. "Can you describe the exact expected behavior for this feature?"
2. "Are there any edge cases or special scenarios this should handle?"
3. "What priority is this relative to other pending features?"
4. "Is this feature purely additive, or does it change existing behavior?"
5. "Are there any UI/UX requirements or mockups?"
6. "Would you accept a simplified version of this feature as a first iteration?"

**After gathering answers:**
* Append to ticket as `## Requirements Context` section.

---

## Phase 3: Complexity Assessment

Perform a structured complexity evaluation:

* **Lines of Code Affected:** Estimate new + modified LOC.
* **Files Requiring Changes:** Count and list.
* **New Abstractions Needed:** Any new classes, patterns, or utilities required?
* **Test Infrastructure:** Does existing test coverage support this area, or does new infrastructure need to be built?
* **Cross-Layer Changes:** Does this touch multiple architectural layers?

**Assign Complexity Rating:**
| Rating | Criteria |
| :--- | :--- |
| Simple | 1-3 files, single layer, existing patterns, <100 LOC |
| Moderate | 4-8 files, 1-2 layers, minor new abstractions, 100-300 LOC |
| Complex | 9+ files, 2-3 layers, new patterns needed, 300+ LOC |
| Project-Scale | Multiple layers, new architecture needed, significant test infrastructure, 500+ LOC |

**Append to ticket as `## Complexity Assessment` section.**

---

## Phase 4: Implementation Strategy

Based on the complexity rating:

**If Simple or Moderate:**
* Write a detailed implementation plan with:
  - Ordered file modification list
  - Test strategy (which tests to write first)
  - Reusable code identified in Phase 1
* Append to ticket as `## Implementation Strategy`.

**If Complex:**
* Break into smaller sub-tasks, each independently testable.
* Number sub-tasks in implementation order.
* Identify which sub-tasks could be separate feature tickets.
* Append to ticket as `## Implementation Strategy`.

**If Project-Scale:**
* Draft a Project Proposal:
```markdown
## Project Proposal [YYYY-MM-DD HH:MM]
**Feature:** [FEAT-ID]
**Reason:** Feature exceeds "small change" scope
**Estimated Systems Affected:** [count]
**Files Requiring Changes:** [list]
**Suggested Project Phases:** [numbered list]
**Recommendation:** Create Project in Projects/active_projects/
```
* Append to ticket as `## Implementation Strategy`.

---

## Phase 5: Resolution or Escalation

**If implementable (Simple, Moderate, or Complex):**
1. Proceed with TDD implementation (Phase 2-4 of Protocol 02).
2. Update `Features/feature_plan.md`: Set status to `[Awaiting Confirmation]`.
3. **STOP.** Inform the user: "Feature analyzed and implemented. Status set to Awaiting Confirmation. Please verify."

**If Project-Scale:**
1. Update `Features/feature_plan.md`: Set status to `[Needs Project]`.
2. **STOP.** Inform the user: "Feature exceeds the scope of the feature track. A Project Proposal has been added to the ticket. Recommend creating a formal Project in Projects/active_projects/."

**CRITICAL:** Do NOT mark as [Completed]. Do NOT move to `archived_features/`.
