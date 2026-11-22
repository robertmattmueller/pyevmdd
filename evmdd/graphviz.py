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
Graphviz output and display of |EVMDDs|.
"""

import logging
import os
import subprocess
import tempfile
from itertools import groupby
from operator import attrgetter
from sys import platform


class GraphvizWriter(object):
    """Helper class that writes |EVMDDs| to strings in Graphviz/DOT format."""

    _root_node_gvz_tmpl = '%s [style=invis];'
    _var_node_gvz_tmpl = '%s [style=filled,fillcolor=lightgrey,label="%s"];'
    _sink_node_gvz_tmpl = '%s [shape=box,height=0.25,width=0.5,rank=sink,label="0"];'
    _weight_node_gvz_tmpl = '%s [shape=box,height=0.25,width=0.5,label="%+d"];'

    _var_to_weight_edge_gvz_tmpl = '%s -> %s [arrowhead=none, label="%s"];'
    _weight_to_var_edge_gvz_tmpl = '%s -> %s;'

    _var_node_name_tmpl = '"s%s[level=%s]"'
    _weight_node_name_tmpl = '"s%s[level=%s]=%s"'

    def __init__(self, manager):
        self._manager = manager
        self._index = None

    def _root_node_gvz(self, var_node_name):
        return self._root_node_gvz_tmpl % var_node_name

    def _var_node_gvz(self, var_node_name, var_name):
        return self._var_node_gvz_tmpl % (var_node_name, var_name)

    def _sink_node_gvz(self, var_node_name):
        return self._sink_node_gvz_tmpl % var_node_name

    def _weight_node_gvz(self, weight_node_name, weight):
        return self._weight_node_gvz_tmpl % (weight_node_name, weight)

    def _var_to_weight_edge_gvz(self, var_node_name, weight_node_name, domain_idx):
        return self._var_to_weight_edge_gvz_tmpl % (var_node_name, weight_node_name, domain_idx)

    def _weight_to_var_edge_gvz(self, weight_node_name, succ_var_node_name):
        return self._weight_to_var_edge_gvz_tmpl % (weight_node_name, succ_var_node_name)

    def _var_node_name(self, node):
        return self._var_node_name_tmpl % (self._index[node], node.level)

    def _weight_node_name(self, node, domain_idx):
        return self._weight_node_name_tmpl % (self._index[node], node.level, domain_idx)

    def _root_edge_to_gvz(self, evmdd):
        var_node_name = 'dummyNode'
        weight_node_name = 'constantWeight'
        var_node = self._root_node_gvz(var_node_name)
        weight_node = self._weight_node_gvz(weight_node_name, evmdd.weight)
        var_to_weight_edge = self._var_to_weight_edge_gvz(var_node_name, weight_node_name, '')
        succ_var_node_name = self._var_node_name(evmdd.succ)
        weight_to_var_edge = self._weight_to_var_edge_gvz(weight_node_name, succ_var_node_name)
        return [var_node, weight_node, var_to_weight_edge, weight_to_var_edge]

    def _node_to_gvz(self, node):
        var_node_name = self._var_node_name(node)
        if node.is_sink_node():
            return [self._sink_node_gvz(var_node_name)]
        var_name = self._manager.var_name_of(node)
        var_node = self._var_node_gvz(var_node_name, var_name)
        result = [var_node]
        for domain_idx, child in enumerate(node.children):
            weight_node_name = self._weight_node_name(node, domain_idx)
            weight_node = self._weight_node_gvz(weight_node_name, child.weight)
            var_to_weight_edge = self._var_to_weight_edge_gvz(
                var_node_name, weight_node_name, domain_idx
            )
            succ_var_node_name = self._var_node_name(child.succ)
            weight_to_var_edge = self._weight_to_var_edge_gvz(weight_node_name, succ_var_node_name)
            result.extend([weight_node, var_to_weight_edge, weight_to_var_edge])
        return result

    def _node_rank_to_gvz(self, rank):
        rank = ';'.join([self._var_node_name(node) for node in rank])
        return '{rank = same; %s;}' % rank

    def evmdd_to_gvz(self, evmdd):
        """Translate a given |EVMDD| to Graphviz format.

        Args:
            evmdd (Edge): an |EVMDD|.

        Returns:
            `string`: an encoding of the |EVMDD| in Graphviz/DOT format.
        """
        nodes = evmdd.nodes()
        sorting_fn = attrgetter('level')
        nodes = sorted(nodes, key=sorting_fn)

        self._index = {node: idx for idx, node in enumerate(nodes)}
        lines = ['digraph G {']
        lines.extend(self._root_edge_to_gvz(evmdd))
        for node in nodes:
            lines.extend(self._node_to_gvz(node))
        for _, group in groupby(nodes, key=sorting_fn):
            lines.append(self._node_rank_to_gvz(group))
        lines.extend(['}'])
        return '\n'.join(lines)


class EvmddVisualizer(object):
    """Helper class that displays |EVMDDs| on the screen."""

    def __init__(self, manager):
        self._gvz_writer = GraphvizWriter(manager)

    def _encode_in_gvz_format(self, evmdd):
        return self._gvz_writer.evmdd_to_gvz(evmdd)

    def _run(self, cmd):
        """Run an external command. Return true iff it succeeded."""
        try:
            subprocess.run(cmd, check=True)
        except (OSError, subprocess.CalledProcessError) as e:
            logging.error('Skipped EVMDD visualization due to error calling %s: %s', cmd[0], e)
            return False
        return True

    def visualize(self, evmdd, file_prefix=None):
        """Visualize a given |EVMDD|.

        The given |EVMDD| is first exported in Graphviz/DOT syntax and
        written to a DOT file. Then, depending on the OS, the DOT file is
        either displayed using `xdot` (under Linux), or converted to SVG
        using `dot` and subsequently opened in the default SVG viewer
        (under macOS).

        In both cases, we assume that Graphviz is installed.

        Notice that generated DOT/SVG files are not deleted after visualization.

        Args:
            `evmdd` (Edge): the |EVMDD| to be visualized.

            `file_prefix` (string, optional): path and file name of dot file to
            write to, without the ``.dot`` extension (a new temporary file
            ``evmdd-gvz-*.dot`` by default)

        Returns:
            `None`

        Side effect:
            visualization of the given |EVMDD|.
        """
        if file_prefix:
            dot_filename = file_prefix + '.dot'
        else:
            fd, dot_filename = tempfile.mkstemp(prefix='evmdd-gvz-', suffix='.dot')
            os.close(fd)
        svg_filename = dot_filename + '.svg'
        gvz = self._encode_in_gvz_format(evmdd)
        try:
            with open(dot_filename, 'w') as dot_file:
                dot_file.write(gvz)
        except OSError as e:
            logging.error('EVMDD visualization failed. Could not write to %s: %s', dot_filename, e)
            return
        if platform == 'darwin':
            if self._run(['dot', '-Tsvg', '-O', dot_filename]):
                self._run(['open', svg_filename])
        else:
            self._run(['xdot', dot_filename])
