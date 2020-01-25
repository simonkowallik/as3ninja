import runpy

import pytest


def test_main(mocker):
    """test as3ninja calls cli() on __main__"""
    mocked_cli = mocker.patch("as3ninja.cli.cli")
    runpy.run_module("as3ninja", run_name="__main__")
    assert mocked_cli.called is True
