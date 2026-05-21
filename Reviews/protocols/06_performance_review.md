# PROTOCOL 06: Performance Review
**Role:** Code Review Coordinator
**Extends:** 00_review_core.md

**Purpose:** Conduct a performance-focused analysis to identify bottlenecks, inefficient algorithms, memory issues, and optimization opportunities.

---

## Overview

The Performance Review focuses on finding performance issues through code analysis. While it can't replace profiling with real data, it can identify common performance anti-patterns, algorithmic inefficiencies, and areas likely to cause problems at scale.

**Best For:**
- Pre-optimization analysis
- Understanding why something is slow
- Identifying scaling concerns
- Finding memory leaks/issues
- Optimizing critical paths
- Game loop and frame-rate sensitive code

---

## Default Agent Configuration

### Required Agents
| Agent | Focus |
|-------|-------|
| Performance Profiler | Overall performance analysis, common anti-patterns |
| Algorithm Analyst | Algorithm efficiency, Big-O analysis, data structure choices |

### Recommended Agents
| Agent | Focus |
|-------|-------|
| Memory/Resource Analyst | Memory leaks, resource management, allocation patterns |
| Hot Path Identifier | Frequently executed code, critical paths |

### Optional Agents
| Agent | Focus | Include When |
|-------|-------|--------------|
| Data Flow Tracer | Data movement, I/O patterns | I/O-bound concerns |
| Architecture Reviewer | System-level performance patterns | System-wide review |
| Documentation Consistency Reviewer | Documented patterns vs actual implementation | Performance issues may stem from pattern deviation |
| Module Specialist (x N) | Deep dive on performance-critical modules | Complex systems |

### Typical Agent Count: 4-8

---

## Phase A: Scope Definition (Extended)

### Questions to Ask User

Use AskUserQuestion with these options:

1. **Review Scope**
   - Entire codebase
   - Specific hot paths (list known slow areas)
   - Specific module/feature
   - Game loop / frame-critical code
   - Startup / initialization code

2. **Performance Concerns**
   - CPU-bound (computation heavy)
   - Memory-bound (memory usage, allocations)
   - I/O-bound (file, network, database)
   - Latency-sensitive (response time)
   - Throughput-sensitive (operations per second)
   - All of the above

3. **Known Slow Areas**
   - Any specific operations known to be slow?
   - When does slowness occur? (startup, peak load, specific operations)
   - Any profiling data available?

4. **Performance Goals**
   - Target frame rate? (for games)
   - Target response time?
   - Target throughput?
   - Memory budget?

5. **Constraints**
   - Must maintain compatibility?
   - Can algorithms be changed?
   - Can data structures be changed?

---

## Phase B: Agent Planning (Extended)

### Scaling Guidelines for Performance Review

| Scope | Recommended Configuration |
|-------|--------------------------|
| Targeted (specific slow area) | 4 agents: PP, AA, MEM, HP |
| Module-level | 5-6 agents: All recommended + Data Flow |
| System-wide | 6-8 agents: Add Architecture + Module Specialists |
| Game/Real-time | 6-8 agents: Focus on HP, add Module Specialists for critical loops |

### Critical Path Identification
Before launching agents, identify likely hot paths:
- Main loops (game loop, event loop)
- Frequently called functions
- User-facing response paths
- Data processing pipelines

---

## Phase C: Review Swarm Launch (Extended)

### Agent-Specific Instructions

#### Performance Profiler (Primary)
```markdown
# Performance Analysis Task

## Scope
{SCOPE_FROM_PHASE_A}

## Performance Concerns
{CONCERNS_FROM_PHASE_A}

## Primary Analysis Areas

### 1. Common Performance Anti-Patterns
Look for:
- Nested loops with high iteration counts
- Repeated calculations that could be cached
- String concatenation in loops
- Creating objects in loops unnecessarily
- Synchronous blocking in async code
- Busy waiting / spin loops
- Inefficient regex patterns
- Repeated file/network operations that could be batched

### 2. Database/Query Patterns (if applicable)
Look for:
- N+1 query patterns
- Missing indexes (by analyzing query patterns)
- Fetching more data than needed
- Unbounded queries
- Queries in loops

### 3. Caching Opportunities
Look for:
- Repeated expensive calculations
- Repeated external calls
- Data that could be memoized
- Missing caching where beneficial

### 4. Lazy vs Eager Loading
Look for:
- Unnecessary eager loading
- Repeated lazy loading (load once instead)
- Deferred computation opportunities

### 5. Concurrency Issues
Look for:
- Lock contention patterns
- Sequential operations that could parallelize
- Async operations done synchronously
- Thread pool exhaustion patterns

## Severity Ratings
- CRITICAL: Causes visible slowdown/hang in normal use
- HIGH: Significant impact on performance
- MEDIUM: Noticeable under load
- LOW: Minor inefficiency
- INFO: Optimization opportunity
```

#### Algorithm Analyst
```markdown
# Algorithm Efficiency Analysis

## Focus Areas

### 1. Time Complexity
For significant algorithms:
- What's the Big-O complexity?
- Is there a more efficient algorithm?
- What's the expected vs worst case?

### 2. Data Structure Choices
Look for:
- List used where Set/Dict would be faster
- Linear searches that could be O(1) lookups
- Inappropriate data structures for the use case
- Missing indexes for frequent lookups

### 3. Sorting and Searching
Look for:
- Inefficient sort algorithms
- Sorting repeatedly instead of maintaining order
- Linear search where binary search would work
- Custom implementations vs standard library

### 4. Algorithm Patterns
Look for:
- Brute force where dynamic programming helps
- Repeated subproblems not memoized
- Unnecessary recursion that could be iterative
- Graph traversal inefficiencies

### 5. Specific Patterns
For game/simulation code:
- Collision detection algorithms
- Pathfinding efficiency
- Spatial partitioning opportunities
- Update loop optimizations

## Report Format
For each finding:
- Current complexity
- Recommended complexity
- Specific code location
- Suggested improvement
```

#### Memory/Resource Analyst
```markdown
# Memory & Resource Analysis

## Focus Areas

### 1. Memory Leaks
Look for:
- Objects added to collections but never removed
- Event handlers not unsubscribed
- Resources not closed/disposed
- Circular references preventing garbage collection
- Growing caches without bounds

### 2. Memory Allocation Patterns
Look for:
- Allocations in hot loops
- Unnecessary object creation
- String operations creating many intermediates
- Large allocations that could be pooled/reused

### 3. Resource Management
Look for:
- Files not closed
- Connections not released
- Missing context managers / using statements
- Resource exhaustion possibilities

### 4. Memory Efficiency
Look for:
- Data structures with high overhead
- Storing more data than needed
- Duplicate data storage
- Compression opportunities

### 5. Object Lifecycle
Look for:
- Objects living longer than needed
- Premature optimization causing complexity
- Missing object pooling for frequent create/destroy

## Severity
- CRITICAL: Memory leak in common path
- HIGH: Significant memory waste
- MEDIUM: Inefficient but bounded
- LOW: Minor optimization
```

#### Hot Path Identifier
```markdown
# Hot Path Analysis

## Focus Areas

### 1. Identify Hot Paths
Find code that runs:
- Every frame (game loop)
- Every request (server)
- Every event (event handlers)
- Every iteration (loops)

### 2. Analyze Hot Path Content
For each hot path:
- What operations are performed?
- Are there avoidable allocations?
- Are there avoidable calculations?
- Can anything be moved outside the hot path?

### 3. Call Chain Analysis
- What does the hot path call?
- Are called functions optimized for frequent calling?
- Hidden expensive operations?

### 4. Optimization Opportunities
For each hot path:
- What can be cached?
- What can be precomputed?
- What can be lazily computed?
- What can be batched?

### 5. Frame Budget (for games)
If applicable:
- Estimate time spent in each hot path
- Identify budget-busters
- Prioritize optimization targets
```

---

## Phase D: Findings Compilation (Extended)

### Performance Report Structure

```markdown
# Performance Review Report

## Executive Summary
- **Performance Health:** [Good / Needs Attention / Problematic]
- **Critical Bottlenecks:** {N}
- **Optimization Opportunities:** {N}
- **Estimated Impact:** [description]

## Critical Performance Issues

### PERF-C01: {Title}
**Severity:** CRITICAL
**Location:** `file:lines`
**Issue Type:** {algorithm/memory/I-O/concurrency}
**Description:** {description}
**Current Performance:** {estimate if possible}
**Impact:** {when/how this affects users}
**Recommendation:** {specific fix}
**Expected Improvement:** {estimate}

## High Priority Optimizations
[Same format]

## Quick Wins
[Low-effort, high-impact optimizations]

## By Category

### Algorithm Inefficiencies
| ID | Location | Current | Recommended | Impact |
|----|----------|---------|-------------|--------|

### Memory Issues
...

### I/O Bottlenecks
...

### Hot Path Issues
...

## Hot Path Analysis
| Path | Frequency | Current Cost | Optimization Potential |
|------|-----------|--------------|------------------------|

## Recommendations
### Immediate (High Impact)
1. ...

### Short-term (Moderate Impact)
1. ...

### Long-term (Architecture)
1. ...

## Benchmarking Recommendations
[How to measure improvement]
```

---

## Phase E: User Summary (Extended)

### Presenting Performance Findings

1. **Lead with Impact**
   - What's causing the biggest slowdowns?
   - What will users notice?

2. **Prioritize by Effort/Impact**
   - Quick wins first
   - Then high-impact changes
   - Note complex optimizations

3. **Explain the "Why"**
   - Why is this slow?
   - Why will the fix help?

4. **Provide Specific Recommendations**
   - Don't just say "optimize this"
   - Explain the specific change

5. **Note Measurement Needs**
   - Recommend benchmarking
   - Suggest profiling approaches

---

## Special Considerations

### Don't Over-Optimize
- Focus on actual bottlenecks
- Premature optimization is problematic
- Recommend profiling to confirm

### Context Matters
- What's slow in a game loop is different from a batch job
- Consider frequency of execution
- Consider acceptable latency

### Trade-offs
- Performance vs readability
- Performance vs memory
- Document trade-offs clearly

### Game-Specific Concerns
- Frame time budgets
- Garbage collection pauses
- Asset loading strategies
- Update vs render separation

---

## Example Workflow

1. User runs "Performance Review" prompt
2. Coordinator asks scope questions
3. User: "The combat system feels sluggish during large battles, review game/simulation/combat/"
4. Review folder: `2026-01-23_performance_combat-system/`
5. Agents: Performance Profiler, Algorithm Analyst, Memory Analyst, Hot Path Identifier
6. Agents analyze combat code
7. Findings:
   - Critical: O(n²) collision detection with all units
   - High: Creating new damage calculation objects every frame
   - Medium: String formatting for damage numbers in hot path
8. Recommendations:
   - Implement spatial partitioning (quadtree)
   - Pool damage calculation objects
   - Cache formatted strings
9. User creates optimization project

---

## Termination

After presenting findings:
1. Discuss highest-impact items
2. Recommend profiling approach to validate
3. Offer options:
   - Create optimization project
   - Provide detailed implementation guidance
   - Identify benchmarking approach
4. Update `reviews_index.md`
