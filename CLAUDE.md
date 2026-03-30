# Claude Code - Project Context

This file provides context for Claude Code when working on the Starship Battles project **in interactive mode** (VS Code plugin).

> **Note:** For automated CLI loop execution, see `Projects/refactor_loop/WORKER.md`. This file is for interactive sessions where you want explanations, questions, and collaborative problem-solving.

---

## THREE NON-NEGOTIABLE RULES

These three rules apply to ALL work, ALL tasks, ALL conversations. They are not guidelines — they are hard requirements. Violating any of them is a failed task, even if the code works.

### Rule 1: Test-Driven Development — ALWAYS

**Write tests BEFORE implementation. No exceptions.**

The TDD cycle is:
1. **Write a failing test** that describes the behavior you want
2. **Run the test** — confirm it fails for the right reason
3. **Write the minimum code** to make it pass
4. **Run the test** — confirm it passes
5. **Refactor** while keeping tests green
6. **Run the full relevant test suite** before considering the task done

**If you catch yourself writing implementation code without a failing test, STOP.** Delete or stash what you wrote, write the test first, then reimplement. This is not optional.

- DO NOT write implementation code first and then "backfill" tests after
- DO NOT write tests that are designed to pass against code you already wrote — that's confirmation bias, not TDD
- DO NOT skip the "run tests to see them fail" step — a test that has never failed has never proven anything
- DO NOT treat tests as a chore to do at the end — they are the FIRST thing you do

DO:
- Start every task by asking "what test would prove this works?"
- Write tests that would catch regressions if someone broke this feature
- Test edge cases, not just the happy path
- Run tests incrementally as you work, not just at the end

**Reminder at every stage:** Before writing any function, class, or method — ask yourself: "Have I written a test for this yet?" If no, write the test first.

### Rule 2: Documentation — CHECK Before, UPDATE After

**Read the relevant docs before starting. Update them when you're done. Every time.**

**BEFORE starting any task:**
1. Read [`docs/README.md`](docs/README.md) to identify which docs are relevant
2. Read the relevant docs (always 01-03, plus task-specific ones)
3. Understand the existing architecture and patterns before proposing changes

**AFTER completing any task that changes behavior, architecture, or patterns:**
1. Identify which docs are affected by your changes
2. Update those docs in the same commit as your code changes
3. If you added a new system, pattern, or convention — document it

**If you catch yourself about to commit code without checking whether docs need updating, STOP.** Review your changes against the docs before committing.

- DO NOT start coding without reading the relevant architecture docs first
- DO NOT finish a task and forget to update documentation
- DO NOT assume docs are up to date — verify by reading them
- DO NOT leave documentation updates for "later" — later never comes
- DO NOT silently diverge from documented patterns without raising it

DO:
- Treat docs as part of the deliverable, not an afterthought
- When you find a discrepancy between docs and code, STOP and raise it with the user
- Update docs in the same commit as the code change, not a separate commit
- When in doubt about whether a doc needs updating, update it

**The docs directory is the source of truth.** See the [Documentation First](#documentation-first) section below for the full reading order.

### Rule 3: Clean-Sheet Design — ALWAYS the Right Solution

**Solve the real problem. Never bandaid, never workaround, never "good enough for now."**

When faced with any design decision, ask: **"If I were building this from scratch with no legacy constraints, what would I do?"** Then do that.

- DO NOT override internal methods to work around a bug — fix the bug
- DO NOT monkey-patch objects to change behavior — redesign the interface
- DO NOT add special-case `if` branches to handle edge cases that reveal a design flaw — fix the design
- DO NOT duplicate existing logic because it's "easier than refactoring" — refactor
- DO NOT suppress errors or default behavior — understand why the error occurs and fix the cause
- DO NOT add backward compatibility layers — migrate and delete the old system
- DO NOT accept "this works for now" — if it's not the right design, it doesn't work

DO:
- Trace problems to their root cause before writing any code
- Refactor surrounding code if needed to support the clean solution
- Delete old systems entirely when replacing them (see [System Migration Policy](#system-migration-policy))
- Propose a larger refactor if the right fix requires it — let the user decide scope
- When the clean solution is significantly more work, explain the trade-off to the user and recommend the clean approach

**If you catch yourself writing a workaround, STOP.** Ask: "What is the real problem here?" Fix that instead.

---

## Your Role: Technical Consultant

When working in VS Code, you are a **helpful technical consultant**, not an automated worker.

**Be conversational and collaborative:**
- Explain your changes and reasoning
- Ask clarifying questions when requirements are unclear
- Suggest alternatives and trade-offs
- Provide context and background information
- Point out potential issues or improvements
- Discuss design decisions

---

## Documentation First

**Before reviewing, understanding, or changing ANY code, read the relevant `docs/` files first.**

The `docs/` directory is the authoritative source of truth for architecture, patterns, conventions, and system design. Start at [`docs/README.md`](docs/README.md) which provides a reading order by task type.

**Mandatory reading before any work:**
1. [`docs/01_ARCHITECTURE.md`](docs/01_ARCHITECTURE.md) — Layer structure, package APIs, protocols
2. [`docs/02_PATTERNS.md`](docs/02_PATTERNS.md) — 14 design patterns with file locations
3. [`docs/03_CONVENTIONS.md`](docs/03_CONVENTIONS.md) — Naming, file organization, imports

**Then read task-specific docs** (services, error handling, UI styling, combat, strategy, AI, etc.) as listed in the README.

### Code-Documentation Consistency

All code changes MUST remain consistent with the documentation. This is a two-way contract:

- **When writing code:** Follow the patterns, conventions, and architecture described in `docs/`. If the docs say to use a pattern, use it. If the docs say not to do something, don't do it.
- **When you find a discrepancy** between the docs and the code: **STOP and raise it with the user.** Do not silently follow stale docs or silently ignore them. Ask which is correct — the code or the docs — and fix whichever is wrong.
- **When changing architecture or patterns:** Update the relevant doc in the same change. Documentation and code must stay in sync.

---

## Project Overview

**Starship Battles** is a turn-based space combat strategy game with:
- Tactical ship-to-ship combat simulation
- Strategic galaxy map with fleet management
- Ship design workshop with component customization
- AI opponents with various difficulty levels

**Tech Stack:**
- Python 3.x
- Pygame for rendering
- Pytest for testing (7353 tests baseline)
- Test parallelization with pytest-xdist

**Display Target:**
- Minimum resolution: 2560x1600
- Optimized for: 4K (3840x2160)
- All UI layout calculations should assume 2560px minimum width

---

## Project Structure

```
game/
├── core/              # Foundation (registries, validation, utilities)
├── simulation/        # Combat simulation engine
│   ├── components/    # Ship components and abilities
│   └── formula_system.py  # Damage, accuracy, movement calculations
├── strategy/          # Galaxy map, fleets, planets, research
├── ai/                # AI controllers and targeting
└── ui/                # Pygame screens and rendering

tests/
├── unit/              # Fast unit tests
├── integration/       # Integration tests
└── simulation_tests/  # Battle simulation tests

Projects/
├── active_projects/   # Current refactoring projects
├── protocols/         # Development workflows
└── scripts/           # Automation helpers
```

---

## Development Workflows

### For Refactoring Projects

Projects are organized in `Projects/active_projects/PROJ-XX/`:
- `plan.md` - Project overview and current state
- `design.md` - Architecture and design decisions
- `decisions.md` - Decision log
- `phase_N_checklist.md` - Detailed task lists

**Protocols** (in `Projects/protocols/`):
- `02_plan_protocol.md` - How to use project plans
- `03a_continue_working.md` - Autonomous work loop
- `04_audit_project.md` - Audit methodology
- `08_automated_loop_protocol.md` - CLI automation (reference)

### TDD Workflow (Mandatory for ALL Code Changes)

**Every code change follows this workflow. No exceptions.**

1. **Read docs** — Understand the architecture before touching code (Rule 2)
2. **Write failing tests** — Define the expected behavior (Rule 1)
3. **Run tests** — Verify they fail for the right reason (Rule 1)
4. **Implement** — Write the cleanest solution, not the quickest (Rule 3)
5. **Run tests** — Verify they pass
6. **Refactor** — Clean up while tests stay green
7. **Update docs** — If behavior/architecture/patterns changed (Rule 2)
8. **Run full suite** — `pytest tests/ -n 12` before committing

**Test commands:**
```bash
# Incremental (fast)
pytest tests/ --testmon

# Targeted
pytest tests/path/to/test.py

# Full suite (use -n 12 for xdist parallelism)
pytest tests/ -n 12

# With coverage
pytest tests/ --cov=game -n 12
```

---

## Key Conventions

### Code Quality
- Use type hints for function signatures
- Add docstrings to public APIs
- Keep functions focused and small (<50 lines preferred)
- Avoid deep nesting (max 3 levels)

### Long-Term Quality
When faced with choices, prefer:
- Proper refactor over quick fix
- Root cause fix over workaround
- Comprehensive tests over minimal tests
- Named constants over magic numbers
- Specific exceptions over broad catches
- Extract abstraction over copy-paste
- Dependency injection over singletons
- Delegate to existing logic over reimplementing it

### System Migration Policy

**When a new system replaces an old one, ERADICATE the old system completely.**

- DO NOT add "fallback" code paths to old systems
- DO NOT keep backward compatibility layers "just in case"
- DO NOT leave old code commented out or behind feature flags
- DO NOT maintain parallel systems that do the same thing
- DO delete the old system entirely
- DO update ALL call sites to use the new system
- DO remove old data files, configs, and dependencies

**Save files are disposable.** Old saves are not migrated — they are discarded. Do not write compatibility shims or migration code for save data.

---

## Architecture Principles

**See [`docs/`](docs/README.md) for full architecture documentation.** The summary below is for quick reference only — the docs are authoritative.

### Layer Separation
- **Core** - No dependencies on other layers
- **Simulation** - Depends on Core only (no UI, no Pygame)
- **Strategy** - Depends on Core and Simulation
- **UI** - Top layer, depends on all others
- **AI** - Depends on Simulation and Strategy

### Key Patterns (see `docs/02_PATTERNS.md` for full list)
- **Registry Pattern** - Centralized component/ship/planet registration
- **Singleton via SingletonMeta** - Thread-safe metaclass in `game/core/singleton.py`
- **Protocol + TypeGuard** - Duck typing with runtime checks
- **Dependency Injection** - IRegistryProvider for production/test split
- **Facade/Delegate** - StrategySessionFacade, Ship→ShipCombatEngine
- **CQRS-lite** - Command/query separation with frozen DTOs
- **Two-Phase Ability Aggregation** - Intra-group MAX, inter-group SUM/MULTIPLY

---

## Common Tasks

### Adding a New Component Ability
1. Read [`docs/guides/adding_abilities.md`](docs/guides/adding_abilities.md) first
2. **Write tests** in `tests/unit/simulation/components/abilities/`
3. Define ability in `game/simulation/components/abilities/`
4. Add to `__init__.py` exports
5. Document in component schema
6. Update `components.json` with example usage
7. **Update [`docs/systems/ability_reference.md`](docs/systems/ability_reference.md)** with the new ability

---

## Testing Configuration

- **CLI parallel workers:** 12 (`-n 12`)
- **VS Code Test Explorer:** Use 4 workers (higher breaks the integrated test panel)
- **Test monitor:** `--testmon` for incremental runs
- **Baseline:** 7353 passed, 0 skipped

---

## Git Workflow

- Commit frequently with clear messages
- Use conventional commit format when applicable
- **Run full test suite before pushing** (Rule 1)
- **Verify docs are updated before committing** (Rule 2)
- Keep commits focused on single changes

---

## Subagent Report Output

Subagent reports go to `.agent_reports/` by default. This directory is git-ignored and its contents are disposable.

### Default Workflow

1. **Main agent** creates `.agent_reports/<descriptive-job-name>/` before spawning subagents
2. **Main agent** passes the full path to each subagent in its prompt
3. **Subagents** write reports ONLY to the provided directory, using the Write tool (not Bash)
4. **Main agent** reads/processes reports, then deletes the job folder when the task is complete

Reports in `.agent_reports/` are **ephemeral** — they will be deleted once the main agent finishes its task. Do not rely on them persisting across conversations.

### Skill/Protocol Override

When a skill or protocol specifies its own report location, use that location instead of `.agent_reports/`. The skill/protocol is authoritative. Examples:

- **Project reviews** → `Projects/active_projects/PROJ-XX/findings/` (protocols 01, 04, 09)
- **Codebase analysis sweeps** → `Reviews/results/{DATE}_{TYPE}_{SCOPE}/` (analysis-sweep skill)

The main agent passes the skill-specified path to subagents in the same way — subagents should always write to whatever path they are given.
