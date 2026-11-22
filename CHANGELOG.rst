Change Log
==========

All notable changes to this project will be documented in this file.

[Unreleased]
------------

Added
~~~~~

* Exponentiation with nonnegative integer exponents (``**``).
* ``evmdd`` command line tool (also ``python -m evmdd``) with options
  ``--dot FILE`` and ``--quasi-reduced``.
* Type annotations (checked with mypy, PEP 561 ``py.typed`` marker).
* Test suite (pytest), linting and formatting (ruff), and CI on
  GitHub Actions for Python 3.10 to 3.14.

Changed
~~~~~~~

* Requires Python 3.10 or newer. Packaging via ``pyproject.toml``.
* Invalid input raises ``ValueError`` (or ``TypeError`` for unsupported
  operand types) with a descriptive message instead of failing
  assertions.
* ``term_to_evmdd`` takes keyword-only arguments ``var_names``,
  ``var_domains``, and ``fully_reduced`` instead of ``**kwargs``.
* Non-integer constants in function terms are rejected instead of being
  truncated.
* ``Edge`` and ``Node`` are regular classes with unique instances
  (hash-consing); equality is object identity. Unused EVMDDs are
  garbage collected.
* Much faster EVMDD construction thanks to a cache in ``apply`` and
  O(1) uniqueness checks.
* Visualization uses a proper temporary file and the default SVG viewer
  on macOS.
* ``__all__`` lists the names exported by the package.

Fixed
~~~~~

* Parsing of terms with numbers on Python 3.8+, and importing the
  package on Python 3.14.
* Exponential running time of ``nodes()``, ``num_nodes()``,
  ``num_edges()`` and the Graphviz output for EVMDDs with shared
  sub-EVMDDs.
* Visualization no longer calls Graphviz when the DOT file could not be
  written.
* Quasi-reduced EVMDDs now branch over all variables of the ordering,
  including variables that do not occur in the term. Previously, such
  levels were skipped, and ``evaluate`` failed with an ``AssertionError``.

Removed
~~~~~~~

* ``evmdd_script.py`` (replaced by the ``evmdd`` command).
* ``evmdd.util`` module (``memoize``, ``EqualityMixin``).
* ``setup.py`` and ``setup.cfg``.

[v0.1] - 2016-01-07
-------------------

Added
~~~~~

* Internal EVMDD representation.
* EVMDD output as a `Graphviz <http://www.graphviz.org/>`_ file plus
  visualization.
* Function evaluation.
* Arithmetic operations addition, subtraction, unary
  negation, and multiplication on EVMDDs.
* Choice between fully reduced and quasi-reduced EVMDDs.
* Input of arithmetic functions in Python syntax.
