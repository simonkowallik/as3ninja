# -*- coding: utf-8 -*-
"""
The ninjafunctions contains clever jinja2 functions.
"""
import re
from pathlib import Path
from uuid import uuid4

from jinja2 import contextfunction
from jinja2.runtime import Context

from .utils import deserialize
from .vault import VaultClient as _VaultClient
from .vault import VaultSecret, VaultSecretsEngines
from .vault import vault as _vault

ninjafunctions = dict()


# additional __all__ entries will be added by registerfunction
__all__ = ["ninjafunctions"]


def registerfunction(f, name=None):
    """A decorator which registers the decorated function in ninjafunctions dict and appends it's name to __all__"""
    global ninjafunctions
    ninjafunctions[name or f.__name__] = f
    __all__.append(name or f.__name__)
    return f


@registerfunction
@contextfunction
def vault(*args, **kwargs):
    return _vault(*args, **kwargs)


@registerfunction
class VaultClient(_VaultClient):
    pass


@registerfunction
def uuid() -> str:
    """Returns a UUID4"""
    return str(uuid4())


@registerfunction
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
            except:
                _li.append(deserialize(datasource=filepath, return_as=str))

            return tuple(_li)
        else:
            raise StopIteration
