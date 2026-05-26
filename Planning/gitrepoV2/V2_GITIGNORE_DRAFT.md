# V2 `.gitignore` Draft

> **Drafted:** 2026-05-25 against V1 HEAD `bc755f012`. Status: **draft, pending user review.**
>
> Starting point: the live V1 `.gitignore` (already well-tuned post-asset-reorg). Changes vs V1:
> - **Dropped** the "Legacy pre-rename size-folder names" block (V1 lines 131–150). V2 starts fresh; pre-rename leftover directories cannot exist.
> - **Dropped** `combat_lab/test_history.json.migrated` (V1 line 78). That's a per-test-id-shard migration sentinel; V2 starts post-migration.
> - **Added** defense-in-depth ignores for V1 accidentally-tracked artifacts so they cannot reappear (`--help/`, `--output-dir/`, `panel_profile.prof`, `test_profiling_*.json*`, `.coverage`, broader `*.log` and `*.prof`).
> - **Added** `external_artifacts.local.json` (the per-machine vault config from Phase 6).
> - **Added** `.opencode/node_modules/` (V1 has this untracked; we ignore it explicitly so npm install doesn't surprise anyone).
> - Kept everything else verbatim from V1.

## Proposed `.gitignore`

```gitignore
# Python caches
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Virtual environments
env/
venv/
.env
.venv

# IDE / editor state
.vscode/
.idea/
.VSCodeCounter/

# Ship designs live in output/ships/ (covered by /output/ below).
# Root-level config JSONs are tracked individually; this one is generated.
/component_presets.json

# Runtime / generated output
/output/
/combat_lab/output/
/combat_lab/battle_states/
combat_lab/test_history/
combat_lab/battle.log
collect_log*.txt

# Test infrastructure
.pytest_cache/
.testmondata*
.test_durations.json
.test_file_duration_history.json

# Coverage
.coverage
coverage.json
htmlcov/

# Profiling output (root-level *.prof / *.json from profilers)
*.prof
test_profiling_*.json
test_profiling_*.json.tmp

# Generic log files (battle logs, tool logs)
*.log

# Personal development tools (left in for compatibility; harmless if absent)
VibeCodingHotkeys.ahk
cleanup_nul.py

# Windows reserved-name workaround: tools sometimes create a literal
# "nul" file when redirected to NUL incorrectly. Always ignore.
nul

# QA Observer per-session output
Tools/qa_observer/session_data/

# PROJ-314: ship-portrait regeneration manifest (per-run, ephemeral)
Tools/regenerate_ship_portraits/last_run.json

# Test artifact: MagicMock stringified as a directory path
MagicMock/

# Subagent temporary reports
.agent_reports/

# Agent coordination per-checkout state
AgentCoordination/local/
# Skill usage summary is purely derived from by_install/*.json and is regenerated
# by Tools/agent_coordination/log_skill_usage.py on every skill invocation.
AgentCoordination/generated/skill_usage/summary.json
# Test baseline summary is derived from the canonical baseline and per-install
# verification receipts.
AgentCoordination/generated/test_baseline/summary.json
# Per-checkout state for the OpenCode review system
AgentCoordination/opencodereview/local/
# Scratchpad: agent transient working area. Contents are local-only and may be
# deleted at any time. See AgentCoordination/SCRATCHPAD.md for conventions.
AgentCoordination/Scratchpad/

# Claude settings backups + per-machine local settings
.claude/settings.json.backup.*
.claude/settings.local.json.backup.*
.claude/settings.local.json
.claude/worktrees/

# Codex repo config is tracked; local Codex artifacts stay ignored.
.codex/*
!.codex/config.toml

# OpenCode npm artifacts
.opencode/node_modules/

# Generated analysis output
dead_code_candidates.txt

# Corrupt backup files
*.corrupt

# Phase-aware execution worktrees and review checkouts
.worktrees/
AgentCoordination/opencodereview/local/worktrees/

# External-artifact vault per-machine config (Phase 6 deliverable).
# The companion tracked file is `external_artifacts.example.json`.
external_artifacts.local.json

# Ship-theme workflow source folders. If any survive the V1→V2 import they
# stay out of Git. Should be empty / nonexistent in V2 after curation.
assets/images/ship_themes/*/Production/*
assets/images/ship_themes/*/Original Art/*

# Component image-derivative preview workflow folders. Stay ignored so
# `Tools/process_components/recreate_ai_samples.py` doesn't accidentally
# stage its output.
assets/images/components/_ai_recreate_enhanced_preview/*
assets/images/components/_ai_recreate_enhanced_fixes_preview/*
assets/images/components/_ai_recreate_enhanced_repaired_preview/*
assets/images/components/_ai_recreate_enhanced_corrected_preview/*
assets/images/components/_ai_recreate_preview/*
assets/images/components/_processed_preview/*
assets/images/components/_processed_preview_v2/*
assets/images/components/_processed_preview_v3/*

# ============================================================================
# Image-derivative manifests + generated size folders.
#
# Each multi-size asset family stores ONE master size in source control and
# regenerates sibling sizes locally at startup via
# `game.assets.image_derivatives`. See `docs/03_CONVENTIONS.md`
# "Image Asset Derivatives — canonical pattern" for the full table.
#
# Master sizes (tracked in LFS per .gitattributes):
#   components/1024/, flags/flag_*/1024/, stars/1024/, planets/2048/
# ============================================================================

# Components: master is 1024/; all others are derivatives.
assets/images/components/.component_derivatives_manifest.json
assets/images/components/64/*
assets/images/components/128/*
assets/images/components/256/*
assets/images/components/512/*
assets/images/components/2048/*

# Flags: master is flag_*/1024/; all others are derivatives.
assets/images/flags/.flag_derivatives_manifest.json
assets/images/flags/flag_*/32/*
assets/images/flags/flag_*/64/*
assets/images/flags/flag_*/128/*
assets/images/flags/flag_*/256/*
assets/images/flags/flag_*/512/*

# Stars: master is 1024/; all others are derivatives.
assets/images/stars/.star_derivatives_manifest.json
assets/images/stars/128/*
assets/images/stars/256/*
assets/images/stars/512/*

# Planets: master is 2048/; all others are derivatives.
assets/images/planets/.planet_derivatives_manifest.json
assets/images/planets/128/*
assets/images/planets/256/*
assets/images/planets/512/*
assets/images/planets/1024/*

# ============================================================================
# Defense in depth: V1 accidentally-tracked tool output.
#
# These paths should never exist in V2 (the cleanup pass that removes them
# from V1 happens BEFORE the V2 import — see MIGRATION_CLASSIFICATION.md
# SKIP rows). The ignores are belt-and-braces so a future agent invoking the
# same tool with the same wrong flags doesn't re-introduce them.
# ============================================================================

# audit_shrink output: when the runner is invoked with `--help` or
# `--output-dir <dir>` mis-parsed as positional, it creates a folder
# named literally `--help` or `--output-dir` and writes raw/ into it.
/--help/
/--output-dir/

# Build / dist (defense in depth; V1 had none, V2 might publish wheels later)
build/
dist/
*.egg-info/

# Pre-deletion staging buckets (Stage-0 hygiene; never imported)
_marked_for_deletion_*/
```

## Changes vs V1, line by line

### Dropped from V1

| V1 entry | Why dropped |
|---|---|
| `combat_lab/test_history.json.migrated` (V1 L78) | Per-test-id-shard migration sentinel. V2 starts post-migration; the marker is irrelevant. |
| Legacy pre-rename size-folder block (V1 L131-150: `assets/images/components/Components 64/` … `assets/images/Planets/Planets_V3/`) | These mute pre-rename leftover dirs from `git status` on machines that pulled the old commits. V2 starts fresh — no machine pulled the pre-rename commits into V2 — so the block is unnecessary. |
| Duplicate `AgentCoordination/generated/skill_usage/summary.json` (V1 L154) | V1 has this line twice; consolidated. |

### Added in V2

| New entry | Why added |
|---|---|
| `.coverage` | V1 has `.coverage` **accidentally tracked** as a top-level file (DI-logged separately). V2 must not inherit. |
| `*.prof` | V1 has `panel_profile.prof` **accidentally tracked**. Catches any future profiler output dumped at repo root. |
| `test_profiling_*.json`, `test_profiling_*.json.tmp` | V1 has ~12 such files tracked accidentally. |
| `*.log` | V1 ignores only `collect_log*.txt`, `combat_lab/battle.log`, and lets every other `*.log` slip through; the legacy_tickets battle logs (49 MiB BUG-122 + others) entered the repo this way. Broader rule prevents recurrence. |
| `/--help/`, `/--output-dir/` | V1 has these **accidentally tracked** at the repo root from a tool invocation that mis-parsed flag names as positional output-dir arguments (DI-logged separately). Anchored to root so a legitimate file named `--help` inside a tool's test fixtures wouldn't be caught. |
| `external_artifacts.local.json` | Phase 6 deliverable — per-machine artifact vault config. The example/template `external_artifacts.example.json` IS tracked. |
| `.opencode/node_modules/` | V1 has `npm install` not run (no `node_modules/` on disk locally), but the `.opencode/package.json` exists; once anyone runs `npm install`, `node_modules/` would surface. Defense in depth. |
| `_marked_for_deletion_*/` | V1 has `_marked_for_deletion_2026-05-29/` as a tracked staging bucket. The pattern is intentional during cleanup work but should never enter V2. |
| `assets/images/ship_themes/*/Production/*`, `*/Original Art/*` | V1 hardcodes specific themes' `Production/` directories (Ossivine, Prismsteel, Aetherwake). Globbed pattern is cleaner and covers any theme that adds workflow folders. |

### Adjusted in V2

- `.codex/*` + `!.codex/config.toml` block: unchanged; restated as a section for clarity.
- The "QA Observer" / `PROJ-314 ship-portrait` per-tool lines: kept verbatim (still load-bearing).

## What this file deliberately does NOT do

- No `*.png filter=lfs` style rules — that's `.gitattributes` territory. The path-scoped LFS rules live in `V2_GITATTRIBUTES_DRAFT.md`.
- No `docs/_ignore/` rule — `docs/_ignore/` is a tracking-allowed location for personal notes; the convention is "do not read it," not "do not track it." (The V1 `.gitignore` reflects this too.) **Cross-check at import:** if V1's actual `docs/_ignore/` content was personal user notes, classify it per Task D.
- No size-threshold rules. Git LFS handles large-file storage by path scope, not size threshold. Adding a size check here would either be redundant or create classification ambiguity.

## Exit criteria

- Draft `.gitignore` ready before V2 first hygiene commit. ✓
- Inventory-derived patterns added. ✓ (the V1 accidentally-tracked-output defenses)
- Risky broad patterns reviewed. ✓ (`*.log`, `*.prof` are the broadest; both are appropriate at root level and on per-tool subpaths because V1 surveys show no legitimate `*.log` / `*.prof` content that should be tracked).
- `.gitignore` is committed before any source/asset import per Phase 10 step 4.
