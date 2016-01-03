#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging

from evmdd.graphviz import EvmddVisualizer
from evmdd.parser import term_to_evmdd

def _print_usage():
    print('usage:   %s "<function term in Python syntax>"' % (
        sys.argv[0]) + ' ["<variable ordering>" ["<variable domain sizes>"]]')
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
        var_domains = {var: int(dom) for var, dom in zip(var_names, var_domains)}
    except IndexError:
        print('WARNING: No variable domain sizes specified.')
        print('         Assuming binary domains for all variables.')
        var_domains = None
        _print_usage()

    return function_term, var_names, var_domains

def main():
    function_term, var_names, var_domains = _parse_command_line()
    evmdd, manager = term_to_evmdd(function_term,
                                   var_names=var_names, var_domains=var_domains, fully_reduced=True)
    visualizer = EvmddVisualizer(manager)
    visualizer.visualize(evmdd)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
    main()
