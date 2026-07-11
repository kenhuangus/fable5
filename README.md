# fable5 - Loop Engineering with Claude Fable 5 and Mythos 5

Working examples of loop engineering with Anthropic's Claude Fable 5 and
Mythos 5: a deep research agent, an agentic SOC triage loop, and a Mythos scope
gate for approved defensive security work. The shared loop anatomy is trigger,
rules, executor, fresh-context verifier, memory, and stop rules.

Companion repo to my Substack series:

- [Part 1 — Claude Fable 5: What Changed, and How to Stop Prompting It Like Opus](https://kenhuangus.substack.com/p/claude-fable-5-what-changed-and-how)
- [Part 2 — Loop Engineering, or How I Stopped Writing Prompts](https://kenhuangus.substack.com) (paid)
- [Part 3 — Memory Engineering](https://kenhuangus.substack.com) (paid)
- [Part 4 — Ten Weekend Security Projects, or Plan Expensive, Build Cheap](https://kenhuangus.substack.com) (paid)
- [Part 5 — Auditing a Third-Party Fable 5 Tool, Then Building Our Own](https://kenhuangus.substack.com) (paid)
- [Part 6 — Ten Fable 5-Native Agent Skills](https://kenhuangus.substack.com) (paid)
- [Part 7 — Moving a Production Fleet Off Opus 4.8](https://kenhuangus.substack.com) (paid)
- [Part 8 — The Refusal Your Error Handler Can't See](https://kenhuangus.substack.com) (paid)
- [Part 9 — Don't Pay Twice for a Fallback](https://kenhuangus.substack.com) (paid)
- [Part 10 — The Effort Dial Is a Cost Dial](https://kenhuangus.substack.com) (paid)

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
- `job_packet/` — the shared library behind the ten weekend projects below:
  `prep` (cheap model), `plan_or_audit` (Fable 5, returns a fallback category
  when classifiers reroute the request), `execute` (cheap model), `verify`
  (fresh-context grader).
- `projects/` — ten weekend projects for security architects, agentic AI
  engineers, and CISOs, each following prep → plan/audit → execute → verify.
  Every project ships with generic sample data, so none of them need your
  actual codebase to run.
- `fable_scanner/` — a clean-room Fable 5 hygiene tool with three subcommands:
  `scan` (lint CLAUDE.md/skills/agent configs for the anti-patterns in
  Anthropic's own Fable 5 prompting guide), `canary` (regression canary —
  a fixed prompt set run periodically, alerting on refusal-rate or latency
  drift), and `monitor` (refusal-category and cost analytics from local
  Messages API response logs, no network calls). Independently designed and
  written; see Part 5 for why and how it was audited before anything from
  the third-party tool that inspired it was trusted.
- `skills/` — ten Fable 5-native Agent Skills (`SKILL.md` files, installable
  as a Claude Code plugin): effort routing, scope fencing, no gold-plating,
  evidence-bound progress, act-on-sufficiency, verifier subagents, autonomy
  contracts, lesson memory with an anti-poisoning gate, reader-first
  summaries, and refusal-aware API calling. Independently designed after
  auditing a third-party skills collection for Part 6.
- `migration/` — a linter that diffs an existing Opus 4.8 request body against
  Fable 5's requirements: it flags the sampling params (`temperature`, `top_p`,
  `top_k`) and manual thinking config that now return a 400, carried thinking
  blocks that bill as dead input tokens after a model switch, and a missing
  `fallbacks` parameter. Returns `(field, severity, message)` tuples so CI can
  fail a build on any error. Part 7.
- `refusal/` — the wire-level refusal handler: send with the server-side
  fallback wired, then a `read` function that branches on `stop_reason` (never
  on `content`, which is empty on a refusal) and reads `usage.iterations` to
  report whether Fable answered directly or a fallback caught a decline. Part 8.
- `fallback_credit/` — manual fallback-credit redemption for custom retry loops
  that lack the SDK middleware: redeem the one-time `fallback_credit_token` on
  an exact-body-match retry so a hand-rolled fallback isn't billed for two cache
  writes, plus a `served_by_sticky` check that separates a sticky-routed turn
  from a real fallback. Part 9.
- `effort/` — a router that maps each task's kind to one of the five effort
  levels (`low`/`medium`/`high`/`xhigh`/`max`), so routine work runs cheap and
  only capability-sensitive tasks pay for `xhigh`. Effort shapes all output
  tokens (prose, tool calls, and thinking), so it is the fleet's cost policy in
  one function. Part 10.
- `mythos_scope/` — a Fable/Mythos admission-control check. Fable workloads
  should have refusal/fallback telemetry; Mythos workloads require a Glasswing
  scope id, approved target set, private evidence store, independent
  validation, and a patch owner before any defensive cyber run proceeds.

  | # | Project | Fable's job |
  |---|---|---|
  | 01 | [Threat model your own agent stack](projects/01_threat_model) | full threat model: injection, tool poisoning, memory attacks, confused deputy |
  | 02 | [Audit your MCP server sprawl](projects/02_mcp_audit) | least-privilege violations, redundant connectors, exfil risk |
  | 03 | [Model-routing cost dashboard](projects/03_cost_dashboard) | design the Haiku/Sonnet/Fable routing policy |
  | 04 | [Refactor legacy security automation](projects/04_refactor_legacy) | risk-ranked refactor plan with checkpoints |
  | 05 | [Policy into enforcement code](projects/05_policy_to_code) | build the enforcement tool itself |
  | 06 | [Clone one GRC workflow](projects/06_grc_clone) | design the grounded-answer rubric |
  | 07 | [Ship-readiness audit](projects/07_ship_readiness) | go/no-go audit before production |
  | 08 | [Personal SOC dashboard](projects/08_soc_dashboard) | architect the unified, prioritized view |
  | 09 | [Migrate the legacy codebase](projects/09_migration) | sequence the no-downtime migration |
  | 10 | [Red-team-in-a-box](projects/10_redteam_box) | design the attack-scoring rubric |

## Quickstart

```
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python deep_research/research_loop.py "your research question"
python agentic_soc/triage_loop.py agentic_soc/sample_alerts.jsonl
python projects/01_threat_model/threat_model.py
python -m fable_scanner scan fable_scanner/examples
python -m fable_scanner monitor fable_scanner/examples/refusal_log.jsonl
python migration/migration_linter.py migration/sample_opus_request.json
python -m migration.test_migration_linter
python effort/effort_router.py
python mythos_scope/scope_gate.py mythos_scope/sample_mythos_scope.json
python -m mythos_scope.test_scope_gate
```

Every project script takes its sample data path(s) as optional CLI args, so
swapping in your own inventory/policy/codebase is a matter of pointing the
same script at different files, not editing the script.

## Fable 5 and Mythos 5 API notes baked into the code

1. Fable 5 and Mythos 5 share the same 1M context, 128k output ceiling,
   always-on adaptive thinking behavior, and $10/$50 pricing. Mythos is
   restricted to approved Project Glasswing use; Fable is the generally
   available safeguarded deployment.
2. Thinking is always on. The code never sends a `thinking` parameter; depth is
   controlled with `output_config.effort` (`low` for graders, `medium` for
   execution, `xhigh` for planning and synthesis).
3. Every Fable request opts into the server-side Opus 4.8 fallback
   (`server-side-fallback-2026-06-01`), so a safety-classifier refusal on
   benign work (common on security tooling) reroutes instead of stalling the loop.
4. `stop_reason` is checked before content is read; `refusal` is handled as a
   loop event, not an exception.
5. Mythos runs do not use Fable's classifier/refusal signal as the safety
   boundary. `mythos_scope/` validates authorization, target scope, artifact
   controls, and independent validation instead.
6. The maker is never the grader: verifiers run in fresh context and receive
   artifacts only, never the worker's narration.

## License

MIT
