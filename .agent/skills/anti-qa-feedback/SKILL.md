---
name: anti-qa-feedback
description: Process a QA session interactively within the current agent session, using Socratic questioning to deeply understand each observation before continuing work
disable-model-invocation: true
argument-hint: [session_directory_name] (e.g., 20260314_074413, or omit for latest)
---

# QA Session Feedback

Process a QA Observer session log interactively within the current agent session. The goal is **deep understanding through Socratic questioning** — not ticket creation. This skill creates a feedback loop: the agent that did the work hears and engages with what the user observed, then continues with corrective action.

## Your Role

You are receiving **direct feedback related to the current session's work**. The user ran the game after your changes and recorded a QA session describing what they observed. This could be anything: unexpected behavior, things that look great, ideas for enhancements, design direction, new features to add, or simply how the system feels after the changes.

**Be genuinely curious.** Ask questions. Propose theories. Connect observations to your changes. Don't rush to act — first make sure you truly understand what the user experienced and what they want.

---

## Phase 1: Session Loading

### Step 1: Locate the Session

The session argument is: **$ARGUMENTS**

1. If the argument is empty or omitted:
   - List directories in `Tools/qa_observer/session_data/`
   - Sort by name (they are `YYYYMMDD_HHMMSS` format)
   - Select the most recent directory that contains a `QA_Session_Log.md`
   - Report which session was auto-selected
2. Otherwise:
   - Strip any path prefix; use just the directory name
   - Construct path: `Tools/qa_observer/session_data/<argument>/QA_Session_Log.md`
   - Verify the file exists. If not, list available sessions and **STOP**.

### Step 2: Read the Session Log

1. Read the full `QA_Session_Log.md` file.
2. Parse into a list of **observations**. An observation is a logical unit consisting of:
   - One or more timestamped spoken commentary blocks
   - Zero or more screenshot references that appear between or after the commentary
3. **Group by topic:**
   - Consecutive commentary about the same subject forms one observation.
   - A topic change starts a new observation.
4. **Cross-session merging:** Scan the ENTIRE log for observations that return to the same issue later in the session. Users often mention something, move on, then come back to it. Merge all mentions of the same issue into a single observation, preserving:
   - All timestamps from each mention
   - All spoken commentary in chronological order
   - All associated screenshots
   - Note which parts came from separate mentions (e.g., "First mentioned at 07:44, revisited at 07:52")

### Step 3: Present Overview

Present a brief numbered list of observations with one-line summaries:

> Here's what I see in this session:
> 1. [Summary of observation 1]
> 2. [Summary of observation 2]
> ...
> Let's go through them one at a time.

No formal confirmation step is needed. The user can interject to skip, reorder, or add context, but the default is sequential processing.

---

## Phase 2: Context Refresh (Optional)

Before diving into observations, **offer** to review recent git changes:

> "Would you like me to review the recent git diff to correlate these observations with specific code changes? Or do I have enough context from our session?"

- If the user accepts: run `git log --oneline -20` and `git diff HEAD~N` (where N covers the session's work) to load the changes into context.
- If the user declines or you already have sufficient session context: skip and proceed.

This phase is about making connections explicit — "I changed X in file Y, and observation 3 might be related."

---

## Phase 3: Socratic Engagement

Process each observation **ONE AT A TIME**, sequentially. For each observation:

### Step A: Present the Observation

Display to the user:
- The timestamp range (or multiple timestamp ranges if merged)
- The full spoken commentary text (cleaned of speech-to-text artifacts: filler words, false starts, missing punctuation)
- Any associated screenshots — **read the image files** so you can see exactly what the user saw
- A brief restatement: "It sounds like you're describing [X]. Is that right?"

**Log cross-referencing:** If `Tools/qa_observer/session_data/<session_id>/logs/` exists:
1. Read `word_timestamps.jsonl` from the session root to identify the precise time window for this observation. Each line is `{"time": <unix>, "ts": "HH:MM:SS", "word": "..."}`. Find the words corresponding to this observation's timestamps to narrow the window.
2. Search `logs/battle.log` (format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`) around that time window for errors, warnings, or relevant state changes.
3. Also check `logs/battle_log.txt` (combat events) and `logs/crash_log.txt` (crash tracebacks) if they exist.
4. Include pertinent log excerpts when presenting the observation.

### Step B: Investigate (Your Discretion)

If you need to look at code to understand the observation:
- Read relevant files directly or launch Explore agents
- This is **not mandatory** — you may already understand from session context
- **Always investigate** when the observation is unexpected or unclear to you

Present findings naturally: "I looked at [file:function] and here's what I see..."

### Step C: Socratic Questioning

Ask probing questions until you are **confident you fully understand** the observation. Types of questions to draw from:

- **Behavioral**: "Was the previous behavior X? What did you expect to see instead?"
- **Causal**: "Could this be related to the change I made in [file:function]?"
- **Scope**: "Is this the only place you noticed this, or does it affect other areas?"
- **Intent**: "Is the old behavior what you want restored, or is there a different target behavior?"
- **Priority**: "How important is this relative to the other observations?"
- **Design**: "What should this look like when it's working correctly?"
- **Edge cases**: "Does this happen every time, or only under certain conditions?"

Continue asking until satisfied. This could be 1 question or 5 — **you judge when you have enough understanding.** Don't move on while uncertain.

Use **AskUserQuestion** for questions where structured options help (e.g., "Which of these describes what you expected?"), but plain conversational questions are also fine for open-ended discussion.

### Step D: Summarize Understanding

Once you're satisfied:
1. State back your full understanding:
   - What the issue or observation is
   - Why it happened (if you can determine the cause)
   - What the desired behavior should be
2. Ask: "Have I got that right? Anything I'm missing?"
3. User confirms or corrects
4. If corrected, ask follow-up questions until understanding is confirmed
5. Move to the next observation

---

## Phase 4: Synthesis and Handoff

After all observations have been processed:

### Step 1: Cross-Cutting Analysis

Look across all observations for:
- **Patterns**: Multiple observations that share a root cause
- **Priorities**: Which observations are most critical to address
- **Dependencies**: Whether fixes need to happen in a particular order
- **Scope assessment**: Is this a quick fix, or does it suggest a deeper design issue?

Present this analysis to the user.

### Step 2: Save Memory Entries

Save key learnings as auto-memory entries — things that will be useful in future sessions:
- **Feedback-type memories**: If the user corrected your understanding of how something should work, or revealed a preference about system behavior
- **Project-type memories**: If you learned something non-obvious about ongoing work, goals, or constraints

Only save memories that would genuinely help in future conversations. Don't save things that are obvious from the code itself.

### Step 3: Propose Next Steps

Based on your understanding of all observations:
- Propose what needs to happen next: fixes, enhancements, design changes
- Suggest a priority order
- Ask: "Based on this feedback, here's what I think I need to do — shall I proceed?"

### Step 4: Natural Transition

The skill ends by flowing into the next task. There is no formal "skill complete" boundary. Once the user agrees on next steps, start working on them. The feedback session was the prelude to action.

---

## Constraints

- **SOCRATIC FIRST**: Always ask before assuming. The goal is understanding, not speed.
- **ONE AT A TIME**: Process observations sequentially — don't batch or rush.
- **SCREENSHOTS ARE EVIDENCE**: Always read and view screenshot image files. They show what the user actually saw.
- **NO TICKETS**: This skill does not create bug tickets, feature tickets, or triage items. If the user wants tickets, point them to `/anti-qa-triage`.
- **AGENT DISCRETION ON INVESTIGATION**: You decide when you need to look at code vs. when your existing context is sufficient.
- **MEMORY, NOT FILES**: Persist learnings as auto-memory entries, not report files or summaries.
- **CLEAN TEXT**: Speech-to-text output has no punctuation, contains filler words, repetition, and false starts. Clean it up into proper sentences when restating observations. Preserve the original meaning faithfully.
- **NATURAL HANDOFF**: Flow into continued work — don't end with a summary wall or a formal closing statement.
- **GENUINELY CURIOUS**: Engage openly with every observation — whether it's a bug, an enhancement idea, a design direction, or positive feedback. Propose theories, make connections, and explore the user's intent fully.
