import pandas as pd


class App:
    def __init__(self, a: int, b: "B", df: pd.DataFrame):
        self.a = a
        self.b = b
        self.df = df

    def run(self):
        print(self.a)
        print(self.df)
        self.b.run()


class B:
    def __init__(self, c: "C"):
        self.c = c

    def run(self):
        print("B.run")
        self.c.run()


class C:
    def run(self):
        print("C.run")
