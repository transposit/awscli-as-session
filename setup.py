#!/usr/bin/env python

from setuptools import setup

requires = ['awscli>=1.14.0']

setup(
    name='awscli-as-session',
    packages=['awscli_as_session'],
    version='0.3',
    description='aws-cli plugin that invokes commands with creds set',
    long_description=open('README.md').read(),
    author='Transposit',
    url='https://github.com/transposit/awscli-as-session',
    keywords=['awscli', 'plugin', 'terraform'],
    install_requires=requires
)
