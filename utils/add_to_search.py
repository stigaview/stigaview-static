import argparse
import os
import pathlib
import sys

import meilisearch

SEARCH_HOST = "https://search.stigaview.com"
MASTER_KEY = os.environ.get("SEARCH_MASTER_KEY")


def _get_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json-output-path",
        required=True,
        type=str,
        help="Path to output JSON. Normally out/json",
    )
    return parser


def main():
    if not os.environ.get("SEARCH_MASTER_KEY"):
        print("Please set the environment variable SEARCH_MASTER_KEY", file=sys.stderr)
        sys.exit(1)
    if not os.environ.get("SEARCH_MASTER_KEY"):
        print("Please set the environment variable SEARCH_MASTER_KEY", file=sys.stderr)
        sys.exit(1)
    args = _get_arg_parser().parse_args()
    json_output_path = pathlib.Path(args.json_output_path)
    if not json_output_path.exists():
        print(
            f"No such file or directory {json_output_path.absolute()}", file=sys.stderr
        )
    client = meilisearch.Client(SEARCH_HOST, MASTER_KEY)
    index = client.get_index("controls")
    if not index:
        print("No index found", file=sys.stderr)
        sys.exit(1)
