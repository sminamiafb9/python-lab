from typing import Any
from pathlib import Path
import importlib
import inspect

import yaml


def create_instance(config: dict[str, Any]) -> Any:
    cls_name = config.pop('cls')
    cls = globals()[cls_name]

    args = config.pop('args', {})
    kwargs = {}
    for key, value in args.items():
        if isinstance(value, dict) and 'cls' in value:
            kwargs[key] = create_instance(value)
        else:
            kwargs[key] = value
    return cls(**kwargs)


def load_modules(module_names: list[str]) -> None:
    for module_name in module_names:
        module = importlib.import_module(module_name)
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and obj.__module__.startswith(module_name):
                globals()[name] = obj


def run_app(config: dict[str, Any]):
    load_modules(config.get('modules', []))
    app = create_instance(config)
    entry_point_name = config['entry_point']
    getattr(app, entry_point_name)()


def cmd(yaml_file_name: str) -> None:
    yaml_file_path = Path(yaml_file_name)
    yml = yaml.safe_load(yaml_file_path.open())
    run_app(yml)


if __name__ == "__main__":
    import fire  # type: ignore
    fire.Fire(cmd)
