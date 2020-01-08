#!/usr/bin/env python3

from distutils.core import setup
import setuptools

setup(
    name='kblab-client',
    version='0.0.15a0',
    description='KB lab client',
    author='Martin Malmsten',
    author_email='martin.malmsten@kb.se',
    url="https://github.com/kungbib/kblab",
    install_requires = [
        'requests',
        'pyyaml',
        'lxml',
        'htfile'
    ],
    packages=[ 'kblab' ],
    include_package_data = True
)

