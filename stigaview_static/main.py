import argparse
import datetime
import os
import sys
import pathlib
import tomllib

from stigaview_static import import_stig
from stigaview_static import models
from stigaview_static import html_output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create the STIG A View site from STIG XML"
    )
    parser.add_argument(
        "-o",
        "--out-dir",
        help="Directory to place the output. Defaults to out/",
        default="out",
    )
    parser.add_argument("input", help="Input folder. See README.md for more details")
    parser.add_argument(
        "-c",
        "--config",
        help="Path to config file, defaults to stigaview.toml",
        default="stigaview.toml",
    )
    return parser.parse_args()


def load_config(path: str) -> dict:
    if not os.path.exists(path):
        sys.stderr.write(f"Config file not found: {path}\n")
        exit(3)
    with open(path) as f:
        content = f.read()
        data = tomllib.loads(content)
        return data


def main():
    args = parse_args()
    config = load_config(args.config)
    products = process_products(config, args.input)
    html_output.write_products(products, args.out_dir)


def process_product(product: models.Product, product_path: str, config: dict) -> models.Product:
    product_path = pathlib.Path(product_path)
    stig_files = product_path.glob("*.xml")
    for file in stig_files:
        date = datetime.date(2023, 1, 1)
        stig = import_stig.import_stig(file, date)
        product.stigs.append(stig)
    return product


def process_products(config: dict, input_path: str) -> list[models.Product]:
    products = models.Product.get_products(config)
    for product in products:
        product_path = os.path.join(input_path, product.short_name)
        if not os.path.exists(product_path):
            sys.stderr.write(f"Unable to find path for {product} at {product_path}\n")
            exit(4)
        product = process_product(product, product_path, config)
    return products
