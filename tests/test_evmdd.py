# This file is part of the EVMDD Library for Python (pyevmdd).
# Copyright (C) 2016 Robert Mattmüller

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gc
import weakref

import pytest

from evmdd import Edge, EvmddManager, Node, evaluate, term_to_evmdd


@pytest.mark.parametrize(
    'var_names, var_domains',
    [
        (['A', 'B'], [2]),
        (['A', 'A'], [2, 2]),
        (['A'], [0]),
        (['A'], [-1]),
        (['A'], [2.0]),
    ],
)
def test_invalid_manager_arguments_are_rejected(var_names, var_domains):
    with pytest.raises(ValueError):
        EvmddManager(var_names, var_domains)


def test_unknown_variable_is_rejected():
    manager = EvmddManager(['A'], [2])
    with pytest.raises(ValueError, match='B'):
        manager.make_var_evmdd_for_var('B')


@pytest.mark.parametrize('value', [-1, 3])
def test_valuation_outside_of_domain_is_rejected(value):
    evmdd, manager = term_to_evmdd('A', var_domains={'A': 3})
    with pytest.raises(ValueError, match='A'):
        evaluate(evmdd, {'A': value}, manager)


def test_mixing_fully_and_quasi_reduced_evmdds_is_rejected():
    fully, _ = term_to_evmdd('A', fully_reduced=True)
    quasi, _ = term_to_evmdd('A', fully_reduced=False)
    with pytest.raises(ValueError):
        fully + quasi


@pytest.mark.parametrize('other', ['x', 1.5, None])
def test_unsupported_operand_types_raise_type_error(other):
    evmdd, _ = term_to_evmdd('A')
    for operation in [lambda: evmdd + other, lambda: evmdd - other, lambda: evmdd * other]:
        with pytest.raises(TypeError):
            operation()


def test_adding_integer_shifts_function():
    evmdd, manager = term_to_evmdd('A')
    assert evaluate(evmdd + 3, {'A': 1}, manager) == 4
    assert evaluate(evmdd - 3, {'A': 1}, manager) == -2


def test_equal_functions_are_represented_by_identical_objects():
    left, manager = term_to_evmdd('A*B + B', var_names=['A', 'B'])
    right, _ = term_to_evmdd('B + B*A', var_names=['A', 'B'])
    assert left is right


def test_node_and_edge_construction_is_unique_regardless_of_argument_form():
    sink = Node(0, [])
    assert Node(level=0, children=(), is_fully_reduced=True) is sink
    children = [Edge(0, sink), Edge(weight=1, succ=sink)]
    assert Node(1, children) is Node(level=1, children=tuple(children))


def test_unused_evmdds_are_garbage_collected():
    evmdd, _ = term_to_evmdd('A*B*C*D + 12345', var_domains={v: 7 for v in 'ABCD'})
    edge_ref, node_ref = weakref.ref(evmdd), weakref.ref(evmdd.succ)
    del evmdd
    gc.collect()
    assert edge_ref() is None
    assert node_ref() is None


def test_shared_sub_evmdds_are_traversed_once():
    # A chain of nodes where each node has two edges to the same successor:
    # there are 2**depth paths, but only depth + 1 nodes.
    depth = 64
    edge = Edge(0, Node(0, []), is_fully_reduced=False)
    for level in range(1, depth + 1):
        node = Node(level, [edge, edge + 1], is_fully_reduced=False)
        edge = Edge(0, node, is_fully_reduced=False)
    assert edge.num_nodes() == depth + 1
    assert edge.num_edges() == 2 * depth + 1
