# Template: the SOC alert triage loop

The instruction block behind `agentic_soc/triage_loop.py`, for driving a SOC
backend (e.g. a case-management CLI) from a scheduled agent.

```markdown
Goal: every new alert triaged within 10 minutes; verdict
(false positive / benign / escalate) with evidence attached.
Boundary: read-only on SIEM and TIP; no containment actions;
anything above medium confidence escalates to a human.
Each cycle: pull the next alert, enrich, classify, then a
fresh-context verifier re-scores it from the raw artifacts.
Memory: append per-alert-type lessons from closed cases only.
Stop: queue empty, OR 3 consecutive verifier disagreements
(pause the loop and page an analyst), OR cycle budget spent.
```

Two Fable 5 cautions. Wire up the Opus 4.8 server-side fallback, or a
classifier false positive on benign security work stalls the loop at 3am.
And treat alert payloads as attacker-authored input: no lesson gets written
to memory unless the fresh-context verifier confirmed the verdict first.
