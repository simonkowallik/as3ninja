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
        :param err_colno: exact error position on errorneous line
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
        doc_highlighted = self._highlight_error(
            declaration_template, original_exception.lineno
        )
        super(AS3TemplateSyntaxError, self).__init__(
            f"{message}: {original_exception.message}. Error on line:{original_exception.lineno}.\nJinja2 template:\n{doc_highlighted}"
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

        The AS3 declaration is created unsing the given template configuration, which can be either a dict or list of dicts.
        If a list is provided, the member dicts will be merged using :py:meth:`_dict_deep_update`.

        Optionally a jinja2 declaration_template can be provided, otherwise it is read from the configuration.
        The template file reference is expected to be at `as3ninja.declaration_template` within the configuration.
        An explicitly specified declaration_template takes precedence over any included template.

        :param template_configuration: Template configuration as ``dict`` or ``list``
        :param declaration_template: Optional Declaration Template as ``str`` (Default value = ``None``)
        :param jinja2_searchpath: The jinja2 search path for the FileSystemLoader. Important for jinja2 includes. (Default value = ``"."``)
    """

    def __init__(
        self,
        template_configuration: Union[dict, List[dict]],
        declaration_template: str = None,
        jinja2_searchpath: str = ".",
    ):
        self.__configuration: dict = {}

        self._template_configuration = template_configuration
        self._declaration_template = declaration_template
        self._configuration = template_configuration
        self._jinja2_searchpath = jinja2_searchpath

        if not self._declaration_template:
            try:
                declaration_template_file = self.configuration["as3ninja"][
                    "declaration_template"
                ]
                self._declaration_template = deserialize(
                    datasource=f"{self._jinja2_searchpath}/{declaration_template_file}",
                    return_as=str,
                )
            except (KeyError, TypeError) as err:
                raise KeyError(
                    f"as3ninja.declaration_template not valid or missing in template_configuration: {err}"
                )
        self._transform()

    @property
    def declaration(self) -> dict:
        """Read-Only Property returns the tranformed AS3 declaration as ``dict``"""
        return self._declaration

    @property
    def declaration_asjson(self) -> Union[str, None]:
        """Read-Only Property returns the tranformed AS3 declaration as ``str`` (contains JSON)"""
        if not self._declaration_asjson:
            self._declaration_asjson = json.dumps(self._declaration)
        return self._declaration_asjson

    @property
    def _declaration(self) -> dict:
        """Private Property: Returns the declaration as dict"""
        return self.__declaration

    @_declaration.setter
    def _declaration(self, declaration: str) -> None:
        """Private Property: sets __declaration and _declaration_asjson variables

            :param declaration: AS3 declaration
        """
        try:
            self.__declaration = json.loads(declaration)
            # this properly formats the json
            self._declaration_asjson = json.dumps(json.loads(declaration))
        except json.decoder.JSONDecodeError as exc:
            raise AS3JSONDecodeError("JSONDecodeError", exc)

    @property
    def configuration(self) -> dict:
        """Read-Only Property returns the template configuration as dict.
        This is the merged configuration in case template_configuration was a list of configurations.
        """
        return self.__configuration

    @property
    def _configuration(self) -> dict:
        """
        Private Property: Returns the template configuration as dict.
        This is the merged configuration in case template_configuration was a list of configurations.
        """
        return self.__configuration

    @_configuration.setter
    def _configuration(self, template_configuration: Union[dict, list]) -> None:
        """
        Private Property: Merges a list of template_configuration elements in case a list is specfied.

            :param template_configuration: Union[dict, list]:

        """
        if isinstance(template_configuration, list):
            for entry in template_configuration:
                self.__configuration = self._dict_deep_update(
                    self.__configuration, entry
                )
        elif isinstance(template_configuration, dict):
            self.__configuration = template_configuration
        else:
            raise TypeError(
                f"template_configuration has wrong type:{type(template_configuration)}"
            )

    def _dict_deep_update(self, dict_to_update: dict, update: dict) -> dict:
        """
        Private Method: similar to dict.update() but with full depth.

            :param dict_to_update: dict:
            :param update: dict:

        Example:

        .. code:: python

            dict.update:
            { 'a': {'b':1, 'c':2} }.update({'a': {'d':3} })
            -> { 'a': {'d':3} }

            _dict_deep_update:
            { 'a': {'b':1, 'c':2} } with _dict_deep_update({'a': {'d':3} })
            -> { 'a': {'b':1, 'c':2, 'd':3} }

        """
        for k, v in iteritems(update):
            dv = dict_to_update.get(k, {})
            if not isinstance(dv, abc.Mapping):
                dict_to_update[k] = v
            elif isinstance(v, abc.Mapping):
                dict_to_update[k] = self._dict_deep_update(dv, v)
            else:
                dict_to_update[k] = v
        return dict_to_update

    @property
    def declaration_template(self) -> Union[str, None]:
        """Read-Only Property returns the declaration template as dict or None (if non-existend)."""
        return self._declaration_template

    @property
    def template_configuration(self) -> Union[dict, list, None]:
        """
        Read-Only Property returns the template configuration(s) as specified during class initialization.
        It returns either a dict or list of dicts.
        """
        return self._template_configuration

    def _transform(self) -> None:
        """
        Private Method: Transforms the declaration_template using the template_configuration to an AS3 declaration.
        """
        env = Environment(
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
        )
        env.globals["jinja2_searchpath"] = self._jinja2_searchpath + "/"
        env.globals["ninja"] = self.configuration
        env.globals.update(ninjafunctions)
        env.filters.update(ninjafilters)

        try:
            self._declaration = env.get_template("template").render()
        except (TemplateSyntaxError, UndefinedError) as exc:
            if isinstance(exc, TemplateSyntaxError):
                raise AS3TemplateSyntaxError(
                    "AS3 declaration template caused jinja2 syntax error",
                    self.declaration_template,
                    exc,
                )
            elif isinstance(exc, UndefinedError):
                raise AS3UndefinedError(
                    "AS3 declaration template tried to operate on an Undefined variable, attribute or type",
                    exc,
                )
