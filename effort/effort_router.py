"""Part 10: route each task to an effort level instead of a fleet-wide default.

effort is set as output_config.effort (nested, no beta header) and takes one
of five values: low, medium, high, xhigh, max. high is the default and is
identical to omitting the field. Effort shapes ALL response tokens -- text,
tool-call arguments, and thinking -- so a lower level also means fewer tool
calls, not just shorter prose. It is a behavioral signal, not a hard cap.

    python effort/effort_router.py
"""
import sys

from anthropic import Anthropic

FABLE = "claude-fable-5"
BETA = "server-side-fallback-2026-06-01"
FALLBACKS = [{"model": "claude-opus-4-8"}]
LEVELS = ("low", "medium", "high", "xhigh", "max")

client = Anthropic()


def effort_for(task):
    """One place to encode the fleet's cost policy. Routine work runs cheap;
    only the capability-sensitive tasks pay for xhigh."""
    kind = task.get("kind")
    if kind in ("classify", "extract", "format"):
        return "low"
    if kind in ("summarize", "chat", "route"):
        return "medium"
    if kind in ("migrate", "audit", "novel-research"):
        return "xhigh"
    return "high"  # the default for everything else


def run(task):
    effort = effort_for(task)
    msg = client.beta.messages.create(
        model=FABLE,
        max_tokens=task.get("max_tokens", 2048),
        output_config={"effort": effort},
        betas=[BETA],
        fallbacks=FALLBACKS,
        messages=[{"role": "user", "content": task["prompt"]}],
    )
    out = msg.usage.output_tokens
    return {"kind": task.get("kind"), "effort": effort, "output_tokens": out}


def main():
    fleet = [
        {"kind": "classify", "prompt": "Is this ticket a bug or a feature? 'App crashes on save.'"},
        {"kind": "summarize", "prompt": "Summarize: the deploy failed on a missing env var."},
        {"kind": "audit", "prompt": "Threat-model an agent that can read tickets and deploy."},
    ]
    for task in fleet:
        r = run(task)
        print(f"  {r['kind']:<10} effort={r['effort']:<6} out={r['output_tokens']} tok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
