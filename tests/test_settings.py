# -*- coding: utf-8 -*-
from pathlib import Path

import mock
import pytest
from mock import call
from pydantic import ValidationError

from as3ninja.settings import NinjaSettings, NinjaSettingsLoader


class Test_NinjaSettings:
    @staticmethod
    def test_required_attributes():
        njs = NinjaSettings()
        assert "GITGET_TIMEOUT" in njs.dict()
        assert "GITGET_SSL_VERIFY" in njs.dict()
        assert "GITGET_PROXY" in njs.dict()
        assert "SCHEMA_BASE_PATH" in njs.dict()
        assert "SCHEMA_GITHUB_REPO" in njs.dict()
        assert "VAULT_SSL_VERIFY" in njs.dict()

    @staticmethod
    def test_forbid_extra_attributes():
        with pytest.raises(ValidationError):
            NinjaSettings(EXTRA_ATTRIBUTES_ARE_FORBIDDEN=True)

    @staticmethod
    def test_attributes_from_env(monkeypatch):
        """
        Test environment variables override defaults
        """
        monkeypatch.setenv("AS3N_GITGET_TIMEOUT", "1234", prepend=False)
        monkeypatch.setenv("AS3N_GITGET_SSL_VERIFY", "False", prepend=False)
        monkeypatch.setenv("AS3N_GITGET_PROXY", "http://proxy:8080", prepend=False)
        monkeypatch.setenv(
            "AS3N_SCHEMA_GITHUB_REPO", "SCHEMA_GITHUB_REPO", prepend=False
        )
        monkeypatch.setenv("AS3N_VAULT_SSL_VERIFY", "False", prepend=False)

        njs = NinjaSettings()
        assert njs.dict()["GITGET_TIMEOUT"] == 1234
        assert njs.dict()["GITGET_SSL_VERIFY"] is False
        assert njs.dict()["GITGET_PROXY"] == "http://proxy:8080"
        assert njs.dict()["SCHEMA_GITHUB_REPO"] == "SCHEMA_GITHUB_REPO"
        assert njs.dict()["VAULT_SSL_VERIFY"] is False


class Test_NinjaSettingsLoader_methods:
    @staticmethod
    def test_save_config(mocker):
        """
        Test config write functionality
        Also: Must not write RUNTIME_CONFIG keys
        """
        mocked_open = mocker.patch("builtins.open", mock.mock_open())
        mocked_self = mock.Mock
        mocked_self.AS3NINJA_CONFIGFILE_NAME = "as3ninja.config.json"
        mocked_self.RUNTIME_CONFIG = ["SCHEMA_BASE_PATH"]
        mocked_self._settings = mock.Mock()
        mocked_self._settings.dict.return_value = {
            "FOO": "BAR",
            "SCHEMA_BASE_PATH": "SCHEMA_BASE_PATH",
        }
        NinjaSettingsLoader._save_config(mocked_self)

        mocked_open_handle = mocked_open()
        mocked_open_handle.write.assert_called_once_with(
            '{\n    "FOO": "BAR"\n}'
        )  # check this is written to the config file

    @staticmethod
    def test_detect_schema_base_path(mocker):
        mP_exists = mocker.patch.object(Path, "exists", return_value=False)
        mP_home = mocker.patch.object(Path, "home")
        mP_mkdir = mocker.patch.object(Path, "mkdir")

        # returns str (a path)
        assert isinstance(NinjaSettingsLoader._detect_schema_base_path(), str)

        # Path.exists() called once
        assert mP_exists.call_count == 1

        # Path.home() called twice
        assert mP_home.call_count == 2

        # Path.mkdir() called twice with the options listed
        mP_mkdir.assert_has_calls(
            [
                call(mode=448, parents=True, exist_ok=True),
                call(mode=448, parents=True, exist_ok=True),
            ]
        )

    @staticmethod
    def test_detect_schema_base_path__exists(mocker):
        mP_exists = mocker.patch.object(Path, "exists", return_value=True)

        # returns str (a path)
        _schema_base_path = NinjaSettingsLoader._detect_schema_base_path()
        assert isinstance(_schema_base_path, str)
        assert NinjaSettingsLoader.AS3_SCHEMA_DIRECTORY in _schema_base_path

        # Path.exists() called once
        assert mP_exists.call_count == 1

    @staticmethod
    def test_detect_config_file__noConfigFile(mocker):
        mP_is_file = mocker.patch.object(
            Path, "is_file", return_value=False
        )  # No config file exists at all
        mocker.patch.object(Path, "home")
        mP_mkdir = mocker.patch.object(Path, "mkdir")
        mP_touch = mocker.patch.object(Path, "touch")

        # returns None
        assert NinjaSettingsLoader._detect_config_file() is None

        # Path.is_file() called twice
        assert mP_is_file.call_count == 2

        # Path.touch() called with the options listed
        mP_touch.assert_has_calls([call(mode=384, exist_ok=True)])

        # Path.mkdir() called with the options listed
        mP_mkdir.assert_has_calls([call(mode=448, parents=True, exist_ok=True)])

    @staticmethod
    def test_detect_config_file__exists(mocker):
        mP_is_file = mocker.patch.object(
            Path, "is_file", return_value=True
        )  # config file found on first try
        mocker.patch.object(Path, "home")
        mP_mkdir = mocker.patch.object(Path, "mkdir")
        mP_touch = mocker.patch.object(Path, "touch")

        # returns config file
        _cfgfile = NinjaSettingsLoader._detect_config_file()
        assert isinstance(_cfgfile, str)
        assert "as3ninja" in _cfgfile

        # Path.is_file() called once only (file found)
        assert mP_is_file.call_count == 1

        # Path.touch() not called
        assert mP_touch.call_count == 0

        # Path.mkdir() not called
        mP_mkdir.call_count == 0


class Test_NinjaSettingsLoader:
    @staticmethod
    def test_no_config_file(mocker):
        """
        Test code path for non-existing config file in __init__
        """
        mocker.patch.object(
            NinjaSettingsLoader, "_detect_config_file", return_value=None
        )
        mocker.patch.object(NinjaSettingsLoader, "_save_config")

        NSL = NinjaSettingsLoader()

        # check that NinjaSettings is returned
        assert isinstance(NSL(), NinjaSettings)

    @staticmethod
    def test_config_file_exists(mocker):
        """
        Test code path for non-existing config file in __init__
        """
        mocker.patch.object(
            NinjaSettingsLoader,
            "_detect_config_file",
            return_value="path/to/config.file",
        )
        mocker.patch.object(NinjaSettingsLoader, "_detect_schema_base_path")
        mocker.patch("as3ninja.settings.NinjaSettings")
        mocked_deserialize = mocker.patch("as3ninja.settings.deserialize")

        NSL = NinjaSettingsLoader()
        _ = NSL()

        # deserialize called with return value from _detect_config_file
        mocked_deserialize.assert_called_once_with("path/to/config.file")
