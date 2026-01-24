# PROTOCOL 03: Focused Question Review
**Role:** Code Review Coordinator
**Extends:** 00_review_core.md

**Purpose:** Answer a specific question the user has about the codebase. Deploy investigators to research the question and provide a direct, evidence-based answer.

---

## Overview

The Focused Question Review is different from other review types. Instead of scanning for general issues, it focuses on answering a specific question the user has. The output is a direct answer with supporting evidence, not a list of findings.

**Best For:**
- "Why does X happen?"
- "How does Y work?"
- "What would break if we changed Z?"
- "Where is feature F implemented?"
- "What's causing bug B?"

---

## Default Agent Configuration

### Primary Agent
| Agent | Focus |
|-------|-------|
| Question Investigator | Primary researcher - follows the question wherever it leads |

### Supporting Agents (Selected Based on Question Type)
| Question Type | Supporting Agents |
|---------------|-------------------|
| "Why does X crash/freeze/fail?" | Error Handling Auditor, Performance Profiler |
| "How is data validated/processed?" | Security Auditor, Data Flow Tracer |
| "What would break if we changed X?" | Architecture Reviewer, Dependency Mapper, Test Impact Analyst |
| "How does feature X work?" | Architecture Reviewer, Module Specialist |
| "Why is X slow?" | Performance Profiler, Algorithm Analyst |
| "Where is X implemented?" | Module Specialist (x2-3 for different areas) |

### Typical Agent Count: 3-6 (varies by question complexity)

---

## Phase A: Scope Definition (Extended)

### The Question is the Scope

Unlike other reviews, Phase A focuses on understanding the question:

1. **Capture the Question**
   - Get the specific question from user
   - Clarify any ambiguity

2. **Classify the Question Type**
   | Type | Characteristics |
   |------|-----------------|
   | Behavior | "Why does X happen?" |
   | Architecture | "How does X work?" |
   | Impact | "What breaks if we change X?" |
   | Location | "Where is X?" |
   | Cause | "What's causing X?" |

3. **Identify Known Context**
   - Any known relevant files/modules?
   - When does the issue occur?
   - Any reproduction steps?
   - Previous investigation attempts?

4. **Define Success Criteria**
   - What would a satisfactory answer look like?
   - Level of detail needed?
   - Need for code examples?

---

## Phase B: Agent Planning (Extended)

### Agent Selection by Question Type

#### "Why does X crash/freeze/fail?"
```
Primary: Question Investigator
Supporting:
- Error Handling Auditor (exception paths)
- Performance Profiler (if freeze/hang)
- Data Flow Tracer (if data corruption)
```

#### "How does X work?"
```
Primary: Question Investigator
Supporting:
- Architecture Reviewer (overall design)
- Module Specialist (specific module)
```

#### "What would break if we changed X?"
```
Primary: Question Investigator
Supporting:
- Architecture Reviewer (dependency analysis)
- Test Impact Analyst (test implications)
- Module Specialist (affected areas)
```

#### "Where is X implemented?"
```
Primary: Question Investigator
Supporting:
- Module Specialist (x2-3 for parallel search)
```

#### "What's causing bug X?"
```
Primary: Question Investigator
Supporting:
- Error Handling Auditor
- Data Flow Tracer
- Test Behavior Analyst (if test-related)
```

---

## Phase C: Review Swarm Launch (Extended)

### Agent-Specific Instructions

#### Question Investigator (Primary)
```markdown
# Your Question to Answer:
{THE_USER_QUESTION}

## Known Context:
{CONTEXT_FROM_PHASE_A}

## Your Task:
1. Investigate thoroughly to answer this question
2. Follow the evidence wherever it leads
3. Document your investigation path
4. Provide a clear, direct answer

## Your Report Structure:

### Answer Summary
[1-3 sentence direct answer to the question]

### Confidence Level
[High/Medium/Low] - [Why this confidence level]

### Evidence
For each piece of evidence:
- **Finding:** [What you found]
- **Location:** `file:lines`
- **Relevance:** [How this relates to the question]

### Investigation Path
1. [First step taken]
2. [What that revealed]
3. [Next step based on findings]
... (document your logical progression)

### Supporting Details
[Deeper explanation with code references]

### Remaining Uncertainties
[What you couldn't determine, if anything]

### Recommendations
[If applicable - how to address/fix/improve]
```

#### Supporting Agents
```markdown
# Research Task:
Support the investigation of: {THE_USER_QUESTION}

## Your Focus Area:
{AGENT_SPECIFIC_FOCUS}

## Your Task:
1. Investigate your specific focus area
2. Look for anything relevant to the main question
3. Report findings that help answer the question

## Report any:
- Direct evidence related to the question
- Indirect evidence that provides context
- Potential red herrings (things that look relevant but aren't)
- Areas that need deeper investigation
```

---

## Phase D: Findings Compilation (Extended)

### Different Compilation Approach

For Focused Question reviews, compilation focuses on synthesizing an answer:

1. **Read All Agent Reports**
   - Primary investigator's answer
   - Supporting evidence from other agents

2. **Synthesize Answer**
   - Combine evidence into coherent narrative
   - Resolve any contradictions between agents
   - Determine overall confidence level

3. **Structure the Response**
   ```markdown
   # Answer: {THE_QUESTION}

   ## Direct Answer
   [Clear, concise answer]

   ## Confidence: [High/Medium/Low]
   [Explanation of confidence level]

   ## Evidence Summary
   [Key evidence points with locations]

   ## Detailed Explanation
   [Full narrative with code references]

   ## Investigation Notes
   [How the answer was determined]

   ## Related Findings
   [Anything interesting discovered along the way]

   ## Recommendations
   [If applicable]
   ```

---

## Phase E: User Summary (Extended)

### Presenting the Answer

1. **Lead with the Answer**
   - State the direct answer first
   - Don't make user wade through investigation to find it

2. **Show Your Work**
   - Key evidence supporting the answer
   - Code references they can verify

3. **State Confidence Level**
   - High: Strong evidence, clear conclusion
   - Medium: Good evidence, some uncertainty
   - Low: Limited evidence, best guess

4. **Discuss Implications**
   - What this answer means for the user
   - Any actions recommended

5. **Handle Follow-ups**
   - User may have follow-up questions
   - May spawn additional investigation

---

## Special Considerations

### When the Answer is "It Depends"
- Enumerate the conditions
- Provide answer for each condition
- Help user determine which applies to them

### When the Answer is "Unknown"
- State what could be determined
- State what couldn't be determined and why
- Suggest how to find out (debugging, logging, etc.)

### When Investigation Reveals Other Issues
- Note them as "Related Findings"
- Don't let them derail the main question
- User can decide to investigate separately

### When Question is Too Broad
- Clarify with user before full investigation
- May need to narrow scope
- May need to split into multiple questions

---

## Example Workflows

### Example 1: Behavior Question
**Question:** "Why does the game sometimes freeze during combat?"

1. Coordinator classifies: Behavior question (crash/freeze)
2. Agents: Question Investigator, Performance Profiler, Error Handling Auditor
3. Investigation finds: Infinite loop in damage calculation when armor is negative
4. Answer: "The freeze occurs because `calculate_damage()` in `combat/damage.py:145` enters an infinite loop when target armor goes negative, which can happen with armor-piercing effects."
5. Confidence: High (reproducible, clear code evidence)

### Example 2: Impact Question
**Question:** "What would break if we removed the legacy event system?"

1. Coordinator classifies: Impact question
2. Agents: Question Investigator, Architecture Reviewer, Test Impact Analyst
3. Investigation maps all dependencies
4. Answer: "Removing the legacy event system would break 12 modules that still subscribe to events: [list]. Additionally, 34 tests rely on event mocking. Recommended migration path: [summary]"
5. Confidence: Medium (dependency analysis complete, but runtime behavior may vary)

---

## Termination

After presenting the answer:
1. Confirm user's question is answered
2. Offer to:
   - Investigate follow-up questions
   - Create project if fix is needed
   - Document findings for future reference
3. Update `reviews_index.md` with question and answer summary
