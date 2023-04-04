"""This module defines custom ``generate_source_manifest`` setuptools
command."""

from __future__ import annotations

import os
import subprocess
import sys

from distutils.cmd import Command

from ..constants import SKBUILD_DIR, SKBUILD_MARKER_FILE
from . import set_build_base_mixin


class generate_source_manifest(set_build_base_mixin, Command):
    """Custom setuptools command generating a `MANIFEST` file if
    not already provided."""

    description = "generate source MANIFEST"

    def initialize_options(self) -> None:
        """Set default values for all the options that this command supports."""

    def run(self) -> None:
        """
        If neither a `MANIFEST`, nor a `MANIFEST.in` file is provided, and
        we are in a git repo, try to create a `MANIFEST.in` file from the output of
        `git ls-tree --name-only -r HEAD`.

        We need a reliable way to tell if an existing `MANIFEST` file is one
        we've generated.  distutils already uses a first-line comment to tell
        if the `MANIFEST` file was generated from `MANIFEST.in`, so we use a
        dummy file, `_skbuild_MANIFEST`, to avoid confusing distutils.
        """
        do_generate = (
            # If there's a MANIFEST.in file, we assume that we had nothing to do
            # with the project's manifest.
            not os.path.exists("MANIFEST.in")
            # otherwise, we check to see that there is no MANIFEST, ...
            if not os.path.exists("MANIFEST")
            # ... (if there is one,) that we created it
            else os.path.exists(SKBUILD_MARKER_FILE())
        )

        if do_generate:
            try:
                with open("MANIFEST.in", "wb") as manifest_in_file:
                    # Since Git < 2.11 does not support --recurse-submodules option, fallback to
                    # regular listing.
                    try:
                        cmd_out = subprocess.run(
                            ["git", "ls-files", "--recurse-submodules"], stdout=subprocess.PIPE, check=True
                        ).stdout
                    except subprocess.CalledProcessError:
                        cmd_out = subprocess.run(["git", "ls-files"], stdout=subprocess.PIPE, check=True).stdout
                    git_files = [git_file.strip() for git_file in cmd_out.split(b"\n")]
                    manifest_text = b"\n".join([b"include %s" % git_file.strip() for git_file in git_files if git_file])
                    manifest_text += b"\nexclude MANIFEST.in"
                    manifest_in_file.write(manifest_text)
            except subprocess.CalledProcessError:
                sys.stderr.write(
                    "\n\n"
                    "Since scikit-build could not find MANIFEST.in or "
                    "MANIFEST, it tried to generate a MANIFEST.in file "
                    "automatically, but could not because it could not "
                    "determine which source files to include.\n\n"
                    'The command used was "git ls-files"\n'
                    "\n\n"
                )
                raise

            if not os.path.exists(SKBUILD_DIR()):
                os.makedirs(SKBUILD_DIR())

            with open(SKBUILD_MARKER_FILE(), "w", encoding="utf-8"):  # touch
                pass

    def finalize_options(self, *args: object, **kwargs: object) -> None:
        """Set final values for all the options that this command supports."""
