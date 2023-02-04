# -*- coding: utf-8 -*-
import json
from pathlib import Path

import mock
import pytest
import yaml
from click.testing import CliRunner

from as3ninja.cli import cli
from as3ninja.gitget import Gitget
from tests.utils import fixture_tmpdir, format_json, load_file


@pytest.fixture(scope="class")
def fixture_clicker():
    return CliRunner()


@pytest.mark.usefixtures("fixture_clicker")
class Test_validate:
    @staticmethod
    def test_validation_success(fixture_clicker, capsys):
        """
        Non AS3 Schema JSON test with simple test data

        as3ninja validate --declaration tests/testdata/cli/validate/declaration.json
        """
        result = fixture_clicker.invoke(
            cli,
            [
                "validate",
                "--declaration",
                "tests/testdata/cli/validate/declaration.json",
            ],
        )

        assert result.exit_code == 0

    @staticmethod
    def test_validation_failure(fixture_clicker, capsys):
        """
        Non AS3 Schema JSON test with simple test data

        as3ninja validate --version 3.9.0 -d tests/testdata/cli/validate/declaration.json
        """
        result = fixture_clicker.invoke(
            cli,
            [
                "validate",
                "--version",
                "3.9.0",
                "-d",
                "tests/testdata/cli/validate/declaration.json",
            ],
        )

        assert result.exit_code == 1

    @staticmethod
    def test_validation_failure_details(fixture_clicker, capsys):
        """
        Non AS3 Schema JSON test with simple test data

        as3ninja validate -d tests/testdata/cli/validate/errors.json
        """
        result = fixture_clicker.invoke(
            cli,
            [
                "validate",
                "-d",
                "tests/testdata/cli/validate/errors.json",
            ],
        )
        assert result.exit_code != 0


@pytest.mark.usefixtures("fixture_clicker")
class Test_git_transform:
    @staticmethod
    def test_simple(fixture_clicker, mocker):
        """
        Non AS3 Schema JSON test with simple test data and validation disabled -> success

        as3ninja git-transform --no-validate --repository .. -c file1 file2 -t template ...
        """
        mocked_Gitget = mocker.patch("as3ninja.cli.Gitget")
        mocked_Gitget.return_value.__enter__.return_value.repodir = str(Path.cwd())
        mocked_Gitget.return_value.__enter__.return_value.info = {"key": "value"}
        result = fixture_clicker.invoke(
            cli,
            [
                "git-transform",
                "--no-validate",
                "--repository",
                "https://github.com/simonkowallik/as3ninja",
                "-c",
                "tests/testdata/cli/transform_git/config.yaml",
                "-c",
                "tests/testdata/cli/transform_git/config2.yaml",
                "-t",
                "tests/testdata/cli/transform_git/template.jinja2",
                "--pretty",
            ],
        )
        assert result.exit_code == 0

        result_dict = json.loads(result.output)
        assert result_dict["config"] == "yes!"
        assert result_dict["config2"] == "yes!"
        assert result_dict["gitrepo.info"] == "{'key': 'value'}"

    @staticmethod
    def test_simple_validate_failure(fixture_clicker, mocker):
        """
        Non AS3 Schema JSON test with simple test data and validation enabled -> exit code 1 (validation error)

        as3ninja git-transform --repository .. -c file1 file2 -t template ...
        """
        mocked_Gitget = mocker.patch("as3ninja.cli.Gitget")
        mocked_Gitget.return_value.__enter__.return_value.repodir = str(Path.cwd())
        mocked_Gitget.return_value.__enter__.return_value.info = {"key": "value"}
        result = fixture_clicker.invoke(
            cli,
            [
                "git-transform",
                "--repository",
                "https://github.com/simonkowallik/as3ninja",
                "-c",
                "tests/testdata/cli/transform_git/config.yaml",
                "-c",
                "tests/testdata/cli/transform_git/config2.yaml",
                "-t",
                "tests/testdata/cli/transform_git/template.jinja2",
            ],
        )
        assert result.exit_code == 1


@pytest.mark.usefixtures("fixture_tmpdir")
@pytest.mark.usefixtures("fixture_clicker")
class Test_transform:
    @staticmethod
    def test_yaml_datatypes(fixture_clicker):
        """
        python3 -mas3ninja transform --no-validate -c examples/yaml_datatypes/config.yaml -t examples/yaml_datatypes/template.j2
        """
        result = fixture_clicker.invoke(
            cli,
            [
                "transform",
                "--no-validate",
                "-c",
                "examples/yaml_datatypes/config.yaml",
                "-t",
                "examples/yaml_datatypes/template.j2",
            ],
        )
        assert result.exit_code == 0
        print(f"\n\nresult.output:{result.output}\n\n")
        assert format_json(result.output) == format_json(
            load_file("examples/yaml_datatypes/output.json")
        )

    @staticmethod
    def test_yaml_pretty_print(fixture_clicker):
        """
        python3 -mas3ninja transform --pretty --no-validate -c examples/yaml_datatypes/config.yaml -t examples/yaml_datatypes/template.j2
        """
        result = fixture_clicker.invoke(
            cli,
            [
                "transform",
                "--pretty",
                "--no-validate",
                "-c",
                "examples/yaml_datatypes/config.yaml",
                "-t",
                "examples/yaml_datatypes/template.j2",
            ],
        )
        assert result.exit_code == 0
        assert result.output == load_file("examples/yaml_datatypes/output.json")

    @staticmethod
    def test_yaml_datatypes_schemavalidation_failure(fixture_clicker):
        """
        python3 -mas3ninja transform -c examples/yaml_datatypes/config.yaml -t examples/yaml_datatypes/template.j2
        raises a AS3ValidationError
        """
        result = fixture_clicker.invoke(
            cli,
            [
                "transform",
                "-c",
                "examples/yaml_datatypes/config.yaml",
                "-t",
                "examples/yaml_datatypes/template.j2",
            ],
        )
        assert result.exit_code == 1

    @staticmethod
    def test_yaml_simple(fixture_clicker):
        """
        python3 -mas3ninja transform -c examples/simple/ninja.yaml -t examples/simple/template.j2
        """
        result = fixture_clicker.invoke(
            cli,
            [
                "transform",
                "-c",
                "examples/simple/ninja.yaml",
                "-t",
                "examples/simple/template.j2",
            ],
        )
        assert result.exit_code == 0
        assert format_json(result.output) == format_json(
            load_file("examples/simple/declaration.json")
        )

    @staticmethod
    def test_yaml_simple_longoptions(fixture_clicker):
        """
        python3 -mas3ninja transform --configuration-file examples/simple/ninja.yaml --declaration-template examples/simple/template.j2
        """
        result = fixture_clicker.invoke(
            cli,
            [
                "transform",
                "--configuration-file",
                "examples/simple/ninja.yaml",
                "--declaration-template",
                "examples/simple/template.j2",
            ],
        )
        assert result.exit_code == 0
        assert format_json(result.output) == format_json(
            load_file("examples/simple/declaration.json")
        )

    @staticmethod
    def test_yaml_simple_outputfile(fixture_tmpdir, fixture_clicker):
        """
        python3 -mas3ninja transform -c examples/simple/ninja.yaml -t examples/simple/template.j2 -o /tmp/output.json
        """
        tmpdir = fixture_tmpdir
        result = fixture_clicker.invoke(
            cli,
            [
                "transform",
                "-c",
                "examples/simple/ninja.yaml",
                "-t",
                "examples/simple/template.j2",
                "-o",
                f"{tmpdir}/output.json",
            ],
        )
        assert result.exit_code == 0
        assert format_json(load_file(f"{tmpdir}/output.json")) == format_json(
            load_file("examples/simple/declaration.json")
        )

    @staticmethod
    def test_yaml_simple_outputfile_longoption(fixture_tmpdir, fixture_clicker):
        """
        python3 -mas3ninja transform --configuration-file examples/simple/ninja.yaml --declaration-template examples/simple/template.j2 --output-file /tmp/output.json
        """
        tmpdir = fixture_tmpdir
        result = fixture_clicker.invoke(
            cli,
            [
                "transform",
                "--configuration-file",
                "examples/simple/ninja.yaml",
                "--declaration-template",
                "examples/simple/template.j2",
                "--output-file",
                f"{tmpdir}/output.json",
            ],
        )
        assert result.exit_code == 0
        assert format_json(load_file(f"{tmpdir}/output.json")) == format_json(
            load_file("examples/simple/declaration.json")
        )

    @staticmethod
    def test_yaml_simple_configoverlay(fixture_clicker):
        """
        python3 -mas3ninja transform -c examples/simple/ninja.yaml -c examples/simple/overlay.json -t examples/simple/template.j2
        """
        result = fixture_clicker.invoke(
            cli,
            [
                "transform",
                "-c",
                "examples/simple/ninja.yaml",
                "-c",
                "examples/simple/overlay.json",
                "-t",
                "examples/simple/template.j2",
            ],
        )
        assert result.exit_code == 0
        assert format_json(result.output) == format_json(
            load_file("examples/simple/declaration_with_overlay.json")
        )


@pytest.mark.usefixtures("fixture_tmpdir")
@pytest.mark.usefixtures("fixture_clicker")
class Test_transform_git:
    # TODO: implement tests
    pass


@pytest.mark.usefixtures("fixture_clicker")
class Test_schema_versions:
    @staticmethod
    def test_versions(fixture_clicker):
        """
        as3ninja schema versions text output (default)
        """
        result = fixture_clicker.invoke(
            cli,
            [
                "schema",
                "versions",
            ],
        )

        assert result.exit_code == 0
        assert result.output.count("\n") > 2  # more than two versions in output

    @staticmethod
    def test_versions_json(fixture_clicker):
        """
        as3ninja schema versions JSON outout
        """
        result = fixture_clicker.invoke(
            cli,
            [
                "schema",
                "versions",
                "--json",
            ],
        )

        assert result.exit_code == 0
        json_result = json.loads(result.output)
        assert "as3_schema_versions" in json_result
        assert (
            len(json_result["as3_schema_versions"]) > 2
        )  # more than two versions in output

    @staticmethod
    def test_versions_yaml(fixture_clicker):
        """
        as3ninja schema versions YAML outout
        """
        result = fixture_clicker.invoke(
            cli,
            [
                "schema",
                "versions",
                "--yaml",
            ],
        )

        assert result.exit_code == 0
        yaml_result = yaml.safe_load(result.output)
        assert "as3_schema_versions" in yaml_result
        assert (
            len(yaml_result["as3_schema_versions"]) > 2
        )  # more than two versions in output


class Test_schema_update:
    @staticmethod
    def test_update(fixture_clicker, mocker):
        """
        as3ninja schema update
        """
        mocked_as3schema = mock.MagicMock()
        type(mocked_as3schema).version = mock.PropertyMock(
            side_effect=["3.1.0", "3.2.0", "3.1.0", "3.2.0"]
        )
        mocked_as3schema.return_value = mocked_as3schema

        mocker.patch("as3ninja.cli.AS3Schema", mocked_as3schema)

        result = fixture_clicker.invoke(
            cli,
            [
                "schema",
                "update",
            ],
        )

        assert result.exit_code == 0
        assert result.output.count("3.1.0") == 1
        assert result.output.count("3.2.0") == 1

    @staticmethod
    def test_update_current(fixture_clicker, mocker):
        """
        as3ninja schema update
        """
        mocked_as3schema = mock.MagicMock()
        type(mocked_as3schema).version = mock.PropertyMock(
            side_effect=["3.1.0", "3.1.0", "3.1.0", "3.1.0"]
        )
        mocked_as3schema.return_value = mocked_as3schema

        mocker.patch("as3ninja.cli.AS3Schema", mocked_as3schema)

        result = fixture_clicker.invoke(
            cli,
            [
                "schema",
                "update",
            ],
        )

        assert result.exit_code == 0
        assert result.output.count("3.1.0") == 1
