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
    template_configuration: list = []
    if configuration_file:
        for config_file in configuration_file:
            template_configuration.append(deserialize(datasource=config_file))
    else:
        try:
            template_configuration.append(deserialize(datasource="./ninja.json"))
        except:
            # json failed, try yaml, then yml
            try:
                template_configuration.append(deserialize(datasource="./ninja.yaml"))
            except:
                template_configuration.append(deserialize(datasource="./ninja.yml"))

    if declaration_template:
        template = declaration_template.read()
    else:
        template = None

    as3d = AS3Declaration(
        declaration_template=template, template_configuration=template_configuration
    )

    if validate:
        as3s = AS3Schema()
        as3s.validate(declaration=as3d.declaration)

    if output_file:
        output_file.write(as3d.declaration_asjson)
    else:
        if pretty:
            print(json.dumps(as3d.declaration, indent=4, sort_keys=True))
        else:
            print(as3d.declaration_asjson)


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
@click.option("--repository", required=True, default=False, help="Git repository")
@click.option("--branch", required=False, default=False, help="Git branch to use")
@click.option("--commit", required=False, default=False, help="Git commit id (long)")
@click.option("--depth", required=False, default=False, help="Git clone depth")
@logger.catch
def git_transform(
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
    template_configuration: list = []
    with Gitget(
        repository=repository, branch=branch, commit=commit, depth=depth
    ) as gitrepo:
        try:
            template_configuration.append(
                deserialize(datasource=f"{gitrepo.repodir}/ninja.json")
            )
        except:
            # json failed, try yaml, then yml
            try:
                template_configuration.append(
                    deserialize(datasource=f"{gitrepo.repodir}/ninja.yaml")
                )
            except:
                template_configuration.append(
                    deserialize(datasource=f"{gitrepo.repodir}/ninja.yml")
                )
        template_configuration.append({"as3ninja": {"git": gitrepo.info}})
        as3d = AS3Declaration(
            template_configuration=template_configuration,
            jinja2_searchpath=gitrepo.repodir,
        )
        if validate:
            as3s = AS3Schema()
            as3s.validate(declaration=as3d.declaration)

        if output_file:
            output_file.write(as3d.declaration_asjson)
        else:
            if pretty:
                print(json.dumps(as3d.declaration, indent=4, sort_keys=True))
            else:
                print(as3d.declaration_asjson)
