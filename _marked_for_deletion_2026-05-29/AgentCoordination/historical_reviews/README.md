# Historical AgentCoordination reviews

Nineteen markdown files were generated during the V1–V4 plan rounds and the
implementation/system-review rounds of the agent coordination project (Apr
2026). They have served their purpose; the consolidated current policy is
`AgentCoordination/codex_agent_coordination_plan_final.md`. These are kept
here for the 30-day cooling-off window in case any historical decision needs
to be re-examined; after 2026-05-29 they are recoverable from git history.

## Inventory

| Round | Files |
|---|---|
| V1 plan | `codex_agent_coordination_plan.md` |
| V2 plan + claim responses | `codex_agent_coordination_plan_v2.md`, `codex_agent_coordination_claim_responses.md`, `claude_code_agent_coordination_v2_comments.md`, `opencode_deepseek_v4_pro_agent_coordination_v2_comments.md`, `antigravity_agent_coordination_v2_comments.md` |
| V3 plan | `codex_agent_coordination_plan_v3.md`, `claude_code_agent_coordination_v3_comments.md`, `opencode_deepseek_v4_pro_agent_coordination_v3_comments.md`, `antigravity_agent_coordination_v3_comments.md` |
| V4 plan | `codex_agent_coordination_plan_v4.md`, `claude_code_agent_coordination_v4_comments.md` |
| Initial agent comments (pre-V2) | `claude_code_agent_coordination_comments.md`, `opencode_deepseek_v4_pro_agent_coordination_comments.md`, `antigravity_agent_coordination_comments.md` |
| Baseline inventory reviews | `claude_code_baseline_inventory_review.md`, `opencode_deepseek_baseline_inventory_review.md` |
| Implementation review (mid-build) | `opencode_deepseek_implementation_review.md` |
| Final system review | `codex_agent_coordination_system_review.md` |

## How the policy converged

The final plan (`codex_agent_coordination_plan_final.md` at the AgentCoordination
top level) is the authoritative artifact. It supersedes every file here. The
five major decisions captured along the way:

1. `AGENTS.md` is the shared source of truth.
2. Runtime skills carry agent prefixes: `claude-`, `anti-`, `ocode-`, `codex-`.
3. Generated baseline + inventory + usage counters are tracked.
4. Reinforcement duplication is allowed only with closed validator markers.
5. Per-checkout, script-driven usage counters; never auto-delete.

Everything else in this archive is intermediate reasoning and review.
