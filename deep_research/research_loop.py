"""Deep research agent as a bounded loop on Claude Fable 5.

Loop anatomy:
  trigger  -> CLI invocation (or wire this into cron / a Routine)
  executor -> decompose (xhigh), then one web-search pass per angle
  verifier -> 3 fresh-context adversarial voters per claim; 2/3 refutes kill
  memory   -> claims.jsonl accumulates verdicts across runs
  stop     -> fixed angle cap + per-run token budget
"""
import json
import sys
from pathlib import Path

from anthropic import Anthropic

MODEL = "claude-fable-5"
BETAS = ["server-side-fallback-2026-06-01", "task-budgets-2026-03-13"]
FALLBACKS = [{"model": "claude-opus-4-8"}]
WEB_SEARCH = {"type": "web_search_20260209", "name": "web_search", "max_uses": 5}
MAX_ANGLES = 5
MEMORY = Path(__file__).with_name("claims.jsonl")

client = Anthropic()


def ask(prompt, effort, tools=None, budget=None):
    """One Fable 5 call. Returns text, or None on a refusal (loop event)."""
    output_config = {"effort": effort}
    if budget:
        output_config["task_budget"] = {"type": "tokens", "total": budget}
    with client.beta.messages.stream(
        model=MODEL,
        max_tokens=16000,
        output_config=output_config,
        betas=BETAS,
        fallbacks=FALLBACKS,
        tools=tools or [],
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        msg = stream.get_final_message()
    if msg.stop_reason == "refusal":
        return None
    return "".join(b.text for b in msg.content if b.type == "text")


def decompose(question):
    text = ask(
        f"Decompose this research question into at most {MAX_ANGLES} "
        f"complementary search angles. Return one angle per line, no "
        f"numbering, no commentary.\n\nQuestion: {question}",
        effort="xhigh",
    )
    return [a.strip() for a in (text or "").splitlines() if a.strip()][:MAX_ANGLES]


def search_angle(question, angle):
    text = ask(
        f"Research question: {question}\nAngle: {angle}\n\n"
        "Search the web for this angle. Return up to 5 falsifiable claims, "
        "one per line as JSON: {\"claim\": ..., \"source\": url}.",
        effort="medium",
        tools=[WEB_SEARCH],
        budget=30000,
    )
    claims = []
    for line in (text or "").splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                claims.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return claims


def verify(claim):
    """The maker is never the grader: 3 fresh-context voters, artifacts only."""
    votes = 0
    for voter in range(3):
        text = ask(
            f"You are adversarial claim verifier {voter + 1}/3. Try to REFUTE "
            f"this claim using web search. Answer with one word first, REFUTED "
            f"or SUPPORTED, then one sentence of evidence.\n\n"
            f"Claim: {claim['claim']}\nStated source: {claim['source']}",
            effort="low",
            tools=[WEB_SEARCH],
            budget=20000,
        )
        if text and text.strip().upper().startswith("REFUTED"):
            votes += 1
    return votes < 2  # 2/3 refutations kill the claim


def main():
    question = " ".join(sys.argv[1:]) or sys.exit("usage: research_loop.py <question>")
    survivors = []
    for angle in decompose(question):
        print(f"[angle] {angle}")
        for claim in search_angle(question, angle):
            ok = verify(claim)
            claim["verdict"] = "confirmed" if ok else "refuted"
            with MEMORY.open("a", encoding="utf-8") as f:
                f.write(json.dumps(claim) + "\n")
            print(f"  [{claim['verdict']}] {claim['claim'][:80]}")
            if ok:
                survivors.append(claim)

    report = ask(
        "Write a short cited research report answering the question below, "
        "using ONLY these verified claims.\n\nQuestion: " + question +
        "\n\nClaims:\n" + json.dumps(survivors, indent=2),
        effort="xhigh",
    )
    print("\n" + (report or "(synthesis refused; see claims.jsonl)"))


if __name__ == "__main__":
    main()
