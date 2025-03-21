from dataclasses import dataclass
from typing import cast, Any
import importlib

from omegaconf import OmegaConf


@dataclass
class AppRunner:
    module: str
    cls: str
    entry_point: str
    args: dict[str, Any]

    def __post_init__(self) -> None:
        self.module_ = importlib.import_module(self.module)
        self.cls_ = getattr(self.module_, self.cls)

    def run(self):
        schema = OmegaConf.structured(self.cls_)
        conf = OmegaConf.create(self.args)
        merged = OmegaConf.merge(schema, conf)
        app = cast(self.cls_, OmegaConf.to_object(merged))  # type: ignore
        getattr(app, self.entry_point)()


def cmd(yaml_file_name: str) -> None:
    schema = OmegaConf.structured(AppRunner)
    conf = OmegaConf.load(yaml_file_name)
    merged = OmegaConf.merge(schema, conf)

    # to_object will convert it to an object, but it lacks type information.
    # You need to cast it separately.
    runner = cast(AppRunner, OmegaConf.to_object(merged))
    runner.run()


if __name__ == "__main__":
    import fire  # type: ignore

    fire.Fire(cmd)
