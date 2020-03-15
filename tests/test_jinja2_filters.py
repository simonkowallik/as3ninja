# -*- coding: utf-8 -*-
from uuid import UUID

import pytest
from jinja2 import DictLoader, Environment
from jinja2.runtime import Context

from as3ninja.jinja2 import J2Ninja
from as3ninja.jinja2.filterfunctions import *
from as3ninja.jinja2.filters import *
from tests.utils import format_json


def test_J2Ninja_filters_is_dict():
    assert type(J2Ninja.filters) == dict


class Test_Base64:
    @staticmethod
    def test_b64encode():
        decoded = r"123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
        encoded = r"MTIzNDU2Nzg5Ojs8PT4/QEFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaW1xdXl9gYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXp7fH1+"
        assert b64encode(decoded) == encoded

    @staticmethod
    def test_b64decode():
        decoded = r"123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
        encoded = r"MTIzNDU2Nzg5Ojs8PT4/QEFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaW1xdXl9gYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXp7fH1+"
        assert b64decode(encoded) == decoded

    @staticmethod
    def test_b64encode_urlsafe():
        decoded = r"123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
        encoded = r"MTIzNDU2Nzg5Ojs8PT4_QEFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaW1xdXl9gYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXp7fH1-"
        assert b64encode(decoded, urlsafe=True) == encoded

    @staticmethod
    def test_b64decode_urlsafe():
        decoded = r"123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
        encoded = r"MTIzNDU2Nzg5Ojs8PT4_QEFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaW1xdXl9gYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXp7fH1-"
        assert b64decode(encoded, urlsafe=True) == decoded


class Test_jsonify:
    @staticmethod
    def test_simple_json():
        teststring = '{"json":true}'
        expectation = '"{\\"json\\":true}"'

        assert jsonify(teststring) == expectation

    @staticmethod
    def test_json_noquote():
        teststring = '{"json":true}'
        expectation = '{\\"json\\":true}'

        assert jsonify(teststring, quote=False) == expectation


def test_uuid():
    myuuid = uuid("")
    assert isinstance(myuuid, str)
    assert isinstance(UUID(myuuid), UUID)


class Test_readfile:
    @staticmethod
    def test_textfile_ascii():
        result = readfile(Context, "tests/testdata/functions/iterfiles/text/file.txt")
        assert isinstance(result, str)

    @staticmethod
    def test_textfile_utf8():
        with pytest.raises(UnicodeDecodeError):
            result = readfile(Context, "tests/testdata/functions/utf8.txt")

    @staticmethod
    def test_non_existing_file_missingOk():
        result = readfile(Context, "does/not/exist.ext", missing_ok=True)
        assert isinstance(result, str)
        assert result == ""

    @staticmethod
    def test_non_existing_file():
        with pytest.raises(OSError):
            readfile(Context, "does/not/exist.ext", missing_ok=False)


class Test_ninjutsu:
    @staticmethod
    def _get_env(declaration_template: str, template_configuration: dict):
        env = Environment(
            loader=DictLoader({"template": declaration_template}),
            trim_blocks=False,
            lstrip_blocks=False,
        )
        env.filters.update({"ninjutsu": ninjutsu, "readfile": readfile})
        env.globals["ninja"] = template_configuration
        return env

    def test_ninjutsu(self):
        declaration_template: str = """{
        {% set myns = namespace() -%}
        {% set myns.var = "some value" -%}
        {{ninja.bfile | readfile | ninjutsu}}
        }"""
        template_configuration: dict = {
            "a": "from_config",
            "bfile": "tests/testdata/filters/ninjutsu.j2",
        }
        expected_result = '{"from_config": "from_config", "from_context": "some value"}'
        env = self._get_env(
            declaration_template=declaration_template,
            template_configuration=template_configuration,
        )

        result = env.get_template("template").render()

        assert format_json(result) == format_json(expected_result)
