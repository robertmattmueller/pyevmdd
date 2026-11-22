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

import pytest

from evmdd import EvmddManager, evaluate, term_to_evmdd


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
