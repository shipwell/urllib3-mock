#!/usr/bin/env python
"""
urllib3-mock
============

A utility library for mocking out the `urllib3` Python library.
This is an adaptation of the `responses` library.

:copyright: (c) 2015 Florent Xicluna
:copyright: (c) 2015 David Cramer
:license: Apache 2.0
"""

from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys


with open('README.rst') as f:
    long_description = f.read()

setup_requires = []

if 'test' in sys.argv:
    setup_requires.append('pytest')

install_requires = []
if sys.version_info < (3, 3):
    install_requires.append('mock')
# Also required: 'urllib3' or 'requests'

tests_require = [
    'pytest',
    'pytest-cov',
    'flake8',
    'requests',
]


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['test_urllib3_mock.py']
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='urllib3-mock',
    version='0.3.3',
    author='Florent Xicluna',
    author_email='florent.xicluna@gmail.com',
    url='https://github.com/florentx/urllib3-mock',
    description=(
        'A utility library for mocking out the `urllib3` Python library.'
    ),
    license='Apache 2.0',
    long_description=long_description,
    py_modules=['urllib3_mock'],
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'tests': tests_require,
    },
    tests_require=tests_require,
    setup_requires=setup_requires,
    cmdclass={'test': PyTest},
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
)
