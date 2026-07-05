---
name: verifier-subagent
description: Check finished work with a fresh-context subagent instead of self-critique when using Claude Fable 5. Use when designing multi-agent harnesses, verifying long-run output, or any time self-review keeps missing its own mistakes -- the maker should not grade its own work.
---

# Verifier Subagent

Fable 5 dispatches and sustains parallel subagents dependably enough to make this practical at scale, and the pattern is worth defaulting to: a separate subagent with a clean context outperforms self-critique at catching defects, because it doesn't share the maker's assumptions or blind spots.

## The rule

The agent that produced the work does not grade it. Give the verifier the *specification* and the *output* -- never the maker's reasoning or narration about what it did. A verifier that reads "I fixed the race condition by adding a lock" will look for a lock; a verifier that only reads the diff will look for a race condition.

## When to delegate at all

Split out a subtask when it is independent of your current context, large enough to amortize the handoff, and specifiable in a few sentences plus file pointers. Don't delegate tightly coupled edits -- coordination cost exceeds the parallelism gain.

## Coordination

- Launch independent subagents in the same turn and keep working while they run; don't block on the slowest one.
- Intervene only on signal: a subagent visibly off track or missing context it has no way to discover itself.
- Prefer a long-lived subagent that carries context across related subtasks over respawning per subtask -- repeated context loading is the dominant hidden cost.

## Verifier cadence

For a long-running build, run verification at a defined interval (every N components, every X hours), not once at the end. A defect caught at component 3 is cheap; the same defect caught after component 40 depend on it is not.

## Handoff template

A subagent brief needs exactly: the goal (one sentence), inputs (paths or data), a checkable definition of done, constraints (what not to touch), and where to write results. If you can't fill in all five, the task isn't ready to delegate.
