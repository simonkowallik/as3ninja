# -*- coding: utf-8 -*-
"""
This module holds Jinja2 functions for AS3 Ninja.
"""

# pylint: disable=C0330 # Wrong hanging indentation before block
# pylint: disable=C0301 # Line too long

import re
from pathlib import Path

from .j2ninja import J2Ninja
from ..utils import deserialize


@J2Ninja.registerfunction
class iterfiles:
    """iterates files, returns a tuple of all globbing matches and the file content as dict.
    Assumes the file content is either JSON or YAML.

    iterfiles will ignore missing files if `missing_ok=True` is specified (default: False),
    otherwise will raise a `FileNotFoundError` exception.

        :param missing_ok: bool:  (Default value = False)
    """

    def __init__(self, pattern, missing_ok=False):
        p = Path(".")
        self._filepaths = list(sorted(p.glob(pattern)))
        self._filepaths.reverse()
        if not missing_ok and not self._filepaths:
            raise FileNotFoundError(
                f"iterfiles: Could not find any files for pattern:{pattern}"
            )

        self._pattern = pattern
        self._pattern = self._pattern.replace("**", "*")
        self._pattern = self._pattern.replace(".", "\\.")
        self._pattern = "(.*)".join(self._pattern.split("*"))

    def __iter__(self):
        return self

    def __next__(self):
        if self._filepaths:
            filepath = str(self._filepaths.pop())
            m = re.search(self._pattern, filepath)

            _li = list(m.groups())
            try:
                _li.append(deserialize(datasource=filepath))
            except ValueError:
                with open(filepath, "r") as filepath_fh:
                    _li.append(filepath_fh.read())

            return tuple(_li)
        else:
            raise StopIteration
