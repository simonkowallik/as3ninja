# -*- coding: utf-8 -*-
"""
Various utils and helpes used by AS3 Ninja
"""

# pylint: disable=C0330 # Wrong hanging indentation before block
# pylint: disable=C0301 # Line too long
# pylint: disable=C0116 # Missing function or method docstring

import json
import sys
from functools import wraps
from typing import Any, ItemsView, Iterator, KeysView, Optional, Union, ValuesView

import yaml


def deserialize(datasource: str) -> dict:
    """
    deserialize de-serializes JSON or YAML from a file to a python dict.

    A ValueError exception is raised if JSON and YAML de-serialization fails.

    :param datasource: A file or data to deserialize
    """
    with open(datasource, "r") as jy_file:
        data = jy_file.read()

    try:
        _data = json.loads(data)
    except (json.JSONDecodeError, TypeError):
        try:
            _data = yaml.safe_load(data)
        except (yaml.parser.ParserError, yaml.scanner.ScannerError):
            _data = None

    if not isinstance(_data, dict):
        raise ValueError("deserialize: Could not deserialize datasource.")

    return _data


class DictLike:
    """Makes objects `feel` like a dict.

    Implements required dunder methods and common methods used to access dict data.
    """

    _dict: dict = {}

    def __iter__(self) -> Iterator[str]:
        for key in self._dict:
            yield key

    def __len__(self) -> int:
        return len(self._dict)

    def __contains__(self, item: Any) -> bool:
        return item in self._dict

    def __eq__(self, other: Any) -> bool:
        return self._dict.items() == other.items()

    def __getitem__(self, key: str) -> Any:
        return self._dict.__getitem__(key)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._dict})"

    def __str__(self) -> str:
        return str(self._dict)

    def get(self, key: Any, default: Any = None) -> Any:
        return self._dict.get(key, default)

    def keys(self) -> KeysView[Any]:
        return self._dict.keys()

    def values(self) -> ValuesView[Any]:
        return self._dict.values()

    def items(self) -> ItemsView[Any, Any]:
        return self._dict.items()


def failOnException(wrapped_function):
    """sys.exit(1) on any exception"""

    @wraps(wrapped_function)
    def failOnException_wrapper(*args, **kwargs):
        """wrapper function"""
        try:
            return wrapped_function(*args, **kwargs)
        except Exception:  # pylint: disable=W0703
            sys.exit(1)

    return failOnException_wrapper


def escape_split(string_to_split: str, seperator: str = ".") -> tuple:
    """Splits a string based on the provided seperator.

    escape_split supports escaping the seperator by prepending a backslash.

    :param string_to_split: String to split
    :param seperator: Seperator to use for splitting (Default: ".")
    """
    i, res, buffer = 0, [], ""
    while True:
        j, e = string_to_split.find(seperator, i), 0
        if j < 0:
            return tuple(res + [buffer + string_to_split[i:]])
        while j - e and string_to_split[j - e - 1] == "\\":
            e += 1
        d = e // 2
        if e != d * 2:
            buffer += string_to_split[i : j - d - 1] + string_to_split[j]
            i = j + 1
            continue
        res.append(buffer + string_to_split[i : j - d])
        i = j + len(seperator)
        buffer = ""


class PathAccessError(KeyError, IndexError, TypeError):
    """An amalgamation of KeyError, IndexError, and TypeError,
    representing what can occur when looking up a path in a nested
    object.
    """

    def __init__(self, exc, seg, path):
        self.exc = exc
        self.seg = seg
        self.path = path

    def __repr__(self):
        return f"{self.__class__.__name__}({self.exc}, {self.seg}, {self.path})"

    def __str__(self):
        return (
            f"could not access {self.seg} from path {self.path}, got error: {self.exc}"
        )


def dict_filter(
    dict_to_filter: dict, filter: Optional[Union[tuple, str]] = None
) -> Any:
    """Filters a dict based on the provided filter.

    dict_filter will walk the dict keys based on the filter and will return the value of the last key.
    If filter is empty, dict_to_filter will be returned.

    Example:
    assert dict_filter({ 'a': { 'b': [1,2,3] } }, filter="a.b") == [1,2,3]

    :param dict_to_filter: Python dict to filter
    :param filter: Filter to apply to the dict. Filter can be a ``str`` (will be split on `.`) or a ``tuple``.
    """
    if filter:
        if isinstance(filter, str):
            filter = escape_split(filter)
        for seg in filter:
            try:
                dict_to_filter = dict_to_filter[seg]
            except (KeyError, IndexError) as exc:
                raise PathAccessError(exc, seg, filter)
            except TypeError as exc:
                # either string index in a list, or a parent that
                # doesn't support indexing
                try:
                    seg = int(seg)
                    dict_to_filter = dict_to_filter[seg]
                except (ValueError, KeyError, IndexError, TypeError):
                    try:
                        iter(dict_to_filter)
                    except TypeError:
                        exc = TypeError(
                            f"{type(dict_to_filter).__name__} object is not indexable"
                        )
                    raise PathAccessError(exc, seg, filter)

    return dict_to_filter


# pylint: disable=W0105 # String statement has no effect
"""
PathAccessError and dict_filter are based on boltons iterutils: https://github.com/mahmoud/boltons

boltons license:
Copyright (c) 2013, Mahmoud Hashemi

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.

    * Redistributions in binary form must reproduce the above
      copyright notice, this list of conditions and the following
      disclaimer in the documentation and/or other materials provided
      with the distribution.

    * The names of the contributors may not be used to endorse or
      promote products derived from this software without specific
      prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
