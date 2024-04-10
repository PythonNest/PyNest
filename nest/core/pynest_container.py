import logging
from typing import Any, List, NoReturn, Optional, Union

import click
from injector import Injector, UnknownProvider, singleton

from nest.common.constants import DEPENDENCIES, INJECTABLE_TOKEN
from nest.common.exceptions import (
    CircularDependencyException,
    NoneInjectableException,
    UnknownModuleException,
)
from nest.common.module import (
    Module,
    ModuleCompiler,
    ModuleFactory,
    ModulesContainer,
    ModuleTokenFactory,
)

TController = type("TController", (), {})
TProvider = type("TProvider", (), {})


class PyNestContainer:
    _instance = None
    _dependencies = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PyNestContainer, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.logger = logging.getLogger("pynest")
        self._injector = Injector()

    _global_modules = set()
    _modules = ModulesContainer()
    _module_token_factory = ModuleTokenFactory()
    _module_compiler = ModuleCompiler(_module_token_factory)
    _modules_metadata = {}

    @property
    def modules(self):
        return self._modules

    @property
    def module_token_factory(self):
        return self._module_token_factory

    @property
    def modules_metadata(self):
        return self._modules_metadata

    @property
    def module_compiler(self):
        return self._module_compiler

    def get_instance(
        self,
        dependency: TProvider,
        provider: Optional[Union[TProvider, TController]] = None,
    ):
        try:
            self._injector.binder.bind(dependency, scope=singleton)
            instance = self._injector.get(dependency)
            self.logger.info(
                f"{click.style(dependency.__name__ + ' Detected ', fg='blue')}"
            )
        except UnknownProvider:
            raise Exception(f"Unknown provider {provider}")
        return instance

    def get_module_by_key(self, module_key: str) -> Module:
        return self._modules[module_key]

    def add_module(self, metaclass):
        module_factory = self._module_compiler.compile(metaclass)
        token = module_factory.token
        if self._modules.has(token):
            return {"module_ref": self.modules.get(token), "inserted": True}
        return {"module_ref": self.set_module(module_factory), "inserted": False}

    def add_related_module(self, related_module, token: str):
        if not self.modules.has(token):
            return
        module_ref = self.modules.get(token)
        compile_related_module = self.module_compiler.compile(related_module)
        related = self.modules.get(compile_related_module.token)
        module_ref.add_import(related)

    def _get_controllers(self, token: str):
        module_metadata = self.modules_metadata[token]
        controllers = module_metadata["controllers"]
        return controllers

    def _get_providers(self, token: str):
        module_metadata = self.modules_metadata[token]
        providers = module_metadata["providers"]
        return providers

    def add_providers(self, providers: List[Any], module_token: str):
        for provider in providers:
            self.add_provider(module_token, provider)

    def add_controllers(self, controllers: List[Any], module_token: str) -> NoReturn:
        for controller in controllers:
            self._add_controller(module_token, controller)

    def _add_controller(self, token: str, controller: TController) -> NoReturn:
        if not self.modules.has(token):
            raise UnknownModuleException()
        module_ref: Module = self.modules[token]
        module_ref.add_controller(controller)
        if hasattr(controller, DEPENDENCIES):
            for provider_name, provider_type in getattr(
                controller, DEPENDENCIES
            ).items():
                instance = self.get_instance(provider_type, controller)
                setattr(controller, provider_name, instance)

    def set_module(self, module_factory: ModuleFactory) -> Module:
        module_ref = Module(module_factory.type, self)
        module_ref.token = module_factory.token
        self._modules[module_factory.token] = module_ref

        self.add_metadata(module_factory.token, module_factory.dynamic_metadata)
        self.add_import(module_factory.token)
        self.add_providers(
            self._get_providers(module_factory.token), module_factory.token
        )
        self.add_controllers(
            self._get_controllers(module_factory.token), module_factory.token
        )

        self.logger.info(
            f"{click.style(module_factory.type.__name__ + ' Detected ', fg='green')}"
        )

        return module_ref

    def add_metadata(self, token: str, module_metadata):
        if not module_metadata:
            return
        self._modules_metadata[token] = module_metadata

    def add_modules(self, modules: List[Any]):
        if not modules:
            return
        for module in modules:
            self.add_module(module)

    def add_import(self, token: str):
        if not self.modules.has(token):
            return
        module_metadata = self._modules_metadata.get(token)
        module_ref: Module = self.modules.get(token)
        imports_mod: List[Any] = module_metadata.get("imports")
        self.add_modules(imports_mod)
        module_ref.add_imports(imports_mod)

    def add_provider(self, token: str, provider):
        module_ref: Module = self.modules[token]
        if not provider:
            raise CircularDependencyException(module_ref.metatype)

        if not module_ref:
            raise UnknownModuleException()
        if not hasattr(provider, INJECTABLE_TOKEN):
            error_message = f"""
            {click.style(provider.__name__, fg='red')} is not injectable. 
      To make {provider.__name__} injectable, apply the {click.style("@Injectable decorator", fg='green')} to the class definition. 
     or remove {click.style(provider.__name__, fg='red')} from the provider array of the Module class. 
     Please check your code and ensure that the decorator is correctly applied to the class.
          """
            raise NoneInjectableException(error_message)

        for dependency_name, dependency_instance in getattr(
            provider, DEPENDENCIES
        ).items():
            try:
                instance = self.get_instance(dependency_instance, provider)
                setattr(provider, dependency_name, instance)
            except Exception as e:
                self.logger.error(e)
                raise e

        module_ref.add_provider(provider)

    def clear(self):
        self.modules.clear()
