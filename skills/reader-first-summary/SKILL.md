---
name: reader-first-summary
description: Make Claude Fable 5's final report readable to someone who saw none of the work. Use for long agentic sessions, overnight runs, and multi-tool tasks whenever summaries come back as arrow-chain shorthand, invented abbreviations, or references to reasoning the reader never saw.
---

# Reader-First Summary

A long run builds private vocabulary -- abbreviations, arrow chains, names for intermediate artifacts. Efficient while working, opaque in a report. The reader is seeing all of it for the first time, so the final message has to re-ground them, not continue the working thread.

## Rules for the final message

- Open with the outcome: one sentence answering "what happened" or "what did you find." Detail follows; it never leads.
- Full sentences. No arrow chains (`A -> B -> fails`), no hyphen-stacked compound labels, no abbreviation you coined mid-run. If a term you built up while working is worth keeping, reintroduce it as if new.
- Never point back at your own reasoning or working notes as if the reader saw them ("as established above" pointing at a tool transcript they never read).
- Give every identifier -- file, commit, flag, endpoint -- its own plain-language clause: what it is and why it matters here.
- Shorten by dropping details that wouldn't change the reader's next action, not by squeezing the grammar out of the sentences. Clear beats short when they conflict.
- Close with the one or two things you actually need from the reader, if any.

## Shape

1. Outcome, one sentence.
2. What was done or found, in reader-facing language.
3. Failures, skips, open questions -- stated plainly.
4. What's needed from you, if anything.

Shorthand between tool calls is fine; that's thinking out loud. This skill applies the moment you address the human.
