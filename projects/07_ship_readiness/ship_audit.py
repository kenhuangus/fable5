"""Project 7: ship-readiness audit for an agent before production.

prep    -- cheap model bundles system prompt, tool definitions, and eval
           results into one packet.
plan/audit -- Fable 5 (xhigh) audits go/no-go: unhandled edge cases,
              injection surfaces, missing rate limits, logging gaps.
execute -- cheap model proposes a concrete fix for each finding.

Swap sample_agent/ for your own system_prompt.md, tools.json, and
eval_results.json.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from job_packet.packet import prep, plan_or_audit, execute  # noqa: E402


def main(agent_dir):
    agent_dir = Path(agent_dir)
    system_prompt = (agent_dir / "system_prompt.md").read_text(encoding="utf-8")
    tools = (agent_dir / "tools.json").read_text(encoding="utf-8")
    evals = (agent_dir / "eval_results.json").read_text(encoding="utf-8")

    packet = prep(
        "Summarize this agent's behavior contract in one page: what it's "
        "allowed to do unsupervised, what needs escalation, and what the "
        "eval failures reveal about where the contract already breaks.\n\n"
        f"System prompt:\n{system_prompt}\n\nTools:\n{tools}\n\n"
        f"Eval results:\n{evals}"
    )
    print("=== Behavior contract summary ===\n" + packet)

    audit, fallback = plan_or_audit(
        "Give a go/no-go readiness verdict for shipping this agent to "
        "real users. Cover unhandled edge cases, prompt-injection "
        "surfaces (what can a customer's message make this agent do "
        "that it shouldn't), missing rate limits, and logging gaps. Rank "
        "findings by severity.\n\n" + packet,
        effort="xhigh",
    )
    if fallback:
        print(f"[routed to Opus 4.8 fallback: category={fallback}]")
    print("\n=== Go/no-go audit ===\n" + audit)

    fixes = execute(
        "For each finding above, propose a concrete fix: a system-prompt "
        "change, a tool-parameter constraint, or a rate-limit value. Be "
        "specific enough to implement directly.\n\n" + audit
    )
    print("\n=== Proposed fixes ===\n" + fixes)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else
         str(Path(__file__).with_name("sample_agent")))
