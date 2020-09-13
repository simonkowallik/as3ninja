# -*- coding: utf-8 -*-
"""
The AS3TemplateConfiguration module allows to compose AS3 Template Configurations from YAML, JSON or dict(s).
"""

# pylint: disable=C0330 # Wrong hanging indentation before block
# pylint: disable=C0301 # Line too long

import json
from pathlib import Path
from typing import Dict, Generator, List, Optional, Union

from pydantic import BaseModel, ValidationError
from six import iteritems

from as3ninja.exceptions import AS3TemplateConfigurationError
from as3ninja.utils import DictLike, deserialize

__all__ = ["AS3TemplateConfiguration"]


class AS3TemplateConfiguration(DictLike):
    """The AS3TemplateConfiguration module. Allows to build an AS3 Template Configuration from YAML, JSON or dict.
    Creates a AS3TemplateConfiguration instance for use with AS3Declaration.

    The Template Configuration can be created from one or more files or `dicts`.
    Globbing based on pathlib Path glob is supported to load multiple files.
    De-serialization for files is automatically performed, YAML and JSON is supported.
    If a file is included multiple times, it is only loaded once on first occurrence.
    AS3TemplateConfigurationError exception is raised when a file is not found or not readable.

    Files can be included using the as3ninja.include ``Union[str, List[str]]`` namespace in every specified configuration file.
    Files included through this namespace will not be checked for as3ninja.include and therefore cannot include further files.

    The as3ninja.include namespace is updated with entries of all as3ninja.include entries, globbing will be expanded. This helps during troubleshooting.

    If a list of inputs is provided, the input will be merged using :py:meth:`_dict_deep_update`.

    If template_configuration is ``None``, AS3TemplateConfiguration will look for the first default configuration
    file it finds in the current working directory (files are in order: `ninja.json`, `ninja.yaml`, `ninja.yml`).

    :param template_configuration: Template Configuration (Optional)
    :param base_path: Base path for any configuration file includes. (Optional)


    Example usage:

    .. code:: python

        from as3ninja.templateconfiguration import AS3TemplateConfiguration

        as3tc = AS3TemplateConfiguration([
                    {"inlineConfig": True},
                    "./config.yaml",
                    "./config.json",
                    "./includes/*.yaml"
            ])

        as3tc.dict()
        as3tc.json()
        as3tc_dict = dict(as3tc)

    """

    class TemplateConfigurationValidator(BaseModel):
        """Data Model validation and de-serialization for as3ninja.include namespace."""

        template_configuration: Union[List[Union[dict, str]], dict, str]

    def __init__(
        self,
        template_configuration: Optional[
            Union[List[Union[dict, str]], dict, str]
        ] = None,
        base_path: Optional[str] = "",
        overlay: Optional[dict] = None,
    ):
        self._includes: list = []
        self._configuration: dict = {}
        self._configuration_json: str = ""
        self._template_configurations: list = []

        self._base_path: str = base_path or ""

        if template_configuration is None:
            template_configuration = self._ninja_default_configfile()

        try:
            self.TemplateConfigurationValidator(
                template_configuration=template_configuration
            )
        except ValidationError as exc:
            raise AS3TemplateConfigurationError("Input Validation Error") from exc

        if isinstance(template_configuration, tuple):
            self._template_configurations = list(template_configuration)
        elif not isinstance(template_configuration, list):
            self._template_configurations = [template_configuration]
        else:
            self._template_configurations = template_configuration

        if overlay:
            self._template_configurations.append(overlay)

        self._deserialize_files()
        self._import_includes()  # import as3ninja.include includes

        self._merge_configuration()

        self._update_configuration_includes()
        self._tidy_as3ninja_namespace()

        self._dict = self._configuration  # enable DictLike

    def _deserialize_files(self):
        """De-serialize configuration files in self._template_configurations"""
        _template_configurations = []
        for config in self._template_configurations:
            if isinstance(config, str):  # every str is a configuration file
                # defer de-serialization to _import_includes
                _template_configurations.append(
                    {"as3ninja": {"__deserialize_file": [config]}}
                )
            else:
                _template_configurations.append(config)

        self._template_configurations = _template_configurations

        self._import_includes(defferred=True)  # import defferred file includes

    def _tidy_as3ninja_namespace(self):
        """Tidy as3ninja. namespace in the configuration.
        Removes:

          - __deserialize_file
          - removes entire as3ninja namespace if empty
        """
        if self._configuration.get("as3ninja", {}).get("__deserialize_file"):
            del self._configuration["as3ninja"]["__deserialize_file"]

        # as3ninja might be empty if was only used with __deserialize_file
        if "as3ninja" in self._configuration and not self._configuration["as3ninja"]:
            del self._configuration["as3ninja"]

    def _update_configuration_includes(self):
        """Updates as3ninja.include with the full list of included files and removes __deserialize_file"""
        if self._configuration.get("as3ninja", {}).get("include"):
            self._configuration["as3ninja"]["include"] = self._includes

    def dict(self) -> dict:
        """Returns the merged Template Configuration"""
        return self._configuration

    def json(self) -> str:
        """Returns the merged Template Configuration as JSON"""
        if not self._configuration_json:
            self._configuration_json = json.dumps(self._configuration)

        return self._configuration_json

    def _ninja_default_configfile(self) -> str:
        """Identify first config file which exists:ninja.json, ninja.yaml or ninja.yml.
        Raise AS3TemplateConfigurationError on error."""
        for ninja_configfile in ("ninja.json", "ninja.yaml", "ninja.yml"):
            if Path(self._base_path + ninja_configfile).is_file():
                return ninja_configfile

        raise AS3TemplateConfigurationError(
            f"No AS3 Ninja configuration file found (ninja.json, ninja.yaml, ninja.yml) (base_path:{self._base_path})"
        )

    def _import_includes(self, defferred: bool = False):
        """Iterates the list of Template Configurations and imports all includes in order.

        :param defferred: Include defferred includes instead of user specified as3ninja.include
        """
        _expanded_template_configurations = []

        for current_config in self._template_configurations:
            _expanded_template_configurations.append(current_config)
            if defferred:
                register = False
                includes = current_config.get("as3ninja", {}).get(
                    "__deserialize_file", []
                )
            else:
                register = True
                includes = current_config.get("as3ninja", {}).get("include", [])
                # includes can be specified as str but a list is expected by _deserialize_includes
                if isinstance(includes, str):
                    includes = [includes]

            for include_config in self._deserialize_includes(
                includes, register=register
            ):
                _expanded_template_configurations.append(include_config)

        self._template_configurations = _expanded_template_configurations

    def _path_glob(self, pattern: str) -> Generator[Path, None, None]:
        """Path(self._base_path).glob(pattern) with support for an absolute pattern."""
        _base_path = self._base_path
        if pattern.startswith("/"):
            pattern = pattern.lstrip("/")
            _base_path = _base_path + "/"

        return Path(_base_path).glob(pattern)

    def _deserialize_includes(
        self, includes: List[str], register: bool = True
    ) -> Generator:
        """Iterates and expands over the list of includes and yields the deseriealized data.

        :param includes: List of include files
        :param register: Register include file to avoid double inclusion (Default: ``True``)
        """
        for include in includes:
            if not list(self._path_glob(include)):
                # Path().glob() didn't find any file
                raise AS3TemplateConfigurationError(
                    f"Include: {str(include)} doesn't exist or not a file (base_path:{self._base_path})."
                )

            # globbing potentially results in multiple files to include
            for include_file in sorted(self._path_glob(include)):
                if not include_file.is_file():
                    raise AS3TemplateConfigurationError(
                        f"Include: {str(include_file)} doesn't exist or not a file (base_path:{self._base_path})."
                    )
                # avoid including the same configuration template multiple times
                if register:
                    if str(include_file) in self._includes:
                        continue
                    self._includes.append(str(include_file))

                yield deserialize(str(include_file))

    def _merge_configuration(self):
        """Merges _template_configurations list of dicts to a single dict"""
        for config in self._template_configurations:
            self._configuration = self._dict_deep_update(self._configuration, config)

    def _dict_deep_update(self, dict_to_update: Dict, update: Dict) -> Dict:
        """Similar to dict.update() but with full depth.

        :param dict_to_update: dict to update (will be mutated)
        :param update: dict: dict to use for updating dict_to_update

        Example:

        .. code:: python

            dict.update:
            { 'a': {'b':1, 'c':2} }.update({'a': {'d':3} })
            -> { 'a': {'d':3} }

            _dict_deep_update:
            { 'a': {'b':1, 'c':2} } with _dict_deep_update({'a': {'d':3} })
            -> { 'a': {'b':1, 'c':2, 'd':3} }

        """
        for key, value in iteritems(update):
            dict_value = dict_to_update.get(key, {})
            if not isinstance(dict_value, dict):
                dict_to_update[key] = value
            elif isinstance(value, dict):
                dict_to_update[key] = self._dict_deep_update(dict_value, value)
            else:
                dict_to_update[key] = value
        return dict_to_update
