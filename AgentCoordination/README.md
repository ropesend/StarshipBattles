# Agent Coordination

This directory holds the shared coordination policy for Starship Battles
agent surfaces (Claude Code, OpenCode/DeepSeek, Codex, Antigravity), plus the
generated artifacts that record the current state of those surfaces.

The authoritative policy is `codex_agent_coordination_plan_final.md`. Earlier
review rounds are kept as `*_v[1-4]_*.md` for historical context.

## Contents

- `codex_agent_coordination_plan_final.md` — current policy.
- `generated/test_baseline.json` — repo-wide test count baseline (auto-updated by the sharded runner; tracked).
- `generated/agent_surface_inventory.json` — schema-versioned inventory of every skill surface (regenerate with `inventory_agent_surfaces.py`; tracked).
- `skill_rename_map.toml` — machine-readable plan for the upcoming prefix rename (regenerate with the renamer dry-run).
- `SKILL_RENAMES.md` — human-readable audit artifact for the rename plan.
- `local/` — gitignored per-checkout state (e.g. install IDs for usage tracking).

## Tooling

| Command | Purpose |
| --- | --- |
| `python Tools/agent_coordination/inventory_agent_surfaces.py` | Regenerate `agent_surface_inventory.json`. |
| `python Tools/agent_coordination/check_skill_prefixes.py` | Fast prefix-only check; runs in pre-commit. |
| `python Tools/agent_coordination/rename_skills_with_prefixes.py --dry-run` | Refresh the rename plan + audit artifacts. |
| `python Tools/agent_coordination/sanitize_claude_settings.py` | Classify entries in `.claude/settings*.json`; dry-run only. |
| `python Tools/agent_coordination/validate_agent_surfaces.py` | Run every coordination check. |
| `python Tools/test_sharded/test_sharded.py --refresh-baseline-timestamp` | Refresh `test_baseline.json verified_at` after a green run. |

## Coordination policy summary

1. `AGENTS.md` is the shared source of truth.
2. Runtime skills use `claude-`, `anti-`, `ocode-`, or `codex-` prefixes; reserved cross-agent prefix is `shared-`.
3. Generated baseline and inventory files are tracked.
4. Sanitized Claude local settings may be tracked once safe; until then the sanitizer reports findings.
5. Stable reinforcement duplication is allowed only with closed validator markers (`tdd`, `docs-first`, `code-doc-consistency`, `root-cause`, `no-ignore-folder`, `no-revert-unrelated`).
6. Volatile facts (exact test counts in prose, removed paths, stale baselines, `python -m unittest discover`) belong in generated artifacts.
7. OpenCode permission map keeps `*: allow` first; specific deny patterns follow. Defensive `anti-*: deny` is required.
8. Antigravity remains lower priority and focused on tooling/assets.
9. Stale `.agent/workflows/` and `.agent/MIGRATION_PROGRESS.md` are scheduled for removal once replacement artifacts are in place.

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
