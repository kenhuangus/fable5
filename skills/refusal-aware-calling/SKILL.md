---
name: refusal-aware-calling
description: Write and review Claude Fable 5 API calls and prompts so a safety-classifier refusal degrades gracefully instead of dead-ending. Use whenever adding a new claude-fable-5 call, reviewing security/red-team/bio/ML-adjacent workloads that are refusal-prone, or debugging a request that silently returned no content.
---

# Refusal-Aware Calling

A Fable 5 refusal is an HTTP 200 with `stop_reason: "refusal"` and empty content, not an error your existing error handling will notice. Code that only checks HTTP status will treat a declined request as a quiet success with nothing in it.

## The four documented categories

`stop_details.category` on a refusal is one of `cyber`, `bio`, `frontier_llm`, or `reasoning_extraction` (source: [Refusals and fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback)), or `null` when the refusal doesn't map to a named category -- that `null` is a normal, permanent value, not a placeholder. Benign work can trip any of the first three: legitimate security research reads as `cyber`, legitimate life-sciences work reads as `bio`, legitimate ML research reads as `frontier_llm`. `reasoning_extraction` fires on the prompt shape, not the topic -- asking the model to echo its internal reasoning as response text.

## Rules

- Every `claude-fable-5` call names a `fallbacks` model and sends the `server-side-fallback-2026-06-01` beta header. A call with neither dead-ends silently on refusal.
- Check `stop_reason` before reading `content`. Branch on `stop_reason == "refusal"` directly -- don't infer it from an empty `content` array, which can also happen for other reasons.
- Never ask the model to reproduce its reasoning as output text. Use adaptive thinking (`output_config.effort`) instead of "think step by step" or "explain your reasoning" framing -- both are documented `reasoning_extraction` triggers.
- Give sub-agent and tool-execution calls their own fallback wiring. `fallbacks` on the top-level request does not propagate into calls made from inside tool execution.
- Log refusals as their own signal, separate from error rates -- a refusal never shows up as a 5xx. See [`fable_scanner/monitor.py`](../../fable_scanner/monitor.py) in this repo for a working refusal-analytics aggregator.

## Before shipping a refusal-prone workload

For security tooling, red-team harnesses, or anything cyber/bio/ML-adjacent, run your actual prompts against the target model before committing a workflow to it -- a fallback-served response comes from a different, weaker-fallback model, and a harness that assumed only the requested model would ever answer can produce silently degraded output. `fable_scanner canary` in this repo is built for exactly this check.
