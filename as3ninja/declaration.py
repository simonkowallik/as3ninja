# -*- coding: utf-8 -*-
"""The AS3Declaration module. Represents an AS3 Declaration as a python class."""
import json
from collections import abc
from typing import List, Union

from jinja2 import (
    ChoiceLoader,
    DictLoader,
    Environment,
    FileSystemLoader,
    StrictUndefined,
)
from jinja2.exceptions import TemplateSyntaxError, UndefinedError
from six import iteritems

from .filters import ninjafilters
from .functions import ninjafunctions
from .templateconfiguration import AS3TemplateConfiguration
from .utils import deserialize

__all__ = [
    "AS3Declaration",
    "AS3JSONDecodeError",
    "AS3TemplateSyntaxError",
    "AS3UndefinedError",
]


class AS3JSONDecodeError(ValueError):
    """Raised when the produced JSON cannot be decoded"""

    def __init__(self, message: str = "", original_exception=None):
        doc_highlighted = self._highlight_error(
            original_exception.doc, original_exception.lineno, original_exception.colno
        )
        super(AS3JSONDecodeError, self).__init__(
            f"{message}: {original_exception.msg}. Error pos:{original_exception.pos} on line:{original_exception.lineno} on col:{original_exception.colno}.\nJSON document:\n{doc_highlighted}"
        )

    @staticmethod
    def _highlight_error(doc: str, err_lineno: int, err_colno: int) -> str:
        """Adds line numbers and highlights the error in the JSON document.

        :param doc: (invalid) JSON document
        :param err_lineno: Erroneous line number
        :param err_colno: exact error position on erroneous line
        """
        doc_list: list = []
        lineno = 1
        lines_total = doc.count("\n")
        indent = len(str(lines_total))
        for line in doc.splitlines():
            if lineno == err_lineno:
                err_indent = indent + 1 + err_colno
                doc_list.append(
                    "{lineno:>{indent}}: {line}<---- Error line:{err_lineno}, position {err_colno}".format(
                        lineno=lineno,
                        indent=indent,
                        line=line,
                        err_lineno=err_lineno,
                        err_colno=err_colno,
                    )
                )
                doc_list.append(
                    "{_:{err_indent}}^---- Exact Error position".format(
                        _="", err_indent=err_indent
                    )
                )
            else:
                doc_list.append(
                    "{lineno:>{indent}}: {line}".format(
                        lineno=lineno, indent=indent, line=line
                    )
                )
            lineno += 1
        return "\n".join(doc_list)


class AS3UndefinedError(UndefinedError):
    """Raised if a AS3 declaration template tries to operate on ``Undefined``."""

    def __init__(self, message: str, original_exception=None):
        super(AS3UndefinedError, self).__init__(f"{message}: {str(original_exception)}")


class AS3TemplateSyntaxError(Exception):
    """Raised to tell the user that there is a problem with the AS3 declaration template."""

    def __init__(
        self, message: str, declaration_template: str, original_exception=None
    ):
        if original_exception.filename:
            with open(original_exception.filename, "r") as templatefile:
                declaration_template = templatefile.read()

        doc_highlighted = self._highlight_error(
            declaration_template, original_exception.lineno
        )
        super(AS3TemplateSyntaxError, self).__init__(
            f"{message}: {original_exception.message}\nDeclaration Template file: {original_exception.filename}\nError on line: {original_exception.lineno}\nJinja2 template code:\n{doc_highlighted}"
        )

    @staticmethod
    def _highlight_error(doc: str, err_lineno: int) -> str:
        """Adds line numbers and highlights the error in the Jinja2 template.

        :param doc: (invalid) Jinja2 template
        :param err_lineno: Erroneous line number
        """
        doc_list: list = []
        lineno = 1
        lines_total = doc.count("\n")
        indent = len(str(lines_total))
        for line in doc.splitlines():
            if lineno == err_lineno:
                doc_list.append(
                    "{lineno:>{indent}}: {line}<---- Error line:{err_lineno}".format(
                        lineno=lineno, indent=indent, line=line, err_lineno=err_lineno
                    )
                )
                marks = ["^" for _ in line]
                doc_list.append(
                    "{_:{indent}}  {marks}------- Erroneous line above".format(
                        _="", indent=indent, marks="".join(marks)
                    )
                )
            else:
                doc_list.append(
                    "{lineno:>{indent}}: {line}".format(
                        lineno=lineno, indent=indent, line=line
                    )
                )
            lineno += 1
        return "\n".join(doc_list)


class AS3Declaration:
    """Creates an AS3Declaration instance representing the AS3 declaration.

        The AS3 declaration is created using the given template configuration, which can be either a dict or list of dicts.
        If a list is provided, the member dicts will be merged using :py:meth:`_dict_deep_update`.

        Optionally a jinja2 declaration_template can be provided, otherwise it is read from the configuration.
        The template file reference is expected to be at `as3ninja.declaration_template` within the configuration.
        An explicitly specified declaration_template takes precedence over any included template.

        :param template_configuration: AS3 Template Configuration as ``dict`` or ``list``
        :param declaration_template: Optional Declaration Template as ``str`` (Default value = ``None``)
        :param jinja2_searchpath: The jinja2 search path for the FileSystemLoader. Important for jinja2 includes. (Default value = ``"."``)
    """

    def __init__(
        self,
        template_configuration: dict,
        declaration_template: str = None,
        jinja2_searchpath: str = ".",
    ):
        self._template_configuration = template_configuration
        self._declaration_template = declaration_template
        self._jinja2_searchpath = jinja2_searchpath

        if not self._declaration_template:
            try:
                declaration_template_file = self._template_configuration["as3ninja"][
                    "declaration_template"
                ]
                self._declaration_template = deserialize(
                    datasource=f"{self._jinja2_searchpath}/{declaration_template_file}",
                    return_as=str,
                )
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
    def declaration_template(self) -> Union[str, None]:
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
        env.globals.update(ninjafunctions)
        env.filters.update(ninjafilters)

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
