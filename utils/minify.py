#!/usr/bin/env python3
import argparse
import glob
import pathlib

from csscompressor import compress
from rjsmin import jsmin


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output_path",
        help="Root of the output path",
        default="out",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    output_path = pathlib.Path(args.output_path)
    css_path = output_path.joinpath("static", "css")
    css_files = glob.glob(root_dir=css_path, pathname="*.css")
    for file in css_files:
        css_file = css_path.joinpath(file)
        minified = compress(css_file.read_text())
        css_file.write_text(minified)
    js_path = output_path.joinpath("static", "js")
    js_files = glob.glob(root_dir=js_path, pathname="*.js")
    for file in js_files:
        js_file = js_path.joinpath(file)
        minified = jsmin(js_file.read_text())
        js_file.write_text(minified)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
