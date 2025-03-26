from dataclasses import dataclass
from typing import cast, Any
import importlib

from injector import Injector, Module, singleton
from omegaconf import OmegaConf


def split_fully_qualified_name(s: str) -> tuple[str, str, str]:
    module, cls = s.split(":")
    if "." in cls:
        cls, method = cls.split(".")
    else:
        method = None
    return (module, cls, method)


def load_class_from(module_name: str, cls_name: str) -> type[Any]:
    module = importlib.import_module(module_name)
    cls = getattr(module, cls_name)
    return cls


def instantiate(cls: type[Any], args: dict[str, Any]) -> Any:
    schema = OmegaConf.structured(cls)
    conf = OmegaConf.create(args)
    merged = OmegaConf.merge(schema, conf)
    instance = cast(cls, OmegaConf.to_object(merged))  # type: ignore
    return instance


class Binder(Module):
    def __init__(self, binds: list[dict[str, Any]]):
        self.binds = binds

    def configure(self, binder):
        for bind_args in self.binds:
            ifqn = bind_args["interface"]
            tfqn = bind_args["to"]
            args = bind_args["args"]
            interface, instance = self._get_interface_and_instance(ifqn, tfqn, args)
            binder.bind(interface, instance, scope=singleton)
    
    def _get_interface_and_instance(self, ifqn: str, tfqn: str, args: dict[str, Any]) -> tuple[type[Any], type[Any]]:
        interface_module_name, interface_name, _ = split_fully_qualified_name(ifqn) 
        interface = load_class_from(interface_module_name, interface_name)

        class_module_name, class_name, _ = split_fully_qualified_name(tfqn)
        cls = load_class_from(class_module_name, class_name)
        ins = instantiate(cls, args)
        return interface, ins


@dataclass
class AppRunner:
    main: str
    binds: list[dict[str, Any]]

    def run(self):
        injector = Injector([Binder(self.binds)])

        main_module_name, main_cls_name, method_name = split_fully_qualified_name(self.main)
        cls = load_class_from(main_module_name, main_cls_name)
        app = injector.get(cls)
        getattr(app, method_name)()


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
