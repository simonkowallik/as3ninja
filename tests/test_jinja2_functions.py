# -*- coding: utf-8 -*-
from uuid import UUID

import pytest

from as3ninja.jinja2 import J2Ninja
from as3ninja.jinja2.filterfunctions import *
from as3ninja.jinja2.functions import *


def test_J2Ninja_functions_is_dict():
    assert type(J2Ninja.functions) == dict


class Test_iterfiles:
    @staticmethod
    def test_all_files():
        content_types = {"json": dict, "yaml": dict, "text": str}
        loop_min = 3
        loop_count = 0
        for dirname, filename, fileextension, fcontent in iterfiles(
            "tests/testdata/functions/iterfiles/*/*.*"
        ):
            loop_count += 1
            assert dirname in ("json", "text", "yaml")
            assert filename
            assert fileextension in ("json", "txt", "yaml")
            assert isinstance(fcontent, content_types[dirname])

        assert loop_count >= loop_min

    @staticmethod
    def test_json():
        for dirname, filename, fcontent in iterfiles(
            "tests/testdata/functions/iterfiles/**/*.json"
        ):
            assert dirname in ("json", "json/subdir")
            assert filename
            assert isinstance(fcontent, dict)

    @staticmethod
    def test_nonexistent():
        with pytest.raises(FileNotFoundError):
            for dirname, filename, fcontent in iterfiles("nonexistend/**/*.json"):
                print(dirname)  # this never happens

    @staticmethod
    def test_nonexistent_missing_ok():
        for dirname, filename, fcontent in iterfiles(
            pattern="nonexistend/**/*.json", missing_ok=True
        ):
            print(dirname)  # this never happens


def test_uuid():
    myuuid = uuid()
    assert isinstance(myuuid, str)
    assert isinstance(UUID(myuuid), UUID)
