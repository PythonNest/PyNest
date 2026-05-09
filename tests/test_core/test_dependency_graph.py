import pytest
from nest.core.dependency_graph import DependencyGraph, CycleError


class A: pass
class B: pass
class C: pass
class D: pass


def test_add_node_is_idempotent():
    g = DependencyGraph()
    g.add_node(A)
    g.add_node(A)
    assert A in g.nodes


def test_add_dependency_adds_both_nodes():
    g = DependencyGraph()
    g.add_dependency(A, B)  # A depends on B
    assert A in g.nodes
    assert B in g.nodes


def test_no_cycles_in_linear_chain():
    g = DependencyGraph()
    g.add_dependency(A, B)
    g.add_dependency(B, C)
    assert g.detect_cycles() == []


def test_direct_cycle_detected():
    g = DependencyGraph()
    g.add_dependency(A, B)
    g.add_dependency(B, A)
    cycles = g.detect_cycles()
    assert len(cycles) == 1
    cycle = cycles[0]
    assert A in cycle
    assert B in cycle


def test_indirect_cycle_detected():
    g = DependencyGraph()
    g.add_dependency(A, B)
    g.add_dependency(B, C)
    g.add_dependency(C, A)
    cycles = g.detect_cycles()
    assert len(cycles) == 1
    assert A in cycles[0]
    assert B in cycles[0]
    assert C in cycles[0]


def test_no_cycle_in_diamond():
    g = DependencyGraph()
    g.add_dependency(A, B)
    g.add_dependency(A, C)
    g.add_dependency(B, D)
    g.add_dependency(C, D)
    assert g.detect_cycles() == []


def test_topological_sort_single_node():
    g = DependencyGraph()
    g.add_node(A)
    result = g.topological_sort()
    assert result == [A]


def test_topological_sort_dependency_comes_first():
    g = DependencyGraph()
    g.add_dependency(A, B)  # A depends on B → B must come first
    result = g.topological_sort()
    assert result.index(B) < result.index(A)


def test_topological_sort_chain():
    g = DependencyGraph()
    g.add_dependency(A, B)
    g.add_dependency(B, C)
    result = g.topological_sort()
    assert result.index(C) < result.index(B) < result.index(A)


def test_topological_sort_diamond():
    g = DependencyGraph()
    g.add_dependency(A, B)
    g.add_dependency(A, C)
    g.add_dependency(B, D)
    g.add_dependency(C, D)
    result = g.topological_sort()
    assert result.index(D) < result.index(B)
    assert result.index(D) < result.index(C)
    assert result.index(B) < result.index(A)
    assert result.index(C) < result.index(A)


def test_validate_raises_cycle_error_with_chain():
    g = DependencyGraph()
    g.add_dependency(A, B)
    g.add_dependency(B, A)
    with pytest.raises(CycleError) as exc_info:
        g.validate()
    assert "A" in str(exc_info.value) or "B" in str(exc_info.value)


def test_validate_passes_for_valid_graph():
    g = DependencyGraph()
    g.add_dependency(A, B)
    g.add_dependency(B, C)
    g.validate()  # must not raise
