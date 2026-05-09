from __future__ import annotations

from typing import Any, List, Set


class CycleError(Exception):
    """Raised when a circular dependency is detected in the provider graph."""
    pass


class DependencyGraph:
    """
    Directed graph where an edge A → B means 'A depends on B'.
    Used to detect circular dependencies and determine initialization order.
    """

    def __init__(self) -> None:
        self._edges: dict[Any, Set[Any]] = {}

    @property
    def nodes(self) -> Set[Any]:
        return set(self._edges.keys())

    def add_node(self, node: Any) -> None:
        if node not in self._edges:
            self._edges[node] = set()

    def add_dependency(self, dependent: Any, dependency: Any) -> None:
        """Record that `dependent` requires `dependency` to be initialized first."""
        self.add_node(dependent)
        self.add_node(dependency)
        self._edges[dependent].add(dependency)

    def detect_cycles(self) -> List[List[Any]]:
        """Return a list of cycles (each cycle is a list of nodes). Empty list = no cycles."""
        visited: Set[Any] = set()
        path: List[Any] = []
        path_set: Set[Any] = set()
        cycles: List[List[Any]] = []

        def dfs(node: Any) -> None:
            visited.add(node)
            path.append(node)
            path_set.add(node)
            for dep in self._edges.get(node, set()):
                if dep not in visited:
                    dfs(dep)
                elif dep in path_set:
                    idx = path.index(dep)
                    cycles.append(list(path[idx:]) + [dep])
            path.pop()
            path_set.discard(node)

        for node in list(self._edges.keys()):
            if node not in visited:
                dfs(node)
        return cycles

    def topological_sort(self) -> List[Any]:
        """Return nodes in initialization order: dependencies come before dependents."""
        visited: Set[Any] = set()
        result: List[Any] = []

        def visit(node: Any) -> None:
            if node in visited:
                return
            visited.add(node)
            for dep in self._edges.get(node, set()):
                visit(dep)
            result.append(node)

        for node in list(self._edges.keys()):
            visit(node)
        return result

    def validate(self) -> None:
        """Raise CycleError if any circular dependencies exist."""
        cycles = self.detect_cycles()
        if cycles:
            chain = " → ".join(
                getattr(n, "__name__", repr(n)) for n in cycles[0]
            )
            raise CycleError(f"Circular dependency detected: {chain}")
