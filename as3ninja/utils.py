# -*- coding: utf-8 -*-
"""
utils holds various helper functions used in as3ninja.
"""
import json
from typing import Union

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
