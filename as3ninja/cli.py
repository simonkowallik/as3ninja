# -*- coding: utf-8 -*-
"""
AS3 Ninja CLI module
"""
import json
from typing import Optional, Union

import click
from loguru import logger

from . import __version__
from .declaration import AS3Declaration
from .gitget import Gitget
from .schema import AS3Schema
from .templateconfiguration import AS3TemplateConfiguration, AS3TemplateConfigurationError
from .utils import deserialize

# TODO: figure out how click can raise an non-zero exit code on AS3ValidationError


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
    help="Declaration template file, JSON with jinja2",
)
@click.option(
    "-c",
    "--configuration-file",
    required=False,
    nargs=0,
    type=click.File("r"),
    help="JSON/YAML configuration file used to parameterize declaration template",
)
@click.argument("configuration-file", nargs=-1)
@click.option(
    "-o",
    "--output-file",
    required=False,
    type=click.File("w"),
    help="optional output file, result is written to STDOUT otherwise",
)
@click.option(
    "--validate/--no-validate",
    required=False,
    default=True,
    is_flag=True,
    help="Validate/do not validate the generated declaration against the json schema (default is to validate)",
)
@click.option(
    "--pretty", required=False, default=False, is_flag=True, help="Pretty print JSON"
)
@logger.catch
def transform(
    declaration_template: str,
    configuration_file: Optional[tuple],
    output_file: Union[str, None],
    validate: bool,
    pretty: bool,
):
    """Transforms a declaration template using the configuration file to an AS3 delcaration which is validated against the JSON schema."""
    if declaration_template:
        template = declaration_template.read()
    else:
        template = None

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
    "-o",
    "--output-file",
    required=False,
    type=click.File("w"),
    help="optional output file, result is written to STDOUT otherwise",
)
@click.option(
    "--validate/--no-validate",
    required=False,
    default=True,
    is_flag=True,
    help="Validate/do not validate the generated declaration against the json schema (default is to validate)",
)
@click.option(
    "--pretty", required=False, default=False, is_flag=True, help="Pretty print JSON"
)
@click.option(
    "-c",
    "--configuration-file",
    required=False,
    nargs=0,
    type=str,
    help="JSON/YAML configuration file used to parameterize declaration template",
)
@click.argument("configuration-file", nargs=-1)
@click.option("--repository", required=True, default=False, help="Git repository")
@click.option("--branch", required=False, default=False, help="Git branch to use")
@click.option("--commit", required=False, default=False, help="Git commit id (long)")
@click.option("--depth", required=False, default=False, help="Git clone depth")
@logger.catch
def git_transform(
    configuration_file: Optional[tuple],
    repository: str,
    branch: Union[str, None],
    commit: Union[str, None],
    depth: Union[int, None],
    output_file: Union[str, None],
    validate: bool,
    pretty: bool,
):
    """Transforms a declaration from a git repository using either the default configuration files (ninja.json/yaml/yml) or the configuration file specified through the command line.
    The AS3 delcaration which is validated against the JSON schema.
    """
    with Gitget(
        repository=repository, branch=branch, commit=commit, depth=depth
    ) as gitrepo:
        as3tc = AS3TemplateConfiguration(
            template_configuration=configuration_file,
            base_path=f"{gitrepo.repodir}/",
            overlay={"as3ninja": {"git": gitrepo.info}},
        )

        as3declaration = AS3Declaration(
            template_configuration=as3tc.dict(),
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
