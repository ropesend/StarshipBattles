# Stateless Refactor Loop System

**Automated Claude CLI workflow for executing multi-phase refactoring projects**

---

## Overview

This system enables fully automated, stateless execution of refactoring tasks using Claude Code CLI. Each Claude instance:
1. Reads the master plan
2. Executes ONE phase
3. Updates the plan
4. Commits changes
5. Exits

The shell loop restarts Claude for the next phase, creating a fresh context each time.

---

## Quick Start

### Prerequisites

1. **Claude Code CLI** installed and authenticated
   ```bash
   npm install -g @anthropic-ai/claude-code
   claude --version
   ```

2. **All tests passing** - Verify before starting:
   ```bash
   cd "C:/Dev/Starship Battles"
   pytest tests/
   ```

3. **Clean git state** - Commit or stash any pending changes

### Running the Loop

```bash
cd "C:/Dev/Starship Battles"
./loop_runner.sh
```

**That's it!** The system will:
- Execute phases one at a time
- Run tests after each phase
- Commit successful phases to git
- Continue until all tasks complete or an error occurs

### Stopping the Loop

- **Ctrl+C** - Stop gracefully after current iteration
- The loop will resume from where it left off when restarted

---

## System Architecture

```
refactor_loop/
├── refactor_plan.md          # Master task list (read/write by Claude)
├── WORKER.md                 # System prompt for automated worker
└── REFACTOR_LOOP_README.md   # This file

refactor_loop/loop_runner.ps1  # Main automation loop (PowerShell)
refactor_loop/loop_runner.sh   # Main automation loop (Bash)
CLAUDE.md                     # Rules and context for interactive Claude

Projects/
├── scripts/
│   ├── check_completion.py   # Verify all tasks complete
│   ├── update_plan.py        # Update plan programmatically
│   └── commit_phase.py       # Create standardized commits
└── active_projects/
    └── PROJ-XX/
        ├── plan.md           # Project overview
        └── phase_N_checklist.md  # Detailed tasks
```

---

## How It Works

### 1. Master Plan (`refactor_loop/refactor_plan.md`)

Contains:
- **Agent Context** - Handoff notes between Claude instances
- **Master Task List** - All projects and phases with checkboxes
- **Execution Log** - History of completed phases

Example task:
```markdown
### PROJ-45: Error Handling and Exception Management Refactor
- [ ] Phase 1: Foundation - Exception Hierarchy & Error Codes
- [ ] Phase 2: Core Layer - Fix Core Module Error Handling
- [x] Phase 3: Simulation Layer - Components & Formulas
```

### 2. Claude Rules (`refactor_loop/WORKER.md`)

10 critical rules for automated execution:
1. **Non-Interactive** - No user input allowed
2. **Read Plan First** - Always start with `refactor_loop/refactor_plan.md`
3. **One Phase Per Session** - Execute only next incomplete phase
4. **Test-Driven Development** - Tests before implementation
5. **All Tests Must Pass** - Never proceed with failures
6. **Update Plan and Exit** - Mark complete and exit immediately
7. **Git Commits** - Handled automatically by loop
8. **Context Management** - Handoff notes if context exhausted
9. **Follow Protocols** - Use project protocols strictly
10. **Quality Standards** - Maintain code quality

### 3. Loop Runner (`loop_runner.sh`)

Bash script that:
- Checks for incomplete tasks
- Runs Claude CLI with `--dangerously-skip-user-approval` (YOLO mode)
- Waits 10 seconds between iterations
- Exits when all tasks complete or max iterations reached

### 4. Helper Scripts

**`check_completion.py`** - Parse plan file and count tasks
```bash
python Projects/scripts/check_completion.py refactor_loop/refactor_plan.md
# Output: Task Status: Total: 45, Completed: 12, Incomplete: 33
```

**`update_plan.py`** - Programmatically update plan
```bash
# Mark phase complete
python Projects/scripts/update_plan.py mark-complete refactor_loop/refactor_plan.md PROJ-45 1

# Update agent context
python Projects/scripts/update_plan.py update-context refactor_loop/refactor_plan.md \
    "PROJ-45 Phase 1" "Ready for Phase 2" "5199 passed"

# Add execution log entry
python Projects/scripts/update_plan.py add-log refactor_loop/refactor_plan.md \
    PROJ-45 "Phase 1" "Complete" "5199 passed"
```

**`commit_phase.py`** - Create standardized git commits
```bash
python Projects/scripts/commit_phase.py . PROJ-45 1 "Exception Hierarchy" "5199 passed"
# Creates: [PROJ-45] Phase 1: Exception Hierarchy - Automated
```

---

## Workflow Example

### Iteration 1: PROJ-45 Phase 1

1. **Loop starts** → Runs `check_completion.py` → Tasks remain
2. **Claude starts** → Reads `refactor_loop/refactor_plan.md`
3. **Claude finds** → First `[ ]` task: PROJ-45 Phase 1
4. **Claude loads** → `Projects/active_projects/PROJ-45/plan.md`
5. **Claude loads** → `Projects/active_projects/PROJ-45/phase_1_checklist.md`
6. **Claude executes** → Creates exception hierarchy (TDD)
7. **Claude tests** → `pytest tests/` → All pass
8. **Claude updates** → Marks phase `[x]` in `refactor_loop/refactor_plan.md`
9. **Claude updates** → Agent Context with handoff notes
10. **Claude commits** → `[PROJ-45] Phase 1: Exception Hierarchy - Automated`
11. **Claude exits** → Session complete
12. **Loop waits** → 10 seconds
13. **Loop continues** → Next iteration

### Iteration 2: PROJ-45 Phase 2

Same process, fresh Claude instance, new context.

---

## Customization

### Ordering Projects

Edit `refactor_loop/refactor_plan.md` to reorder projects/phases as needed. The system executes tasks in order from top to bottom.

### Adjusting Sleep Duration

Edit `loop_runner.sh`:
```bash
SLEEP_DURATION=10  # Change to desired seconds
```

### Max Iterations

Edit `loop_runner.sh`:
```bash
MAX_ITERATIONS=1000  # Safety limit
```

### Custom Prompts

Edit the Claude prompt in `loop_runner.sh`:
```bash
claude \
    --dangerously-skip-user-approval \
    -p "Your custom prompt here"
```

---

## Monitoring Progress

### Real-Time

Watch the terminal output - each iteration shows:
- Task status
- Claude session output
- Git commit confirmation

### Check Status Anytime

```bash
python Projects/scripts/check_completion.py refactor_loop/refactor_plan.md
```

### View Execution Log

Open `refactor_loop/refactor_plan.md` and scroll to "Execution Log" table.

### Git History

```bash
git log --oneline --grep="Automated"
```

---

## Troubleshooting

### Loop Exits with Error

**Check:** Last Claude session output for errors
**Fix:** Manually resolve issue, update plan, restart loop

### Tests Failing

**Check:** `pytest tests/` output
**Fix:** Claude should fix or remove invalid tests per Rule 5
**Manual:** If Claude exhausted context, fix manually and restart

### No Progress

**Check:** `refactor_loop/refactor_plan.md` Agent Context for blockers
**Fix:** Address blocker, update context, restart loop

### Git Conflicts

**Check:** `git status`
**Fix:** Resolve conflicts manually, commit, restart loop

### Claude Not Exiting

**Check:** CLAUDE.md Rule 6 compliance
**Fix:** Manually exit (Ctrl+C), update plan, restart loop

---

## Safety Features

1. **Max Iterations** - Prevents infinite loops (default: 1000)
2. **Test Validation** - All tests must pass before phase completion
3. **Git Commits** - Each phase is committed separately
4. **Context Handoff** - Detailed notes if context exhausted
5. **Error Handling** - Loop exits on Claude CLI errors

---

## Best Practices

### Before Starting

- [ ] All tests passing
- [ ] Git state clean
- [ ] Projects ordered correctly in `refactor_loop/refactor_plan.md`
- [ ] Sufficient disk space for git history

### During Execution

- Monitor terminal output periodically
- Check `refactor_loop/refactor_plan.md` Agent Context for issues
- Review git commits occasionally

### After Completion

- Review all automated commits
- Run full test suite: `pytest tests/`
- Verify code quality
- Push to remote: `git push`

---

## Advanced Usage

### Running Specific Project

Edit `refactor_loop/refactor_plan.md` to comment out other projects:
```markdown
<!-- ### PROJ-41: Documentation Health Remediation -->
<!-- - [ ] Phase 1: Audit & Categorization -->

### PROJ-45: Error Handling
- [ ] Phase 1: Foundation
```

### Parallel Execution (Experimental)

Run multiple loops on different branches:
```bash
# Terminal 1
git checkout -b refactor-proj-45
./loop_runner.sh

# Terminal 2
git checkout -b refactor-proj-42
# Edit refactor_loop/refactor_plan.md to only include PROJ-42
./loop_runner.sh
```

**Warning:** Requires careful branch management and merge strategy.

### Dry Run Mode

Test without committing:
```bash
# Edit loop_runner.sh to skip git commit
# Comment out the commit_phase.py call
```

---

## Files Reference

| File | Purpose | Modified By |
|------|---------|-------------|
| `refactor_loop/refactor_plan.md` | Master task list | Claude (automated) |
| `refactor_loop/WORKER.md` | System prompt for worker | Manual (setup) |
| `refactor_loop/loop_runner.ps1` | Main loop script (PowerShell) | Manual (setup) |
| `refactor_loop/loop_runner.sh` | Main loop script (Bash) | Manual (setup) |
| `Projects/scripts/check_completion.py` | Task completion checker | Loop script |
| `Projects/scripts/update_plan.py` | Plan updater | Claude (optional) |
| `Projects/scripts/commit_phase.py` | Git commit helper | Claude (optional) |

---

## FAQ

**Q: Can I pause and resume?**
A: Yes! Ctrl+C to stop, `./loop_runner.sh` to resume.

**Q: What if a phase is too large for one context?**
A: Claude will update Agent Context with handoff notes. Next instance continues.

**Q: Can I manually edit the plan during execution?**
A: Not recommended. Stop loop, edit, restart.

**Q: How do I skip a phase?**
A: Mark it `[x]` manually in `refactor_loop/refactor_plan.md`.

**Q: What if I disagree with a change?**
A: `git revert <commit>`, update plan, restart loop.

**Q: Can I use this for non-refactoring tasks?**
A: Yes! Adapt `refactor_loop/refactor_plan.md` and `CLAUDE.md` for any multi-phase work.

---

## License

Part of the Starship Battles project.

---

## Support

For issues or questions, review:
1. This README
2. `CLAUDE.md` rules
3. `refactor_loop/refactor_plan.md` Agent Context
4. Git commit history
5. Terminal output logs
