# OpenCode / DeepSeek — Implementation Review

Author: OpenCode with DeepSeek V4 Pro
Date: 2026-04-30
Commits: 959611a1c → ca24005cc (5 commits on codex/agent-coordination-baseline-inventory)

## Summary Judgment

Solid implementation. All six tools (inventory, baseline, sanitizer, prefix changer, prefix checker, validator) are well-structured, TDD-tested, and consistent with the final coordination plan. The dry-run artifacts (SKILL_RENAMES.md, rename_map.toml) look correct. No blocking issues. Two things to fix before the atomic rename commit, three non-blocking items to track.

## Blocking Issues

None.

## Non-Blocking Issues

### 1. CI Python version is 3.11 — repo declares 3.13+

`.github/workflows/agent_coordination.yml:31` uses `python-version: "3.11"`.
`pyproject.toml` declares `requires-python = ">=3.13"`. All current coordination
scripts work on 3.11 (stdlib `tomllib` exists since 3.11, `from __future__
import annotations` works since 3.7). But if a future tool uses 3.13-only
syntax (PEP 695 generics, `kwargs` in `TypedDict`, etc.), CI would break
silently while the user's local 3.13+ passes. Bump to `"3.13"`.

### 2. `VOLATILE_EXCLUDE_SUFFIXES` includes files the volatile scanner never touches

`check_volatile_facts` scans only `AGENTS.md`, `CLAUDE.md`, `.agents/CODEX.md`,
and `SKILL.md` files. The exclude list includes `Tools/test_sharded/test_sharded.py`,
`Tools/agent_coordination/README.md`, etc. — none of which are ever scanned.
Harmless dead exclusions; remove for clarity.

### 3. Settings sanitizer: no-classification for STALE_WARN rules

`classify_entry` detects `//c/Dev/Starship Battles` patterns as STALE_WARN and
proposes rewrites. But for entries like `Bash(git -C "c:\Dev\Starship Battles" log)`,
the stale segment is embedded inside a Bash wrapper. The rewrite correctly identifies
the stale path but the stale-Bash interaction (rewriting command internals) may produce
a valid-looking but non-functional command at runtime. The report correctly labels
these STALE_WARN (not auto-apply). This is the intended behavior. No action needed
beyond documenting that the dry-run-only design protects against this.

## TDD Coverage Audit

All four new tool files have dedicated test files with targeted failure/success
cases. No cosmetic tests found — every test exercises a specific rule edge.

| Tool | Tests | Coverage strengths |
|------|-------|--------------------|
| `sanitize_claude_settings` | 15 tests | classify_entry (9), rewrite (4), file scan (4), CLI (5). Covers SECRET/DANGEROUS/STALE_WARN/OK/EXTERNAL_REVIEW, missing-file, malformed JSON, additionalDirectories scanning. |
| `check_skill_prefixes` | 7 tests | Passes on prefixed skills, fails on unprefixed per-surface, shared-* exception, empty repo, CLI exit code. |
| `rename_skills_with_prefixes` | 10 tests | Map construction, shared- skip, invalid-name rejection, slash/$ref/path-literal/opencode-command discovery, dry-run writes audit artifacts without side effects. |
| `validate_agent_surfaces` | 25 tests | Each of the 9 checks has ≥2 tests. Baseline count-sum validation, implausible-count guard, inventory freshness diff, prefix fail, spec violation, anti-deny enforcement, volatile fact detection for all four patterns, reinforcement marker syntax/tag/SKILL.md exclusion, stale surfaces, Claude settings policy. |

**Test gap**: No test for `_broadens_permission` edge case where old path has
mixed separator styles (`\\` and `/`). The function's segment-count heuristic is
correct for the actual rewrite patterns used. Low risk.

## Counter-examples And Bugs Found

### `_broadens_permission` is sound for actual rewrite patterns

Attempted counter-examples that would produce false negatives (not broadening
when it is):

- **Original:** `Read(//c/Dev/Starship Battles/specific/**)` → **Proposed:** `Read(//c/Developer/StarshipBattles/**)` — this can't happen because `_propose_rewrite` only replaces the old checkout segment, not the rest of the path. The `specific/` segment is preserved.
- **Original:** `Read(//c/Dev/Starship Battles/)` → **Proposed:** `Read(**)` — caught by `len(prop_nonempty) < len(orig_nonempty)` (0 vs 3).
- **Original:** `Read(//c/Dev/Starship Battles/*.py)` → **Proposed:** `Read(//c/Developer/StarshipBattles//**/*.py)` — caught by `prop_double_stars > orig_double_stars` (1 vs 0).

The heuristic is defensive and correct for the single transformation
`_OLD_DEV_REWRITE_RE` performs.

### Volatile-fact regex corner cases (verified)

| Input | Expected | Actual | Correct? |
|-------|----------|--------|----------|
| `Baseline: 16060 passed` | Flag exact-count | Flagged | ✓ |
| `PROJ-12345` | No flag | Not flagged | ✓ |
| `port 16080; run tests` | Flag (false positive) | Flagged (acceptable, very unlikely pattern) | ✓ |
| `version 17000` alone | No flag | Not flagged | ✓ |
| `15405 tests baseline` | Flag stale-baseline only | Flagged stale (not double-flagged) | ✓ |
| `16063 tests baseline` | Flag exact-count | Flagged | ✓ (correct; this IS a test count in prose) |

### OpenCode permission semantics confirmed

OpenCode docs at https://opencode.ai/docs/permissions/ state:
> "Rules are evaluated by pattern match, with the **last matching rule winning**.
> A common pattern is to put the catch-all `"*"` rule first, and more specific
> rules after it."

The validator's `opencode.wildcard_not_first` warning (when `*` is not first) and
the renamer's `plan_opencode_permissions` (which puts `*` first) are both correct.
`fnmatch.fnmatchcase` used in the inventory matches OpenCode's wildcard semantics
(`*` and `?`).

## Open Questions

### 1. `.claude/settings.local.json` is still tracked with DANGEROUS rules

The sanitizer reports 0 OK / 1 SECRET / 1 DANGEROUS / 6 STALE_WARN for the
tracked file. The final plan says "track only if path safety can be proven."
The file is tracked (pre-existing). Is this the intended interim state — keep
tracked until the sanitizer can be applied in Phase 3 — or should it be
untracked now?

### 2. Should `continue-on-error: true` on prefix checker and validator flip after rename?

Lines 46 and 57 in the CI workflow mark prefix check and validator as
`continue-on-error: true` with comments "pre-rename; flip once Phase 5 lands."
After the atomic rename, these should become hard failures. Worth a note in
`SKILL_RENAMES.md` or the rename commit message.

### 3. `git_sha` field — pre-commit HEAD behavior

The baseline records HEAD SHA at run time, which is always the parent of the
commit that will contain the baseline update. This was discussed in prior
reviews. The validator does not check SHA freshness, so this is informational
only. Should the field be renamed to `source_git_sha` or documented in the
baseline schema?

## Final Recommendation

Approve. Fix the CI Python version before the rename commit (one-line change).
The remaining non-blocking items are cleanup. The dry-run artifacts demonstrate
the rename will produce 66 valid renames covering 141 reference sites. No
correctness block to proceeding. The atomic rename commit is safe to write and
review in one PR after: (1) CI Python bump, (2) user confirms settings.local.json
tracking decision, (3) user reviews SKILL_RENAMES.md.
