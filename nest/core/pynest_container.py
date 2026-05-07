from __future__ import annotations

import inspect
import logging
from typing import Any, Dict, List, Optional, Type, Union

from nest.common.exceptions import CircularDependencyException
from nest.common.module import CompiledModule, ModuleCompiler, ModuleTokenFactory
from nest.common.provider import InjectionToken, ProviderDescriptor
from nest.core.dependency_graph import DependencyGraph
from nest.core.injector_module import build_injector, _to_key


class ModuleRef:
    """Internal container representation of a registered module."""

    def __init__(self, token: str, metatype: Type, compiled: CompiledModule) -> None:
        self.token = token
        self.metatype = metatype
        self.compiled = compiled

    @property
    def name(self) -> str:
        return self.metatype.__name__


class PyNestContainer:
    """
    IoC container managing the module graph, provider bindings, and instance lifecycle.
    NOT a singleton — one fresh instance per application, created by PyNestFactory.
    """

    def __init__(self) -> None:
        self._logger = logging.getLogger("pynest.container")
        self._injector = None
        self._modules: Dict[str, ModuleRef] = {}
        self._all_descriptors: List[ProviderDescriptor] = []
        self._controller_classes: List[Type] = []
        self._module_token_factory = ModuleTokenFactory()
        self._module_compiler = ModuleCompiler(self._module_token_factory)

    # ── Public API ─────────────────────────────────────────────────────────────

    @property
    def modules(self) -> Dict[str, ModuleRef]:
        return self._modules

    @property
    def module_token_factory(self):
        return self._module_token_factory

    @property
    def module_compiler(self):
        return self._module_compiler

    def add_module(self, module_class: Type) -> dict:
        """Compile and register a module and all its imports recursively."""
        compiled = self._module_compiler.compile(module_class)
        token = compiled.token

        if token in self._modules:
            return {"module_ref": self._modules[token], "inserted": False}

        # Register imported modules first (depth-first)
        for imported in compiled.imports:
            self.add_module(imported)

        module_ref = ModuleRef(token=token, metatype=module_class, compiled=compiled)
        self._modules[token] = module_ref
        self._all_descriptors.extend(compiled.provider_descriptors)
        self._controller_classes.extend(compiled.controllers)

        self._logger.info(f"Module registered: {module_class.__name__}")
        return {"module_ref": module_ref, "inserted": True}

    def build(self) -> None:
        """
        Validate the dependency graph and build the injector.
        Must be called once after all add_module() calls, before any get() calls.
        """
        self._validate_dependency_graph()

        # Controller classes need singleton bindings too so the injector can resolve them
        all_descriptors = self._all_descriptors + self._make_controller_descriptors()
        self._injector = build_injector(all_descriptors)
        self._logger.info("Container built successfully")

    def get(self, token: Union[Type, InjectionToken, str]) -> Any:
        """Retrieve a fully-wired instance from the container."""
        if self._injector is None:
            raise RuntimeError(
                "Container not built. Call container.build() before resolving providers."
            )
        return self._injector.get(_to_key(token))

    def get_controller_instance(self, controller_class: Type) -> Any:
        """Get a controller instance with all its service dependencies injected."""
        return self.get(controller_class)

    def clear(self) -> None:
        """Reset container state. Useful in tests."""
        self._injector = None
        self._modules.clear()
        self._all_descriptors.clear()
        self._controller_classes.clear()

    # ── Internal ───────────────────────────────────────────────────────────────

    def _make_controller_descriptors(self) -> List[ProviderDescriptor]:
        from nest.common.provider import Scope
        return [
            ProviderDescriptor(provide=cls, use_class=cls, scope=Scope.SINGLETON)
            for cls in self._controller_classes
        ]

    def _validate_dependency_graph(self) -> None:
        """Build a DAG from all class providers and raise CircularDependencyException on cycles."""
        import sys

        graph = DependencyGraph()

        # Build a name→class lookup from all registered providers so forward refs can be resolved
        provider_classes = {
            desc.use_class.__name__: desc.use_class
            for desc in self._all_descriptors
            if desc.use_class is not None
        }

        for desc in self._all_descriptors:
            if desc.use_class is None:
                continue
            target = desc.use_class
            graph.add_node(target)
            try:
                sig = inspect.signature(target.__init__)
            except (ValueError, TypeError):
                continue

            # Resolve type hints, handling string forward references
            try:
                hints = {}
                for param_name, param in sig.parameters.items():
                    if param_name == "self":
                        continue
                    ann = param.annotation
                    if ann is param.empty:
                        continue
                    if isinstance(ann, str):
                        # Try to resolve the string annotation against known providers
                        resolved = provider_classes.get(ann)
                        if resolved is not None:
                            hints[param_name] = resolved
                    elif isinstance(ann, type):
                        hints[param_name] = ann
            except Exception:
                continue

            for dep_type in hints.values():
                graph.add_dependency(target, dep_type)

        cycles = graph.detect_cycles()
        if cycles:
            chain = " → ".join(
                getattr(n, "__name__", repr(n)) for n in cycles[0]
            )
            raise CircularDependencyException(
                f"Circular dependency detected: {chain}"
            )
