# -*- coding: utf-8 -*-

"""setuptools based setup module.
"""

from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyevmdd',
    version='0.1.dev1',
    description='EVMDD Library for Python',
    long_description=long_description,
    url='https://github.com/robertmattmueller/pyevmdd',
    author='Robert Mattmüller',
    author_email='robert@robert-mattmueller.de',
    license='GPLv3+',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
    ],
    keywords='evmdd',
    packages=['evmdd'],
    install_requires=[],
)
