---
name: codex-starship-performance-profiling
description: Run Starship Battles Scalene profiling workflows. Use when profiling speed, CPU hotspots, memory growth, copy volume, performance regressions, or optimization candidates with Tools/profiling/run_scalene.py and docs/guides/performance_profiling.md.
---

# Codex Starship Performance Profiling

Use this skill for evidence-driven performance investigations. Profiling may identify optimization work, but it does not permit architecture shortcuts.

## Required Context

1. Read `AGENTS.md`.
2. Read `docs/README.md`, `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, and `docs/03_CONVENTIONS.md`.
3. Read `docs/guides/performance_profiling.md`.
4. Read task-specific docs for the profiled area.

## Workflow

1. Define the performance question in user-visible or test-visible terms.
2. Identify or add a focused failing/characterization test before changing production code.
3. Use `Tools/profiling/run_scalene.py --dry-run` to verify the command.
4. Run CPU mode first:

```powershell
python Tools/profiling/run_scalene.py pytest --mode cpu --pytest-target tests/path/to/test.py --pytest-filter test_name
python Tools/profiling/run_scalene.py app --mode cpu
python Tools/profiling/run_scalene.py combat-lab --mode cpu
```

5. Use `--mode full` only when CPU results indicate allocation, leak, or copy-volume questions.
6. Interpret Scalene output by classifying hotspots as Python, native, system, memory, or copy-volume dominated.
7. Optimize only root causes that preserve documented layering and maintainability.
8. Re-run the same test and profiling scenario after changes.
9. Record before/after notes using `Tools/profiling/workflows/profile-pass-template.md` when the result should be durable.

## Guardrails

- Do not optimize from a single noisy profile.
- Do not profile the full suite first.
- Do not add hidden globals, cross-layer imports, compatibility shims, monkey patches, or benchmark-only branches.
- Prefer algorithmic improvements, scoped caching with explicit invalidation, removal of duplicate work, and reduced allocation/copy churn.
- Keep generated profiles under `output/profiles/scalene/`; they are ignored by git.
