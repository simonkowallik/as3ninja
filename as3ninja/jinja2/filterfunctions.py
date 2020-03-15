# -*- coding: utf-8 -*-
"""
This module holds Jinja2 functions which also work as filters.
"""

# pylint: disable=C0330 # Wrong hanging indentation before block
# pylint: disable=C0301 # Line too long

import base64
import json
from uuid import uuid4

from jinja2 import contextfilter
from jinja2.runtime import Context

from .j2ninja import J2Ninja


@J2Ninja.registerfilter
@J2Ninja.registerfunction
def b64encode(data: str, urlsafe: bool = False) -> str:
    """Accepts a string and returns the Base64 encoded representation of this string.
    `urlsafe=True` encodes string as urlsafe base64
    """
    if urlsafe:
        b64 = base64.urlsafe_b64encode(data.encode("ascii"))
        return b64.decode("ascii")
    b64 = base64.b64encode(data.encode("ascii"))
    return b64.decode("ascii")


@J2Ninja.registerfilter
@J2Ninja.registerfunction
def b64decode(data: str, urlsafe: bool = False) -> str:
    """Accepts a string and returns the Base64 decoded representation of this string.
    `urlsafe=True` decodes urlsafe base64
    """
    if urlsafe:
        b64 = base64.urlsafe_b64decode(data.encode("ascii"))
        return b64.decode("ascii")
    b64 = base64.b64decode(data.encode("ascii"))
    return b64.decode("ascii")


@J2Ninja.registerfilter
@J2Ninja.registerfunction
@contextfilter
def readfile(ctx: Context, filepath: str, missing_ok: bool = False) -> str:
    """Reads a file and returns its content as ASCII.
    Expects the file to be a ASCII (not utf8!) encoded file.

    `missing_ok=True` prevents raising an exception when the file is missing and will return an empty string (default: missing_ok=False).
    """
    path_prefix: str = ""
    if isinstance(ctx, Context):
        path_prefix = ctx.parent.get("jinja2_searchpath", "")
    try:
        with open(path_prefix + filepath, "rb") as f:
            content = f.read()
            return content.decode("ascii")
    except OSError:
        if missing_ok:
            return ""
        raise


@J2Ninja.registerfilter
@J2Ninja.registerfunction
def jsonify(data: str, quote: bool = True) -> str:
    """serializes data to JSON format.

    ``quote=False`` avoids surrounding quotes,
    For example:

    .. code-block:: jinja

        "key": "{{ ninja.somevariable | jsonify(quote=False) }}"

    Instead of:

    .. code-block:: jinja

        "key": {{ ninja.somevariable | jsonify }}

    """

    if quote:
        return json.dumps(data)
    else:
        jsonified = json.dumps(data)
        return jsonified[1:-1]


@J2Ninja.registerfilter
@J2Ninja.registerfunction
def uuid(_=None) -> str:
    """Returns a UUID4"""
    return str(uuid4())
