#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

"""
This input and parser module is responsible for translating arithmetic
function terms specified in Python syntax to |EVMDDs|.
"""

import ast

from .evmdd import EvmddManager

_LEGAL_EXPRESSIONS = [ast.Expression, ast.Load, ast.BinOp,
                      ast.Add, ast.Mult, ast.Num, ast.Name,
                      ast.UnaryOp, ast.USub, ast.Sub]

def read_function_term(function_term):
    """Read a function term and transform it into an AST.

    Args:
        `function_term` (string): a function term using only :math:`+`, :math:`-`, and :math:`*`.

    Returns:
        `AST`: the abstract syntax tree representing function_term.
    """
    expression = ast.parse(function_term, mode='eval')
    for node in ast.walk(expression):
        assert type(node) in _LEGAL_EXPRESSIONS
    return expression

def collect_variables(function_term_ast):
    """Determine the set of all variables occurring in a given function term.

    Args:
        `function_term_ast`: a term represented as an abstract syntax tree.

    Returns:
        `set[string]`: the set of variables occurring in function_term_ast.
    """
    variables = set()
    for node in ast.walk(function_term_ast):
        if isinstance(node, ast.Name):
            name = node.id
            variables.add(name)
    return variables

def _to_evmdd_rec(node, manager):
    """Translate a function term represented as an AST to the corresponding
    EVMDD recursively.

    Base cases: if the given term is a number or a variable, return the
    corresponding constant or variable |EVMDD|. Recursive cases: if the
    term is an addition, subtraction, multiplication, or unary negation,
    recurse into the subexpressions, recursively translate them, and compose
    the sub-|EVMDDs| accordingly.

    Args:
        `node` (AST node): the abstract syntax tree node representing the
        arithmetic term to be translated into an |EVMDD|.

        `manager` (EvmddManager): the manager responsible for `node`.

    Returns:
        `Edge`: the corresponding |EVMDD|.
    """
    if isinstance(node, ast.Num):
        return manager.make_const_evmdd(int(node.n))
    elif isinstance(node, ast.Name):
        return manager.make_var_evmdd_for_var(node.id)
    elif isinstance(node, ast.BinOp):
        left = _to_evmdd_rec(node.left, manager)
        right = _to_evmdd_rec(node.right, manager)
        if isinstance(node.op, ast.Add):
            return left + right
        elif isinstance(node.op, ast.Sub):
            return left - right
        else:
            assert isinstance(node.op, ast.Mult)
            return left * right
    else:
        assert isinstance(node, ast.UnaryOp)
        assert isinstance(node.op, ast.USub)
        return -_to_evmdd_rec(node.operand, manager)

def term_to_evmdd(function_term, **kwargs):
    """Translate a function term to the corresponding |EVMDD|.

    The variable names in the desired variable ordering can be optionally
    specified. If no variable ordering is specified, the variable names are
    determined from the function term and ordered lexicographically.

    Also, the user may optionally specify the domain sizes of the variables.
    If no domain sized are specified, they default to 2 for all variables.

    Args:
        `function_term` (string): a function term in Python syntax using only
        constants, variables, addition, subtraction and multiplication.

        \*\*\ `kwargs`: optionally, the variable names in the desired ordering,
        `var_names` (list of strings), their domain sizes `var_domains`
        (dict from strings to ints), and a flag `fully_reduced`
        determining whether the |EVMDD| should be fully reduced or
        quasi-reduced.

    Returns:
        a tuple consisting of the corresponding |EVMDD| and its manager.

    The following example code constructs the fully reduced |EVMDD| for the
    running example :math:`f(A,B,C) = AB^2 + C + 2` for variable ordering
    :math:`A, B, C` and evaluates it for the valuation :math:`A=1`, :math:`B=2`,
    and :math:`C=0`.

    Example:
        >>> from .evmdd import evaluate
        >>> expr = 'A*B*B + C + 2'
        >>> var_names = ['A', 'B', 'C']
        >>> var_domains = {'A': 2, 'B': 3, 'C': 2}
        >>> evmdd, manager = term_to_evmdd(
        ...                      expr, var_names=var_names,
        ...                      var_domains=var_domains, fully_reduced=True)
        >>> valuation = {'A': 1, 'B': 2, 'C': 0}
        >>> evaluate(evmdd, valuation, manager)
        6

    The next example shows that this works across a range of function terms,
    variable orderings, valuations, and both for fully and quasi-reduced
    |EVMDDs|.

    Example:
        >>> from itertools import permutations, product
        >>> from .evmdd import evaluate
        >>>
        >>> def collect_variables(function_term):
        ...     variables = set()
        ...     expression = ast.parse(function_term, mode='eval')
        ...     for node in ast.walk(expression):
        ...         if(type(node) == ast.Name):
        ...             name = node.id
        ...             variables.add(name)
        ...     return variables
        ...
        >>>
        >>> exprs = [
        ...     '0', '1',
        ...     'A', 'B', '0*A', '2*A', '0*B', '2*B',
        ...     'A+B', 'B+A', '1-A', '1-B',
        ...     '-A', 'A-B', 'B-A', '-(A+B)',
        ...     'A*B + B', 'B + A*B',
        ...     'A*B*B + C + 2', 'A*B - 17',
        ...     'A*B - A*B', 'A-A'
        ... ]
        ...
        >>> domain_size = 4
        >>>
        >>> all_results_as_expected = True
        >>> for expr in exprs:
        ...     var_set = collect_variables(expr)
        ...     var_domains = {var: domain_size for var in var_set}
        ...     for fully_reduced in [True, False]:
        ...         for var_names in permutations(var_set):
        ...             for valuation in product(range(domain_size), repeat=len(var_set)):
        ...                 valuation = {var:val for var, val in zip(var_names,valuation)}
        ...                 evmdd, manager = term_to_evmdd(expr,
        ...                                  var_names=var_names, var_domains=var_domains,
        ...                                  fully_reduced=fully_reduced)
        ...                 actual = evaluate(evmdd, valuation, manager)
        ...                 expected = eval(expr, valuation)
        ...                 if actual != expected:
        ...                     all_results_as_expected = False
        ...
        >>> all_results_as_expected
        True
    """

    var_names = kwargs.get('var_names', None)
    var_domains = kwargs.get('var_domains', None)
    fully_reduced = kwargs.get('fully_reduced', True)

    function_term_ast = read_function_term(function_term)

    if not var_names:
        var_names = sorted(list(collect_variables(function_term_ast)))

    assert collect_variables(function_term_ast) <= set(var_names)

    if not var_domains:
        var_domains = {var: 2 for var in var_names}

    assert all([var in var_domains for var in var_names])
    var_domains = [var_domains[var] for var in var_names]

    manager = EvmddManager(var_names, var_domains, fully_reduced)

    assert isinstance(function_term_ast, ast.Expression)
    return _to_evmdd_rec(function_term_ast.body, manager), manager


def _test():
    import doctest
    doctest.testmod()


if __name__ == "__main__":
    _test()
