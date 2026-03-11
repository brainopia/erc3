from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from .public_sdk import PublicERC3
from .runner import load_agent_callable, run_many, run_task_with_agent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="erc3-live")
    sub = parser.add_subparsers(dest="command", required=True)

    list_tasks = sub.add_parser("list-tasks")
    list_tasks.add_argument("--benchmark", default="erc3-prod")

    run_task = sub.add_parser("run-task")
    run_task.add_argument("--benchmark", default="erc3-prod")
    run_task.add_argument("--spec", required=True)
    run_task.add_argument("--agent", required=True)

    run_all = sub.add_parser("run-all")
    run_all.add_argument("--benchmark", default="erc3-prod")
    run_all.add_argument("--agent", required=True)
    run_all.add_argument("--spec", action="append", dest="spec_ids")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    core = PublicERC3()
    try:
        if args.command == "list-tasks":
            tasks = core.list_public_tasks(args.benchmark)
            print(json.dumps([asdict(task) for task in tasks], ensure_ascii=False, indent=2))
            return 0
        agent = load_agent_callable(args.agent)
        if args.command == "run-task":
            result = run_task_with_agent(core, args.benchmark, args.spec, agent)
            print(json.dumps(asdict(result), ensure_ascii=False, indent=2, default=str))
            return 0
        if args.command == "run-all":
            results = run_many(core, args.benchmark, agent, spec_ids=args.spec_ids)
            summary = core.aggregate_results(results)
            print(json.dumps({
                "results": [asdict(result) for result in results],
                "summary": asdict(summary),
            }, ensure_ascii=False, indent=2, default=str))
            return 0
        parser.error(f"Unknown command: {args.command}")
    finally:
        core.close()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
