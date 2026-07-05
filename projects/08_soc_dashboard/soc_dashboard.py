"""Project 8: build a personal security-operations dashboard.

prep    -- cheap model normalizes alerts, tickets, and on-call into one
           packet with metric definitions.
plan/audit -- Fable 5 (high) architects the unified view: what to
              prioritize and why, given all three sources at once.
execute -- cheap model renders Fable's spec as an actual terminal report.

Swap the three sample_*.json files for your own exports.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from job_packet.packet import prep, plan_or_audit, execute  # noqa: E402


def main(alerts_path, tickets_path, oncall_path):
    alerts = json.loads(Path(alerts_path).read_text(encoding="utf-8"))
    tickets = json.loads(Path(tickets_path).read_text(encoding="utf-8"))
    oncall = json.loads(Path(oncall_path).read_text(encoding="utf-8"))
    raw = json.dumps({"alerts": alerts, "tickets": tickets, "oncall": oncall}, indent=2)

    packet = prep(
        "Normalize this alerts/tickets/on-call data into one packet with "
        "clear metric definitions: open critical count, oldest unaddressed "
        "P1, and who owns the next 6 hours.\n\n" + raw
    )
    print("=== Normalized packet ===\n" + packet)

    spec, fallback = plan_or_audit(
        "Architect a single-pane dashboard view from this packet: what "
        "goes at the top (highest-priority action), what's secondary, "
        "and what's just for awareness. Justify the ordering.\n\n" + packet,
        effort="high",
    )
    if fallback:
        print(f"[routed to Opus 4.8 fallback: category={fallback}]")
    print("\n=== Dashboard spec ===\n" + spec)

    report = execute(
        "Render this dashboard spec as an actual terminal report using "
        "the raw data below: headers, one line per item, most urgent "
        "first.\n\n" + spec + "\n\nRaw data:\n" + raw
    )
    print("\n=== Dashboard ===\n" + report)


if __name__ == "__main__":
    base = Path(__file__).parent
    main(
        sys.argv[1] if len(sys.argv) > 1 else str(base / "sample_alerts.json"),
        sys.argv[2] if len(sys.argv) > 2 else str(base / "sample_tickets.json"),
        sys.argv[3] if len(sys.argv) > 3 else str(base / "sample_oncall.json"),
    )
