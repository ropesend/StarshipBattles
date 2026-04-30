# Agent Coordination

This directory holds the shared coordination policy for Starship Battles
agent surfaces (Claude Code, OpenCode/DeepSeek, Codex, Antigravity), plus the
generated artifacts that record the current state of those surfaces.

The authoritative policy is `codex_agent_coordination_plan_final.md`. Earlier
review rounds are kept as `*_v[1-4]_*.md` for historical context.

## Contents

- `codex_agent_coordination_plan_final.md` — authoritative policy.
- `generated/test_baseline.json` — repo-wide test count baseline; auto-updated by the sharded runner on green whole-suite runs. Tracked.
- `generated/agent_surface_inventory.json` — schema-versioned inventory of every skill surface. Regenerate with `inventory_agent_surfaces.py`. Tracked.
- `generated/skill_usage/by_install/<install_id>.json` — per-checkout skill usage counters. Tracked.
- `generated/skill_usage/summary.json` — aggregated usage summary. Tracked.
- `skill_rename_map.toml` — current-state report from the renamer. After the atomic prefix migration completed every entry shows `already_compliant`. The original migration map is preserved in git history at commit `c1b774b29` (atomic prefix rename).
- `SKILL_RENAMES.md` — current-state audit report. See `skill_rename_map.toml` note above; for the original old→new mapping, see git history at `c1b774b29`.
- `local/` — gitignored per-checkout state (install IDs).
- `*_v[1-4]_*.md`, `*_baseline_inventory_review.md`, `*_implementation_review.md`, `*_system_review.md` — historical agent review artifacts. Read for context only; do not treat as current policy.

## Tooling

| Command | Purpose |
| --- | --- |
| `python Tools/agent_coordination/inventory_agent_surfaces.py` | Regenerate `agent_surface_inventory.json`. |
| `python Tools/agent_coordination/check_skill_prefixes.py` | Fast prefix-only check; pre-commit-friendly. |
| `python Tools/agent_coordination/rename_skills_with_prefixes.py --dry-run` | Re-emit the rename plan/report (now a no-op; kept for audit and future renames). |
| `python Tools/agent_coordination/sanitize_claude_settings.py` | Classify entries in `.claude/settings*.json`. Dry-run by default. |
| `python Tools/agent_coordination/sanitize_claude_settings.py --apply` | Rewrite `STALE_WARN` entries to their proposed canonical form. Refuses if any `SECRET`/`DANGEROUS`/`EXTERNAL_REVIEW` finding is present. Creates a timestamped backup. |
| `python Tools/agent_coordination/validate_agent_surfaces.py` | Run every coordination check (11 currently). |
| `python Tools/agent_coordination/log_skill_usage.py --agent <name> --skill <name>` | Record one skill invocation. Auto-installed via Claude Code's `UserPromptExpansion` hook for `claude-*` skills; called manually by other agents per `AGENTS.md §"Skill Usage Logging"`. |
| `python Tools/agent_coordination/summarize_skill_usage.py` | Aggregate per-install counters into `summary.json`. |
| `python Tools/agent_coordination/backfill_legacy_slash_commands.py` | One-shot rewrite of leftover unprefixed `/foo` and `$foo` invocations in current docs. Idempotent. |
| `python Tools/test_sharded/test_sharded.py --refresh-baseline-timestamp` | Refresh `test_baseline.json verified_at` after a green run. |

## Coordination policy summary

1. `AGENTS.md` is the shared source of truth.
2. Runtime skills use `claude-`, `anti-`, `ocode-`, or `codex-` prefixes; reserved cross-agent prefix is `shared-`. Atomic migration completed at commit `c1b774b29`.
3. Generated baseline, inventory, and usage-counter files are tracked.
4. Claude local settings (`.claude/settings*.json`) are tracked. The sanitizer rewrites stale paths and the validator hard-fails on any `SECRET`/`DANGEROUS`/`EXTERNAL_REVIEW` finding.
5. Stable reinforcement duplication is allowed only with closed validator markers (`tdd`, `docs-first`, `code-doc-consistency`, `root-cause`, `no-ignore-folder`, `no-revert-unrelated`).
6. Volatile facts (exact test counts in prose, removed paths, stale baselines, `python -m unittest discover`) belong in generated artifacts.
7. OpenCode permission map keeps `*: allow` first; specific deny patterns follow. Defensive `anti-*: deny` is enforced.
8. Antigravity remains lower priority and focused on tooling/assets.
9. Legacy `.agent/workflows/` and `.agent/MIGRATION_PROGRESS.md` were removed at commit `af08531c8`. Git history is the archive.
10. Skill usage counters are advisory only and never authorize automatic deletion.

## Maintenance cadence

- Run `validate_agent_surfaces.py` before committing changes to any file under `AgentCoordination/`, `.claude/`, `.agent/`, `.agents/`, `.opencode/`, `Projects/protocols/`, `Tracking/protocols/`, `AGENTS.md`, `CLAUDE.md`, `.agents/CODEX.md`, or `opencode.json`.
- Re-run `inventory_agent_surfaces.py` whenever you add, remove, or rename a skill, and commit the updated JSON in the same change.
- Run the full sharded suite with `--refresh-baseline-timestamp` before large coordination commits so `verified_at` stays current even when counts are unchanged.

## CI

GitHub Actions workflow at `.github/workflows/agent_coordination.yml` runs the
focused tooling tests, the prefix checker, the inventory freshness check, and
the full validator on PRs that touch agent surfaces. See that file for the
exact path triggers.

## Optional pre-commit setup

`pre-commit` is not required, but if you want the validator and inventory
freshness checks to run before every commit that touches an agent surface,
the following config drops in cleanly. Save as `.pre-commit-config.yaml` at
the repo root:

```yaml
repos:
  - repo: local
    hooks:
      - id: agent-prefix-check
        name: Agent skill prefix check
        entry: python Tools/agent_coordination/check_skill_prefixes.py
        language: system
        pass_filenames: false
        files: ^(\.claude|\.agent|\.agents|\.opencode)/skills/
      - id: agent-inventory-freshness
        name: Agent surface inventory freshness
        entry: python Tools/agent_coordination/inventory_agent_surfaces.py
        language: system
        pass_filenames: false
        files: ^(\.claude|\.agent|\.agents|\.opencode)/skills/|^opencode\.json$|^AGENTS\.md$|^CLAUDE\.md$|^\.agents/CODEX\.md$
      - id: agent-validator
        name: Agent surface validator
        entry: python Tools/agent_coordination/validate_agent_surfaces.py
        language: system
        pass_filenames: false
        files: ^(AgentCoordination|\.claude|\.agent|\.agents|\.opencode|Projects/protocols|Tracking/protocols)/|^AGENTS\.md$|^CLAUDE\.md$|^opencode\.json$
```

Install once with `pre-commit install`. The same commands run unconditionally
in CI, so the hook is purely a local convenience to surface failures before
the push.
