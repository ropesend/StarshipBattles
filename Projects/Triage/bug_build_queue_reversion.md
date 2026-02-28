# Build Queues Instant-Build Behavior Reversion

## Context
From QA Session Log: 20260228_104923
Timestamp: 10:55:08

## Description
The build queue operates on a legacy "1 turn" instant completion instead of the tick-based continuous production system. It also fails to deduct resources correctly during construction. 

*Note: This is a major issue; it was working correctly before and somehow has reverted to a legacy system. Explore the codebase, as the code to implement this correctly likely already exists and is just not being used.*

## Screenshots
- [![Screenshot](../../tools/qa_observer/session_data/20260228_104923/images/bug_capture_105509.png)](../../tools/qa_observer/session_data/20260228_104923/images/bug_capture_105509.png) - Shows build queue incorrectly displaying "1 Turn" and zero resource consumption for Colony Ships.
- [![Screenshot](../../tools/qa_observer/session_data/20260228_104923/images/bug_capture_105548.png)](../../tools/qa_observer/session_data/20260228_104923/images/bug_capture_105548.png) - Shows the same zero-consumption issue for a complex added to a different build yard.
- [![Screenshot](../../tools/qa_observer/session_data/20260228_104923/images/bug_capture_105609.png)](../../tools/qa_observer/session_data/20260228_104923/images/bug_capture_105609.png) - Shows items instantly built on the first turn instead of being constructed over time.
