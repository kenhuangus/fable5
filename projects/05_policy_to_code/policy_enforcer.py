"""Project 5: turn one internal security policy into working enforcement code.

prep    -- cheap model converts the policy doc into a PRD with testable,
           numbered requirements.
plan/audit -- Fable 5 (high) builds the enforcement tool itself (a
              pre-commit-style checker script), since this is the
              judgment-dense part: knowing what a violation looks like.
verify  -- a fresh-context subagent grades the generated tool against the
           ORIGINAL requirements, not against Fable's own description of
           what it built.

Swap sample_policy.md for your own policy text.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from job_packet.packet import prep, plan_or_audit, verify  # noqa: E402


def main(policy_path):
    policy = Path(policy_path).read_text(encoding="utf-8")

    prd = prep(
        "Convert this policy into a PRD: one numbered, testable "
        "requirement per policy rule, phrased so a script could check "
        "each one automatically.\n\n" + policy
    )
    print("=== PRD ===\n" + prd)

    tool_code, fallback = plan_or_audit(
        "Write a single-file Python script that checks a directory of "
        "text/log files against these requirements and prints one "
        "violation per matching line, with file and line number. No "
        "external dependencies.\n\n" + prd,
        effort="high",
    )
    if fallback:
        print(f"[routed to Opus 4.8 fallback: category={fallback}]")
    print("\n=== Generated enforcement tool ===\n" + tool_code)

    passed, detail = verify(
        claim="This tool satisfies every numbered requirement in the PRD.",
        evidence=f"PRD:\n{prd}\n\nGenerated tool:\n{tool_code}",
    )
    print(f"\n=== Verifier: {'PASS' if passed else 'FAIL'} ===\n{detail}")
    if not passed:
        print("[do not merge until this is addressed]")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else
         str(Path(__file__).with_name("sample_policy.md")))
