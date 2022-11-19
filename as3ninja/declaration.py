# -*- coding: utf-8 -*-
"""
The AS3Declaration module. Represents an AS3 Declaration as a python class.
"""

# pylint: disable=C0330 # Wrong hanging indentation before block
# pylint: disable=C0301 # Line too long

import json
from typing import Dict, Optional

from jinja2 import (
    ChoiceLoader,
    DictLoader,
    Environment,
    FileSystemLoader,
    StrictUndefined,
)
from jinja2.exceptions import TemplateSyntaxError, UndefinedError

from .exceptions import AS3JSONDecodeError, AS3TemplateSyntaxError, AS3UndefinedError
from .jinja2 import J2Ninja

__all__ = ["AS3Declaration"]


class AS3Declaration:
    """Creates an AS3Declaration instance representing the AS3 declaration.

    The AS3 declaration is created using the given template configuration, which can be either a dict or list of dicts.
    If a list is provided, the member dicts will be merged using :py:meth:`_dict_deep_update`.

    Optionally a jinja2 declaration_template can be provided, otherwise it is read from the configuration.
    The template file reference is expected to be at `as3ninja.declaration_template` within the configuration.
    An explicitly specified declaration_template takes precedence over any included template.

    :param template_configuration: AS3 Template Configuration as ``dict`` or ``list``
    :param declaration_template: Optional Declaration Template as ``str`` (Default value = ````)
    :param jinja2_searchpath: The jinja2 search path for the FileSystemLoader. Important for jinja2 includes. (Default value = ``"."``)
    """

    def __init__(
        self,
        template_configuration: Dict,
        declaration_template: Optional[str] = None,
        jinja2_searchpath: str = ".",
    ):
        self._template_configuration = template_configuration
        self._declaration_template = declaration_template or ""
        self._jinja2_searchpath = jinja2_searchpath

        if not self._declaration_template:
            try:
                declaration_template_file = self._template_configuration["as3ninja"][
                    "declaration_template"
                ]
                with open(
                    f"{self._jinja2_searchpath}/{declaration_template_file}", "r"
                ) as declaration_template_file_fh:
                    self._declaration_template = declaration_template_file_fh.read()

            except (KeyError, TypeError) as exc:
                raise KeyError(
                    f"as3ninja.declaration_template not valid or missing in template_configuration: {exc}"
                )
        self._transform()

    def dict(self) -> dict:
        """Returns the AS3 Declaration."""
        return self._declaration

    def json(self) -> str:
        """Returns the AS3 Declaration as JSON."""
        return self._declaration_json

    @property
    def declaration_template(self) -> str:
        """Property contains the declaration template loaded or provided during instantiation"""
        return self._declaration_template

    def _jinja2_render(self) -> str:
        """Renders the declaration using jinja2.
        Raises relevant exceptions which need to be handled by the caller.
        """
        env = Environment(  # nosec (bandit: autoescaping is not helpful for as3ninja's use-case)
            loader=ChoiceLoader(
                [
                    DictLoader({"template": self.declaration_template}),
                    FileSystemLoader(searchpath=self._jinja2_searchpath),
                ]
            ),
            trim_blocks=False,
            lstrip_blocks=False,
            keep_trailing_newline=True,
            undefined=StrictUndefined,
            autoescape=False,
        )
        env.globals["jinja2_searchpath"] = self._jinja2_searchpath + "/"
        env.globals["ninja"] = self._template_configuration
        env.globals.update(J2Ninja.functions)
        env.filters.update(J2Ninja.filters)
        env.tests.update(J2Ninja.tests)

        return env.get_template("template").render()

    def _transform(self) -> None:
        """Transforms the declaration_template using the template_configuration to an AS3 declaration.
        On error raises:

        - AS3TemplateSyntaxError on jinja2 template syntax errors
        - AS3UndefinedError for undefined variables in the declaration template
        - AS3JSONDecodeError in case the rendered declaration is not valid JSON
        """
        try:
            declaration = self._jinja2_render()

            self._declaration = json.loads(declaration)

            # remove $schema as AS3 currently fails to install declarattion when present
            # https://github.com/F5Networks/f5-appsvcs-extension/issues/173
            try:
                del self._declaration["$schema"]
            except (KeyError, TypeError):
                pass  # ignore missing $schema

            self._declaration_json = json.dumps(
                self._declaration
            )  # properly formats JSON

        except TemplateSyntaxError as exc:
            raise AS3TemplateSyntaxError(
                "AS3 declaration template caused jinja2 syntax error",
                self.declaration_template,
                exc,
            )
        except UndefinedError as exc:
            raise AS3UndefinedError(
                "AS3 declaration template tried to operate on an Undefined variable, attribute or type",
                exc,
            )
        except json.decoder.JSONDecodeError as exc:
            raise AS3JSONDecodeError("JSONDecodeError", exc)
