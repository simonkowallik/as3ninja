# -*- coding: utf-8 -*-
import pytest
from click.testing import CliRunner

from as3ninja.cli import cli
from tests.utils import fixture_tmpdir, format_json, load_file


@pytest.fixture(scope="class")
def fixture_clicker():
    return CliRunner()


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
    @pytest.mark.xfail
    def test_yaml_datatypes_schemavalidation_failure(fixture_clicker):
        """
        python3 -mas3ninja transform -c examples/yaml_datatypes/config.yaml -t examples/yaml_datatypes/template.j2
        raises a AS3ValidationError
        """
        # TODO: implement non zero exit code in click/cli
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
        assert result.exit_code != 0

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
