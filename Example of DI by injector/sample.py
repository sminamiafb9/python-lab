from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from injector import inject
import pandas as pd


@inject
@dataclass
class App:
    b: "B"
    config: "Configuration"

    def __post_init__(self):
        self._a = self.config.a
        self._df = pd.DataFrame(self.config.df)

    def run(self):
        print(self._a)
        print(self._df)
        self.b.run()


@inject
@dataclass
class B:
    c: "IC"

    def run(self):
        print("B.run")
        self.c.run()


@runtime_checkable
class IC(Protocol):
    def run(self): ...


@dataclass
class C:
    def run(self):
        print("C.run")


@dataclass
class Configuration:
    a: int
    df: dict[str, Any]
