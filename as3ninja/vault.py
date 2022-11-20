# -*- coding: utf-8 -*-
"""
HashiCorp Vault integration
"""

# pylint: disable=C0330 # Wrong hanging indentation before block
# pylint: disable=C0301 # Line too long
# pylint: disable=E0213 # Method should have "self" as first argument
# pylint: disable=R0201 # Method could be a function

from enum import Enum
from os import getenv
from pathlib import Path
from typing import Dict, Optional, Union

import hvac
from jinja2 import pass_context
from jinja2.runtime import Context
from pydantic import BaseModel, validator

from .jinja2.j2ninja import J2Ninja
from .settings import NINJASETTINGS
from .utils import dict_filter

__all__ = ["VaultSecretsEngines", "VaultSecret", "VaultClient", "vault"]


class VaultSecretsEngines(Enum):
    """Supported Vault Secret Engines"""

    kv1 = "kv1"
    kv2 = "kv2"
    """Aliases"""
    default = "kv2"
    kv = "kv1"


class VaultSecret(BaseModel):
    """Vault Secret configuration BaseModel.

    :param path: The secret path. If `mount_point` is not specified the first path element is assumed to be the `mount_point`.
    :param mount_point: The secrets engine path. Optional.
    :param engine: The secrets engine. Optional.
    :param filter: Optional Filter to select specific data from the secret, e.g. "data.privateKey". Filter automatically prepends "data." for kv2 to replicate the same behaviour for kv1 and kv2.
    :param version: The version of the secret. Only relevant for KV2 Secrets Engine. Optional. Default: 0 (latest secret version)
    """

    path: str
    mount_point: str
    engine: Union[str, VaultSecretsEngines] = VaultSecretsEngines["default"]
    filter: Optional[str]
    version: int = 0

    def __init__(self, *args, **kwargs):
        path = kwargs.pop("path", None)
        mount_point = kwargs.pop("mount_point", None)
        if path and not mount_point:
            (mount_point, path) = self._split_mount_point_path(path)

        super().__init__(*args, mount_point=mount_point, path=path, **kwargs)

    @validator("version")
    def validate_version(cls, value):
        """Validate version"""
        if not value >= 0:
            raise ValueError("version must be >= 0")
        return value

    @validator("engine")
    def validate_engine(cls, value):
        """Validate engine against VaultSecretsEngines"""
        return VaultSecretsEngines[value]

    @validator("path", "mount_point")
    def validate_pathlike(cls, value):
        """Basic secrets path validation using pathlib.Path.
        This should work for most vault secrets paths.
        """
        if value:
            if value[0] == "/":
                return str(Path(value))
            return str(Path(f"/{value}"))
        return value

    @staticmethod
    def _split_mount_point_path(path: str) -> tuple:
        """Splits mount_point from path. The first path element is treated as the mount_point.

        :param path: path parameter
        """
        offset = 0
        if str(path)[0] == "/":
            offset = 1
        _path = str(Path(str(path)))  # normalize path
        _path = _path.split(sep="/", maxsplit=1 + offset)
        if len(_path) > offset + 1:
            return (_path[offset], _path[1 + offset])
        return (None, path)


@J2Ninja.registerfunction
class VaultClient:
    """Vault Client object, returns a hvac.v1.Client object.

    :param addr: Vault Address (url, eg. `https://myvault:8200/`)
    :param token: Vault Token to use for authentication
    :param verify: If `True` Verify TLS Certificate of Vault (Default: `True`)
    """

    _defaultClient = None

    def __init__(
        self, addr: str, token: Optional[str] = None, verify: Union[str, bool] = True
    ):
        self._client = hvac.Client(url=addr, verify=verify)
        if token:
            self._client.token = token

        if not self._client.is_authenticated():
            raise hvac.exceptions.VaultError(
                message="Could not successfully authenticate."
            )

    def Client(self) -> hvac.v1.Client:
        """Returns hvac.client callable based on VaultClient() initialization parameters."""
        return self._client

    @classmethod
    def defaultClient(cls, ctx: Context) -> hvac.v1.Client:
        """Returns a hvac.v1.Client based on system/environment settings.

        This is method is not intended to be used directly.

        First checks for existing authentication based on `vault` cli.
        If authenticated no further action is performed.

        Then check the Jinja2 Context for the namespace ``ninja.as3ninja.vault`` and
        use ``addr``, ``token`` and ``ssl_verify`` to establish a Vault connection.
        For any of the above variables that doesn't exist the respective environment variable will be used as a fallback:
        ``addr`` = ``VAULT_ADDR``
        ``token`` = `VAULT_TOKEN`
        ``ssl_verify`` = ``VAULT_SKIP_VERIFY``

        If ``VAULT_SKIP_VERIFY`` does not exist ``VAULT_SSL_VERIFY`` from the AS3 Ninja configuration file (`as3ninja.settings.json`) is used.

        :param ctx: Context: Jinja2 Context
        """
        if not cls._defaultClient:
            client = hvac.Client()
            # client might be authenticated already, e.g. when run through CLI
            if not client.is_authenticated():
                vaddr = (
                    ctx.parent.get("ninja")
                    .get("as3ninja", {})
                    .get("vault", {})
                    .get("addr", getenv("VAULT_ADDR", None))
                )
                token = (
                    ctx.parent.get("ninja")
                    .get("as3ninja", {})
                    .get("vault", {})
                    .get("token", getenv("VAULT_TOKEN", None))
                )
                verify = (
                    ctx.parent.get("ninja")
                    .get("as3ninja", {})
                    .get("vault", {})
                    .get(
                        "ssl_verify",
                        getenv("VAULT_SKIP_VERIFY", NINJASETTINGS.VAULT_SSL_VERIFY),
                    )
                )
                if isinstance(verify, str):
                    if verify in ("true", "True", "TRUE", "1"):
                        verify = False
                    else:
                        verify = True

                client = hvac.Client(url=vaddr, verify=verify)
                if token:
                    client.token = token

                if not client.is_authenticated():
                    raise hvac.exceptions.VaultError(
                        message="Could not successfully authenticate."
                    )

            cls._defaultClient = client

        return cls._defaultClient


@J2Ninja.registerfilter
@J2Ninja.registerfunction
@pass_context
def vault(
    ctx: Context,
    secret: Dict,
    client: Optional[VaultClient] = None,
    filter: Optional[str] = None,
    version: Optional[int] = None,
) -> Dict:
    """Vault filter to retrieve a secret. The secret is returned as a dict.

    :param ctx: Context: Jinja2 Context (automatically provided by jinja2)
    :param secret: secret configuration statement, automatically passed by "piping" to the vault filter
    :param client: Optional Vault client
    :param filter: Optional Filter to select specific data from the secret, e.g. "data.privateKey". Filter automatically prepends "data." for kv2 to replicate the same behaviour for kv1 and kv2.
    :param version: Optional secret version (overrides version provided by secret configuration statement)

    """
    _secret: VaultSecret = VaultSecret(**secret)

    if version:
        _secret.version = version

    if client:
        vault_client = client.Client()
    else:
        vault_client = VaultClient.defaultClient(ctx=ctx)

    if filter is None:
        filter = _secret.filter

    if _secret.engine == VaultSecretsEngines.kv2:
        if filter:
            # prepend "data." for kv2 to replicate behaviour of kv1
            filter = "data." + filter
        return dict_filter(
            vault_client.secrets.kv.v2.read_secret_version(
                path=_secret.path,
                mount_point=_secret.mount_point,
                version=_secret.version,
            ),
            filter=filter,
        )
    elif _secret.engine == VaultSecretsEngines.kv1:
        return dict_filter(
            vault_client.secrets.kv.v1.read_secret(
                path=_secret.path, mount_point=_secret.mount_point
            ),
            filter=filter,
        )
