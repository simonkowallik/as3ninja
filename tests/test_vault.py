# -*- coding: utf-8 -*-
from functools import partial
from typing import Callable, Optional, Union

import hvac
import pydantic
import pytest
from mock import call

from as3ninja.settings import NINJASETTINGS
from as3ninja.vault import VaultClient, VaultSecret, VaultSecretsEngines, vault


class MockContext:
    """Mock Jinja2 Context, provide property `parent`"""

    def __init__(self, context: dict = {}):
        self.parent = {"ninja": {"as3ninja": {}}}
        if context:
            self.parent = {"ninja": {"as3ninja": {"vault": context}}}


class Mock_hvacClient:
    """is_authenticated() returns False on 1st call, true on all following calls"""

    def __init__(self):
        (self.auth, self.token) = (False, None)

    def is_authenticated(self):
        _status = self.auth
        self.auth = True
        return _status


@pytest.fixture(scope="function")
def fixture_hvacClient(mocker, monkeypatch):
    """fixture returns function which accepts v_ctx: dict, which is passed to MockContext.
    function returns VaultClient.defaultClient() with MockContext(v_ctx) passed to it
    """

    def _func(mocker, monkeypatch, v_ctx):
        mocker.patch("as3ninja.vault.hvac.Client", autospec=True)
        hvac.Client.return_value = Mock_hvacClient()
        monkeypatch.setattr(VaultClient, "_defaultClient", False)
        return VaultClient.defaultClient(ctx=MockContext(v_ctx))

    return partial(_func, mocker, monkeypatch)


class Test_VaultSecretsEngines:
    """VaultSecretEngines enum"""

    @staticmethod
    @pytest.mark.parametrize(
        ("test_input", "expected"),
        [("kv1", "kv1"), ("kv2", "kv2"), ("default", "kv2"), ("kv", "kv1")],
    )
    def test_valid_engines(test_input, expected):
        assert VaultSecretsEngines[test_input].name == expected


class Test_VaultSecret:
    """VaultSecret configuration BaseModel tests"""

    @staticmethod
    @pytest.mark.parametrize(
        "test_input",
        [
            {
                "path": "/secret/path",
                "mount_point": "/mount_point",
                "version": 1,
                "filter": None,
                "engine": "kv2",
            },
            {
                "path": "/secret/path",
                "mount_point": "/mount_point",
                "version": 2,
                "filter": None,
                "engine": "kv1",
            },
        ],
    )
    def test_explicit_settings(test_input):
        s = VaultSecret(**test_input)
        secret = s.dict()
        secret["engine"] = secret[
            "engine"
        ].name  # map actual engine to str name representation
        assert secret == test_input

    @staticmethod
    @pytest.mark.parametrize(
        ("test_input", "expected"),
        [
            (
                {"path": "/mount_point/secret/path"},
                {"path": "/secret/path", "mount_point": "/mount_point"},
            ),
            (
                {"path": "/.//mount_point//.//secret/path"},
                {"path": "/secret/path", "mount_point": "/mount_point"},
            ),
            (
                {"path": "/secret/path", "mount_point": "/mount_point"},
                {"path": "/secret/path", "mount_point": "/mount_point"},
            ),
        ],
    )
    def test_valid_paths(test_input, expected):
        s = VaultSecret(**test_input)
        secret = s.dict()
        for key in expected:
            assert secret[key] == expected[key]

    @staticmethod
    @pytest.mark.parametrize(
        ("test_input", "expected"),
        [
            (
                {"path": "/a/b", "note": "default engine is kv2"},
                {"engine": VaultSecretsEngines.kv2},
            ),
            (
                {"path": "/a/b", "engine": "default"},
                {"engine": VaultSecretsEngines.kv2},
            ),
            ({"path": "/a/b", "engine": "kv2"}, {"engine": VaultSecretsEngines.kv2}),
            ({"path": "/a/b", "engine": "kv1"}, {"engine": VaultSecretsEngines.kv1}),
            ({"path": "/a/b", "engine": "kv"}, {"engine": VaultSecretsEngines.kv1}),
        ],
    )
    def test_valid_engines(test_input, expected):
        s = VaultSecret(**test_input)
        secret = s.dict()
        for key in expected:
            assert secret[key] == expected[key]

    @staticmethod
    @pytest.mark.parametrize(
        ("test_input", "expected"),
        [
            ({"path": "/a/b", "note": "default version is 0"}, {"version": 0}),
            ({"path": "/a/b", "version": 1}, {"version": 1}),
            ({"path": "/a/b", "version": 123123123}, {"version": 123123123}),
        ],
    )
    def test_valid_versions(test_input, expected):
        s = VaultSecret(**test_input)
        secret = s.dict()
        for key in expected:
            assert secret[key] == expected[key]

    @staticmethod
    @pytest.mark.parametrize(
        "test_input",
        [{"path": "/a/b", "version": -1}, {"path": "/a/b", "version": "abc"}],
    )
    def test_invalid_versions(test_input):
        with pytest.raises(ValueError):
            VaultSecret(**test_input)

    @staticmethod
    @pytest.mark.parametrize(
        "test_input",
        [
            {"path": "/"},
            {"path": None},
            {"path": 1},
            {},
            {"mount_point": "/"},
            {"mount_point": 1},
        ],
    )
    def test_invalid_paths(test_input):
        with pytest.raises(pydantic.error_wrappers.ValidationError) as excinfo:
            VaultSecret(**test_input)
        assert "validation error" in str(excinfo.value)

    @staticmethod
    @pytest.mark.parametrize(
        ("test_input", "expected"),
        [
            ("/.//mount_point//.//secret/path", ("mount_point", "secret/path")),
            ("/mount_point/secret/path", ("mount_point", "secret/path")),
        ],
    )
    def test__split_mount_point_path(test_input, expected):
        assert VaultSecret._split_mount_point_path(test_input) == expected


class Test_VaultClient_Client:
    """Vault Client"""

    @staticmethod
    def test_is_authenticated(mocker):
        mocked_Client = mocker.patch("as3ninja.vault.hvac.Client")
        assert VaultClient(addr="http://localhost:18200", token="123")

        mocked_Client.assert_called_with(url="http://localhost:18200", verify=True)

    @staticmethod
    def test_not_authenticated(monkeypatch):
        monkeypatch.setattr(hvac.Client, "is_authenticated", lambda _: False)
        with pytest.raises(hvac.exceptions.VaultError):
            VaultClient(addr="http://localhost:18200", token="123")

    @staticmethod
    def test_interface(mocker):
        mocked_Client = mocker.patch("as3ninja.vault.hvac.Client")
        vc = VaultClient(addr="http://localhost:18200", token="123", verify=False)

        mocked_Client.assert_called_with(url="http://localhost:18200", verify=False)
        assert vc._client.token == "123"

    @staticmethod
    def test_Client_return_value(mocker):
        """test Client() returns self._client"""
        mocked_Client = mocker.patch("as3ninja.vault.hvac.Client")
        vc = VaultClient(addr="http://localhost:18200", token="123", verify=False)

        mocked_vc__client = mocker.patch.object(vc, "_client")
        mocked_Client.assert_called_with(url="http://localhost:18200", verify=False)
        assert vc.Client() == mocked_vc__client


class Test_VaultClient_DefaultClient:
    """Vault Client - DefaultClient tests"""

    @staticmethod
    def test_not_authenticated(monkeypatch):
        monkeypatch.setattr(hvac.Client, "is_authenticated", lambda _: False)
        with pytest.raises(hvac.exceptions.VaultError):
            VaultClient.defaultClient(ctx=MockContext())

    @staticmethod
    def test_no_token(fixture_hvacClient):
        """Test explicit settings via ninja.as3ninja.vault. namespace"""
        vault_config = {"addr": "http://localhost:18123", "ssl_verify": False}
        expected_call_signatures = [
            (),
            ({"url": vault_config["addr"], "verify": vault_config["ssl_verify"]},),
        ]

        vc = fixture_hvacClient(v_ctx=vault_config)

        assert hvac.Client.call_count == 2
        assert hvac.Client.call_args_list == expected_call_signatures
        assert vc.token is None

    @staticmethod
    def test_explicit_vault_config(fixture_hvacClient):
        """Test explicit settings via ninja.as3ninja.vault. namespace"""
        vault_config = {
            "addr": "http://localhost:18123",
            "token": "123",
            "ssl_verify": False,
        }
        expected_call_signatures = [
            (),
            ({"url": vault_config["addr"], "verify": vault_config["ssl_verify"]},),
        ]

        vc = fixture_hvacClient(v_ctx=vault_config)

        assert hvac.Client.call_count == 2
        assert hvac.Client.call_args_list == expected_call_signatures
        assert vc.token == vault_config["token"]

    @staticmethod
    def test_ssl_verify_default(fixture_hvacClient):
        """Test that (ssl_)verify is set to True by default"""
        vault_config = {
            "addr": "http://localhost:18123",
            "token": "123",
            "__ssl_verify__": "ssl_verify is not set, vaule is read from NINJASETTIGNS",
        }
        expected_call_signatures = [
            (),
            ({"url": vault_config["addr"], "verify": True},),
        ]

        vc = fixture_hvacClient(v_ctx=vault_config)

        assert hvac.Client.call_count == 2
        assert hvac.Client.call_args_list == expected_call_signatures
        assert vc.token == vault_config["token"]

    @staticmethod
    def test_ssl_verify_NINJASETTIGNS(fixture_hvacClient, mocker):
        """Test that (ssl_)verify read from NINJASETTIGNS when no other setting is provided"""
        vault_config = {
            "addr": "http://localhost:18123",
            "token": "123",
            "__ssl_verify__": "ssl_verify is not set, value is read from NINJASETTIGNS",
        }
        expected_call_signatures = [
            (),
            ({"url": vault_config["addr"], "verify": False},),
        ]
        mocker.patch.object(NINJASETTINGS, "VAULT_SSL_VERIFY", False)

        vc = fixture_hvacClient(v_ctx=vault_config)

        assert hvac.Client.call_count == 2
        assert hvac.Client.call_args_list == expected_call_signatures
        assert vc.token == vault_config["token"]

    @staticmethod
    def test_environment_variable_overrides(fixture_hvacClient, mocker, monkeypatch):
        """Test that environment variables are properly overridden"""
        vault_config = {
            "addr": "http://localhost:18123",
            "token": "s.xyz",
            "ssl_verify": True,
        }
        expected_call_signatures = [
            (),
            ({"url": "http://localhost:18123", "verify": True},),
        ]
        # make sure NINJASETTINGS.VAULT_SSL_VERIFY is True
        mocker.patch.object(NINJASETTINGS, "VAULT_SSL_VERIFY", True)
        # environment overrides
        monkeypatch.setenv("VAULT_ADDR", "https://127.1.1.1:8200", prepend=False)
        monkeypatch.setenv("VAULT_TOKEN", "s.abc", prepend=False)
        monkeypatch.setenv("VAULT_SKIP_VERIFY", "true", prepend=False)

        vc = fixture_hvacClient(v_ctx=vault_config)

        assert hvac.Client.call_count == 2
        assert hvac.Client.call_args_list == expected_call_signatures
        assert vc.token == "s.xyz"

    @staticmethod
    @pytest.mark.parametrize(
        ("test_input", "expected_verify"),
        [
            ("true", False),
            ("True", False),
            ("TRUE", False),
            ("1", False),
            ("tRuE", True),
            ("On", True),
            ("on", True),
            ("FALSE", True),
            ("false", True),
            ("False", True),
            ("0", True),
        ],
    )
    def test_env_VAULT_SKIP_VERIFY(
        fixture_hvacClient, mocker, monkeypatch, test_input, expected_verify
    ):
        """Test that settings are properly overridden by environment variables"""
        expected_call_signatures = [
            (),
            ({"url": "https://127.1.1.1:8200", "verify": expected_verify},),
        ]
        # make sure NINJASETTINGS.VAULT_SSL_VERIFY is True
        mocker.patch.object(NINJASETTINGS, "VAULT_SSL_VERIFY", True)
        # environment overrides
        monkeypatch.setenv("VAULT_SKIP_VERIFY", test_input, prepend=False)
        monkeypatch.setenv("VAULT_ADDR", "https://127.1.1.1:8200", prepend=False)

        fixture_hvacClient(v_ctx={})

        assert hvac.Client.call_count == 2
        assert hvac.Client.call_args_list == expected_call_signatures

    @staticmethod
    def test_existing_defaultClient(mocker, monkeypatch):
        """check that hvac.Client is not called when self._defaultClient is not None"""
        mocker.patch("as3ninja.vault.hvac.Client")
        monkeypatch.setattr(VaultClient, "_defaultClient", hvac.v1.Client())
        vc = VaultClient.defaultClient(ctx=MockContext({}))

        assert isinstance(vc, hvac.v1.Client)
        assert hvac.Client.called == False


class Test_vault:
    """vault filter"""

    @staticmethod
    @pytest.mark.parametrize(
        ("test_input", "expected_call"),
        [
            (
                {
                    "path": "/secret/path",
                    "mount_point": "/mount_point",
                    "version": 1,
                    "engine": "kv2",
                },
                [
                    (
                        call().secrets.kv.v2.read_secret_version(
                            mount_point="/mount_point", path="/secret/path", version=1
                        )
                    )
                ],
            ),
            (
                {
                    "path": "/secret/path",
                    "mount_point": "/mount_point_kv2",
                    "version": 3,
                },
                [
                    (
                        call().secrets.kv.v2.read_secret_version(
                            mount_point="/mount_point_kv2",
                            path="/secret/path",
                            version=3,
                        )
                    )
                ],
            ),
            (
                {
                    "path": "/secret/path",
                    "mount_point": "/mount_point",
                    "engine": "kv1",
                },
                [
                    (
                        call().secrets.kv.v1.read_secret(
                            mount_point="/mount_point", path="/secret/path"
                        )
                    )
                ],
            ),
        ],
    )
    def test_expected_defaultClient_calls(mocker, test_input, expected_call):
        """check for expected calls to defaultClient"""
        mocker.patch.object(VaultClient, "defaultClient", autospec=True)
        vault(ctx=MockContext(), secret=test_input)
        # print(VaultClient.defaultClient.mock_calls)
        VaultClient.defaultClient.assert_has_calls(expected_call)

    @staticmethod
    @pytest.mark.parametrize(
        ("test_input", "expected_call"),
        [
            (
                {
                    "path": "/secret/path",
                    "mount_point": "/mount_point",
                    "version": 1,
                    "engine": "kv2",
                },
                [
                    (call()),
                    (
                        call().secrets.kv.v2.read_secret_version(
                            mount_point="/mount_point", path="/secret/path", version=1
                        )
                    ),
                ],
            ),
            (
                {
                    "path": "/secret/path",
                    "mount_point": "/mount_point_kv2",
                    "version": 3,
                },
                [
                    (call()),
                    (
                        call().secrets.kv.v2.read_secret_version(
                            mount_point="/mount_point_kv2",
                            path="/secret/path",
                            version=3,
                        )
                    ),
                ],
            ),
            (
                {
                    "path": "/secret/path",
                    "mount_point": "/mount_point",
                    "engine": "kv1",
                },
                [
                    (call()),
                    (
                        call().secrets.kv.v1.read_secret(
                            mount_point="/mount_point", path="/secret/path"
                        )
                    ),
                ],
            ),
        ],
    )
    def test_expected_client_calls(mocker, test_input, expected_call):
        """check for expected calls to defaultClient"""
        mocker.patch.object(VaultClient, "Client")
        vault(ctx=MockContext(), secret=test_input, client=VaultClient)
        # print(VaultClient.Client.mock_calls)
        VaultClient.Client.assert_has_calls(expected_call)

    @staticmethod
    @pytest.mark.parametrize(
        ("test_input", "version_override"),
        [
            (
                {
                    "path": "/secret/path",
                    "mount_point": "/mount_point",
                    "version": 1,
                    "engine": "kv2",
                },
                10,
            ),
            (
                {
                    "path": "/secret/path",
                    "mount_point": "/mount_point_kv2",
                    "version": 3,
                },
                20,
            ),
            (
                {
                    "path": "/secret/path",
                    "mount_point": "/mount_point",
                    "engine": "kv1",
                },
                30,
            ),
        ],
    )
    def test_explicit_version(mocker, test_input, version_override):
        """check that the secret version is overridden when explicit version is provided to vault jinja2 filter"""
        mocker.patch.object(VaultClient, "defaultClient")
        mocked_VaultSecret = mocker.MagicMock()
        mocker.patch("as3ninja.vault.VaultSecret", return_value=mocked_VaultSecret)
        vault(ctx=MockContext(), secret=test_input, version=version_override)
        assert mocked_VaultSecret.version == version_override

    @staticmethod
    @pytest.mark.parametrize(
        ("test_secret", "expected_filter"),
        [
            (
                {
                    "path": "/secret/path",
                    "mount_point": "/mount_point",
                    "version": 1,
                    "engine": "kv2",
                    "filter": "data.key",
                },
                "data.data.key",  # kv2 prepends 'data.' automatically
            ),
            (
                {
                    "path": "/secret/path",
                    "mount_point": "/mount_point",
                    "engine": "kv1",
                    "filter": "data.key",
                },
                "data.key",
            ),
        ],
    )
    def test_expected_filters(mocker, test_secret, expected_filter):
        """check that the filter for kv1 and kv2 are applied correctly.
        kv2 should have data.data.key as a result as data. is prepended automatically."""
        mocker.patch.object(VaultClient, "Client")
        mocked_dict_filter = mocker.patch("as3ninja.vault.dict_filter")
        vault(ctx=MockContext(), secret=test_secret, client=VaultClient)

        assert mocked_dict_filter.call_args.kwargs == {"filter": expected_filter}

    @staticmethod
    @pytest.mark.parametrize(
        ("test_secret", "filter_overridden", "expected_filter"),
        [
            (
                {
                    "path": "/secret/path",
                    "mount_point": "/mount_point",
                    "version": 1,
                    "engine": "kv2",
                    "filter": "data.key",
                },
                "data.OtherKey",
                "data.data.OtherKey",  # kv2 prepends 'data.' automatically
            ),
            (
                {
                    "path": "/secret/path",
                    "mount_point": "/mount_point",
                    "version": 1,
                    "engine": "kv2",
                    "filter": "data.key",
                },
                "",  # test override with empty filter (to return complete secret)
                "",
            ),
            (
                {
                    "path": "/secret/path",
                    "mount_point": "/mount_point",
                    "engine": "kv1",
                    "filter": "data.key",
                },
                "data.OtherKey",
                "data.OtherKey",
            ),
            (
                {
                    "path": "/secret/path",
                    "mount_point": "/mount_point",
                    "engine": "kv1",
                },
                "data.newFilter",
                "data.newFilter",
            ),
        ],
    )
    def test_filter_override(mocker, test_secret, filter_overridden, expected_filter):
        """test that a manually specified filter overrides the filter in the secret definition"""
        mocker.patch.object(VaultClient, "Client")
        mocked_dict_filter = mocker.patch("as3ninja.vault.dict_filter")
        vault(
            ctx=MockContext(),
            secret=test_secret,
            client=VaultClient,
            filter=filter_overridden,
        )

        assert mocked_dict_filter.call_args.kwargs == {"filter": expected_filter}
