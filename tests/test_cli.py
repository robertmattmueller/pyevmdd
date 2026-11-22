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

from evmdd import GraphvizWriter, term_to_evmdd
from evmdd.cli import main


def test_dot_output_to_stdout(capsys):
    main(['A*B*B + C + 2', 'A, B, C', '2, 3, 2', '--dot', '-'])
    evmdd, manager = term_to_evmdd(
        'A*B*B + C + 2', var_names=['A', 'B', 'C'], var_domains={'A': 2, 'B': 3, 'C': 2}
    )
    assert capsys.readouterr().out == GraphvizWriter(manager).evmdd_to_gvz(evmdd) + '\n'


def test_dot_output_to_file(tmp_path):
    dot_file = tmp_path / 'evmdd.dot'
    main(['A + B', '--quasi-reduced', '--dot', str(dot_file)])
    evmdd, manager = term_to_evmdd('A + B', fully_reduced=False)
    assert dot_file.read_text() == GraphvizWriter(manager).evmdd_to_gvz(evmdd) + '\n'


def test_display_is_default(monkeypatch):
    shown = []
    monkeypatch.setattr('evmdd.cli.EvmddVisualizer.visualize', lambda self, e: shown.append(e))
    main(['A'])
    assert len(shown) == 1


@pytest.mark.parametrize(
    'argv, message',
    [
        ([], 'function_term'),
        (['A + B', 'A, B', '2'], '2 variable names, but 1 domain sizes'),
        (['A + B', 'A, B', '2, x'], 'domain sizes must be integers'),
        (['A + C', 'A, B'], 'missing from variable ordering'),
        (['A / B'], 'Unsupported syntax'),
        (['A +'], 'invalid syntax'),
        (['A', 'A', '0'], 'positive integer'),
    ],
)
def test_invalid_input_exits_with_error(argv, message, capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(argv)
    assert exc_info.value.code == 2
    assert message in capsys.readouterr().err
