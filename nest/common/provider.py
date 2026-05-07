from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, List, Optional, Type, Union


class Scope(str, Enum):
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    REQUEST = "request"


class InjectionToken:
    """Named token for injecting non-class values (strings, primitives, configs)."""

    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description

    def __repr__(self) -> str:
        return f"InjectionToken({self.name!r})"

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, InjectionToken) and self.name == other.name


@dataclass
class ProviderDescriptor:
    """Normalized provider definition. Exactly one of use_class/use_value/use_factory/use_existing must be set."""

    provide: Union[Type, InjectionToken, str]
    use_class: Optional[Type] = None
    use_value: Any = None
    use_factory: Optional[Callable] = None
    use_existing: Optional[Union[Type, InjectionToken]] = None
    scope: Scope = Scope.SINGLETON
    inject: List[Any] = field(default_factory=list)


def normalize_provider(
    provider: Union[Type, dict, ProviderDescriptor],
) -> ProviderDescriptor:
    """Convert any provider form (class, dict, or ProviderDescriptor) to a ProviderDescriptor."""
    if isinstance(provider, ProviderDescriptor):
        return provider

    if isinstance(provider, dict):
        provide = provider["provide"]
        scope = provider.get("scope", Scope.SINGLETON)
        if "useValue" in provider:
            return ProviderDescriptor(
                provide=provide, use_value=provider["useValue"], scope=scope
            )
        if "useClass" in provider:
            return ProviderDescriptor(
                provide=provide, use_class=provider["useClass"], scope=scope
            )
        if "useFactory" in provider:
            return ProviderDescriptor(
                provide=provide,
                use_factory=provider["useFactory"],
                inject=provider.get("inject", []),
                scope=scope,
            )
        if "useExisting" in provider:
            return ProviderDescriptor(
                provide=provide, use_existing=provider["useExisting"], scope=scope
            )
        raise ValueError(
            f"Invalid provider descriptor: {provider!r}. "
            "Must contain one of: useValue, useClass, useFactory, useExisting"
        )

    if not callable(provider):
        raise ValueError(
            f"Provider must be a class, dict, or ProviderDescriptor, got {provider!r}"
        )
    return ProviderDescriptor(provide=provider, use_class=provider, scope=Scope.SINGLETON)
