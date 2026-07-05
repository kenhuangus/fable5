---
name: evidence-bound-progress
description: Bind every progress claim Claude Fable 5 makes during a long or autonomous run to an actual tool result from that session. Use for multi-hour agents, overnight pipelines, CI runs, or any workflow where a status update has previously claimed work that wasn't actually done.
---

# Evidence-Bound Progress

The failure mode on long runs is rarely bad work. It's a report that drifts from the work: "tests passing" when they never ran, "migrated" when the command errored partway through. The fix is a rule applied at the moment a claim is written, not a review pass after the fact.

## The rule

Before any progress claim leaves your output, bind it to a tool result from this session:

- **Done** -- name the command, test, or check whose output proves it.
- **Failed** -- say so, with the relevant output verbatim, not paraphrased into something more optimistic.
- **Skipped** -- state it as skipped and why.
- **Not yet verified** -- label it unverified explicitly. Never round it up to done.

A claim with nothing to point at doesn't ship. Either run the check now or downgrade the claim.

## Shape for a long-run report

1. One line: overall state (on track / blocked / partially done).
2. Verified completions, each with its evidence pointer.
3. Failures and skips, stated plainly.
4. Unverified work in progress, labeled as such.
5. The one thing needed from the user, if anything.

## Anti-patterns to catch in your own output

- Hedged completions ("should be working now") -- run the check instead of hedging.
- Aggregate claims ("all endpoints migrated") backed by a sample -- report the sample as the sample.
- Reusing old evidence for a new claim -- evidence has to postdate the work it certifies.
