---
name: codex-starship-combat-lab
description: Work on Starship Battles Combat Lab and simulation tests. Use for combat_lab scenarios, ability test coverage, comparison scenarios, simulation validation, TestScenario authoring, Combat Lab data schemas, combat formulas, battle runner tests, and docs/guides/simulation_testing.md workflows.
---

# Codex Starship Combat Lab

Use this skill for Combat Lab scenario authoring, simulation test maintenance, and ability coverage.

## Required Context

1. Read `AGENTS.md` and `.agents/CODEX.md`.
2. Read `combat_lab/README.md`.
3. Read `docs/guides/simulation_testing.md`.
4. Read `docs/systems/combat_simulation.md` and `docs/systems/ability_reference.md` for combat or ability changes.
5. Read relevant `combat_lab/scenarios/`, `combat_lab/data/`, and validation docs for the task.

## Core Rules

- Use strict TDD for scenario/framework changes.
- Verify assumptions with precondition checks before relying on scenario outcomes.
- Prefer existing scenario templates such as `StaticTargetScenario`, `DuelScenario`, `PropulsionScenario`, and `ComparisonScenario` when they fit.
- Keep the one-category-per-ability pattern for ability-specific coverage.
- Test stacking behavior for abilities that can stack.
- Use surface distance, not center distance, when validating weapon ranges and hit probabilities.
- Use TOST/statistical checks where the framework expects probabilistic validation.

## Commands

- Run all Combat Lab tests: `python -m combat_lab.run_tests`.
- Filter or list scenarios using the options documented in `combat_lab/README.md` and `docs/guides/simulation_testing.md`.
- Run regular pytest tests when changes affect `game/` or pytest-covered integration behavior.

## Documentation

- Update `combat_lab/` docs when scenario authoring patterns or framework behavior changes.
- Update `docs/systems/ability_reference.md` when adding or changing abilities.
- Update `docs/systems/combat_simulation.md` when battle flow, damage, targeting, or simulation architecture changes.
