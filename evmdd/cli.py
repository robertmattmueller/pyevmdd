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
Command line interface for constructing and visualizing |EVMDDs|.
"""

import logging
import sys

from .graphviz import EvmddVisualizer
from .parser import term_to_evmdd


def _print_usage():
    print(
        'usage:   %s "<function term in Python syntax>"' % (sys.argv[0])
        + ' ["<variable ordering>" ["<variable domain sizes>"]]'
    )
    print('example: %s "A*B*B + C + 2" "A, B, C" "2, 3, 2"' % sys.argv[0])


def _parse_comma_separated_list(line):
    return [s.strip() for s in line.split(',')]


def _parse_command_line():
    try:
        function_term = sys.argv[1]
    except IndexError:
        print('ERROR: No function term specified.')
        _print_usage()
        sys.exit()

    try:
        var_names = sys.argv[2]
        var_names = _parse_comma_separated_list(var_names)
    except IndexError:
        print('WARNING: No valid variable ordering specified.')
        print('         Using lexicographic ordering.')
        var_names = None

    try:
        var_domains = sys.argv[3]
        var_domains = _parse_comma_separated_list(var_domains)
        assert len(var_names) == len(var_domains)
        var_domains = {var: int(dom) for var, dom in zip(var_names, var_domains, strict=True)}
    except IndexError:
        print('WARNING: No variable domain sizes specified.')
        print('         Assuming binary domains for all variables.')
        var_domains = None
        _print_usage()

    return function_term, var_names, var_domains


def main():
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
    function_term, var_names, var_domains = _parse_command_line()
    evmdd, manager = term_to_evmdd(
        function_term, var_names=var_names, var_domains=var_domains, fully_reduced=True
    )
    visualizer = EvmddVisualizer(manager)
    visualizer.visualize(evmdd)


if __name__ == '__main__':
    main()
