import logging
from typing import Any, List, Optional, Union

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
    """
    A singleton container class for managing modules, providers, and dependencies
    in a PyNest application.
    """

    _instance = None
    _dependencies = None

    def __new__(cls):
        """Create a singleton instance of PyNestContainer."""
        if cls._instance is None:
            cls._instance = super(PyNestContainer, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the PyNestContainer."""
        if not hasattr(self, "_initialized"):  # Prevent reinitialization
            self.logger = logging.getLogger("pynest")
            self._injector = Injector()
            self._global_modules = set()
            self._modules = ModulesContainer()
            self._module_token_factory = ModuleTokenFactory()
            self._module_compiler = ModuleCompiler(self._module_token_factory)
            self._modules_metadata = {}
            self._initialized = True

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
            self.logger.info(click.style(dependency.__name__ + " Detected ", fg="blue"))
        except UnknownProvider:
            raise Exception(f"Unknown provider {provider}")
        return instance

    def add_module(self, metaclass) -> dict:
        """
        Add a module to the container.

        Args:
            metaclass: The metaclass of the module to be added.

        Returns:
            dict: A dictionary containing the module reference and a
            boolean flag indicating if it was newly inserted.
        """
        module_factory = self._module_compiler.compile(metaclass)
        token = module_factory.token
        if self._modules.has(token):
            return {"module_ref": self.modules.get(token), "inserted": False}
        return {"module_ref": self.register_module(module_factory), "inserted": True}

    def register_module(self, module_factory: ModuleFactory) -> Module:
        """
        Register a module in the container.

        This method creates a module reference from the provided module factory, registers
        the module within the container, adds metadata, imports, providers, and controllers
        associated with the module, and logs the detection of the module.

        Args:
            module_factory (ModuleFactory): The factory object that contains the type and metadata
                                            for creating the module.

        Returns:
            Module: The module reference that has been registered in the container.

        """
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
            click.style(module_factory.type.__name__ + " Detected ", fg="green")
        )

        return module_ref

    def add_metadata(self, token: str, module_metadata) -> None:
        """Add metadata for a module."""
        if module_metadata:
            self._modules_metadata[token] = module_metadata

    def add_import(self, token: str):
        """Add imports for a module."""
        if not self.modules.has(token):
            return
        module_metadata = self._modules_metadata.get(token)
        module_ref: Module = self.modules.get(token)
        imports_mod: List[Any] = module_metadata.get("imports")
        self.add_modules(imports_mod)
        module_ref.add_imports(imports_mod)

    def add_modules(self, modules: List[Any]) -> None:
        """Add multiple modules to the container."""
        if modules:
            for module in modules:
                self.add_module(module)

    def add_providers(self, providers: List[Any], module_token: str) -> None:
        """Add multiple providers to a module."""
        for provider in providers:
            self.add_provider(module_token, provider)

    def add_provider(self, token: str, provider):
        """Add a provider to a module."""
        module_ref: Module = self.modules[token]
        if not provider:
            raise CircularDependencyException(module_ref.metatype)

        if not module_ref:
            raise UnknownModuleException()

        if not hasattr(provider, INJECTABLE_TOKEN):
            error_message = f"""
            {click.style(provider.__name__, fg='red')} is not injectable. 
            To make {provider.__name__} injectable, apply the {click.style("@Injectable decorator", fg='green')}
            to the class definition, or remove {click.style(provider.__name__, fg='red')} from the provider array
            of the Module class. Please check your code and ensure that the decorator is correctly applied to the
            class.
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

    def _get_providers(self, token: str) -> List[Any]:
        """Get providers from the module metadata."""
        return self.modules_metadata[token]["providers"]

    def add_controllers(self, controllers: List[Any], module_token: str) -> None:
        """Add multiple controllers to a module."""
        for controller in controllers:
            self._add_controller(module_token, controller)

    def _add_controller(self, token: str, controller: TController) -> None:
        """Add a controller to a module."""
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

    def _get_controllers(self, token: str) -> List[Any]:
        """Get controllers from the module metadata."""
        return self.modules_metadata[token]["controllers"]

    def clear(self):
        """Clear all modules from the container."""
        self.modules.clear()

    # UNUSED: This function is currently not used but retained for potential future use.
    def add_related_module(self, related_module, token: str) -> None:
        if not self.modules.has(token):
            return
        module_ref = self.modules.get(token)
        compile_related_module = self.module_compiler.compile(related_module)
        related = self.modules.get(compile_related_module.token)
        module_ref.add_import(related)

    # UNUSED: This function is currently not used but retained for potential future use.
    # It retrieves a module from the container by its key.
    def get_module_by_key(self, module_key: str) -> Module:
        return self._modules[module_key]
