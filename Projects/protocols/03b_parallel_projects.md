# PROTOCOL 03b: Parallel Project Execution (Coordinated Multi-Agent)
**Role:** Project Coordinator

## Configuration

| Variable | Value |
|----------|-------|
| ACTIVE_DIR | Projects/active_projects |
| SESSION_DIR | .agent_reports/proj-session |

---

**Goal:** Execute multiple projects in parallel using worktree-isolated agents, with file-level conflict avoidance. Each project runs sequentially through its own phases (per Protocol 03a), but multiple projects execute concurrently.

**CRITICAL CONSTRAINTS:**
- NEVER launch two project workers whose manifests share ANY file.
- ALL project workers MUST run in isolated git worktrees.
- Merge + test ONE project at a time (sequential merges to isolate regressions).
- Projects must have a `manifest.md` file to participate.

---

## Prerequisites

Each project must have:
1. An approved plan (`plan.md` with phases and tasks)
2. A file manifest (`manifest.md` listing all files the project will modify)
3. Phase checklists (`phase_N_checklist.md`)

Projects without `manifest.md` are rejected — tell the user to generate one via `/proj-start` or manually.

---

## Coordinator State

### Files-In-Use Registry

```
FILES_IN_USE = {
    "game/strategy/data/empire.py": "PROJ-87",
    "game/strategy/engine/game_session.py": "PROJ-87",
    "game/ui/panels/fleet_report.py": "PROJ-86",
}
```

- **Add entries** when a project worker is launched (ALL files from its manifest).
- **Remove entries** when a project completes and its branch is merged (or fails).

### Project Queue States

- `queued` — Waiting to start (no worker launched yet)
- `running` — Worker executing in worktree
- `merging` — Worker done, branch being merged and tested
- `done` — Merged and verified
- `waiting` — Blocked by file conflict with another running project
- `failed` — Tests failed after merge, or worker reported failure
- `overflow` — Worker hit context limit; partial progress merged, awaiting relaunch

---

## Execution Procedure

### Step 1: Session Setup

1. Parse arguments — specific PROJ-IDs or `all` (all active projects with manifests).
2. For each target project:
   a. Verify `{ACTIVE_DIR}/PROJ-XX/manifest.md` exists.
   b. Read manifest to get complete file list.
   c. Read `plan.md` to verify project has incomplete phases.
3. Build conflict matrix — for each pair of projects, check if their manifests share ANY file.
4. Create session directory:
   ```
   .agent_reports/proj-session/
   └── results/
   ```
5. Write initial dashboard to `{SESSION_DIR}/dashboard.md`.
6. Present conflict analysis and execution schedule to user.

### Step 2: Conflict Matrix

Build a simple overlap check:

```
For each pair of projects (A, B):
    shared_files = A.manifest_files ∩ B.manifest_files
    if shared_files:
        record conflict: A ↔ B on shared_files
```

From the conflicts, determine which projects can run in parallel:
- Projects with NO file overlap can run concurrently.
- Projects that share files must be serialized (second waits for first to complete).

Present to user:
```
Conflict Analysis:
- PROJ-86 ↔ PROJ-87: no overlap → can run in parallel
- PROJ-88 ↔ PROJ-87: share game_session.py → PROJ-88 waits for PROJ-87
- PROJ-89 ↔ PROJ-86: no overlap → can run in parallel
```

### Step 3: Rolling Loop

```
WHILE projects remain (queued, running, waiting, or overflow):

    # LAUNCH: Fill available slots
    FOR each queued/overflow project:
        IF worker slots available (< 3 concurrent):
            Check manifest files against FILES_IN_USE
            IF no conflicts:
                Add all manifest files to FILES_IN_USE
                Launch worker in worktree (background)
                Mark project as "running"
            ELSE:
                Mark project as "waiting"

    # PROCESS: Handle completed workers
    WHEN a worker completes:
        → Go to Step 4 (Merge & Verify)

    # UPDATE: Dashboard
    Update {SESSION_DIR}/dashboard.md
```

### Step 4: Merge & Verify

When a project worker completes:

1. Read the worker's result (status, worktree path, branch name).

2. **If worker completed ALL phases (SUCCESS):**
   a. Merge branch: `git merge <branch> --no-edit`
   b. Run full test suite: `python scripts/test_sharded.py`
   c. **If tests pass:**
      - Update project `plan.md`: all phases Complete, Current State = "Audit ready"
      - Mark project `done`
      - Report to user: "PROJ-XX complete! Tests: {count} passed."
   d. **If merge conflict:**
      - Attempt auto-resolve. If ambiguous, present to user.
      - If unresolvable: `git merge --abort`, mark `failed`.
   e. **If tests fail:**
      - `git reset --hard HEAD~1`
      - Report failures to user. Mark `failed`.

3. **If worker hit context limit (PARTIAL):**
   a. Merge partial branch (completed phases only).
   b. Run tests.
   c. If tests pass: mark `overflow`, project stays in queue for relaunch.
   d. If tests fail: revert, mark `failed`.

4. **If worker reported BLOCKED:**
   - Update project plan with findings.
   - Mark `failed`. Report to user.

5. **Always after processing:**
   - Remove project's files from FILES_IN_USE.
   - **Scan waiting projects:** For each waiting project, check if ALL its files are now free. If yes, mark as `queued` (will be picked up next loop iteration).
   - If a slot freed: next loop iteration will launch queued projects.

### Step 5: Session Summary

When all projects are processed:

```markdown
## Parallel Project Session Complete

### Projects Completed:
- PROJ-86: All phases done, merged, tests pass
- PROJ-87: All phases done, merged, tests pass

### Projects Failed:
- PROJ-88: Tests failed after merge — [details]

### Projects Partially Completed:
- PROJ-89: Phases 1-3 merged, Phase 4+ remaining (context overflow)

### Test Results:
- Final suite: XXXX passed, X failed
```

Clean up `{SESSION_DIR}/` directory.

---

## Worker Prompt Template

```
You are implementing PROJ-{ID} in an isolated git worktree. Other projects are
being implemented in parallel in separate worktrees.

## Your Role
Project Developer — autonomous TDD implementation (Protocol 03a).

## Protocols
Follow these protocols:
- Projects/protocols/02_plan_protocol.md (how to read/use the plan)
- Projects/protocols/03a_continue_working.md (autonomous work loop)

## Project Plan
{FULL_PLAN_MD_CONTENT}

## Project Files
Your project modifies these files (from manifest.md):
{MANIFEST_FILE_LIST}

## Instructions

1. Read the plan's Current State to understand where to start.
2. Read relevant docs/ files for the areas being worked on.
3. Run project status:
   python Projects/scripts/project_status.py PROJ-{ID}
   python Projects/scripts/current_task.py PROJ-{ID}
4. If this is the first session on this project, run: pytest tests/
5. Execute the autonomous work loop (Protocol 03a):
   - Work through ALL phases and tasks using Strict TDD
   - Use pytest tests/ --testmon for incremental testing
   - Check off subtasks as you complete them
   - Update Current State as you progress
   - Validate phases: python Projects/scripts/validate_phase.py PROJ-{ID} N
6. If you complete ALL phases:
   - Run full test suite: python scripts/test_sharded.py
   - Update Current State to indicate project complete
   - Report SUCCESS
7. If you approach context limit (~80%):
   - Stop at a clean point (end of task or phase)
   - Write comprehensive Current State handoff
   - Report PARTIAL with details of what's done and what remains
8. If you encounter a blocker:
   - Document in Current State
   - Report BLOCKED with details

## Constraints
- Follow Strict TDD — tests before implementation
- Code must be consistent with docs/
- If you find discrepancies between code and docs, note them
- Update checkboxes, notes, and Current State as you work
- Do NOT update the project dashboard (coordinator handles this)
```

---

## Manifest File Format

```markdown
# PROJ-XX File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/strategy/data/empire.py | Production | Add _galaxy, modify add/remove_fleet |
| game/strategy/engine/game_initializer.py | Production | Wire up galaxy references |
| tests/unit/strategy/data/test_empire_fleet_registration.py | Test | New file |
```

**Rules:**
- Include ALL production files that will be edited
- Include ALL test files (new and existing) that will be modified
- Type is `Production` or `Test`
- Notes briefly describe what changes
- Generated during `/proj-start` by scanning task `**File:**` fields and Key Files table

---

## Dashboard Format

Written to `{SESSION_DIR}/dashboard.md`:

```markdown
# Parallel Project Session — {DATE}

## Active Workers
| Slot | Project | Status | Files Locked |
|------|---------|--------|-------------|
| 1 | PROJ-86 | Running | empire.py, game_initializer.py, ... |
| 2 | PROJ-87 | Running | production_engine.py, ... |
| 3 | (free) | — | — |

## Waiting (file conflicts)
| Project | Blocked By | Shared Files |
|---------|-----------|-------------|
| PROJ-88 | PROJ-87 | game_session.py |

## Completed
| Project | Tests After Merge | Phases |
|---------|------------------|--------|
| (none yet) | | |

## Files In Use
- game/strategy/data/empire.py → PROJ-86
- game/strategy/engine/game_session.py → PROJ-87
```

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Worker completes successfully | Merge, test, update plan, release files |
| Worker context overflow | Merge partial, test, relaunch for remaining phases |
| Tests fail after merge | Revert merge, mark failed, release files, report to user |
| Merge conflict | Attempt auto-resolve; present to user if ambiguous |
| Worker blocked | Mark failed, release files, report to user |
| Manifest missing | Reject project; tell user to generate manifest |
| All slots blocked by conflicts | Report deadlock to user; suggest priority order |
| User wants to stop | Stop launching; wait for active workers; merge completed work |

---

## Integration Points

- **Protocol 03a** (`03a_continue_working.md`): Workers follow this for TDD execution.
- **Protocol 02** (`02_plan_protocol.md`): Workers follow this for plan reading/maintenance.
- **Project plans** (`Projects/active_projects/PROJ-XX/plan.md`): Workers update phases and Current State.
- **Manifests** (`Projects/active_projects/PROJ-XX/manifest.md`): Coordinator reads for conflict detection.
- **Git branches**: Each worktree creates a branch. Merged to current branch on success.
- **`.agent_reports/`**: Session directory is ephemeral per CLAUDE.md convention.

---

## Concurrency Limits

| Resource | Limit |
|----------|-------|
| Concurrent project workers | 3 max |
| Merge + test | 1 at a time (sequential) |

---

## The Handoff Rule

If the coordinator runs out of context mid-session:
1. Wait for all active workers to complete.
2. Merge any successful results.
3. Write handoff to `{SESSION_DIR}/dashboard.md`:
   - Projects completed and merged
   - Projects still running (with branch names)
   - Projects in queue
   - Waiting queue state
4. Inform user: "Context at capacity. Session state saved. Resume with `/proj-parallel` to continue remaining projects."
