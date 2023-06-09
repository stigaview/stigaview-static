from __future__ import annotations

import datetime
import pathlib
import sys
import tomllib
from typing import List

from pydantic import BaseModel


class Srg(BaseModel):
    srg_id: str
    title: str | None
    controls: list[Control] = []

    @property
    def url(self) -> str:
        return f"/srgs/{ self.srg_id }"


class Control(BaseModel):
    srg: Srg
    vulnerability_id: str
    disa_stig_id: str
    severity: str
    title: str
    description: str
    fix: str
    check: str
    cci: str
    stig: Stig

    def __repr__(self):
        return f"<Control {self.disa_stig_id}>"

    def __le__(self, other):
        return self.disa_stig_id < other.disa_stig_id

    def __gt__(self, other):
        return self.disa_stig_id > other.disa_stig_id

    @property
    def url(self) -> str:
        return f"/{self.stig.url}/{self.disa_stig_id}"


class Stig(BaseModel):
    release: int
    version: int
    release_date: datetime.date
    controls: List[Control] = []
    product: Product

    @property
    def short_version(self) -> str:
        return f"V{self.version}R{self.release}"

    @property
    def url(self) -> str:
        return f"/products/{self.product.url}/"

    def __repr__(self):
        return f"<Stig {self.short_version}>"

    def __le__(self, other):
        return self.release_date < other.release_date

    def __gt__(self, other):
        return self.release_date > other.release_date


class Product(BaseModel):
    full_name: str
    short_name: str
    stigs: list[Stig] = []

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
                p = Product(
                    full_name=product_config["full_name"],
                    short_name=product_config["short_name"],
                )
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

    @property
    def url(self) -> str:
        return f"/products/{self.short_name}"
