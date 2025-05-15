import multiprocessing
import os.path
import shutil

import minify_html
from jinja2 import Environment, FileSystemLoader
from tqdm import tqdm

from stigaview_static import models
from stigaview_static.utils import get_config, get_git_revision_short_hash


def render_template(template: str, out_path: str, **kwargs):
    file_loader = FileSystemLoader("templates")
    env = Environment(loader=file_loader)
    template = env.get_template(template)
    config = get_config()
    context = kwargs | config
    output = template.render(git_sha=get_git_revision_short_hash(), **context)
    minified = minify_html.minify(output)
    with open(out_path, "w") as fp:
        fp.write(minified)


def render_product(product: models.Product, out_path: str):
    out_product = os.path.join(out_path, product.short_name)
    render_product_index(out_path, product)
    for stig in product.stigs:
        real_out_path = render_stig_detail(out_product, product, stig)
        for control in stig.controls:
            render_control(control, real_out_path)
    _copy_latest_stig(out_product, product)


def render_stig_detail(out_product, product, stig):
    real_out_path = os.path.join(out_product, stig.short_version.lower())
    real_out = os.path.join(real_out_path, "index.html")
    os.makedirs(real_out_path, exist_ok=True)
    render_template("stig.html", real_out, product=product, stig=stig)
    one_page_out = os.path.join(real_out_path, "onepage")
    stig.controls = sorted(stig.controls)
    render_onepage_stig_detail(one_page_out, product, stig)
    return real_out_path


def render_onepage_stig_detail(out_product, product, stig):
    real_out = os.path.join(out_product, "index.html")
    os.makedirs(out_product, exist_ok=True)
    render_template("one_page_stig.html", real_out, product=product, stig=stig)
    return out_product


def render_control(control, real_out_path):
    control_out_path = os.path.join(real_out_path, control.disa_stig_id)
    os.makedirs(control_out_path, exist_ok=True)
    control_out = os.path.join(control_out_path, "index.html")
    render_template("control.html", control_out, control=control)


def render_product_index(out_path, product):
    real_out = os.path.join(out_path, product.short_name)
    full_out_path = os.path.join(real_out, "index.html")
    os.makedirs(real_out, exist_ok=True)
    product.stigs = sorted(product.stigs)
    render_template("product.html", full_out_path, product=product)


def process_product_args(args):
    product, real_out = args
    return render_product(product, real_out)


def write_products(products: list[models.Product], out_path: str) -> None:
    logging.info("Beginning rendering products")
    real_out = os.path.join(out_path, "products")
    full_out_path = os.path.join(real_out, "index.html")
    os.makedirs(real_out, exist_ok=True)
    render_template("products.html", full_out_path, products=sorted(products))
    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        list(
            tqdm(
                pool.imap(
                    process_product_args, [(product, real_out) for product in products]
                ),
                total=len(products),
                desc="Rendering products",
                mininterval=0.5,
                unit="product",
            )
        )


def render_stig_index(products: list[models.Product], out_path: str) -> None:
    real_out = os.path.join(out_path, "stigs")
    full_out_path = os.path.join(real_out, "index.html")
    os.makedirs(real_out, exist_ok=True)
    stigs = list()
    for product in products:
        for stig in product.stigs:
            stig.product = product
            stigs.append(stig)
    render_template("stigs.html", full_out_path, stigs=sorted(stigs))


def write_index(products: list[models.Product], out_path: str) -> None:
    stigs = list()
    for product in products:
        stigs.extend(product.stigs)

    def _sort_stigs_by_date(stig):
        return stig.release_date

    stigs = sorted(stigs, key=_sort_stigs_by_date)
    full_out_path = os.path.join(out_path, "index.html")
    render_template("index.html", full_out_path, stigs=sorted(stigs[-9:], reverse=True))


def render_srg_index(srgs: dict, out_path: str) -> None:
    real_out = os.path.join(out_path, "srgs")
    full_out_path = os.path.join(real_out, "index.html")
    os.makedirs(real_out, exist_ok=True)
    render_template("srgs.html", full_out_path, srgs=srgs)
    render_srg_details(srgs, out_path)


def render_srg_details(srgs: dict, out_path: str) -> None:
    for srg_id in tqdm(srgs.keys(), desc="Rendering SRG details", unit="page"):
        controls = srgs[srg_id]
        full_out_path = os.path.join(out_path, "srgs", srg_id)
        os.makedirs(full_out_path, exist_ok=True)
        full_out = os.path.join(full_out_path, "index.html")
        render_template("srg_detail.html", full_out, controls=controls, srg_id=srg_id)


def _copy_latest_stig(out_product: str, product: models.Product):
    latest_stig = product.latest_stig
    current_versioned_root = os.path.join(
        out_product, latest_stig.short_version.lower()
    )
    product_latest_path = os.path.join(out_product, "latest")
    shutil.copytree(current_versioned_root, product_latest_path)
