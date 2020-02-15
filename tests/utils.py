# -*- coding: utf-8 -*-
"""contains utility functions and pytest fixtures for code testing"""

import json
import shutil
from pathlib import Path
from tempfile import mkdtemp
from typing import Union

import pytest

# from tests.utils import *


__all__ = ["format_json", "load_file", "fixture_tmpdir"]


def format_json(jsondata: Union[str, dict]) -> str:
    """formats json based on the formatting defaults of json.dumps"""
    if isinstance(jsondata, str):
        return json.dumps(json.loads(jsondata), sort_keys=True)
    return json.dumps(jsondata, sort_keys=True)


def load_file(filename: str) -> str:
    with open(filename, "r") as f:
        return str(f.read())


@pytest.yield_fixture
def fixture_tmpdir():
    tmpdir = str(mkdtemp(suffix=".ninja.tests"))
    yield tmpdir
    try:
        shutil.rmtree(tmpdir)
    except FileNotFoundError:
        # ignore exception: tests can delete the tmpdir
        pass
