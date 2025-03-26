from dataclasses import dataclass
from typing import cast, Any
import importlib

from injector import Injector, Module, singleton
from omegaconf import OmegaConf


@dataclass(frozen=True)
class QualifiedName:
    module: str
    cls: str
    method: str | None

    @staticmethod
    def split_fully_qualified_name(fqn: str) -> "QualifiedName":
        module, cls = fqn.split(":")
        method = None
        if "." in cls:
            cls, method = cls.split(".")
        return QualifiedName(module=module, cls=cls, method=method)


def load_class(module_name: str, cls_name: str) -> type[Any]:
    module = importlib.import_module(module_name)
    return getattr(module, cls_name)

def create_instance(cls: type[Any], args: dict[str, Any]) -> Any:
    schema = OmegaConf.structured(cls)
    conf = OmegaConf.create(args)
    merged = OmegaConf.merge(schema, conf)
    return cast(cls, OmegaConf.to_object(merged))  # type: ignore

class Binder(Module):
    def __init__(self, bindings: list[dict[str, Any]]):
        self.bindings = bindings

    def configure(self, binder):
        for binding in self.bindings:
            interface, instance = self._resolve_binding(binding)
            binder.bind(interface, instance, scope=singleton)
    
    def _resolve_binding(self, binding: dict[str, Any]) -> tuple[type[Any], type[Any]]:
        interface = self._load_class(binding["interface"])
        implementation = self._create_instance(binding["to"], binding["args"])
        return interface, implementation

    def _load_class(self, fqcn: str) -> type[Any]:
        qualified_name = QualifiedName.split_fully_qualified_name(fqcn)
        return load_class(qualified_name.module, qualified_name.cls)

    def _create_instance(self, fqcn: str, args: dict[str, Any]) -> Any:
        cls = self._load_class(fqcn)
        return create_instance(cls, args)

@dataclass
class AppRunner:
    main: str
    bindings: list[dict[str, Any]]

    def run(self):
        injector = Injector([Binder(self.bindings)])
        app_class = self._load_main_class()
        app_instance = injector.get(app_class)
        self._run_app(app_instance)

    def _load_main_class(self) -> type[Any]:
        qualified_name = QualifiedName.split_fully_qualified_name(self.main)
        return load_class(qualified_name.module, qualified_name.cls)

    def _run_app(self, app: Any) -> None:
        method_name = QualifiedName.split_fully_qualified_name(self.main).method
        if method_name:
            getattr(app, method_name)()

def execute(yaml_file: str) -> None:
    config = OmegaConf.load(yaml_file)
    app_config = OmegaConf.merge(OmegaConf.structured(AppRunner), config)
    runner = cast(AppRunner, OmegaConf.to_object(app_config))
    runner.run()

if __name__ == "__main__":
    import fire  # type: ignore
    fire.Fire(execute)
