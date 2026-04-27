# Shared Agent Instructions

This file is neutral guidance for AI coding tools working in the Starship Battles repository. Tool-specific adapters live beside it and should not replace the shared project docs and protocols.

## Agent Adapter Map

- Codex: read `.agents/CODEX.md` before project work. Codex skills are prefixed `codex-` and live in `.agents/skills/`.
- Claude Code: use `CLAUDE.md` and `.claude/skills/`.
- Antigravity: use `.agent/skills/` and `.agent/workflows/`.
- OpenCode or DeepSeek: use this file plus the shared docs and protocols unless an OpenCode-specific adapter is added later.

Do not copy rules between adapter folders unless the user explicitly asks. Shared behavior belongs in `docs/`, `Projects/protocols/`, `Tracking/protocols/`, or this file.

## Non-Negotiable Project Rules

1. Use strict TDD for code changes. Write or identify the failing test first, run it to confirm the failure, implement the smallest clean fix, then rerun targeted and relevant regression tests.
2. Read docs before changing code. Start with `docs/README.md`, then always read `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, and `docs/03_CONVENTIONS.md`, plus task-specific docs.
3. Keep code and docs consistent. If code contradicts docs, determine which is more recent and correct, escalate unclear design intent, and update docs in the same change when behavior, architecture, patterns, or conventions change.
4. Solve root causes. Do not add compatibility shims, fallback systems, monkey patches, broad special cases, or duplicate logic when a clean design change is the right fix.
5. Never read, summarize, or act on `docs/_ignore/`.
6. Do not revert or overwrite unrelated user changes. Check the worktree before edits and work around existing changes unless the user asks for a reset.

## Project Basics

- Python target: 3.13 or newer. Use the repo virtual environment at `.venv` when available.
- Main final test command: `python Tools/test_sharded/test_sharded.py`.
- Incremental test command: `pytest tests/ --testmon`.
- Targeted test command: `pytest tests/path/to/test.py --testmon`.
- Combat Lab test command: `python -m combat_lab.run_tests`.
- Minimum UI target resolution: 2560x1600, optimized for 3840x2160.

## Shared Systems

- Project workflows live in `Projects/protocols/` and active projects live in `Projects/active_projects/PROJ-XX/`.
- Bug and feature ticket workflows live in `Tracking/protocols/` with active tickets under `Tracking/bugs/active/` and `Tracking/features/active/`.
- Development tool docs live in `Tools/README.md` and each tool subdirectory.
- Combat Lab docs live in `combat_lab/` and `docs/guides/simulation_testing.md`.

When a protocol conflicts with a tool adapter, follow the shared protocol for project behavior and the adapter only for tool mechanics.
