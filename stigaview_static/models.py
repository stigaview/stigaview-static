from __future__ import annotations

import datetime
import pathlib
import sys
import tomllib


class Srg:
    srg_id: str
    title: str
    controls: list[Control]


class Control:
    srg: Srg
    vulnerability_id: str
    disa_stig_id: str
    severity: str
    title = str
    description: str
    fix_text: str
    fix: str
    check_content: str
    cci: str

    def __repr__(self):
        return f"<Control {self.disa_stig_id}>"

    def __le__(self, other):
        return self.disa_stig_id < other.disa_stig_id

    def __gt__(self, other):
        return self.disa_stig_id > other.disa_stig_id


class Stig:
    release: int
    version: int
    release_date: datetime.date
    controls: list[Control]
    product: Product

    def __init__(self, release: int, version: int, release_date: datetime.date):
        self.release = release
        self.version = version
        self.release_date = release_date
        self.controls = list()

    @property
    def short_version(self) -> str:
        return f"V{self.version}R{self.release}"

    def __repr__(self):
        return f"<Stig {self.short_version}>"

    def __le__(self, other):
        return self.release_date < other.release_date

    def __gt__(self, other):
        return self.release_date > other.release_date


class Product:
    full_name: str
    short_name: str
    stigs: list[Stig]

    def __init__(self, full_name: str, short_name: str):
        self.full_name = full_name
        self.short_name = short_name
        self.stigs = list()

    @staticmethod
    def get_products(config: dict) -> list[Product]:
        products = list()
        products_path = pathlib.Path(config["products_path"])
        for product in products_path.iterdir():
            config_path = product.joinpath("product.toml")
            if not config_path.exists():
                sys.stderr.write(
                    f"Unable to find config for {product.name} at {str(config_path.absolute())}"
                )
                exit(5)
            with open(config_path, "r") as config_file:
                product_config = tomllib.loads(config_file.read())
                p = Product(product_config["full_name"], product_config["short_name"])
                products.append(p)
        return products

    def sort_stigs(self):
        self.stigs = sorted(self.stigs)

    def __repr__(self):
        return repr((self.short_name, self.full_name))

    def __le__(self, other):
        return self.short_name < other.short_name

    def __gt__(self, other):
        return self.short_name > other.short_name
