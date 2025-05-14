import argparse
import datetime
import os
import pathlib
import sys
import tomllib

from stigaview_static import html_output, import_stig, json_output, models


def _prep_models():
    models.Stig.update_forward_refs()
    models.Control.update_forward_refs()


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
    start_time = datetime.datetime.now(datetime.timezone.utc)
    _prep_models()
    args = parse_args()
    config = load_config(args.config)
    products, srg_dict = process_products(config, args.input)
    html_output.render_stig_index(products, args.out_dir)
    html_output.render_srg_index(srg_dict, args.out_dir)
    html_output.write_index(products, args.out_dir)
    html_output.write_products(products, args.out_dir)
    json_output.write_product_stig_map(products, args.out_dir)
    endtime = datetime.datetime.now(datetime.timezone.utc)
    print(f"This script took {endtime-start_time}")


def process_product(
    product: models.Product, product_path: str, config: dict
) -> tuple[models.Product, dict[str, list]]:
    product_path = pathlib.Path(product_path)
    product_config_path = product_path.joinpath("product.toml")
    with open(product_config_path, "r") as f:
        product_config = tomllib.loads(f.read())
    stig_files = product_path.glob("v*.xml")
    srgs = dict[str, list[models.Control]]
    for file in stig_files:
        if file.name.startswith("skip"):
            continue
        short_version = file.name.split(".")[0]
        if short_version not in product_config["stigs"]:
            raise ValueError(
                f"{product.full_name} doesn't have a config for {short_version}"
            )
        stig_release_date = product_config["stigs"][short_version]["release_date"]
        stig, srgs = import_stig.import_stig(file, stig_release_date, product)
        product.stigs.append(stig)
        srgs.update(srgs)
    return product, srgs


def process_products(
    config: dict, input_path: str
) -> tuple[list[models.Product], dict[str, list]]:
    products = models.Product.get_products(config)
    result = list()
    srgs_dict = dict()
    for product in products:
        product_path = os.path.join(input_path, product.short_name)
        if not os.path.exists(product_path):
            sys.stderr.write(
                f"Unable to find path for {product.short_name} at {product_path}\n"
            )
            exit(4)
        product, srgs = process_product(product, product_path, config)
        for srg, controls in srgs.items():
            if srg not in srgs_dict.keys():
                srgs_dict[srg] = controls
            else:
                for control in controls:
                    srgs_dict[srg].append(control)
        result.append(product)
    return result, srgs_dict
