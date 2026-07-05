# Template: the nightly verifier loop

Hand this to a scheduled agent (`/schedule` Routine, platform deployment, or
`/loop` while you watch the first cycles live).

```markdown
Goal: [checkable end state, e.g. "ruff clean and pytest green
on branch nightly-fixes, PR opened when done"].
Boundary: work only on branch nightly-fixes; never push to main;
never touch files outside [paths].
Each cycle, do one bounded unit, then spawn a fresh-context
verifier to audit your claims against pytest/ruff output.
Memory: read memory/INDEX.md first; append lessons after.
Stop: success condition above, OR same failure 3 times
(open an issue with state), OR cycle budget spent.
```

The goal is checkable, the boundary is a blast radius, and every stop is
explicit. On Fable 5 that's enough; the model fills in the how, and the
verifier keeps the filling honest.
