from __future__ import annotations

from typing import Any, List

from injector import Injector, Module as InjectorModule, noscope, singleton

from nest.common.provider import InjectionToken, ProviderDescriptor, Scope


def _injector_scope(scope: Scope):
    if scope == Scope.SINGLETON:
        return singleton
    return noscope  # TRANSIENT and REQUEST both use noscope at this layer


def _to_key(token: Any) -> Any:
    """Convert an InjectionToken or string to an injector-compatible key.

    Both InjectionToken and plain strings are usable directly as injector
    binding keys (the injector library accepts any hashable as a key).
    """
    return token


class PyNestInjectorModule(InjectorModule):
    """Translates a list of ProviderDescriptors into injector bindings.

    use_class and use_value providers are bound eagerly inside configure().
    use_factory and use_existing providers are deferred to build_injector()
    so that their dependencies (or aliased singletons) are already resolved.
    """

    def __init__(self, descriptors: List[ProviderDescriptor]) -> None:
        self._descriptors = [
            d for d in descriptors if d.use_factory is None and d.use_existing is None
        ]

    def configure(self, binder) -> None:
        from injector import InstanceProvider

        for desc in self._descriptors:
            scope = _injector_scope(desc.scope)
            key = _to_key(desc.provide)

            if desc.use_value is not None:
                binder.bind(key, to=InstanceProvider(desc.use_value))
            elif desc.use_class is not None:
                binder.bind(key, to=desc.use_class, scope=scope)


def build_injector(descriptors: List[ProviderDescriptor]) -> Injector:
    """
    Build and return a configured Injector from a list of ProviderDescriptors.

    use_factory and use_existing providers are resolved post-build so that
    their dependencies and aliased singletons are already in the injector.
    """
    from injector import InstanceProvider

    injector = Injector([PyNestInjectorModule(descriptors)])
    provider_counts = {}
    last_provider_index = {}
    for index, desc in enumerate(descriptors):
        key = _to_key(desc.provide)
        provider_counts[key] = provider_counts.get(key, 0) + 1
        last_provider_index[key] = index

    for index, desc in enumerate(descriptors):
        key = _to_key(desc.provide)

        if desc.use_factory is not None:
            deps = [injector.get(_to_key(t)) for t in desc.inject]
            instance = desc.use_factory(*deps)
            injector.binder.bind(key, to=InstanceProvider(instance))

        elif desc.use_existing is not None:
            # Resolve the aliased key to get the same (singleton) instance
            existing_instance = injector.get(_to_key(desc.use_existing))
            injector.binder.bind(key, to=InstanceProvider(existing_instance))

        elif (
            desc.use_value is not None
            and provider_counts[key] > 1
            and last_provider_index[key] == index
        ):
            injector.binder.bind(key, to=InstanceProvider(desc.use_value))

        elif (
            desc.use_class is not None
            and provider_counts[key] > 1
            and last_provider_index[key] == index
        ):
            injector.binder.bind(
                key,
                to=desc.use_class,
                scope=_injector_scope(desc.scope),
            )

    return injector
