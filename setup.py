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
        "Development Status :: 3 - Alpha",
        "Intended Audience :: DevOps",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="AS3 Ninja contains all the boilerplate you need to create a Python package.",
    entry_points={"console_scripts": ["as3ninja=as3ninja.cli:cli"]},
    install_requires=[
        "aiofiles==0.4.0",
        "aniso8601==7.0.0",
        "async-exit-stack==1.0.1",
        "async-generator==1.10",
        "attrs==19.3.0",
        "certifi==2019.9.11",
        "chardet==3.0.4",
        "click==7.0",
        "dnspython==1.16.0",
        "email-validator==1.0.5",
        "fastapi==0.42.0",
        "graphene==2.1.8",
        "graphql-core==2.2.1",
        "graphql-relay==2.0.0",
        "h11==0.8.1",
        "httptools==0.0.13",
        "hvac==0.9.5",
        "idna==2.8",
        "importlib-metadata==0.23",
        "itsdangerous==1.1.0",
        "jinja2==2.10.3",
        "jsonschema==3.1.1",
        "loguru==0.3.2",
        "markupsafe==1.1.1",
        "more-itertools==7.2.0",
        "promise==2.2.1",
        "pydantic==0.32.2",
        "pyrsistent==0.15.5",
        "python-multipart==0.0.5",
        "pyyaml==5.1.2",
        "requests==2.22.0",
        "rx==1.6.1",
        "six==1.12.0",
        "starlette==0.12.9",
        "ujson==1.35",
        "urllib3==1.25.6",
        "uvicorn==0.10.3",
        "uvloop==0.14.0rc2",
        "websockets==8.1",
        "zipp==0.6.0",
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
