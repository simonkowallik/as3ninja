# -*- coding: utf-8 -*-
"""AS3 Ninja global configuration parameters"""
import json
from pathlib import Path
from typing import Union

from pydantic import BaseSettings

__all__ = ["NINJASETTINGS"]


global AS3_SCHEMA_DIRECTORY
global AS3NINJA_CONFIGFILE_NAME
AS3_SCHEMA_DIRECTORY = "/f5-appsvcs-extension"
AS3NINJA_CONFIGFILE_NAME = "as3ninja.settings.json"


global RUNTIME_CONFIG
RUNTIME_CONFIG = ["SCHEMA_BASE_PATH"]


def detect_SCHEMA_BASE_PATH() -> Path:
    """Detect where AS3 JSON Schema files are stored.

    First checks for existence of `Path.cwd()/f5-appsvcs-extension` and uses this path if found.
    Alternatively `Path.home()/.as3ninja/f5-appsvcs-extension` is used and created if it doesn't exist.
    """
    _cwd = Path(str(Path.cwd()) + AS3_SCHEMA_DIRECTORY)
    if _cwd.exists():
        return _cwd

    # create path's independently to make sure 0700 is used for both paths
    _home = Path(str(Path.home()) + "/.as3ninja")
    _home.mkdir(mode=0o700, parents=True, exist_ok=True)
    _homeSchema = Path(str(Path.home()) + "/.as3ninja" + AS3_SCHEMA_DIRECTORY)
    _homeSchema.mkdir(mode=0o700, parents=True, exist_ok=True)

    return _homeSchema


def detect_CONFIG_FILE() -> Union[Path, None]:
    """Detect if/where the AS3 Ninja config file `(as3ninja.settings.json)` is located.

    First checks for existence of `as3ninja.settings.json` and uses this file if found.
    Alternatively `Path.home()/.as3ninja/as3ninja.settings.json` is used and created if it doesn't exist.
    """

    _cwd = Path(str(Path.cwd()) + AS3NINJA_CONFIGFILE_NAME)
    if _cwd.is_file():
        return _cwd

    # create path to make sure 0700 is used
    _home = Path(str(Path.home()) + "/.as3ninja")
    _home.mkdir(mode=0o700, parents=True, exist_ok=True)

    _configfile = Path(str(Path.home()) + "/.as3ninja/" + AS3NINJA_CONFIGFILE_NAME)

    if _configfile.is_file():
        return _configfile

    _configfile.touch(mode=0o600, exist_ok=True)
    return None


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
    SCHEMA_BASE_PATH: str = str(detect_SCHEMA_BASE_PATH())
    # Github repository to fetch schema files
    SCHEMA_GITHUB_REPO: str = "https://github.com/F5Networks/f5-appsvcs-extension"

    # SSL/TLS certificate verification (True -> verify)
    VAULT_SSL_VERIFY: bool = True

    class Config:
        env_prefix = "AS3N_"
        case_sensitive = True


config_file = detect_CONFIG_FILE()

if config_file is None:
    NINJASETTINGS = NinjaSettings()

    with open(
        file=str(Path.home()) + "/.as3ninja/" + AS3NINJA_CONFIGFILE_NAME, mode="w"
    ) as cf:
        cf_json = NINJASETTINGS.dict()
        for key in RUNTIME_CONFIG:
            cf_json.pop(key)
        cf.write(json.dumps(cf_json, indent=4, sort_keys=True))
else:
    NINJASETTINGS = NinjaSettings().parse_file(path=config_file)
