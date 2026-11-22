EVMDD Library for Python (pyevmdd)
==================================

The purpose of this small project is to provide a lightweight, pure Python
EVMDD library. It is still in a very early stage of development.

Usage
=====

pyevmdd requires Python 3.10 or newer. After installation, an EVMDD for a
function term can be constructed and visualized (requires
`Graphviz <https://graphviz.org/>`_) from the command line::

    evmdd "A*B*B + C + 2" "A, B, C" "2, 3, 2"

Use ``--dot FILE`` to write the EVMDD in Graphviz/DOT format instead of
displaying it, and ``evmdd --help`` for all options.

Development
===========

Development uses `uv <https://docs.astral.sh/uv/>`_::

    uv run pytest
    uv run ruff check
    uv run ruff format

Copyright
=========

Copyright (C) 2016 Robert Mattmüller

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
