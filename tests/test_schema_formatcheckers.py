# -*- coding: utf-8 -*-
import pytest
from jsonschema import FormatChecker

from as3ninja.schema.formatcheckers import AS3FormatChecker


class Test_AS3FormatChecker_staticmethods:
    @staticmethod
    def test_is_type_True():
        assert AS3FormatChecker._is_type(int, 4) is True

    @staticmethod
    def test_is_type_False():
        assert AS3FormatChecker._is_type(int, "string") is False

    @staticmethod
    def test_positive_match():
        assert AS3FormatChecker._regex_match("^[a-z]{3}$", "foo") is True

    @staticmethod
    def test_negative_match():
        assert AS3FormatChecker._regex_match("[^a-z]{3}$", "foo") is False


class Test_AS3FormatChecker_as3_schema_format_checkers:
    @staticmethod
    def test_is_dict():
        fc = AS3FormatChecker()
        assert isinstance(fc.as3_schema_format_checkers, dict)

    @pytest.mark.parametrize(
        "key, value_tuple", AS3FormatChecker().as3_schema_format_checkers.items()
    )
    def test_valid_format(self, key, value_tuple):
        """
        jsonschmea.FormatChecker expects a dict with tuples

            { "formatname": (function, ()) }
        """
        assert isinstance(key, str)
        assert isinstance(value_tuple, tuple)
        assert value_tuple[0] is not None
        assert value_tuple[1] is not None


class Test_AS3FormatChecker_checkers:

    fc = AS3FormatChecker()

    @pytest.mark.parametrize(
        "format_check, test_string, expected_result",
        [
            ["f5label", "some label", True],
            ["f5label", '!\a%""', False],
            ["f5remark", "Hi there! this is a remark!", True],
            ["f5pointer", "/@/A/serviceMain/virtualPort", True],
            ["f5base64", "dGVzdA==", True],
            ["f5base64", "dGVzdA_/+", True],
            ["f5name", "My_ObjectName", True],
            ["f5label", "This is a label", True],
            ["f5ip", "0.0.0.0", True],
            ["f5ip", "255.255.255.255%65534/32", True],
            ["f5ip", "2001:0db8::7334", True],
            ["f5ipv4", "255.255.255.255%65534/32", True],
            ["f5ipv6", "2001:0db8:85a3:0000:0000:8A2E:0370:7334%65534/128", True],
            ["f5ipv6", "0.0.0.0", False],
            ["f5ipv6", "2001:0db8::7334", True],
            [
                "f5long-id",
                "sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
                True,
            ],
        ],
    )
    def test_formatcheckers(self, format_check, test_string, expected_result):
        assert self.fc.checkers[format_check][0](test_string) is expected_result
