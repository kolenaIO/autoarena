import argparse
from pathlib import Path

import uvicorn

from autoarena.seed import seed_head_to_heads


def parse_args(args: list[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser("autoarena")
    sp = ap.add_subparsers(dest="command")
    sp.default = "serve"

    serve_parser = sp.add_parser("serve", help="[Default] Serve the AutoArena app")
    serve_parser.add_argument("-d", "--dev", action="store_true", help="Run in development mode")

    seed_parser = sp.add_parser(
        "seed",
        help="Seed a project with head-to-heads stored in a CSV or Parquet file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""\
Seed a new project from a CSV or Parquet file where each row represents a head-to-head matchup between two models.

The following columns are required:

- `model_a`: name of model A in this head-to-head
- `model_b`: name of model B in this head-to-head
- `prompt`: the prompt that both models were run on
- `response_a`: the response from model A to the prompt
- `response_b`: the response from model B to the prompt
- `winner`: the winner of the head-to-head, either "A", "B", or "-" for ties""",
    )
    seed_parser.add_argument("head_to_heads", type=Path, help="Path to head-to-heads CSV or Parquet file")

    return ap.parse_args(args)


def main(args: list[str]) -> None:
    parsed_args = parse_args(args)
    if parsed_args.command == "seed":
        seed_head_to_heads(parsed_args.head_to_heads)
    if parsed_args.command == "serve":
        uvicorn.run(
            "autoarena.server:server",
            host="localhost",
            port=8899,
            reload=getattr(parsed_args, "dev", False),
            factory=True,
            timeout_graceful_shutdown=1,  # wait 1 second for tasks to complete before forcefully exiting
        )
