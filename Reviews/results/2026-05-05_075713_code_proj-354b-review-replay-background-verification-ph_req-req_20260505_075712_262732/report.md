# Review Report: 2026-05-05_075713_code_proj-354b-review-replay-background-verification-ph_req-req_20260505_075712_262732

## Metadata
- **Date:** 2026-05-05
- **Type:** code (delegated by Claude Code)
- **Description:** 
- **Agents Used:** 25

## Executive Summary
- **Total Findings:** 42
- **Critical:** 5 | **Major:** 13 | **Minor:** 14 | **Info:** 10
- **Overall Assessment:** Requires Immediate Attention

### Validation Summary
- **Original Findings:** 44
- **Confirmed:** 31 | **Downgraded:** 0 | **Rejected:** 2
- **Rejection Rate:** 4.5%
- **Findings Without Verdict:** 11

## Priority Findings (Top 10)

### 1. CRITICAL: Simulation layer imports from Strategy l
**ID:** AR-001
**Agent:** Validated
**Location:** `game/simulation/replay/replay_`
**Effort:** Unknown

**Location:** `game/simulation/replay/replay_`

---

### 2. CRITICAL: `compute_outcome_diff` treats list and t
**ID:** CJ-01
**Agent:** Validated
**Location:** `Unknown`
**Effort:** Unknown

**Location:** `Unknown`

---

### 3. CRITICAL: `compute_outcome_diff` missing-key / ext
**ID:** TC-C01
**Agent:** Validated
**Location:** `Unknown`
**Effort:** Unknown

**Location:** `Unknown`

---

### 4. CRITICAL: `compute_outcome_diff` type-mismatch bra
**ID:** TC-C02
**Agent:** Validated
**Location:** `Unknown`
**Effort:** Unknown

**Location:** `Unknown`

---

### 5. CRITICAL: `compute_outcome_diff` tuple path is unt
**ID:** TC-C03
**Agent:** Validated
**Location:** `Unknown`
**Effort:** Unknown

**Location:** `Unknown`

---

### 6. MAJOR: Multiple cross-class accesses to ReplayS
**ID:** AR-002
**Agent:** Validated
**Location:** `Unknown`
**Effort:** Unknown

**Location:** `Unknown`

---

### 7. MAJOR: Float comparison with strict `!=` — FPU
**ID:** CJ-02
**Agent:** Validated
**Location:** `Unknown`
**Effort:** Unknown

**Location:** `Unknown`

---

### 8. MAJOR: List length mismatch reports entire list
**ID:** CJ-03
**Agent:** Validated
**Location:** `Unknown`
**Effort:** Unknown

**Location:** `Unknown`

---

### 9. MAJOR: `_difference_to_dict` passes through unv
**ID:** CJ-04
**Agent:** Validated
**Location:** `Unknown`
**Effort:** Unknown

**Location:** `Unknown`

---

### 10. MAJOR: Worker loop missing outer exception hand
**ID:** ERR-354B-001
**Agent:** Validated
**Location:** `Unknown`
**Effort:** Unknown

**Location:** `Unknown`

---


## Findings by Severity

### Critical (5)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-001 | Simulation layer imports from Strategy l | `game/simulation/replay/replay_` | Unknown |
| CJ-01 | `compute_outcome_diff` treats list and t | `Unknown` | Unknown |
| TC-C01 | `compute_outcome_diff` missing-key / ext | `Unknown` | Unknown |
| TC-C02 | `compute_outcome_diff` type-mismatch bra | `Unknown` | Unknown |
| TC-C03 | `compute_outcome_diff` tuple path is unt | `Unknown` | Unknown |

### Major (13)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-002 | Multiple cross-class accesses to ReplayS | `Unknown` | Unknown |
| CJ-02 | Float comparison with strict `!=` — FPU | `Unknown` | Unknown |
| CJ-03 | List length mismatch reports entire list | `Unknown` | Unknown |
| CJ-04 | `_difference_to_dict` passes through unv | `Unknown` | Unknown |
| ERR-354B-001 | Worker loop missing outer exception hand | `Unknown` | Unknown |
| ERR-354B-002 | Listener registry accessed without synch | `Unknown` | Unknown |
| TC-M01 | No test for exactly-at-cap diff count (2 | `Unknown` | Unknown |
| TC-M02 | `ReplayVerificationResult` frozen datacl | `Unknown` | Unknown |
| TC-M03 | Race-condition shutdown path in `_on_rec | `Unknown` | Unknown |
| TC-M04 | R6 replay_dir-cleared-mid-verification p | `Unknown` | Unknown |
| TC-M05 | Weak diff assertions in coordinator PASS | `Unknown` | Unknown |
| TC-M06 | `save_json` returning `False` (non-excep | `Unknown` | Unknown |
| TC-M07 | `duration_ms` may be `None` in `Verifica | `Unknown` | Unknown |

### Minor (14)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-003 | Race window between worker start and lis | `game/strategy/services/replay_` | Unknown |
| AR-004 | shutdown docstring claims queue is dropp | `game/strategy/services/replay_` | Unknown |
| CJ-05 | `ReplayStore.delete` does not clean orph | `Unknown` | Unknown |
| CJ-06 | `ReplayStore.delete` returns `True` when | `Unknown` | Unknown |
| CJ-08 | `ReplayResolver.resolve` uses lazy metho | `Unknown` | Unknown |
| ERR-354B-003 | delete() orphans sidecar when replay JSO | `Unknown` | Unknown |
| ERR-354B-005 | save_json leaves stale .tmp file on rena | `Unknown` | Unknown |
| ERR-354B-006 | Worker drains queue on shutdown rather t | `Unknown` | Unknown |
| TC-m01 | `start()` idempotence untested | `Unknown` | Unknown |
| TC-m02 | `shutdown_all_coordinators` with multipl | `Unknown` | Unknown |
| TC-m03 | `_unlink_sidecar` error path (OSError) u | `Unknown` | Unknown |
| TC-m04 | `remove_on_record_persisted_listener` fo | `Unknown` | Unknown |
| TC-m05 | `VerificationSidecar.to_dict()` and `fro | `Unknown` | Unknown |
| TC-m06 | `_iter_replay_files` sidecar exclusion h | `Unknown` | Unknown |

### Info (10)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-005 | ReplayStore depends on verification side | `Unknown` | Unknown |
| AR-006 | ReplayVerificationCoordinator faithfully | `game/strategy/services/replay_` | Unknown |
| CJ-09 | `_evict_excess` tie-breaking on `st_mtim | `Unknown` | Unknown |
| CJ-10 | `shutdown_all_coordinators` may miss coo | `Unknown` | Unknown |
| ERR-354B-007 | All broad except annotations present and | `Unknown` | Unknown |
| ERR-354B-008 | Atomic write via tmp-then-rename confirm | `Unknown` | Unknown |
| ERR-354B-009 | Shutdown pattern correctly mirrors refer | `Unknown` | Unknown |
| TC-i01 | Deep mixed nesting not stress-tested in | `Unknown` | Unknown |
| TC-i02 | `_fallback_ship_builder` parameter of co | `Unknown` | Unknown |
| TC-i03 | Save root set to `None` after persist — | `Unknown` | Unknown |


## Agent Reports

- [Architecture Reviewer Report](findings/architecture_reviewer_report.md)
- [Code Quality Report](findings/code_quality_report.md)
- [Error Handling Report](findings/error_handling_report.md)
- [Test Coverage Report](findings/test_coverage_report.md)

## Appendix: Statistics

| Metric | Value |
|--------|-------|
| Total Findings | 42 |
| Critical | 5 |
| Major | 13 |
| Minor | 14 |
| Info | 10 |
| Agents Used | 25 |

---
*Report generated: 2026-05-05 01:14*
