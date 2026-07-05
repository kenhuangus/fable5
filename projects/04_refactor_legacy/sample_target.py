"""Toy stand-in for "the crusty SIEM parser nobody dares touch": brittle
regex parsing, no tests, silent failure on malformed lines."""
import re

PATTERN = re.compile(r"^(\S+) (\S+) severity=(\d) user=(\S+) (.*)$")


def parse_line(line):
    m = PATTERN.match(line)
    if not m:
        return None  # silently drops malformed lines
    ts, host, sev, user, msg = m.groups()
    return {"ts": ts, "host": host, "severity": int(sev), "user": user, "msg": msg}


def parse_log(path):
    events = []
    for line in open(path, encoding="utf-8"):
        e = parse_line(line.rstrip("\n"))
        if e:
            events.append(e)
    return events
