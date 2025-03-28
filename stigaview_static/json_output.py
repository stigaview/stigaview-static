import collections
import json
import os
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
