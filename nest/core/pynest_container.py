from __future__ import annotations

import inspect
import logging
from typing import Any, Dict, List, Optional, Type, Union

from nest.common.exceptions import CircularDependencyException
from nest.common.interfaces import (
    BeforeApplicationShutdown,
    OnApplicationBootstrap,
    OnApplicationShutdown,
    OnModuleDestroy,
    OnModuleInit,
)
from nest.common.module import CompiledModule, ModuleCompiler, ModuleTokenFactory
from nest.common.provider import InjectionToken, ProviderDescriptor
from nest.core.dependency_graph import DependencyGraph
from nest.core.encapsulation import validate_module_encapsulation
from nest.core.injector_module import build_injector, _to_key

_LIFECYCLE_METHOD_NAMES = (
    "on_module_init",
    "on_application_bootstrap",
    "before_application_shutdown",
    "on_module_destroy",
    "on_application_shutdown",
)


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
        self._module_instances: Dict[str, Any] = {}
        self._lifecycle_initialized = False
        self._lifecycle_shutdown = False
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
        validate_module_encapsulation(self._modules)

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
        self._module_instances.clear()
        self._lifecycle_initialized = False
        self._lifecycle_shutdown = False

    async def initialize_lifecycle(self) -> None:
        """Run module init and application bootstrap hooks once."""
        if self._injector is None:
            raise RuntimeError(
                "Container not built. Call container.build() before lifecycle hooks."
            )
        if self._lifecycle_initialized:
            return

        for module_ref in self._modules.values():
            await self._call_hooks(
                self._get_module_lifecycle_instances(module_ref),
                OnModuleInit,
                "on_module_init",
            )

        await self._call_hooks(
            self._get_all_lifecycle_instances(),
            OnApplicationBootstrap,
            "on_application_bootstrap",
        )
        self._lifecycle_initialized = True

    async def shutdown_lifecycle(self, signal: Optional[str] = None) -> None:
        """Run application shutdown hooks once in graceful shutdown order."""
        if self._injector is None:
            raise RuntimeError(
                "Container not built. Call container.build() before lifecycle hooks."
            )
        if self._lifecycle_shutdown:
            return

        modules = list(self._modules.values())
        for module_ref in reversed(modules):
            await self._call_hooks(
                self._get_module_lifecycle_instances(module_ref),
                BeforeApplicationShutdown,
                "before_application_shutdown",
                signal,
            )

        for module_ref in reversed(modules):
            await self._call_hooks(
                self._get_module_lifecycle_instances(module_ref),
                OnModuleDestroy,
                "on_module_destroy",
            )

        for module_ref in reversed(modules):
            await self._call_hooks(
                self._get_module_lifecycle_instances(module_ref),
                OnApplicationShutdown,
                "on_application_shutdown",
                signal,
            )

        self._lifecycle_shutdown = True

    # ── Internal ───────────────────────────────────────────────────────────────

    def _make_controller_descriptors(self) -> List[ProviderDescriptor]:
        from nest.common.provider import Scope

        return [
            ProviderDescriptor(provide=cls, use_class=cls, scope=Scope.SINGLETON)
            for cls in self._controller_classes
        ]

    def _validate_dependency_graph(self) -> None:
        """Build a DAG from all class providers and raise CircularDependencyException on cycles."""
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
            chain = " → ".join(getattr(n, "__name__", repr(n)) for n in cycles[0])
            raise CircularDependencyException(f"Circular dependency detected: {chain}")

    def _get_all_lifecycle_instances(self) -> List[Any]:
        instances: List[Any] = []
        seen: set[int] = set()
        for module_ref in self._modules.values():
            for instance in self._get_module_lifecycle_instances(module_ref):
                instance_id = id(instance)
                if instance_id in seen:
                    continue
                seen.add(instance_id)
                instances.append(instance)
        return instances

    def _get_module_lifecycle_instances(self, module_ref: ModuleRef) -> List[Any]:
        instances: List[Any] = []
        seen: set[int] = set()

        for desc in module_ref.compiled.provider_descriptors:
            instance = self.get(desc.provide)
            instance_id = id(instance)
            if instance_id in seen:
                continue
            seen.add(instance_id)
            instances.append(instance)

        module_instance = self._get_module_instance(module_ref)
        if module_instance is not None and id(module_instance) not in seen:
            instances.append(module_instance)

        return instances

    def _get_module_instance(self, module_ref: ModuleRef) -> Optional[Any]:
        if module_ref.token in self._module_instances:
            return self._module_instances[module_ref.token]

        if not any(
            callable(getattr(module_ref.metatype, name, None))
            for name in _LIFECYCLE_METHOD_NAMES
        ):
            return None

        instance = self._instantiate_module(module_ref.metatype)
        self._module_instances[module_ref.token] = instance
        return instance

    def _instantiate_module(self, module_class: Type) -> Any:
        try:
            signature = inspect.signature(module_class.__init__)
        except (TypeError, ValueError):
            return module_class()

        kwargs = {}
        for param in list(signature.parameters.values())[1:]:
            if param.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                continue
            if param.annotation is not inspect.Parameter.empty:
                kwargs[param.name] = self.get(param.annotation)
            elif param.default is inspect.Parameter.empty:
                raise RuntimeError(
                    f"Cannot instantiate module {module_class.__name__}: "
                    f"constructor parameter {param.name!r} has no type annotation"
                )

        return module_class(**kwargs)

    async def _call_hooks(
        self, instances: List[Any], protocol: Type, method_name: str, *args: Any
    ) -> None:
        calls = [
            self._call_hook(instance, method_name, *args)
            for instance in instances
            if isinstance(instance, protocol)
        ]
        if calls:
            import asyncio

            await asyncio.gather(*calls)

    async def _call_hook(self, instance: Any, method_name: str, *args: Any) -> None:
        result = getattr(instance, method_name)(*args)
        if inspect.isawaitable(result):
            await result
