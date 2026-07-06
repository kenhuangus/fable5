"""Part 8: the refusal protocol underneath a fallback-aware call.

A Fable 5 refusal is a normal HTTP 200 with stop_reason == "refusal" and an
empty content array, not an exception. This module shows the wire-level
handling: send with server-side fallback wired, then read the response
correctly whether Fable answered, a fallback answered, or every model refused.

    python refusal/refusal_stack.py "your prompt here"
"""
import sys

from anthropic import Anthropic

FABLE = "claude-fable-5"
BETA = "server-side-fallback-2026-06-01"
FALLBACKS = [{"model": "claude-opus-4-8"}]
CATEGORIES = ("cyber", "bio", "frontier_llm", "reasoning_extraction")

client = Anthropic()


def call(prompt, effort="high"):
    return client.beta.messages.create(
        model=FABLE,
        max_tokens=2048,
        output_config={"effort": effort},
        betas=[BETA],
        fallbacks=FALLBACKS,
        messages=[{"role": "user", "content": prompt}],
    )


def read(msg):
    """Return (text, provenance). Branch on stop_reason, never on content."""
    # usage.iterations records every attempt; a fallback_message entry means
    # a fallback model produced the returned turn.
    iterations = msg.usage.iterations or []
    served_by_fallback = any(it.type == "fallback_message" for it in iterations)

    if msg.stop_reason == "refusal":
        # Every model in the chain declined. content is empty; do not read it.
        category = getattr(msg.stop_details, "category", None)
        return None, f"refused (category={category})"

    text = "".join(b.text for b in msg.content if b.type == "text")
    who = msg.model if served_by_fallback else f"{FABLE} (direct)"
    return text, who


def main(prompt):
    text, provenance = read(call(prompt))
    print(f"served by: {provenance}")
    if text is None:
        print("no fallback in the chain accepted this request")
        return 1
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "Write a haiku about caches."))
