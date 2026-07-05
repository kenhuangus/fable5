"""Runnable self-check: python -m fable_scanner.test_scanner"""
from pathlib import Path

from fable_scanner.rules import run_rules
from fable_scanner.monitor import analyze

EXAMPLES = Path(__file__).parent / "examples"


def test_bad_prompt_trips_multiple_categories():
    text = (EXAMPLES / "bad_prompt.md").read_text()
    findings = run_rules(text, "prompt")
    cats = {f["rule"]["category"] for f in findings}
    assert "reasoning-extraction" in cats, cats
    assert "overtriggering" in cats, cats
    assert "fable-specific" in cats, cats


def test_good_prompt_is_clean_of_errors():
    text = (EXAMPLES / "good_prompt.md").read_text()
    findings = run_rules(text, "prompt")
    errors = [f for f in findings if f["rule"]["severity"] == "error"]
    assert not errors, errors


def test_config_trips_temperature_and_thinking_rules():
    text = (EXAMPLES / "agent_config.json").read_text()
    findings = run_rules(text, "config")
    ids = {f["rule"]["id"] for f in findings}
    assert "FS-02" in ids, ids
    assert "FS-03" in ids, ids


def test_monitor_counts_refusals_and_fallback():
    lines = (EXAMPLES / "refusal_log.jsonl").read_text().splitlines()
    stats = analyze(lines)
    assert stats["total"] == 4
    assert stats["refused"] == 2
    assert stats["by_category"]["cyber"] == 1
    assert stats["by_category"]["reasoning_extraction"] == 1
    assert stats["fallback_served"] == 1


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok  {name}")
    print("all checks passed")
