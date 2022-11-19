# -*- coding: utf-8 -*-
"""
Gitget provides a minimal interface to 'git' to clone a repository with a specific branch, tag or commit id.
"""

# pylint: disable=C0330 # Wrong hanging indentation before block
# pylint: disable=C0301 # Line too long

import shlex
import shutil
from datetime import datetime
from pathlib import Path
from subprocess import PIPE, CalledProcessError, TimeoutExpired, run
from tempfile import mkdtemp
from typing import Optional, Union

from .exceptions import GitgetException
from .settings import NINJASETTINGS

__all__ = ["Gitget"]


class Gitget:
    """Gitget context manager clones a git repository. Raises GitgetException on failure.
    Exports:
    `info` dict property with information about the cloned repository
    `repodir` str property with the filesystem path to the temporary directory
    Gitget creates a shall clone of the specified repository using the specified and optional depth.
    A branch can be selected, if not specified the git server default branch is used (usually master).

    A specific commit id in long format can be selected, depth can be used to reach back into the past in case the commit id isn't available through a shallow clone.

        :param repository: Git Repository URL.
        :param depth: Optional. Depth to clone. Specify `depth=0` for a full clone without a depth limit. (Default value = 1)
        :param branch: Optional. Branch or Tag to clone. If None, default remote branch will be cloned. (Default value = None)
        :param commit: Optional. Commit ID or HEAD~ format. Commit ID must either be within the last 20 commits or within the specified `depth`. (Default value = None)
        :param repodir: Optional. Target directory for repositroy. This directory will persist on disk, Gitget will not remove it for you. (Default value = None)
        :param force: Optional. Forces removal of an existing repodir before cloning (use with care). (Default value = False)
    """

    _gitcmd = (
        "git",
        "-c",
        f"http.sslVerify={NINJASETTINGS.GITGET_SSL_VERIFY}",
        "-c",
        f"http.proxy={NINJASETTINGS.GITGET_PROXY}",
    )

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        repository: str,
        depth: Optional[int] = None,
        branch: Optional[str] = None,
        commit: Optional[str] = None,
        repodir: Optional[str] = None,
        force: bool = False,
    ):
        if depth is None:
            depth = 1
        elif depth < 0:
            raise ValueError("depth must be 0 or a positive number.")
        self._depth = depth
        self._branch = branch
        self._commit = commit
        self._repo = repository
        if repodir:
            self._repodir = repodir
            self._repodir_persist = True
        else:
            self._repodir = str(mkdtemp(suffix=".ninja.git"))
            self._repodir_persist = False
        self._force = force
        self._gitlog: dict = {"branch": self._branch, "commit": {}, "author": {}}

    def __enter__(self):
        _repodir = Path(self._repodir)
        if _repodir.exists() and self._force:
            # git clone aborts if a directory exists and is not empty. recursively remove existing directory if _force is True.
            shutil.rmtree(_repodir)
        _repodir.mkdir(mode=0o700, parents=True, exist_ok=True)

        self._clone()
        if self._commit:
            self._checkout_commit()
        self._get_gitlog()

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if not self._repodir_persist:
            shutil.rmtree(path=self._repodir)

    def rmrepodir(self) -> None:
        """Method: Removes the repodir.

        This method is useful if repodir has been specified in :meth:`__init__`.
        """
        if Path(self._repodir).exists():
            shutil.rmtree(Path(self._repodir))

    @property
    def info(self) -> dict:
        """Property: returns dict with git log information"""
        return self._gitlog

    @property
    def repodir(self) -> str:
        """Property: returns the (temporary) directory of the repository"""
        return self._repodir

    @staticmethod
    def _datetime_format(epoch: Union[int, str]) -> str:
        """Private Method: returns a human readable UTC format (%Y-%m-%dT%H:%M:%SZ) of the unix epoch

        :param epoch: Unix epoch
        """
        return datetime.utcfromtimestamp(int(epoch)).strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def _sh_quote(arg) -> str:
        """Private Method: returns a shell escaped version of arg, where arg can by any type convertible to str. uses shlex.quote

        :param arg: Argument to pass to `shlex.quote`
        """
        try:
            # prevent quoting HEAD~<integer>
            if isinstance(arg, str) and arg.startswith("HEAD~"):
                if not arg == "HEAD~":
                    int(arg.lstrip("HEAD~"))
                return str(arg)
        except (ValueError, TypeError):
            pass

        return shlex.quote(str(arg))

    def _clone(self):
        """Private Method: clones git repository"""
        self._run_command(
            (
                "clone",
                self._depth and "--depth" or None,
                self._depth and self._sh_quote(self._depth) or None,
                self._branch and "--branch" or None,
                self._branch and self._sh_quote(self._branch) or None,
                self._sh_quote(self._repo),
                self._sh_quote(self._repodir),
            )
        )

    def _checkout_commit(self):
        """Private Method: checks out specific commit id

        Note: short ID (example: 2b54d17) is not allowed, must be the long commit id
        Note: The referenced commit id must be in the cloned repository or within a depth of 20
        """
        if self._depth and self._depth == 1:
            # by default look for commit within the last 20 commits
            self._run_command(("fetch", "--depth", "20"))

        self._run_command(("reset", "--hard", self._sh_quote(self._commit)))

    def _get_gitlog(self) -> None:
        """Private Method: parses the git log to a dict"""
        # git log -n 1 --pretty=commit_id:%H%nauthor:%an%nauthor_email:%aE%nauthor_date:%at%ncommit_date:%ct%ncommit_subject:%s
        result = self._run_command(
            ("log", "-n", "1", "--pretty=%H%n%ct%n%s%n%an%n%aE%n%at")
        )
        (
            self._gitlog["commit"]["id"],
            self._gitlog["commit"]["epoch"],
            self._gitlog["commit"]["subject"],
            self._gitlog["author"]["name"],
            self._gitlog["author"]["email"],
            self._gitlog["author"]["epoch"],
        ) = result.splitlines(keepends=False)

        self._gitlog["commit"]["id_short"] = self._gitlog["commit"]["id"][0:7]
        self._gitlog["commit"]["date"] = self._datetime_format(
            self._gitlog["commit"]["epoch"]
        )
        self._gitlog["author"]["date"] = self._datetime_format(
            int(self._gitlog["author"]["epoch"])
        )
        if not self._branch:
            # git rev-parse --abbrev-ref HEAD
            result = self._run_command(("rev-parse", "--abbrev-ref", "HEAD"))
            self._gitlog["branch"] = result.rstrip()

    def _run_command(self, cmd: tuple) -> str:
        """Private Method: runs a shell command and handles/raises exceptions based on the command return code

        :param cmd: list of command + arguments
        """
        result = None
        try:
            # exclude None types from command
            cmd = tuple(command for command in cmd if command)
            result = run(  # nosec (bandit: disable subprocess.run check)
                self._gitcmd + cmd,
                shell=False,
                cwd=self._repodir,
                check=False,
                stdout=PIPE,
                stderr=PIPE,
                timeout=NINJASETTINGS.GITGET_TIMEOUT,
            )
            result.check_returncode()
        except CalledProcessError as exc:
            _stderr = result.stderr.decode("utf8")
            _stderr = _stderr.replace("\n", "\\n")
            raise GitgetException(
                f"Gitget failed due to exception:CalledProcessError, STDERR: {_stderr}"
            )
        except TimeoutExpired as exc:
            raise GitgetException(
                f"Gitget failed due to exception:TimeoutExpired, exception details: {str(exc)}"
            )

        return result.stdout.decode("utf8")
