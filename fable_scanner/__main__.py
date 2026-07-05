"""python -m fable_scanner <scan|canary|monitor> ..."""
import sys

from fable_scanner import scan, canary, monitor

COMMANDS = {"scan": scan.main, "canary": canary.main, "monitor": monitor.main}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("usage: python -m fable_scanner <scan|canary|monitor> ...")
        return 2
    return COMMANDS[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    sys.exit(main())
