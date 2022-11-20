# -*- coding: utf-8 -*-
import json

import pytest
from jinja2.exceptions import TemplateSyntaxError

from as3ninja.declaration import AS3Declaration
from as3ninja.exceptions import (
    AS3JSONDecodeError,
    AS3TemplateSyntaxError,
    AS3UndefinedError,
)
from as3ninja.templateconfiguration import AS3TemplateConfiguration
from tests.utils import fixture_tmpdir, format_json, load_file

mock_template_configuration = AS3TemplateConfiguration({"a": "aaa", "b": "bbb"})
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

mock_template_configuration2 = AS3TemplateConfiguration(
    [
        {"a": "aaa", "b": "bbb"},
        {"a": "AAA", "c": "CCC"},
    ]
)
mock_template_configuration2_merged = AS3TemplateConfiguration(
    {"a": "AAA", "b": "bbb", "c": "CCC"}
)
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

mock_template_configuration_with_template = AS3TemplateConfiguration(
    [
        {"a": "aaa", "b": "bbb", "as3ninja": {"declaration_template": "/dev/null"}},
        {
            "a": "AAA",
            "c": "CCC",
            "as3ninja": {
                "declaration_template": "tests/testdata/declaration/transform/template.j2"
            },
        },
    ]
)

mock_template_configuration_with_template_inline = AS3TemplateConfiguration(
    [
        {"a": "aaa", "b": "bbb"},
        {
            "a": "AAA",
            "c": "CCC",
            "as3ninja": {
                "declaration_template": '{"json": True,"a": "{{ninja.a}}","b": "{{ninja.b}}","c": "{{ninja.c}}"}'  # this will fail as a file is required
            },
        },
    ]
)


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
        template_configuration=AS3TemplateConfiguration({"non empty": "dict"}),
    )


@pytest.mark.usefixtures("as3d_interface1")
@pytest.mark.usefixtures("as3d_interface2")
class Test_Interface:
    @staticmethod
    def test_declaration(as3d_interface1):
        assert isinstance(as3d_interface1.dict(), dict)
        assert as3d_interface1.dict() == json.loads(mock_declaration)

    @staticmethod
    def test_json(as3d_interface1, as3d_interface2):
        assert isinstance(as3d_interface1.json(), str)
        assert format_json(as3d_interface1.json()) == format_json(mock_declaration)

        assert isinstance(as3d_interface2.json(), str)
        assert format_json(as3d_interface2.json()) == format_json(mock_declaration2)

    @staticmethod
    def test_declaration_template(as3d_interface1):
        assert isinstance(as3d_interface1.declaration_template, str)
        assert as3d_interface1.declaration_template == mock_declaration_template

    @staticmethod
    def test_declaration_template_file_in_configuration():
        as3d = AS3Declaration(
            template_configuration=mock_template_configuration_with_template
        )
        assert isinstance(as3d.dict(), dict)
        assert format_json(as3d.json()) == format_json(mock_declaration2)

    @staticmethod
    def test_declaration_template_in_configuration_inline():
        with pytest.raises(FileNotFoundError):
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


class Test_implicit_transform:
    @staticmethod
    def test_simple():
        as3d = AS3Declaration(
            declaration_template=mock_declaration_template,
            template_configuration=mock_template_configuration,
        )
        assert as3d.dict()["a"] == "aaa"

    @staticmethod
    def test_simple_list():
        as3d = AS3Declaration(
            declaration_template=mock_declaration_template2,
            template_configuration=mock_template_configuration2,
        )
        assert as3d.dict()["a"] == "AAA"
        assert as3d.dict()["c"] == "CCC"

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
        assert as3d.dict() == expected_result

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
        assert as3d.dict() == expected_result

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
        assert as3d.dict() == expected_result

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
            template_configuration=AS3TemplateConfiguration(configuration),
            jinja2_searchpath="tests/testdata/declaration/transform/",
        )
        assert as3d.dict() == expected_result


class Test_transform_syntaxerror:
    @staticmethod
    def test_multi_template_syntax_error():
        """https://github.com/simonkowallik/as3ninja/issues/4"""
        template = """{
            "include": {% include './include.jinja2' %}
            }"""

        with pytest.raises(AS3TemplateSyntaxError) as exc:
            _ = AS3Declaration(
                declaration_template=template,
                template_configuration={},
                jinja2_searchpath="tests/testdata/declaration/syntax_error/",
            )
        assert "{% This line raises a Syntax Error %}<---- Error line:2" in str(
            exc.value
        )


class Test_transform_DOLLARschema:
    @pytest.mark.parametrize(
        "template",
        [
            """{ "$schema": "schemalink", "foo": "bar" }""",  # $schema will be removed
            """{ "foo": "bar" }""",  # must yield the same result as above
        ],
    )
    def test_remove_schema(self, template):
        expected_result = {"foo": "bar"}

        as3d = AS3Declaration(
            declaration_template=template,
            template_configuration={},
        )
        assert as3d.dict() == expected_result


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
