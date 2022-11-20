# -*- coding: utf-8 -*-
"""
This module holds Jinja2 functions which also work as filters.
"""

# pylint: disable=C0330 # Wrong hanging indentation before block
# pylint: disable=C0301 # Line too long

import base64
import hashlib
import json
import os
from typing import Any, Optional, Union
from uuid import uuid4

from jinja2 import pass_context
from jinja2.runtime import Context

from .j2ninja import J2Ninja


@J2Ninja.registerfilter
@J2Ninja.registerfunction
def b64encode(data: Union[str, bytes], urlsafe: bool = False) -> str:
    """Accepts a string and returns the Base64 encoded representation of this string.
    `urlsafe=True` encodes string as urlsafe base64
    """
    if not isinstance(data, bytes):
        data = data.encode("ascii")
    if urlsafe:
        b64 = base64.urlsafe_b64encode(data)
        return b64.decode("ascii")
    b64 = base64.b64encode(data)
    return b64.decode("ascii")


@J2Ninja.registerfilter
@J2Ninja.registerfunction
def b64decode(data: Union[str, bytes], urlsafe: bool = False) -> Union[str, bytes]:
    """Accepts a string and returns the Base64 decoded representation of this string.
    `urlsafe=True` decodes urlsafe base64
    """
    if not isinstance(data, bytes):
        data = data.encode("ascii")
    if urlsafe:
        b64 = base64.urlsafe_b64decode(data)
    else:
        b64 = base64.b64decode(data)
    try:
        return b64.decode("ascii")
    except UnicodeDecodeError:
        return b64


@J2Ninja.registerfilter
@J2Ninja.registerfunction
@pass_context
def readfile(ctx: Context, filepath: str, missing_ok: bool = False) -> str:
    """Reads a file and returns its content as ASCII.
    Expects the file to be a ASCII (not utf8!) encoded file.

    `missing_ok=True` prevents raising an exception when the file is missing and will return an empty string (default: missing_ok=False).
    """
    path_prefix: str = ""
    if isinstance(ctx, Context):
        path_prefix = ctx.parent.get("jinja2_searchpath", "")
    try:
        with open(path_prefix + filepath, "rb") as filehandle:
            content = filehandle.read()
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

    jsonified = json.dumps(data)
    return jsonified[1:-1]


@J2Ninja.registerfilter
@J2Ninja.registerfunction
def to_list(data: Any) -> list:
    """Converts ``data`` to a list.
    Unlike ``list`` it will not convert ``str`` to a list of each character but wrap the whole ``str`` in a list.
    Does not convert existing lists.

    For example:

    .. code-block:: jinja

        "virtualAddresses": {{ ninja.virtual_addresses | to_list | jsonify }},

    If ``ninja.virtual_addresses`` is a list already it will not be nested, if it is a string, the string will be placed in a list.

    Another example using the python REPL:

    .. code-block:: python

        ( to_list("foo bar") == ['foo bar'] ) == True  # strings

        ( to_list(["foo", "bar"]) == ['foo', 'bar'] ) == True  # existing lists

        ( to_list(245) == [245] ) == True  # integers

    """

    if isinstance(data, (str, int)):
        return [data]
    return list(data)


@J2Ninja.registerfilter
@J2Ninja.registerfunction
def env(env_var: str, default: Optional[Union[str, int]] = None) -> str:
    """Reads an environment variable and returns its value.

    Use ``default`` to specify a default value in case the environment variable does not exist,
    Empty environment variables will return an empty string.


    Examples:

    .. code-block:: jinja

        {# using env as a filter #}
        "HOME_DIR": "{{ 'HOME' | env }}"


    .. code-block:: jinja

        {# using env as a function #}
        {% set home_dir = env("HOME") %}
        {% set temp_dir = env("TEMPDIR", default="/tmp") %}

    """

    return str(os.getenv(env_var, default=default))


@J2Ninja.registerfilter
@J2Ninja.registerfunction
def uuid(_=None) -> str:
    """Returns a UUID4"""
    return str(uuid4())


@J2Ninja.registerfilter
@J2Ninja.registerfunction
def sha1sum(data: Union[str, bytes]) -> str:
    """
    Returns the hash as a hexdigest of ``data``.
    ``data`` is automatically converted to bytes, using backslashreplace for utf8 characters.
    """
    return hashfunction(data=data, hash_algo="sha1", digest_format="hex")


@J2Ninja.registerfilter
@J2Ninja.registerfunction
def sha256sum(data: Union[str, bytes]) -> str:
    """
    Returns the hash as a hexdigest of ``data``.
    ``data`` is automatically converted to bytes, using backslashreplace for utf8 characters.
    """
    return hashfunction(data=data, hash_algo="sha256", digest_format="hex")


@J2Ninja.registerfilter
@J2Ninja.registerfunction
def sha512sum(data: Union[str, bytes]) -> str:
    """
    Returns the hash as a hexdigest of ``data``.
    ``data`` is automatically converted to bytes, using backslashreplace for utf8 characters.
    """
    return hashfunction(data=data, hash_algo="sha512", digest_format="hex")


@J2Ninja.registerfilter
@J2Ninja.registerfunction
def md5sum(data: Union[str, bytes]) -> str:
    """
    Returns the hash as a hexdigest of ``data``.
    ``data`` is automatically converted to bytes, using backslashreplace for utf8 characters.
    """
    return hashfunction(data=data, hash_algo="md5", digest_format="hex")


@J2Ninja.registerfilter
@J2Ninja.registerfunction
def hashfunction(
    data: Union[str, bytes], hash_algo: str, digest_format: str = "hex"
) -> Union[str, bytes]:
    """
    Returns the digest of ``data`` for hash algorithm ``hash_algo``.
    The digest is returned as hex by default, but can be returned as binary as well (``digest_format``)

    Check the `hashlib documentation`_ of your python version for supported hash functions.

    :param hash_algo: hash algorithm
    :param digest_format: Digest format to return. Either `hex` (default) or `binary`.

    .. _`hashlib documentation`: https://docs.python.org/3/library/hashlib.html

    For the variable length shake digest, 256 bits are returned.

    .. code-block:: jinja

        {% set whirlpool_hexdigest = hashfunction("fun with hashes", "whirlpool") %}
        {# value of whirlpool_hexdigest is "ce38f0a536e71b5b0758932c1d5f32d2ab6cc5bff9f02fb7c97a70291d45efa4516d4e3d99000956587c7c9f691f64b3444a91661d45f526552a9e2d42428b09"
         # note that whirlpool is not a guaranteed hash function, hence might not be available on all platforms
         #}

    """
    if isinstance(data, str):
        data = data.encode("utf-8")

    hash_function = hashlib.new(hash_algo, data)

    if digest_format == "hex":  # use hexdigest method of hash_function
        hash_function_digest = getattr(hash_function, "hexdigest")
    elif digest_format == "binary":  # use binary digest method of hash_function
        hash_function_digest = getattr(hash_function, "digest")
    else:
        raise ValueError(
            f"digest_format:{digest_format} is unknown. digest_format must be either `hex` or `binary`."
        )

    if hash_algo.startswith(
        "shake_"
    ):  # shake is a variable length digest, return 256 bits
        return hash_function_digest(32)  # type: ignore[call-arg]
    return hash_function_digest()
