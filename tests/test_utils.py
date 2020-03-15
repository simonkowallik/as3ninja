# -*- coding: utf-8 -*-
from copy import deepcopy

import pytest

from as3ninja.utils import (
    DictLike,
    PathAccessError,
    deserialize,
    dict_filter,
    escape_split,
    failOnException,
)
from tests.utils import fixture_mktmpfile

json_str = """
{
    "key":"value",
    "array": [ "one", 2, "three" ]
}
"""
yaml_str = """
key: value
array:
    - one
    - 2
    - "three"
"""


class Test_deserialize:
    @staticmethod
    def test_json_from_file():
        result = deserialize(
            datasource="tests/testdata/functions/iterfiles/json/file.json"
        )
        assert isinstance(result, dict)

        assert result["key"] == "value"
        assert result["array"][1] == "second"

    @staticmethod
    def test_yaml_from_file():
        result = deserialize(
            datasource="tests/testdata/functions/iterfiles/yaml/file.yaml"
        )
        assert isinstance(result, dict)

        assert result["key"] == "value"
        assert result["array"][1] == "second"

    @staticmethod
    def test_from_text_file_raises_ValueError():
        with pytest.raises(ValueError):
            deserialize(datasource="tests/testdata/functions/iterfiles/text/file.txt")

    @staticmethod
    def test_simple_string():
        with pytest.raises(FileNotFoundError):
            deserialize(datasource="does/not/exist.file")

    @staticmethod
    def test_yaml_scanner_error(fixture_mktmpfile):
        not_yaml_file = fixture_mktmpfile(
            data="""
        when not_yaml {
        yaml: false
        }
        """
        )

        with pytest.raises(ValueError):
            deserialize(datasource=not_yaml_file)


class Test_DictLike:
    class DLTest(DictLike):
        def __init__(self, configuration: dict):
            self._dict = deepcopy(configuration)

    dltest_data = {"key1": {"dict": True, "numbers": [1, 2, 3]}, "key2": "string"}
    dltest_instance = DLTest(dltest_data)

    def test_dict_items(self):
        assert self.dltest_instance.items() == self.dltest_data.items()

    def test_dict_values(self):
        assert str(self.dltest_instance.values()) == str(self.dltest_data.values())

    def test_dict_keys(self):
        assert self.dltest_instance.keys() == self.dltest_data.keys()

    def test_dict_get(self):
        assert self.dltest_instance.get("key1") == self.dltest_data.get("key1")

    def test_dict_get_missing(self):
        assert self.dltest_instance.get("MissingKey") == self.dltest_data.get(
            "MissingKey"
        )

    def test_dunder_str(self):
        assert str(self.dltest_instance) == str(self.dltest_data)

    def test_dunder_repr(self):
        DLTest = self.DLTest
        assert eval(repr(self.dltest_instance)) == DLTest(self.dltest_data)

    def test_dunder_getitem(self):
        assert self.dltest_instance.__getitem__("key1") == self.dltest_data.__getitem__(
            "key1"
        )

    def test_dunder_eq(self):
        assert dict(self.dltest_instance) == self.dltest_data

    def test_dunder_contains(self):
        assert "key1" in self.dltest_instance
        assert "key2" in self.dltest_instance
        assert not "MissingKey" in self.dltest_instance

    def test_dunder_len(self):
        assert len(self.dltest_instance) == 2

    def test_dunder_iter(self):

        keylist = list(self.dltest_instance.keys())

        for key in self.dltest_instance:
            assert key == keylist.pop(keylist.index(key))
        assert len(keylist) == 0


class Test_failOnException:
    @staticmethod
    def test_fail():
        @failOnException
        def throw_exception():
            raise ValueError("raises ValueError")

        with pytest.raises(SystemExit) as exc_info:
            throw_exception()
        assert exc_info.type == SystemExit
        assert exc_info.value.code == 1


class Test_escape_split:
    @staticmethod
    def test_simple():
        test_string = "foo.bar.baz"
        result = escape_split(test_string)
        assert isinstance(result, tuple)
        assert result == ("foo", "bar", "baz")

    @pytest.mark.parametrize(
        "test_string,expected_result",
        [
            (r"foo\.bar.baz", ("foo.bar", "baz")),
            (r"foo\\.bar.baz", ("foo\\", "bar", "baz")),
            (r"foo\\\.bar.baz", ("foo\\.bar", "baz")),
        ],
    )
    def test_escaped(self, test_string, expected_result):
        result = escape_split(test_string)
        assert isinstance(result, tuple)


class Test_dict_filter:

    test_dict = {
        "data": {
            "key": "value",
            "k.e.y": "v.a.l.u.e",
            "data": {"key1": "value1", "list": [1, 2, 3, "one", "two", "three"],},
        }
    }

    @pytest.mark.parametrize(
        "test_filter,expected_result",
        [
            ("data.key", "value"),
            (r"data.k\.e\.y", "v.a.l.u.e"),
            ("data.data.key1", "value1"),
            ("data.data.list", [1, 2, 3, "one", "two", "three"]),
        ],
    )
    def test_str_tuple(self, test_filter, expected_result):
        assert dict_filter(self.test_dict, filter=test_filter) == expected_result
        # test with a tuple as filter
        assert (
            dict_filter(self.test_dict, filter=escape_split(test_filter))
            == expected_result
        )

    def test_empty_filter(self):
        assert dict_filter(self.test_dict, filter="") == self.test_dict

    def test_none_filter(self):
        assert dict_filter(self.test_dict, filter=None) == self.test_dict

    def test_list_position(self):
        assert dict_filter({"data": [0, "one"]}, filter="data.1") == "one"

    def test_fail_incorrect_filter(self):
        with pytest.raises(PathAccessError):
            dict_filter(self.test_dict, filter="data.DOESNOTEXIST")

    def test_fail_incorrect_type(self):
        with pytest.raises(PathAccessError):
            dict_filter({"data": 1}, filter="data.key")


class Test_PathAccessError:
    @staticmethod
    def test_raise_PathAccessError():
        with pytest.raises(PathAccessError):
            exc = PathAccessError(TypeError("type error"), "segment", "filter")
            assert repr(exc) == "PathAccessError(type error, segment, filter)"
            assert isinstance(str(exc), str)
            assert (
                str(exc)
                == "could not access segment from path filter, got error: type error"
            )
            raise exc
