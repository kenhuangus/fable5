"""Project 9: migrate the legacy codebase you've been postponing.

prep    -- cheap model summarizes the source slice and the target
           architecture into one packet.
plan/audit -- Fable 5 (xhigh) sequences the migration file by file,
              since a wrong sequencing step (cut over a caller before its
              dependency) fails silently until an audit finds it months
              later.
execute -- cheap model migrates one file per step.
verify  -- fresh-context grader checks each file's diff against the
           target architecture before the next file starts.

Swap sample_legacy/ and target_architecture.md for your own migration.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from job_packet.packet import prep, plan_or_audit, execute, verify  # noqa: E402


def main(legacy_dir, target_path):
    legacy_dir = Path(legacy_dir)
    target = Path(target_path).read_text(encoding="utf-8")
    files = sorted(legacy_dir.glob("*.py"))
    sources = {f.name: f.read_text(encoding="utf-8") for f in files}
    listing = "\n\n".join(f"--- {n} ---\n{c}" for n, c in sources.items())

    packet = prep(
        "Summarize this codebase slice: what each file does and what "
        "depends on what.\n\n" + listing
    )
    print("=== Codebase summary ===\n" + packet)

    plan, fallback = plan_or_audit(
        "Sequence the migration to this target architecture as an "
        "ordered list of files, one per line, no downtime allowed (each "
        "file must work with either credential source until the fleet "
        "cuts over).\n\nTarget:\n" + target + "\n\nCodebase:\n" + packet,
        effort="xhigh",
    )
    if fallback:
        print(f"[routed to Opus 4.8 fallback: category={fallback}]")
    print("\n=== Migration sequence ===\n" + plan)

    for name in [n for n in sources if n in plan]:
        diff = execute(
            f"Migrate {name} to the target architecture. Support both "
            f"the static key and workload-token paths during rollout.\n\n"
            f"Target:\n{target}\n\nCurrent {name}:\n{sources[name]}"
        )
        passed, detail = verify(
            claim=f"{name} matches the target architecture and still "
                  "works during a mixed rollout.",
            evidence=diff,
        )
        print(f"\n=== {name}: {'PASS' if passed else 'FAIL'} ===\n{diff}")
        if not passed:
            print(f"[stop: verifier disagreed on {name} -- {detail}]")
            break


if __name__ == "__main__":
    base = Path(__file__).parent
    main(
        sys.argv[1] if len(sys.argv) > 1 else str(base / "sample_legacy"),
        sys.argv[2] if len(sys.argv) > 2 else str(base / "target_architecture.md"),
    )
