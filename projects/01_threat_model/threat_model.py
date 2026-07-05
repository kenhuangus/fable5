"""Project 1: threat model your own agent stack.

prep    -- cheap model turns a raw agent-stack manifest into an architecture doc.
plan/audit -- Fable 5 (xhigh): injection paths, tool poisoning, memory
              persistence attacks, confused-deputy scenarios, ranked.
execute -- cheap model turns the ranked findings into a PR checklist.

Swap sample_agent_stack.json for your own manifest; the shape (agents,
tools, mcp_servers, credentials, data_flows, trust_boundaries) is all
Fable needs, not your actual codebase.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from job_packet.packet import prep, plan_or_audit, execute  # noqa: E402


def main(manifest_path):
    manifest = Path(manifest_path).read_text(encoding="utf-8")

    architecture_doc = prep(
        "Turn this raw agent-stack manifest into a one-page architecture "
        "doc: list every agent, its tools, MCP servers, credentials, and "
        "who talks to whom with what data.\n\n" + manifest
    )
    print("=== Architecture doc ===\n" + architecture_doc)

    audit, fallback = plan_or_audit(
        "Threat-model this agent stack. Cover: prompt injection paths "
        "(where untrusted content enters and what it can reach), tool "
        "poisoning (can one tool's output steer another agent), memory "
        "persistence attacks (does anything read back its own or another "
        "agent's saved state), and confused-deputy scenarios (does a "
        "low-trust agent inherit a high-trust agent's credentials). Output "
        "a ranked mitigation plan; flag anything that needs a human call.\n\n"
        + architecture_doc,
        effort="xhigh",
    )
    if fallback:
        print(f"[routed to Opus 4.8 fallback: category={fallback}]")
    print("\n=== Threat model + mitigation plan ===\n" + audit)

    pr_plan = execute(
        "Turn this ranked mitigation plan into a numbered PR checklist, "
        "one PR per finding, ordered by rank.\n\n" + audit
    )
    print("\n=== PR checklist ===\n" + pr_plan)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else
         str(Path(__file__).with_name("sample_agent_stack.json")))
