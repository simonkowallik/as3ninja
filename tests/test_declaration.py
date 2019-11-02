# -*- coding: utf-8 -*-
import json

import pytest
from jinja2.exceptions import TemplateSyntaxError

from as3ninja.declaration import (
    AS3Declaration,
    AS3JSONDecodeError,
    AS3TemplateSyntaxError,
    AS3UndefinedError,
)
from tests.utils import fixture_tmpdir, format_json, load_file

mock_template_configuration: dict = {"a": "aaa", "b": "bbb"}
mock_declaration_template: str = """{
    "json": true,
    "a": "{{ninja.a}}",
    "b": "{{ninja.b}}"
}"""
mock_declaration: str = """{
    "json": true,
    "a": "aaa",
    "b": "bbb"
}"""

mock_template_configuration2: list = [
    {"a": "aaa", "b": "bbb"},
    {"a": "AAA", "c": "CCC"},
]
mock_template_configuration2_merged: dict = {"a": "AAA", "b": "bbb", "c": "CCC"}
mock_declaration_template2: str = """{
    "json": true,
    "a": "{{ninja.a}}",
    "b": "{{ninja.b}}",
    "c": "{{ninja.c}}"
}"""
mock_declaration2: str = """{
    "json": true,
    "a": "AAA",
    "b": "bbb",
    "c": "CCC"
}"""

mock_template_configuration_with_template: list = [
    {"a": "aaa", "b": "bbb", "as3ninja": {"declaration_template": "/dev/null"}},
    {
        "a": "AAA",
        "c": "CCC",
        "as3ninja": {
            "declaration_template": "tests/testdata/declaration/transform/template.j2"
        },
    },
]

mock_template_configuration_with_template_inline: list = [
    {"a": "aaa", "b": "bbb"},
    {
        "a": "AAA",
        "c": "CCC",
        "as3ninja": {
            "declaration_template": '{"json": True,"a": "{{ninja.a}}","b": "{{ninja.b}}","c": "{{ninja.c}}"}'
        },
    },
]


@pytest.fixture(scope="class")
def as3d_interface1():
    d = AS3Declaration(
        declaration_template=mock_declaration_template,
        template_configuration=mock_template_configuration,
    )
    return d


@pytest.fixture(scope="class")
def as3d_interface2():
    d = AS3Declaration(
        declaration_template=mock_declaration_template2,
        template_configuration=mock_template_configuration2,
    )
    return d


@pytest.fixture(scope="class")
def as3d_empty():
    return AS3Declaration(
        declaration_template='{"json": true}',
        template_configuration={"non empty": "dict"},
    )


@pytest.mark.usefixtures("as3d_interface1")
@pytest.mark.usefixtures("as3d_interface2")
class Test_Interface:
    @staticmethod
    def test_declaration(as3d_interface1):
        assert isinstance(as3d_interface1.declaration, dict)
        assert as3d_interface1.declaration == json.loads(mock_declaration)

    @staticmethod
    def test_declaration_asjson(as3d_interface1, as3d_interface2):
        assert isinstance(as3d_interface1.declaration_asjson, str)
        assert format_json(as3d_interface1.declaration_asjson) == format_json(
            mock_declaration
        )

        assert isinstance(as3d_interface2.declaration_asjson, str)
        assert format_json(as3d_interface2.declaration_asjson) == format_json(
            mock_declaration2
        )

    @staticmethod
    def test_declaration_template(as3d_interface1):
        assert isinstance(as3d_interface1.declaration_template, str)
        assert as3d_interface1.declaration_template == mock_declaration_template

    @staticmethod
    def test_template_configuration(as3d_interface1, as3d_interface2):
        assert isinstance(as3d_interface1.template_configuration, dict)
        assert as3d_interface1.template_configuration == mock_template_configuration

        assert isinstance(as3d_interface2.template_configuration, list)
        assert as3d_interface2.template_configuration == mock_template_configuration2

    @staticmethod
    def test_configuration(as3d_interface1, as3d_interface2):
        assert isinstance(as3d_interface1.configuration, dict)
        assert as3d_interface1.configuration == mock_template_configuration

        assert isinstance(as3d_interface2.configuration, dict)
        assert as3d_interface2.configuration == mock_template_configuration2_merged

    @staticmethod
    def test_declaration_template_file_in_configuration():
        as3d = AS3Declaration(
            template_configuration=mock_template_configuration_with_template
        )
        assert isinstance(as3d.declaration, dict)
        assert format_json(as3d.declaration_asjson) == format_json(mock_declaration2)

    @staticmethod
    def test_declaration_template_in_configuration_inline():
        with pytest.raises(ValueError):
            AS3Declaration(
                template_configuration=mock_template_configuration_with_template_inline
            )
            # inline declaration templates are not supported

    @staticmethod
    def test_missing_template_configuration():
        with pytest.raises(TypeError):
            AS3Declaration(declaration_template=mock_declaration_template)

    @staticmethod
    def test_missing_declaration_template_in_configuration():
        with pytest.raises(KeyError):
            AS3Declaration(template_configuration=mock_template_configuration)

    @staticmethod
    def test_fail_empty_init():
        with pytest.raises(TypeError):
            AS3Declaration()


@pytest.mark.usefixtures("as3d_empty")
class Test__dict_deep_update:
    @staticmethod
    def test_simple(as3d_empty):
        dict_to_update = {"a": {"a": 1}}
        update = {"b": {"b": 1}, "a": {"b": 1}}
        expected_result = {"a": {"a": 1, "b": 1}, "b": {"b": 1}}
        as3d = as3d_empty._dict_deep_update(
            dict_to_update=dict_to_update, update=update
        )
        assert as3d == expected_result

    @staticmethod
    def test_nested(as3d_empty):
        dict_to_update = {"a": {"a": 1}}
        update = {"b": {"b": 1}, "a": {"b": 1, "a": {"updated_by_b": 1}}}
        expected_result = {"a": {"a": {"updated_by_b": 1}, "b": 1}, "b": {"b": 1}}
        as3d = as3d_empty._dict_deep_update(
            dict_to_update=dict_to_update, update=update
        )
        assert as3d == expected_result

    @staticmethod
    def test_list(as3d_empty):
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
        as3d = as3d_empty._dict_deep_update(
            dict_to_update=dict_to_update, update=update
        )
        assert as3d == expected_result


class Test_implicit_transform:
    # TODO: test with empty configuration
    # TODO: test with configuration only, where template file location is read from configuration
    @staticmethod
    def test_simple():
        as3d = AS3Declaration(
            declaration_template=mock_declaration_template,
            template_configuration=mock_template_configuration,
        )
        assert as3d.declaration["a"] == "aaa"

    @staticmethod
    def test_simple_list():
        as3d = AS3Declaration(
            declaration_template=mock_declaration_template2,
            template_configuration=mock_template_configuration2,
        )
        assert as3d.declaration["a"] == "AAA"
        assert as3d.declaration["c"] == "CCC"

    @staticmethod
    def test_file_include_searchpath():
        template = """{
            "main": "{{ninja.main}}",
            "include": {% include './include.j2' %}
            }"""
        configuration = {"main": "MAIN", "include": "INCLUDE"}
        expected_result = {"main": "MAIN", "include": {"include": "INCLUDE"}}

        as3d = AS3Declaration(
            declaration_template=template,
            template_configuration=configuration,
            jinja2_searchpath="tests/testdata/declaration/transform/",
        )
        assert as3d.declaration == expected_result

    @staticmethod
    def test_file_include_searchpath_2():
        template = """{
            "main": "{{ninja.main}}",
            "include": {% include './declaration/transform/include.j2' %}
            }"""
        configuration = {"main": "MAIN", "include": "INCLUDE"}
        expected_result = {"main": "MAIN", "include": {"include": "INCLUDE"}}

        as3d = AS3Declaration(
            declaration_template=template,
            template_configuration=configuration,
            jinja2_searchpath="tests/testdata/",
        )
        assert as3d.declaration == expected_result

    @staticmethod
    def test_file_include_no_jinja2_searchpath():
        template = """{
            "main": "{{ninja.main}}",
            "include": {% include 'tests/testdata/declaration/transform/include.j2' %}
            }"""
        configuration = {"main": "MAIN", "include": "INCLUDE"}
        expected_result = {"main": "MAIN", "include": {"include": "INCLUDE"}}

        as3d = AS3Declaration(
            declaration_template=template, template_configuration=configuration
        )
        assert as3d.declaration == expected_result

    @staticmethod
    def test_file_include_searchpath_configlist():
        template = """{
            "main": "{{ninja.main}}",
            "include": {% include './include.j2' %}
            }"""
        configuration = [{"main": "MAIN", "include": "NONE"}, {"include": "INCLUDE"}]
        expected_result = {"main": "MAIN", "include": {"include": "INCLUDE"}}

        as3d = AS3Declaration(
            declaration_template=template,
            template_configuration=configuration,
            jinja2_searchpath="tests/testdata/declaration/transform/",
        )
        assert as3d.declaration == expected_result


class Test_transform_method:
    pass
    # TODO: test the transform method


class Test_invalid_declarations:
    @staticmethod
    def test_invalid_json():
        template: str = """{
            "json": "this json template is invalid, the comma after b will throw a decode exception",
            "a": "{{ninja.a}}",
            "b": "{{ninja.b}}",
        }
        """
        config = {"a": "aaa", "b": "bbb"}
        with pytest.raises(AS3JSONDecodeError):
            as3d = AS3Declaration(
                declaration_template=template, template_configuration=config
            )

    @staticmethod
    def test_missing_jinja_variable():
        template: str = """{
            "json": "this json template is invalid, the comma after b will throw a decode exception",
            "a": "{{ninja.a}}"
            {% if this_is_a_variable %}
            ,"b": "{{ninja.b}}"
            {% endif %}
        }
        """
        config = {"a": "aaa", "b": "bbb"}
        with pytest.raises(AS3UndefinedError):
            AS3Declaration(declaration_template=template, template_configuration=config)

    @staticmethod
    def test_invalid_jinja_template_command():
        template: str = """{
            "a": "{{ninja.a}}"
            {% unknown_command ninja.b %}
            ,"b": "{{ninja.b}}"
            {% endif %}
        }
        """
        config = {"a": "aaa", "b": "bbb"}
        with pytest.raises(AS3TemplateSyntaxError):
            AS3Declaration(declaration_template=template, template_configuration=config)

    @staticmethod
    def test_invalid_jinja_template_syntax():
        template: str = """{
            "a": "{{ninja.a}}"
            {% if ninja.b %}
            ,"b": "{{ninja.b}}"
        }
        """
        config = {"a": "aaa", "b": "bbb"}
        with pytest.raises(AS3TemplateSyntaxError):
            AS3Declaration(declaration_template=template, template_configuration=config)

    @staticmethod
    def test_invalid_jinja_template_syntax2():
        template: str = """{
            "a": "{{ninja.a}}"
            {% if ninja.b %}
            ,"b": "{{ninja.b}}"
            {%
        }
        """
        config = {"a": "aaa", "b": "bbb"}
        with pytest.raises(AS3TemplateSyntaxError):
            AS3Declaration(declaration_template=template, template_configuration=config)
