# Claude Code Review: Baseline + Inventory Slice

Author: Claude Code (Opus 4.7, 1M context)
Date: 2026-04-28
Branch: `codex/agent-coordination-baseline-inventory`
Commit: `22f17ba16`
Reviews: [codex_agent_coordination_plan_final.md](codex_agent_coordination_plan_final.md), `Tools/test_sharded/test_sharded.py`, `Tools/agent_coordination/inventory_agent_surfaces.py`, generated artifacts, both new test files.

## Summary Judgment

Approve with non-blocking fixes. The core policy logic is correct: baseline updates only on full-suite green runs, count-change vs timestamp-only refresh paths are distinguished, skipped counts flow through XML parsing, and the inventory output is deterministic enough to track. Tests cover the policy state machine cleanly. The artifacts on disk match the intended schema, and `AGENTS.md`/`CLAUDE.md` no longer carry inline counts.

The main concerns are about durability rather than correctness in this commit — a couple of stale-pattern detectors are hardcoded to today's repo and will silently stop working as counts grow, and one OpenCode permission resolution choice depends on JSON ordering in a way the validator phase will need to formalize.

## Blocking Issues

None.

## Non-Blocking Issues

### 1. `HARDCODED_BASELINE_RE` is locked to one numeric era
`inventory_agent_surfaces.py:16` defines `HARDCODED_BASELINE_RE = re.compile(r"\b154\d{2}\+?\b")`. The current baseline is 16063, so this regex already cannot detect a future hardcoded `16060` if someone pastes one back into prose. Suggest: match `\b1[5-9]\d{3}\+?\b` (or wider) with a co-occurrence requirement of `tests`/`baseline`/`passed` on the same line, so it tracks growth without false positives on unrelated 5-digit numbers.

### 2. `stale_starship_path` literal is too specific
`STALE_LITERAL_PATTERNS` line 57 has the literal `//c/Dev/Starship Battles`. The volatile-fact rule should fail any absolute Windows or POSIX path inside tracked agent files, not one specific historical path. Recommend a regex like `[A-Za-z]:[\\/]` or `//[a-z]/` near agent-config files. This is what V4 §"Volatile facts" actually intends.

### 3. `_opencode_permission` iteration order is fragile
`inventory_agent_surfaces.py:121-125` iterates `permissions` items and uses last-match-wins. This works because the user's `opencode.json` declares `*` first, then specific deny patterns. If a future edit reorders rules so a deny appears before `*`, the wildcard "wins" and the inventory will report `allow` for everything visible. Either: (a) document required ordering and fail in the inventory tool when `*` is not first, or (b) verify OpenCode's actual semantics (most-specific-pattern-wins is more typical) and align. Recommend (b) — the inventory should match what OpenCode actually does.

### 4. `_parse_frontmatter` cannot handle list-style YAML
`inventory_agent_surfaces.py:74-91` is a hand-rolled `key: value` parser. List frontmatter (`allowed-tools:\n  - Read`) is silently dropped — the field is detected as present but value is empty. No current skill uses list form, so this is latent. The Phase 7 validator will care; either swap to PyYAML now or add a parser test asserting current limitations.

### 5. `STALE_LITERAL_PATTERNS` is substring-only
`python -m unittest discover` will match a line that *quotes* the string in a "do not use" warning. Low likelihood, worth a `#` line-comment exception or a word-boundary check before the validator phase.

### 6. `git_sha` is pre-commit
The known scrutiny point. The recorded SHA `2f34d174f` is one commit behind the artifact's actual commit. Accept it: semantically the field is "SHA tests were verified against," not "SHA the file lives at." Add a one-line note in `Tools/agent_coordination/README.md` or the test_sharded README clarifying that, so future readers don't try to "fix" it by chasing the SHA forward.

### 7. Missing test for "all collected, zero failures, but a shard returncode != 0" path
`_write_test_baseline_if_needed` paths are well-tested for the documented states, but `full_suite_success` is computed from four conditions in `main()`; only the policy function is unit-tested. A regression test that calls `main()` with one shard simulating returncode=1 (XML present, zero failures recorded) would lock in the safety check. Optional — the policy function itself is correctly gated.

### 8. No `generated_at` field on inventory
`agent_surface_inventory.json` has `schema_version` and `generated_by` but no timestamp. Phase 7 freshness checks ("does committed inventory match fresh generation?") work via diff regardless, but human readers can't tell when the file was last regenerated. Trivial to add; low priority.

### 9. `Projects/*/WORKER.md` not in surface inventory
V4 plan calls these out as a surface to inventory. This slice scopes to skills only. Fine to defer, just confirm it's in a later phase.

## Questions

1. Is OpenCode's skill-permission resolution most-specific-wins or last-match-wins? The current implementation assumes the latter. If it's the former, item #3 becomes a correctness bug, not just fragility.
2. Should the validator phase replace `HARDCODED_BASELINE_RE` and the `stale_starship_path` literal with the generalized regexes proposed in items #1 and #2, or should those generalize now in this slice so the committed inventory's `stale_references` already reflects the broader scope?
3. The pre-commit `git_sha` semantics — record as-is, or add an explicit `verified_at_sha` rename in schema v2 to disambiguate from "this artifact's commit"? My read: keep schema v1, document semantics. Confirm.

## Evidence

- Baseline policy state machine: `Tools/test_sharded/test_sharded.py:383-415` cleanly implements skipped/created/updated/refreshed/unchanged. Verified against `tests/unit/tools/test_test_sharded_baseline.py:79-194`.
- Skipped-count parsing: `Tools/test_sharded/test_sharded.py:271` (`total_skipped += int(suite.get("skipped", 0))`); test at `tests/unit/tools/test_test_sharded_baseline.py:50-76`.
- `full_suite_success` gating: `Tools/test_sharded/test_sharded.py:560-565` requires `total_tests == len(test_ids) AND total_failures == 0 AND total_errors == 0 AND no shard returncode != 0`. Stronger than the policy function's argument-level check.
- Determinism of inventory: `inventory_agent_surfaces.py:201` (sorted child dirs), `:293-296` (sorted findings by path/line/kind), `:337` (`sort_keys=True`), `:71` (`as_posix()` everywhere).
- `AGENTS.md` and `CLAUDE.md` no longer carry inline counts: verified via `git diff 22f17ba16~1 22f17ba16 -- AGENTS.md CLAUDE.md` — both rewritten to point at `AgentCoordination/generated/test_baseline.json`.
- Schema versions present: `test_baseline.json:8` and `agent_surface_inventory.json:3` both have `"schema_version": 1`.
- Inventory recorded `claude-specific_frontmatter` correctly: `agent_surface_inventory.json` shows `"argument-hint"` and `"disable-model-invocation"` flagged in `.agent/skills/` entries.
- OpenCode visibility correctly reflects current `opencode.json`: `.opencode/skills/audit-shrink` resolves to `allow` (matched by `*`), `.claude/skills/qa-triage` resolves to `allow` (matched by `*`, no specific deny — confirms `qa-*` deny only catches `qa-feedback`/`qa-triage` if they're literally prefixed with that pattern, which they are; verified in current inventory output).
- Stale references: `.agent/workflows`, `.agent/MIGRATION_PROGRESS.md`, removed doc paths, and one `//c/Dev/Starship Battles` hit are all detected without overreach.

## Final Recommendation

Land this slice as the Phase-2 foundation. The non-blocking issues (#1, #2, #3) are the ones to address before the validator phase begins, because they encode policy that the validator will inherit; landing them now keeps the inventory output stable as the source data for later checks. Items #4–#9 can fold into the validator slice or be queued as small follow-ups. The `git_sha` pre-commit semantics are acceptable; document and move on.
