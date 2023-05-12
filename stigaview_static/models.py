from __future__ import annotations
import datetime



class Srg:
    srg_id: str
    title: str


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



class Stig:
    release: int
    version: int
    release_date: datetime.date
    controls: list[Control]

    def __init__(self, release: int, version: int, release_date: datetime.date):
        self.release = release
        self.version = version
        self.release_date = release_date
        self.controls = list()

    @property
    def short_version(self) -> str:
        return f'V{self.version}R{self.release}'


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
        for product in config["products"]:
            p = Product(config["products"][product]["full_name"], product)
            products.append(p)
        return products
