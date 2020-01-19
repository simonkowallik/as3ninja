# -*- coding: utf-8 -*-
"""
AS3 Ninja CLI module
"""
import json
import sys
from typing import Optional, Union

import click
from loguru import logger

from . import __version__
from .declaration import AS3Declaration
from .gitget import Gitget
from .schema import AS3Schema
from .templateconfiguration import (
    AS3TemplateConfiguration,
    AS3TemplateConfigurationError,
)
from .utils import deserialize, failOnException

logger.remove()
log_stderr = logger.bind(task="stderr")
log_stdout = logger.bind(task="stdout")
logger.add(
    sys.stderr,
    colorize=True,
    format="<red>{level}: {message}</red>",
    filter=lambda record: record["extra"]["task"] == "stderr",
)
logger.add(
    sys.stdout,
    colorize=True,
    format="<blue>{level}:</blue> <green>{message}</green>",
    filter=lambda record: record["extra"]["task"] == "stdout",
)


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(version=__version__)
def cli() -> None:
    pass


@cli.command()
@click.option(
    "-t",
    "--declaration-template",
    required=False,
    type=click.File("r"),
    help="Declaration Template file used for transformation (Jinja2 producing JSON)",
)
@click.option(
    "-c",
    "--configuration-file",
    required=False,
    nargs=0,
    type=click.Path(),
    help="Template Configuration file(s) to parameterize the Declaration Template (multiple files allowed)",
)
@click.argument("configuration-file", nargs=-1)
@click.option(
    "-o",
    "--output-file",
    required=False,
    type=click.File("w"),
    help="Output file, STDOUT is used otherwise",
)
@click.option(
    "--validate/--no-validate",
    required=False,
    default=True,
    is_flag=True,
    help="Validate/do not validate the generated AS3 Declaration against the AS3 JSON Schema (validate is the default)",
)
@click.option(
    "--pretty",
    required=False,
    default=False,
    is_flag=True,
    help="Pretty print JSON (when printed to STDOUT)",
)
@failOnException
@log_stderr.catch(reraise=True)
def transform(
    declaration_template: str,
    configuration_file: Optional[tuple],
    output_file: Union[str, None],
    validate: bool,
    pretty: bool,
):
    """Render AS3 Declaration from local files.

    Transforms a Declaration Template using the Template Configuration file(s) to an AS3 Delcaration.

    It is then validated against the AS3 JSON Schema unless validation is disabled.

    If no Declaration Template is specified, it is read from the Template Configuration (as3ninja.declaration_template).
    If no Template Configuration is specified, the first default configuration file (ninja.json, ninja.yaml, ninja.yml). The file is expected to be in the CWD.
    """
    template = None
    if declaration_template:
        template = declaration_template.read()

    as3tc = AS3TemplateConfiguration(template_configuration=configuration_file)
    as3declaration = AS3Declaration(
        declaration_template=template, template_configuration=as3tc.dict()
    )

    if validate:
        as3s = AS3Schema()
        as3s.validate(declaration=as3declaration.dict())

    if output_file:
        output_file.write(as3declaration.json())
    else:
        if pretty:
            print(json.dumps(as3declaration.dict(), indent=4, sort_keys=True))
        else:
            print(as3declaration.json())


@cli.command()
@click.option(
    "-t",
    "--declaration-template",
    required=False,
    type=click.Path(),
    help="Declaration Template file used for transformation (Jinja2 producing JSON)",
)
@click.option(
    "-c",
    "--configuration-file",
    required=False,
    nargs=0,
    type=click.Path(),
    help="Template Configuration file(s) to parameterize the Declaration Template (multiple files allowed)",
)
@click.argument("configuration-file", nargs=-1)
@click.option(
    "-o",
    "--output-file",
    required=False,
    type=click.File("w"),
    help="Output file, STDOUT is used otherwise",
)
@click.option(
    "--validate/--no-validate",
    required=False,
    default=True,
    is_flag=True,
    help="Validate/do not validate the generated AS3 Declaration against the AS3 JSON Schema (validate is the default)",
)
@click.option(
    "--pretty",
    required=False,
    default=False,
    is_flag=True,
    help="Pretty print JSON (when printed to STDOUT)",
)
@click.option("--repository", required=True, default=False, help="Git repository")
@click.option("--branch", required=False, default=False, help="Git branch to use")
@click.option(
    "--commit", required=False, default=False, help="Git commit id or HEAD~<int>"
)
@click.option("--depth", required=False, default=False, help="Git clone depth")
@failOnException
@log_stderr.catch(reraise=True)
def git_transform(
    declaration_template: Optional[str],
    configuration_file: Optional[tuple],
    output_file: Union[str, None],
    validate: bool,
    pretty: bool,
    repository: str,
    branch: Union[str, None],
    commit: Union[str, None],
    depth: Union[int, None],
):
    """Render AS3 Declaration from Git Repository.

    Clones the Git repository with the specified options and then transforms the Declaration Template using the Template Configuration file(s) to an AS3 Delcaration.

    It is then validated against the AS3 JSON Schema unless validation is disabled.

    If no Declaration Template is specified, it is read from the Template Configuration (as3ninja.declaration_template).
    If no Template Configuration is specified, the first default configuration file (ninja.json, ninja.yaml, ninja.yml). The file is expected to be in the root of the Git repository.
    """
    with Gitget(
        repository=repository, branch=branch, commit=commit, depth=depth
    ) as gitrepo:
        as3tc = AS3TemplateConfiguration(
            template_configuration=configuration_file,
            base_path=f"{gitrepo.repodir}/",
            overlay={"as3ninja": {"git": gitrepo.info}},
        )

        if declaration_template is not None:
            with open(f"{gitrepo.repodir}/{declaration_template}", "r") as template:
                declaration_template = template.read()

        as3declaration = AS3Declaration(
            template_configuration=as3tc.dict(),
            declaration_template=declaration_template,
            jinja2_searchpath=gitrepo.repodir,
        )
        if validate:
            as3s = AS3Schema()
            as3s.validate(declaration=as3declaration.dict())

        if output_file:
            output_file.write(as3declaration.json())
        else:
            if pretty:
                print(json.dumps(as3declaration.dict(), indent=4, sort_keys=True))
            else:
                print(as3declaration.json())


@cli.command()
@click.option(
    "-d",
    "--declaration",
    required=False,
    type=click.File("r"),
    help="AS3 Declaration file (JSON) to validate",
)
@click.option(
    "-v",
    "--version",
    required=False,
    default="latest",
    help="AS3 Schema version to use for validation (e.g. 3.16.0)",
)
@failOnException
@log_stderr.catch(reraise=True)
def validate(
    declaration: str, version: Optional[str],
):
    """Validate an AS3 Declaration against the AS3 JSON Schema.

    If no version is specified, the latest available version is used."""
    as3s = AS3Schema(version=version)
    try:
        _declaration = deserialize(declaration.name)
        as3s.validate(declaration=_declaration)
        log_stdout.info(
            "Validation passed for AS3 Schema version: {}",
            as3s.version,
            feature="f-strings",
        )
    except Exception:
        raise
