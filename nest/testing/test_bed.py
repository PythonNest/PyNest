"""
Suites-style unit-testing harness (https://suites.dev).

TestBed builds the unit under test with every constructor dependency replaced
by a spec'd mock — no module graph, no container, no manual wiring::

    unit, unit_ref = TestBed.solitary(UserService).compile()
    unit_ref.get(UserRepository).find_all.return_value = ["alice"]
    assert unit.get_users() == ["alice"]

Sociable mode keeps selected collaborators real while mocking the rest::

    unit, unit_ref = TestBed.sociable(UserService).expose(UserRepository).compile()
"""

from __future__ import annotations

import inspect
import typing
from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Set, Type
from unittest.mock import create_autospec


class UnitRef:
    """Read-only registry of the dependencies built for the unit under test."""

    def __init__(self, instances: Dict[Type, Any]) -> None:
        self._instances = instances

    def get(self, token: Type) -> Any:
        if token not in self._instances:
            known = ", ".join(
                sorted(getattr(t, "__name__", repr(t)) for t in self._instances)
            )
            raise KeyError(
                f"{getattr(token, '__name__', token)!r} was not injected into the "
                f"unit under test. Known dependencies: {known or '(none)'}"
            )
        return self._instances[token]


@dataclass
class UnitTestBed:
    """Result of TestBed.compile(): the real unit and a ref to its dependencies."""

    unit: Any
    unit_ref: UnitRef

    def __iter__(self) -> Iterator[Any]:
        yield self.unit
        yield self.unit_ref


class MockChain:
    """Second half of the .mock(Dep) fluent chain."""

    def __init__(self, builder: "TestBedBuilder", dep: Type) -> None:
        self._builder = builder
        self._dep = dep

    def using(self, **attributes: Any) -> "TestBedBuilder":
        """Configure attributes on the auto-generated mock (configure_mock style)."""
        self._builder._mock_attrs.setdefault(self._dep, {}).update(attributes)
        return self._builder

    def final(self, instance: Any) -> "TestBedBuilder":
        """Use `instance` as the dependency instead of generating a mock."""
        self._builder._finals[self._dep] = instance
        return self._builder


class TestBedBuilder:
    def __init__(self, unit_class: Type, sociable: bool) -> None:
        self._unit_class = unit_class
        self._sociable = sociable
        self._exposed: List[Type] = []
        self._finals: Dict[Type, Any] = {}
        self._mock_attrs: Dict[Type, Dict[str, Any]] = {}

    def mock(self, dep: Type) -> MockChain:
        """Start a mock-customization chain for one dependency."""
        return MockChain(self, dep)

    def expose(self, *deps: Type) -> "TestBedBuilder":
        """Keep these dependencies real (sociable mode only)."""
        if not self._sociable:
            raise RuntimeError(
                "expose() is only available on TestBed.sociable(). "
                "Solitary units mock every dependency."
            )
        self._exposed.extend(deps)
        return self

    def compile(self) -> UnitTestBed:
        registry: Dict[Type, Any] = {}
        building: Set[Type] = set()
        unit = self._build_real(self._unit_class, registry, building)
        return UnitTestBed(unit=unit, unit_ref=UnitRef(registry))

    # ── internal ───────────────────────────────────────────────────────────────

    def _resolve(self, dep_type: Type, registry: Dict, building: Set) -> Any:
        if dep_type in registry:
            return registry[dep_type]

        if dep_type in self._finals:
            instance = self._finals[dep_type]
        elif dep_type in self._exposed:
            instance = self._build_real(dep_type, registry, building)
        else:
            instance = create_autospec(dep_type, instance=True)
            if dep_type in self._mock_attrs:
                instance.configure_mock(**self._mock_attrs[dep_type])

        registry[dep_type] = instance
        return instance

    def _build_real(self, cls: Type, registry: Dict, building: Set) -> Any:
        if cls in building:
            chain = " → ".join(c.__name__ for c in building)
            raise RuntimeError(
                f"Circular dependency while building {cls.__name__} ({chain})"
            )
        building.add(cls)
        try:
            kwargs = {
                name: self._resolve(dep_type, registry, building)
                for name, dep_type in _constructor_dependencies(cls).items()
            }
            return cls(**kwargs)
        finally:
            building.discard(cls)


def _constructor_dependencies(cls: Type) -> Dict[str, Type]:
    """Map constructor parameter names to their annotated types."""
    try:
        signature = inspect.signature(cls.__init__)
    except (TypeError, ValueError):
        return {}

    try:
        hints = typing.get_type_hints(cls.__init__)
    except Exception:
        hints = getattr(cls.__init__, "__annotations__", {}) or {}

    dependencies: Dict[str, Type] = {}
    for name, param in signature.parameters.items():
        if name == "self" or param.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            continue
        annotation = hints.get(name, param.annotation)
        if annotation is inspect.Parameter.empty or not isinstance(annotation, type):
            if param.default is inspect.Parameter.empty:
                raise TypeError(
                    f"Cannot build {cls.__name__}: constructor parameter "
                    f"{name!r} has no usable type annotation and no default."
                )
            continue
        dependencies[name] = annotation
    return dependencies


class TestBed:
    """
    Entry point for Suites-style unit tests.

    - `TestBed.solitary(Unit)` — the unit is real, every dependency is mocked.
    - `TestBed.sociable(Unit).expose(Collaborator)` — exposed collaborators stay
      real (their own dependencies are mocked); everything else is mocked.
    """

    @staticmethod
    def solitary(unit_class: Type) -> TestBedBuilder:
        return TestBedBuilder(unit_class, sociable=False)

    @staticmethod
    def sociable(unit_class: Type) -> TestBedBuilder:
        return TestBedBuilder(unit_class, sociable=True)
