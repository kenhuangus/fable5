"""Project 6: clone the one paid GRC workflow you keep using.

This one takes vendor-questionnaire auto-fill, the workflow security
teams pay a suite for at 20% utilization, and clones just that piece.

prep    -- cheap model normalizes the knowledge base into short facts
           keyed by topic.
plan/audit -- Fable 5 (high) designs the answer rubric: how to match a
              question to a KB fact and what a well-formed answer looks
              like, plus what to do when nothing matches.
execute -- cheap model drafts an answer per question, following the
           rubric, grounded only in the KB.
verify  -- fresh-context grader checks each answer doesn't claim
           anything the KB doesn't say (no hallucinated compliance
           claims in a document a customer will read).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from job_packet.packet import prep, plan_or_audit, execute, verify  # noqa: E402


def main(kb_path, questionnaire_path):
    kb = Path(kb_path).read_text(encoding="utf-8")
    questions = json.loads(Path(questionnaire_path).read_text(encoding="utf-8"))

    normalized = prep(
        "List each knowledge-base fact as 'topic: fact', one per line, "
        "nothing added.\n\n" + kb
    )

    rubric, fallback = plan_or_audit(
        "Design a rubric for answering a security questionnaire from "
        "this knowledge base: how to pick the matching fact, how to "
        "phrase a grounded answer, and what to write when no fact "
        "matches (never invent one).\n\n" + normalized,
        effort="high",
    )
    if fallback:
        print(f"[routed to Opus 4.8 fallback: category={fallback}]")
    print("=== Answer rubric ===\n" + rubric)

    for q in questions:
        answer = execute(
            f"Answer this questionnaire question using only the "
            f"knowledge base, following the rubric.\n\nRubric: {rubric}\n\n"
            f"Knowledge base:\n{normalized}\n\nQuestion: {q}"
        )
        passed, detail = verify(
            claim=f"This answer to '{q}' states nothing beyond the "
                  "knowledge base.",
            evidence=f"Knowledge base:\n{normalized}\n\nAnswer:\n{answer}",
        )
        flag = "OK" if passed else "UNGROUNDED CLAIM"
        print(f"\nQ: {q}\nA: {answer}\n[{flag}] {detail if not passed else ''}")


if __name__ == "__main__":
    base = Path(__file__).parent
    main(
        sys.argv[1] if len(sys.argv) > 1 else str(base / "sample_knowledge_base.json"),
        sys.argv[2] if len(sys.argv) > 2 else str(base / "sample_questionnaire.json"),
    )
