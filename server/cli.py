import argparse
import json
import sys
from typing import Iterable, Optional

from slave_agent.engine import stream_task

def print_event(event: dict) -> None:
    stage = event.get("stage", "event")
    message = event.get("message", "")

    if stage == "start":
        print(f"[{stage}] {message}")
        print(f"output: {event.get('output_dir', '')}")
        return

    if stage == "planner":
        print(f"[{stage}] {message}")
        print(event.get("plan", ""))
        return

    if stage == "scaffolder":
        print(f"[{stage}] {message}")
        print(event.get("filetree", ""))
        return

    if stage == "writer":
        print(f"[{stage}] {message}")
        for path in event.get("files", []):
            print(f"- {path}")
        return

    if stage == "critic":
        print(f"[{stage}] {message}: {event.get('review', '')}")
        return

    if stage == "done":
        print(f"[{stage}] {message}")
        print(f"output: {event.get('output_dir', '')}")
        for path in event.get("files", []):
            print(f"- {path}")
        return

    print(json.dumps(event, indent=2))


def build_command(args: argparse.Namespace) -> int:
    task = " ".join(args.task).strip()

    if not task:
        print("Provide a task, for example: slave create a small command-line tool")
        return 1

    stack = args.stack or "auto"

    for event in stream_task(task, stack, output_root=args.output_root):
        print_event(event)

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="slave", description="Generate projects from the terminal.")
    parser.add_argument("task", nargs="*", help="Task description to build.")
    parser.add_argument("--stack", help="Optional programming language hint, such as python, javascript, go, or rust.")
    parser.add_argument("--output-root", default=".", help="Where generated files are written (project root by default).")
    parser.set_defaults(func=build_command)

    return parser


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = build_parser()

    raw = list(argv) if argv is not None else None
    if raw is None:
        raw = sys.argv[1:]

    args = parser.parse_args(raw)

    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
