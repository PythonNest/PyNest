from nest.common.module import ModuleCompiler, Module
from typing import Union
from nest.core.pynest_container import PyNestContainer
from nest.common.exceptions import UnknownModuleException
import logging


class PyNestApplicationContext:

    _is_initialized = False
    _module_compiler = ModuleCompiler()

    @property
    def is_initialized(self):
        return self._is_initialized

    @is_initialized.setter
    def is_initialized(self, value: bool):
        self._is_initialized = value

    def init(self):
        if self._is_initialized:
            return self

        self._is_initialized = True
        return self

    def __init__(
        self, container: PyNestContainer, context_module: Union[Module, None] = None
    ):
        self.container = container
        self.context_module: Module = context_module
        self.logger = logging.getLogger(PyNestApplicationContext.__name__)

    def select_context_module(self):
        modules = self.container.modules.values()
        self.context_module = next(iter(modules), None)

    def select(self, module):
        modules_container = self.container.modules
        module_token_factory = self.container.module_token_factory

        metadata = self._module_compiler.extract_metadata(module)
        token = module_token_factory.create(
            metadata["type"], metadata["dynamic_metadata"]
        )
        selected_module = modules_container.get(token)
        if selected_module is None:
            raise UnknownModuleException()

        return PyNestApplicationContext(self.container, selected_module)
