import json

import pytest
from starlette.testclient import TestClient

from as3ninja.api import app

api_client = TestClient(app)


class Test_OpenAPI_UI:
    @staticmethod
    def test_ReDoc():
        response = api_client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    @staticmethod
    def test_Swagger():
        response = api_client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    @staticmethod
    def test_openapi_json():
        response = api_client.get("/openapi.json")
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]


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
        response = api_client.post("/api/schema/validate", json=declaration_v390__dict,)
        assert response.status_code == 200
        assert response.json()["valid"] == True

    @staticmethod
    def test_schema_validate_fail():
        invalid_declaration_v390__json: str = r'{"class": "AS3","declaration": {"class": "ADC","schemaVersion": "3.9.0"}}'
        invalid_declaration_v390__dict: dict = json.loads(
            invalid_declaration_v390__json
        )
        response = api_client.post(
            "/api/schema/validate", json=invalid_declaration_v390__dict,
        )
        assert response.status_code == 200
        assert response.json()["valid"] == False
        assert response.json()["error"]


class Test_declaration:
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

    def test_transform_successful(self):
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

    def test_transform_failure(self):
        template_configuration = {}
        declaration_template = self.declaration_template
        response = api_client.post(
            "/api/declaration/transform",
            json={
                "template_configuration": template_configuration,
                "declaration_template": declaration_template,
            },
        )
        print(response.json())
        assert response.status_code == 400
        assert "Tenantname" in response.json()["detail"]
