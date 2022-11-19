import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from as3ninja.exceptions import AS3TemplateConfigurationError
from as3ninja.templateconfiguration import AS3TemplateConfiguration

from .utils import format_json


class Test_TemplateConfigurationValidator:
    @pytest.mark.parametrize(
        "test_data",
        [
            [{"d1_k1": 1, "d1_k2": 2}, {"d2_k1": 3, "d2_k2": 4}],
            ["str1", "str2"],
            [{"DictInList": 1}, "StrInList"],
            {"SingeDict": 1, "a": "a"},
            "SingleStr",
        ],
    )
    def test_allowed_input(self, test_data):
        """test allowed input formats and types"""
        result = AS3TemplateConfiguration.TemplateConfigurationValidator(
            template_configuration=test_data
        )
        assert result.template_configuration == test_data


class Test_AS3TemplateConfiguration_interface:
    @staticmethod
    def test_dict():
        """expect .dict() to return dict.
        expect it to be equal to data"""
        data = {"config": True}
        as3tc = AS3TemplateConfiguration(data)

        assert isinstance(as3tc.dict(), dict)
        assert as3tc.dict() == data
        assert dict(as3tc) == data

    @staticmethod
    def test_json():
        """exepct .json() to return str.
        expect return value to be equal to data.
        expect _configuration_json to be equal to data.
        """
        data = {"config": True}
        as3tc = AS3TemplateConfiguration(data)

        assert isinstance(as3tc.json(), str)
        assert format_json(as3tc.json()) == format_json(data)

    @staticmethod
    def test_api_input1():
        """Test input similar to what the API could see."""
        JSON = """
        {
            "template_configuration": [
                {"inline_json": true},
                "tests/testdata/AS3TemplateConfiguration/file.json",
                {"as3ninja": {
                    "include": "tests/testdata/AS3TemplateConfiguration/included2a.yaml"
                    }
                }
            ]
        }
        """
        data = json.loads(JSON)

        as3tc = AS3TemplateConfiguration(**data)

        assert as3tc.dict()["inline_json"] is True
        assert as3tc.dict()["file.json"] is True
        assert as3tc.dict()["included2a.yaml"] is True
        # 'tests/testdata/AS3TemplateConfiguration/file.json' will be deserialized instead of added to as3ninja.include
        assert as3tc.dict()["as3ninja"]["include"] == [
            "tests/testdata/AS3TemplateConfiguration/included2a.yaml"
        ]

    @staticmethod
    def test_api_input_globbing():
        """Test input similar to what the API could see."""
        JSON = """
        {
            "template_configuration": [
                {"inline_json": true},
                "tests/testdata/AS3TemplateConfiguration/file.*",
                {"as3ninja": {
                    "include": "tests/testdata/AS3TemplateConfiguration/included2a.yaml"
                    }
                }
            ]
        }
        """
        data = json.loads(JSON)

        as3tc = AS3TemplateConfiguration(**data)

        assert as3tc.dict()["inline_json"] is True
        assert as3tc.dict()["file.yaml"] is True
        assert as3tc.dict()["file.json"] is True
        assert as3tc.dict()["included2a.yaml"] is True
        assert as3tc.dict()["as3ninja"]["include"] == [
            "tests/testdata/AS3TemplateConfiguration/included2a.yaml"
        ]

    @staticmethod
    def test_api_input_globbing_includes():
        """Test complex input similar to what the API could see."""
        JSON = """
        {
            "template_configuration": [
                {"inline_json": true},
                "tests/testdata/AS3TemplateConfiguration/file.*",
                "tests/testdata/AS3TemplateConfiguration/include3.yaml",
                {"as3ninja": {
                    "include": "tests/testdata/AS3TemplateConfiguration/include2.yaml"
                    }
                },
                "tests/testdata/AS3TemplateConfiguration/include1.yaml",
                "tests/testdata/AS3TemplateConfiguration/include3.yaml"
            ]
        }
        """
        data = json.loads(JSON)

        as3tc = AS3TemplateConfiguration(**data)

        assert (
            as3tc.dict()["inline_json"] is True
        )  # inline json is part of the configuration
        assert as3tc.dict()["file.yaml"] is True  # file.* globbing includes file.yaml
        assert as3tc.dict()["file.json"] is True  # file.* globbing includes file.json
        assert (
            as3tc.dict()["include3.yaml"] is True
        )  # include3.yaml is part of the configuration
        assert (
            as3tc.dict()["included3.yaml"] is True
        )  # included3.yaml is included by include3.yaml

        assert (
            as3tc.dict()["include2.yaml"] is True
        )  # include2.yaml is part of the configuration but CANNOT include further files!
        # {"as3ninja": {"include": "../include2.yaml"}} is an include already and cannot
        # include further files:
        assert (
            as3tc.dict().get("included2a.yaml", False) is False
        )  # nested includes are not supported
        assert (
            as3tc.dict().get("included2b.yaml", False) is False
        )  # nested includes are not supported
        assert (
            as3tc.dict().get("included2c.yaml", False) is False
        )  # nested includes are not supported

        assert (
            as3tc.dict()["include1.yaml"] is True
        )  # include1.yaml is part of the configuration
        assert (
            as3tc.dict()["included1.yaml"] is True
        )  # included1.yaml is included by include1.yaml and part of the configuration

        assert (
            as3tc.dict()["data"] == "include3.yaml"
        )  # include3.yaml is the last included configuration, it does include further files
        # but these files have been included before, hence they are not included again

        # includes in perserved order
        assert as3tc.dict()["as3ninja"]["include"] == [
            "tests/testdata/AS3TemplateConfiguration/included3.yaml",
            "tests/testdata/AS3TemplateConfiguration/include2.yaml",
            "tests/testdata/AS3TemplateConfiguration/included1.yaml",
        ]

    @staticmethod
    def test_api_input_path_prefix():
        """Test complex input similar to what the API could see with path_prefix.
        Test with ugly but technically correct paths.
        """
        JSON = """
        {
            "template_configuration": [
                {"inline_json": true},
                "////./AS3TemplateConfiguration/file.*",
                {"as3ninja": {
                    "include": "././//./AS3TemplateConfiguration/include2.yaml"
                    }
                },
                "AS3TemplateConfiguration/include1_relativePath.yaml"
            ],
            "base_path": "tests/testdata/"
        }
        """
        data = json.loads(JSON)

        as3tc = AS3TemplateConfiguration(**data)

        assert as3tc.dict() == {
            "inline_json": True,
            "as3ninja": {
                "include": [
                    "tests/testdata/AS3TemplateConfiguration/include2.yaml",
                    "tests/testdata/AS3TemplateConfiguration/included1.yaml",
                ]
            },
            "file.json": True,
            "content": {"jsonList": ["A", "B", "C"], "yamlList": ["a", "b", "c"]},
            "file.yaml": True,
            "include2.yaml": True,
            "data": "included1.yaml",
            "include1_relativePath.yaml": True,
            "included1.yaml": True,
        }

    @staticmethod
    def test_repr_not_supported():
        """Test complex input with repr(). Due to the include handling repr() will not reproduce the same results!"""
        data = {
            "template_configuration": [
                {"inline_json": True},
                "tests/testdata/AS3TemplateConfiguration/file.*",
                "tests/testdata/AS3TemplateConfiguration/include3.yaml",
                {
                    "as3ninja": {
                        "include": "tests/testdata/AS3TemplateConfiguration/include2.yaml"
                    }
                },
                "tests/testdata/AS3TemplateConfiguration/include1.yaml",
                "tests/testdata/AS3TemplateConfiguration/include3.yaml",
            ]
        }

        as3tc = AS3TemplateConfiguration(**data)

        assert as3tc != eval(repr(as3tc))

    @staticmethod
    def test_absolute_file_glob():
        """Test that absolute file paths work"""
        data = {
            "template_configuration": [
                f"{Path.cwd()}/tests/testdata/AS3TemplateConfiguration/include1.*",
            ]
        }

        as3tc = AS3TemplateConfiguration(**data)

        assert "included1.yaml" in as3tc.dict()

    @staticmethod
    def test_overlay():
        """Test"""
        data = [
            "tests/testdata/AS3TemplateConfiguration/include1.yaml",
            {"inline": True, "overlay": False},
        ]

        as3tc = AS3TemplateConfiguration(
            template_configuration=data, overlay={"overlay": True}
        )

        assert "included1.yaml" in as3tc.dict()
        assert as3tc.dict()["inline"] is True
        assert as3tc.dict()["overlay"] is True


class Test_AS3TemplateConfiguration_include:
    @staticmethod
    def test_include2():
        """expected include order: included2b.yaml, included2a.yaml, included2c.yaml"""
        data = [
            {"first_config": True, "as3ninja": {"first_config": True}},
            "tests/testdata/AS3TemplateConfiguration/include2.yaml",
            {"last_config": True, "as3ninja": {"last_config": True}},
        ]
        expected_include_order = [
            "tests/testdata/AS3TemplateConfiguration/included2b.yaml",
            "tests/testdata/AS3TemplateConfiguration/included2a.yaml",
            "tests/testdata/AS3TemplateConfiguration/included2c.yaml",
        ]

        tc = AS3TemplateConfiguration(data)

        assert tc.dict()["as3ninja"]["include"] == expected_include_order
        assert tc.dict()["data"] == "included2c.yaml"
        assert "first_config" in tc.dict()["as3ninja"]
        assert "last_config" in tc.dict()["as3ninja"]

    @staticmethod
    def test_include1():
        data = [
            {"first_config": True, "as3ninja": {"first_config": True}},
            "tests/testdata/AS3TemplateConfiguration/include1.yaml",
            {"last_config": True, "as3ninja": {"last_config": True}},
        ]
        expected_includes = ["tests/testdata/AS3TemplateConfiguration/included1.yaml"]

        tc = AS3TemplateConfiguration(data)

        assert tc.dict()["as3ninja"]["include"] == expected_includes
        assert tc.dict()["data"] == "included1.yaml"
        assert "first_config" in tc.dict()["as3ninja"]
        assert "last_config" in tc.dict()["as3ninja"]

    @staticmethod
    def test_include3():
        """assure non-recursive includes.
        include3.yaml includes included3.yaml which again has includes.
        These includes in included3.yaml MUST be ignored."""
        data = [
            {"first_config": True, "as3ninja": {"first_config": True}},
            "tests/testdata/AS3TemplateConfiguration/include3.yaml",
            {"last_config": True, "as3ninja": {"last_config": True}},
        ]
        expected_include_order = [
            "tests/testdata/AS3TemplateConfiguration/included3.yaml"
        ]

        tc = AS3TemplateConfiguration(data)

        assert tc.dict()["as3ninja"]["include"] == expected_include_order
        assert tc.dict()["data"] == "included3.yaml"
        assert "first_config" in tc.dict()["as3ninja"]
        assert "last_config" in tc.dict()["as3ninja"]

    @staticmethod
    def test_multi():
        data = [
            {"first_config": True, "as3ninja": {"first_config": True}},
            "tests/testdata/AS3TemplateConfiguration/include1.yaml",
            "tests/testdata/AS3TemplateConfiguration/include2.yaml",
            "tests/testdata/AS3TemplateConfiguration/include3.yaml",
            {"last_config": True, "as3ninja": {"last_config": True}},
        ]
        expected_include_order = [
            "tests/testdata/AS3TemplateConfiguration/included1.yaml",
            "tests/testdata/AS3TemplateConfiguration/included2b.yaml",
            "tests/testdata/AS3TemplateConfiguration/included2a.yaml",
            "tests/testdata/AS3TemplateConfiguration/included2c.yaml",
            "tests/testdata/AS3TemplateConfiguration/included3.yaml",
        ]

        tc = AS3TemplateConfiguration(data)

        assert tc.dict()["as3ninja"]["include"] == expected_include_order
        assert tc.dict()["data"] == "included3.yaml"
        assert "first_config" in tc.dict()["as3ninja"]
        assert "last_config" in tc.dict()["as3ninja"]

    @staticmethod
    def test_explicit_nonexisting_include():
        nonexisting_file_name = (
            "tests/testdata/AS3TemplateConfiguration/DOESNOTEXIST.yaml"
        )
        data = [
            {"as3ninja": {"include": nonexisting_file_name}},
        ]

        with pytest.raises(AS3TemplateConfigurationError) as excInfo:
            AS3TemplateConfiguration(data)

        assert nonexisting_file_name in str(excInfo.value)

    @staticmethod
    def test_glob_nonexisting_include():
        nonexisting_file_name = (
            "tests/testdata/AS3TemplateConfiguration/DOESNOTEXIST*.yaml"
        )
        data = [
            {"as3ninja": {"include": nonexisting_file_name}},
        ]

        with pytest.raises(AS3TemplateConfigurationError) as excInfo:
            AS3TemplateConfiguration(data)

        assert nonexisting_file_name in str(excInfo.value)

    @staticmethod
    def test_nonfile_include():
        # directory != file
        nonexisting_file_name = "tests/testdata/AS3TemplateConfiguration"
        data = [
            {"as3ninja": {"include": nonexisting_file_name}},
        ]

        with pytest.raises(AS3TemplateConfigurationError) as excInfo:
            AS3TemplateConfiguration(data)

        assert nonexisting_file_name in str(excInfo.value)


class Test_AS3TemplateConfiguration_ninja_configfile:
    @staticmethod
    def test_nofile():
        """No configuration given, must load ninja.(json|yaml|yml) which doesnt exist"""
        with pytest.raises(AS3TemplateConfigurationError) as excInfo:
            AS3TemplateConfiguration(None)

        assert "No AS3 Ninja configuration file found" in str(excInfo.value)

    @staticmethod
    def test_ninja_yaml(mocker):
        """./ninja.yaml exists"""
        #                                           ninja.json, ninja.yaml, ninja.yml
        from pathlib import Path

        mocked_Path = mocker.MagicMock(**{"is_file.side_effect": [False, True, False]})

        mocked_Path.return_value = mocked_Path
        mocker.patch("as3ninja.templateconfiguration.Path", new=mocked_Path)

        # mock _deserialize_includes to prevent actual de-serialization of non-exiting / mocked files
        mocker.patch(
            "as3ninja.templateconfiguration.AS3TemplateConfiguration._deserialize_includes"
        )

        AS3TemplateConfiguration(None)

        # stops at 2nd call, as ninja.yaml is found
        assert mocked_Path.mock_calls == [
            mocker.call("ninja.json"),
            mocker.call.is_file(),
            mocker.call("ninja.yaml"),
            mocker.call.is_file(),
        ]
        assert mocked_Path.call_count == 2

    @staticmethod
    def test_ninja_all(mocker):
        """./ninja.json, ./ninja.yaml, ./ninja.yml exists but ./ninja.json is used"""
        #                                           ninja.json, ninja.yaml, ninja.yml
        mocked_Path = mocker.MagicMock(**{"is_file.side_effect": [True, True, True]})
        mocked_Path.return_value = mocked_Path
        mocker.patch("as3ninja.templateconfiguration.Path", new=mocked_Path)

        # mock _deserialize_includes to prevent actual de-serialization of non-exiting / mocked files
        mocker.patch(
            "as3ninja.templateconfiguration.AS3TemplateConfiguration._deserialize_includes"
        )

        AS3TemplateConfiguration(None)

        # stops at 2nd call, as ninja.yaml is found
        assert mocked_Path.mock_calls == [
            mocker.call("ninja.json"),
            mocker.call.is_file(),
        ]
        assert mocked_Path.call_count == 1


class Test__dict_deep_update:
    @staticmethod
    def test_simple():
        dict_to_update = {"a": {"a": 1}}
        update = {"b": {"b": 1}, "a": {"b": 1}}
        expected_result = {"a": {"a": 1, "b": 1}, "b": {"b": 1}}
        result = AS3TemplateConfiguration({})._dict_deep_update(
            dict_to_update=dict_to_update, update=update
        )
        assert result == expected_result

    @staticmethod
    def test_nested():
        dict_to_update = {"a": {"a": 1}}
        update = {"b": {"b": 1}, "a": {"b": 1, "a": {"updated_by_b": 1}}}
        expected_result = {"a": {"a": {"updated_by_b": 1}, "b": 1}, "b": {"b": 1}}
        result = AS3TemplateConfiguration({})._dict_deep_update(
            dict_to_update=dict_to_update, update=update
        )
        assert result == expected_result

    @staticmethod
    def test_list():
        dict_to_update = {"a": {"a": [1, 2, 3]}, (1, 2, 3): {"tuple": True}}
        update = {
            "b": {"b": 1},
            "a": {"b": 1, "a": {"updated_by_b": 1}},
            (1, 2, 3): {"tuple": True, "updated_by_b": 1},
        }
        expected_result = {
            "a": {"a": {"updated_by_b": 1}, "b": 1},
            "b": {"b": 1},
            (1, 2, 3): {"tuple": True, "updated_by_b": 1},
        }
        result = AS3TemplateConfiguration({})._dict_deep_update(
            dict_to_update=dict_to_update, update=update
        )
        assert result == expected_result


class Test_AS3TemplateConfiguration:
    @staticmethod
    def test_fail_file_missing():
        data = "tests/testdata/AS3TemplateConfiguration/DOESNOTEXIST.yaml"
        with pytest.raises(AS3TemplateConfigurationError):
            AS3TemplateConfiguration(data)

    @staticmethod
    def test_fail_globbing_notfile():
        data = "tests/testdata/AS3TemplateConfiguration*"
        with pytest.raises(AS3TemplateConfigurationError):
            AS3TemplateConfiguration(data)

    @staticmethod
    def test_fail_wrong_datatype():
        class WrongDatatype:
            pass

        data = WrongDatatype
        with pytest.raises(AS3TemplateConfigurationError):
            AS3TemplateConfiguration(data)

    @staticmethod
    def test_str():
        data = "tests/testdata/AS3TemplateConfiguration/file.yaml"
        AS3TemplateConfiguration(data)

    @staticmethod
    def test_str_globbing():
        data = "tests/testdata/AS3TemplateConfiguration/file.*"
        AS3TemplateConfiguration(data)

    @staticmethod
    def test_dict():
        data = {"deserialized": True}
        AS3TemplateConfiguration(data)

    @staticmethod
    def test_tuple_dict():
        data = ({"deserialized json": True}, {"deserialized yaml": True})
        AS3TemplateConfiguration(data)

    @staticmethod
    def test_list_dict():
        data = [{"deserialized json": True}, {"deserialized yaml": True}]
        AS3TemplateConfiguration(data)

    @staticmethod
    def test_list_str():
        data = [
            "tests/testdata/AS3TemplateConfiguration/file.json",
            "tests/testdata/AS3TemplateConfiguration/file.yaml",
        ]
        AS3TemplateConfiguration(data)

    @staticmethod
    def test_tuple_str():
        data = (
            "tests/testdata/AS3TemplateConfiguration/file.json",
            "tests/testdata/AS3TemplateConfiguration/file.yaml",
        )
        AS3TemplateConfiguration(data)

    @staticmethod
    def test_List_mixed():
        expected_result = {
            "deserialized json": True,
            "file.yaml": True,
            "content": {"yamlList": ["a", "b", "c"], "jsonList": ["A", "B", "C"]},
            "deserialized yaml": True,
            "file.json": True,
        }
        data = (
            {"deserialized json": True},
            "tests/testdata/AS3TemplateConfiguration/file.yaml",
            {"deserialized yaml": True},
            "tests/testdata/AS3TemplateConfiguration/file.json",
        )
        assert AS3TemplateConfiguration(data).dict() == expected_result

    @staticmethod
    def test_empty_as3ninja_namespace():
        expected_result = {"deserialized json": True}
        data = ({"deserialized json": True}, {"as3ninja": {}})
        assert AS3TemplateConfiguration(data).dict() == expected_result
