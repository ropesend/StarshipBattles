# Scalene Profiling Pass Template

Use this template for notes in `Reviews/results/` or a project/ticket update.

## Question

What user-visible slowdown, test slowdown, or memory concern is being investigated?

## Scenario

- Command:
- Mode: `cpu` or `full`
- Profile output:
- Date:
- Hardware/runtime notes:

## Baseline

- User-visible symptom:
- Existing test or benchmark:
- Internal profiler records, if relevant:

## Findings

- Hotspot:
- Evidence:
- Interpretation: Python time, native time, system time, memory growth, or copy volume.
- Confidence:

## Decision

- Optimize now:
- Create ticket/project:
- No-op:

## Validation

- Failing or characterization test:
- Before profile:
- After profile:
- Relevant test commands:
