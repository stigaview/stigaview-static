import argparse
import datetime
import logging
import os
import pathlib
import sys
import tomllib

from tqdm.auto import tqdm

from stigaview_static import html_output, import_stig, json_output, models


def _prep_models():
    models.Stig.update_forward_refs()
    models.Control.update_forward_refs()
    logging.info("Preparing models")

def _log_level_type(value: str) -> int:
    try:
        level = logging.getLevelName(value.upper())
        # getLevelName returns the string if not found, so check if it's an integer
        if isinstance(level, int):
            return level
        raise argparse.ArgumentTypeError(f"Invalid log level: {value}")
    except AttributeError:
        raise argparse.ArgumentTypeError(f"Invalid log level: {value}")

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
    parser.add_argument(
        "-l", "--log-level", help="Log level", default="DEBUG", type=_log_level_type
    )
    return parser.parse_args()


def load_config(path: str) -> dict:
    logging.info("Loading global config")
    if not os.path.exists(path):
        logging.error(f"No such file: {path}")
        exit(3)
    os.environ.setdefault("STIGAVIEW_CONFIG", path)
    with open(path) as f:
        content = f.read()
        data = tomllib.loads(content)
        return data


def main():
    start_time = datetime.datetime.now(datetime.timezone.utc)
    args = _parse_args()
    logging.basicConfig(
        level=logging.getLevelName(args.log_level),
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )
    _prep_models()
    config = load_config(args.config)
    products, srg_dict = process_products(config, args.input)
    html_output.render_stig_index(products, args.out_dir)
    html_output.render_srg_index(srg_dict, args.out_dir)
    html_output.write_index(products, args.out_dir)
    html_output.write_products(products, args.out_dir)
    json_output.write_product_stig_map(products, args.out_dir)
    endtime = datetime.datetime.now(datetime.timezone.utc)
    logging.info(f"This script took {endtime-start_time}")


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
        srgs.update(file_srgs)
        pbar.update(1)
        srgs.update(srgs)
    return product, srgs


def _get_total_files(input_path, products):
    # Count total files to process
    total_files = 0
    for product in products:
        product_path = pathlib.Path(input_path) / product.short_name
        if product_path.exists():
            total_files += len(list(product_path.glob("v*.xml")))
    return total_files


def process_products(
    config: dict, input_path: str
) -> tuple[list[models.Product], dict[str, list]]:
    products = models.Product.get_products(config)
    result = list()
    srgs_dict = dict()
    total_files = _get_total_files(input_path, products)
    with tqdm(total=total_files, desc="Processing all STIG files", unit="file") as pbar:
        for product in products:
            product_path = pathlib.Path(input_path) / product.short_name
            if not product_path.exists():
                logging.error(
                    f"Unable to find path for {product.short_name} at {product_path}"
                )
                exit(4)
            product, srgs = process_product(product, product_path, pbar)
            for srg, controls in srgs.items():
                if srg not in srgs_dict.keys():
                    srgs_dict[srg] = controls
                else:
                    for control in controls:
                        srgs_dict[srg].append(control)
            result.append(product)
    return result, srgs_dict
