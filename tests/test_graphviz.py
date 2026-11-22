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

from evmdd import GraphvizWriter, term_to_evmdd


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
    evmdd, manager = term_to_evmdd('A*B**2 + C + 2', var_names=['A', 'B', 'C'],
                                   var_domains={'A': 2, 'B': 3, 'C': 2})
    dot = GraphvizWriter(manager).evmdd_to_gvz(evmdd)
    for var_name in ['A', 'B', 'C']:
        assert 'label="%s"' % var_name in dot
    assert dot.count('fillcolor=lightgrey') == evmdd.num_nodes() - 1
