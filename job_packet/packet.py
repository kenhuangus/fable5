"""The reusable job-packet loop behind all ten weekend projects.

prep    -- cheap model turns raw input into a job packet Fable can reason
           over without you re-explaining your stack every time.
plan_or_audit -- Fable 5 spends its premium on the judgment-dense middle:
           threat models, audits, refactor plans, migration sequencing.
execute -- cheap model implements against a plan it didn't have to invent.
verify  -- fresh-context grader checks the diff against the plan, never
           against the executor's account of what it did.

See fable5-substack part 4 for the write-up. Every plan_or_audit call can
get rerouted to Opus 4.8 by Fable's safety classifiers (cyber, bio,
frontier_llm, reasoning_extraction) -- check the returned category before
assuming Fable itself saw the prompt.
"""
from anthropic import Anthropic

FABLE = "claude-fable-5"
CHEAP = "claude-sonnet-5"
BETAS = ["server-side-fallback-2026-06-01"]
FALLBACKS = [{"model": "claude-opus-4-8"}]

client = Anthropic()


def _ask(model, prompt, effort, max_tokens=8000):
    msg = client.beta.messages.create(
        model=model,
        max_tokens=max_tokens,
        output_config={"effort": effort},
        betas=BETAS,
        fallbacks=FALLBACKS if model == FABLE else [],
        messages=[{"role": "user", "content": prompt}],
    )
    if msg.stop_reason == "refusal":
        category = getattr(msg.stop_details, "category", None)
        return None, category
    return "".join(b.text for b in msg.content if b.type == "text"), None


def prep(prompt, effort="medium"):
    text, _ = _ask(CHEAP, prompt, effort)
    return text


def plan_or_audit(prompt, effort="high"):
    """Returns (text, fallback_category). category is None unless Fable's
    classifiers rerouted the request to Opus 4.8 -- test this on your real
    prompts before budgeting a weekend around Fable-specific behavior."""
    return _ask(FABLE, prompt, effort)


def execute(prompt, effort="medium"):
    text, _ = _ask(CHEAP, prompt, effort)
    return text


def verify(claim, evidence, effort="low"):
    """Fresh-context grader: sees the claim and the evidence only, never
    the executor's narration. Returns (passed, detail)."""
    prompt = (
        "You are an independent verifier. You see only the claim and the "
        "evidence below, not how either was produced. Does the evidence "
        "support the claim? Answer PASS or FAIL on the first line, then "
        f"one sentence.\n\nClaim: {claim}\n\nEvidence:\n{evidence}"
    )
    text, category = _ask(FABLE, prompt, effort)
    if text is None:
        return False, f"verifier refused (category={category})"
    return text.strip().upper().startswith("PASS"), text
