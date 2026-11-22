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

import os

import pytest

from evmdd import EvmddVisualizer, GraphvizWriter, term_to_evmdd


def test_dot_output_for_single_variable():
    evmdd, manager = term_to_evmdd('A + 2', var_names=['A'], var_domains={'A': 2})
    dot = GraphvizWriter(manager).evmdd_to_gvz(evmdd)
    assert dot.splitlines() == [
        'digraph G {',
        'dummyNode [style=invis];',
        'constantWeight [shape=box,height=0.25,width=0.5,label="+2"];',
        'dummyNode -> constantWeight [arrowhead=none, label=""];',
        'constantWeight -> "s1[level=1]";',
        '"s0[level=0]" [shape=box,height=0.25,width=0.5,rank=sink,label="0"];',
        '"s1[level=1]" [style=filled,fillcolor=lightgrey,label="A"];',
        '"s1[level=1]=0" [shape=box,height=0.25,width=0.5,label="+0"];',
        '"s1[level=1]" -> "s1[level=1]=0" [arrowhead=none, label="0"];',
        '"s1[level=1]=0" -> "s0[level=0]";',
        '"s1[level=1]=1" [shape=box,height=0.25,width=0.5,label="+1"];',
        '"s1[level=1]" -> "s1[level=1]=1" [arrowhead=none, label="1"];',
        '"s1[level=1]=1" -> "s0[level=0]";',
        '{rank = same; "s0[level=0]";}',
        '{rank = same; "s1[level=1]";}',
        '}',
    ]


def test_dot_output_mentions_every_variable_node():
    evmdd, manager = term_to_evmdd(
        'A*B**2 + C + 2', var_names=['A', 'B', 'C'], var_domains={'A': 2, 'B': 3, 'C': 2}
    )
    dot = GraphvizWriter(manager).evmdd_to_gvz(evmdd)
    for var_name in ['A', 'B', 'C']:
        assert f'label="{var_name}"' in dot
    assert dot.count('fillcolor=lightgrey') == evmdd.num_nodes() - 1


@pytest.fixture
def recorded_commands(monkeypatch):
    commands = []
    monkeypatch.setattr('evmdd.graphviz.subprocess.run', lambda cmd, check: commands.append(cmd))
    return commands


def test_visualize_on_macos(monkeypatch, recorded_commands, tmp_path):
    monkeypatch.setattr('evmdd.graphviz.platform', 'darwin')
    evmdd, manager = term_to_evmdd('A + B')
    prefix = str(tmp_path / 'evmdd')
    EvmddVisualizer(manager).visualize(evmdd, file_prefix=prefix)
    assert (tmp_path / 'evmdd.dot').read_text() == GraphvizWriter(manager).evmdd_to_gvz(evmdd)
    assert recorded_commands == [
        ['dot', '-Tsvg', '-O', prefix + '.dot'],
        ['open', prefix + '.dot.svg'],
    ]


def test_visualize_on_linux_uses_temporary_file(monkeypatch, recorded_commands):
    monkeypatch.setattr('evmdd.graphviz.platform', 'linux')
    evmdd, manager = term_to_evmdd('A + B')
    EvmddVisualizer(manager).visualize(evmdd)
    [(command, dot_filename)] = recorded_commands
    assert command == 'xdot'
    assert os.path.basename(dot_filename).startswith('evmdd-gvz-')
    with open(dot_filename) as dot_file:
        assert dot_file.read() == GraphvizWriter(manager).evmdd_to_gvz(evmdd)
    os.remove(dot_filename)


def test_visualize_skips_display_if_graphviz_is_missing(monkeypatch, tmp_path, caplog):
    def run(cmd, check):
        raise FileNotFoundError(cmd[0])

    monkeypatch.setattr('evmdd.graphviz.subprocess.run', run)
    monkeypatch.setattr('evmdd.graphviz.platform', 'darwin')
    evmdd, manager = term_to_evmdd('A')
    EvmddVisualizer(manager).visualize(evmdd, file_prefix=str(tmp_path / 'evmdd'))
    assert 'error calling dot' in caplog.text
