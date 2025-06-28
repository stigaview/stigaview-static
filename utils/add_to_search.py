import argparse
import json
import os
import pathlib
import sys
from typing import Generator, List

import meilisearch

SEARCH_HOST = os.environ.get("SEARCH_HOST", "https://search.stigaview.com")
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


def chunk_list(lst: List, chunk_size: int) -> Generator[List, None, None]:
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]  # noqa: E203


def main():
    if not SEARCH_HOST:
        print("Please set the environment variable SEARCH_MASTER_KEY", file=sys.stderr)
        sys.exit(1)
    if not MASTER_KEY:
        print("Please set the environment variable SEARCH_HOST", file=sys.stderr)
        sys.exit(1)
    args = _get_arg_parser().parse_args()
    json_output_path = pathlib.Path(args.json_output_path)
    if not json_output_path.exists():
        print(
            f"No such file or directory {json_output_path.absolute()}", file=sys.stderr
        )
        sys.exit(1)
    if not json_output_path.is_dir():
        print(
            f"Given path {json_output_path.absolute()} is not a directory",
            file=sys.stderr,
        )
        sys.exit(1)
    json_files = list(json_output_path.glob("*.json"))
    if len(json_files) == 0:
        print(f"No JSON files found in {json_output_path.absolute()}", file=sys.stderr)
        sys.exit(1)
    client = meilisearch.Client(SEARCH_HOST, MASTER_KEY)
    client.create_index("controls")
    index = client.get_index("controls")
    if not index:
        print("No index found", file=sys.stderr)
        sys.exit(1)
    docs = list()
    for file in json_files:
        docs.append(json.loads(file.read_text()))
    tasks = index.add_documents_in_batches(docs, primary_key="id")
    for task in tasks:
        client.wait_for_task(task.task_uid)


if __name__ == "__main__":
    main()
