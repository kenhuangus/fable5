"""Project 2: audit your MCP server sprawl.

prep    -- cheap model formats the raw connector list into a scored table.
plan/audit -- Fable 5 (high): least-privilege violations, redundant
              connectors, exfiltration risk, treating OAuth scopes as too
              coarse for tool-level permissioning.
execute -- cheap model turns findings into a consolidation plan + a
           routing policy readers can enforce.

Swap sample_mcp_servers.json for `claude mcp list --json` (or your
client's equivalent) output; only name/scopes/auth/last_used matter.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from job_packet.packet import prep, plan_or_audit, execute  # noqa: E402


def main(servers_path):
    servers = Path(servers_path).read_text(encoding="utf-8")

    scored = prep(
        "Format this MCP server list as a table: name, scopes, auth "
        "method, days since last use, and a naive risk score (high scope "
        "+ weak auth + stale use = higher risk).\n\n" + servers
    )
    print("=== Connector inventory ===\n" + scored)

    audit, fallback = plan_or_audit(
        "Audit these MCP connectors for least-privilege violations "
        "(scopes broader than any observed use), redundant connectors "
        "(overlapping capability), and exfiltration risk (broad scope on "
        "a stale or unauthenticated connector is the worst combination). "
        "Remember OAuth scopes describe an area of functionality, not "
        "which specific tool on which resource -- call out connectors "
        "that need per-tool policy, not just a scope trim. Output a "
        "ranked consolidation plan.\n\n" + scored,
        effort="high",
    )
    if fallback:
        print(f"[routed to Opus 4.8 fallback: category={fallback}]")
    print("\n=== Audit + consolidation plan ===\n" + audit)

    policy = execute(
        "Turn this consolidation plan into a routing policy document: "
        "which connectors to revoke now, which to scope down and how, "
        "and a review cadence for the rest.\n\n" + audit
    )
    print("\n=== Routing policy ===\n" + policy)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else
         str(Path(__file__).with_name("sample_mcp_servers.json")))
