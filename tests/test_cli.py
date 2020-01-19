# -*- coding: utf-8 -*-
import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from as3ninja.cli import cli
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
        assert result_dict["gitrepo.info"] == "value"

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
