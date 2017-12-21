# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='h1theswan_utils',
    version='0.1.0',
    description='Personal utilities',
    long_description=readme,
    author='Jason Portenoy',
    author_email='jason.portenoy@gmail.com',
    url='https://github.com/h1-the-swan/h1theswan_utils',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=['pandas', 'numpy']
)

