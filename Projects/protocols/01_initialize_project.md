# PROTOCOL 01: Initialize Project
**Role:** Project Architect

**Goal:** Transform a user's refactor/addition request into a comprehensive, actionable plan through deep code review, multi-agent analysis, and iterative refinement with the user.

---

## Phase A: Initial Understanding

1. **Read User's Description**
   - Parse the project description from the prompt
   - Identify: What is being added/refactored? Why?

2. **Assign Project ID**
   - Read `Projects/projects_index.md` to get next sequential ID (PROJ-XX)
   - Create project file: `Projects/active_projects/PROJ-XX.md`

3. **Deep Code Review**
   - Launch 2-3 Explore agents to understand current architecture:
     - Agent 1: Examine the primary code area being modified
     - Agent 2: Identify related components and dependencies
     - Agent 3: Review existing patterns and conventions
   - Document findings in `## Initial Analysis` section

4. **Initial Questions & Suggestions**
   - Use AskUserQuestion to:
     - Clarify scope and boundaries
     - Understand priorities and constraints
     - Confirm assumptions
     - Offer suggestions based on findings
   - Document answers in `## Decisions Log`

5. **Draft Tentative Plan**
   - Create high-level outline of phases and major tasks
   - Present to user for initial feedback

---

## Phase B: Deep Dive Swarm Review

Launch **6-8 Explore agents in parallel** to analyze the codebase with the tentative plan in mind.

### Swarm Role Menu (Select 6-8 based on project scope)

| Role | Focus | When to Include |
|------|-------|-----------------|
| **Architecture Analyst** | Overall structure, module boundaries, coupling | Always |
| **Dependency Mapper** | Import chains, circular dependencies, ripple effects | Always |
| **Test Impact Analyst** | Which tests break, coverage gaps, new tests needed | Always |
| **Pattern Scout** | Existing patterns to follow, anti-patterns to avoid | Refactors, new features |
| **Risk Assessor** | Edge cases, race conditions, data integrity risks | Complex changes |
| **Data Flow Tracer** | How data moves through affected code | Data model changes |
| **API/Interface Reviewer** | Public interfaces, backwards compatibility | API changes |
| **Performance Analyst** | Bottlenecks, scaling concerns, hot paths | Performance-sensitive areas |

**Selection Logic:**
- Architecture, Dependency, and Test Impact are ALWAYS included
- Select 3-5 additional roles based on project type
- Document which roles were selected and why

**Output:** Document all swarm findings in `## Swarm Findings` section:
```markdown
## Swarm Findings

### Architecture Analysis
[Findings from Architecture Analyst]

### Dependency Map
[Findings from Dependency Mapper]

### Test Impact
[Findings from Test Impact Analyst]

### [Additional Role Findings]
...

### Hidden Dangers Identified
- [Risk 1]
- [Risk 2]

### Opportunities Discovered
- [Opportunity 1]
```

---

## Phase C: Plan Refinement

1. **Process Swarm Findings**
   - Identify surprises, risks, and opportunities
   - Determine if plan needs adjustment

2. **Second Round of Questions**
   - If swarm uncovered unknowns, ask user for clarification
   - Present any significant risks and get user acknowledgment
   - Add all decisions to `## Decisions Log`

3. **Create Detailed Plan**
   - Break into logical Phases
   - Each Phase contains Tasks
   - Each Task contains Subtasks (checkboxes)
   - Apply complexity tags: [Simple], [Medium], [Complex]
   - **IMPORTANT:** Any [Complex] task should be broken into simpler subtasks
   - Include test requirements for each task

4. **Finalize Plan Document**
   - Ensure all sections are complete
   - Update `## Current State` with initial state
   - Update `Projects/projects_index.md` with new project

5. **User Approval**
   - Present complete plan to user
   - Get explicit approval before implementation begins

---

## Plan Document Template

Create `Projects/active_projects/PROJ-XX.md` with this structure:

```markdown
# PROJ-XX: [Project Title]

## Overview
[High-level description of the refactor/addition]

## Goals
- [Goal 1]
- [Goal 2]

## Scope
**In Scope:**
- [Item 1]
- [Item 2]

**Out of Scope:**
- [Explicitly excluded item 1]
- [Explicitly excluded item 2]

## Current State
**Last Updated:** [YYYY-MM-DD HH:MM]
**Last Agent Action:** [What was just completed]
**Next Action:** [What should happen next]
**Blockers:** [Any blockers or None]
**Context for Next Agent:** [Important context]

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| YYYY-MM-DD | [Decision made] | [Why this choice was made] |

## Initial Analysis
[Findings from Phase A code review]

## Swarm Findings

### Architecture Analysis
[Findings]

### Dependency Map
[Findings]

### Test Impact
[Findings]

### Hidden Dangers
- [Risk 1]

### Opportunities
- [Opportunity 1]

## Phases

### Phase 1: [Phase Name]
**Objective:** [What this phase accomplishes]
**Status:** [Not Started / In Progress / Complete]

#### Task 1.1: [Task Name] [Simple/Medium]
**Tests:** [Test file/location - written BEFORE implementation]
- [ ] Subtask A
- [ ] Subtask B
- [ ] Subtask C
**Notes:** [Added during implementation]

#### Task 1.2: [Task Name] [Simple]
**Tests:** [Test file/location]
- [ ] Subtask A
- [ ] Subtask B
**Notes:**

### Phase 2: [Phase Name]
...

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All tasks checked off
- [ ] All tests passing
- [ ] Regression tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified
```

---

## Termination

After user approves the plan:
1. Update `## Current State` to indicate plan is approved and ready for implementation
2. Update `Projects/projects_index.md` with project entry
3. Inform user: "Project PROJ-XX plan is approved and ready. Use 'Continue Project' prompt to begin implementation."
