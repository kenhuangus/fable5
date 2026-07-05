"""Project 3: build a model-routing cost dashboard.

prep    -- plain Python aggregates a week of usage (model, task_type,
           tokens, outcome) -- no model call needed for arithmetic.
plan/audit -- Fable 5 (high) designs the routing policy: what belongs on
              Haiku vs Sonnet vs Fable, with cost projections.
execute -- cheap model builds a report that flags log rows violating the
           policy Fable just designed (the "one-sentence test" from part
           4, applied retroactively).

Swap sample_usage_log.csv for your own; columns must match.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from job_packet.packet import plan_or_audit, execute  # noqa: E402

PRICES = {  # $ per million tokens: (input, output)
    "claude-fable-5": (10, 50),
    "claude-sonnet-5": (2, 10),  # intro pricing through 2026-08-31
    "claude-haiku-4-5": (1, 5),
}


def summarize(rows):
    totals = {}
    for r in rows:
        m = r["model"]
        inp, out = int(r["input_tokens"]), int(r["output_tokens"])
        price_in, price_out = PRICES.get(m, (0, 0))
        cost = inp / 1e6 * price_in + out / 1e6 * price_out
        t = totals.setdefault(m, {"calls": 0, "tokens": 0, "cost": 0.0})
        t["calls"] += 1
        t["tokens"] += inp + out
        t["cost"] += cost
    return totals


def main(log_path):
    with open(log_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    totals = summarize(rows)
    summary_text = "\n".join(
        f"{m}: {t['calls']} calls, {t['tokens']} tokens, ${t['cost']:.2f}"
        for m, t in totals.items()
    )
    task_types = "\n".join(f"{r['model']}: {r['task_type']}" for r in rows)
    print("=== Week summary ===\n" + summary_text)

    policy, fallback = plan_or_audit(
        "Design a model-routing policy from this week of usage: which "
        "task types belong on Haiku, Sonnet, or Fable, and why. Use the "
        "one-sentence test -- a task with no branches or judgment call "
        "belongs on the cheapest model that can do it. Flag every task "
        "type below that looks mis-routed given this rule, with the "
        "cheaper model it should move to and the dollar difference.\n\n"
        f"Pricing ($/MTok in, out): {PRICES}\n\nWeek summary:\n{summary_text}"
        f"\n\nPer-call task types:\n{task_types}",
        effort="high",
    )
    if fallback:
        print(f"[routed to Opus 4.8 fallback: category={fallback}]")
    print("\n=== Routing policy ===\n" + policy)

    report = execute(
        "Write a short terminal-style report enforcing this routing "
        "policy: list each mis-routed task type from the policy above, "
        "the model it's on, the model it should be on, and the projected "
        "monthly savings if this week is typical (multiply by 4).\n\n"
        + policy
    )
    print("\n=== Enforcement report ===\n" + report)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else
         str(Path(__file__).with_name("sample_usage_log.csv")))
