# -*- coding: utf-8 -*-
import json
import re
from pathlib import Path
from tempfile import mkdtemp

import pytest
from jsonschema import FormatChecker
from jsonschema.exceptions import RefResolutionError

from as3ninja.exceptions import (
    AS3SchemaError,
    AS3SchemaVersionError,
    AS3ValidationError,
)
from as3ninja.schema import AS3Schema
from tests.utils import fixture_tmpdir


@pytest.fixture(scope="function")
def fixture_as3schema():
    s = AS3Schema()
    yield s
    # tear down / empty class attributes to prevent tests from influencing each other
    AS3Schema._latest_version = ""
    AS3Schema._versions = ()
    AS3Schema._schemas = {}
    AS3Schema._validators = {}


def test_schema__ref_update(fixture_as3schema):
    schema_ref_relative = {
        "a_level1": {
            "a_level2": {
                "$ref": "#a_level2",
                "a_level3": {
                    "$ref": "#a_level3",
                    "a_level4": {"somekey": "somevalue", "$ref": "#a_level4"},
                },
            }
        },
        "b_level1": {"$ref": "#b_level1", "b_level2": {"$ref": "#b_level2"}},
        "c_level1": [
            {"$ref": "#c_level1_one"},
            {"c_level2": {"$ref": "#c_level2", "c_level3": {"$ref": "#c_level3"}}},
            [{"$ref": "#c_level2_A"}, {"$ref": "#c_level2_B"}],
        ],
        "$ref": "#level1",
        10: 10,
        (1, 2): [1, 2],
        False: True,
        True: False,
    }
    schema_ref_updated = {
        "a_level1": {
            "a_level2": {
                "$ref": "https://prefix.url/path/file.json#a_level2",
                "a_level3": {
                    "$ref": "https://prefix.url/path/file.json#a_level3",
                    "a_level4": {
                        "somekey": "somevalue",
                        "$ref": "https://prefix.url/path/file.json#a_level4",
                    },
                },
            }
        },
        "b_level1": {
            "$ref": "https://prefix.url/path/file.json#b_level1",
            "b_level2": {"$ref": "https://prefix.url/path/file.json#b_level2"},
        },
        "c_level1": [
            {"$ref": "https://prefix.url/path/file.json#c_level1_one"},
            {
                "c_level2": {
                    "$ref": "https://prefix.url/path/file.json#c_level2",
                    "c_level3": {"$ref": "https://prefix.url/path/file.json#c_level3"},
                }
            },
            [
                {"$ref": "https://prefix.url/path/file.json#c_level2_A"},
                {"$ref": "https://prefix.url/path/file.json#c_level2_B"},
            ],
        ],
        "$ref": "https://prefix.url/path/file.json#level1",
        10: 10,
        (1, 2): [1, 2],
        False: True,
        True: False,
    }
    fixture_as3schema._ref_update(
        schema=schema_ref_relative, _ref_url="https://prefix.url/path/file.json"
    )
    assert schema_ref_relative == schema_ref_updated


@pytest.mark.usefixtures("fixture_as3schema")
class Test__check_version:
    @staticmethod
    def test_valid_3_8_1(fixture_as3schema):
        version = "3.8.1"
        assert version == fixture_as3schema._check_version(version=version)

    @staticmethod
    def test_not_valid_latest(fixture_as3schema):
        version = "latest"
        assert version != fixture_as3schema._check_version(version=version)

    @staticmethod
    def test_invalid(fixture_as3schema):
        version = "12.315.1231"
        with pytest.raises(AS3SchemaVersionError):
            assert version == fixture_as3schema._check_version(version=version)

    @staticmethod
    def test_minimum_version_is_3_8_0(fixture_as3schema):
        version = "3.7.0"
        with pytest.raises(AS3SchemaVersionError):
            assert version == fixture_as3schema._check_version(version=version)


@pytest.mark.usefixtures("fixture_as3schema")
class Test__check_version_format:
    @staticmethod
    def test_valid_3_8_0(fixture_as3schema):
        version = "3.8.0"
        assert None is fixture_as3schema._validate_schema_version_format(
            version=version
        )

    @staticmethod
    def test_valid_3_1_0(fixture_as3schema):
        version = "3.1.0"
        with pytest.raises(AS3SchemaVersionError):
            fixture_as3schema._validate_schema_version_format(version=version)

    @staticmethod
    def test_valid_latest(fixture_as3schema):
        version = "latest"
        assert None is fixture_as3schema._validate_schema_version_format(
            version=version
        )

    @staticmethod
    def test_valid_99_245_123(fixture_as3schema):
        version = "99.245.123"
        assert None is fixture_as3schema._validate_schema_version_format(
            version=version
        )

    @staticmethod
    def test_invalid_str(fixture_as3schema):
        version = "invalid_str"
        with pytest.raises(AS3SchemaVersionError):
            fixture_as3schema._validate_schema_version_format(version=version)


@pytest.mark.usefixtures("fixture_as3schema")
class Test_schema:
    @staticmethod
    def test_readonly(fixture_as3schema):
        with pytest.raises(AttributeError):
            fixture_as3schema.schema = {}

    @staticmethod
    def test_returns_dict(fixture_as3schema):
        assert isinstance(fixture_as3schema.schema, dict)

    @staticmethod
    def test_returns_json(fixture_as3schema):
        assert isinstance(json.loads(fixture_as3schema.schema_asjson), dict)


@pytest.mark.usefixtures("fixture_as3schema")
class Test_schemas:
    @staticmethod
    def test_readonly(fixture_as3schema):
        with pytest.raises(AttributeError):
            fixture_as3schema.schemas = {}

    @staticmethod
    def test_no_latest(fixture_as3schema):
        with pytest.raises(KeyError):
            fixture_as3schema.schemas["latest"]

    @staticmethod
    def test_is_dict(fixture_as3schema):
        assert isinstance(fixture_as3schema.schemas, dict)

    @staticmethod
    def test_contains_dicts(fixture_as3schema):
        for schema in fixture_as3schema.schemas:
            assert isinstance(fixture_as3schema.schemas[schema], dict)

    @staticmethod
    def test_is_sorted():
        """Add versions to the class schema attribute and check if they are sorted based on version"""
        schema_previous = None
        s = AS3Schema(version="3.9.0")
        s = AS3Schema(version="3.11.1")
        s = AS3Schema(version="3.10.0")
        s = AS3Schema(version="3.8.1")
        for schema in s.schemas:
            if schema_previous:
                if not re.match("^[0-9]+$", schema.replace(".", "")):
                    continue
                assert int(schema_previous.replace(".", "")) > int(
                    schema.replace(".", "")
                )
            schema_previous = schema

    @staticmethod
    def test_returns_all_schemas(fixture_as3schema):
        """make sure .schemas returns all known versions"""
        for version in fixture_as3schema.versions:
            assert isinstance(fixture_as3schema.schemas[version], dict)


@pytest.mark.usefixtures("fixture_as3schema")
class Test_version:
    @staticmethod
    def test_version_readonly(fixture_as3schema):
        with pytest.raises(AttributeError):
            fixture_as3schema.version = "1.2.3"

    @staticmethod
    def test_version_returns_str(fixture_as3schema):
        assert isinstance(fixture_as3schema.version, str)

    @staticmethod
    def test_latest_version_returns_str(fixture_as3schema):
        assert isinstance(fixture_as3schema.latest_version, str)

    @staticmethod
    def test_latest_version_converts_to_int(fixture_as3schema):
        assert isinstance(int(fixture_as3schema.latest_version.replace(".", "")), int)


@pytest.mark.usefixtures("fixture_as3schema")
class Test_versions:
    @staticmethod
    def test_returns_tuple(fixture_as3schema):
        assert isinstance(fixture_as3schema.versions, tuple)

    @staticmethod
    def test_is_sorted():
        """Load schema versions to populate the class versions attribute and check if it is sorted correctly"""
        s = AS3Schema(version="3.9.0")
        s = AS3Schema(version="3.11.1")
        s = AS3Schema(version="3.10.0")
        s = AS3Schema(version="3.8.1")
        version_previous = None
        for version in s.versions:
            if version_previous:
                assert int(version_previous.replace(".", "")) > int(
                    version.replace(".", "")
                )
            version_previous = version


class Test_specific_schema_versions:
    @staticmethod
    def test_instantiate_older_version():
        s = AS3Schema(version="3.8.1")
        assert s.schema == s.schemas["3.8.1"]

    @staticmethod
    def test_is_latest_false():
        s = AS3Schema(version="3.8.1")
        assert s.is_latest is False

    @staticmethod
    def test_is_latest_true():
        s = AS3Schema(version="latest")
        assert s.is_latest is True

    @staticmethod
    def test_implicit_is_latest_true():
        s = AS3Schema()
        assert s.is_latest is True

    @staticmethod
    def test_version_is_latest_version():
        s = AS3Schema()
        assert s.latest_version == s.version


@pytest.mark.usefixtures("fixture_as3schema")
class Test_validate_declaration:
    declaration_v390__json: str = r'{"class": "AS3","action": "deploy","persist": true,"logLevel": "debug","declaration": {"class": "ADC","schemaVersion": "3.9.0","id": "C3DFeatures","label": "C3D Test","remark": "test","Sample_C3D": {"class": "Tenant","appC3D": {"class": "Application","template": "generic","webtls": {"class": "TLS_Server","certificates": [{"matchToSNI": "www.test.domain.com","certificate": "webcert1"},{"certificate": "webcert2"}],"authenticationMode": "request","authenticationTrustCA": {"bigip": "/Common/dev_chain.crt"},"crlFile": {"bigip": "/Common/dev_crl.crl"},"allowExpiredCRL": true,"c3dOCSPUnknownStatusAction": "ignore","c3dOCSP": {"use": "ocsp"},"c3dEnabled": true},"webcert1": {"class": "Certificate","remark": "test","certificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----","privateKey": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"},"webcert2": {"class": "Certificate","remark": "test","certificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----","privateKey": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"},"ocsp": {"class": "Certificate_Validator_OCSP","dnsResolver": {"bigip": "/Common/10.10.10.10"},"responderUrl": "http://oscp.responder.test.com","timeout": 299},"clienttls": {"class": "TLS_Client","clientCertificate": "defaultCert","crlFile": {"bigip": "/Common/c3d_crl.crl"},"allowExpiredCRL": true,"c3dEnabled": true,"c3dCertificateAuthority": "c3dCA","c3dCertificateLifespan": 360,"c3dCertificateExtensions": ["subject-alternative-name"],"trustCA": {"bigip": "/Common/c3d_chain.crt"}},"c3dCA": {"class": "Certificate","certificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----","privateKey": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"},"defaultCert": {"class": "Certificate","certificate": {"bigip": "/Common/default.crt"},"privateKey": {"bigip": "/Common/default.key"}}}}}}'
    declaration_v390__dict: dict = json.loads(declaration_v390__json)
    declaration_v371__json: str = r'{"class": "ADC","schemaVersion": "3.7.1","id": "Service_Generic","Sample_misc_03": {"class": "Tenant","Application": {"class": "Application","template": "generic","testItem": {"class": "Service_Generic","virtualPort": 200,"virtualAddresses": ["192.0.2.21"],"metadata": {"example": {"value": "example","persist": true}}}}}}'
    declaration_v371__dict: dict = json.loads(declaration_v371__json)

    def test_validate_390_against_latest(self, fixture_as3schema):
        fixture_as3schema.validate(
            declaration=self.declaration_v390__dict, version="latest"
        )

    def test_validate_390_against_390(self, fixture_as3schema):
        fixture_as3schema.validate(
            declaration=self.declaration_v390__dict, version="3.9.0"
        )

    def test_validate_390_version_auto(self, fixture_as3schema):
        fixture_as3schema.validate(
            declaration=self.declaration_v390__dict, version="auto"
        )

    @pytest.mark.skip(reason="3.71 schema not valid anymore")
    def test_validate_371_against_latest(self, fixture_as3schema):
        fixture_as3schema.validate(declaration=self.declaration_v371__dict)

    def test_validate_371_against_370(self, fixture_as3schema):
        with pytest.raises(AS3SchemaVersionError):
            fixture_as3schema.validate(
                declaration=self.declaration_v371__dict, version="3.7.1"
            )

    def test_validate_371_against_381(self, fixture_as3schema):
        with pytest.raises(AS3ValidationError):
            fixture_as3schema.validate(
                declaration=self.declaration_v371__dict, version="3.8.1"
            )

    def test_validate_371_against_390(self, fixture_as3schema):
        with pytest.raises(AS3ValidationError):
            fixture_as3schema.validate(
                declaration=self.declaration_v371__dict, version="3.9.0"
            )

    def test_validate_371_against_3100(self, fixture_as3schema):
        fixture_as3schema.validate(
            declaration=self.declaration_v371__dict, version="3.10.0"
        )

    def test_validate_390_json_formatted(self, fixture_as3schema):
        fixture_as3schema.validate(declaration=self.declaration_v390__json)

    @pytest.mark.skip(reason="3.71 schema not valid anymore")
    def test_validate_370_json_formatted(self, fixture_as3schema):
        fixture_as3schema.validate(declaration=self.declaration_v371__json)

    def test_validate_390_against_381_AS3ValidationError_exception(
        self, fixture_as3schema
    ):
        """The v390 delcaration uses features not available in v3.8.1"""
        with pytest.raises(AS3ValidationError):
            fixture_as3schema.validate(
                declaration=self.declaration_v390__dict, version="3.8.1"
            )

    def test_validate_does_not_mutate_AS3Schema(self, fixture_as3schema):
        """Make sure the .schema attribute is not mutated due to updating the # references, which are supposed to be stored in a separate dict"""
        fixture_as3schema.validate(declaration=self.declaration_v390__json)
        assert (
            fixture_as3schema.schema["definitions"]["ADC_Array"]["items"][
                "$ref"
            ].startswith("#")
            is True
        )

    @pytest.mark.parametrize(
        "declaration",
        [
            """{ "class": "AS3", "declaration": { "class": "ADC", "schemaVersion": "3.11.0", "id": "invalid --> ' <--", "TurtleCorp": { "class": "Tenant", "WebApp": { "class": "Application", "template": "http", "pool_web": { "class": "Pool", "minimumMembersActive": 1, "monitors": [ "http", "tcp" ], "members": [ { "serverAddresses": [ "192.0.2.10", "192.0.2.11" ], "servicePort": 80 } ] }, "serviceMain": { "class": "Service_HTTP", "virtualAddresses": [ "10.0.1.11" ], "pool": "pool_web" } } } } }""",
            """{ "class": "AS3", "declaration": { "class": "ADC", "schemaVersion": "3.11.0", "id": "id", "label": "invalid --> ' <--", "TurtleCorp": { "class": "Tenant", "WebApp": { "class": "Application", "template": "http", "pool_web": { "class": "Pool", "minimumMembersActive": 1, "monitors": [ "http", "tcp" ], "members": [ { "serverAddresses": [ "192.0.2.10", "192.0.2.11" ], "servicePort": 80 } ] }, "serviceMain": { "class": "Service_HTTP", "virtualAddresses": [ "10.0.1.11" ], "pool": "pool_web" } } } } }""",
            """{ "class": "AS3", "declaration": { "class": "ADC", "schemaVersion": "3.11.0", "id": "id", "remark": "invalid --> \\\\ <--", "TurtleCorp": { "class": "Tenant", "WebApp": { "class": "Application", "template": "http", "pool_web": { "class": "Pool", "minimumMembersActive": 1, "monitors": [ "http", "tcp" ], "members": [ { "serverAddresses": [ "192.0.2.10", "192.0.2.11" ], "servicePort": 80 } ] }, "serviceMain": { "class": "Service_HTTP", "virtualAddresses": [ "10.0.1.11" ], "pool": "pool_web" } } } } }""",
            """{ "class": "AS3", "declaration": { "class": "ADC", "schemaVersion": "3.11.0", "id": "id", "Turtle<!invalid!>Corp": { "class": "Tenant", "WebApp": { "class": "Application", "template": "http", "pool_web": { "class": "Pool", "minimumMembersActive": 1, "monitors": [ "http", "tcp" ], "members": [ { "serverAddresses": [ "192.0.2.10", "192.0.2.11" ], "servicePort": 80 } ] }, "serviceMain": { "class": "Service_HTTP", "virtualAddresses": [ "10.0.1.11" ], "pool": "pool_web" } } } } }""",
            """{ "class": "AS3", "declaration": { "class": "ADC", "schemaVersion": "3.11.0", "id": "id", "TurtleCorp": { "class": "Tenant", "WebApp": { "class": "Application", "template": "http", "pool_web": { "class": "Pool", "minimumMembersActive": 1, "monitors": [ "http", "tcp" ], "members": [ { "serverAddresses": [ "INVALID" ], "servicePort": 80 } ] }, "serviceMain": { "class": "Service_HTTP", "virtualAddresses": [ "10.0.1.11" ], "pool": "pool_web" } } } } }""",
        ],
    )
    def test_invalid_f5formats(self, declaration, fixture_as3schema):
        """test invalid field formats against AS3 Format Checker"""
        with pytest.raises(AS3ValidationError):
            fixture_as3schema.validate(declaration=declaration)


@pytest.mark.usefixtures("fixture_as3schema")
class Test_AS3SchemaError:
    declaration_v390__json: str = r'{"class": "AS3","action": "deploy","persist": true,"logLevel": "debug","declaration": {"class": "ADC","schemaVersion": "3.9.0","id": "C3DFeatures","label": "C3D Test","remark": "test","Sample_C3D": {"class": "Tenant","appC3D": {"class": "Application","template": "generic","webtls": {"class": "TLS_Server","certificates": [{"matchToSNI": "www.test.domain.com","certificate": "webcert1"},{"certificate": "webcert2"}],"authenticationMode": "request","authenticationTrustCA": {"bigip": "/Common/dev_chain.crt"},"crlFile": {"bigip": "/Common/dev_crl.crl"},"allowExpiredCRL": true,"c3dOCSPUnknownStatusAction": "ignore","c3dOCSP": {"use": "ocsp"},"c3dEnabled": true},"webcert1": {"class": "Certificate","remark": "test","certificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----","privateKey": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"},"webcert2": {"class": "Certificate","remark": "test","certificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----","privateKey": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"},"ocsp": {"class": "Certificate_Validator_OCSP","dnsResolver": {"bigip": "/Common/10.10.10.10"},"responderUrl": "http://oscp.responder.test.com","timeout": 299},"clienttls": {"class": "TLS_Client","clientCertificate": "defaultCert","crlFile": {"bigip": "/Common/c3d_crl.crl"},"allowExpiredCRL": true,"c3dEnabled": true,"c3dCertificateAuthority": "c3dCA","c3dCertificateLifespan": 360,"c3dCertificateExtensions": ["subject-alternative-name"],"trustCA": {"bigip": "/Common/c3d_chain.crt"}},"c3dCA": {"class": "Certificate","certificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----","privateKey": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"},"defaultCert": {"class": "Certificate","certificate": {"bigip": "/Common/default.crt"},"privateKey": {"bigip": "/Common/default.key"}}}}}}'
    declaration_v390__dict: dict = json.loads(declaration_v390__json)

    def test_SchemaError(self, fixture_as3schema):
        """Test AS3SchemaError is raised when the JSON schema is broken"""
        s = fixture_as3schema
        # set AS3 type to false (which doesn't make sense and isn't valid) to provoke a jsonschema.exceptions.SchemaError
        latest_schema = list(s._schemas.keys())[0]
        s._schemas[latest_schema]["definitions"]["AS3"]["properties"]["class"][
            "type"
        ] = False
        with pytest.raises(AS3SchemaError) as excinfo:
            s.validate(declaration=self.declaration_v390__dict)
        assert "JSON Schema Error" in str(excinfo.value)

    def test_RefResolutionError(self, fixture_as3schema):
        """Test AS3SchemaError is raised when JSON Schema references cannot be resolved"""
        s = fixture_as3schema
        # set an invalid JSON Schema reference to provoke jsonschema.exceptions.RefResolutionError
        version = "3.10.0"
        _ = s.schemas[version]  # load schema
        s._schemas[version]["properties"]["declaration"]["additionalProperties"][
            "$ref"
        ] = "#/definitions/InvalidReference"

        with pytest.raises(RefResolutionError) as excinfo:
            s.validate(declaration=self.declaration_v390__dict, version=version)
        assert "definitions/InvalidReference" in str(excinfo.value)


@pytest.mark.usefixtures("fixture_tmpdir")
class Test_updateschemas:
    @staticmethod
    def test_targetdir(fixture_tmpdir):
        repodir = fixture_tmpdir + "/f5-appsvcs-extension"
        s = AS3Schema()
        s.updateschemas(repodir=repodir)
        assert Path(repodir + "/schema/latest/").exists()
