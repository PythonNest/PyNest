from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Type, Union
from unittest.mock import create_autospec

from nest.common.provider import InjectionToken, ProviderDescriptor, Scope
from nest.core.decorators.guards import BaseGuard
from nest.core.pynest_container import PyNestContainer

ProviderToken = Union[Type, InjectionToken, str]

_MISSING = object()


def _token_name(token: Any) -> str:
    return (
        getattr(token, "__name__", None)
        or getattr(token, "name", None)
        or repr(token)
    )


def create_auto_mock(cls: Type) -> Any:
    """Create a spec'd mock instance of `cls`. Async methods become AsyncMocks."""
    return create_autospec(cls, instance=True)


class OverrideBy:
    """Second half of the override_provider() fluent chain."""

    def __init__(self, builder: "TestingModuleBuilder", token: ProviderToken) -> None:
        self._builder = builder
        self._token = token

    def use_value(self, value: Any) -> "TestingModuleBuilder":
        """Replace the provider with a pre-built instance."""
        return self._builder._add_provider_override(
            self._token, ProviderDescriptor(provide=self._token, use_value=value)
        )

    def use_class(self, cls: Type) -> "TestingModuleBuilder":
        """Replace the provider with a different class (constructor-injected)."""
        return self._builder._add_provider_override(
            self._token,
            ProviderDescriptor(provide=self._token, use_class=cls, scope=Scope.SINGLETON),
        )

    def use_factory(
        self, factory: Callable, inject: Optional[List[Any]] = None
    ) -> "TestingModuleBuilder":
        """Replace the provider with the result of a factory function."""
        return self._builder._add_provider_override(
            self._token,
            ProviderDescriptor(
                provide=self._token, use_factory=factory, inject=list(inject or [])
            ),
        )


class GuardOverrideBy:
    """Second half of the override_guard() fluent chain."""

    def __init__(self, builder: "TestingModuleBuilder", guard: Type) -> None:
        self._builder = builder
        self._guard = guard

    def use_value(self, value: Any) -> "TestingModuleBuilder":
        """Replace the guard with a pre-built guard instance."""
        return self._builder._add_guard_override(
            self._guard, _guard_class_from_value(value)
        )

    def use_class(self, cls: Type) -> "TestingModuleBuilder":
        """Replace the guard with a different guard class."""
        return self._builder._add_guard_override(self._guard, cls)


def _guard_class_from_value(value: Any) -> Type:
    """Wrap a guard instance in a class so it fits the class-based guard pipeline."""

    class _ValueGuard(BaseGuard):
        security_scheme = getattr(value, "security_scheme", None)

        def __new__(cls):
            return value

    _ValueGuard.__name__ = f"Override({type(value).__name__})"
    return _ValueGuard


class TestingModuleBuilder:
    """
    Fluent builder for a test DI container, mirroring NestJS's Test.createTestingModule.

    Example::

        module = (
            PyNestTestingModule.create_testing_module(imports=[UserModule])
            .override_provider(UserRepository).use_value(FakeUserRepository())
            .compile()
        )
    """

    def __init__(
        self,
        imports: Optional[List[Type]] = None,
        controllers: Optional[List[Type]] = None,
        providers: Optional[List[Any]] = None,
        exports: Optional[List[Any]] = None,
    ) -> None:
        self._imports = list(imports or [])
        self._controllers = list(controllers or [])
        self._providers = list(providers or [])
        self._exports = list(exports or [])
        self._provider_overrides: List[tuple] = []
        self._guard_overrides: Dict[Type, Type] = {}
        self._auto_mock = False
        self._auto_mock_exclude: List[Any] = []
        self._auto_mock_factory: Optional[Callable[[Type], Any]] = None

    # ── overrides ──────────────────────────────────────────────────────────────

    def override_provider(self, token: ProviderToken) -> OverrideBy:
        """Start an override chain for a provider token."""
        return OverrideBy(self, token)

    def override_guard(self, guard: Type) -> GuardOverrideBy:
        """Start an override chain for a guard class applied via @UseGuards."""
        return GuardOverrideBy(self, guard)

    def use_auto_mock(
        self,
        exclude: Optional[List[Any]] = None,
        mock_factory: Optional[Callable[[Type], Any]] = None,
    ) -> "TestingModuleBuilder":
        """
        Replace every class-based provider with a spec'd mock
        (unittest.mock.create_autospec; async methods become AsyncMocks).

        Explicit override_provider() calls and tokens in `exclude` keep
        their real implementation. Controllers are never mocked.
        """
        self._auto_mock = True
        self._auto_mock_exclude = list(exclude or [])
        self._auto_mock_factory = mock_factory
        return self

    def _add_provider_override(
        self, token: ProviderToken, descriptor: ProviderDescriptor
    ) -> "TestingModuleBuilder":
        self._provider_overrides.append((token, descriptor))
        return self

    def _add_guard_override(self, guard: Type, replacement: Type) -> "TestingModuleBuilder":
        self._guard_overrides[guard] = replacement
        return self

    # ── compilation ────────────────────────────────────────────────────────────

    def compile(self) -> "TestingModule":
        """
        Build the container and return a TestingModule.

        Works both synchronously and with `await` (TestingModule is awaitable)::

            module = builder.compile()
            module = await builder.compile()
        """
        container = PyNestContainer()
        container.add_module(self._build_root_module())

        for token, descriptor in self._provider_overrides:
            replaced = container.replace_provider(token, descriptor)
            if not replaced:
                known = ", ".join(
                    sorted(_token_name(d.provide) for d in container.provider_descriptors)
                )
                raise ValueError(
                    f"Cannot override provider {_token_name(token)!r}: it is not "
                    f"registered in the testing module. Known providers: {known}"
                )

        if self._auto_mock:
            self._apply_auto_mock(container)

        container.build()
        return TestingModule(container, dict(self._guard_overrides))

    def _build_root_module(self) -> Type:
        return type(
            "PyNestTestingRootModule",
            (),
            {
                "imports": list(self._imports),
                "controllers": list(self._controllers),
                "providers": list(self._providers),
                "exports": list(self._exports),
                "__is_module__": True,
                "__is_global__": False,
            },
        )

    def _apply_auto_mock(self, container: PyNestContainer) -> None:
        overridden = [token for token, _ in self._provider_overrides]
        make_mock = self._auto_mock_factory or create_auto_mock

        for desc in container.provider_descriptors:
            if desc.use_class is None:
                continue
            if desc.provide in overridden:
                continue
            if desc.provide in self._auto_mock_exclude or (
                desc.use_class in self._auto_mock_exclude
            ):
                continue
            if hasattr(desc.use_class, "__websocket_gateway__"):
                continue
            container.replace_provider(
                desc.provide,
                ProviderDescriptor(provide=desc.provide, use_value=make_mock(desc.use_class)),
            )


class TestingModule:
    """
    A compiled test container. Resolve providers with get(), drive lifecycle
    with init()/close(), and test HTTP behavior with create_http_client().

    Awaitable (so `await builder.compile()` works) and usable as an async
    context manager (init() on enter, close() on exit).
    """

    def __init__(
        self, container: PyNestContainer, guard_overrides: Dict[Type, Type]
    ) -> None:
        self._container = container
        self._guard_overrides = guard_overrides
        self._app = None
        self._guard_patches: List[tuple] = []

    @property
    def container(self) -> PyNestContainer:
        return self._container

    def get(self, token: ProviderToken) -> Any:
        """Retrieve a fully-wired instance (provider or controller) by token."""
        return self._container.get(token)

    async def init(self) -> "TestingModule":
        """Run on_module_init / on_application_bootstrap lifecycle hooks."""
        await self._container.initialize_lifecycle()
        return self

    async def close(self, signal: Optional[str] = None) -> None:
        """Run shutdown lifecycle hooks and undo guard patches."""
        try:
            await self._container.shutdown_lifecycle(signal)
        finally:
            self._restore_guards()

    def __await__(self):
        async def _identity() -> "TestingModule":
            return self

        return _identity().__await__()

    async def __aenter__(self) -> "TestingModule":
        return await self.init()

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    # ── HTTP testing ───────────────────────────────────────────────────────────

    def create_nest_application(self, **fastapi_kwargs: Any):
        """
        Create (and cache) a full PyNestApp with all routes registered.
        Guard overrides are applied before route registration.
        """
        if self._app is None:
            from fastapi import FastAPI

            from nest.core.pynest_application import PyNestApp

            # Guards are captured into route dependencies during PyNestApp
            # construction, so the __guards__ patches can be undone right after —
            # no global state leaks between testing modules.
            self._apply_guard_overrides()
            try:
                self._app = PyNestApp(self._container, FastAPI(**fastapi_kwargs))
            finally:
                self._restore_guards()
        return self._app

    def create_http_client(self, **client_kwargs: Any):
        """
        In-process async HTTP client (httpx.AsyncClient over ASGITransport).
        No network, no server process. Requires the `testing` extra:
        pip install "pynest-api[testing]".
        """
        httpx = _import_httpx()
        app = self.create_nest_application().get_server()
        client_kwargs.setdefault("base_url", "http://testserver")
        return httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), **client_kwargs
        )

    def create_test_client(self, **client_kwargs: Any):
        """Synchronous in-process client (fastapi.testclient.TestClient)."""
        from fastapi.testclient import TestClient

        return TestClient(self.create_nest_application().get_server(), **client_kwargs)

    # ── guard patching ─────────────────────────────────────────────────────────

    def _apply_guard_overrides(self) -> None:
        if not self._guard_overrides:
            return
        for module_ref in self._container.modules.values():
            for controller in module_ref.compiled.controllers:
                self._patch_guards(controller)
                for member in vars(controller).values():
                    if callable(member) and hasattr(member, "__guards__"):
                        self._patch_guards(member)

    def _patch_guards(self, owner: Any) -> None:
        guards = getattr(owner, "__guards__", None)
        if not guards:
            return
        patched = [self._guard_overrides.get(guard, guard) for guard in guards]
        if patched == list(guards):
            return
        original = vars(owner).get("__guards__", _MISSING)
        self._guard_patches.append((owner, original))
        setattr(owner, "__guards__", patched)

    def _restore_guards(self) -> None:
        for owner, original in reversed(self._guard_patches):
            if original is _MISSING:
                try:
                    delattr(owner, "__guards__")
                except AttributeError:
                    pass
            else:
                setattr(owner, "__guards__", original)
        self._guard_patches.clear()


class PyNestTestingModule:
    """
    Entry point for PyNest's testing utilities, mirroring NestJS's `Test` class.

    Example::

        from nest.testing import PyNestTestingModule

        module = (
            PyNestTestingModule.create_testing_module(imports=[AppModule])
            .override_provider(Database).use_value(FakeDatabase())
            .compile()
        )
        service = module.get(UserService)
    """

    @staticmethod
    def create_testing_module(
        imports: Optional[List[Type]] = None,
        controllers: Optional[List[Type]] = None,
        providers: Optional[List[Any]] = None,
        exports: Optional[List[Any]] = None,
    ) -> TestingModuleBuilder:
        return TestingModuleBuilder(
            imports=imports,
            controllers=controllers,
            providers=providers,
            exports=exports,
        )


# NestJS-style alias: Test.create_testing_module(...)
Test = PyNestTestingModule


def _import_httpx():
    try:
        import httpx
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "httpx is required for create_http_client(). "
            'Install it with: pip install "pynest-api[testing]"'
        ) from exc
    return httpx
