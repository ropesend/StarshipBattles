# Audit Shrink

Comprehensive code shrinkage audit system. Combines deterministic analysis tools with LLM agent review to find dead code, near-duplicate code, and complexity hotspots across the production codebase.

## Purpose

Find opportunities to shrink the Starship Battles codebase by identifying:

1. **Dead code** — unused classes, functions, imports, and entire files
2. **Near-duplicate code** — similar functions/methods across different files or layers
3. **Complexity hotspots** — high-complexity functions that may hide duplication
4. **Shrinkage trends** — is the codebase growing, shrinking, or stable?

This tool is **read-only** — it does not modify any source code.

## Requirements

- Python 3.13+
- `vulture` (dead code detection)
- `radon` (cyclomatic complexity)
- Both installed via `requirements-dev.txt`

## Architecture

### Phase 1: Deterministic Analysis (runs in ~30 seconds)

`audit_shrink.py` orchestrates these tools against `game/`:

| Step | Tool | Output |
|------|------|--------|
| 1 | `Tools/loc/loc.py --detailed` | LOC baseline by section |
| 2 | `vulture` (100% confidence) | Confirmed dead code |
| 3 | `vulture` (80% confidence) | High-likelihood dead code |
| 4 | `Tools/check_orphans/` | Orphaned modules |
| 5 | `Tools/analyze_dependency_graph/` | Unreachable files |
| 6 | `radon cc` | Complexity hotspots |
| 7 | `clone_detector.py` | AST near-duplicate clusters |
| 8 | `manifest.py` | File inventory + shard rotation |

### Phase 2: Agent-Driven Semantic Review (LLM, ~5 minutes)

The `audit-shrink` skill launches 3 agents:

| Agent | Scope | Function |
|-------|-------|----------|
| Cross-Shard Duplication | All shards, every run | Validates clone detector output, hunts cross-layer duplication |
| In-Shard Deep Review | 1 shard, rotates weekly | Exhaustive file-by-file review of assigned shard |
| Dead Code Validator | All shards, every run | Validates vulture/orphan/dependency findings |

### Coverage Guarantee

| Coverage | Frequency | Mechanism |
|----------|-----------|-----------|
| 100% of files, deterministic tools | Every run | All tools run on the full game/ tree |
| Cross-shard duplication | Every run | Clone detector (all files) + Agent 1 |
| 100% of files, LLM deep review | Every 4 runs | Agent 2 rotates through 4 shards |
| Dead code validation | Every run | Agent 3 validates all findings |

### Shard Rotation

| Run | Agent 2 Deep Reviews |
|-----|---------------------|
| 1 | UI (`game/ui/`) |
| 2 | Simulation (`game/simulation/`) |
| 3 | Strategy (`game/strategy/`) |
| 4 | Foundation (`game/core/`, `game/engine/`, `game/ai/`, `game/research/`) |

## Usage

Single command — loads the skill and it handles everything:

```
/audit-shrink
```

This automatically:
1. Runs Phase 1 deterministic tools (~30 seconds)
2. Launches 3 LLM agents for semantic review (~5 minutes)
3. Compiles the final `report.md`

To run just Phase 1 by itself:

```bash
python Tools/audit_shrink/audit_shrink.py
```

To run individual tools standalone:

```bash
# Clone detector only:
python Tools/audit_shrink/clone_detector.py output.json

# Manifest only:
python Tools/audit_shrink/manifest.py output_dir/
```

## Output

Each run creates:
```
Reviews/results/YYYY-MM-DD_HHMMSS_audit_shrink/
├── raw/                              # Deterministic tool outputs
│   ├── loc_baseline.txt
│   ├── vulture_100.txt
│   ├── vulture_80.txt
│   ├── orphans.txt
│   ├── dead_deps.txt
│   ├── radon.json
│   ├── clones.json
│   └── manifest.json
├── findings/                         # Agent reports
│   ├── duplication_cross_shard.md    # Agent 1
│   ├── deep_review_UI.md             # Agent 2 (shard varies)
│   └── dead_code_validation.md       # Agent 3
└── report.md                         # Final compiled report

Reviews/results/shrink_tracker.json   # Run history for trend comparison
```

## Report Sections

The final `report.md` contains:

1. Executive Summary
2. Coverage Status (shard rotation progress)
3. Dead Code Inventory (by tier with LOC estimates)
4. Duplication Clusters (by severity, cross-shard pairs flagged)
5. Complexity Hotspots (CC >= 20)
6. In-Shard Deep Review Summary
7. Shrinkage Scorecard (estimated reclaimable LOC)
8. Prioritized Cleanup Plan (top 10 by impact/effort)
9. Trend Comparison (vs previous run)
10. Appendices

## Clone Detector

The clone detector parses all `.py` files in `game/` with Python's AST and:

1. Extracts function/method bodies as normalized token sequences
2. Computes structural fingerprints from statement types
3. Groups functions by fingerprint to avoid O(n^2) comparison
4. Uses difflib.SequenceMatcher for detailed comparison within groups
5. Clusters related pairs into connected clone groups
6. Outputs JSON with similarity ratios and LOC estimates

Minimum similarity threshold: 75%. Minimum function body: 5 lines.
