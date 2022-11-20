# -*- coding: utf-8 -*-
"""
This module holds Jinja2 filters for AS3 Ninja.
"""

# pylint: disable=C0330 # Wrong hanging indentation before block
# pylint: disable=C0301 # Line too long

from jinja2 import pass_context
from jinja2.runtime import Context

from .j2ninja import J2Ninja

@J2Ninja.registerfilter
@pass_context
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
