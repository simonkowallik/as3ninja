# -*- coding: utf-8 -*-
import pytest

from as3ninja.utils import deserialize
from tests.utils import fixture_recursion_depth_100


class Test_deserialize_yaml_include:
    @staticmethod
    def test_include_explicit():
        """
        Explicitly include two yaml files returns a list of both
        """
        d = deserialize("tests/testdata/utils/deserialize/explicit.yaml")
        assert isinstance(d["some_namespace"], list)
        assert {"file": "1.yaml"} in d["some_namespace"]
        assert {"file": "2.yaml"} in d["some_namespace"]

    @staticmethod
    def test_include_single_asterisk():
        """
        Test use of single asterisk matching a single file
        """
        d = deserialize("tests/testdata/utils/deserialize/single_2.yaml")
        assert isinstance(d["some_namespace"], dict)
        assert {"file": "2.yaml"} == d["some_namespace"]

    @staticmethod
    def test_include_single_asterisk():
        """
        Test use of single asterisk matching multiple files
        """
        d = deserialize("tests/testdata/utils/deserialize/single_all.yaml")
        assert isinstance(d["some_namespace"], list)
        assert {"file": "2.yaml"} in d["some_namespace"]
        assert {"file": "3.yaml"} in d["some_namespace"]

    @staticmethod
    def test_include_double_asterisk():
        """
        Test Path().glob() functionality using double asterisks returning multiple files (generates a list of deserialized data)
        """
        d = deserialize("tests/testdata/utils/deserialize/double.yaml")
        assert isinstance(d["some_namespace"], list)
        assert {"file": "1.yaml"} in d["some_namespace"]
        assert {"file": "2.yaml"} in d["some_namespace"]
        assert {"file": "3.yaml"} in d["some_namespace"]

    @staticmethod
    def test_include_double_single_result():
        """
        Test double asterisks returning a single result, which doesn't generate a list
        """
        d = deserialize("tests/testdata/utils/deserialize/double_single_result.yaml")
        print(d)
        assert isinstance(d["some_namespace"], dict)
        assert {"file": "2.yaml"} == d["some_namespace"]

    @staticmethod
    def test_include_force_list():
        """
        Force generation of a list
        """
        d = deserialize("tests/testdata/utils/deserialize/force_list.yaml")
        print(d)
        assert isinstance(d["some_namespace"], list)
        assert {"file": "2.yaml"} == d["some_namespace"][0]

    @staticmethod
    def test_include_nested_includes():
        """
        Test nested includes (a includes b includes c)
        """
        d = deserialize("tests/testdata/utils/deserialize/nested/a.yaml")
        print(d)
        assert isinstance(d, dict)
        assert {"a": {"b": {"c": "this is c"}}} == d

    @staticmethod
    def test_include_non_existend_glob():
        """
        When non existing files are included a FileNotFoundError exception should be raised
        """
        with pytest.raises(FileNotFoundError):
            _ = deserialize(
                "tests/testdata/utils/deserialize/non_existend_include.yaml"
            )

    @staticmethod
    def test_include_double_asterisk_incorrect_usage():
        """
        Test Path().glob() functionality using double asterisks incorrectly (incorrect Path.glob pattern syntax)
        """
        with pytest.raises(ValueError):
            _ = deserialize(
                "tests/testdata/utils/deserialize/double_incorrect_usage.yaml"
            )

    @staticmethod
    def test_include_circular(fixture_recursion_depth_100):
        """
        Circular includes end in a RecursionError
        """
        with pytest.raises(RecursionError):
            _ = deserialize(
                "tests/testdata/utils/deserialize/circular_RecursionError.yaml"
            )

    @staticmethod
    def test_include_unsupported_node_type():
        """
        Test for ValueError when yaml node type is unsupported
        """
        with pytest.raises(ValueError):
            _ = deserialize("tests/testdata/utils/deserialize/type_error.yaml")
