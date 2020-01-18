# -*- coding: utf-8 -*-
from copy import deepcopy

import pytest

from as3ninja.utils import DictLike, deserialize

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
    def test_json():
        result = deserialize(datasource=json_str)
        assert isinstance(result, dict)

        assert result["key"] == "value"

        assert isinstance(result["array"][1], int)
        assert result["array"][1] == 2

    @staticmethod
    @pytest.mark.xfail
    def test_json_as_str():
        # TODO: fix test - see deserialize utils for more details
        # deserialze should not be used to read data from a str and return it as a str if the first isnt a file
        result = deserialize(datasource=json_str, return_as=str)
        assert isinstance(result, str)
        assert result == json_str

    @staticmethod
    def test_yaml():
        result = deserialize(datasource=yaml_str)
        assert isinstance(result, dict)

        assert result["key"] == "value"

        assert isinstance(result["array"][1], int)
        assert result["array"][1] == 2

    @staticmethod
    @pytest.mark.xfail
    def test_yaml_as_str():
        # TODO: fix test - see deserialize utils for more details
        # deserialze should not be used to read data from a str and return it as a str if the first isnt a file
        result = deserialize(datasource=yaml_str, return_as=str)
        assert isinstance(result, str)
        assert result == yaml_str

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
    def test_str_from_file():
        result = deserialize(
            datasource="tests/testdata/functions/iterfiles/text/file.txt", return_as=str
        )
        assert isinstance(result, str)

    @staticmethod
    def test_from_text_file_raises_ValueError():
        with pytest.raises(ValueError):
            deserialize(datasource="tests/testdata/functions/iterfiles/text/file.txt")

    @staticmethod
    def test_non_standard_json():
        non_standard_json = "{ key: value,\n array:[one, 2, three] }"
        result = deserialize(datasource=non_standard_json)

        assert isinstance(result, dict)

        assert result["key"] == "value"

        assert isinstance(result["array"][1], int)
        assert result["array"][1] == 2

    @staticmethod
    def test_simple_string():
        with pytest.raises(ValueError):
            deserialize(datasource="simple string")

    @staticmethod
    def test_multiline_string():
        multiline_string = """this is just a
        multi line
        string
        """
        with pytest.raises(ValueError):
            deserialize(datasource=multiline_string)

    @staticmethod
    def test_not_yaml_not_json():
        not_yaml_not_json = """
        {
        key: value
        array:
            - one
            - 2
            - "three"
        }
        """
        with pytest.raises(ValueError):
            deserialize(datasource=not_yaml_not_json)

    @staticmethod
    def test_yaml_scanner_error():
        not_yaml = """
        when not_yaml {
        yaml: false
        }
        """
        with pytest.raises(ValueError):
            deserialize(datasource=not_yaml)


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
