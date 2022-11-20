import json
from functools import partial
from os import getenv
from pathlib import Path

import httpx
import pytest
from starlette.testclient import TestClient

from as3ninja.api import app, startup

# ENV: DOCKER_TESTING=true to test docker

DOCKER_TESTING = False
if getenv("DOCKER_TESTING") == "true":
    DOCKER_TESTING = True


class RequestsApiTestClient:
    """RequestsApiTestClient wraps requests and prepends a base_url.

    :param base_url: base URL to prepend (eg. http://localhost:8000)
    """

    def __init__(self, base_url):
        self._session = httpx.Session()
        if base_url.endswith("/"):
            base_url = base_url[0:-1]
        self._base_url = base_url

    def __getattr__(self, name):
        """return _request method where the name is used to indicate the HTTP method"""
        return partial(self._request, name)

    def _request(self, verb, path, **kwargs):
        """calls requests Session request method and prepends the base URL"""
        if not path.startswith("/"):
            path = "/" + path

        url = self._base_url + path

        return self._session.request(verb, url, **kwargs)


class ApiClient:
    """generates the api_client based on module name"""

    def __init__(self):
        if DOCKER_TESTING:
            # testing actual docker container
            self._api_client = RequestsApiTestClient("http://localhost:8000")
        else:
            # testing api with starlette testclient
            self._api_client = TestClient(app)

    def __getattr__(self, name):
        return getattr(self._api_client, name)


api_client = ApiClient()


class Test_OpenAPI_UI:
    @staticmethod
    def test_ReDoc():
        response = api_client.get("/redoc")
        assert str(response.url).endswith("/api/redoc") is True
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    @staticmethod
    def test_Swagger():
        response = api_client.get("/docs")
        assert str(response.url).endswith("/api/docs") is True
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    @staticmethod
    def test_openapi_json():
        response = api_client.get("/openapi.json")
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

    @staticmethod
    def test_openapi_equals():
        _openapi_json = api_client.get("/openapi.json")
        _api_openapi_json = api_client.get("/api/openapi.json")
        assert _openapi_json.json() == _api_openapi_json.json()

    @staticmethod
    def test_default_redirect():
        response = api_client.get("/")
        assert str(response.url).endswith("/api/docs") is True
        assert "text/html" in response.headers["content-type"]


class Test_Schema:
    SCHEMA_VERSION = "3.8.1"

    @staticmethod
    def test_latest_version():
        response = api_client.get("/api/schema/latest_version")
        assert response.status_code == 200
        assert response.json()["latest_version"]

    @staticmethod
    def test_latest_schema():
        response = api_client.get("/api/schema/schema")
        assert response.status_code == 200
        assert response.json()["$schema"]

    def test_schema_version(self):
        response = api_client.get(f"/api/schema/schema?version={self.SCHEMA_VERSION}")
        assert response.status_code == 200
        assert response.json()["$schema"]

    def test_schema_non_existing_version(self):
        ver = "3.999999.999999"
        response = api_client.get(f"/api/schema/schema?version={ver}")
        assert response.status_code == 400
        assert response.json()["detail"] == f"schema version:{ver} is unknown"

    def test_schema_versions(self):
        response = api_client.get(f"/api/schema/versions")
        assert response.status_code == 200
        assert self.SCHEMA_VERSION in response.json()

    def test_schemas(self):
        response = api_client.get("/api/schema/schemas")
        assert response.status_code == 200
        assert response.json()[self.SCHEMA_VERSION]["$schema"]

    @staticmethod
    def test_schema_validate_success():
        declaration_v390__json: str = r'{"class": "AS3","action": "deploy","persist": true,"logLevel": "debug","declaration": {"class": "ADC","schemaVersion": "3.9.0","id": "C3DFeatures","label": "C3D Test","remark": "test","Sample_C3D": {"class": "Tenant","appC3D": {"class": "Application","template": "generic","webtls": {"class": "TLS_Server","certificates": [{"matchToSNI": "www.test.domain.com","certificate": "webcert1"},{"certificate": "webcert2"}],"authenticationMode": "request","authenticationTrustCA": {"bigip": "/Common/dev_chain.crt"},"crlFile": {"bigip": "/Common/dev_crl.crl"},"allowExpiredCRL": true,"c3dOCSPUnknownStatusAction": "ignore","c3dOCSP": {"use": "ocsp"},"c3dEnabled": true},"webcert1": {"class": "Certificate","remark": "test","certificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----","privateKey": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"},"webcert2": {"class": "Certificate","remark": "test","certificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----","privateKey": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"},"ocsp": {"class": "Certificate_Validator_OCSP","dnsResolver": {"bigip": "/Common/10.10.10.10"},"responderUrl": "http://oscp.responder.test.com","timeout": 299},"clienttls": {"class": "TLS_Client","clientCertificate": "defaultCert","crlFile": {"bigip": "/Common/c3d_crl.crl"},"allowExpiredCRL": true,"c3dEnabled": true,"c3dCertificateAuthority": "c3dCA","c3dCertificateLifespan": 360,"c3dCertificateExtensions": ["subject-alternative-name"],"trustCA": {"bigip": "/Common/c3d_chain.crt"}},"c3dCA": {"class": "Certificate","certificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----","privateKey": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"},"defaultCert": {"class": "Certificate","certificate": {"bigip": "/Common/default.crt"},"privateKey": {"bigip": "/Common/default.key"}}}}}}'
        declaration_v390__dict: dict = json.loads(declaration_v390__json)
        response = api_client.post("/api/schema/validate", json=declaration_v390__dict)
        assert response.status_code == 200
        assert response.json()["valid"] == True

    @staticmethod
    def test_schema_validate_invalid_schema_version():
        ver = "3.99.99"
        declaration_v390__json: str = r'{"class": "AS3","action": "deploy","persist": true,"logLevel": "debug","declaration": {"class": "ADC","schemaVersion": "3.9.0","id": "C3DFeatures","label": "C3D Test","remark": "test","Sample_C3D": {"class": "Tenant","appC3D": {"class": "Application","template": "generic","webtls": {"class": "TLS_Server","certificates": [{"matchToSNI": "www.test.domain.com","certificate": "webcert1"},{"certificate": "webcert2"}],"authenticationMode": "request","authenticationTrustCA": {"bigip": "/Common/dev_chain.crt"},"crlFile": {"bigip": "/Common/dev_crl.crl"},"allowExpiredCRL": true,"c3dOCSPUnknownStatusAction": "ignore","c3dOCSP": {"use": "ocsp"},"c3dEnabled": true},"webcert1": {"class": "Certificate","remark": "test","certificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----","privateKey": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"},"webcert2": {"class": "Certificate","remark": "test","certificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----","privateKey": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"},"ocsp": {"class": "Certificate_Validator_OCSP","dnsResolver": {"bigip": "/Common/10.10.10.10"},"responderUrl": "http://oscp.responder.test.com","timeout": 299},"clienttls": {"class": "TLS_Client","clientCertificate": "defaultCert","crlFile": {"bigip": "/Common/c3d_crl.crl"},"allowExpiredCRL": true,"c3dEnabled": true,"c3dCertificateAuthority": "c3dCA","c3dCertificateLifespan": 360,"c3dCertificateExtensions": ["subject-alternative-name"],"trustCA": {"bigip": "/Common/c3d_chain.crt"}},"c3dCA": {"class": "Certificate","certificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----","privateKey": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"},"defaultCert": {"class": "Certificate","certificate": {"bigip": "/Common/default.crt"},"privateKey": {"bigip": "/Common/default.key"}}}}}}'
        declaration_v390__dict: dict = json.loads(declaration_v390__json)
        response = api_client.post(
            f"/api/schema/validate?version={ver}", json=declaration_v390__dict
        )
        assert response.status_code == 400
        print(response.json())
        assert response.json()["detail"] == f"schema version:{ver} is unknown"

    @staticmethod
    def test_schema_validate_fail():
        invalid_declaration_v390__json: str = (
            r'{"class": "AS3","declaration": {"class": "ADC","schemaVersion": "4.9.0"}}'
        )
        invalid_declaration_v390__dict: dict = json.loads(
            invalid_declaration_v390__json
        )
        response = api_client.post(
            "/api/schema/validate", json=invalid_declaration_v390__dict
        )
        assert response.status_code == 200
        assert response.json()["valid"] == False
        assert response.json()["error"]


class Test_declaration_transform_git:
    def test_successful(self, mocker):
        if not DOCKER_TESTING:
            mocked_Gitget = mocker.patch("as3ninja.api.Gitget")
            mocked_Gitget.return_value.__enter__.return_value.repodir = str(Path.cwd())
            mocked_Gitget.return_value.__enter__.return_value.info = {
                "commit": {"id": "1234"}
            }

        response = api_client.post(
            "/api/declaration/transform/git",
            json={
                "repository": "https://github.com/simonkowallik/as3ninja",
                "branch": "edge",
                "template_configuration": "tests/testdata/api/transform_git/config.yaml",
                "declaration_template": "tests/testdata/api/transform_git/template.jinja2",
            },
        )
        assert response.status_code == 200
        assert response.json()["config"] == "yes!"
        assert response.json()["gitrepo.info"] != ""

    def test_failure(self):
        response = api_client.post(
            "/api/declaration/transform/git",
            json={
                "repository": "none",
            },
        )
        assert response.status_code == 400
        assert "repository 'none' does not exist" in response.json()["detail"]


class Test_declaration_transform:
    declaration_template = """
        {
            "class": "AS3",
            "declaration": {
                "class": "ADC",
                "schemaVersion": "3.11.0",
                "id": "urn:uuid:{{ uuid() }}",
                "{{ ninja.Tenantname }}": {
                    "class": "Tenant"
                }
            }
        }
    """

    def test_successful(self):
        template_configuration = {"Tenantname": "TestTenantName"}
        declaration_template = self.declaration_template
        response = api_client.post(
            "/api/declaration/transform",
            json={
                "template_configuration": template_configuration,
                "declaration_template": declaration_template,
            },
        )
        assert response.status_code == 200
        assert response.json()["declaration"]["TestTenantName"]
        assert len(response.json()["declaration"]["id"]) == 45

    def test_failure(self):
        template_configuration = {}
        declaration_template = self.declaration_template
        response = api_client.post(
            "/api/declaration/transform",
            json={
                "template_configuration": template_configuration,
                "declaration_template": declaration_template,
            },
        )
        assert response.status_code == 400
        assert (
            "AS3 declaration template tried to operate on an Undefined variable"
            in response.json()["detail"]
        )
        assert "has no attribute 'Tenantname'" in response.json()["detail"]


class Test_API_Startup_event:
    @staticmethod
    def test_startup(mocker):
        mocked_AS3Schema = mocker.patch("as3ninja.api.AS3Schema")
        startup()
        assert mocked_AS3Schema.called
