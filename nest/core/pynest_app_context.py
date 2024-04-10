import logging
from typing import TypeVar, Union

from nest.common.exceptions import UnknownModuleException
from nest.common.module import Module, ModuleCompiler
from nest.core.pynest_container import PyNestContainer

T = TypeVar("T")


class PyNestApplicationContext:
    """
    Represents the application context in a PyNest application.
    This class is responsible for managing the application's lifecycle and modules.

    Attributes:
        container (PyNestContainer): The container that holds the application's modules and manages the dependency injection.
        context_module (Module, optional): The module that represents the current context of the application.
        logger (Logger): Logger for the application context.

    Args:
        container (PyNestContainer): The container for the application.
        context_module (Union[Module, None], optional): The initial context module of the application.
    """

    _is_initialized = False
    _module_compiler = ModuleCompiler()

    @property
    def is_initialized(self):
        """
        Property to check if the application context is initialized.

        Returns:
            bool: True if the application context is initialized, False otherwise.
        """
        return self._is_initialized

    @is_initialized.setter
    def is_initialized(self, value: bool):
        """
        Setter for the is_initialized property.

        Args:
            value (bool): The new value for the is_initialized property.
        """
        self._is_initialized = value

    def init(self):
        """
        Initializes the application context. If the context is already initialized, it returns itself.

        Returns:
            PyNestApplicationContext: The initialized application context.
        """
        if self._is_initialized:
            return self

        self._is_initialized = True
        return self

    def __init__(
        self, container: PyNestContainer, context_module: Union[Module, None] = None
    ):
        """
        Constructor for the PyNestApplicationContext.

        Args:
            container (PyNestContainer): The container for the application.
            context_module (Union[Module, None], optional): The initial context module of the application.
        """
        self.container = container
        self.context_module: Module = context_module
        self.logger = logging.getLogger(PyNestApplicationContext.__name__)

    def select_context_module(self):
        """
        Selects the first module from the container as the context module.
        """
        modules = self.container.modules.values()
        self.context_module = next(iter(modules), None)

    def select(self, module: T) -> T:
        """
        Selects a specific module as the current context module based on the provided module class - The selected Module is the AppModule that contains all the application's graph.

        Args:
            module (Module): The module class to select.

        Returns:
            PyNestApplicationContext: A new application context with the selected module.

        Raises:
            UnknownModuleException: If the specified module is not found in the application's modules.
        """
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
