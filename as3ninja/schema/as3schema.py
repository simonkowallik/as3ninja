# -*- coding: utf-8 -*-
"""
AS3 Schema Class module. Represents the AS3 JSON Schema as a python class.
"""

# pylint: disable=C0330 # Wrong hanging indentation before block
# pylint: disable=C0301 # Line too long

import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Optional, Union

from jsonschema import Draft7Validator
from jsonschema.exceptions import RefResolutionError, SchemaError, ValidationError

from ..exceptions import AS3SchemaError, AS3SchemaVersionError, AS3ValidationError
from ..gitget import Gitget
from ..settings import NINJASETTINGS
from .formatcheckers import AS3FormatChecker

__all__ = ["AS3Schema"]


class AS3Schema:
    """Creates a AS3Schema instance of specified version.
        The :py:meth:`validate` method provides AS3 Declaration validation based on the AS3 JSON Schema.

        :param version: AS3 Schema version (Default value = "latest")
    """

    _latest_version: str = ""
    _versions: tuple = ()
    _schemas: dict = {}
    _schemas_ref_updated: dict = {}
    _validators: dict = {}

    _SCHEMA_REF_URL_TEMPLATE = (
        NINJASETTINGS.SCHEMA_BASE_PATH
        + "/schema/{{version}}/as3-schema-{{version}}-*.json"
    )
    _SCHEMA_LOCAL_FSPATH = Path(NINJASETTINGS.SCHEMA_BASE_PATH + "/schema/")
    _SCHEMA_FILENAME_GLOB = "**/as3-schema-*.json"

    # IDEA: The AS3 Schema uses semantic versioning. For a given MAJOR + MINOR version the latest available PATCH version should be used for validation of the Schema.

    def __init__(self, version: str = "latest"):
        self._validate_schema_version_format(version=version)

        if not self._SCHEMA_LOCAL_FSPATH.exists():
            self.updateschemas()

        if version != "latest":
            # make sure latest version gets always loaded first
            self._load_schema(version="latest")

        self._load_schema(version=version)

        self._version = self._check_version(version=version)
        self._schema = self._schemas[self._version]

    def _load_schema(self, version: str, force: bool = False) -> None:
        """Private Method: load schema file from disk for specified version.
        ``force`` parameter can be used to force load the schema file, even if it has been read already.

            :param version: AS3 Schema version
            :param force: Force loading of Schema even if it was loaded before (Default value = False)
        """
        if version not in self._schemas or force:
            path = self._SCHEMA_LOCAL_FSPATH
            # build sorted list of schema files
            # intention is a sorted schema.schemas dict with newest version first
            schemalist: list = []
            versions: list = []

            for _schema_file in list(path.glob(self._SCHEMA_FILENAME_GLOB)):
                schemalist.append(str(_schema_file))
            schemalist.sort(key=self.__schemalist_sort_helper, reverse=True)

            if version == "latest":
                # schemalist is sorted, use first element as latest version
                version = schemalist[0].split("/")[-2]

            for schemafile in schemalist:
                version_file = schemafile.split("/")[-2]

                if version_file == "latest":
                    continue

                versions.append(version_file)

                if version == version_file:
                    try:
                        self._validate_schema_version_format(version=version_file)
                        with open(schemafile, "rb") as _schemafile_fh:
                            _schema = json.loads(_schemafile_fh.read())
                            self._schemas[version] = _schema
                    except (AS3SchemaVersionError, ValueError):
                        print(
                            f"Could not read schemafile: {schemafile}, schemafile ignored.",
                            file=sys.stderr,
                        )
            # update versions
            self._update_versions(versions=versions)

            # (re-)sort loaded schemas according to version
            self._sort_schemas()

    def _sort_schemas(self) -> None:
        """Private Method: Sorts the schemas class attribute according to version"""
        _schemas_versions = list(self._schemas.keys())
        _schemas_versions.sort(key=self.__version_sort_helper, reverse=True)

        for _schema_version in _schemas_versions:
            self._schemas[_schema_version] = self._schemas.pop(_schema_version)

    def _update_versions(self, versions: list) -> None:
        """Private Method: Updates and sorts the versions class attribute"""
        try:
            versions.pop(versions.index("latest"))
        except ValueError:
            # pass exception if 'latest' doesn't exist
            pass
        versions.sort(key=self.__version_sort_helper, reverse=True)
        self._versions = tuple(versions)

        self._latest_version = versions[0]

    def updateschemas(
        self,
        githubrepo: str = NINJASETTINGS.SCHEMA_GITHUB_REPO,
        repodir: str = NINJASETTINGS.SCHEMA_BASE_PATH,
    ) -> None:
        """Method: Fetches/Updates AS3 Schemas from the GitHub Repository.

            :param githubrepo: str: Git/Github repository to fetch AS3 Schemas from (Default value = constant NINJASETTINGS.SCHEMA_GITHUB_REPO)
            :param repodir: str: Target directory to clone to (Default value = constant NINJASETTINGS.SCHEMA_BASE_PATH)
        """
        with Gitget(repository=githubrepo, repodir=repodir, force=True):
            self._load_schema(version="latest", force=True)

    def _check_version(self, version: str) -> str:
        """Private Method: _check_version checks if the specified version exists in available schemas.
        In case the specified schema version is not loaded, it will load the version.
        It converts "latest" to the actual version.

        The checked version is returned as str.

            :param version: str: AS3 Schema version
        """
        if version == "latest":
            return self._latest_version

        if version in self.versions:
            if version not in self.schemas:
                self._load_schema(version=version)
            return version

        raise AS3SchemaVersionError(f"schema version:{version} is unknown")

    @property
    def latest_version(self) -> str:
        """Property: returns the latest AS3 schema version as str."""
        return self._latest_version

    @staticmethod
    def __version_sort_helper(value: str) -> int:
        """Private Method: A sort helper. converts value: str to int and removes "."

            :param value: str: A version str (example: "3.8.1")
        """
        # could be a lambda but this staticmethod improves documentation.
        return int(value.replace(".", ""))

    @staticmethod
    def _validate_schema_version_format(version: str) -> None:
        """Private Method: validates the format and minimum version.

            :param version: str: AS3 Schema version
        """
        if version != "latest":
            try:
                _ver = int(version.replace(".", ""))
                if _ver < 380:
                    raise AS3SchemaVersionError(
                        f"Minimum AS3 Schema version is 3.8.0, requested version:{version}"
                    )
            except Exception as exc:
                raise AS3SchemaVersionError(
                    f"version:{version} is not a valid version string, exception occurred:{exc}"
                )

    @staticmethod
    def __schemalist_sort_helper(value: str) -> int:
        """Private Method: A sort helper.

        Sorts based on the schema version (converted to int).

            :param value: str: Path to the schema file (example: f5-appsvcs-extension/schema/3.8.1/as3-schema.json)
        """
        value = value.split("/")[-2].replace(".", "")
        try:
            return int(value)
        except ValueError:
            # extracted value isn't convertible to int, for example for 'latest'
            return 0

    @property
    def is_latest(self) -> bool:
        """Property: returns bool(True) if this instance has the latest Schema version available. Returns False otherwise."""
        return self.version == self._latest_version

    @property
    def versions(self) -> tuple:
        """Property: returns all versions available as a sorted tuple."""
        return self._versions

    @property
    def version(self) -> str:
        """Property: returns the Schema version of this AS3 Schema instance as str."""
        return self._version

    @property
    def schema(self) -> dict:
        """Property: returns the Schema of this AS3 Schema instance as dict."""
        return self._schema

    @property
    def schema_asjson(self) -> str:
        """Property: returns the Schema as JSON of this AS3 Schema instance as a python str."""
        return json.dumps(self.schema)

    @property
    def schemas(self) -> dict:
        """Property: returns all known AS3 Schemas as dict."""
        for _ver in self.versions:
            self._load_schema(version=_ver)
        return self._schemas

    def _ref_update(self, schema: dict, _ref_url: str) -> None:
        """Private Method: _ref_update performs an in-place update of relative $ref (starting with #) into absolute references by prepending _ref_url.

        See: https://github.com/Julian/jsonschema/issues/570

            :param schema: The AS3 Schema
            :param _ref_url: The URL used to update references
        """
        for k in schema:
            if isinstance(k, (dict, list)):
                self._ref_update(schema=k, _ref_url=_ref_url)
            elif k == "$ref" and schema.get(k).startswith("#"):
                schema[k] = _ref_url + schema.get(k)
            elif isinstance(schema, dict) and isinstance(schema.get(k), (dict, list)):
                self._ref_update(schema=schema.get(k), _ref_url=_ref_url)

    def _build_ref_url(self, version: str) -> str:
        """Private Method: _build_ref_url builds the absolute filesystem url to the AS3 Schema file for specified version.

            :param version: The AS3 Schema version
        """
        url = Path(self._SCHEMA_REF_URL_TEMPLATE.replace("{{version}}", version))
        url = list(Path(url.parent).glob(url.name))
        if len(url) > 1:
            raise ValueError(
                f"Expected to find a single AS3 Schema file, found: {len(url)}, urls:{url}"
            )
        return url[0].as_uri()

    def _schema_ref_update(self, version: str) -> dict:
        """Private Method: _schema_ref_update returns the AS3 Schema for specified version with updated references.

            :param version: The AS3 Schema version
        """
        # do not mutate schema, create full copy instead
        _schema = deepcopy(self.schemas[version])
        self._ref_update(
            schema=_schema, _ref_url=self._build_ref_url(version=version),
        )

        return _schema

    def _validator(self, version: str) -> None:
        """Creates jsonschema.Draft7Validator for specified AS3 schema version.
        Will check schema is valid and raise a jsonschema SchemaError otherwise.
        Memoizes the Draft7Validator instance for faster re-use.

            :param version: AS3 schema version
        """

        # create validator and memoize if it doesn't exist
        if version not in self._validators:
            _schema = self._schema_ref_update(version=version)
            validator = Draft7Validator(
                schema=_schema, format_checker=AS3FormatChecker(),
            )
            validator.check_schema(_schema)  # check schema is valid
            self._validators[version] = validator  # memoize validator

        return self._validators[version]

    def validate(
        self, declaration: Union[dict, str], version: Optional[str] = None
    ) -> None:
        """Method: Validates a declaration against the AS3 Schema. Raises a AS3ValidationError on failure.

            :param declaration: Declaration to be validated against the AS3 Schema.
            :param version: Allows to validate the declaration against the specified version
                    instead of this AS3 Schema instance version. If set to "auto", the version of the declaration is used.
        """
        if isinstance(declaration, str):
            declaration = json.loads(declaration)

        if not version:
            version = self.version
        elif version == "auto":
            version = declaration["declaration"]["schemaVersion"]
        else:
            version = self._check_version(version=version)

        try:
            validator = self._validator(version)
            validator.validate(declaration)
        except ValidationError as exc:
            raise AS3ValidationError("AS3 Validation Error: ", exc) from exc
        except (SchemaError) as exc:
            raise AS3SchemaError("JSON Schema Error", exc)
