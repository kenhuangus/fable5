# fable5 — Loop Engineering with Claude Fable 5

Working examples of loop engineering with Anthropic's Claude Fable 5: a deep
research agent and an agentic SOC triage loop, built on the loop anatomy of
trigger, rules, executor, fresh-context verifier, memory, and stop rules.

Companion repo to my Substack series:

- [Part 1 — Claude Fable 5: What Changed, and How to Stop Prompting It Like Opus](https://kenhuangus.substack.com/p/claude-fable-5-what-changed-and-how)
- [Part 2 — Loop Engineering, or How I Stopped Writing Prompts](https://kenhuangus.substack.com) (paid)
- [Part 3 — Memory Engineering](https://kenhuangus.substack.com) (paid)

## What's here

- `deep_research/` — a bounded research loop: decompose the question at
  `xhigh` effort, search each angle with the server-side web search tool,
  verify every claim with three fresh-context adversarial voters, synthesize
  only what survives.
- `agentic_soc/` — an alert triage loop: enrich and classify each alert,
  re-score it with a fresh-context verifier that sees only the artifacts,
  escalate or close, and distill lessons from verifier-confirmed verdicts only.
  Read-only by design; containment stays behind a human gate.
- `memory/` — memory engineering: a client-side handler for the official
  memory tool (`memory_20250818`) with traversal guards and size caps, and a
  startup scan that quarantines lessons that command instead of describe
  (the anti-poisoning gate).
- `templates/` — the loop instruction blocks and the memory scaffold, as
  paste-ready markdown.

## Quickstart

```
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python deep_research/research_loop.py "your research question"
python agentic_soc/triage_loop.py agentic_soc/sample_alerts.jsonl
```

## Fable 5 API notes baked into the code

1. Thinking is always on. The code never sends a `thinking` parameter; depth is
   controlled with `output_config.effort` (`low` for graders, `medium` for
   execution, `xhigh` for planning and synthesis).
2. Every request opts into the server-side Opus 4.8 fallback
   (`server-side-fallback-2026-06-01`), so a safety-classifier refusal on
   benign work (common on security tooling) reroutes instead of stalling the loop.
3. `stop_reason` is checked before content is read; `refusal` is handled as a
   loop event, not an exception.
4. The maker is never the grader: verifiers run in fresh context and receive
   artifacts only, never the worker's narration.

## License

MIT
