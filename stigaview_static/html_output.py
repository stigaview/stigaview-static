import os.path

from jinja2 import Environment, FileSystemLoader

from stigaview_static import models


def render_template(template: str, out_path: str, **kwargs):
    file_loader = FileSystemLoader("templates")
    env = Environment(loader=file_loader)
    template = env.get_template(template)
    output = template.render(**kwargs)
    with open(out_path, "w") as fp:
        fp.write(output)


def render_product(product: models.Product, out_path: str):
    out_product = os.path.join(out_path, product.short_name)
    render_product_index(out_path, product)
    for stig in product.stigs:
        real_out_path = render_stig_detail(out_product, product, stig)
        for control in stig.controls:
            render_control(control, real_out_path)


def render_stig_detail(out_product, product, stig):
    real_out_path = os.path.join(out_product, stig.short_version.lower())
    real_out = os.path.join(real_out_path, "index.html")
    os.makedirs(real_out_path, exist_ok=True)
    render_template("stig.html", real_out, product=product, stig=stig)
    return real_out_path


def render_control(control, real_out_path):
    control_out_path = os.path.join(real_out_path, control.disa_stig_id)
    os.makedirs(control_out_path, exist_ok=True)
    control_out = os.path.join(control_out_path, "index.html")
    render_template("control.html", control_out, control=control)


def render_product_index(out_path, product):
    real_out = os.path.join(out_path, product.short_name)
    full_out_path = os.path.join(real_out, "index.html")
    os.makedirs(real_out, exist_ok=True)
    render_template("product.html", full_out_path, product=product)


def write_products(products: list[models.Product], out_path: str) -> None:
    real_out = os.path.join(out_path, "products")
    full_out_path = os.path.join(real_out, "index.html")
    os.makedirs(real_out, exist_ok=True)
    render_template("products.html", full_out_path, products=products)
    for product in products:
        render_product(product, real_out)


def render_stig_index(products: list[models.Product], out_path: str) -> None:
    real_out = os.path.join(out_path, "stigs")
    full_out_path = os.path.join(real_out, "index.html")
    os.makedirs(real_out, exist_ok=True)
    render_template("stigs.html", full_out_path, products=products)


def write_index(out_path: str) -> None:
    full_out_path = os.path.join(out_path, "index.html")
    render_template("index.html", full_out_path)
