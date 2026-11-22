# This file is part of the EVMDD Library for Python (pyevmdd).
# Copyright (C) 2016, 2026 Robert Mattmüller

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

import argparse
import logging
from collections.abc import Sequence

from .graphviz import EvmddVisualizer, GraphvizWriter
from .parser import term_to_evmdd


def _parse_comma_separated_list(line: str) -> list[str]:
    return [s.strip() for s in line.split(',')]


def _make_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='evmdd',
        description='Construct the EVMDD for an arithmetic function term and visualize it.',
        epilog='example: evmdd "A*B*B + C + 2" "A, B, C" "2, 3, 2"',
    )
    parser.add_argument(
        'function_term',
        help='function term in Python syntax using integer constants, variables, +, -, *, and **',
    )
    parser.add_argument(
        'var_names',
        nargs='?',
        type=_parse_comma_separated_list,
        help='comma-separated variable ordering (default: lexicographic)',
    )
    parser.add_argument(
        'var_domains',
        nargs='?',
        type=_parse_comma_separated_list,
        help='comma-separated domain sizes in the same order (default: 2 for all variables)',
    )
    parser.add_argument(
        '--quasi-reduced',
        action='store_true',
        help='construct a quasi-reduced instead of a fully reduced EVMDD',
    )
    parser.add_argument(
        '--dot',
        metavar='FILE',
        help="write the EVMDD in Graphviz/DOT format to FILE ('-' for stdout) instead of "
        'displaying it',
    )
    return parser


def _parse_var_domains(
    parser: argparse.ArgumentParser, var_names: list[str] | None, var_domains: list[str] | None
) -> dict[str, int] | None:
    if var_domains is None:
        return None
    # argparse only fills the second optional positional argument if the first one is given.
    assert var_names is not None
    if len(var_names) != len(var_domains):
        parser.error(f'got {len(var_names)} variable names, but {len(var_domains)} domain sizes')
    try:
        return {var: int(dom) for var, dom in zip(var_names, var_domains, strict=True)}
    except ValueError:
        parser.error(f'domain sizes must be integers: {", ".join(var_domains)}')


def main(argv: Sequence[str] | None = None) -> None:
    """Run the command line interface.

    Args:
        `argv` (list of strings, optional): the command line arguments
        without the program name (default: ``sys.argv[1:]``).
    """
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
    parser = _make_argument_parser()
    args = parser.parse_args(argv)
    var_domains = _parse_var_domains(parser, args.var_names, args.var_domains)
    try:
        evmdd, manager = term_to_evmdd(
            args.function_term,
            var_names=args.var_names,
            var_domains=var_domains,
            fully_reduced=not args.quasi_reduced,
        )
    except (SyntaxError, ValueError) as e:
        parser.error(str(e))

    if args.dot == '-':
        print(GraphvizWriter(manager).evmdd_to_gvz(evmdd))
    elif args.dot:
        with open(args.dot, 'w') as dot_file:
            dot_file.write(GraphvizWriter(manager).evmdd_to_gvz(evmdd) + '\n')
    else:
        EvmddVisualizer(manager).visualize(evmdd)


if __name__ == '__main__':
    main()
