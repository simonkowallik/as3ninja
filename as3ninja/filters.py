# -*- coding: utf-8 -*-
"""
The ninjafilters module contains clever jinja2 filters.
"""
import base64
import json
from typing import Union
from uuid import uuid4

from jinja2 import Environment, contextfilter, environmentfilter
from jinja2.runtime import Context

from .vault import VaultSecret, VaultSecretsEngines
from .vault import vault as _vault

ninjafilters = dict()


# additional __all__ entries will be added by registerfilter
__all__ = ["ninjafilters"]


def registerfilter(f, name=None):
    """A decorator which registers the decorated function in ninjafilters dict and appends it's name to __all__"""
    global ninjafilters
    ninjafilters[name or f.__name__] = f
    __all__.append(name or f.__name__)
    return f


@registerfilter
@contextfilter
def vault(*args, **kwargs):
    return _vault(*args, **kwargs)


@registerfilter
def b64encode(data: str, urlsafe: bool = False) -> str:
    """Accepts a string and returns the Base64 encoded representation of this string.
    `urlsafe=True` encodes string as urlsafe base64
    """
    if urlsafe:
        b64 = base64.urlsafe_b64encode(data.encode("ascii"))
        return b64.decode("ascii")
    b64 = base64.b64encode(data.encode("ascii"))
    return b64.decode("ascii")


@registerfilter
def b64decode(data: str, urlsafe: bool = False) -> str:
    """Accepts a string and returns the Base64 decoded representation of this string.
    `urlsafe=True` decodes urlsafe base64
    """
    if urlsafe:
        b64 = base64.urlsafe_b64decode(data.encode("ascii"))
        return b64.decode("ascii")
    b64 = base64.b64decode(data.encode("ascii"))
    return b64.decode("ascii")


@registerfilter
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
    except (OSError):
        if missing_ok:
            return ""
        raise


@registerfilter
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


@registerfilter
def uuid(data: Union[str, None] = None) -> str:
    """Returns a UUID4"""
    return str(uuid4())


@registerfilter
@contextfilter
def ninjutsu(ctx: Context, value: str, **kwargs: dict) -> str:
    """ninjutsu passes its input to jinja2 rendereing using the existing jinja2 environment and context.
    You can specify arbitary keyword arguments to pass additional variables to the renderer.
    This is important if you define variables within control structures, for example loops.
    These variables are not exported in the context and can therefore not be accessed within the jinja2 template passed to ninjutsu.

    Example:

    .. code-block:: jinja

        ...
        {% for thisone in allofthem %}
        ...
        {# making thisone available to ninjutsu by passing
         # it as a keyword argument with the same name
         #}
        {{ somesource.content.with.jinja2 | ninjutsu(thisone=thisone) }}
        ...
        {% endfor %}

    If ``somesource.content.with.jinja2`` uses ``myvar`` it would fail if we don't specify the keyword argument ``myvar=myvar``,
    as it is not automatically exposed to the existing `jinja2 context`.

    An alternative are namespaces, just make sure the namespace is defined outside any of the control structures.
    Also note that the variable name will be an attribute of the namespace.

    .. code-block:: jinja

        ...
        {% clipboard = namespace() %}
        {% for thisone in allofthem %}
        ...
        {% set clipboard.thisone = thisone %}
        ...
        {# thisone is now available to ninjutsu as clipboard.thisone #}
        {{ somesource.content.with.jinja2 | ninjutsu }}
        ...
        {% endfor %}

    """
    return ctx.environment.from_string(value).render({**ctx, **kwargs})
