import collections
import json
import os
import pathlib
from typing import Dict

from stigaview_static import models


def write_product_stig_map(products: list[models.Product], out_dir: str):
    product_stig_map = collections.defaultdict(list)
    products_list: Dict[str, str] = dict()
    for product in products:
        products_list[product.short_name] = product.full_name
        for stig in sorted(product.stigs):
            product_stig_map[product.short_name].append(stig.short_version)

    with open(os.path.join(out_dir, "product-stig-map.json"), "w") as f:
        f.write(json.dumps(product_stig_map, indent=0))
    with open(os.path.join(out_dir, "products.json"), "w") as f:
        f.write(json.dumps(products_list, indent=0))


def render_json_control(control: models.Control, real_out_path: str):
    out_path = pathlib.Path(real_out_path).joinpath("..", "json_controls")
    if not out_path.exists():
        out_path.mkdir(parents=True)
    filename = out_path.joinpath(f"{control.search_primary_key}.json")
    filename.write_text(json.dumps(control.to_search_json(), indent=0))
