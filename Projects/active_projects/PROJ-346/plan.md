# PROJ-346: Closeout Sprint 4 - Vacuous test purges from PROJ-331/338/339/340 review

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-346` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. PROJ-339 vacuous purges (4 files) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. PROJ-338 vacuous purges (3 files) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. PROJ-340 vacuous purges + zero-coverage adds | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. PROJ-331 vacuous purges | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** Planning (awaiting implementation kickoff)
**Last Action:** Project scaffolded
**Next Action:** Begin Phase 1
**Blockers:** None (file-disjoint with PROJ-343 / PROJ-344 / PROJ-345; can run after them in any order)

## Overview

~14 tests across PROJ-331/338/339/340 pass without exercising production. Each must be replaced with a real characterization test pinning observed production behavior, not deleted outright (the file-coverage gap is real). Plus 8 zero-coverage paths in `ship_theme_manager.py`. NO production refactors.

## Goals

- PROJ-339: replace 7 vacuous tests with meaningful production-pinning assertions.
- PROJ-338: replace 4 vacuous tests likewise.
- PROJ-340: replace 3 + add ~8 new tests for `_validate_declared_keys`, missing-`assets`-block, non-dict `assets[ship_class]`, and the three zero-coverage public methods (`get_manual_scale`, `get_skin_path`, `get_portrait_path`).
- PROJ-331: replace 5 (UnboundedRegion tautology, hit_effects 3 "does not raise", shield early-return guard that doesn't fire).

## Scope

**In:** test files only. NO production-code changes.

**Out:** any production refactor. Apparent bugs found during replacement are documented as Observations in [decisions.md](decisions.md).

## Parallelism note

The four PROJ batches are file-disjoint. Up to 2 parallel general-purpose agents are safe (one per batch pair). **Do NOT use `isolation: "worktree"`** — known broken on this system per `Projects/active_projects/PROJ-329A/findings/concurrent_commit_audit.md`. Each agent must `git status` before staging and `git reset HEAD <unrelated-file>` if it sees other agents' staged work.

## Verification

- [ ] All 4 phase checklists complete
- [ ] `pytest tests/unit/ -q` — full suite stays green (15,708+ pass / 0 fail / 2 skip baseline; small delta acceptable)
- [ ] `python Tools/lint_test_files.py` — 0 violations
- [ ] User verified
