1) there are at least 3 different paths leading to starshipbattles in use and there may be more
2) maintaining an exact count of the total number of tests seems like something that should be automated the sharded run could write to a file
3) is there a good reason not to track this: `.claude/settings.local.json` should not be tracked. - There is only one user (me) and no one else develops this program at the moment
4) counts of skills should be an automatable thing as well
5) I would like for All SKILLS to be given a prefix specific to the agent/system they are designed for:
    - claude - for claude
    - anti - for antigravity
    - deep - for opencode/deepseek-
    - codex - for codex
    I want this because when I am implementing a skill, I know what agent I'm using, and this makes it harder to pass the wrong one if it sees another.
6) Antigravity seems to be the agent that conforms least to the infrastructure around it, if we can find out more that would be good.  It is mostly used for tooling development.  The workhorse agents will be Claude, Codex and DeepSeek, antigravity is still unfortunatly the least reliable with large code bases - it mostly is used for tools and asset generation.
7) .agent workflows are stale, claude has been the dominant agent until recently.  While some if it's skills/information may also be stale it is probably the most current and up to date.
8) We can discuss deletion of existing obsolete workflows, one of the ideas that I have (I know it can be done with claude skills but I don't know about any others) is to have some sort of counter associated with each skill so it tracks how often the skill is used.  Unused skills could be purged and removed.
9) Some agents are better a different tasks, for example codex has the best image model now, antigravity is second, claude and deepseek have no image gen capability.  I never max out my codex, or antigravity plans, but claude does ocasionally get maxed out.  Deep seek is tokens but very cheap
10) I have not used any of the claude loop systems in a while
11) Most of you have 1M token context windows (not codex), one of the issues with that is that you get a little forgetful when you are getting into the upper half of your context window.  For that readon some things are deliberatly in multiple places, things like TDD, importance of documentation, etc... taking up 1k of tokens to say things a extra time or two to make sure it is remembered is a worthwile tradoff.
