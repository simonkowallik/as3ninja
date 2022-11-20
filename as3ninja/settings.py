# -*- coding: utf-8 -*-
"""
AS3 Ninja global configuration parameters.
"""

# pylint: disable=C0330 # Wrong hanging indentation before block
# pylint: disable=C0301 # Line too long
# pylint: disable=R0903 # Too few public methods

import json
from pathlib import Path
from typing import Union

from pydantic import BaseSettings

from .utils import deserialize

__all__ = ["NINJASETTINGS"]


class NinjaSettings(BaseSettings):
    """AS3 Ninja Settings class.

    Holds the default configuration for AS3 Ninja.

    Reads from $CWD/as3ninja.settings.json if it exists, otherwise from `$HOME/.as3ninja/as3ninja.settings.json`.
    If none of the configuration files exist, it creates `$HOME/.as3ninja/as3ninja.settings.json` and writes the current configuration (default + settings overwritten by ENV vars).

    Any setting can be overwritten using environment variables. The ENV variable has a prefix of `AS3N_` + name of the setting.
    The environment variables take precedence over any setting in the configuration file.

    """

    # Timeout for a Gitget operation
    GITGET_TIMEOUT: int = 120
    # SSL/TLS certificate verification (True -> verify)
    GITGET_SSL_VERIFY: bool = True
    # Proxy Server
    GITGET_PROXY: str = ""

    # Base path for Schema files
    SCHEMA_BASE_PATH: str = ""
    # Github repository to fetch schema files
    SCHEMA_GITHUB_REPO: str = "https://github.com/F5Networks/f5-appsvcs-extension"

    # SSL/TLS certificate verification (True -> verify)
    VAULT_SSL_VERIFY: bool = True

    class Config:
        """Configuration for NinjaSettings BaseSettings class"""

        env_prefix = "AS3N_"
        case_sensitive = True
        extra = "forbid"  # forbid extra attributes not explicitly listed above


class NinjaSettingsLoader:
    """
    The NinjaSettingsLoader class is an utility class which will return a callable instance which in fact returns an instance of NinjaSettings.
    NinjaSettingsLoader contains utility functions to detect the config file and the SCHEMA_BASE_PATH, it will also create the config file if
    it does not yet exist.
    """

    AS3_SCHEMA_DIRECTORY = "/f5-appsvcs-extension"
    AS3NINJA_CONFIGFILE_NAME = "as3ninja.settings.json"

    RUNTIME_CONFIG = ["SCHEMA_BASE_PATH"]

    _settings: NinjaSettings = NinjaSettings()

    def __init__(self):
        config_file = self._detect_config_file()

        if config_file:
            _config = deserialize(config_file)
            self._settings = NinjaSettings().parse_obj(
                {**_config, **{"SCHEMA_BASE_PATH": self._detect_schema_base_path()}}
            )
        else:
            self._settings = NinjaSettings(
                SCHEMA_BASE_PATH=self._detect_schema_base_path()
            )
            self._save_config()

    def __call__(self) -> NinjaSettings:
        """
        Returns instance of NinjaSettings.
        """
        return self._settings

    def _save_config(self) -> None:
        """
        Saves the current settings as JSON to the configuration file in ~/.as3ninja/.
        It removes any RUNTIME_CONFIG keys before saving.
        """
        with open(
            file=str(Path.home()) + "/.as3ninja/" + self.AS3NINJA_CONFIGFILE_NAME,
            mode="w",
        ) as configfile_handle:
            cf_json = self._settings.dict()
            for key in self.RUNTIME_CONFIG:  # remove runtime only config variables
                cf_json.pop(key)
            configfile_handle.write(json.dumps(cf_json, indent=4, sort_keys=True))

    @classmethod
    def _detect_schema_base_path(cls) -> str:
        """Detect where AS3 JSON Schema files are stored.

        First checks for existence of `Path.cwd()/f5-appsvcs-extension` and uses this path if found.
        Alternatively `Path.home()/.as3ninja/f5-appsvcs-extension` is used and created if it doesn't exist.
        """
        _cwd = Path(str(Path.cwd()) + cls.AS3_SCHEMA_DIRECTORY)
        if _cwd.exists():
            return str(_cwd)

        # create path's independently to make sure 0700 is used for both paths
        _home = Path(str(Path.home()) + "/.as3ninja")
        _home.mkdir(mode=0o700, parents=True, exist_ok=True)
        _home_schema = Path(str(Path.home()) + "/.as3ninja" + cls.AS3_SCHEMA_DIRECTORY)
        _home_schema.mkdir(mode=0o700, parents=True, exist_ok=True)

        return str(_home_schema)

    @classmethod
    def _detect_config_file(cls) -> Union[str, None]:
        """Detect if/where the AS3 Ninja config file `(as3ninja.settings.json)` is located.

        First checks for existence of `as3ninja.settings.json` and uses this file if found.
        Alternatively `Path.home()/.as3ninja/as3ninja.settings.json` is used and created if it doesn't exist.
        """

        _config_in_cwd = Path(str(Path.cwd()) + "/" + cls.AS3NINJA_CONFIGFILE_NAME)
        if _config_in_cwd.is_file():
            return str(_config_in_cwd)

        # create path to make sure 0700 is used
        _home = Path(str(Path.home()) + "/.as3ninja")
        _home.mkdir(mode=0o700, parents=True, exist_ok=True)

        _configfile = Path(
            str(Path.home()) + "/.as3ninja/" + cls.AS3NINJA_CONFIGFILE_NAME
        )

        if _configfile.is_file():
            return str(_configfile)

        _configfile.touch(mode=0o600, exist_ok=True)
        return None


NSL = NinjaSettingsLoader()

NINJASETTINGS = NSL()
