# Claude Code - Project Context

This file provides context for Claude Code when working on the Starship Battles project **in interactive mode** (VS Code plugin).

> **Note:** For automated CLI loop execution, see `Projects/refactor_loop/WORKER.md`. This file is for interactive sessions where you want explanations, questions, and collaborative problem-solving.

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

## Project Overview

**Starship Battles** is a turn-based space combat strategy game with:
- Tactical ship-to-ship combat simulation
- Strategic galaxy map with fleet management
- Ship design workshop with component customization
- AI opponents with various difficulty levels

**Tech Stack:**
- Python 3.x
- Pygame for rendering
- Pytest for testing (6246 tests baseline)
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
│   └── formulas/      # Damage, accuracy, movement calculations
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

### Test-Driven Development

Always follow TDD:
1. Write tests first
2. Run tests to verify they fail
3. Implement minimal code to pass
4. Refactor while keeping tests green
5. Run full suite before committing

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

**Always prefer the clean-sheet design.** When choosing an approach, pick the one you'd choose if building from scratch. Don't compromise the design to make short-term tasks easier.

**Minimize technical debt. Maximize maintainability.**

### System Migration Policy (CRITICAL)

**When a new system replaces an old one, ERADICATE the old system completely.**

DO NOT:
- Add "fallback" code paths to old systems
- Keep backward compatibility layers "just in case"
- Leave old code commented out or behind feature flags
- Maintain parallel systems that do the same thing

DO:
- Delete the old system entirely
- Update ALL call sites to use the new system
- Remove old data files, configs, and dependencies

**Rationale:** Backward compatibility layers create confusion about which system is authoritative, bugs from rarely-tested code paths, and maintenance burden that accumulates over time.

**Save files are disposable.** Old saves are not migrated — they are discarded. Do not write compatibility shims or migration code for save data.

---

## Architecture Principles

For comprehensive architecture documentation, see [`docs/README.md`](docs/README.md).

### Layer Separation
- **Core** - No dependencies on other layers
- **Simulation** - Depends on Core only (no UI, no Pygame)
- **Strategy** - Depends on Core and Simulation
- **UI** - Top layer, depends on all others
- **AI** - Depends on Simulation and Strategy

### Key Patterns
- **Registry Pattern** - Centralized component/ship/planet registration
- **Ability System** - Component abilities with stacking rules
- **Hull as Component** - Ships are component containers
- **Two-Stage Aggregation** - Collect abilities, then apply modifiers

---

## Common Tasks

### Adding a New Component Ability
1. Define ability in `game/simulation/components/abilities/`
2. Add to `__init__.py` exports
3. Document in component schema
4. Write tests in `tests/unit/simulation/components/abilities/`
5. Update `components.json` with example usage

---

## Testing Configuration

- **CLI parallel workers:** 12 (`-n 12`)
- **VS Code Test Explorer:** Use 4 workers (higher breaks the integrated test panel)
- **Test monitor:** `--testmon` for incremental runs
- **Baseline:** 6246 passed, 0 skipped

---

## Git Workflow

- Commit frequently with clear messages
- Use conventional commit format when applicable
- Run full test suite before pushing
- Keep commits focused on single changes

