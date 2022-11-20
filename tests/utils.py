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


@pytest.fixture
def fixture_tmpdir():
    tmpdir = str(mkdtemp(suffix=".ninja.tests"))
    yield tmpdir
    try:
        shutil.rmtree(tmpdir)
    except FileNotFoundError:
        # ignore exception: tests can delete the tmpdir
        pass


@pytest.fixture
def fixture_mktmpfile(tmp_path_factory):
    """Fixture to create a temporary file with 'data' as content"""

    def _mktmpfile(data):
        """Fixture to create a temporary file with 'data' as content"""
        fn = tmp_path_factory.mktemp("mktmpfile")
        fn_file = str(fn) + "/file"
        with open(fn_file, "w") as fn_handle:
            fn_handle.write(data)
        return fn_file

    return _mktmpfile


@pytest.fixture
def fixture_recursion_depth_100(scope="function"):
    """
    Temporarily lowers the recursionlimit to 100
    """
    import sys

    sys_recursionlimit = sys.getrecursionlimit()
    sys.setrecursionlimit(100)
    yield
    sys.setrecursionlimit(sys_recursionlimit)
