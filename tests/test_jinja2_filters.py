# -*- coding: utf-8 -*-
from os import stat
from uuid import UUID

import pytest
from jinja2 import DictLoader, Environment
from jinja2.runtime import Context

from as3ninja.jinja2 import J2Ninja
from as3ninja.jinja2.filterfunctions import *
from as3ninja.jinja2.filters import *
from tests.test_api import Test_API_Startup_event
from tests.utils import format_json


def test_J2Ninja_filters_is_dict():
    assert type(J2Ninja.filters) == dict


class Test_Base64:
    @staticmethod
    def test_b64encode():
        decoded = r"123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
        encoded = r"MTIzNDU2Nzg5Ojs8PT4/QEFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaW1xdXl9gYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXp7fH1+"
        assert b64encode(decoded) == encoded

    @staticmethod
    def test_b64decode():
        decoded = r"123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
        encoded = r"MTIzNDU2Nzg5Ojs8PT4/QEFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaW1xdXl9gYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXp7fH1+"
        assert b64decode(encoded) == decoded

    @staticmethod
    def test_b64encode_binary():
        decoded = b"\xc3\xab\x8f\xf17 \xe8\xad\x90G\xdd9Fk<\x89t\xe5\x92\xc2\xfa8=J9`qL\xae\xf0\xc4\xf2"
        encoded = "w6uP8Tcg6K2QR905Rms8iXTlksL6OD1KOWBxTK7wxPI="
        assert b64encode(decoded) == encoded
        assert isinstance(encoded, str)

    @staticmethod
    def test_b64decode_binary():
        decoded = b"\xc3\xab\x8f\xf17 \xe8\xad\x90G\xdd9Fk<\x89t\xe5\x92\xc2\xfa8=J9`qL\xae\xf0\xc4\xf2"
        encoded = "w6uP8Tcg6K2QR905Rms8iXTlksL6OD1KOWBxTK7wxPI="
        assert b64decode(encoded) == decoded
        assert isinstance(decoded, bytes)

    @staticmethod
    def test_b64encode_urlsafe():
        decoded = r"123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
        encoded = r"MTIzNDU2Nzg5Ojs8PT4_QEFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaW1xdXl9gYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXp7fH1-"
        assert b64encode(decoded, urlsafe=True) == encoded

    @staticmethod
    def test_b64decode_urlsafe():
        decoded = r"123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
        encoded = r"MTIzNDU2Nzg5Ojs8PT4_QEFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaW1xdXl9gYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXp7fH1-"
        assert b64decode(encoded, urlsafe=True) == decoded


class Test_jsonify:
    @staticmethod
    def test_simple_json():
        teststring = '{"json":true}'
        expectation = '"{\\"json\\":true}"'

        assert jsonify(teststring) == expectation

    @staticmethod
    def test_json_noquote():
        teststring = '{"json":true}'
        expectation = '{\\"json\\":true}'

        assert jsonify(teststring, quote=False) == expectation


def test_uuid():
    myuuid = uuid("")
    assert isinstance(myuuid, str)
    assert isinstance(UUID(myuuid), UUID)


class Test_env:
    @staticmethod
    def test_exists(monkeypatch):
        """
        Variable exists and is not empty
        """
        monkeypatch.setenv("TEST_ENV_VAR", "variable exists", prepend=False)
        assert env("TEST_ENV_VAR") == "variable exists"
        assert isinstance(env("TEST_ENV_VAR"), str)

    @staticmethod
    def test_empty(monkeypatch):
        """
        Variable exists but is empty
        """
        monkeypatch.setenv("TEST_ENV_VAR", "", prepend=False)
        assert env("TEST_ENV_VAR") == ""
        assert isinstance(env("TEST_ENV_VAR"), str)

    @staticmethod
    def test_empty_with_default(monkeypatch):
        """
        Variable exists but is empty. default value is set but doesn't apply as the variable exists.
        """
        monkeypatch.setenv("TEST_ENV_VAR", "", prepend=False)
        assert env("TEST_ENV_VAR", default="default value") == ""
        assert isinstance(env("TEST_ENV_VAR"), str)

    @staticmethod
    def test_default(monkeypatch):
        """
        Variable does not exist but a default value is set.
        """
        monkeypatch.delenv("TEST_ENV_VAR", raising=False)
        assert env("TEST_ENV_VAR", default="default value") == "default value"
        assert isinstance(env("TEST_ENV_VAR"), str)


class Test_uuid:
    @staticmethod
    def test_simple():
        my_uuid = uuid("")
        assert isinstance(my_uuid, str)
        assert isinstance(UUID(my_uuid), UUID)


class Test_to_list:
    @staticmethod
    def test_str():
        assert to_list("foo bar") == ["foo bar"]

    @staticmethod
    def test_int():
        assert to_list(245) == [245]

    @staticmethod
    def test_list():
        assert to_list(["foo", "bar"]) == ["foo", "bar"]


class Test_readfile:
    @staticmethod
    def test_textfile_ascii():
        result = readfile(Context, "tests/testdata/functions/iterfiles/text/file.txt")
        assert isinstance(result, str)

    @staticmethod
    def test_textfile_utf8():
        with pytest.raises(UnicodeDecodeError):
            result = readfile(Context, "tests/testdata/functions/utf8.txt")

    @staticmethod
    def test_non_existing_file_missingOk():
        result = readfile(Context, "does/not/exist.ext", missing_ok=True)
        assert isinstance(result, str)
        assert result == ""

    @staticmethod
    def test_non_existing_file():
        with pytest.raises(OSError):
            readfile(Context, "does/not/exist.ext", missing_ok=False)


class Test_ninjutsu:
    @staticmethod
    def _get_env(declaration_template: str, template_configuration: dict):
        env = Environment(
            loader=DictLoader({"template": declaration_template}),
            trim_blocks=False,
            lstrip_blocks=False,
        )
        env.filters.update({"ninjutsu": ninjutsu, "readfile": readfile})
        env.globals["ninja"] = template_configuration
        return env

    def test_ninjutsu(self):
        declaration_template: str = """{
        {% set myns = namespace() -%}
        {% set myns.var = "some value" -%}
        {{ninja.bfile | readfile | ninjutsu}}
        }"""
        template_configuration: dict = {
            "a": "from_config",
            "bfile": "tests/testdata/filters/ninjutsu.j2",
        }
        expected_result = '{"from_config": "from_config", "from_context": "some value"}'
        env = self._get_env(
            declaration_template=declaration_template,
            template_configuration=template_configuration,
        )

        result = env.get_template("template").render()

        assert format_json(result) == format_json(expected_result)


class Test_hashlib:
    @staticmethod
    def test_hashfunction():
        assert (
            hashfunction(hash_algo="sha1", data="fun with hashes")
            == "c16ced2f8ff2c50626266632cdfa0d2b80c44d50"
        )

    @staticmethod
    def test_hashfunction_unicode():
        assert (
            hashfunction(hash_algo="sha1", data="fun with hashes \u1f600")
            == "22c90831555130511851b192b3f0f0ae8291d9a5"
        )

    @staticmethod
    def test_hashfunction_bytes():
        assert (
            hashfunction(
                hash_algo="sha1", data="fun with hashes \u1f600".encode("utf-8")
            )
            == "22c90831555130511851b192b3f0f0ae8291d9a5"
        )

    @staticmethod
    def test_hashfunction_digest_format_hex():
        assert (
            hashfunction(
                data="fun with hashes",
                hash_algo="sha3_256",
                digest_format="hex",
            )
            == "19dbf4cfe516e0bb9a983c45b8e9f300dd69c083ab776d835559750181026802"
        )

    @staticmethod
    def test_hashfunction_digest_format_binary():
        assert (
            hashfunction(
                data="fun with hashes",
                hash_algo="sha3_256",
                digest_format="binary",
            )
            == b"\x19\xdb\xf4\xcf\xe5\x16\xe0\xbb\x9a\x98<E\xb8\xe9\xf3\x00\xddi\xc0\x83\xabwm\x83UYu\x01\x81\x02h\x02"
        )

    @staticmethod
    def test_hashfunction_digest_format_ValueError():
        with pytest.raises(ValueError) as exc:
            hashfunction(
                data="fun with hashes",
                hash_algo="sha3_256",
                digest_format="unsupported_format",
            )

        assert "unsupported_format" in str(exc.value)
        assert "hex" in str(exc.value)
        assert "binary" in str(exc.value)

    @staticmethod
    @pytest.mark.parametrize(
        "algo,test_string,hexdigest",
        [
            (
                "sha3_256",
                "fun with hashes",
                "19dbf4cfe516e0bb9a983c45b8e9f300dd69c083ab776d835559750181026802",
            ),
            (
                "sha3_256",
                "fun with hashes \u1f600",
                "648b955f78eb3b05f60e9c9e4f812abdc45f23749a0aaa8ebfd2326ca6693513",
            ),
            (
                "shake_256",
                "fun with hashes",
                "cc35a852a42ef7760065adde3f30c88be6361ffae3c1256da383c03c50861a0d",
            ),
            (
                "shake_256",
                "fun with hashes \u1f600",
                "84ab55560bf3c95642f899a21acaf3dbdfaf3b5cb31e1a736bca173442a3ef37",
            ),
            (
                "blake2b",
                "fun with hashes",
                "0afcadbf0589b34557d12fba2668fb9e0f6c9bd4efc04bd80b49367481d84df8964d01371085fbf48f5204e64396b9fe44a2107e1e3abd9020b896828954ff82",
            ),
            (
                "blake2b",
                "fun with hashes \u1f600",
                "199b7ae6f320a7926c6c6be92684f861f3438288437b01ed36a572d9af059ad5b5e9b2d0842abf850898c3ae9d58bd73e202ed3fac6a3fa13f6c61b623c394c7",
            ),
        ],
    )
    def test_hashfunction_advanced_hex(algo, test_string, hexdigest):
        """
        Test multiple test functions which are not directly exposed via functions using the hex formatted digest
        """
        assert hashfunction(data=test_string, hash_algo=algo) == hexdigest
        assert (
            hashfunction(data=test_string, hash_algo=algo, digest_format="hex")
            == hexdigest
        )

    @staticmethod
    @pytest.mark.parametrize(
        "algo,test_string,binarydigest",
        [
            (
                "sha3_256",
                "fun with hashes",
                b"\x19\xdb\xf4\xcf\xe5\x16\xe0\xbb\x9a\x98<E\xb8\xe9\xf3\x00\xddi\xc0\x83\xabwm\x83UYu\x01\x81\x02h\x02",
            ),
            (
                "sha3_256",
                "fun with hashes \u1f600",
                b"d\x8b\x95_x\xeb;\x05\xf6\x0e\x9c\x9eO\x81*\xbd\xc4_#t\x9a\n\xaa\x8e\xbf\xd22l\xa6i5\x13",
            ),
            (
                "shake_256",
                "fun with hashes",
                b"\xcc5\xa8R\xa4.\xf7v\x00e\xad\xde?0\xc8\x8b\xe66\x1f\xfa\xe3\xc1%m\xa3\x83\xc0<P\x86\x1a\r",
            ),
            (
                "shake_256",
                "fun with hashes \u1f600",
                b"\x84\xabUV\x0b\xf3\xc9VB\xf8\x99\xa2\x1a\xca\xf3\xdb\xdf\xaf;\\\xb3\x1e\x1ask\xca\x174B\xa3\xef7",
            ),
            (
                "blake2b",
                "fun with hashes \u1f600",
                b"\x19\x9bz\xe6\xf3 \xa7\x92llk\xe9&\x84\xf8a\xf3C\x82\x88C{\x01\xed6\xa5r\xd9\xaf\x05\x9a\xd5\xb5\xe9\xb2\xd0\x84*\xbf\x85\x08\x98\xc3\xae\x9dX\xbds\xe2\x02\xed?\xacj?\xa1?la\xb6#\xc3\x94\xc7",
            ),
            (
                "blake2b",
                "fun with hashes",
                b"\n\xfc\xad\xbf\x05\x89\xb3EW\xd1/\xba&h\xfb\x9e\x0fl\x9b\xd4\xef\xc0K\xd8\x0bI6t\x81\xd8M\xf8\x96M\x017\x10\x85\xfb\xf4\x8fR\x04\xe6C\x96\xb9\xfeD\xa2\x10~\x1e:\xbd\x90 \xb8\x96\x82\x89T\xff\x82",
            ),
        ],
    )
    def test_hashfunction_advanced_binary(algo, test_string, binarydigest):
        """
        Test multiple test functions which are not directly exposed via functions using the binary formatted digest
        """
        assert (
            hashfunction(data=test_string, hash_algo=algo, digest_format="binary")
            == binarydigest
        )

    @staticmethod
    def test_hashfunction_shake_variable_length():
        """
        Test shake variable length hash functions, check that the returned digest is 64 chars long (256 bits)
        """
        assert (
            hashfunction(hash_algo="shake_256", data="fun with hashes")
            == "cc35a852a42ef7760065adde3f30c88be6361ffae3c1256da383c03c50861a0d"
        )
        assert len(hashfunction(hash_algo="shake_256", data="fun with hashes")) == 64
        assert (
            hashfunction(hash_algo="shake_128", data="fun with hashes")
            == "93c241518c553eec896aa14ffff43dc717ce133590e84381f1371cee7f7c05bd"
        )
        assert len(hashfunction(hash_algo="shake_128", data="fun with hashes")) == 64

    @staticmethod
    def test_hashfunction_missing_hashfunction():
        """
        ValueError: unsupported hash type ...
        """
        with pytest.raises(ValueError) as exc:
            hashfunction(
                data="the hash function does not exist", hash_algo="foobar-hashfunction"
            )

        assert "foobar-hashfunction" in str(exc.value)

    @staticmethod
    @pytest.mark.parametrize(
        "test_string,hexdigest",
        [
            ("fun with hashes", "c16ced2f8ff2c50626266632cdfa0d2b80c44d50"),
            ("fun with hashes \u1f600", "22c90831555130511851b192b3f0f0ae8291d9a5"),
        ],
    )
    def test_sha1sum(test_string, hexdigest):
        assert sha1sum(test_string) == hexdigest

    @staticmethod
    @pytest.mark.parametrize(
        "test_string,hexdigest",
        [
            (
                "fun with hashes",
                "9a1a995cfab4ee7c5dff458f903931c0e489e9e07d7c71e2d916f59d428a48c0",
            ),
            (
                "fun with hashes \u1f600",
                "9cf9553ad0ab1c4c4d98e50b0fc2ca20583155603ed2ed1d826e4d0eeaa93eee",
            ),
        ],
    )
    def test_sha256sum(test_string, hexdigest):
        assert sha256sum(test_string) == hexdigest

    @staticmethod
    @pytest.mark.parametrize(
        "test_string,hexdigest",
        [
            (
                "fun with hashes",
                "b8b25c9998c82ab0aaac9b84f3c60065c0cdd68733a4b6def06f1c622452d16b308caf4641e34e1bd06c28aa894e7abb25981f4cd4f1bbfaeb564b8cdcb99153",
            ),
            (
                "fun with hashes \u1f600",
                "171e044b6f48286fc54a72d5e53f9ff1c611ed85e652b6115a425e42bfc08204a6ffae66b1a482bd4541fab56c2eabe413c4f4c9a98a555d9b22a3bc08dfd564",
            ),
        ],
    )
    def test_sha512sum(test_string, hexdigest):
        assert sha512sum(test_string) == hexdigest

    @staticmethod
    @pytest.mark.parametrize(
        "test_string,hexdigest",
        [
            ("fun with hashes", "95ef654efb20725651c542b80d91bbe8"),
            ("fun with hashes \u1f600", "9f50b2b6393e9ce6273c4e7937f0c3bc"),
            ("fun with hashes ὠ0", "9f50b2b6393e9ce6273c4e7937f0c3bc"),
        ],
    )
    def test_md5sum(test_string, hexdigest):
        assert md5sum(test_string) == hexdigest
