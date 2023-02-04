# -*- coding: utf-8 -*-
"""
AS3 Schema Format Checker for F5 specific formats.
"""

# pylint: disable=C0301 # Line too long

import re
from typing import Any

from jsonschema import FormatChecker

from ..types import F5IP, F5IPv4, F5IPv6


class AS3FormatChecker(FormatChecker):
    """
    AS3FormatChecker subclasses jsonschema.FormatChecker to provide AS3 specific format checks.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # update FormatChecker instance's format checkers with AS3 schema specific format checkers
        self.checkers.update(self.as3_schema_format_checkers)

    @property
    def as3_schema_format_checkers(self) -> dict:
        """
        Returns dict of AS3 formats: f5ip, f5ipv4, f5ipv6, f5label, f5long-id, f5remark, f5pointer, f5base64
        Currently missing formats used in AS3:

            - date-time
            - uri
            - url
        """
        return {
            # based on F5 IP addressing schemes for Virtual Servers, Nodes and Pool Members
            "f5ip": (lambda v: self._is_type(F5IP, v), ()),
            "f5ipv4": (lambda v: self._is_type(F5IPv4, v), ()),
            "f5ipv6": (lambda v: self._is_type(F5IPv6, v), ()),
            # based on AS3 3.17.1 : lib/adcParserFormats.js
            "f5name": (
                lambda v: self._regex_match(r"^([A-Za-z][0-9A-Za-z_]{0,63})?$", v),
                (),
            ),
            "f5bigip": (
                lambda v: self._regex_match(
                    r"^\x2f[^\x00-\x19\x22#\'*<>?\x5b-\x5d\x7b-\x7d\x7f]+$", v
                ),
                (),
            ),
            "f5long-id": (
                lambda v: self._regex_match(
                    r"^[^\x00-\x20\x22\'<>\x5c^`|\x7f]{0,255}$", v
                ),
                (),
            ),
            "f5label": (
                lambda v: self._regex_match(
                    r"^[^\x00-\x1f\x22#&*<>?\x5b-\x5d`\x7f]{0,64}$", v
                ),
                (),
            ),
            "f5remark": (
                lambda v: self._regex_match(r"^[^\x00-\x1f\x22\x5c\x7f]{0,64}$", v),
                (),
            ),
            "f5pointer": (
                lambda v: self._regex_match(
                    r"((@|[0-9]+)|(([0-9]*\x2f)?((@|[0-9]+|[A-Za-z][0-9A-Za-z_]{0,63})\x2f)*([0-9]+|([A-Za-z][0-9A-Za-z_]{0,63}))))?#?$",
                    v,
                ),
                (),
            ),
            "f5base64": (
                lambda v: self._regex_match(
                    r"^([0-9A-Za-z\/+_-]*|[0-9A-Za-z\/+_-]+={1,2})$", v
                ),
                (),
            ),
        }

    @staticmethod
    def _is_type(is_type: Any, value: Any) -> bool:
        """
        Helper function _is_type returns `True` when `is_type(value)` does not raise an exception, `False` otherwise

        :param is_type: The type to check against
        :param value: Value to check
        """
        try:
            is_type(value)
            return True
        except Exception:  # pylint: disable=W0703 # we do not care which exception occurs
            return False

    @staticmethod
    def _regex_match(regex: str, value: str) -> bool:
        """
        Helper function _regex_match matches a regular expression against the given value.
        Returns `True` when regex matches, `False` otherwise.

        :param regex: The regular expression, for example: ``r'^[ -~]+$'``
        :param value: Value to apply the regular expression to
        """
        if not isinstance(value, str):
            return False
        reg_ex = re.compile(regex)
        if reg_ex.match(value) is None:
            return False
        return True
