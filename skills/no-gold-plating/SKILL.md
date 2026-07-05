---
name: no-gold-plating
description: Keep Claude Fable 5's diffs mapped one-to-one to the request -- no unrequested refactors, speculative abstractions, or defensive error handling for states that can't occur. Use in code review and any coding session where the diff comes back larger than the ask, especially at high or xhigh effort.
---

# No Gold-Plating

Higher effort makes Fable 5 more thorough, and thoroughness without a fence spills into the diff: a helper for a single call site, a config flag for a value that never changes, error handling for an input the caller can't produce. Each addition is more surface to review and more code to carry.

## Rules

- The diff should be traceable to the request in one step. A bug fix touches the bug, not the file around it.
- No abstraction for one caller. Inline it; extract it later if a second caller actually shows up.
- Don't design for a requirement that doesn't exist yet. Ship the simplest thing that is correct today.
- Validate at system boundaries -- user input, external APIs, file contents -- and trust your own internal invariants everywhere else.
- Prefer changing the code directly over adding a flag or a compatibility shim, unless the code is a published interface someone else depends on.

## Self-check before finalizing

1. Could a reviewer trace every hunk back to the request in one step?
2. Did I add anything "while I was here"?
3. Is every new error-handling branch actually reachable?

Any "no" means cut it, not comment it. If something adjacent genuinely deserves attention, name it once at the end and leave it undone.
