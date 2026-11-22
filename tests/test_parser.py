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

from itertools import permutations, product

import pytest

from evmdd import collect_variables, evaluate, read_function_term, term_to_evmdd

EXPRS = [
    '0',
    '1',
    'A',
    'B',
    '0*A',
    '2*A',
    '0*B',
    '2*B',
    'A+B',
    'B+A',
    '1-A',
    '1-B',
    '-A',
    'A-B',
    'B-A',
    '-(A+B)',
    'A*B + B',
    'B + A*B',
    'A*B*B + C + 2',
    'A*B - 17',
    'A*B - A*B',
    'A-A',
    '1*(A+2)',
    'A*(B+2)',
    'A*(B+2)*(B+2) + C + 2',
    'A**0',
    'A**1',
    'A*B**2 + C + 2',
    '(A-B)**3',
    '-2*A**2',
]

DOMAIN_SIZE = 4


@pytest.mark.parametrize('fully_reduced', [True, False])
@pytest.mark.parametrize('expr', EXPRS)
def test_evmdd_agrees_with_python_eval(expr, fully_reduced):
    """For every variable ordering and every valuation, evaluating the
    |EVMDD| must yield the same value as evaluating the term in Python."""
    var_set = collect_variables(read_function_term(expr))
    var_domains = {var: DOMAIN_SIZE for var in var_set}
    for var_names in permutations(sorted(var_set)):
        evmdd, manager = term_to_evmdd(
            expr, var_names=list(var_names), var_domains=var_domains, fully_reduced=fully_reduced
        )
        for values in product(range(DOMAIN_SIZE), repeat=len(var_names)):
            valuation = dict(zip(var_names, values, strict=True))
            assert evaluate(evmdd, valuation, manager) == eval(expr, valuation)


def test_default_ordering_and_domains():
    evmdd, manager = term_to_evmdd('B + 2*A')
    assert evaluate(evmdd, {'A': 1, 'B': 1}, manager) == 3


@pytest.mark.parametrize('expr', ['A + B', 'A*B - A*B + 3', 'A + B - B'])
def test_fully_reduced_is_not_larger_than_quasi_reduced(expr):
    fully, _ = term_to_evmdd(expr, fully_reduced=True)
    quasi, _ = term_to_evmdd(expr, fully_reduced=False)
    assert fully.num_nodes() <= quasi.num_nodes()


def test_constant_function_has_only_sink_node():
    evmdd, _ = term_to_evmdd('A*B - A*B + 3', var_names=['A', 'B'])
    assert evmdd.weight == 3
    assert evmdd.succ.is_sink_node()


@pytest.mark.parametrize('expr', ['A**B', 'A**-1', 'A**1.5'])
def test_illegal_exponent_is_rejected(expr):
    with pytest.raises(ValueError):
        term_to_evmdd(expr)


@pytest.mark.parametrize(
    'expr', ['A / B', 'A % 2', 'f(A)', "'x' + A", 'True + A', 'None', '2.5 * A', '1j']
)
def test_illegal_syntax_is_rejected(expr):
    with pytest.raises(ValueError):
        read_function_term(expr)


def test_variable_missing_from_ordering_is_rejected():
    with pytest.raises(ValueError, match='C'):
        term_to_evmdd('A + C', var_names=['A', 'B'])


def test_variable_missing_from_domains_is_rejected():
    with pytest.raises(ValueError, match='B'):
        term_to_evmdd('A + B', var_domains={'A': 2})


def test_unknown_keyword_argument_is_rejected():
    with pytest.raises(TypeError):
        term_to_evmdd('A', var_order=['A'])
