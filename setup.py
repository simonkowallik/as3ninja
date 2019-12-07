#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
from as3ninja import __version__

from setuptools import setup, find_packages

with open("_README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

setup(
    dependency_links=[],
    author="Simon Kowallik",
    author_email="github@simonkowallik.com",
    classifiers=[
        "Natural Language :: English",
        "Intended Audience :: DevOps",
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: ISC License (ISCL)",
    ],
    description="AS3 Ninja is a templating and validation engine for your AS3 declarations providing a CLI and Swagger REST API",
    entry_points={"console_scripts": ["as3ninja=as3ninja.cli:cli"]},
    install_requires=[
        "click==7.0",
        "fastapi==0.44.0",
        "hvac==0.9.6",
        "jinja2==2.10.3",
        "jsonschema==3.2.0",
        "loguru==0.3.2",
        "pydantic==1.2",
        "pyyaml==5.1.2",
        "uvicorn==0.10.8",
    ],
    license="ISC license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="as3ninja",
    name="as3ninja",
    packages=find_packages(include=["as3ninja"]),
    setup_requires=["pytest-runner"],
    test_suite="tests",
    tests_require=["pytest"],
    url="https://github.com/simonkowallik/as3ninja",
    version=__version__,
    zip_safe=False,
)
