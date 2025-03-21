from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass
class App:
    a: int
    b: "B"
    df: dict[str, Any]  # It works with primitive data types.

    def __post_init__(self):
        self._df = pd.DataFrame(self.df)

    def run(self):
        print(self.a)
        print(self._df)
        self.b.run()


@dataclass
class B:
    c: "C"

    def run(self):
        print("B.run")
        self.c.run()


@dataclass
class C:
    def run(self):
        print("C.run")
