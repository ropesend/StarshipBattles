# Agent Coordination

This directory holds the shared coordination policy for Starship Battles
agent surfaces (Claude Code, OpenCode/DeepSeek, Codex, Antigravity), plus the
generated artifacts that record the current state of those surfaces.

The authoritative policy is `codex_agent_coordination_plan_final.md`. Earlier
review rounds are kept as `*_v[1-4]_*.md` for historical context.

## Contents

- `codex_agent_coordination_plan_final.md` — authoritative historical policy.
- `agent_surface_policy.json` — current mutable policy manifest for validator-enforced agent surface rules.
- `protocols/` — durable shared protocol specifications for agent coordination workflows, including `protocols/interagent_discussion.md`.
- `generated/test_baseline.json` — repo-wide test count baseline; counts-only canonical artifact auto-updated by the sharded runner on green whole-suite runs when counts change. Tracked.
- `generated/test_baseline/by_install/<install_id>.json` — per-checkout full-suite verification receipts. Tracked. Each checkout writes only its own UUID-keyed file, mirroring skill-usage ownership.
- `generated/test_baseline/summary.json` — aggregated test baseline verification summary. **Gitignored.** Purely derived from the canonical baseline plus `by_install/*.json`; regenerate with `summarize_test_baseline.py`.
- `generated/agent_surface_inventory.json` — schema-versioned inventory of every skill surface. Regenerate with `inventory_agent_surfaces.py`. Tracked.
- `generated/skill_usage/by_install/<install_id>.json` — per-checkout skill usage counters. Tracked. Each checkout writes only its own UUID-keyed file, so there are no cross-checkout merge conflicts.
- `generated/skill_usage/summary.json` — aggregated usage summary. **Gitignored.** Purely derived from `by_install/*.json` and rewritten on every skill invocation; tracking it produced meaningless merge conflicts on every parallel-checkout merge. Regenerate locally with `summarize_skill_usage.py` (or just invoke any skill — the logger rewrites it).
- `skill_rename_map.toml` — current-state report from the renamer. After the atomic prefix migration completed every entry shows `already_compliant`. The original migration map is preserved in git history at commit `c1b774b29` (atomic prefix rename).
- `SKILL_RENAMES.md` — current-state audit report. See `skill_rename_map.toml` note above; for the original old→new mapping, see git history at `c1b774b29`.
- `local/` — gitignored per-checkout state (install IDs).
- Historical V1–V4 plans, agent comments, baseline/implementation/system reviews — staged at `_marked_for_deletion_2026-05-29/AgentCoordination/historical_reviews/` and removed from this directory on 2026-04-29. Recoverable via `git mv` until 2026-05-29; recoverable from git history thereafter.

## Tooling

| Command | Purpose |
| --- | --- |
| `python Tools/agent_coordination/inventory_agent_surfaces.py` | Regenerate `agent_surface_inventory.json`. |
| `python Tools/agent_coordination/check_skill_prefixes.py` | Fast prefix-only check; pre-commit-friendly. |
| `python Tools/agent_coordination/rename_skills_with_prefixes.py --dry-run` | Re-emit the rename plan/report (now a no-op; kept for audit and future renames). |
| `python Tools/agent_coordination/sanitize_claude_settings.py` | Classify entries in tracked shared Claude settings. Dry-run by default. |
| `python Tools/agent_coordination/sanitize_claude_settings.py --apply` | Rewrite `STALE_WARN` entries to their proposed canonical form. Refuses if any `SECRET`/`DANGEROUS`/`EXTERNAL_REVIEW` finding is present. Creates a timestamped backup. |
| `python Tools/agent_coordination/validate_agent_surfaces.py` | Run every coordination check. |
| `python Tools/agent_coordination/log_skill_usage.py --agent <name> --skill <name>` | Record one skill invocation and update both the per-install counter and `summary.json`. Auto-installed via Claude Code hooks for `claude-*` skills; called manually by other agents per `AGENTS.md §"Skill Usage Logging"`. |
| `python Tools/agent_coordination/summarize_skill_usage.py` | Regenerate `summary.json` from per-install counters as a repair/maintenance command. |
| `python Tools/agent_coordination/summarize_test_baseline.py` | Regenerate the gitignored test-baseline verification summary from canonical counts and per-install receipts. |
| `python Tools/agent_coordination/backfill_legacy_slash_commands.py` | One-shot rewrite of leftover unprefixed `/foo` and `$foo` invocations in current docs. Idempotent. |
| `python Tools/test_sharded/test_sharded.py --refresh-baseline-timestamp` | Compatibility flag; green runs always refresh per-install test-baseline verification. |

## Coordination policy summary

1. `AGENTS.md` is the shared source of truth.
2. Runtime skills use `claude-`, `anti-`, `ocode-`, or `codex-` prefixes; reserved cross-agent prefix is `shared-`. Atomic migration completed at commit `c1b774b29`.
3. Generated baseline counts, baseline verification receipts, inventory, and per-install usage-counter files are tracked. Aggregated summary files are gitignored because they are purely derived from tracked per-install files.
4. Shared Claude settings (`.claude/settings.json`) are tracked. Local settings (`.claude/settings.local.json`) are ignored and skipped by validator content checks by default.
5. Stable reinforcement duplication is allowed only with closed validator markers (`tdd`, `docs-first`, `code-doc-consistency`, `root-cause`, `no-ignore-folder`, `no-revert-unrelated`).
6. Volatile facts (exact test counts in prose, removed paths, stale baselines, `python -m unittest discover`) belong in generated artifacts.
7. OpenCode permission map keeps `*: allow` first; specific deny patterns follow. Defensive `anti-*: deny` is enforced.
8. Antigravity remains lower priority and focused on tooling/assets.
9. Antigravity's live skill surface is limited by `agent_surface_policy.json`.
10. Legacy `.agent/workflows/` and `.agent/MIGRATION_PROGRESS.md` were removed at commit `af08531c8`. Git history is the archive.
11. Skill usage counters are advisory only and never authorize automatic deletion.
12. Per-install files (`generated/skill_usage/by_install/<uuid>.json` and `generated/test_baseline/by_install/<uuid>.json`) are owned by the machine whose `local/install_id.json` matches the filename UUID. Other checkouts' files may be pulled but never modified locally. The validator's ownership checks enforce this at commit time when a local `install_id.json` exists; see `Tools/agent_coordination/README.md` for details.

## Maintenance cadence

- Run `validate_agent_surfaces.py` before committing changes to any file under `AgentCoordination/`, `.claude/`, `.agent/`, `.agents/`, `.opencode/`, `Projects/protocols/`, `Tracking/protocols/`, `AGENTS.md`, `CLAUDE.md`, `.agents/CODEX.md`, or `opencode.json`.
- Re-run `inventory_agent_surfaces.py` whenever you add, remove, or rename a skill, and commit the updated JSON in the same change.
- Run the full sharded suite before large coordination commits so the local per-install baseline verification stays current even when canonical counts are unchanged.

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
