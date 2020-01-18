# -*- coding: utf-8 -*-
"""Various utils and helpes used by AS3 Ninja"""
import json
from typing import Any, ItemsView, Iterator, KeysView, List, Tuple, Union, ValuesView

import yaml


def deserialize(
    datasource: str, return_as: Union[dict, str, None] = None
) -> Union[dict, str]:
    """deserialize first tries to read a config from a file otherwise from the passed variable.
        depending on return_as the content is parsed to a dict from JSON|YAML or returned as str

    :param datasource: str:
    :param return_as: Union[dict: str: None:]:  (Default value = None)

    """
    # TODO: probably a good idea to seperate datasource parameter into file/data
    (error_file_open, error_json_deserialize) = (False, False)
    try:
        with open(datasource, "r") as jyfile:
            data = jyfile.read()
    except OSError:
        data = datasource
        error_file_open = "Error"

    if return_as is str and not error_file_open:
        return str(data)

    try:
        _data = json.loads(data)
    except (json.JSONDecodeError, TypeError):
        error_json_deserialize = "Error"
        try:
            _data = yaml.safe_load(data)
        except (yaml.parser.ParserError, yaml.scanner.ScannerError):
            _data = None

    if not isinstance(_data, dict):
        raise ValueError(
            f"deserialize: Could not convert datasource to dict. Errors: file open:{error_file_open}, JSON deserialize:{error_json_deserialize}, YAML deserialize:Error, datasource:{datasource}"
        )

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
