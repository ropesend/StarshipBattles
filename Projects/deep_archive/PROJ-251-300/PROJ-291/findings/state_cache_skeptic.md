# State Coherence — Skeptical Audit (PROJ-283..290)

## Verdict

Clean with ONE critical logic bug and TWO cache-boundary concerns. The transient-field reset-on-load is correct, and the per-turn cache invalidation strategy is sound. However, a wrong-race-fallback in HappinessEngine._get_race_config() silently returns a mismatched race's config, and the CachedRaceRegistry invalidation is entirely manual with no on-disk mtime check.

## Investigation

### Scenario 1: Save/load transient coherence

**ColonySpeciesConfig.last_consumption_ratios** — CORRECT
- to_dict() explicitly omits the field (line 82: only food_allocation).
- from_dict() ignores transient keys (line 86-89).
- Fresh dict via default_factory per-instance (line 50).
- Post-load: empty dict, last_food_ratio property returns 1.0. SAFE.

**ColonySpeciesConfig.last_food_ratio property** — CORRECT
- Computed property (line 59-77): min(dict.values()) if non-empty, else 1.0.
- No setter; prevents shadowing.
- Post-load resets properly. SAFE.

**Planet._cached_habitability_multiplier cache** — CORRECT
- Marked init=False, repr=False, compare=False (line 146-148).
- Does NOT serialize in to_dict().
- Resets on from_dict() to default None.
- Keyed on turn number; TurnEngine bumps it at boundaries (line 501-506). SAFE.

**CachedRaceRegistry** — SAFE WITHIN SESSION
- Session-scoped; new instance per load.
- Manual invalidation required on save (line 941 race_setup_screen.py).
- No automatic mtime check for external edits. AT-RISK (see Finding 2).

### Scenario 2: Mid-turn race-editor save

**HappinessEngine._get_race_config() fallback** — WRONG
Lines 90-95: when race_id does NOT match empire.race_config.race_id, the function still returns race_config instead of None. This causes wrong base_happiness for mismatched species. CRITICAL (see Finding 1).

### Scenario 3: Colony population goes extinct mid-turn

**OrganicsConsumptionEngine** — CORRECT
- Clears ratios every turn (line 96).
- Writes 1.0 for zero-pop (line 101-102).
- SAFE.

**Planet cache** — turn-boundary refresh masks mid-turn staleness. ACCEPTABLE.

### Scenario 4: last_food_ratio property edge cases

All edge cases (empty dict, all 1.0, stale keys, drift) handled correctly. SAFE.

### Scenario 5: Per-turn cache + error boundary

**TurnStateSnapshot.restore()** — VULNERABILITY UNCERTAIN
Does restore() reset init=False cache fields? If not, stale multiplier persists post-rollback. VULNERABLE (see Finding 3).

### Scenario 6: Singleton pollution

**set_default_economy_config(None)** — AUTOUSE TEST FIXTURE GUARDS IT
Fixture at test line 75-81 resets singleton per test. No production pollution. ACCEPTABLE.

## Findings

### Finding 1: HappinessEngine._get_race_config() wrong-race fallback
**Severity:** Critical  
**Location:** game/strategy/engine/happiness_engine.py:90-95  
**What's wrong:** Unconditionally returns empire.race_config even when race_id does NOT match. Causes multi-species colonies to compute happiness using wrong race's base_happiness.
**Recommended fix:** Return None on mismatch, or wire the multi-species registry.

### Finding 2: CachedRaceRegistry no mtime check
**Severity:** Major  
**Location:** game/strategy/systems/race_library.py:265-294  
**What's wrong:** No automatic invalidation if race file is edited externally. Manual invalidate() call required; if bypassed, cache stales.
**Recommended fix:** Add optional mtime fallback in get_race(), or document constraint.

### Finding 3: Planet cache may not reset on PROJ-251 error rollback
**Severity:** Major  
**Location:** game/strategy/data/planet.py:146-151, turn_engine.py:540-554  
**What's wrong:** Cache fields marked init=False. Unclear if TurnStateSnapshot.restore() resets them. If not, stale multiplier persists post-rollback.
**Recommended fix:** Verify restore() resets cache fields; add explicit reset if not.

## False Positives

1. Numerical drift is realistic and correct per Liebig's Law.
2. HappinessEngine gracefully skips when race_config is None.
3. Test economy singleton pollution prevented by autouse fixture.
