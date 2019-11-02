# -*- coding: utf-8 -*-
from pathlib import Path

import pytest

from as3ninja.gitget import Gitget, GitgetException
from tests.utils import fixture_tmpdir

# TODO: mock actual git interactions to decrease test time + increase predictability


class Test_Gitget_staticmethods:
    @staticmethod
    def test_datetime_format_returns_string():
        result = Gitget._datetime_format("1234567890")
        assert isinstance(result, str)

    @staticmethod
    def test_datetime_format_string():
        result = Gitget._datetime_format("1234567890")
        assert result == "2009-02-13T23:31:30Z"

    @staticmethod
    def test_datetime_format_int():
        result = Gitget._datetime_format(1234567890)
        assert result == "2009-02-13T23:31:30Z"

    @staticmethod
    def test_sh_quote__no_quote():
        teststring = "abc"
        result = Gitget._sh_quote(teststring)
        assert result == f"{teststring}"

    @staticmethod
    def test_sh_quote__integer():
        teststring = 1234
        result = Gitget._sh_quote(teststring)
        assert result == f"{teststring}"

    @staticmethod
    def test_sh_quote__simple_quote():
        teststring = "a b c"
        result = Gitget._sh_quote(teststring)
        assert result == f"'{teststring}'"

    @staticmethod
    def test_sh_quote__command_injection():
        teststring = "'; ls /; echo"
        result = Gitget._sh_quote(teststring)
        assert result == "''\"'\"'; ls /; echo'"


class Test_Gitget_interface:
    @staticmethod
    def test_Gitget_simple():
        with Gitget(
            repository="https://github.com/simonkowallik/ihac", branch="master"
        ) as gitrepo:
            assert isinstance(gitrepo.info, dict)
            assert gitrepo.info["branch"] == "master"

    @staticmethod
    def test_Gitget_repo_only():
        with Gitget(repository="https://github.com/simonkowallik/ihac") as gitrepo:
            assert isinstance(gitrepo.info, dict)
            assert gitrepo.info["branch"] == "master"

    @staticmethod
    def test_Gitget_tag():
        with Gitget(
            repository="https://github.com/simonkowallik/ihac", branch="2.0"
        ) as gitrepo:
            assert isinstance(gitrepo.info, dict)
            assert gitrepo.info["branch"] == "2.0"

    @staticmethod
    def test_Gitget_depth0():
        with Gitget(
            repository="https://github.com/simonkowallik/ihac", branch="master", depth=0
        ) as gitrepo:
            assert isinstance(gitrepo.info, dict)
            assert gitrepo.info["branch"] == "master"

    @staticmethod
    def test_Gitget_depth_negative():
        with pytest.raises(ValueError) as exception_info:
            with Gitget(
                repository="https://github.com/simonkowallik/ihac",
                branch="master",
                depth=-1,
            ) as gitrepo:
                print(gitrepo.info)

        assert exception_info.type is ValueError

    @staticmethod
    def test_non_existing_commit():
        with pytest.raises(GitgetException) as exception_info:
            with Gitget(
                repository="https://github.com/simonkowallik/ihac", commit=40 * "1"
            ) as gitrepo:
                print(gitrepo.info)

        assert exception_info.type is GitgetException

    @staticmethod
    def test_invalid_commit_id():
        with pytest.raises(ValueError) as exception_info:
            with Gitget(
                repository="https://github.com/simonkowallik/ihac", commit="1234567"
            ) as gitrepo:
                print(gitrepo.info)

        assert exception_info.type is ValueError

    @staticmethod
    def test_non_existing_repository():
        # TODO: this prompts for user+password. requires credential handling
        with pytest.raises(GitgetException) as exception_info:
            with Gitget(
                repository="https://github.com/simonkowallik/does-not-exist",
                branch="doesnt-exist",
            ) as gitrepo:
                print(gitrepo.info)

        assert exception_info.type is GitgetException


@pytest.mark.usefixtures("fixture_tmpdir")
class Test_Gitget_advanced_interface:
    @staticmethod
    def test_custom_repodir(fixture_tmpdir):
        repodir = fixture_tmpdir
        with Gitget(
            repository="https://github.com/simonkowallik/ihac",
            branch="master",
            repodir=repodir,
        ) as gitrepo:
            assert isinstance(gitrepo.info, dict)
            assert gitrepo.info["branch"] == "master"

        assert Path(repodir).exists()

    @staticmethod
    def test_rmrepodir(fixture_tmpdir):
        repodir = fixture_tmpdir
        with Gitget(
            repository="https://github.com/simonkowallik/ihac",
            branch="master",
            repodir=repodir,
        ) as gitrepo:
            assert isinstance(gitrepo.info, dict)
            assert gitrepo.info["branch"] == "master"
            gitrepo.rmrepodir()

        assert Path(repodir).exists() is False

    @staticmethod
    def test_custom_repodir_2ndclone_force(fixture_tmpdir):
        repodir = fixture_tmpdir
        # first clone
        with Gitget(
            repository="https://github.com/simonkowallik/ihac",
            branch="master",
            repodir=repodir,
        ) as gitrepo:
            assert isinstance(gitrepo.info, dict)
            assert gitrepo.info["branch"] == "master"

        # second clone to existing repo
        with Gitget(
            repository="https://github.com/simonkowallik/ihac",
            branch="master",
            repodir=repodir,
            force=True,
        ) as gitrepo:
            assert isinstance(gitrepo.info, dict)
            assert gitrepo.info["branch"] == "master"

    @staticmethod
    def test_custom_repodir_2ndclone_noforce(fixture_tmpdir):
        repodir = fixture_tmpdir
        # first clone
        with Gitget(
            repository="https://github.com/simonkowallik/ihac",
            branch="master",
            repodir=repodir,
        ) as gitrepo:
            assert isinstance(gitrepo.info, dict)
            assert gitrepo.info["branch"] == "master"

        # second clone to existing repo without force raises exception
        with pytest.raises(GitgetException) as exception_info:
            with Gitget(
                repository="https://github.com/simonkowallik/ihac",
                branch="master",
                repodir=repodir,
            ) as gitrepo:
                print(gitrepo.info)

        assert exception_info.type is GitgetException


class Test_previous_issues:
    @staticmethod
    def test_dir_exists_on_with():
        with Gitget(repository="https://github.com/simonkowallik/ihac") as gitrepo:
            assert Path(gitrepo.repodir + "/.git").exists()
