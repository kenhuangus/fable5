---
name: effort-router
description: Pick and re-evaluate the output_config.effort level for a Claude Fable 5 workload. Use when designing a pipeline that mixes routine and hard tasks, when a call feels slow or expensive for what it's doing, or when porting an Opus 4.7/4.8 harness that defaulted to xhigh.
---

# Effort Router

Effort is the dial that trades intelligence for latency and cost on Fable 5. Two mistakes dominate: carrying over an old model's default effort unexamined, and picking one effort for an entire pipeline instead of per task class.

## Defaults, not habits

- `high` is the API default and the right starting point for most analysis, writing, and agentic/coding work.
- `medium` (or `low` when latency is visible to a user) for routine transforms: classification, short edits, formatting.
- `xhigh` only for the tasks that actually need it: large migrations, one-way-door changes, multi-day autonomous runs.
- `max` almost never — reserve it for problems where `xhigh` measurably fell short, not as a default upgrade.

If you're migrating a harness built for Opus 4.7 or 4.8, don't keep `xhigh` "because that's what coding needs" — that guidance was for the older model. Re-test at `high` first; Fable 5 at `high` frequently matches or beats an older model at `xhigh`.

## Route by task class

A triage step at `low`/`medium` that escalates only the cases that need it to `high`/`xhigh` beats any single fixed setting across a mixed workload — see [`job_packet/packet.py`](../../job_packet/packet.py) in this repo for a working example: `prep` and `execute` run cheap, `plan_or_audit` spends the premium effort only where judgment is dense.

## Self-check

Before shipping a pipeline's effort settings, ask: if I doubled every effort level, would output quality visibly improve? If not, you're overpaying somewhere.
