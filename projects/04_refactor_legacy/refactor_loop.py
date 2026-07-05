"""Project 4: refactor your oldest security automation, with checkpoints.

prep    -- cheap model documents current behavior from the source itself
           (not from memory of what it's supposed to do).
plan/audit -- Fable 5 (high): a refactor plan broken into checkpoints,
              ranked by risk, since this model tends to keep exploring
              long tasks until something else cuts it off (CodeRabbit's
              finding, part 4) -- checkpoints are the stop rule.
execute -- cheap model implements ONE checkpoint at a time.
verify  -- fresh-context grader checks each checkpoint's diff before the
           next one starts; a failed verify halts the loop.

Swap sample_target.py for your own file.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from job_packet.packet import prep, plan_or_audit, execute, verify  # noqa: E402


def main(target_path):
    source = Path(target_path).read_text(encoding="utf-8")

    doc = prep(
        "Document the current behavior of this module: what it does, "
        "what it silently fails on, and what a caller depends on that "
        "isn't obvious from the code alone.\n\n" + source
    )
    print("=== Current-behavior doc ===\n" + doc)

    plan, fallback = plan_or_audit(
        "Produce a refactor plan for this module as a numbered list of "
        "checkpoints, ordered from lowest to highest risk. Each "
        "checkpoint is one self-contained change with a one-line "
        "acceptance criterion a verifier could check against a diff. "
        "Flag the riskiest checkpoint explicitly.\n\n" + doc + "\n\n" + source,
        effort="high",
    )
    if fallback:
        print(f"[routed to Opus 4.8 fallback: category={fallback}]")
    print("\n=== Refactor plan ===\n" + plan)

    checkpoints = [ln for ln in plan.splitlines() if ln.strip().startswith(tuple("0123456789"))]
    for i, checkpoint in enumerate(checkpoints, 1):
        diff = execute(
            f"Implement checkpoint {i} against the current source. Output "
            f"only the changed function(s), not the whole file.\n\n"
            f"Checkpoint: {checkpoint}\n\nCurrent source:\n{source}"
        )
        passed, detail = verify(
            claim=f"This diff satisfies checkpoint {i}: {checkpoint}",
            evidence=diff,
        )
        print(f"\n=== Checkpoint {i}: {'PASS' if passed else 'FAIL'} ===\n{diff}")
        if not passed:
            print(f"[stop: verifier disagreed -- {detail}]")
            break


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else
         str(Path(__file__).with_name("sample_target.py")))
