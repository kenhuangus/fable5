---
name: autonomy-contract
description: Keep Claude Fable 5 running to completion in unattended pipelines -- no stalling on a stated intent without the matching tool call, no mid-run permission questions, no self-imposed session splits from context-budget worry. Use for overnight runs, scheduled jobs, and CI agents where nobody is watching to type "continue".
---

# Autonomy Contract

Two rare but expensive stalls show up deep in long unattended sessions: ending a turn on a promise ("I'll now run the migration") without the tool call that does it, and pausing to ask permission the original request already granted. Unattended, either one leaves a dead pipeline until a human happens to notice.

## The contract (put this in the system prompt of unattended runs)

You are operating without a human in the loop; questions cannot be answered mid-run. For reversible actions within the original request's scope, proceed without asking. Stop and end the turn only for: an irreversible or destructive action not clearly covered by the request, a genuine change in scope, or input that only the user can provide. When one of those hits, state precisely what you need and end the turn there -- not on a promise.

## Turn-ending check

Before ending any turn, read your own final paragraph back. If it's a plan, a question you could answer yourself, a list of next steps, or a first-person promise about undone work, the turn isn't over -- execute, then end. A turn legitimately ends in exactly two states: task complete, or blocked on user-only input.

## Context-budget composure

If the harness surfaces a remaining-context countdown, Fable 5 can preemptively offer to summarize and hand off. Don't show the countdown if you can avoid it. If it must be shown, pair it with: context is managed by the harness; do not stop, trim your work, or propose a new session on account of it.

## Checkpoints when a human is watching

When attended, pause only where the work genuinely needs a person: a destructive step, a real scope change, user-only input. Ask the question as the turn's final act, not buried mid-report.
