# -*- coding: utf-8 -*-
"""All AS3 Ninja exceptions."""

# pylint: disable=C0330 # Wrong hanging indentation before block
# pylint: disable=C0301 # Line too long

from subprocess import SubprocessError

from jinja2.exceptions import UndefinedError
from jsonschema.exceptions import SchemaError, ValidationError

__all__ = [
    "AS3JSONDecodeError",
    "AS3TemplateSyntaxError",
    "AS3UndefinedError",
    "GitgetException",
    "AS3SchemaVersionError",
    "AS3SchemaError",
    "AS3ValidationError",
    "AS3TemplateConfigurationError",
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


class AS3UndefinedError(UndefinedError):
    """Raised if a AS3 declaration template tries to operate on ``Undefined``."""

    def __init__(self, message: str, original_exception=None):
        super(AS3UndefinedError, self).__init__(f"{message}: {str(original_exception)}")


class GitgetException(SubprocessError):
    """Gitget Exception, subclassed SubprocessError Exception"""


class AS3TemplateConfigurationError(ValueError):
    """Raised when a problem occurs during building the Template Configuration."""


class AS3SchemaError(SchemaError):
    """Raised when AS3 Schema is erroneous, eg. does not adhere to jsonschema standards."""

    def __init__(self, message: str = "", original_exception=None):
        # super(AS3SchemaError, self).__init__(f"{message}: {str(original_exception)}")
        super().__init__(
            message=message + original_exception.message,
            validator=original_exception.validator,
            path=original_exception.path,
            cause=original_exception.cause,
            context=original_exception.context,
            validator_value=original_exception.validator_value,
            instance=original_exception.instance,
            schema=original_exception.schema,
            schema_path=original_exception.schema_path,
            parent=original_exception.parent,
        )


class AS3SchemaVersionError(ValueError):
    """AS3 Schema Version Error, version is likely invalid or unknown."""


class AS3ValidationError(ValidationError):
    """Validation of AS3 declaration against AS3 Schema produced an error."""

    def __init__(self, message: str = "", original_exception=None):
        if original_exception:
            super().__init__(
                message=message + original_exception.message,
                validator=original_exception.validator,
                path=original_exception.path,
                cause=original_exception.cause,
                context=original_exception.context,
                validator_value=original_exception.validator_value,
                instance=original_exception.instance,
                schema=original_exception.schema,
                schema_path=original_exception.schema_path,
                parent=original_exception.parent,
            )
        else:
            super().__init__(message=message)
